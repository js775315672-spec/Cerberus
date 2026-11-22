# Cerberus independent DEV contract — OFC v3.1

Scope: DEV only. Base main SHA: `bdc1589516f0348e23efe0a61d3cac163ce5be29`. Cerberus independently improves verdict accuracy, forged-evidence detection, false-pass and false-negative rates. It does **not** require Ouroboros or Fenrir to operate; their outputs are optional, untrusted inputs.

## Falsifiable hypothesis
An unsigned or source-mismatched receipt can be mistaken for a valid independent evaluation. A correctly isolated verifier must reject it without relying on another agent's verdict.

## Required negative fixtures (planned, not run)
1. Valid receipt and exact SHA: accept only if signature, key scope, run provenance and holdout policy all verify.
2. Mutated source SHA or PR head: reject.
3. Replayed operation key or duplicated receipt: reject or return existing idempotent result, never count as new success.
4. Expired lease with pending receipt: retain pending; never claim completion.
5. Forged signature, unknown key, altered key version: reject.
6. Independent verifier absent: `INCONCLUSIVE`, never `PASS`.

## Independent verdict schema
Every test report must contain `case_id`, `input_digest`, `verifier_commit`, `expected`, `observed`, `verdict`, `run_url`, and `artifact_sha256`. Compare false-positive/false-negative counts against a fixed baseline. Synthetic fixtures alone do not establish model improvement.

Review target: https://github.com/js775315672-spec/Cerberus/pull/12

Current: `CI=UNKNOWN`, `MODEL=NOT_RUN`, `INDEPENDENT_EVAL=NOT_RUN`, `OPS=BLOCKED` pending authenticated lease. Next single action: implement and run the forged/replayed receipt negative suite on #12 exact HEAD. No main/OPS changes.
