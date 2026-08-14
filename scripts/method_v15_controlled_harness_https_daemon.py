#!/usr/bin/env python3
"""Silent HTTPS adapter for the target-blind Method v1.5 harness boundary.

The committed configuration is PRE-P1 and cannot bind a listener.  Operational
callers must inject the OIDC verifier, public-chain binding provider, and real
executor used by ``method_v15_controlled_harness_service.py``.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sqlite3
import ssl
import subprocess
import threading
from typing import Any, Iterable, Mapping, Protocol
from urllib.parse import urlsplit

from jsonschema import Draft7Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DAEMON_CONTRACT = ROOT / "results/benchmark/v1.5-protocol/controlled-harness-https-daemon-contract.json"
DAEMON_SCHEMA = ROOT / "schemas/benchmark-controlled-harness-https-daemon-contract-v1.5.schema.json"
ACTIVATION_SCHEMA = ROOT / "schemas/benchmark-operational-controlled-harness-activation-v1.5.schema.json"
SERVICE_PATH = Path(__file__).with_name("method_v15_controlled_harness_service.py")
_SPEC = importlib.util.spec_from_file_location("method_v15_controlled_harness_service", SERVICE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
SERVICE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(SERVICE)


class DaemonError(ValueError):
    """The transport or operational daemon contract failed closed."""


class SilentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise DaemonError("invalid daemon arguments")


class Providers(Protocol):
    verifier: SERVICE.JWKSVerifier
    executor: SERVICE.Executor

    def public_binding(self, *, raw_request: bytes, request_sha256: str) -> dict[str, Any]: ...


class SQLiteReplayLedger:
    """Durable atomic replay reservations; one connection/transaction per call."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS reservations ("
                "scheduled_for_utc TEXT PRIMARY KEY, request_sha256 TEXT NOT NULL UNIQUE, "
                "workflow_run_id TEXT NOT NULL)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def reserve(self, *, scheduled_for_utc: str, request_sha256: str, workflow_run_id: str) -> bool:
        with self._lock, self._connect() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    "INSERT INTO reservations VALUES (?, ?, ?)",
                    (scheduled_for_utc, request_sha256, workflow_run_id),
                )
                connection.execute("COMMIT")
                return True
            except sqlite3.IntegrityError:
                connection.execute("ROLLBACK")
                return False


def load_contract(path: Path = DAEMON_CONTRACT) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        schema = json.loads(DAEMON_SCHEMA.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DaemonError("invalid daemon contract") from exc
    errors = sorted(
        Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise DaemonError("invalid daemon contract")
    return value


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def object_digest(value: Mapping[str, Any], digest_key: str) -> str:
    return hashlib.sha256(canonical_json({key: item for key, item in value.items() if key != digest_key})).hexdigest()


def authenticate_activation(path: Path, expected_sha256: str) -> dict[str, Any]:
    """Authenticate canonical activation bytes against the P1-frozen unit digest."""
    if len(expected_sha256) != 64 or any(character not in "0123456789abcdef" for character in expected_sha256):
        raise DaemonError("invalid expected activation digest")
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
        schema = json.loads(ACTIVATION_SCHEMA.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DaemonError("invalid activation binding") from exc
    if not isinstance(value, dict) or canonical_json(value) != raw:
        raise DaemonError("activation binding bytes are not canonical")
    errors = sorted(
        Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise DaemonError("activation binding schema failure")
    actual = object_digest(value, "activation_inputs_sha256")
    if value["activation_inputs_sha256"] != actual or actual != expected_sha256:
        raise DaemonError("activation binding digest mismatch")
    return value


def activated_contract(policy: dict[str, Any], activation: dict[str, Any]) -> dict[str, Any]:
    """Derive the operational policy; no caller-supplied FROZEN daemon contract exists."""
    if policy["status"] != "PRE_P1_NONOPERATIONAL_NO_LISTENER" or policy["transport"]["listener_permitted"] is not False:
        raise DaemonError("committed daemon policy is not PRE-P1")
    if activation["oidc"]["audience_prefix"] != policy["oidc"]["audience_prefix"]:
        raise DaemonError("activation audience does not match daemon policy")
    selected = copy.deepcopy(policy)
    selected["status"] = "FROZEN_P1_EXECUTABLE"
    selected["transport"].update({
        "listener_permitted": True,
        "https_endpoint": activation["listener"]["https_endpoint"],
        "bind_address": activation["listener"]["bind_address"],
        "port": activation["listener"]["port"],
    })
    return selected


def activated_service_contract(daemon_contract: dict[str, Any], activation: dict[str, Any], tls_spki_sha256: str) -> dict[str, Any]:
    selected = SERVICE.load_object(SERVICE.CONTRACT_PATH, "P1 service contract")
    selected["transport"]["tls_spki_sha256"] = tls_spki_sha256
    selected["oidc"]["workflow_ref"] = activation["oidc"]["workflow_ref"]
    selected["binding"]["p1t_commit"] = activation["p1"]["commit"]
    return operational_service_contract(daemon_contract, selected)


def operational_service_contract(daemon_contract: dict[str, Any], service_contract: dict[str, Any]) -> dict[str, Any]:
    """Bind the existing pure verifier to the daemon's one canonical audience/path."""
    if daemon_contract["status"] != "FROZEN_P1_EXECUTABLE" or daemon_contract["transport"]["listener_permitted"] is not True:
        raise DaemonError("PRE-P1 daemon cannot listen")
    selected = copy.deepcopy(service_contract)
    selected["status"] = "FROZEN_P1_EXECUTABLE"
    selected["transport"]["listener_permitted"] = True
    selected["transport"]["https_endpoint"] = daemon_contract["transport"]["https_endpoint"]
    selected["oidc"]["audience_prefix"] = daemon_contract["oidc"]["audience_prefix"]
    if selected["oidc"]["audience_prefix"] != "c5k4-method-v1.5":
        raise DaemonError("noncanonical OIDC audience prefix")
    if daemon_contract["transport"]["path"] != "/v1/checkpoint":
        raise DaemonError("noncanonical checkpoint path")
    SERVICE.validate_contract(selected, require_operational=True)
    return selected


class HTTPSAdapter:
    """Transport-only adapter; it never decodes or logs request content."""

    def __init__(self, *, daemon_contract: dict[str, Any], service_contract: dict[str, Any], providers: Providers, replay_ledger: SERVICE.ReplayLedger, authorized_request_sha256: str | None = None) -> None:
        self.daemon_contract = daemon_contract
        self.service_contract = operational_service_contract(daemon_contract, service_contract)
        self.providers = providers
        self.replay_ledger = replay_ledger
        self.authorized_request_sha256 = authorized_request_sha256
        self._request_lock = threading.Lock()

    @staticmethod
    def _one(headers: Iterable[tuple[str, str]], name: str) -> str | None:
        values = [value for key, value in headers if key.casefold() == name.casefold()]
        return values[0] if len(values) == 1 else None

    def handle(self, *, method: str, path: str, headers: Iterable[tuple[str, str]], body: bytes) -> tuple[int, tuple[tuple[str, str], ...], bytes]:
        transport = self.daemon_contract["transport"]
        headers = tuple(headers)
        if method != transport["method"]:
            return self._failure(405)
        if path != transport["path"]:
            return self._failure(404)
        if self._one(headers, "Content-Type") != transport["content_type"]:
            return self._failure(415)
        length = self._one(headers, "Content-Length")
        if length is None or not length.isascii() or not length.isdecimal() or int(length) != len(body):
            return self._failure(400)
        if not body or len(body) > transport["max_request_bytes"]:
            return self._failure(413)
        digest = hashlib.sha256(body).hexdigest()
        if self.authorized_request_sha256 is not None and digest != self.authorized_request_sha256:
            return self._failure(401)
        if self._one(headers, transport["request_digest_header"]) != digest:
            return self._failure(400)
        authorization = self._one(headers, "Authorization")
        prefix = transport["authorization_scheme"] + " "
        if authorization is None or not authorization.startswith(prefix):
            return self._failure(401)
        token = authorization[len(prefix):]
        if not token or any(character.isspace() for character in token):
            return self._failure(401)
        try:
            with self._request_lock:
                binding = self.providers.public_binding(raw_request=body, request_sha256=digest)
                response = SERVICE.verify_and_execute(
                    raw_request=body,
                    oidc_token=token,
                    public_binding=binding,
                    verifier=self.providers.verifier,
                    replay_ledger=self.replay_ledger,
                    executor=self.providers.executor,
                    contract=self.service_contract,
                )
        except Exception:
            return self._failure(400)
        return 200, (("Content-Type", "application/json"), ("Content-Length", str(len(response)))), response

    @staticmethod
    def _failure(status: int) -> tuple[int, tuple[tuple[str, str], ...], bytes]:
        return status, (("Content-Length", "0"), ("Connection", "close")), b""


def tls13_context(certificate: Path, private_key: Path) -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    context.maximum_version = ssl.TLSVersion.TLSv1_3
    context.verify_mode = ssl.CERT_NONE
    context.load_cert_chain(str(certificate), str(private_key))
    return context


def handler_for(adapter: HTTPSAdapter) -> type[BaseHTTPRequestHandler]:
    class SilentHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, format: str, *args: object) -> None:
            return

        def do_POST(self) -> None:
            raw_length = self.headers.get("Content-Length")
            limit = adapter.daemon_contract["transport"]["max_request_bytes"]
            length = int(raw_length) if raw_length and raw_length.isascii() and raw_length.isdecimal() else 0
            body = self.rfile.read(min(length, limit + 1)) if length else b""
            self._write(adapter.handle(method="POST", path=self.path, headers=self.headers.raw_items(), body=body))

        def _write(self, response: tuple[int, tuple[tuple[str, str], ...], bytes]) -> None:
            status, headers, body = response
            reason = {200: "OK", 400: "Bad Request", 401: "Unauthorized", 404: "Not Found", 405: "Method Not Allowed", 413: "Content Too Large", 415: "Unsupported Media Type"}.get(status, "Error")
            self.wfile.write(f"HTTP/1.1 {status} {reason}\r\n".encode("ascii"))
            for key, value in headers:
                self.wfile.write(f"{key}: {value}\r\n".encode("ascii"))
            self.wfile.write(b"\r\n" + body)

        do_GET = do_DELETE = do_PATCH = do_PUT = lambda self: self._write(adapter._failure(405))

    return SilentHandler


def serve(*, adapter: HTTPSAdapter, certificate: Path, private_key: Path) -> None:
    transport = adapter.daemon_contract["transport"]
    server = HTTPServer((transport["bind_address"], transport["port"]), handler_for(adapter), bind_and_activate=False)
    server.socket = tls13_context(certificate, private_key).wrap_socket(server.socket, server_side=True)
    server.server_bind()
    server.server_activate()
    server.serve_forever(poll_interval=0.5)


def load_providers(path: Path, contract: dict[str, Any]) -> Providers:
    """Load the one P1-frozen provider bundle; importing it is an operational act."""
    try:
        spec = importlib.util.spec_from_file_location("c5k4_harness_providers", path)
        if spec is None or spec.loader is None:
            raise DaemonError("invalid provider module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        providers = module.build_providers(copy.deepcopy(contract))
        if not callable(providers.verifier) or not callable(providers.executor) or not callable(providers.public_binding):
            raise DaemonError("invalid provider bundle")
        return providers
    except Exception as exc:
        raise DaemonError("invalid provider bundle") from exc


def verified_file(path: Path, expected_sha256: str, label: str) -> None:
    try:
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise DaemonError(f"invalid {label}") from exc
    if actual != expected_sha256:
        raise DaemonError(f"invalid {label}")


def openssl(argv: list[str], *, stdin: bytes | None = None) -> bytes:
    try:
        result = subprocess.run(
            ["openssl", *argv], input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=10, env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise DaemonError("OpenSSL identity verification is unavailable") from exc
    if result.returncode != 0 or (not result.stdout and "-checkhost" not in argv):
        raise DaemonError("OpenSSL rejected the TLS identity")
    return result.stdout


def derive_tls_spki(certificate: Path, private_key: Path, https_endpoint: str) -> str:
    """Return curl's sha256//base64(DER SubjectPublicKeyInfo) pin."""
    hostname = urlsplit(https_endpoint).hostname
    if not hostname:
        raise DaemonError("HTTPS endpoint has no TLS hostname")
    certificate_public_pem = openssl(["x509", "-in", str(certificate), "-pubkey", "-noout"])
    certificate_public_der = openssl(["pkey", "-pubin", "-outform", "DER"], stdin=certificate_public_pem)
    private_public_der = openssl(["pkey", "-in", str(private_key), "-pubout", "-outform", "DER"])
    if certificate_public_der != private_public_der:
        raise DaemonError("TLS private key does not match certificate SPKI")
    openssl(["x509", "-in", str(certificate), "-checkhost", hostname, "-noout"])
    digest = hashlib.sha256(certificate_public_der).digest()
    return "sha256//" + base64.b64encode(digest).decode("ascii")


def main(argv: list[str] | None = None) -> int:
    parser = SilentParser(add_help=False)
    parser.add_argument("--activation-binding", type=Path)
    parser.add_argument("--expected-binding-sha256")
    parser.add_argument("--daemon-contract", type=Path)
    parser.add_argument("--control-socket", type=Path)
    parser.add_argument("--tls-certificate", type=Path)
    parser.add_argument("--tls-private-key", type=Path)
    parser.add_argument("--check-config", action="store_true")
    try:
        args = parser.parse_args(argv)
        if args.check_config:
            policy = load_contract()
            if policy["status"] != "PRE_P1_NONOPERATIONAL_NO_LISTENER":
                raise DaemonError("committed daemon policy is not PRE-P1")
            return 0
        if None in (args.activation_binding, args.expected_binding_sha256, args.daemon_contract, args.control_socket, args.tls_certificate, args.tls_private_key):
            return 2
        activation = authenticate_activation(args.activation_binding, args.expected_binding_sha256)
        if str(args.activation_binding) != activation["service"]["activation_binding_path"]:
            raise DaemonError("activation binding path does not match its authenticated content")
        if str(args.control_socket) != activation["service"]["control_socket_path"]:
            raise DaemonError("control socket is not activation-bound")
        if str(args.daemon_contract) != activation["service"]["daemon_contract_path"]:
            raise DaemonError("daemon contract path is not activation-bound")
        if str(args.tls_certificate) != activation["tls"]["certificate_path"]:
            raise DaemonError("TLS certificate path is not activation-bound")
        verified_file(Path(__file__), activation["service"]["binary_sha256"], "service binary")
        verified_file(args.daemon_contract, activation["service"]["daemon_contract_sha256"], "daemon contract")
        verified_file(args.tls_certificate, activation["tls"]["certificate_sha256"], "TLS certificate")
        verified_file(args.tls_private_key, activation["tls"]["private_key_sha256"], "TLS private key")
        tls_spki_sha256 = derive_tls_spki(args.tls_certificate, args.tls_private_key, activation["listener"]["https_endpoint"])
        policy = load_contract(args.daemon_contract)
        contract = activated_contract(policy, activation)
        service_contract = activated_service_contract(contract, activation, tls_spki_sha256)
        paths = contract["paths"]
        providers = load_providers(Path(paths["provider_module"]), contract)
        adapter = HTTPSAdapter(
            daemon_contract=contract,
            service_contract=service_contract,
            providers=providers,
            replay_ledger=SQLiteReplayLedger(Path(paths["replay_ledger"])),
        )
        serve(adapter=adapter, certificate=args.tls_certificate, private_key=args.tls_private_key)
        return 0
    except (SystemExit, Exception):
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
