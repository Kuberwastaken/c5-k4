#!/usr/bin/env python3
"""Focused positive and adversarial tests for Method v1.5 JSON contracts."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
H = "a" * 64
O = "b" * 40
T = "2026-08-14T00:17:00Z"
SCHEMAS = {name: json.loads((ROOT / f"schemas/benchmark-{name}-v1.5.schema.json").read_text()) for name in (
    "vendor-base-receipt", "source-snapshot", "generation-proof", "provenance-ledger", "future-registry-input", "future-registry-output"
)}

def valid(name: str, value: dict) -> None:
    Draft7Validator(SCHEMAS[name], format_checker=FormatChecker()).validate(value)

def vendor() -> dict:
    return {"schema":"c5k4-method-v1.5-vendor-base-receipt-1.0","status":"AUTHENTICATED_IMMUTABLE_SOURCE_CUSTODY","acquired_at_utc":T,"repository_path":"/tmp/vendor.git","fresh_repository":True,"bare_repository":True,"remote":"https://example.com/r.git","remote_ref":"refs/heads/main","destination_ref":"refs/c5k4-benchmark/v1.5/vendor/upstream","fetch_command":["git","-c","x","-c","y","-c","z","fetch","--atomic","--no-tags","--no-progress","origin","refs/heads/main:refs/c5k4-benchmark/v1.5/vendor/upstream"],"fetch_stdout_sha256":H,"fetch_stderr_sha256":H,"audit":{"object_format":"sha1","commit":O,"root_tree":O,"refs":[{"ref":"refs/c5k4-benchmark/v1.5/vendor/upstream","object_id":O,"object_type":"commit"}],"connectivity_fsck_stdout_sha256":H,"connectivity_fsck_stderr_sha256":H},"retry_count":0,"receipt_sha256":H}

def snapshot() -> dict:
    return {"schema":"c5k4-method-v1.5-source-snapshot-1.0","status":"COMPLETE_CONTENT_ADDRESSED_SOURCE_SNAPSHOT","snapshot_id":"s1","source_id":"repo","source_kind":"GIT_REPOSITORY","captured_at_utc":T,"coverage":{"lower_bound_utc":T,"upper_bound_utc":T,"complete":True,"gaps":[]},"capture":{"producer_id":"capture","executable_sha256":H,"invocation_contract_sha256":H},"artifacts":[{"locator":"blob:x","content_sha256":H,"byte_count":1}],"source_complete":True,"snapshot_sha256":H}

def generation() -> dict:
    return {"schema":"c5k4-method-v1.5-generation-proof-1.0","status":"VERIFIED_MACHINE_REGISTRY_CONTACT","generation_id":"g1","generated_at_utc":T,"chronology":{"basis_commit":O,"output_commit":O,"producer_frozen_at_commit":O,"historical_inputs_predate_output":True},"producer":{"producer_id":"p","executable_path":"scripts/p.py","executable_sha256":H,"invocation_contract_sha256":H},"inputs":[{"artifact_id":"i","file_sha256":H,"canonical_sha256":H,"schema_version":"c5k4-input-1.0"}],"allowed_operations":["IDENTITY"],"output":{"artifact_id":"o","path":"out.json","file_sha256":H,"canonical_sha256":H,"schema_version":"c5k4-output-1.0","schema_sha256":H,"byte_count":1,"row_count":1},"locator_binding":{"source_id":"s","source_kind":"git","locator":"git-blob:"+O+":x","role":"machine-generated-git-blob","content_sha256":H,"content_schema":None,"unit_identity_sha256":H,"locator_specific":True},"semantic_bounds":{"statement_text_emitted":False,"target_residual_emitted":False,"target_ranking_emitted":False,"candidate_or_route_emitted":False,"result_emitted":False,"natural_language_delivery":False},"verification":{"schema_valid":True,"self_digest_valid":True,"input_digests_replayed":True,"producer_digest_replayed":True,"deterministic_exact_replay_one":True,"deterministic_exact_replay_two":True,"replays_byte_identical":True},"proof_sha256":H}

def ledger() -> dict:
    return {"schema":"c5k4-method-v1.5-provenance-ledger-1.0","status":"CLASSIFIED_COMPLETE","ledger_id":"l1","created_at_utc":T,"source_snapshot_sha256":H,"source_id":"repo","ontology_sha256":H,"units":[{"unit_id":H,"locator":"x","role":"vendor-base-blob","content_sha256":H,"provenance_class":"IMMUTABLE_SOURCE_CUSTODY","classification_reason":"VERIFIED_CUSTODY","delivery_path":"CUSTODY_ONLY","producer_proof_sha256":H}],"counts":{"SEMANTIC_EXPOSURE":0,"MACHINE_REGISTRY_CONTACT":0,"IMMUTABLE_SOURCE_CUSTODY":1,"UNKNOWN":0},"source_complete":True,"fail_closed":False,"ledger_sha256":H}

def reg_input() -> dict:
    return {"schema_version":"c5k4-future-registry-input-1.5","authority":"P1_FROZEN_SCHEDULED_CHECKPOINT","protocol_version":"1.5","checkpoint":{"ordinal":1,"label":"checkpoint-2026-08-14","scheduled_at_utc":T,"valid_start_before_utc":"2026-08-14T06:00:00Z","capture_started_at_utc":T,"hard_horizon_checkpoint":False},"chronology":{"p1t_commit":O,"u1_commit":O,"u1_tree":O,"prior_checkpoint_chain_sha256":H,"prior_valid_checkpoint_count":0,"all_prior_valid_checkpoints_failed_quota_gate":True},"producer":{"producer_id":"method-v1.5-future-cohort-registry-builder","executable_sha256":H,"invocation_contract_sha256":H,"input_schema_sha256":H,"output_schema_sha256":H},"inputs":{k:H for k in ("chronology_receipt_sha256","u1_registry_sha256","v14_exclusion_sha256","grouping_rule_sha256","classifier_sha256","provenance_ledger_sha256","quota_rule_sha256")},"controls":{"scheduled_event":True,"manual_dispatch":False,"rerun":False,"statement_text_permitted":False,"outcomes_permitted":False,"ranking_permitted":False,"entropy_used":False,"selection_permitted":False,"overwrite_permitted":False}}

def counts(n: int) -> dict:
    return {"GRAPH_SCALAR_INEQUALITY":n,"GRAPH_STRUCTURAL_PROPERTY":n,"FINITE_ALGEBRA_EQUATIONAL":n,"AUTOMATA_GAME_PROCESS":n,"FINITE_COMBINATORIAL":n}

def reg_output() -> dict:
    rec={"cluster_id":"future:x","identity_sha256":H,"path":"FormalConjectures/X.lean","module_blob_sha256":H,"declarations":[{"name":"x","kind":"theorem","category_line":1,"statement_header_sha256":H}],"machine_stratum":"GRAPH_SCALAR_INEQUALITY","classification_basis":["TYPE_SHAPE"],"first_introduction_commit":O,"first_introduction_tree":O,"membership_status":"INCLUDE","exclusion_reasons":[]}
    return {"schema_version":"c5k4-future-cohort-registry-1.5","authority":"SCHEDULED_IDENTITY_ONLY_CHECKPOINT","upstream":{"repository":"https://github.com/google-deepmind/formal-conjectures.git","u1_commit":O,"u1_tree":O,"u2_commit":O,"u2_tree":O,"ancestry_interval":O+".."+O},"inputs":{"chronology_receipt_sha256":H},"controls":{"statement_text_present":False,"outcomes_present":False,"ranking_present":False,"entropy_used":False,"selection_permitted":False,"first_introduction_basis":"GIT_ANCESTRY_AND_TREE_CONTENT","v14_exclusion_cluster_count":728},"counts":{"u1_open_clusters":1,"u2_open_clusters":2,"delta_records":1,"included":1,"excluded":0,"included_by_stratum":counts(3),"exclusion_reasons":{}},"quota_certificate":{"checkpoint_ordinal":1,"checkpoint_label":"checkpoint-2026-08-14","commit":O,"tree":O,"quotas":{"GRAPH_SCALAR_INEQUALITY":3,"GRAPH_STRUCTURAL_PROPERTY":3,"FINITE_ALGEBRA_EQUATIONAL":2,"AUTOMATA_GAME_PROCESS":2,"FINITE_COMBINATORIAL":2},"eligible_by_stratum":counts(3),"deficits":counts(0),"status":"PASS","candidate_count":15,"prior_checkpoint_chain_sha256":H,"all_prior_valid_checkpoints_failed":True,"first_passing_checkpoint":True,"registry_sha256":H},"records":[rec],"registry_sha256":H}

class SchemaContracts(unittest.TestCase):
    def test_schemas_and_positive_fixtures(self):
        fixtures={"vendor-base-receipt":vendor(),"source-snapshot":snapshot(),"generation-proof":generation(),"provenance-ledger":ledger(),"future-registry-input":reg_input(),"future-registry-output":reg_output()}
        for name,schema in SCHEMAS.items():
            Draft7Validator.check_schema(schema); valid(name,fixtures[name])

    def test_unknown_fields_fail_every_contract(self):
        fixtures={"vendor-base-receipt":vendor(),"source-snapshot":snapshot(),"generation-proof":generation(),"provenance-ledger":ledger(),"future-registry-input":reg_input(),"future-registry-output":reg_output()}
        for name,value in fixtures.items():
            value["statement_text"]="forbidden"
            with self.assertRaises(Exception, msg=name): valid(name,value)

    def test_semantic_and_chronology_bypasses_fail(self):
        x=generation(); x["semantic_bounds"]["statement_text_emitted"]=True
        with self.assertRaises(Exception): valid("generation-proof",x)
        x=reg_input(); x["controls"]["manual_dispatch"]=True
        with self.assertRaises(Exception): valid("future-registry-input",x)
        x=reg_input(); x["chronology"]["all_prior_valid_checkpoints_failed_quota_gate"]=False
        with self.assertRaises(Exception): valid("future-registry-input",x)
        x=reg_output(); x["quota_certificate"]["first_passing_checkpoint"]=False
        with self.assertRaises(Exception): valid("future-registry-output",x)

    def test_provenance_delivery_and_completeness_fail_closed(self):
        x=ledger(); x["units"][0]["delivery_path"]="HUMAN_OR_MODEL"
        with self.assertRaises(Exception): valid("provenance-ledger",x)
        x=snapshot(); x["source_complete"]=False
        with self.assertRaises(Exception): valid("source-snapshot",x)
        x=vendor(); x["retry_count"]=1
        with self.assertRaises(Exception): valid("vendor-base-receipt",x)

if __name__ == "__main__": unittest.main()
