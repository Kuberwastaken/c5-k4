#!/usr/bin/env python3
"""Run one content-addressed Method v1.1 benchmark job.

The script is deliberately an orchestration layer, not a search driver.  It
resolves the selected contract from a lint-clean frozen manifest, checks that
the contract repeats the frozen seed/grid/transformation and budgets exactly,
then launches its already-enumerated processes concurrently.  Each process
tree is pinned to one CPU and placed in a network namespace, so sixty seconds
of wall time also bounds that tree to at most sixty CPU-seconds.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema

import lint_benchmark_v11 as benchmark_linter


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SCHEMA = ROOT / "schemas" / "benchmark-run-contract-v1.schema.json"
ARMS = ("CATALOGUE", "GENERIC", "WALL_NAVIGATION")
MODES = ("DISCOVERY_ARM", "SHARED_ANALYSIS", "INDEPENDENT_VERIFICATION")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
OID_RE = re.compile(r"^[0-9a-fA-F]{40,64}$")
SAFE_PROCESS_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


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


def find_cluster(manifest: dict[str, Any], cluster_id: str) -> dict[str, Any]:
    matches = [cluster for cluster in manifest["clusters"] if cluster["cluster_id"] == cluster_id]
    if len(matches) != 1:
        raise ContractError(f"cluster_id must resolve exactly once; found {len(matches)}")
    return matches[0]


def contract_reference(
    cluster: dict[str, Any], mode: str, arm: str | None
) -> dict[str, str]:
    if mode == "DISCOVERY_ARM":
        if arm not in ARMS:
            raise ContractError("DISCOVERY_ARM requires one frozen discovery arm")
        if cluster.get("arms") is None:
            raise ContractError("cluster has no frozen discovery arms")
        return cluster["arms"][arm]["contract"]
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


def validate_contract(
    manifest: dict[str, Any],
    cluster: dict[str, Any],
    contract: dict[str, Any],
    mode: str,
    arm: str | None,
    repo_root: Path,
) -> None:
    validate_contract_shape(contract)
    if contract["benchmark_id"] != manifest["benchmark_id"]:
        raise ContractError("contract benchmark_id differs from manifest")
    if contract["cluster_id"] != cluster["cluster_id"]:
        raise ContractError("contract cluster_id differs from requested cluster")
    if contract["job_mode"] != mode or contract["arm"] != arm:
        raise ContractError("contract mode/arm differs from requested job")
    if contract["no_adaptation"] is not True:
        raise ContractError("contract must prohibit adaptation")
    if contract["network_policy"] != "DENY":
        raise ContractError("contract must deny network access")
    if contract["process_wall_cap_seconds"] != 60:
        raise ContractError("every process must have an exact 60-second hard wall cap")
    if len(contract["processes"]) != contract["process_count"]:
        raise ContractError("process list length differs from frozen process_count")

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

    count = contract["process_count"]
    cpu_budget = contract["cpu_budget_seconds"]
    if cpu_budget > count * 60:
        raise ContractError("CPU budget exceeds process_count times the hard wall cap")

    if mode == "DISCOVERY_ARM":
        frozen = cluster["arms"][arm]
        global_budget = manifest["budgets"]["discovery_arm"]
        expected = (8, 60, global_budget["cpu_budget_seconds"])
        observed = (count, contract["process_wall_cap_seconds"], cpu_budget)
        if expected != (8, 60, 480) or observed != expected:
            raise ContractError("discovery execution must be exactly 8 x 60s and 480 CPU-seconds")
        for key in ("seed", "parameter_grid", "transformation_id", "no_adaptation"):
            if contract[key] != frozen[key]:
                raise ContractError(f"contract {key} differs from the frozen arm")
        if cluster.get("runnable") is not True:
            raise ContractError("discovery arm requires a runnable cluster")
        if frozen["status"] != "PENDING":
            raise ContractError("runner only starts a discovery arm frozen as PENDING")
    elif mode == "SHARED_ANALYSIS":
        budget = manifest["budgets"]["shared_analysis"]
        if budget["process_wall_cap_seconds"] != 60:
            raise ContractError("manifest shared-analysis wall cap must equal 60 seconds")
        if cpu_budget > budget["cpu_budget_seconds"] or count > 10:
            raise ContractError("shared analysis exceeds its 600 CPU-second cap")
        if cluster.get("evaluation_started_at_utc") is not None:
            raise ContractError("shared analysis cannot start after cluster evaluation")
        if cluster.get("arms") is not None and any(
            frozen["status"] != "PENDING" for frozen in cluster["arms"].values()
        ):
            raise ContractError("shared analysis cannot run after a discovery arm starts")
    else:
        budget = manifest["budgets"]["independent_verification"]
        expected = (2, 60, 120)
        observed = (count, contract["process_wall_cap_seconds"], cpu_budget)
        frozen = (budget["process_count"], budget["process_wall_cap_seconds"], budget["cpu_budget_seconds"])
        if frozen != expected or observed != expected:
            raise ContractError("independent verification must be exactly 2 x 60s and 120 CPU-seconds")
        if cluster.get("arms") is None or any(
            item["status"] != "TERMINATED" for item in cluster["arms"].values()
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
        "wall_cap_seconds": 60,
    }
    (process_dir / "invocation.json").write_text(
        json.dumps(invocation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    argv = [
        "taskset",
        "-c",
        str(cpu),
        "sudo",
        "-n",
        "unshare",
        "--net",
        "--setuid",
        str(os.getuid()),
        "--setgid",
        str(os.getgid()),
        "/usr/bin/time",
        "--quiet",
        "-f",
        "user_seconds=%U\nsystem_seconds=%S\nmax_rss_kb=%M\nexit_status=%x",
        "-o",
        str(time_path),
        "--",
        *process["argv"],
    ]
    environment = sanitized_environment(
        process_dir,
        process_id,
        contract["benchmark_id"],
        contract["cluster_id"],
        contract["job_mode"],
        contract["arm"],
    )
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
    return result


def git_output(repo_root: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", *args], cwd=repo_root, text=True, capture_output=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def write_artifact_inventory(output_root: Path) -> None:
    rows = []
    for path in sorted(output_root.rglob("*")):
        if path.is_file() and path.name != "artifact-inventory.json":
            rows.append(
                {
                    "path": path.relative_to(output_root).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    (output_root / "artifact-inventory.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def execute(args: argparse.Namespace) -> int:
    repo_root = ROOT.resolve()
    if args.require_git_ancestry:
        manifest_path = relative_path(repo_root, str(args.manifest), "manifest_path")
    else:
        manifest_path = args.manifest.resolve()
    output_root = args.output.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    if any(output_root.iterdir()):
        raise ContractError("output directory must be empty")

    findings = benchmark_linter.lint_manifest(manifest_path)
    if findings:
        details = "; ".join(f"{item.code} {item.path}: {item.message}" for item in findings)
        raise ContractError(f"benchmark manifest does not lint cleanly: {details}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["phase"] not in {"C1_SELECTED", "EVALUATING"}:
        raise ContractError("execution requires phase C1_SELECTED or EVALUATING")
    if args.mode not in MODES:
        raise ContractError(f"unknown job mode: {args.mode}")
    arm = None if args.arm == "NONE" else args.arm
    cluster = find_cluster(manifest, args.cluster_id)
    reference = contract_reference(cluster, args.mode, arm)
    contract_path = benchmark_linter.resolve_path(manifest_path, reference["path"]).resolve()
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
    c1_commit = manifest["chronology"]["c1_commit"]
    if args.require_git_ancestry:
        if head is None or not isinstance(c1_commit, str) or not OID_RE.fullmatch(c1_commit):
            raise ContractError("cannot establish frozen C1 Git ancestry")
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", c1_commit, head], cwd=repo_root, check=False
        )
        if ancestry.returncode != 0:
            raise ContractError("checked-out execution ref does not descend from frozen C1")

    status_before = git_output(repo_root, "status", "--porcelain=v1", "--untracked-files=all")
    (output_root / "repository-status-before.txt").write_text(
        (status_before or "") + "\n", encoding="utf-8"
    )
    metadata = {
        "schema_version": "c5k4-benchmark-run-artifact-1",
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
        "frozen_c1_commit": c1_commit,
        "available_cpus": sorted(os.sched_getaffinity(0)),
        "process_count": contract["process_count"],
        "process_wall_cap_seconds": 60,
        "cpu_budget_seconds": contract["cpu_budget_seconds"],
        "network_isolation": "sudo -n unshare --net with immediate uid/gid drop",
        "environment_policy": "fixed allowlist; no runner or GitHub secrets inherited",
        "started_at_utc": utc_now(),
    }
    (output_root / "run-metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    results: list[dict[str, Any]] = []
    infrastructure_error: str | None = None
    if not args.dry_run:
        for executable in ("taskset", "sudo", "unshare", "/usr/bin/time"):
            if shutil.which(executable) is None:
                raise ContractError(f"required isolation executable is unavailable: {executable}")
        preflight = subprocess.run(
            [
                "sudo",
                "-n",
                "unshare",
                "--net",
                "--setuid",
                str(os.getuid()),
                "--setgid",
                str(os.getgid()),
                "true",
            ],
            env=sanitized_environment(output_root, "preflight", manifest["benchmark_id"], cluster["cluster_id"], args.mode, arm),
            capture_output=True,
            text=True,
            check=False,
        )
        if preflight.returncode != 0:
            raise ContractError(f"network-isolation preflight failed closed: {preflight.stderr.strip()}")

        cpus = sorted(os.sched_getaffinity(0))
        with concurrent.futures.ThreadPoolExecutor(max_workers=contract["process_count"]) as pool:
            futures = [
                pool.submit(run_process, process, cpus[index % len(cpus)], output_root, repo_root, contract)
                for index, process in enumerate(contract["processes"])
            ]
            for future in futures:
                try:
                    results.append(future.result())
                except Exception as exc:  # record orchestration loss without dropping other logs
                    infrastructure_error = f"{type(exc).__name__}: {exc}"
    status_after = git_output(repo_root, "status", "--porcelain=v1", "--untracked-files=all")
    (output_root / "repository-status-after.txt").write_text(
        (status_after or "") + "\n", encoding="utf-8"
    )
    tracked_diff = git_output(repo_root, "diff", "--binary", "--no-ext-diff")
    (output_root / "repository-after.diff").write_text(
        (tracked_diff or "") + "\n", encoding="utf-8"
    )
    summary = {
        "dry_run": args.dry_run,
        "expected_process_count": contract["process_count"],
        "completed_process_count": len(results),
        "timed_out_processes": sorted(row["process_id"] for row in results if row["timed_out"]),
        "nonzero_processes": sorted(row["process_id"] for row in results if row["returncode"] != 0),
        "cpu_budget_violations": sorted(row["process_id"] for row in results if row["cpu_budget_violation"]),
        "charged_cpu_seconds_upper_bound": contract["process_count"] * 60,
        "contract_cpu_budget_seconds": contract["cpu_budget_seconds"],
        "infrastructure_error": infrastructure_error,
        "repository_status_before": status_before,
        "repository_status_after": status_after,
        "repository_status_changed": status_before != status_after,
        "finished_at_utc": utc_now(),
    }
    (output_root / "run-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_artifact_inventory(output_root)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 1 if infrastructure_error or summary["cpu_budget_violations"] or summary["repository_status_changed"] else 0


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
