# 일본 콘텐츠 1단계 최초 로드 보고서

## 1. 실행 정보

| 항목 | 값 |
|---|---|
| 실행 시각 | 2026-09-01 00:41:52 KST |
| 실행 파일 | `victoria3_win_console.exe -debug_mode` |
| 게임 버전 | Victoria 3 `1.13.11` |
| 전면 복원 파일 | 53개, 2,312,731 bytes |
| 동일성 검사 | 원본–활성본 SHA-256 불일치 0개 |
| 초기화 결과 | `Empty -> Game` 전환 완료, 66.93539초 |
| 테스트 종료 | 초기화 로그 확보 후 프로세스 정상 종료 처리 |

현재 launcher 설정에는 EAFP와 Workshop 항목 `3385002128`이 함께 활성화되어 있었다. 사용자 playset은 변경하지 않았다. 따라서 원시 로그에는 다른 모드와 바닐라에서 발생한 메시지도 포함되며, 아래 분류는 일본 파일·키·경로가 확인되는 항목에 초점을 둔다.

## 2. 보존한 원시 로그

| 파일 | bytes | SHA-256 |
|---|---:|---|
| `documentation/japan_stage1_error.log` | 120276 | `a2a029fae525c281a947b9743a0ccb2f386141c1904184ca2f27bc0575e08540` |
| `documentation/japan_stage1_debug.log` | 35197 | `d8a8beb0a18dea1bf0b9b97bc565b91b8e7fb75ffe6b6577e940a991fcb542b8` |
| `documentation/japan_stage1_game.log` | 112581 | `d71a6e87b57a8e7ffb878322530bd0e530cf0bbdf7597cf4ff7434d27e426bd2` |
| `documentation/japan_stage1_database_conflicts.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## 3. 요약

- `error.log` 전체 827줄 중 timestamp가 있는 오류는 728줄이었다.
- 일본 관련 파일명·키 필터에 일치한 줄은 484줄이었다.
- localization 중복 메시지는 일본 필터 안에서 185개였다.
  - `japan_historical_names_l_korean.yml` 내부 중복이 177개였다.
  - `kurofune_l_korean.yml`의 `meiji.13.*`, `meiji.14.*`와 현행 바닐라 localization 충돌이 8개였다.
- `common/scripted_effects/eafp_japan_effects.txt` 관련 메시지가 148개로 가장 많았다.
- 게임은 오류가 있어도 데이터베이스 초기화를 끝내고 메인 게임 상태로 전환했다. 이 보고서는 수정 전 기준선이며 오류 해결을 수행한 결과가 아니다.

## 4. 우선 수정군

| 우선도 | 유형 | 최초 로드 근거 | 후속 처리 |
|---|---|---|---|
| P0 | 바닐라 JE 중복 | `je_ryukyu_rivalry`, `je_zaibatsu` duplicated key | 계획대로 바닐라 소유로 돌리고 EAFP 확장만 분리 |
| P0 | 회사 중복 | `company_sumitomo` duplicated key | 바닐라 회사 정본 사용, EAFP 중복 정의 제거 |
| P0 | 옛 이념 ID | `ideology_nankiha`, `ideology_kaikakuha`, `ideology_hoshuha`, `ideology_hitotsubashiha`가 invalid | 현행 바닐라 덴포 파벌 adapter와 EAFP faction resolver로 교체 |
| P0 | 지역·국가 ID | `region_japan`, `NIP`가 invalid | 현행 strategic region과 `JAP`로 이관 |
| P0 | JE group 누락 | `je_group_bakuhantaisei` 참조 실패 8개 | 상위 JE UI 재설계 시 현행 group 또는 독립 group 정의로 교체 |
| P0 | history 오류 | `jap_building.txt` invalid building, `je_terakoya` invalid journal entry | 현행 건물·바닐라 JE 기준으로 history 갱신 |
| P1 | 효과·트리거 문법 | EAFP 일본 effect PostValidate 48개, 일본 이벤트 trigger PostValidate 다수 | wrapper 효과·트리거로 순차 치환 |
| P1 | localization 자체 중복 | 역사명 파일 내부 중복 177개 | 첫 정의/최종 정의 정책을 정하고 중복 키를 하나로 정리 |
| P1 | 쿠로후네 localization 충돌 | `meiji.13.*`, `meiji.14.*` 8개 | EAFP namespaced 키로 이관 |
| P1 | 이벤트 고아 | `meiji.13`, `eafp_japan.1/2007/2309/5004`, `tenpo_famine.1`, `zaibatsu_events.1-4` 등 | 살아남는 JE·on_action 또는 바닐라 사건 풀에 재연결 |
| P1 | 구식 회사·건물 | `building_military_shipyard` 등 invalid key | 현행 building type으로 매핑하거나 중복 회사와 함께 제거 |

## 5. 대표 오류 위치

- `common/journal_entries/eafp_japan.txt`: `je_group_bakuhantaisei` 누락, `je_zaibatsu` 중복, `NIP` 참조
- `common/scripted_effects/eafp_japan_effects.txt`: 옛 파벌 이념과 다수의 effect PostValidate 실패
- `events/eafp_jap_events/eafp_japan.txt`: 폐지된 trigger·`region_japan` 참조
- `events/eafp_jap_events/eafp_boshin_war.txt`: `NIP`와 옛 지역 계산 참조
- `common/company_types/eafp_companies_japan.txt`: `company_sumitomo` 및 구식 건물 중복·누락
- `localization/korean/japan_historical_names_l_korean.yml`: 파일 내부 중복 키
- `localization/korean/unused/kurofune_l_korean.yml`: 바닐라 `meiji.*` localization 충돌

## 6. 1단계 판정

1단계의 목적은 오류 없는 최종 구현이 아니라, 모든 옛 일본 파일을 무수정 활성 복원하고 실제 초기 로드 오류를 기준선으로 보존하는 것이다. 다음 조건을 충족했으므로 1단계는 완료로 판정한다.

- 53개 원본이 모두 활성 확장자로 복원됨
- 복원 당시 원본–활성본 SHA-256 불일치 0개
- 기존 활성 파일 덮어쓰기 0개
- 원본 `.disable` 수정·삭제 0개
- Victoria 3 데이터베이스 초기화 완료
- 최초 `error/debug/game/database_conflicts` 로그 보존
- 후속 수정 우선군 분류 완료
