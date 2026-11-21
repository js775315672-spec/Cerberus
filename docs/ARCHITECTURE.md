# CERBERUS v0.1 — independent verification architecture

## Mission and boundaries

CERBERUS is a distinct verifier, not an Ouroboros role-play or Fenrir persona. The three agents maintain separate ownership and evidence:

1. **OUROBOROS** develops a candidate and publishes its immutable candidate SHA-256, source commit and execution evidence.
2. **FENRIR** independently reviews the same SHA-256, supplies criticisms as structured findings, and publishes its own execution evidence.
3. **CERBERUS** consumes both reports and evaluates constraints. v0.1 is a contract gate only. It does not run model inference, independently reproduce benchmarks, or authenticate agent identity.

The scheduled orchestration is a supervisor and must not fabricate a missing Fenrir run. When O or F artifacts are missing, the cycle stops at WAITING_FENRIR / INCONCLUSIVE; no simulated F agent or self-criticism may replace F.

## Trust model (critical)

- All submitted JSON is **untrusted**.
- Checking strings such as agent_id, execution_id, candidate_sha256 and evidence_url does **not prove** independent execution or ownership. An attacker can self-assert these fields.
- Evidence URLs are recorded but **not fetched or authenticated** by v0.1.
- INCONCLUSIVE means metadata has basic consistency, not PASS. BLOCKED means a contract failure or confirmed high-severity objection. Neither result grants merge, deployment, release or model-intelligence claims.
- Real independence requires separately authenticated actor/runner identity, immutable provenance attestation, independent hidden evaluation, hash matching and protected approval in later iterations.
- Fenrir's critical confirmed findings block by default; a finding explicitly marked hypothesis is not automatically treated as proven.
- Do not expose protected holdout examples or evaluation secrets to the development agent.

## Evidence protocol

OUROBOROS JSON:
- cycle_id: stable ID within a cycle
- candidate_sha256: 64 lowercase hex characters identifying the exact candidate artifact
- source_commit: 40 lowercase hex characters
- producer: agent_id=OUROBOROS, execution_id, evidence_url (HTTPS)

FENRIR JSON:
- same cycle_id and candidate_sha256
- producer: agent_id=FENRIR, independent execution_id, evidence_url (HTTPS)
- findings: up to 100 items, each with id, severity (P0–P3), classification (confirmed/hypothesis), summary, reproduction, evidence_url

The current CLI does not enforce that the declared SHA represents an actual downloaded artifact. Trust must be established outside the submitted documents; this is an intentionally documented limitation.

## Execution

Run: python -m unittest discover -s tests -v

Run: python -m cerberus.gate examples/ouroboros.json examples/fenrir.json --output report.json

The CLI returns exit code 1 for BLOCKED or 2 for INCONCLUSIVE; there is currently no success/approval exit code. report.json is still produced when --output is supplied.

## Next milestones (requires separate validation)

- P0: Signed or GitHub-OIDC-authenticated provenance, strict immutable artifact links, replay in a separate trusted environment
- P0: Holdout isolation and leakage-resistant tests; strong failure-path and malicious JSON fuzzing
- P1: Independent comparator for baseline vs new candidate, sample size and uncertainty tracking
- P1: CERBERUS self-improvement experiments scored on hidden defect-detection tasks without modifying protected evaluator
- P2: GitHub evidence-handoff dispatcher with atomic lease / idempotency; automatic Draft PR only, no auto merge

## Non-goals

No secrets, financial trading, deployment, auto-merge, agent impersonation, hidden chain-of-thought extraction or claims of autonomous intelligence improvement.
