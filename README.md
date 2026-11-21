# CERBERUS

**Independent critical verification gate for autonomous AI systems (prototype v0.1).**

CERBERUS is a separate project from [Harness-Ouroboros-MCP](https://github.com/js775315672-spec/Harness-Ouroboros-MCP) and the FENRIR red-team agent. OUROBOROS develops; FENRIR independently criticizes; CERBERUS turns verified criticisms into reproducible checks and develops its own verifier.

## Current capabilities

- Offline, deterministic contract checks for O -> F -> C JSON handoff
- Candidate SHA-256 and cycle-ID binding checks
- Explicit independent execution-ID metadata checks; fail-closed on duplicates or invalid metadata
- P0/P1 confirmed-Fenrir finding blocks promotion
- Reject duplicate JSON keys and payloads over 1 MB
- Standard-library unit tests and read-only GitHub Actions CI

**Important:** Metadata labels and evidence URLs cannot prove independence. This version does not call FENRIR, authenticate URLs, run hidden evaluations or independently replay model benchmarks. It **never returns PASS** or authorizes merge/deployment. An INCONCLUSIVE result is not a success.

## Local check

Python 3.11+ required. No external packages.

    python -m unittest discover -s tests -v
    python -m cerberus.gate examples/ouroboros.json examples/fenrir.json --output report.json

The example JSON files are synthetic and deliberately contain a blocking finding. Exit code 1 = BLOCKED, exit code 2 = INCONCLUSIVE. Neither grants approval.

See [architecture, handoff contract and milestones](docs/ARCHITECTURE.md).

## Safety

No automatic merge; no production deployment; no credentials; no financial trades; no assertion of model intelligence gains from CI passes. This work is proposed as a **Draft PR**, not automatically released.
