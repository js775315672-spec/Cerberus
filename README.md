# Cerberus

Cerberus는 Ouroboros가 만든 후보와 Fenrir의 검토 보고서를 받아, 출처를 확인하고 후보의 최종 검증 결과를 기록하는 프로젝트입니다.

## 검증 대시보드

**보고서 인계 성공 · 후보 최종 판정 `INCONCLUSIVE`**

2026-11-21 KST 기준 · 사이클 `ORIL-OFC-PR346-001` · [Ouroboros 후보 PR #346](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/pull/346) · [Cerberus 구현 PR #3](https://github.com/js775315672-spec/Cerberus/pull/3)

| 단계 | 상태 | 확인한 내용과 근거 |
| --- | --- | --- |
| Ouroboros 후보 고정 | 완료 | 커밋 `083eb00e`에서 가져온 Python 소스와 공개 테스트 2개의 SHA-256이 일치했습니다. [후보 원본](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/blob/083eb00e9efb91c8a951a551a91fcccfb6d2efcb/scripts/oril_v2_teacher_distillation_pack.py) |
| Fenrir 모델 검토 | 완료 | 별도 러너에서 Qwen2.5-Coder-1.5B-Instruct가 후보를 검토하고, 출처 증명이 붙은 보고서를 발행했습니다. [실행 로그](https://github.com/js775315672-spec/Cerberus/actions/runs/44875233515/job/136758358544) · [보고서](https://github.com/js775315672-spec/Cerberus/actions/runs/44875233515/artifacts/14695543748) |
| Cerberus 보고서 수신 | 완료 | 발행 워크플로와 실행 커밋을 인증하고, 보고서의 후보 해시와 실행 ID를 대조했습니다. [수신 로그](https://github.com/js775315672-spec/Cerberus/actions/runs/44875233515/job/136759511400) |
| Cerberus 후보 재현·비공개 평가 | 대기 | 다음 단계는 보호된 검증 환경에서 동일 후보를 재실행하고 판정 근거를 기록하는 것입니다. [검증 추적 이슈](https://github.com/js775315672-spec/Cerberus/issues/2) |

**후보 소스 SHA-256**  
`1c77af88c66ffa1a3abbdb7176d328d9d3803687138c43cb24cd749b2e4d7969`

이번 인계는 Draft PR의 단일 워크플로에서 Fenrir 발행 작업과 Cerberus 수신 작업을 분리해 검증했습니다. 운영용 신뢰 정책의 보호와 후보의 독립 재현은 후속 과제입니다. [전체 실행 기록](https://github.com/js775315672-spec/Cerberus/actions/runs/44875233515) · [저장소 간 인계 원장](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/issues/347)


## OFC DEV 12-cycle expansion (unverified)

- Scope: isolated DEV branch only; no OPS registry, main merge, holdout or protected edits.
- Runner: `agent/dev_cycle_12.py` (maximum 12 sequential candidate/verifier command pairs, wall-clock budget, atomic local checkpoint, stable operation keys).
- Safety: ambiguous pending blocks replay; failure stops the track; independent command exit 0 is **not** evidence of model intelligence improvement.
- Tests: `tests/test_dev_cycle_12.py`; Windows/Linux workflow `.github/workflows/ofc-dev-12-cycle.yml`.
- Evidence: this Draft PR and its head SHA / Actions checks. Current CI outcome: UNKNOWN until completed. Real Qwen runs: NOT_RUN. Protected independent evaluation: NOT_RUN. OPS cycle IDs: UNKNOWN.
- Limitations: no actual Qwen orchestration or artifact-backed independent evaluation; monetary cost cannot be enforced by this runner, so use only approved zero-cost commands. The runner must not be used for external side effects until operation reconciliation and source provenance gates are verified.
- Next single action: validate Windows/Linux regression and independently audit pending/restart behavior before enabling any real candidate commands.


## OFC D-plan: adaptive 120-cycle DEV planner (verification pending)

- A gate: 12-cycle Linux/Windows safety CI passed on the pre-expansion PR head. This is **not** proof of independent model improvement.
- B DEV files: `agent/adaptive_dev_120.py`, `tests/test_adaptive_dev_120.py`, `.github/workflows/ofc-dev-120-cycle.yml`. Maximum 10 batches × 12 cycles, stable keys, fail-closed pending, bounded budget counters, and independent-evaluation receipt fields.
- Status: planner committed to this independent Draft PR; new 120-cycle Windows/Linux CI must pass before promotion. The code is a **planner/receipt ledger**, not an external model executor or trusted evaluator. It does not automatically enforce third-party spending or cryptographically authenticate evaluator evidence.
- C gate: real approved free Qwen calls NOT_RUN; model hash, candidate SHA, evaluator SHA, actual run ID, artifact digest and independent holdout evaluation remain UNKNOWN/NOT_RUN. No OPS lease acquired; no main/protected/registry writes.
- Next single action: verify 120-cycle CI and harden evidence authentication and real-cost metering before any Qwen execution.


## OFC A-gate 120-cycle CI evidence — 2026-11-23

- Verification target before this documentation commit: `8284e0e1254f55ac2fca01148c1cffe11f482e26` (Draft PR, DEV-only).
- Workflow: `OFC DEV 120-cycle planner safety`; run: https://github.com/js775315672-spec/Cerberus/actions/runs/45047638567.
- Linux: **PASS**; Windows: **PASS** at inspection time. Do not treat queued as passed or failed.
- A-gate: **PASS for pinned code head; rerun required for any subsequent code changes**.
- Evidence limitations: test suite checks deterministic planner bounds, pending replay block, independent-agent ledger separation, fail-closed receipts and budget counters. It does not prove real Qwen inference, authenticated evaluation artifacts, real spend enforcement, or intelligence gains.
- New README commit changes PR head: verify the new head separately before final gate promotion.
- OPS registry / PROTECTED / main: unchanged. No automatic merge.

### OFC C-gate read-only artifact verification (2026-11-23)
- DEV-only: `agent/github_artifact_evidence.py` fetches GitHub run and artifact metadata using a separately provided read-only token; verifies repository, exact head SHA, successful completed run, artifact binding, expiry and SHA-256 of downloaded ZIP (50 MB limit).
- Windows/Linux test: `tests/test_github_artifact_evidence.py` (mock transport). The workflow executes both planner and provenance tests. A mocked PASS is **not** a live authenticated artifact verification.
- **BLOCKED** until the newest CI for this exact README head passes on both OSes, a real artifact is available and independently authenticated, lease and zero-cost provider are verified. No real Qwen calls, independent improvements, or operational cycles are claimed.


### OFC P0 live audit snapshot (2026-11-23)
- Inspected pre-documentation DEV head: `04225b340cb6c566096c311a9791d8c695bfc3d3`; P0 Actions run: https://github.com/js775315672-spec/Cerberus/actions/runs/45048546786.
- Observed at audit: Windows/Linux isolated regression PASS; CAS running; Linux artifact 14765175527 SHA256 cc678ec3fd51ff44d9e93867818ab3048114fb4dadf9dafd9a5c903b0afbc561; Windows artifact 14764901709 SHA256 1da39d74385939336eada0def2f7768b0be2708487bd07ede61ac7fca7850777; both ZIP integrity PASS.
- Final `verify-live-artifacts` job: NOT_PASSED / not yet executed. P0 overall BLOCKED; no new Qwen invocation, independent improvement, or verified operational cycle.
- Snapshot only: this README commit changes the DEV head and requires fresh head-bound CI; do not promote previous-run evidence as current-head PASS. main, OPS, PROTECTED and automations unchanged.
