# 일본 콘텐츠 4단계 런타임 오류 해결 계획

작성일: 2026-09-02

기준 게임: Victoria 3 1.13.11

검증 환경: 모든 DLC 활성, EAFP만 활성, `-debug_mode`, 신게임 전용

세이브 migration: 수행하지 않음

bridge trigger/effect 및 바닐라 JE 상태 복제: 사용하지 않음

## 1. 이번 로그가 증명한 범위

이번 실행에서는 게임 데이터베이스와 메인 메뉴를 정상 로드한 뒤 샌드박스 신게임 초기화를 시작했다. 이 과정에서 전역 1836 history가 실행되었으나, 일본 국가 선택 후 날짜 진행까지는 완료하지 않았다. 따라서 이 문서는 다음 두 층을 구분한다.

1. 메인 메뉴 이전에 검출된 데이터베이스·구문·참조 오류
2. 신게임 history 초기화에서 추가로 검출된 국가 소유권·주 scope 오류

원본 로그는 다음 위치에 보존한다.

- `scratch/japan_stage4_runtime_qa/menu_error.log`: 메인 메뉴 기준선
- `scratch/japan_stage4_runtime_qa/latest_error.log`: 신게임 history 초기화 포함
- `scratch/japan_stage4_runtime_qa/menu_game.log`
- `scratch/japan_stage4_runtime_qa/latest_game.log`
- `scratch/japan_stage4_runtime_qa/latest_debug.log`

테스트를 위해 변경했던 `content_load.json`은 기존 플레이셋으로 복원했으며 Victoria 3 프로세스도 종료했다.

## 2. 핵심 판정

- `database_conflicts.log`는 0바이트다. 이번 오류의 주원인은 같은 데이터베이스 키를 이중 등록한 것이 아니라, 존재하지 않거나 현행 1.13.11에서 형식이 바뀐 키를 옛 스크립트가 참조하는 데 있다.
- `eafp_00_meiji_restoration.txt`, `eafp_07_taming_the_north.txt`, `eafp_07_tenpo_crisis.txt`의 7개 `REPLACE:` JE는 직접적인 JE 파싱 오류를 만들지 않았다. 세 파일에서 나온 직접 경고는 UTF-8 BOM 누락뿐이다.
- 따라서 바닐라 전문을 다시 복사하거나 `REPLACE:` 본체를 재설계하지 않는다. 먼저 그 본체가 호출하는 옛 막부 지원 계층을 현행 문법으로 복구한다.
- 가장 먼저 해결할 오류는 `INJECT:STATE_CHUBU`와 `INJECT:STATE_CHUGOKU`다. 두 문자열이 patch 지시어가 아니라 새 state region 키로 읽혀 0개 province를 가진 잘못된 주가 만들어졌다.
- 신게임 history에서 추가된 120개 오류 엔트리 중 대부분은 잘못된 초기 주 소유권과 삭제된 `STATE_CHUBU`가 일으킨 연쇄 오류다. 이 상태에서는 일본 저널의 실제 동작을 검증할 수 없다.

## 3. 현재 오류 기준선

`latest_error.log`는 1,454줄, 1,004개 타임스탬프 엔트리다. 아래 수치는 로그 문자열 출현 횟수이며 하나의 원인이 `PostValidate` 오류를 추가로 발생시키는 경우가 있으므로 고유 버그 수와 같지는 않다.

| 오류 묶음 | 출현 | 판정 | 우선순위 |
|---|---:|---|---|
| 잘못된 `INJECT:STATE_*` | 4 | 일본 map/history 직접 차단 | P0 |
| 신게임 `region_state` 무효 | 28 | 중국·만주·몽골·신강 소유권 변경 시점 문제 | P0 |
| `NULL_STATE` pop 생성 | 63 | 위 소유권 문제의 연쇄 오류 | P0 |
| `NULL_STATE` building 생성 | 14 | 위 소유권 문제의 연쇄 오류 | P0 |
| 군사 편제 생성 실패 | 5 | 위 소유권 문제의 연쇄 오류 | P0 |
| `STATE_CHUBU` 없음 | 1 | 현행 `STATE_TOKAI`·`STATE_HOKUSHINETSU` 이관 누락 | P0 |
| 다이묘 충성도 effect 인자 오류 | 15 | 계산식 블록을 scripted effect 인자로 전달 | P0 |
| 구식 `has_port` | 6 | 현행 trigger에서 제거됨 | P0 |
| `law_bakufu` variant를 parent trigger에 전달 | 5 | `has_law_or_variant` 오용 | P0 |
| 잘못된 `region_japan` | 14 | 전략지역과 지리지역 체계 혼용 | P0 |
| 없는 `NIP` 국가 | 8 | 옛 보신전쟁 고정 태그 잔재 | P0 |
| 없는 존황양이 movement | 7 | 정의 제거 후 참조 잔존 | P0 |
| 없는 막부 4개 이념 관련 오류 | 56 | 정의를 주석 처리했으나 trigger/effect가 계속 사용 | P0 |
| `je_group_bakuhantaisei` 없음 | 1 | 그룹 정의만 주석 처리됨 | P0 |
| trigger localization 없음 | 4 | 활성 trigger와 `.disable` 현지화의 불일치 | P0 |
| 잘못된 `has_potential_resource` target | 2 | building group를 building type 자리에 사용 | P0 |
| 잘못된 인물 템플릿 | 1 | 빈 `ideology =`와 잘못된 IG 값 | P0 |
| 일본 static modifier type 없음 | 5 | 1.13.11에서 삭제·개명된 modifier | P0 |
| UTF-8 BOM 누락 | 30 | 일본 활성 파일 20개를 포함 | P1 |
| 한국어 일본 인명 loc 중복 | 177 전후 | 한 파일 안에서 154개 키가 중복됨 | P1 |
| 사용되지 않는 4단계 변수 | 3 | 실제 소비자가 없는 추적 변수 | P1 |
| 한국·몽골·중국·debug·GUI·asset 오류 | 다수 | 일본 직접 오류와 분리하되 최종 통합 로그에서 해결 | P2 |

## 4. 변경 금지선

다음 결정은 오류를 고치는 과정에서도 되돌리지 않는다.

- 7개 지역 `je_bakuhantaisei_*`를 복원하지 않는다.
- 8개 `je_bakufu_seisaku*`, `je_terakoya`, 독립 `je_tenpo_famine`, 옛 `je_hokkaido`, 옛 재벌 JE·사건을 복원하지 않는다.
- `goryo`, 지역 `independency`, `reduce_nidome*`를 다시 만들지 않는다.
- 바닐라 JE 상태를 읽어 EAFP 변수로 복제하는 bridge를 만들지 않는다.
- 구버전 세이브용 cleanup, tombstone JE, migration runner를 만들지 않는다.
- 오류를 숨기기 위한 빈 scripted trigger/effect나 항상 참인 대체 정의를 추가하지 않는다.
- 현행 바닐라 기반 7개 `REPLACE:` JE는 해당 JE 자체에서 재현되는 오류가 확인되지 않는 한 수정하지 않는다.

## 5. P0-A: map 및 신게임 history 정상화

### 5.1 잘못된 state region patch 제거

대상 파일:

- `map_data/state_regions/eafp_state_regions.txt`
- `common/history/pops/99_jap.txt`
- `events/eafp_jap_events/eafp_japan.txt`
- `events/eafp_jap_events/eafp_boshin_war.txt`
- `common/scripted_effects/eafp_japan_effects.txt`
- `common/scripted_progress_bars/eafp_bakuhantaisei_progress_bars.txt`
- 일본 3개 언어 localization

처리 순서:

1. `INJECT:STATE_CHUBU`와 `INJECT:STATE_CHUGOKU` 블록을 삭제한다. 1.13.11은 이를 부분 patch로 해석하지 않고 별도 state region으로 등록한다.
2. 활성 스크립트·현지화에 남은 `STATE_CHUBU` 54건을 전수 분류한다.
3. 옛 주부 지방을 한 주로 치환하지 않고 현행 바닐라 분할에 맞춰 `STATE_TOKAI`와 `STATE_HOKUSHINETSU` 두 주로 확장한다.
4. `99_jap.txt`의 유교 인구 변환 10%는 두 주에 각각 적용한다. 기존 바닐라 pop을 새로 만들지 않는다.
5. 다이묘 충성도·임무·보신전쟁 지역 효과는 도카이와 호쿠시네쓰를 각각 독립 주로 처리한다. 한쪽 충성도를 다른 쪽에 복사하지 않는다.
6. 진행 막대의 주별 기여 역시 두 주의 저택 소유 다이묘를 따로 계산한다.
7. 세 언어에서 `CHUBU` 전용 표시 키를 `TOKAI`와 `HOKUSHINETSU` 키로 분리한다. 옛 문구는 지역명만 교체해 최대한 유지한다.

### 5.2 금광 사건의 현행 자원 모델 이관

`eafp_japan.2203` 계열은 `bg_gold_fields`를 `has_potential_resource`에 넘기고 있다. 이 trigger는 building group가 아니라 building type을 요구한다.

1. 삭제된 `STATE_CHUBU`와 map injection에 의존하는 금 발견 로직을 제거한다.
2. 현행 바닐라 `STATE_HOKUSHINETSU`의 `building_gold_mine = 3`과 `STATE_CHUGOKU`의 `building_gold_mine = 1` 잠재량을 사용한다.
3. `has_potential_resource = building_gold_mine`으로 후보 주를 검사한다.
4. `force_resource_discovery = building_gold_field`는 현행 두 주에 undiscovered gold resource가 없으므로 사용하지 않는다.
5. 사건 보상은 기존 잠재 금광에 1레벨을 건설하거나 금광 건설 보너스 modifier를 부여하는 방식 중 하나로 통일한다. 새 map resource를 삽입하지 않는다.
6. 사건 ID, 제목, 설명, 선택지 localization은 유지한다.

### 5.3 중국·만주·몽골·신강 소유권 변경 시점 수정

이 묶음은 일본 콘텐츠 자체는 아니지만 신게임 history를 정상화하지 않으면 일본 캠페인 검증이 불가능하므로 선행 P0로 처리한다.

대상 파일:

- `common/history/states/chi_states.txt`
- `common/history/pops/99_chi.txt`
- `common/history/buildings/chi_building.txt`
- 중국·만주·몽골·신강 초기화 on_action/effect

현재 `chi_states.txt`가 `STATE_DZUNGARIA`, `STATE_TIANSHAN`, `STATE_JETISY` 등을 바닐라 POPS·BUILDINGS·MILITARY 실행 전에 CHI에서 XIN/MGL/MCH로 넘긴다. 그 결과 뒤이어 실행되는 바닐라 `region_state:CHI`가 모두 NULL scope가 된다.

해결 방식:

1. `common/history/states`에서는 바닐라 시작 소유권을 유지한다.
2. POPS·BUILDINGS·MILITARY history 완료 후 실행되는 신게임 초기화 effect에서만 대상 주를 MCH/MGL/XIN에 양도한다.
3. 이 effect는 신게임 최초 1회만 실행하되 save migration이나 bridge 역할을 하지 않는다.
4. `99_chi.txt`와 `chi_building.txt`가 바닐라 인구·건물을 다시 생성하는지 비교한다. 중복분은 삭제하고 EAFP 추가분만 양도 후 적용한다.
5. 양도 후 시장 수도, HQ, 군사 편제, 저택·금융지구 소유권이 새 소유국과 일치하는지 확인한다.

통과 조건:

- `Event target link 'region_state' returned an invalid object` 0건
- `NULL_STATE` pop/building 0건
- 동아시아 초기 군사 편제 실패 0건
- `STATE_CHUBU` 및 `INJECT:STATE_*` 0건

## 6. P0-B: 일본 데이터베이스 정본 복구

### 6.1 막번 JE 그룹

`common/journal_entry_groups/eafp_journal_entries.txt`의 주석 처리된 `je_group_bakuhantaisei`를 다시 활성화한다. 별도 새 그룹을 만들거나 `je_bakuhantaisei`를 무관한 바닐라 그룹에 넣지 않는다.

### 6.2 막부 4개 인물 이념

다음 키는 localization과 호출부가 살아 있지만 정의만 주석 처리되어 있다.

- `ideology_kaikakuha`
- `ideology_hoshuha`
- `ideology_hitotsubashiha`
- `ideology_nankiha`

처리 원칙:

1. `common/ideologies/eafp_leader_ideologies.txt`의 옛 정의를 기반으로 네 이념을 복구한다.
2. 1.13.11의 현행 character ideology 예시와 동일한 필드·scope를 사용한다.
3. 옛 `lawgroup_shogunate`처럼 존재 여부가 불명확한 그룹을 그대로 되살리지 않고, 현행 `lawgroup_distribution_of_power`와 `law_bakufu` variant를 기준으로 선호를 작성한다.
4. 이념은 랜덤 생성용이 아니라 EAFP 막부 정치인에게 명시적으로 부여하는 전용 이념으로 유지하므로 자동 선택 weight는 0으로 둔다.
5. 덴포 결말에서 `tenpo_outcome_reformer_var`는 `kaikakuha`·`hitotsubashiha`, `tenpo_outcome_hardliner_var`는 `hoshuha`·`nankiha`에 연결한다. balanced는 양쪽에 대칭 적용한다.

### 6.3 존황양이 운동과 보신전쟁

옛 `eafp_movement_sonno_joi` 정의는 없고 바닐라 DLC에는 이미 `movement_meiji_restorationist`가 있다. 중복 운동을 새로 만들지 않는다.

1. `common/journal_entries/eafp_japan.txt`, `common/on_actions/japan_code_on_actions.txt`, `events/eafp_jap_events/eafp_boshin_war.txt`의 운동 판정을 `movement_meiji_restorationist`로 이관한다.
2. `mitogaku_modifier`가 주는 운동 지지는 현행 movement용 modifier type을 명시적으로 정의해 연결하거나, 해당 modifier type이 실제로 movement 지지에 연결되지 않으면 그 한 효과만 제거한다.
3. 옛 고정 국가 `c:NIP`는 다시 국가 정의로 만들지 않는다.
4. 보신전쟁 상대는 실제 `movement_meiji_restorationist` civil war 또는 diplomatic play의 반대편 국가 scope를 저장해 사용한다.
5. `je_boshin_war_sabaku`, `je_boshin_war_tobaku`와 `boshin_war.*` 사건 ID는 유지하고 고정 태그 참조만 동적 scope로 바꾼다.
6. civil war 종료·패배·정권 교체 후 저장 scope가 유효하지 않은 경우를 `exists`로 방어한다.

### 6.4 trigger localization 복원

`common/trigger_localization/eafp_japan_trigger_loc.disable`의 원문 중 현재도 살아 있는 다음 네 블록만 `.txt`에 복원한다.

- `is_roju`
- `is_rojushuza`
- `is_tairo`
- `has_bakufu_politician_mission`

삭제된 막부 정책 JE 전용 trigger localization은 복원하지 않는다. 세 언어의 기존 `TRIGGER_*` 문구를 재사용한다.

통과 조건:

- missing ideology, movement, JE group, trigger loc 오류 0건
- `NIP` 활성 참조 0건
- 덴포 개혁파·보수파 결과가 실제 막부 정치인 이념에 반영됨

## 7. P0-C: 현행 1.13.11 문법 및 scope 수정

### 7.1 `law_bakufu` variant

`law_bakufu`는 `law_autocracy`의 variant다. 활성 일본 파일의 모든 `has_law_or_variant = law_type:law_bakufu`를 `has_law = law_type:law_bakufu`로 바꾼다. 로그에 즉시 드러난 5건뿐 아니라 journal, on_action, scripted effect에 남은 활성 참조도 모두 수정한다.

### 7.2 항구와 일본 지역

- state scope의 `has_port = yes` 6건은 현행 바닐라 패턴인 `is_coastal = yes`로 바꾼다.
- state 집합 판정은 `is_in_geographic_region = geographic_region_japan`을 사용한다.
- `has_interest_marker_in_region`은 strategic region을 요구하므로 `region_japan`을 `region_northeast_asia`로 바꾼다.
- 일본 인구·종교 script value는 전략지역 scope 대신 `geographic_region_japan`에 속한 state를 순회한다.
- `region_japan_current`는 해상 strategic region이므로 일본 본토 외교 관심 판정의 대체값으로 사용하지 않는다.

### 7.3 다이묘 충성도 effect 인자

`add_eafp_japan_daimyo_loyalty_inverse`는 `VALUE` 인자로 계산식 블록을 전달해 내부의 `value`, `multiply`가 알 수 없는 effect 인자로 해석된다.

1. inverse wrapper를 제거한다.
2. 모든 호출부에서 최종 부호가 확정된 숫자를 `add_eafp_japan_daimyo_loyalty`에 직접 전달한다.
3. 동적 계산이 필요한 경우 호출 전에 `save_scope_value_as`로 값을 계산한 뒤 단일 값 scope를 전달한다.
4. 기존 autonomy 증가→충성도 감소, autonomy 감소→충성도 증가 대응표를 호출부별 manifest로 만들어 부호 반전 실수를 막는다.
5. 모든 호출에서 대상 state에 저택 소유 magnate가 없을 때는 갱신 effect를 한 번 실행한 후 다시 찾고, 그래도 없으면 상태를 변경하지 않는다.

### 7.4 인물 템플릿

`EAFP_japan_character_templates.txt`의 `eafp_yamaoka_tesshu`는 `interest_group = ideology_reformer`, 빈 `ideology =`를 가지고 있다.

1. 현행 인물 자료와 기존 EAFP 역할을 확인해 올바른 interest group을 지정한다.
2. `ideology = ideology_reformer`를 완전한 한 줄로 복구한다.
3. 같은 형태의 빈 `ideology =`, `interest_group = ideology_*`, `interest_group = ig:*` 혼용을 두 일본 템플릿 파일 전체에서 정적 검색한다.

### 7.5 일본 static modifier

`EAFP_japan_modifiers.txt`의 5개 오류는 다음 원칙으로 수정한다.

| 옛 modifier | 처리 |
|---|---|
| `country_law_enactment_time_mult = -0.1` | `country_law_enactment_speed_mult = 0.1`로 의미와 부호를 변환 |
| `country_max_declared_interests_add` | 1.13.11에 직접 대응 modifier가 없으므로 삭제하고 기존 influence·maneuver 페널티만 유지 |
| `country_convoys_capacity_mult` | 1.13.11에 직접 대응 modifier가 없으므로 삭제하며 임의의 경제 보너스로 바꾸지 않음 |
| `state_pop_support_eafp_movement_sonno_joi_mult` | 바닐라 `movement_meiji_restorationist` 대응 modifier가 검증되면 그 키로 이관, 아니면 해당 한 효과 제거 |

통과 조건:

- unknown trigger/effect/argument 0건
- 일본 파일의 unknown modifier type 0건
- 잘못된 law variant target 0건
- 인물 템플릿 parse 오류 0건

## 8. P1: 인코딩·현지화·변수 정리

### 8.1 UTF-8 BOM 및 CRLF

로그에 나온 일본 활성 파일 20개를 내용 수정이 끝난 뒤 일괄적으로 UTF-8 BOM + CRLF로 정규화한다. 중간 단계에서 반복 변환하지 않는다. 마지막에는 실제 바이트 `EF BB BF`와 CRLF를 검사한다.

대상에는 다음 핵심 파일이 포함된다.

- 4개 일본 JE 파일
- `events/eafp_jap_events/eafp_japan.txt`, `eafp_boshin_war.txt`, `eafp_hokkaido.txt`
- 2개 일본 character template
- 일본 scripted effect/trigger/button/progress bar/on_action/static modifier/script value
- 일본 history country/global 파일

### 8.2 한국어 일본 인명 중복

`localization/korean/japan_historical_names_l_korean.yml`에는 1,586개 키 중 154개 키가 중복되고 중복 초과 행은 178개다.

1. 키별 모든 번역값을 비교한다.
2. 값이 동일하면 첫 정본 한 줄만 유지한다.
3. 값이 다르면 실제 인물 템플릿에서 사용하는 표기와 EAFP 일본 번역 스타일을 기준으로 하나를 선택하고 결정표에 기록한다.
4. 영어·중국어 파일에도 동일 키 중복 검사를 실행한다.
5. 삭제한 중복 인물 템플릿 때문에 완전히 미사용이 된 이름 키는 이번 단계에서 삭제하지 않는다. 중복 제거와 미사용 정리는 분리한다.

### 8.3 사용되지 않는 4단계 변수

현재 경고 대상:

- `eafp_jap_bakufu_reform_timed_out`
- `eafp_jap_restoration_failed`
- `eafp_jap_meiji_diplomacy_finished`

각 변수는 실제 후속 사건·조건·UI 소비자가 있으면 그 소비자를 정상 경로에 연결하고, 단순 보고용 흔적이면 set 구문과 구현 보고서 항목을 함께 삭제한다. 경고를 없애기 위한 더미 trigger나 bridge read는 만들지 않는다.

## 9. P2: 일본 외 전역 오류 분리 처리

일본 P0 수정 후에도 EAFP 전체 로그를 깨끗하게 만들려면 다음 묶음을 별도 변경 단위로 처리한다.

1. 한국·몽골 static modifier의 1.13.11 개명: 전체 13개 unknown modifier 중 일본 5개를 제외한 항목
2. `events/eafp_debug.txt`의 없는 `fix_variable_error` effect 14건과 문자열을 loc key처럼 사용한 3건
3. 만주 범위 effect `every_scope_state_in_dongbei`, `random_scope_state_in_dongbei`
4. 몽골의 구식 relations·infamy event target
5. 한국 character interaction의 중복 `potential`
6. 일본 외 progress bar·button localization 누락
7. 한국 궁궐·에도성 mesh shader 오류와 누락 texture
8. porcelain prestige good 3개 제한 assertion
9. GUI datamodel·texture·localization 오류

이 작업은 일본 4단계 파일과 같은 커밋에 섞지 않는다. 다만 P0-A의 중국 초기 소유권 문제는 일본 신게임을 막으므로 예외적으로 먼저 처리한다.

## 10. 구현 순서와 변경 단위

1. **A1 — state key 정본화**
   - 잘못된 map injection 삭제
   - `CHUBU`를 `TOKAI`·`HOKUSHINETSU`로 분리
   - 정적 검색과 메인 메뉴 로드
2. **A2 — 신게임 history 순서**
   - CHI 주 양도 시점 이동
   - pop/building/military 중복 정리
   - 샌드박스 신게임 history 로그 검증
3. **B1 — 막부 DB 정의**
   - JE group, 4개 이념, trigger localization 복구
   - missing database key 검증
4. **B2 — 보신전쟁 정본화**
   - 바닐라 restorationist movement 사용
   - `NIP`를 동적 civil war scope로 교체
5. **C1 — 문법 일괄 수정**
   - `law_bakufu`, `has_port`, 지역 종류, 자원 target
6. **C2 — 충성도 effect**
   - inverse wrapper 제거와 모든 호출부 부호 검증
7. **C3 — 템플릿·modifier**
   - Yamaoka 템플릿과 일본 modifier 5개 수정
8. **D1 — 인코딩·loc·변수**
   - BOM/CRLF, 인명 중복, 미사용 변수
9. **E1 — 실제 일본 신게임 회귀**
   - 1836 일본 선택, 날짜 진행, JE·사건별 강제 검증
10. **E2 — 일본 외 backlog**
    - P2 항목을 기능별 별도 변경 단위로 해결

각 변경 단위는 직전 로그와 diff를 남기며, 새 오류가 생기면 다음 단위로 넘어가지 않는다.

### 10.1 2026-09-02 선택 구현 현황

- [x] A1 — state key 정본화
- [ ] A2 — 신게임 history 순서: 이번 요청에서 제외
- [x] B1 — 막부 DB 정의
- [x] B2 — 보신전쟁 정본화
- [x] C1 — 선택된 일본 구식 문법 수정
- [x] C2 — 충성도 effect
- [ ] C3 — 템플릿·modifier: 이번 요청에서 제외
- [ ] D1 — 전체 인코딩·loc·변수: 이번 요청에서 제외
- [ ] E1 — 1836 일본 30일 및 사건별 회귀
- [ ] E2 — 일본 외 backlog

선택 구현 보고서: [japan_stage4_selected_p0_implementation_report.md](japan_stage4_selected_p0_implementation_report.md)

## 11. 실제 게임 검증 절차

### 11.1 정적 검사

- 활성 `.txt`의 중괄호 균형
- UTF-8 BOM·CRLF
- top-level key 중복
- `STATE_CHUBU`, `INJECT:STATE_`, `c:NIP`, `region_japan`, `has_port`, `eafp_movement_sonno_joi` 활성 참조 0건
- `has_law_or_variant = law_type:law_bakufu` 활성 참조 0건
- 4개 막부 이념, 막번 JE 그룹, 4개 trigger localization의 정의·참조 일치
- 다이묘 충성도 effect 호출부의 `TARGET`·`VALUE` 계약 일치

### 11.2 데이터베이스 로드

모든 DLC와 EAFP만 활성화하고 `-debug_mode`로 메인 메뉴까지 실행한다.

통과 기준:

- `database_conflicts.log` 0바이트 유지
- 일본 파일 unknown key/trigger/effect/modifier/argument 0건
- 일본 파일 BOM 경고 0건
- 7개 바닐라 기반 `REPLACE:` JE 직접 오류 0건

### 11.3 신게임 전역 초기화

샌드박스 또는 1836 신게임을 시작해 history 실행을 완료한다.

통과 기준:

- `region_state` invalid 0건
- `NULL_STATE` pop/building 0건
- 군사 편제 초기화 실패 0건
- 중국·만주·몽골·신강의 초기 소유권과 수도·시장·HQ 정상

### 11.4 1836 일본 시작

일본을 선택하고 일시정지 상태에서 다음을 확인한다.

- `je_tenpo_crisis`, `je_bakuhantaisei`와 바닐라 시작 JE가 중복 없이 표시
- 삭제한 지역·정책·독립 기근·테라코야·재벌 JE가 표시되지 않음
- 다이묘 magnate와 `daimyo_var`, 각 주 `cached_daimyo_loyalty`가 유효
- 도카이와 호쿠시네쓰가 서로 독립적으로 충성도·세금 누수 계산에 참여
- 4개 막부 이념을 가진 정치인이 정상 생성되고 tooltip이 표시

그 뒤 30일을 진행해 weekly/monthly pulse와 최초 사건을 검증한다.

### 11.5 사건별 강제 회귀

debug console 또는 제한된 테스트 fixture로 다음 분기를 각각 새 게임에서 검증한다.

1. 덴포 hardliner/reformer/balanced/timeout
2. 메이지 restoration 성공·실패와 main/economy/army/diplomacy 완료
3. `je_taming_the_north` 성공·실패와 `hokkaido.*`·`je_karafuto` 후속
4. 바닐라 restorationist movement의 civil war와 EAFP 보신전쟁 양측 JE
5. 도카이·호쿠시네쓰·주고쿠 다이묘 충성도 증감과 세금 누수
6. 금광 사건 대상 선정과 보상

각 분기에서 공식 바닐라 보상과 EAFP 후속 사건이 각각 한 번만 실행되어야 한다.

### 11.6 저장·재로드

리뉴얼 버전으로 시작한 일본 캠페인만 저장·재로드한다. 구버전 세이브는 열지 않는다.

- 1836 시작 직후
- 덴포 진행 중
- 메이지 JE 진행 중
- 북방 JE 완료 직전
- 보신전쟁 진행 중

재로드 후 JE·변수·다이묘 scope·예약 사건이 중복되지 않아야 한다.

## 12. 최종 완료 조건

1. 일본 직접 P0 오류 문자열의 출현 횟수가 모두 0이다.
2. 신게임 history의 `NULL_STATE`·invalid `region_state`가 0이다.
3. 7개 바닐라 기반 `REPLACE:` JE의 본체와 공식 결과가 보존된다.
4. EAFP 옛 사건 ID와 localization은 삭제 결정된 콘텐츠를 제외하고 유지된다.
5. `STATE_CHUBU`는 도카이·호쿠시네쓰의 현행 두 주 모델로 완전히 이관된다.
6. 보신전쟁은 `NIP` 고정 태그 없이 바닐라 restorationist civil war에서 동작한다.
7. 덴포 reformer/hardliner 결과가 EAFP 개혁·보수 파벌에 정확히 반영된다.
8. 다이묘 충성도와 세금 누수는 저택 소유 magnate 기준으로 정상 계산된다.
9. 삭제한 JE·재벌·테라코야·goryo·independency·`reduce_nidome`가 되살아나지 않는다.
10. bridge·바닐라 JE 상태 복제·save migration 코드가 추가되지 않는다.
11. 모든 일본 활성 텍스트 파일이 UTF-8 BOM + CRLF다.
12. 실제 1836 일본 신게임 30일 진행과 새 버전 저장·재로드를 통과한다.
