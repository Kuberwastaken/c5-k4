#!/usr/bin/env python3
"""Resolve checkpoint roles only through a published Method v1.5 P1 closure.

The production entry point has no status/authority override.  It authenticates
P1T from the frozen public remote-tracking ref, authenticates P1A from P1T's
sole parent, and reads component bytes from that exact tree.  Worktree and
index copies must still equal the committed P1 bytes before a role is exposed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any

import jsonschema


ROOT = Path(__file__).parents[1].resolve()
PUBLIC_ORIGIN = "https://github.com/Kuberwastaken/c5-k4.git"
PUBLIC_REF = "refs/remotes/origin/main"
P1_BUILDER_PATH = "scripts/build_benchmark_v15_p1.py"
P1_SCHEMA_ROLE = "p1_schema"
MANIFEST_ROLE = "checkpoint_component_manifest"
MANIFEST_SCHEMA_ROLE = "checkpoint_component_manifest_schema"
OUTPUT_SCHEMA = "c5k4-method-v1.5-p1-role-resolution-1.0"
READINESS_SCHEMA = "c5k4-method-v1.5-p1-role-resolution-readiness-1.0"
OID = re.compile(r"^[0-9a-f]{40}$")
SHA = re.compile(r"^[0-9a-f]{64}$")
SAFE_ENV = {
    "PATH": "/usr/bin:/bin", "HOME": "/nonexistent-c5k4-v15-role-resolution",
    "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_TERMINAL_PROMPT": "0",
    "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_REPLACE_OBJECTS": "1",
}
SAFE_CONFIG = (
    "-c", "core.hooksPath=/dev/null", "-c", "protocol.file.allow=never",
    "-c", "credential.helper=", "-c", "core.fsmonitor=false",
)


class RoleResolutionError(ValueError):
    """The supplied repository state does not prove an exact P1 role closure."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw: bytes, label: str) -> dict[str, Any]:
    def pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, child in rows:
            if key in value:
                raise RoleResolutionError(f"{label} has duplicate JSON key {key!r}")
            value[key] = child
        return value
    try:
        value = json.loads(raw, object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RoleResolutionError(f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise RoleResolutionError(f"{label} is not one JSON object")
    return value


class GitRepo:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def run(self, *args: str, check: bool = True) -> bytes:
        result = subprocess.run(
            ["/usr/bin/git", *SAFE_CONFIG, "-C", str(self.root), *args],
            env=SAFE_ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False,
        )
        if check and result.returncode:
            detail = result.stderr.decode("utf-8", "replace").strip()
            raise RoleResolutionError(f"Git failed ({' '.join(args)}): {detail}")
        return result.stdout if result.returncode == 0 else b""

    def exact_commit(self, value: Any, label: str) -> str:
        if not isinstance(value, str) or OID.fullmatch(value) is None:
            raise RoleResolutionError(f"{label} must be an exact lowercase Git OID")
        resolved = self.run("rev-parse", "--verify", f"{value}^{{commit}}").decode().strip()
        if resolved != value:
            raise RoleResolutionError(f"{label} is not an exact commit OID")
        return value

    def blob(self, commit: str, path: str) -> bytes:
        normalized_path(path)
        return self.run("show", f"{commit}:{path}")


def normalized_path(value: Any) -> str:
    if not isinstance(value, str):
        raise RoleResolutionError("component path is not a string")
    pure = PurePosixPath(value)
    if pure.is_absolute() or not pure.parts or ".." in pure.parts or pure.as_posix() != value:
        raise RoleResolutionError(f"component path is not normalized: {value!r}")
    return value


def schema_validate(value: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    try:
        jsonschema.Draft7Validator.check_schema(schema)
        jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker()).validate(value)
    except jsonschema.SchemaError as exc:
        raise RoleResolutionError(f"{label} schema is invalid: {exc.message}") from exc
    except jsonschema.ValidationError as exc:
        trail = ".".join(map(str, exc.absolute_path)) or "$"
        raise RoleResolutionError(f"{label} fails schema at {trail}: {exc.message}") from exc


def _record(mapping: dict[str, Any], role: str, closure: str) -> dict[str, Any]:
    row = mapping.get(role)
    if not isinstance(row, dict):
        raise RoleResolutionError(f"missing {closure} role {role}")
    expected = {"path", "sha256", "content_class"}
    if closure == "INHERITED_V1_4":
        expected |= {"source_commit", "source_content_class"}
    if set(row) != expected or SHA.fullmatch(str(row.get("sha256", ""))) is None:
        raise RoleResolutionError(f"{closure} role {role} has an inexact binding")
    normalized_path(row["path"])
    return row


def _load_authenticated_builder(repo: GitRepo, p1a_commit: str,
                                native: dict[str, Any]) -> Any:
    row = _record(native, "p1_builder", "NATIVE_V1_5")
    if row["path"] != P1_BUILDER_PATH:
        raise RoleResolutionError("P1 builder occupies the wrong frozen path")
    raw = repo.blob(p1a_commit, row["path"])
    if sha256(raw) != row["sha256"]:
        raise RoleResolutionError("P1 builder committed digest mismatch")
    _require_clean_copy(repo, p1a_commit, row["path"], row["sha256"])
    path = repo.root / row["path"]
    spec = importlib.util.spec_from_file_location("authenticated_v15_p1_builder", path)
    if spec is None or spec.loader is None:
        raise RoleResolutionError("cannot load authenticated P1 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _require_clean_copy(repo: GitRepo, commit: str, path: str, expected: str) -> None:
    candidate = repo.root / path
    if not candidate.is_file() or candidate.is_symlink():
        raise RoleResolutionError(f"resolved role path is absent or non-regular: {path}")
    if sha256(candidate.read_bytes()) != expected:
        raise RoleResolutionError(f"resolved role has uncommitted/wrong-tree bytes: {path}")
    head = repo.run("rev-parse", "HEAD").decode().strip()
    if sha256(repo.blob(head, path)) != expected:
        raise RoleResolutionError(f"HEAD has wrong-tree bytes for resolved role: {path}")
    index_oid = repo.run("ls-files", "-s", "--", path).decode().split()
    if len(index_oid) != 4 or index_oid[3] != path:
        raise RoleResolutionError(f"resolved role is not uniquely present in the index: {path}")
    if sha256(repo.run("cat-file", "blob", index_oid[1])) != expected:
        raise RoleResolutionError(f"index has uncommitted/wrong-tree bytes for resolved role: {path}")
    if repo.blob(commit, path) != candidate.read_bytes():
        raise RoleResolutionError(f"resolved role differs from exact P1A tree: {path}")


def _selectors(value: Any, trail: tuple[str, ...] = ()) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    if isinstance(value, dict):
        if set(value) == {"closure", "role"}:
            closure, role = value["closure"], value["role"]
            if closure not in {"NATIVE_V1_5", "INHERITED_V1_4"} or not isinstance(role, str) or not role:
                raise RoleResolutionError(f"invalid selector at {'.'.join(trail)}")
            rows.append((closure, role, ".".join(trail)))
        else:
            for key, child in value.items():
                rows.extend(_selectors(child, (*trail, key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_selectors(child, (*trail, str(index))))
    return rows


def _resolve_published_roles(repository: Path, p1t_commit: str, p1t_path: str,
                             *, expected_origin: str,
                             publication_ref: str) -> dict[str, Any]:
    """Hermetic implementation; origin/ref injection is contract-test-only."""
    repo = GitRepo(repository)
    p1t_commit = repo.exact_commit(p1t_commit, "P1T commit")
    p1t_path = normalized_path(p1t_path)
    if repo.run("remote", "get-url", "origin").decode().strip() != expected_origin:
        raise RoleResolutionError("origin is not the frozen public repository")
    published_tip = repo.run("rev-parse", "--verify", publication_ref).decode().strip()
    repo.exact_commit(published_tip, "published tip")
    if repo.run("merge-base", "--is-ancestor", p1t_commit, published_tip, check=False) == b"":
        # Successful --is-ancestor also has empty stdout; inspect explicitly.
        result = subprocess.run(
            ["/usr/bin/git", *SAFE_CONFIG, "-C", str(repo.root), "merge-base",
             "--is-ancestor", p1t_commit, published_tip], env=SAFE_ENV,
             stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        if result.returncode != 0:
            raise RoleResolutionError("P1T is not published on the frozen public ref")
    parents = repo.run("show", "-s", "--format=%P", p1t_commit).decode().split()
    if len(parents) != 1:
        raise RoleResolutionError("P1T must have exactly one parent")
    p1a_commit = repo.exact_commit(parents[0], "P1A commit")
    p1t_raw = repo.blob(p1t_commit, p1t_path)
    p1t = strict_json(p1t_raw, "P1T")
    if p1t.get("artifact_kind") != "P1T" or p1t.get("p1a_commit") != p1a_commit:
        raise RoleResolutionError("P1T does not bind its sole P1A parent")
    policy = p1t.get("attestation_policy")
    if not isinstance(policy, dict) or policy.get("allowed_p1t_changed_paths") != [p1t_path]:
        raise RoleResolutionError("P1T does not freeze its sole changed path")
    changed = repo.run("diff-tree", "--no-commit-id", "--name-status", "-r", p1t_commit).decode().splitlines()
    if changed != [f"A\t{p1t_path}"]:
        raise RoleResolutionError("P1T commit is not a one-path add-only attestation")
    p1a_ref = p1t.get("p1a")
    if not isinstance(p1a_ref, dict) or set(p1a_ref) != {"path", "sha256"}:
        raise RoleResolutionError("P1T has an invalid P1A reference")
    p1a_path = normalized_path(p1a_ref["path"])
    p1a_raw = repo.blob(p1a_commit, p1a_path)
    if sha256(p1a_raw) != p1a_ref.get("sha256"):
        raise RoleResolutionError("P1T does not authenticate exact committed P1A bytes")
    p1a = strict_json(p1a_raw, "P1A")
    if p1a.get("artifact_kind") != "P1A" or p1a.get("authority") != "AUTHORITATIVE_P1":
        raise RoleResolutionError("P1A authority is invalid")
    native = p1a.get("components")
    inherited_container = p1a.get("inherited_v1_4")
    inherited = inherited_container.get("components") if isinstance(inherited_container, dict) else None
    if not isinstance(native, dict) or not isinstance(inherited, dict):
        raise RoleResolutionError("P1A component closures are missing")
    if set(native) & set(inherited):
        raise RoleResolutionError("a P1 role is ambiguous across closures")
    builder = _load_authenticated_builder(repo, p1a_commit, native)
    if set(native) != set(builder.NATIVE_COMPONENTS):
        raise RoleResolutionError("P1A has missing or extra native roles")
    if set(inherited) != set(builder.INHERITED_V1_4_ROLES):
        raise RoleResolutionError("P1A has missing or extra inherited roles")
    if inherited_container.get("selected_roles") != list(builder.INHERITED_V1_4_ROLES):
        raise RoleResolutionError("P1A inherited role order is not the frozen closure")

    p1_schema_row = _record(native, P1_SCHEMA_ROLE, "NATIVE_V1_5")
    p1_schema_raw = repo.blob(p1a_commit, p1_schema_row["path"])
    if sha256(p1_schema_raw) != p1_schema_row["sha256"]:
        raise RoleResolutionError("committed P1 schema digest mismatch")
    _require_clean_copy(repo, p1a_commit, p1_schema_row["path"], p1_schema_row["sha256"])
    schema_validate(p1a, strict_json(p1_schema_raw, "P1 schema"), "P1A")
    schema_validate(p1t, strict_json(p1_schema_raw, "P1 schema"), "P1T")

    manifest_row = _record(native, MANIFEST_ROLE, "NATIVE_V1_5")
    manifest_schema_row = _record(native, MANIFEST_SCHEMA_ROLE, "NATIVE_V1_5")
    manifest_raw = repo.blob(p1a_commit, manifest_row["path"])
    manifest_schema_raw = repo.blob(p1a_commit, manifest_schema_row["path"])
    if sha256(manifest_raw) != manifest_row["sha256"] or sha256(manifest_schema_raw) != manifest_schema_row["sha256"]:
        raise RoleResolutionError("checkpoint manifest/schema committed digest mismatch")
    _require_clean_copy(repo, p1a_commit, manifest_row["path"], manifest_row["sha256"])
    _require_clean_copy(repo, p1a_commit, manifest_schema_row["path"], manifest_schema_row["sha256"])
    manifest = strict_json(manifest_raw, "checkpoint component manifest")
    schema_validate(manifest, strict_json(manifest_schema_raw, "checkpoint manifest schema"),
                    "checkpoint component manifest")
    selectors = _selectors(manifest)
    if not selectors:
        raise RoleResolutionError("checkpoint manifest has no role selectors")

    resolved: dict[tuple[str, str], dict[str, Any]] = {}
    selector_paths: dict[tuple[str, str], list[str]] = {}
    used_paths: dict[str, tuple[str, str]] = {}
    for closure, role, selector_path in selectors:
        mapping = native if closure == "NATIVE_V1_5" else inherited
        row = _record(mapping, role, closure)
        key = (closure, role)
        prior_path_role = used_paths.get(row["path"])
        if prior_path_role is not None and prior_path_role != key:
            raise RoleResolutionError(f"component path ambiguously aliases roles: {row['path']}")
        used_paths[row["path"]] = key
        if key in resolved and resolved[key] != row:
            raise RoleResolutionError(f"duplicate selector resolves inconsistently: {closure}/{role}")
        resolved[key] = row
        selector_paths.setdefault(key, []).append(selector_path)
    rows: list[dict[str, Any]] = []
    for closure, role in sorted(resolved):
        row = resolved[(closure, role)]
        raw = repo.blob(p1a_commit, row["path"])
        if sha256(raw) != row["sha256"]:
            raise RoleResolutionError(f"P1 tree digest mismatch for {closure}/{role}")
        _require_clean_copy(repo, p1a_commit, row["path"], row["sha256"])
        rows.append({
            "closure": closure, "role": role, "path": row["path"],
            "sha256": row["sha256"], "content_class": row["content_class"],
            "selector_paths": sorted(selector_paths[(closure, role)]),
        })
    proof = {
        "schema": OUTPUT_SCHEMA,
        "status": "AUTHENTICATED_PUBLISHED_P1_ROLE_CLOSURE",
        "operational": True,
        "target_data_present": False,
        "publication": {
            "repository": expected_origin, "ref": publication_ref,
            "published_tip_commit": published_tip,
        },
        "p1": {
            "p1a_commit": p1a_commit, "p1a_path": p1a_path,
            "p1a_sha256": sha256(p1a_raw), "p1t_commit": p1t_commit,
            "p1t_path": p1t_path, "p1t_sha256": sha256(p1t_raw),
        },
        "manifest": {"path": manifest_row["path"], "sha256": manifest_row["sha256"]},
        "resolved_role_count": len(rows),
        "resolved_roles": rows,
    }
    proof["resolution_sha256"] = sha256(canonical_json(proof))
    return proof


def resolve_published_roles(repository: Path, p1t_commit: str,
                            p1t_path: str) -> dict[str, Any]:
    """Resolve roles against the non-overridable production origin/ref."""
    return _resolve_published_roles(
        repository, p1t_commit, p1t_path,
        expected_origin=PUBLIC_ORIGIN, publication_ref=PUBLIC_REF,
    )


def readiness() -> dict[str, Any]:
    return {
        "schema": READINESS_SCHEMA,
        "status": "PRE_P1_NO_AUTHENTIC_PUBLISHED_BINDING",
        "operational": False,
        "caller_operational_override_accepted": False,
        "target_data_present": False,
        "required_binding": "EXACT_PUBLIC_P1T_TO_SOLE_PARENT_P1A_COMPONENT_CLOSURE",
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, sort_keys=True, indent=2).encode() + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    status = commands.add_parser("readiness")
    status.add_argument("--output", type=Path, required=True)
    resolve = commands.add_parser("resolve")
    resolve.add_argument("--p1t-commit", required=True)
    resolve.add_argument("--p1t-path", required=True)
    resolve.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "readiness":
            write_json(args.output, readiness())
            return 2
        proof = resolve_published_roles(ROOT, args.p1t_commit, args.p1t_path)
        write_json(args.output, proof)
    except (OSError, RoleResolutionError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
