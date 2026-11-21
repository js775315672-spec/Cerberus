# CERBERUS · Independent Verification Gate

> **Current verdict: INCONCLUSIVE / BLOCKED**  
> **FENRIR_VERIFIED=false · Protected independent replay NOT STARTED**  
> This dashboard reports **verified evidence**, not scheduled intentions or automatic approvals.

## Verification dashboard

| Stage | Evidence-backed status | Evidence / limitation |
|---|---|---|
| OUROBOROS candidate | **PARTIAL** — source commit pinned; whole candidate artifact SHA-256 not established | [O PR #346](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/pull/346) |
| Candidate source file SHA-256 | `1c77af88c66ffa1a3abbdb7176d328d9d3803687138c43cb24cd749b2e4d7969` — **one file only** | [O ledger #347](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/issues/347) |
| Earlier FENRIR-related C workflow | **Workflow ran; report acceptance NOT verified** | [C Actions #44875233515](https://github.com/js775315672-spec/Cerberus/actions/runs/44875233515); report completeness and evidence authenticity disputed in [O ledger](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/issues/347) |
| Independent Fenrir repository | **IMPLEMENTED (prototype)** | [Fenrir-Agent Draft PR #1](https://github.com/js775315672-spec/Fenrir-Agent/pull/1) |
| Actual Qwen inference | **PASS — public demo only** | [Fenrir run #44895880606](https://github.com/js775315672-spec/Fenrir-Agent/actions/runs/44895880606); not O PR #346 |
| Fenrir demo artifact | **UPLOADED, NOT O report** | Fenrir run #44895880606, artifact ID `14704580154` |
| F report provenance | **UNVERIFIED** for actual O candidate | GitHub attestation step success does not replace independent verification or authenticate review quality |
| Cerberus candidate replay / protected holdout | **NOT RUN** | [C issue #2](https://github.com/js775315672-spec/Cerberus/issues/2) |
| Merge / deployment approval | **NOT GRANTED** | No main modification or auto-merge authorized |

**Tracked cycle:** `ORIL-OFC-PR346-001`  
**Shared work key:** `ORIL-OFC-PR346-001:F_REPORT_CONTRACT`  
**O source commit (historical pin):** `083eb00e9efb91c8a951a551a91fcccfb6d2efcb`  
**State:** `WAITING_O_ARTIFACT_SHA → WAITING_FENRIR → WAITING_CERBERUS_REPLAY` (the latter stages are **not** reached).

## What is blocked?

1. Pin immutable **whole O candidate artifact** bytes, SHA-256, test contract SHA, source commit, owner and atomic lease; a Git commit hash is not a candidate artifact digest.
2. Run **independently controlled FENRIR** against that same O candidate; record real Qwen run ID, model, original report, reproduction, finding ID/severity, evidence URLs and immutable report digest.
3. Independently verify F report completeness, GitHub attestation subject and issuer, exact candidate binding, replay resistance and evidence provenance. Do not trust an agent's self-declared identity.
4. Only then permit Cerberus's **isolated** replay on a protected holdout and evaluate confirmed defects, false positives/negatives, regressions, costs and time.
5. Keep protected holdout unavailable to O and F. Never auto-merge, deploy, change protected gates or spend on paid APIs.

**Fail-closed:** CI green ≠ authenticated Fenrir review ≠ Cerberus independent validation ≠ model intelligence gain. Missing evidence means `INCONCLUSIVE`, not `PASS`.

## Development history and handoffs

| Checkpoint | What actually happened | What it does NOT establish |
|---|---|---|
| [Cerberus workflow #44875233515](https://github.com/js775315672-spec/Cerberus/actions/runs/44875233515) | Earlier F/C workflow jobs executed | Complete trusted F report, independent O candidate replay or PASS |
| [Fenrir workflow #44895880606](https://github.com/js775315672-spec/Fenrir-Agent/actions/runs/44895880606) | Actual Qwen public-demo inference, artifact upload, attestation step success | Review of O PR #346 |
| [O issue #347 handoff](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/issues/347#issuecomment-7061485286) | Fenrir demo evidence handed to O ledger | Authorized advancement to Cerberus replay |
| [C issue #2 handoff](https://github.com/js775315672-spec/Cerberus/issues/2#issuecomment-7061485628) | Demo evidence recorded in C queue | Independent verification completion |

Detailed source-of-truth logs live in GitHub Actions and issues; README is a **snapshot**. It is not an atomic lock or an auto-updating truth source.

## Cycle improvement and speed trend

| Comparable metric (5–12 homogeneous verified O→F→C cycles) | Result |
|---|---|
| Verified complete comparable cycles | `n=0` for this tracked O→F→C contract |
| End-to-end median / model / independent verification / follow-up times | **Not measured** |
| Independent accepted improvements per hour | **Cannot compute** |
| Retries / failures / regressions / rollbacks | **Insufficient comparable data** |
| Protected holdout quality change | **Not measured** |
| False positive / false negative rate | **Not measured** |
| Cost per verified cycle | **Not measured** |
| Speedup against baseline | **Cannot determine** |

Never reuse historical Hydra or public-demo runs as homogeneous O→F→C cycle samples. A single workflow duration is not model inference latency.

## Architecture and development

- [OUROBOROS](https://github.com/js775315672-spec/Harness-Ouroboros-MCP) — develops and publishes pinned candidates
- [FENRIR](https://github.com/js775315672-spec/Fenrir-Agent) — separate critical reviewer, must provide authenticated original reports
- [CERBERUS](https://github.com/js775315672-spec/Cerberus) — verifies F reports and performs independent replay only after trusted handoff
- [Cerberus Draft PR #1](https://github.com/js775315672-spec/Cerberus/pull/1) — initial rule-based contract prototype, **not** independent LLM identity
- [Cerberus Draft PR #3](https://github.com/js775315672-spec/Cerberus/pull/3) — earlier experimental work; no verified final O→F→C PASS
- [Cerberus tracking issue #2](https://github.com/js775315672-spec/Cerberus/issues/2) — current blocker and handoff

**Safety:** No automatic merge, protected holdout leakage, production deployment, live trading, secret exposure, or unsupported LoRA/intelligence claims.
