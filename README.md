# Cerberus

## 독립 운영 계약 v3.1

Cerberus는 자체 검증기를 개선한다. 정상 자료와 변조 자료를 분리해 거짓 통과율과 거짓 차단율, 재현 비용을 측정한다.

[운영 명세와 원장 사용법](docs/ofc-v3.1.md)

<!-- OFC-DASHBOARD-BEGIN -->
## OFC independent agent dashboard (P0)

| Metric | Evidence-based status |
| --- | --- |
| Real model execution | UNKNOWN |
| Independent improvement | UNKNOWN |
| Improvement throughput | NOT_MEASURED |
| Comparable speed trend | NOT_MEASURED |
| Generalization | NOT_VERIFIED |
| Most recent blocker | P1 real model run + protected independent evaluation not yet connected |

Registry and contract unit tests are **not** model improvements.
<!-- OFC-DASHBOARD-END -->

## HISTORICAL · O→F→C 인계 실험

당시의 필수 입력 계약은 SUPERSEDED 상태다. 아래는 원래 실험 기록이다.

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
