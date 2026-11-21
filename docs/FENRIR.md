# FENRIR — separate adversarial reviewer (prototype v0.1)

**Location:** `fenrir/` in the Cerberus repository, with a separately invoked process and GitHub Actions job. Shared GitHub storage does **not** make OUROBOROS, FENRIR and CERBERUS the same agent, but it also does **not** provide cryptographic independence by itself.

## Responsibilities

- **OUROBOROS:** develops candidates and supplies an immutable artifact digest, source commit and evaluation evidence.
- **FENRIR:** challenges generalization, unseen holdout validity, benchmark reuse, replay independence, reproducibility and missing baselines. It publishes a *separate* `FENRIR_REPORT`.
- **CERBERUS:** validates contract consistency and will independently replay verified findings once trusted provenance / protected evaluation are implemented. It must never invent a FENRIR review.

## How to run FENRIR separately

Requires Python 3.11+ and no external libraries.

```bash
python -m fenrir.reviewer \
  --ouroboros examples/ouroboros.json \
  --execution-id fenrir-local-01 \
  --evidence-url https://github.com/js775315672-spec/Cerberus/actions \
  --output fenrir-report.json
python -m cerberus.gate examples/ouroboros.json fenrir-report.json --output cerberus-result.json
```

The URL above is just an example: use the URL of the **actual executed job**, not a generic landing page, for auditable evidence. `execution_id` also must refer to a real invocation. Do not treat manually supplied labels as authentication.

## GitHub Actions path

`.github/workflows/fenrir-handoff.yml` consists of **two distinct jobs** on separate GitHub-hosted runners. The F job generates a synthetic review artifact and uploads it. C downloads that artifact and asserts its outcome is `INCONCLUSIVE` (never PASS). The workflow currently runs on relevant PR changes and can be manually dispatched **only after that workflow exists on the default branch**.

The workflow is a **synthetic integration test**, not a real reviewed OUROBOROS candidate. The rule-based F reviewer generates conservative *hypotheses*, not confirmed vulnerabilities, and is not a separate LLM model. F and C are separate code modules and jobs but share this repository's permissions; a truly independent trust boundary additionally requires separately protected environment, reviewer identity and immutable signed provenance.

## Current security requirements

- C cannot approve merge/deployment or mark intelligence improvement based on F metadata.
- Missing real F provenance or actual candidate artifact digest implies `WAITING_FENRIR` / `INCONCLUSIVE`.
- Do not execute code from an untrusted candidate in a privileged job, reveal holdout data, auto-merge PRs, or grant secrets to PR workflows.
- Keep OUROBOROS source and FENRIR review data bound to the **same candidate SHA-256**; Git commit SHA-1 does not replace artifact SHA-256.
