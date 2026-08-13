#!/usr/bin/env python3
"""Run one content-addressed Method v1.3 benchmark job.

The runner executes only contracts frozen after C1.  Discovery jobs must all
start from the same manifest state in which all three arms are still pending;
they cannot consume another arm's results.  Every process tree is confined to
one CPU, a PID/process-group boundary, and a network namespace.  The runner
launches the complete frozen process set and never interprets a crossing as a
reason to cancel remaining work.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SCHEMA = ROOT / "schemas" / "benchmark-run-contract-v1.3.schema.json"
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
MODES = ("DISCOVERY_ARM", "SHARED_ANALYSIS", "INDEPENDENT_VERIFICATION")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
OID_RE = re.compile(r"^[0-9a-fA-F]{40,64}$")
SAFE_PROCESS_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
ZERO_SHA256 = "0" * 64
LEDGER_LOCK = threading.Lock()


class ContractError(ValueError):
    """The requested job is not exactly authorized by the frozen inputs."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def row_sha256(row: dict[str, Any]) -> str:
    payload = {key: value for key, value in row.items() if key != "row_sha256"}
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def verify_ledger(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    previous = ZERO_SHA256
    if not path.is_file():
        return rows
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(f"runtime ledger row {index} is not JSON: {exc}") from exc
        if row.get("sequence") != index:
            raise ContractError(f"runtime ledger row {index} has a non-contiguous sequence")
        if row.get("previous_row_sha256") != previous:
            raise ContractError(f"runtime ledger row {index} breaks the previous-hash chain")
        if row.get("row_sha256") != row_sha256(row):
            raise ContractError(f"runtime ledger row {index} has an invalid digest")
        previous = row["row_sha256"]
        rows.append(row)
    return rows


def append_ledger(path: Path, event: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Append and fsync one hash-chained JSONL row; never rewrite prior rows."""

    with LEDGER_LOCK:
        rows = verify_ledger(path)
        row = {
            "sequence": len(rows),
            "previous_row_sha256": rows[-1]["row_sha256"] if rows else ZERO_SHA256,
            "recorded_at_utc": utc_now(),
            "event": event,
            "payload": payload,
        }
        row["row_sha256"] = row_sha256(row)
        encoded = (canonical_json(row) + "\n").encode("utf-8")
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            remaining = memoryview(encoded)
            while remaining:
                written = os.write(descriptor, remaining)
                if written <= 0:  # pragma: no cover - kernel/filesystem failure
                    raise OSError("short write while appending runtime ledger")
                remaining = remaining[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return row


def relative_path(repo_root: Path, recorded: str, label: str) -> Path:
    pure = PurePosixPath(recorded)
    if pure.is_absolute() or ".." in pure.parts:
        raise ContractError(f"{label} must be a repository-relative path")
    resolved = repo_root.joinpath(*pure.parts).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ContractError(f"{label} escapes the repository") from exc
    return resolved


def resolve_reference(manifest_path: Path, recorded: str) -> Path:
    candidate = Path(recorded)
    if candidate.is_absolute():
        return candidate.resolve()
    rooted = ROOT / candidate
    if rooted.exists():
        return rooted.resolve()
    return (manifest_path.parent / candidate).resolve()


def find_cluster(manifest: dict[str, Any], cluster_id: str) -> dict[str, Any]:
    matches = [cluster for cluster in manifest["clusters"] if cluster["cluster_id"] == cluster_id]
    if len(matches) != 1:
        raise ContractError(f"cluster_id must resolve exactly once; found {len(matches)}")
    return matches[0]


def contract_reference(cluster: dict[str, Any], mode: str, arm: str | None) -> dict[str, str]:
    if mode == "DISCOVERY_ARM":
        if arm not in ARMS:
            raise ContractError("DISCOVERY_ARM requires one frozen discovery arm")
        arms = cluster.get("arms")
        if not isinstance(arms, dict) or set(arms) != set(ARMS):
            raise ContractError("cluster must freeze exactly catalogue, generic, and wall-navigation")
        return arms[arm]["contract"]
    if arm is not None:
        raise ContractError(f"{mode} does not accept a discovery arm")
    field = {
        "SHARED_ANALYSIS": "shared_analysis_contract",
        "INDEPENDENT_VERIFICATION": "independent_verification_contract",
    }[mode]
    reference = cluster.get(field)
    if reference is None:
        raise ContractError(f"cluster does not freeze {field}")
    return reference


def validate_contract_shape(contract: dict[str, Any]) -> None:
    schema = json.loads(CONTRACT_SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(contract), key=lambda item: list(item.path))
    if errors:
        rendered = "; ".join(
            f"{'.'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
            for error in errors
        )
        raise ContractError(f"contract schema failure: {rendered}")


def budget_count(budget: dict[str, Any]) -> int:
    value = budget.get("process_tree_count", budget.get("process_count"))
    if not isinstance(value, int):
        raise ContractError("manifest budget lacks an integer process-tree count")
    return value


def validate_contract(
    manifest: dict[str, Any],
    cluster: dict[str, Any],
    contract: dict[str, Any],
    mode: str,
    arm: str | None,
    repo_root: Path,
) -> None:
    validate_contract_shape(contract)
    if contract["benchmark_version"] != "c5k4-benchmark-1.3":
        raise ContractError("contract is not a Method v1.3 contract")
    if contract["benchmark_id"] != manifest["benchmark_id"]:
        raise ContractError("contract benchmark_id differs from manifest")
    if contract["cluster_id"] != cluster["cluster_id"]:
        raise ContractError("contract cluster_id differs from requested cluster")
    if contract["job_mode"] != mode or contract["arm"] != arm:
        raise ContractError("contract mode/arm differs from requested job")
    if contract["no_adaptation"] is not True:
        raise ContractError("contract must prohibit adaptation")
    if contract["continue_after_crossing"] is not True:
        raise ContractError("contract must continue after a crossing")
    if contract["cross_arm_result_inputs"] != []:
        raise ContractError("contract cannot consume cross-arm result inputs")
    if contract["results_embargo"] != "UNTIL_ALL_DISCOVERY_ARMS_TERMINATE":
        raise ContractError("contract must embargo results until every discovery arm terminates")
    if contract["network_policy"] != "DENY":
        raise ContractError("contract must deny network access")
    if contract["process_tree_isolation"] != "ONE_CPU_PROCESS_GROUP_NETWORK_NAMESPACE":
        raise ContractError("contract must isolate every process tree")
    if contract["process_tree_wall_cap_seconds"] != 60:
        raise ContractError("every process tree must have an exact 60-second hard wall cap")
    count = contract["process_tree_count"]
    if len(contract["processes"]) != count:
        raise ContractError("process list length differs from frozen process_tree_count")
    if count * 60 > contract["cpu_budget_seconds"]:
        raise ContractError("full process-tree upper bound exceeds the declared CPU budget")

    process_ids = [process["process_id"] for process in contract["processes"]]
    if len(process_ids) != len(set(process_ids)):
        raise ContractError("process_id values must be unique")
    for process in contract["processes"]:
        if not SAFE_PROCESS_ID_RE.fullmatch(process["process_id"]):
            raise ContractError(f"unsafe process_id: {process['process_id']!r}")
        relative_path(repo_root, process["working_directory"], "working_directory")
        for argument in process["argv"]:
            if "\x00" in argument or "\n" in argument or "\r" in argument:
                raise ContractError("argv entries cannot contain NUL or newline characters")

    budgets = manifest["budgets"]
    if mode == "DISCOVERY_ARM":
        arms = cluster.get("arms")
        if not isinstance(arms, dict) or set(arms) != set(ARMS):
            raise ContractError("discovery requires exactly the three frozen arms")
        if any(item.get("status") != "PENDING" for item in arms.values()):
            raise ContractError("every discovery arm must launch from the same all-PENDING barrier")
        frozen = arms[arm]
        global_budget = budgets["discovery_arm"]
        expected = (8, 60, 480)
        observed = (count, contract["process_tree_wall_cap_seconds"], contract["cpu_budget_seconds"])
        manifest_budget = (
            budget_count(global_budget),
            global_budget["process_wall_cap_seconds"],
            global_budget["cpu_budget_seconds"],
        )
        if observed != expected or manifest_budget != expected:
            raise ContractError("discovery execution must be exactly 8 x 60s and 480 CPU-seconds")
        for key in ("seed", "parameter_grid", "transformation_id", "no_adaptation"):
            if contract[key] != frozen[key]:
                raise ContractError(f"contract {key} differs from the frozen arm")
        if cluster.get("runnable") is not True:
            raise ContractError("discovery arm requires a runnable cluster")
    elif mode == "SHARED_ANALYSIS":
        budget = budgets["shared_analysis"]
        if budget["process_wall_cap_seconds"] != 60 or budget["cpu_budget_seconds"] > 600:
            raise ContractError("manifest shared analysis exceeds its 600 CPU-second cap")
        if budget_count(budget) > 10:
            raise ContractError("manifest shared analysis exceeds ten isolated process trees")
        if count > budget_count(budget) or contract["cpu_budget_seconds"] > budget["cpu_budget_seconds"]:
            raise ContractError("shared analysis exceeds its frozen global budget")
        if count * 60 > 600:
            raise ContractError("shared analysis exceeds 600 CPU-seconds")
        if cluster.get("evaluation_started_at_utc") is not None:
            raise ContractError("shared analysis cannot start after cluster evaluation")
        arms = cluster.get("arms")
        if arms is not None and any(item.get("status") != "PENDING" for item in arms.values()):
            raise ContractError("shared analysis cannot run after a discovery arm starts")
    else:
        budget = budgets["independent_verification"]
        expected = (2, 60, 120)
        observed = (count, contract["process_tree_wall_cap_seconds"], contract["cpu_budget_seconds"])
        frozen = (
            budget_count(budget),
            budget["process_wall_cap_seconds"],
            budget["cpu_budget_seconds"],
        )
        if observed != expected or frozen != expected:
            raise ContractError("independent verification must be exactly 2 x 60s and 120 CPU-seconds")
        arms = cluster.get("arms")
        if not isinstance(arms, dict) or set(arms) != set(ARMS) or any(
            item.get("status") != "TERMINATED" for item in arms.values()
        ):
            raise ContractError("verification is locked until all three discovery arms terminate")
        if cluster.get("evaluation_started_at_utc") is None:
            raise ContractError("verification requires a recorded cluster evaluation start")


def sanitized_environment(
    output_dir: Path, process_id: str, benchmark_id: str, cluster_id: str, mode: str, arm: str | None
) -> dict[str, str]:
    temporary = output_dir / "tmp"
    temporary.mkdir(parents=True, exist_ok=True)
    return {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": str(output_dir),
        "TMPDIR": str(temporary),
        "XDG_CACHE_HOME": str(output_dir / "xdg-cache"),
        "XDG_CONFIG_HOME": str(output_dir / "xdg-config"),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONHASHSEED": "0",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "C5K4_BENCHMARK_VERSION": "1.3",
        "C5K4_BENCHMARK_ID": benchmark_id,
        "C5K4_CLUSTER_ID": cluster_id,
        "C5K4_JOB_MODE": mode,
        "C5K4_ARM": arm or "NONE",
        "C5K4_PROCESS_ID": process_id,
        "C5K4_PROCESS_OUTPUT_DIR": str(output_dir),
    }


def parse_time_metrics(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    values: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key in {"user_seconds", "system_seconds", "max_rss_kb", "exit_status"}:
            try:
                values[key] = float(value) if "." in value else int(value)
            except ValueError:
                values[key] = value
    if isinstance(values.get("user_seconds"), (int, float)) and isinstance(
        values.get("system_seconds"), (int, float)
    ):
        values["cpu_seconds"] = values["user_seconds"] + values["system_seconds"]
    return values


def run_process(
    process: dict[str, Any],
    cpu: int,
    output_root: Path,
    repo_root: Path,
    contract: dict[str, Any],
    ledger_path: Path,
) -> dict[str, Any]:
    process_id = process["process_id"]
    process_dir = output_root / "processes" / process_id
    process_dir.mkdir(parents=True, exist_ok=False)
    stdout_path = process_dir / "stdout.log"
    stderr_path = process_dir / "stderr.log"
    time_path = process_dir / "time.metrics"
    invocation = {
        "process_id": process_id,
        "cpu_affinity": cpu,
        "argv": process["argv"],
        "working_directory": process["working_directory"],
        "parameter_assignment": process["parameter_assignment"],
        "network_policy": "DENY",
        "process_tree_isolation": "ONE_CPU_PROCESS_GROUP_NETWORK_NAMESPACE",
        "wall_cap_seconds": 60,
    }
    (process_dir / "invocation.json").write_text(
        json.dumps(invocation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    append_ledger(ledger_path, "PROCESS_TREE_STARTED", invocation)

    environment = sanitized_environment(
        process_dir, process_id, contract["benchmark_id"], contract["cluster_id"],
        contract["job_mode"], contract["arm"],
    )
    fixed_environment = [f"{key}={value}" for key, value in sorted(environment.items())]
    argv = [
        "taskset", "-c", str(cpu),
        "sudo", "-n", "unshare", "--net", "--pid", "--fork", "--kill-child=KILL",
        "--setuid", str(os.getuid()), "--setgid", str(os.getgid()),
        "/usr/bin/env", "-i", *fixed_environment,
        "/usr/bin/time", "--quiet",
        "-f", "user_seconds=%U\nsystem_seconds=%S\nmax_rss_kb=%M\nexit_status=%x",
        "-o", str(time_path), "--", *process["argv"],
    ]
    started_at = utc_now()
    start = time.monotonic()
    timed_out = False
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        child = subprocess.Popen(
            argv,
            cwd=relative_path(repo_root, process["working_directory"], "working_directory"),
            env=environment,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
        try:
            returncode = child.wait(timeout=60)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            returncode = child.wait()
    elapsed = time.monotonic() - start
    time_metrics = parse_time_metrics(time_path)
    cpu_seconds = time_metrics.get("cpu_seconds")
    cpu_violation = isinstance(cpu_seconds, (int, float)) and cpu_seconds > 60.05
    result = {
        "process_id": process_id,
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "returncode": returncode,
        "timed_out": timed_out,
        "wall_cap_signal_seconds": 60,
        "observed_wall_seconds": elapsed,
        "charged_wall_seconds": min(elapsed, 60.0),
        "cpu_affinity": cpu,
        "cpu_budget_seconds": 60,
        "cpu_budget_violation": cpu_violation,
        "time": time_metrics,
    }
    (process_dir / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    append_ledger(ledger_path, "PROCESS_TREE_FINISHED", result)
    return result


def run_all_processes(
    processes: list[dict[str, Any]],
    cpus: list[int],
    worker: Callable[[dict[str, Any], int], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Submit the entire frozen set before observing any result.

    The function deliberately has no crossing predicate.  A result that says
    ``CROSS`` is data, not control flow; all submitted trees run to completion.
    """

    results: list[dict[str, Any]] = []
    errors: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(processes)) as pool:
        futures = [
            pool.submit(worker, process, cpus[index % len(cpus)])
            for index, process in enumerate(processes)
        ]
        for future in futures:
            try:
                results.append(future.result())
            except Exception as exc:
                errors.append(f"{type(exc).__name__}: {exc}")
    return results, errors


def git_output(repo_root: Path, *args: str) -> str | None:
    result = subprocess.run(["git", *args], cwd=repo_root, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def write_artifact_inventory(output_root: Path) -> None:
    rows = []
    for path in sorted(output_root.rglob("*")):
        if path.is_file() and path.name != "artifact-inventory.json":
            rows.append({
                "path": path.relative_to(output_root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
    (output_root / "artifact-inventory.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def default_manifest_linter(manifest_path: Path) -> Iterable[Any]:
    try:
        module = importlib.import_module("lint_benchmark_v13")
    except ModuleNotFoundError:
        module = importlib.import_module("scripts.lint_benchmark_v13")
    return module.lint_manifest(manifest_path)


def execute(
    args: argparse.Namespace,
    manifest_linter: Callable[[Path], Iterable[Any]] | None = None,
) -> int:
    repo_root = ROOT.resolve()
    manifest_path = (
        relative_path(repo_root, str(args.manifest), "manifest_path")
        if args.require_git_ancestry else args.manifest.resolve()
    )
    output_root = args.output.resolve()
    if args.require_git_ancestry:
        try:
            output_root.relative_to(repo_root)
        except ValueError:
            pass
        else:
            raise ContractError("isolated execution output must be outside the campaign checkout")
    output_root.mkdir(parents=True, exist_ok=True)
    if any(output_root.iterdir()):
        raise ContractError("output directory must be empty")

    findings = list((manifest_linter or default_manifest_linter)(manifest_path))
    if findings:
        details = "; ".join(
            f"{getattr(item, 'code', 'LINT')} {getattr(item, 'path', '$')}: "
            f"{getattr(item, 'message', str(item))}" for item in findings
        )
        raise ContractError(f"benchmark manifest does not lint cleanly: {details}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "c5k4-benchmark-1.3":
        raise ContractError("runner accepts only a Method v1.3 manifest")
    if manifest["phase"] not in {"C1_SELECTED", "EVALUATING"}:
        raise ContractError("execution requires phase C1_SELECTED or EVALUATING")
    if args.mode not in MODES:
        raise ContractError(f"unknown job mode: {args.mode}")
    arm = None if args.arm == "NONE" else args.arm
    cluster = find_cluster(manifest, args.cluster_id)
    reference = contract_reference(cluster, args.mode, arm)
    contract_path = resolve_reference(manifest_path, reference["path"])
    if args.require_git_ancestry:
        try:
            contract_path.relative_to(repo_root)
        except ValueError as exc:
            raise ContractError("frozen contract must be inside the checked-out campaign commit") from exc
    if not contract_path.is_file() or not SHA256_RE.fullmatch(reference["sha256"]):
        raise ContractError("frozen contract reference is invalid")
    actual_contract_sha = sha256_file(contract_path)
    if actual_contract_sha.lower() != reference["sha256"].lower():
        raise ContractError("frozen contract SHA-256 mismatch")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    validate_contract(manifest, cluster, contract, args.mode, arm, repo_root)

    head = git_output(repo_root, "rev-parse", "HEAD")
    chronology = manifest["chronology"]
    c1_commit = chronology.get("c1_attestation_commit", chronology.get("c1_commit"))
    if args.require_git_ancestry:
        if head is None or not isinstance(c1_commit, str) or not OID_RE.fullmatch(c1_commit):
            raise ContractError("cannot establish frozen C1 Git ancestry")
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", c1_commit, head], cwd=repo_root, check=False
        )
        if ancestry.returncode != 0:
            raise ContractError("checked-out execution ref does not descend from frozen C1")
        status = git_output(repo_root, "status", "--porcelain=v1", "--untracked-files=all")
        if status:
            raise ContractError("v1.3 execution requires a clean, immutable campaign checkout")

    ledger_path = output_root / "runtime-ledger.jsonl"
    metadata = {
        "schema_version": "c5k4-benchmark-run-artifact-1.3",
        "dry_run": args.dry_run,
        "benchmark_id": manifest["benchmark_id"],
        "cluster_id": cluster["cluster_id"],
        "job_mode": args.mode,
        "arm": arm,
        "manifest_path": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "contract_path": str(contract_path),
        "contract_sha256": actual_contract_sha,
        "runner_sha256": sha256_file(Path(__file__)),
        "repository_head": head,
        "frozen_c1_attestation_commit": c1_commit,
        "available_cpus": sorted(os.sched_getaffinity(0)),
        "process_tree_count": contract["process_tree_count"],
        "process_tree_wall_cap_seconds": 60,
        "cpu_budget_seconds": contract["cpu_budget_seconds"],
        "continue_after_crossing": True,
        "cross_arm_result_inputs": [],
        "results_embargo": "UNTIL_ALL_DISCOVERY_ARMS_TERMINATE",
        "network_isolation": "sudo unshare network and PID namespaces with kill-child",
        "environment_policy": "fixed allowlist; no runner or GitHub secrets inherited",
        "started_at_utc": utc_now(),
    }
    (output_root / "run-metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    append_ledger(ledger_path, "JOB_STARTED", metadata)

    results: list[dict[str, Any]] = []
    infrastructure_errors: list[str] = []
    if not args.dry_run:
        for executable in ("taskset", "sudo", "unshare", "/usr/bin/env", "/usr/bin/time"):
            if shutil.which(executable) is None:
                raise ContractError(f"required isolation executable is unavailable: {executable}")
        preflight = subprocess.run(
            [
                "sudo", "-n", "unshare", "--net", "--pid", "--fork", "--kill-child=KILL",
                "--setuid", str(os.getuid()), "--setgid", str(os.getgid()), "true",
            ],
            env=sanitized_environment(
                output_root, "preflight", manifest["benchmark_id"], cluster["cluster_id"], args.mode, arm
            ),
            capture_output=True,
            text=True,
            check=False,
        )
        if preflight.returncode != 0:
            raise ContractError(f"process-tree isolation preflight failed closed: {preflight.stderr.strip()}")
        cpus = sorted(os.sched_getaffinity(0))
        worker = lambda process, cpu: run_process(  # noqa: E731 - injectable closure
            process, cpu, output_root, repo_root, contract, ledger_path
        )
        results, infrastructure_errors = run_all_processes(contract["processes"], cpus, worker)

    status_after = git_output(repo_root, "status", "--porcelain=v1", "--untracked-files=all")
    total_cpu = sum(
        row.get("time", {}).get("cpu_seconds", 0)
        for row in results
        if isinstance(row.get("time", {}).get("cpu_seconds", 0), (int, float))
    )
    summary = {
        "dry_run": args.dry_run,
        "expected_process_tree_count": contract["process_tree_count"],
        "completed_process_tree_count": len(results),
        "timed_out_processes": sorted(row["process_id"] for row in results if row["timed_out"]),
        "nonzero_processes": sorted(row["process_id"] for row in results if row["returncode"] != 0),
        "cpu_budget_violations": sorted(
            row["process_id"] for row in results if row["cpu_budget_violation"]
        ),
        "observed_cpu_seconds": total_cpu,
        "charged_cpu_seconds_upper_bound": contract["process_tree_count"] * 60,
        "contract_cpu_budget_seconds": contract["cpu_budget_seconds"],
        "all_frozen_processes_submitted": args.dry_run or len(results) + len(infrastructure_errors) == contract["process_tree_count"],
        "continued_after_crossing_by_construction": True,
        "infrastructure_errors": infrastructure_errors,
        "repository_status_after": status_after,
        "finished_at_utc": utc_now(),
    }
    append_ledger(ledger_path, "JOB_FINISHED", summary)
    verify_ledger(ledger_path)
    summary["runtime_ledger_sha256"] = sha256_file(ledger_path)
    (output_root / "run-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_artifact_inventory(output_root)
    print(json.dumps(summary, indent=2, sort_keys=True))
    failed = bool(
        infrastructure_errors
        or summary["cpu_budget_violations"]
        or not summary["all_frozen_processes_submitted"]
        or total_cpu > contract["cpu_budget_seconds"] + 0.05
    )
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--cluster-id", required=True)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--arm", choices=(*ARMS, "NONE"), default="NONE")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--require-git-ancestry", action="store_true")
    args = parser.parse_args(argv)
    try:
        return execute(args)
    except (ContractError, OSError, json.JSONDecodeError, jsonschema.ValidationError) as exc:
        args.output.mkdir(parents=True, exist_ok=True)
        failure = {"error": type(exc).__name__, "message": str(exc), "failed_at_utc": utc_now()}
        (args.output / "orchestration-error.json").write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"benchmark orchestration rejected: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
