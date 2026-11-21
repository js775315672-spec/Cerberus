"""Fail-closed, offline contract checks for O -> F -> C handoff.

This tool does NOT call Fenrir, execute an independent replay, authenticate
GitHub URLs, or establish an agent's cryptographic identity.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MAX_BYTES = 1_000_000
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SEVERITIES = {"P0", "P1", "P2", "P3"}
CLASSES = {"confirmed", "hypothesis"}


def _no_duplicate_keys(pairs):
    output = {}
    for key, value in pairs:
        if key in output:
            raise ValueError("duplicate JSON key: " + key)
        output[key] = value
    return output


def load_document(path):
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("JSON artifact exceeds 1 MB")
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)
    if not isinstance(data, dict):
        raise ValueError("root must be a JSON object")
    return data


def _valid_text(value, limit=256):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit


def _valid_producer(document, expected, reasons):
    producer = document.get("producer")
    if not isinstance(producer, dict):
        reasons.append(expected + ": producer missing")
        return None
    if producer.get("agent_id") != expected:
        reasons.append(expected + ": wrong agent_id")
    if not _valid_text(producer.get("execution_id"), 128):
        reasons.append(expected + ": missing execution_id")
    evidence = producer.get("evidence_url")
    if not _valid_text(evidence, 2048) or not evidence.startswith("https://"):
        reasons.append(expected + ": missing HTTPS evidence URL")
    return producer


def evaluate(ouroboros, fenrir):
    """Return a deterministic, non-approving assessment of untrusted handoffs."""
    reasons = []
    if not isinstance(ouroboros, dict) or not isinstance(fenrir, dict):
        return {"status": "BLOCKED", "reasons": ["input documents must be JSON objects"],
                "independence_verified": False, "independent_replay_verified": False,
                "eligible_for_merge": False, "findings_count": 0}

    cycle = ouroboros.get("cycle_id")
    if not _valid_text(cycle, 128) or cycle != fenrir.get("cycle_id"):
        reasons.append("cycle_id is missing or mismatched")
    candidate = ouroboros.get("candidate_sha256")
    if not isinstance(candidate, str) or not SHA256.fullmatch(candidate):
        reasons.append("O: candidate_sha256 invalid")
    if candidate != fenrir.get("candidate_sha256"):
        reasons.append("F report does not bind to O candidate_sha256")
    commit = ouroboros.get("source_commit")
    if not isinstance(commit, str) or not SHA40.fullmatch(commit):
        reasons.append("O: source_commit invalid")

    o_producer = _valid_producer(ouroboros, "OUROBOROS", reasons)
    f_producer = _valid_producer(fenrir, "FENRIR", reasons)
    if (o_producer and f_producer
            and o_producer.get("execution_id") == f_producer.get("execution_id")):
        reasons.append("O and F share execution_id; independence cannot be assumed")

    findings = fenrir.get("findings")
    if not isinstance(findings, list) or len(findings) > 100:
        reasons.append("F: findings must be an array with at most 100 items")
        findings = []
    seen = set()
    blocking_findings = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            reasons.append("finding " + str(index) + " is not an object")
            continue
        identity = finding.get("id")
        if not _valid_text(identity, 64) or identity in seen:
            reasons.append("finding id missing or duplicated")
        else:
            seen.add(identity)
        severity = finding.get("severity")
        classification = finding.get("classification")
        if (not isinstance(severity, str) or severity not in SEVERITIES
                or not isinstance(classification, str) or classification not in CLASSES):
            reasons.append("finding " + str(index) + " has invalid severity/classification")
            continue
        if not _valid_text(finding.get("summary"), 1000):
            reasons.append("finding " + str(index) + " missing summary")
        if not _valid_text(finding.get("reproduction"), 4000):
            reasons.append("finding " + str(index) + " missing reproduction")
        evidence = finding.get("evidence_url")
        if not _valid_text(evidence, 2048) or not evidence.startswith("https://"):
            reasons.append("finding " + str(index) + " missing HTTPS evidence URL")
        if isinstance(severity, str) and severity in {"P0", "P1"} and classification == "confirmed":
            blocking_findings.append(identity)

    if blocking_findings:
        reasons.append("confirmed blocking findings: " + ", ".join(str(x) for x in blocking_findings))
    if not findings:
        reasons.append("no Fenrir findings; silence is not approval")

    status = "BLOCKED" if reasons else "INCONCLUSIVE"
    if not reasons:
        reasons.append("external agent identity and evidence URL not authenticated")
        reasons.append("separate independent replay / hidden evaluation not provided")

    raw = json.dumps({"ouroboros": ouroboros, "fenrir": fenrir},
                     ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "status": status,
        "reasons": reasons,
        "cycle_id": cycle if _valid_text(cycle, 128) else None,
        "candidate_sha256": candidate if isinstance(candidate, str) else None,
        "input_fingerprint_sha256": hashlib.sha256(raw).hexdigest(),
        "independence_verified": False,
        "independent_replay_verified": False,
        "eligible_for_merge": False,
        "findings_count": len(findings),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="CERBERUS fail-closed handoff contract gate")
    parser.add_argument("ouroboros", help="Ouroboros report JSON path")
    parser.add_argument("fenrir", help="Fenrir independent report JSON path")
    parser.add_argument("--output", help="optional JSON output path")
    args = parser.parse_args(argv)
    try:
        report = evaluate(load_document(args.ouroboros), load_document(args.fenrir))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        report = {"status": "BLOCKED", "reasons": ["invalid input: " + str(error)],
                  "independence_verified": False, "independent_replay_verified": False,
                  "eligible_for_merge": False, "findings_count": 0}
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 1 if report["status"] == "BLOCKED" else 2


if __name__ == "__main__":
    sys.exit(main())
