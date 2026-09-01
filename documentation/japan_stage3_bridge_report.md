# 일본 콘텐츠 3단계 직접 소유 구현 보고서

## 1. 판정

기존 bridge 구조를 철거하고, EAFP가 신게임부터 일본 저널의 생명주기와 상태 변수를 직접 소유하도록 3단계를 다시 구현했다.

- bridge scripted trigger 삭제
- bridge scripted effect와 character bridge effect 삭제
- 일본 월간 bridge on_action과 등록 호출 삭제
- 바닐라 일본 JE 활성 여부·완료 변수·진행 막대를 관측하는 코드 삭제
- `je_meiji_restoration`, `je_meiji_main`, `je_meiji_economy`, `je_meiji_army`, `je_meiji_diplomacy`, `je_taming_the_north`를 EAFP 정의로 직접 교체
- 조선의 류큐 개입 JE를 바닐라 `je_ryukyu_rivalry`와 무관한 독립 EAFP 진행도로 전환
- 구버전 저장 migration 미구현

Victoria 3 1.13.11, 모든 공식 DLC, EAFP만 활성화한 초기 로드에서 이번 직접 소유 파일의 missing key, invalid trigger, invalid effect, invalid scope와 UTF-8 BOM 경고는 0건이었다. `database_conflicts.log`도 0바이트다.

## 2. 직접 소유 구조

### 2.1 메이지 유신

[`common/journal_entries/eafp_00_meiji_restoration.txt`](../common/journal_entries/eafp_00_meiji_restoration.txt)는 다음 5개 키를 `REPLACE:`로 직접 정의한다.

| 저널 | EAFP가 직접 소유하는 상태와 결과 |
|---|---|
| `je_meiji_restoration` | 개항 뒤 시작하고, 막부법 폐지·지주 비정부·정통성 50 이상 상태가 6개월 유지되면 완료한다. 완료 시 EAFP 유신 flag와 사건 `.1`을 직접 설정·호출한다. |
| `je_meiji_main` | 경제·군사·외교 세 EAFP 완료 flag를 직접 집계한다. 완료 시 main 완료 flag와 사건 `.2`를 직접 처리한다. |
| `je_meiji_economy` | 현행 도시 중심지·철도·채무 조건을 사용하되 완료 상태는 `eafp_jap_meiji_economy_finished`에 직접 기록한다. |
| `je_meiji_army` | 농노제·농민 징집병·군사 PM·비정규 보병 조건을 사용하되 완료 상태와 사건 `.3`을 직접 처리한다. |
| `je_meiji_diplomacy` | 전통주의 폐지·독립·승인국 조건을 사용하고 이와쿠라 사절단 변수를 읽지 않는다. |

바닐라 `meiji.*`, `ep2_meiji.*` 사건을 EAFP 후속 사건의 진입점으로 사용하지 않는다. 보존한 옛 사건은 `eafp_jap_meiji_legacy.1-13`으로만 호출한다.

### 2.2 북방과 가라후토

[`common/journal_entries/eafp_07_taming_the_north.txt`](../common/journal_entries/eafp_07_taming_the_north.txt)는 `je_taming_the_north`를 EAFP가 직접 교체한다. 삭제한 옛 `je_hokkaido`는 되살리지 않았다.

- 홋카이도 전역 소유·편입·도시 중심지 조건으로 시작한다.
- EAFP 자체 북방 진행도를 매월 1씩 올린다.
- 36개월 진행, 인구 50만, GDP 100만을 직접 완료 조건으로 사용한다.
- `hokkaido.2-6`은 이 JE의 월간 pulse에서 직접 호출한다.
- 완료 시 `eafp_jap_taming_north_completed`, `hokkaido.1`, 메이지 북방 후일담 `.13`, `je_karafuto` 진입을 직접 처리한다.
- 아이누 사건 분기는 바닐라 `ainu_friendship_var` 대신 EAFP 자체 우호도 변수를 사용한다.

[`je_karafuto`](../common/journal_entries/eafp_japan.txt)는 북방 완료 flag, 홋카이도 보유, 러시아의 극동·사할린 조건만 직접 검사한다. 바닐라 북방 modifier나 JE 완료 상태는 읽지 않는다.

### 2.3 류큐 개입

[`je_eafp_ryukyu_intervention`](../common/journal_entries/eafp_01_ryukyu_rivalry.txt)은 바닐라 `je_ryukyu_rivalry`의 존재·진행 막대·관여국 목록을 더 이상 읽거나 수정하지 않는다.

- 시작 조건은 조선 자체 상태와 `JAP`·`CHI`·`RYU`의 존재뿐이다.
- 사절단 버튼은 EAFP 진행도에 10을 더한다.
- 항구 무장 버튼은 EAFP 진행도에 20을 더한다.
- 진행도 100에서 조선의 독립적인 류큐 결과를 처리한다.

## 3. 삭제한 bridge 자산

다음 활성 파일은 삭제했다.

- `common/scripted_triggers/eafp_japan_vanilla_bridge.txt`
- `common/scripted_effects/eafp_japan_vanilla_bridge_effects.txt`
- `common/scripted_effects/eafp_japan_character_bridge_effects.txt`
- `common/on_actions/eafp_japan_on_actions.txt`

`common/on_actions/00_code_on_actions_definition.txt`에서도 `eafp_japan_on_monthly_pulse_country` 등록을 제거했다. 따라서 일본 상태를 월간으로 폴링하거나 바닐라→EAFP shadow 상태를 동기화하는 실행 경로가 없다.

## 4. 변수 목록

### 4.1 직접 소유 전환에서 새로 추가한 변수

| 변수 | 형식 | 설정 위치 | 역할 |
|---|---|---|---|
| `eafp_jap_restoration_progress` | 수치 | `je_meiji_restoration` | EAFP 유신 완료에 필요한 연속 진행 월수를 기록한다. |
| `eafp_jap_north_development_progress` | 수치 | `je_taming_the_north` | EAFP 북방 개발 진행 월수를 기록한다. |
| `eafp_jap_ainu_friendship` | 수치 | `je_taming_the_north`, `hokkaido.5-6` | EAFP 아이누 갈등·합류 사건 분기를 직접 소유한다. |
| `eafp_ryukyu_intervention_progress_var` | 수치 | 조선 류큐 개입 JE·버튼 | 바닐라 류큐 진행 막대를 대신하는 독립 진행도다. |

### 4.2 유지한 EAFP 결과·중복 방지 변수

| 변수군 | 변수 |
|---|---|
| 유신 결과 | `eafp_jap_restoration_finished`, `eafp_jap_restoration_failed` |
| 메이지 결과 | `eafp_jap_meiji_main_finished`, `eafp_jap_meiji_economy_finished`, `eafp_jap_meiji_army_finished`, `eafp_jap_meiji_diplomacy_finished` |
| 메이지 사건 guard | `eafp_jap_meiji_legacy_1_fired`부터 `eafp_jap_meiji_legacy_13_fired`까지 13개 |
| 북방 결과 | `eafp_jap_taming_north_completed`, `eafp_jap_taming_north_failed` |
| 홋카이도 사건 guard | `eafp_jap_hokkaido_1_fired`, `eafp_jap_hokkaido_castle_chain_started`, `eafp_jap_hokkaido_castle_chain_completed` |
| 가라후토 수명주기 | `eafp_jap_karafuto_started`, `eafp_jap_karafuto_event_resolved`, `eafp_jap_karafuto_closed` |

### 4.3 제거한 shadow·동반 JE 변수

다음 변수는 더 이상 설정하거나 읽지 않는다.

- `eafp_jap_seen_meiji_restoration`
- `eafp_jap_seen_meiji_main`
- `eafp_jap_seen_taming_north`
- `eafp_jap_seen_ryukyu_rivalry`
- `eafp_jap_meiji_companion_started`
- `eafp_jap_meiji_companion_completed`
- `eafp_jap_meiji_companion_failed`
- `eafp_jap_legacy_restoration_progress`
- `eafp_jap_meiji_main_failed`

### 4.4 읽지 않는 바닐라 일본 변수

다음 식별자는 활성 EAFP `common`·`events` 코드에서 참조 0건이다.

- `meiji_var`
- `completed_je_meiji_economy`
- `completed_je_meiji_army`
- `completed_je_meiji_diplomacy`
- `iwakura_mission_finished`
- `japan_restoration_complete`
- `restoration_timer_var`
- `ainu_friendship_var`
- `hokkaido_agriculture_potentials_counter_var`
- `hokkaido_agriculture_arable_counter_var`

## 5. 신게임 전용 원칙

- 기존 저장에 flag를 소급 설정하지 않는다.
- 기존 저장의 바닐라 변수를 EAFP 변수로 변환하지 않는다.
- 삭제된 bridge shadow flag를 정리하는 migration을 만들지 않는다.
- 콘텐츠 버전 변수와 migration on_action을 만들지 않는다.

## 6. 검증 결과

### 6.1 정적 검사

| 검사 | 결과 |
|---|---:|
| 활성 `common`·`events`의 `eafp_japan_*` bridge 호출 | 0 |
| bridge 파일 존재 | 0 / 4 |
| 바닐라 메이지·북방 내부 변수 참조 | 0 |
| 변경 대상 파일 중괄호 불균형 | 0 |
| `git diff --check` 공백 오류 | 0 |
| 새 JE 파일 UTF-8 BOM 누락 | 0 / 3 |

### 6.2 EAFP 단독 초기 로드

| 항목 | 결과 |
|---|---|
| 실행 | `victoria3_win_console.exe -debug_mode` |
| 활성 콘텐츠 | 모든 공식 DLC + EAFP만 |
| 테스트 뒤 사용자 `content_load.json` | 원본 바이트 복원 확인 |
| 테스트 프로세스 | 잔존 0 |
| 직접 소유 일본 파일의 missing key | 0 |
| 직접 소유 일본 파일의 invalid trigger/effect/scope | 0 |
| 직접 소유 일본 파일의 UTF-8 BOM 경고 | 0 |
| `database_conflicts.log` | 0 bytes |

전체 `error.log`에는 4단계 이후 처리 대상으로 남아 있는 지역 막번체제 group, 구형 일본 사건 trigger, 옛 일본 building history 및 다른 국가 콘텐츠의 기존 오류가 남아 있다. 이번 직접 소유 메이지·북방·류큐 파일에서 발생한 오류는 아니다.

바닐라에 이미 존재하는 예약 현지화 키 `je_meiji_main_goal`이 직접 교체된 JE에서는 자동 사용되지 않는다는 redundant localization 알림 1건은 남는다. missing localization이나 실행 오류는 아니며, EAFP는 JE 이름과 설명만 세 언어 `replace` 파일에서 직접 덮어쓴다.

### 6.3 보존 로그

| 파일 | bytes | lines | SHA-256 |
|---|---:|---:|---|
| `japan_stage3_direct_error.log` | 70574 | 380 | `5168e31386c3a1a45a7366ba48fbf3c12c545c448746a675dec531ee006759c4` |
| `japan_stage3_direct_debug.log` | 300584 | 2852 | `a8959071993786a7081eabe105ff55e23e14c787be9bc32ef4086d3af69aacc5` |
| `japan_stage3_direct_game.log` | 83157 | 829 | `c0ca7e289c668e47e876f242e81a618cdca1072b5588575b9db0f9cc370f668a` |
| `japan_stage3_direct_database_conflicts.log` | 0 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## 7. 4단계 경계

이번 구조 변경은 3단계에서 만들었던 bridge와 바닐라 상태 의존성만 제거한다. 다음 항목은 기존 계획대로 4단계 작업이다.

- 7개 `je_bakuhantaisei_*`와 goryo·independency 제거
- `reduce_nidome*` 제거
- 저택 소유 인물 충성도 기반 세금 공식
- 8개 막부 정책·청원 JE 제거
- `je_tenpo_famine` 삭제와 `je_tenpo_crisis` 사건 병합
- 중복 인물 template의 물리 삭제와 참조 통합

따라서 3단계 종료 상태는 “EAFP를 켠 신게임에서 EAFP가 메이지·북방·류큐 후속 콘텐츠의 상태와 진입을 직접 소유하며, bridge나 바닐라 일본 상태 관측을 사용하지 않는 상태”다.
