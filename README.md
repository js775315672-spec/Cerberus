# Cerberus

Cerberus는 Ouroboros가 만든 후보와 Fenrir의 검토 보고서를 받아 출처·재현 가능성을 독립 검증하는 프로젝트입니다. **코드 분리/CI 성공만으로 모델 지능 향상이나 독립 평가 통과를 주장하지 않습니다.**

<!-- cerberus-ofc-dashboard:start -->
## O→F→C 검증 대시보드

> **기록 시점: 2026-11-21 16:12 KST** · 증거 기반 **스냅샷**(자동 실시간 갱신 아님). 최신 기록: [O 공용 원장 #347](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/issues/347) · [C 이슈 #2](https://github.com/js775315672-spec/Cerberus/issues/2) · [Actions](https://github.com/js775315672-spec/Cerberus/actions).

**현재 상태: `BLOCKED / WAITING_FENRIR_REPORT_REPAIR` · 후보 최종 판정 `INCONCLUSIVE` · `FENRIR_VERIFIED=false`**

| 단계 | 확인된 결과 | 아직 미완료인 것 | 증거 |
| --- | --- | --- | --- |
| **O 후보** | [PR #346](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/pull/346) HEAD `083eb00e9efb91c8a951a551a91fcccfb6d2efcb`. 고정 **단일 소스 파일** SHA-256 `1c77af88c66ffa1a3abbdb7176d328d9d3803687138c43cb24cd749b2e4d7969` | 전체 PR 아티팩트 단일 SHA-256·test_contract_sha·owner/lease 별도 확인 필요 | [후보 원본](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/blob/083eb00e9efb91c8a951a551a91fcccfb6d2efcb/scripts/oril_v2_teacher_distillation_pack.py) |
| **F 실행/수신** | 별도 Qwen2.5-Coder-1.5B-Instruct runner와 보고서 ZIP 생성·수신 실행 확인. ZIP SHA-256 `df8195471f5b1fc75c9f2b1389ddc0e193d6fc3116944cbd3adf7c0ba2f10f4e` | **원본 비판 텍스트 절단**, 예시 URL 포함, F-ID/심각도/확정·가설/재현/반증 테스트/PASS·FAIL 기준 누락. 독립 비판 계약 **불합격** | [Actions #44875233515](https://github.com/js775315672-spec/Cerberus/actions/runs/44875233515) · [본문 감사](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/issues/347#issuecomment-7058820709) |
| **C 원본 수신** | 출처·실행 ID·고정 후보 소스 해시 대조 실험 완료 | 수신 성공은 검증 PASS가 아님 | [Draft PR #3](https://github.com/js775315672-spec/Cerberus/pull/3) |
| **C 독립 replay/holdout** | 해당 실제 후보에 대한 독립 합격 **0건 확인** | 격리 검증·미공개 평가 미실행. 유효한 F 보고서 수신 후 착수 | [이슈 #2](https://github.com/js775315672-spec/Cerberus/issues/2) |
| **승인/운영** | 보호 게이트 변경·자동 병합·배포 없음 | 사용자 승인 및 외부 증거 필요 | [O 원장 #347](https://github.com/js775315672-spec/Harness-Ouroboros-MCP/issues/347) |

### 지금 해결해야 할 차단 원인

1. **P0 — FENRIR_REPORT 재발행:** 원본 절단 보고서를 FAIL fixture로 고정하고 JSON 구조화 필드·종료 검증·실제 evidence URL을 확인합니다. 독립 run/provenance와 동일 후보 해시를 재검증합니다.
2. **P1 — 원자 lease / 작업 owner:** 5개 예약 중 동일 후보 재호출·동시 수정 방지.
3. **P2 — Cerberus 독립 검증:** F 계약이 통과한 뒤에만 별도 보호 러너에서 재현·위양성/위음성·미공개 holdout 평가.

### 개선 속도와 품질 · 증거 기준

| 지표 | 값 | 추세 |
| --- | --- | --- |
| 실제 O→F→C **완결** 검증 | `0건 확인` | 합격/속도 개선 **미입증** |
| 엔드투엔드·모델 호출·독립 검증·운영 시간 | 정규화된 비교 자료 **미측정** | **판단불가** |
| 최근 5~12개 동일 난이도 중앙값·n·증감률 | 비교 가능한 완결 표본 부족 | **산정 불가** |
| 시간당 독립 검증 통과 건수 | 총 실측 작업시간 미확보 | **산정 불가** |
| 재시도·실패·회귀·롤백률 / 비용·대기시간 | 동일 조건 원본 로그 미집계 | **미측정** |
| 미공개 평가/모델 지능 품질 변화 | 미측정 / 미입증 | **판단불가** |

**주의:** GitHub Actions `success`는 Fenrir 작업과 Cerberus **수신 워크플로**가 실행됐다는 뜻이지 구조화 보고서 합격·독립 후보 검증·지능 향상 의미가 아닙니다. README의 값은 확인된 사건의 스냅샷이며, 갱신 시 근거 링크와 SHA를 포함한 별도 PR로 수정합니다.
<!-- cerberus-ofc-dashboard:end -->
