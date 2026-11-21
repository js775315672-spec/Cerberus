"""FENRIR — standalone adversarial review worker (rule-based prototype).

FENRIR and CERBERUS live in separate Python packages. This module must run
as a *separate worker process* and emits a review artifact for CERBERUS to read.

This is NOT a separately hosted LLM agent, authenticated actor identity,
independent model benchmark replay, or evidence of model self-improvement.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


# FENRIR does not import or trust CERBERUS internals.
MAX_BYTES = 1_000_000


def _reject_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key: " + key)
        obj[key] = value
    return obj


def load_document(path):
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("O report exceeds 1 MB")
    document = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    if not isinstance(document, dict):
        raise ValueError("O report root must be an object")
    return document


SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def critique(o_report, *, execution_id, evidence_url):
    """Build conservative, reproducible hypotheses without executing O code."""
    if not isinstance(o_report, dict):
        raise ValueError("O report must be a JSON object")
    cycle = o_report.get("cycle_id")
    artifact_sha = o_report.get("candidate_sha256")
    source_commit = o_report.get("source_commit")
    producer = o_report.get("producer")
    if not isinstance(cycle, str) or not 1 <= len(cycle) <= 128 or not cycle.strip():
        raise ValueError("invalid O cycle_id")
    if not isinstance(artifact_sha, str) or not SHA256.fullmatch(artifact_sha):
        raise ValueError("invalid O candidate_sha256")
    if not isinstance(source_commit, str) or not SHA40.fullmatch(source_commit):
        raise ValueError("invalid O source_commit")
    if not isinstance(producer, dict) or producer.get("agent_id") != "OUROBOROS":
        raise ValueError("expected O producer declaration")
    if not isinstance(execution_id, str) or not execution_id.strip() or len(execution_id) > 128:
        raise ValueError("Fenrir execution_id required")
    if execution_id == producer.get("execution_id"):
        raise ValueError("F and O must not share execution_id")
    if not isinstance(evidence_url, str) or not evidence_url.startswith("https://") or len(evidence_url) > 2048:
        raise ValueError("HTTPS evidence_url required")

    findings = []
    def flag(fid, summary, reproduction):
        findings.append({
            "id": fid,
            "severity": "P2",
            "classification": "hypothesis",
            "summary": summary,
            "reproduction": reproduction,
            "evidence_url": evidence_url,
        })

    evaluation = o_report.get("evaluation", {})
    if not isinstance(evaluation, dict):
        flag("F-INPUT-01", "O evaluation metadata is malformed or missing a structured record.",
             "Submit an immutable evaluation record with task split and replay identifiers.")
        evaluation = {}
    if evaluation.get("holdout_id") is None or evaluation.get("holdout_protected") is not True:
        flag("F-HOLDOUT-01", "Independent hidden holdout evaluation has not been evidenced.",
             "Replay with an access-controlled new holdout; compare matched baseline on identical data.")
    if evaluation.get("independent_replay_url") is None:
        flag("F-REPLAY-01", "Separate-runner replay evidence was not supplied.",
             "Reproduce candidate source SHA on a trusted independent runner; publish its run ID and result.")
    if evaluation.get("baseline_score") is None or evaluation.get("candidate_score") is None:
        flag("F-BASELINE-01", "Comparable baseline and candidate metrics were not supplied.",
             "Score both frozen candidates on identical fresh tasks with uncertainty intervals.")
    if evaluation.get("benchmark_reused") is True:
        flag("F-LEAKAGE-01", "Developer reports repeated benchmark reuse; generalization is at risk.",
             "Evaluate on fresh hidden tasks, with no adaptive error-feedback reuse across candidates.")
    if not findings:
        flag("F-SCOPE-01", "Report metadata alone cannot establish an actual improvement or provenance.",
             "Audit raw model output, source provenance and holdout execution on a separate trusted runner.")

    fingerprint = hashlib.sha256(json.dumps(o_report, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                                 .encode("utf-8")).hexdigest()
    return {
        "cycle_id": cycle,
        "candidate_sha256": artifact_sha,
        "producer": {
            "agent_id": "FENRIR",
            "execution_id": execution_id,
            "evidence_url": evidence_url,
        },
        "review_mode": "RULE_BASED_PROTOTYPE_NOT_INDEPENDENT_LLM",
        "input_report_sha256": fingerprint,
        "findings": findings,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Run FENRIR standalone conservative critic")
    p.add_argument("--ouroboros", required=True, help="Untrusted O JSON report")
    p.add_argument("--execution-id", required=True, help="real separate worker invocation ID")
    p.add_argument("--evidence-url", required=True, help="worker's externally auditable HTTPS URL")
    p.add_argument("--output", required=True, help="FENRIR_REPORT JSON path")
    args = p.parse_args(argv)
    try:
        o = load_document(args.ouroboros)
        report = critique(o, execution_id=args.execution_id, evidence_url=args.evidence_url)
        Path(args.output).write_text(json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8")
    except (OSError, ValueError, UnicodeError) as exc:
        print("FENRIR failed closed: " + str(exc), file=sys.stderr)
        return 1
    print("FENRIR report saved; this is a rule-based critique, NOT authenticated LLM execution.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
