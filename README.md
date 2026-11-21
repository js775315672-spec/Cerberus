# Cerberus

Cerberus는 Ouroboros가 만든 후보와 Fenrir의 검토 보고서를 받아, 출처를 확인하고 후보의 최종 검증 결과를 기록하는 프로젝트입니다.

## Cerberus 독립 성장 연구

Cerberus는 Ouroboros의 마지막 관문에 종속되는 도구가 아니다. 독자적으로 증거 조작 시나리오, 검사기 결함, 재현 불가능한 실험을 연구하고 검증 정확도 자체를 높이는 자율개선형 개체를 목표로 한다. 다른 개체의 요청 없이도 자체 검증기 품질 실험을 시작할 수 있는 구조를 설계한다.

| 항목 | 현재 연구 기준 (2026-11-21) |
| --- | --- |
| 상태 | 연구 설계 작성 (Draft, 자율실행 미시작) |
| 고유 성장 목표 | 거짓 통과 감소·평가 정확도·증거 무결성 |
| 검증된 자기 개선 | 미입증 |
| 다음 실험 | 보호된 재현 및 검사기 변이 테스트 계획 |

[독립 정체성](docs/evolution/identity.md) · [기계 판독 상태](docs/evolution/independent-state.json) · [README 기억 실험 설계](docs/evolution/readme-memory-study.md) · [독립 기억 점검 스크립트](scripts/evolution_context.py)

아래의 기존 `ORIL-OFC-PR346-001` 인계 현황은 *다른 후보에 대한 검증 작업*이며, Cerberus 자신의 능력 개선이 검증됐다는 뜻이 아니다. 로컬 자기 점검: `python scripts/evolution_context.py check|context`.

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

### 독립 자율진화 상세 개발 명세

- [독립 자율개선 루프 상세 계약 v2.0](docs/evolution/standalone-autonomy-spec-v2.md) — 내부 12개 모듈, 상태 기계, 증거 계약, 구현 단계
- [cerberus 전용 구현 계약](docs/evolution/cerberus-implementation-spec-v1.md) — 독자 목표, 평가 및 자체 개선 방법
- [23개 수락 테스트 계획](docs/evolution/acceptance-test-plan-v1.md) — 완료/차단 판정 조건
- [예약 자동개발 지속 프롬프트](docs/evolution/AUTOMATION_CONTINUITY_PROMPT.md) — 매 회차 이전 checkpoint 복구·중복 방지·한 가지 실제 개선

**현재 단계:** 개발 상세 설계 및 읽기 전용 검사 CI. 실제 무인 자기개선 루프와 숨겨진 평가 성과는 미검증이다.

### 3개체 통합 개발 예약 설계 (12분, GitHub Actions Draft)

- [통합 12분 실행 준비 워크플로](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/blob/research/independent-evolution-readme-v1/.github/workflows/sael-three-agent-12min.yml): 매시 05·17·29·41·53분(UTC/KST 분 동일) 각 저장소를 **동시에 별도 읽기 전용 job으로 점검**하도록 제안함.
- **현재는 Draft PR에만 존재하여 12분 예약이 활성화되지 않음.** GitHub Actions `schedule`은 기본 브랜치에 포함된 후에만 작동하며 지연될 수 있음.
- 실제 자율 코드 개발은 각 저장소의 `evolution_runner.py`, 승인된 예산/리스/격리/독립 평가가 마련될 때까지 `NOT_IMPLEMENTED / NOT_RUN`이다.
- ChatGPT의 통합 개발 예약은 별도로 매시간 한 번 진행하며, 세 개체를 하나의 프롬프트 역할극으로 합쳐 독립 검증에 성공했다고 주장해서는 안 됨.
