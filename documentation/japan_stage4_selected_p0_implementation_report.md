# 일본 콘텐츠 4단계 선택 P0 구현 보고서

구현일: 2026-09-02

기준 게임: Victoria 3 1.13.11

검증 조건: 모든 DLC 활성, EAFP만 활성, `-debug_mode`, 신게임용 코드만 고려

세이브 migration: 구현하지 않음

bridge trigger/effect 및 바닐라 일본 JE 상태 조회: 구현하지 않음

## 1. 구현 범위

사용자가 선택한 오류 해결 계획의 1, 3, 4, 5, 6, 7번을 구현했다.

| 번호 | 구현 대상 | 결과 |
|---:|---|---|
| 1 | 잘못된 `INJECT:STATE_*` 제거와 옛 `STATE_CHUBU` 이관 | 완료 |
| 3 | 막번 JE 그룹과 막부 4개 인물 이념 복구 | 완료 |
| 4 | 옛 존황양이 운동을 바닐라 유신 운동에 통합 | 완료 |
| 5 | `NIP` 고정 태그 제거와 실제 내전 상대 scope 사용 | 완료 |
| 6 | 일본 옛 문법·지역·법률·자원 trigger 갱신 | 완료 |
| 7 | 다이묘 충성도 inverse effect 인자 오류 제거 | 완료 |

2번 중국·만주·몽골·신강 초기 소유권 실행 순서와 8번 인물 템플릿·static modifier·전체 인코딩·중복 현지화 정리는 이번 변경 범위에 넣지 않았다.

## 2. 주 지역 이관

- `map_data/state_regions/eafp_state_regions.txt`를 삭제했다. 이 파일에는 엔진이 patch 지시어로 해석하지 못하는 `INJECT:STATE_CHUBU`, `INJECT:STATE_CHUGOKU`만 남아 있었다.
- 활성 스크립트의 `STATE_CHUBU` 참조를 제거했다.
- 옛 주부 전체에 적용되던 다이묘 임무, 충성도 진행 막대, 보신전쟁 후처리, 인구 변환은 `STATE_HOKUSHINETSU`와 `STATE_TOKAI`에 각각 적용되도록 분리했다.
- 밀수와 젠코지 지진처럼 지리적으로 옛 주부 북부를 뜻하는 사건은 `STATE_HOKUSHINETSU`에만 이관했다.
- 영어·한국어·중국어의 임무 선택지, tooltip, modifier, 진행 막대 키를 호쿠시네쓰와 도카이용으로 나눴다.
- `CHUBU_kokudaka_value`는 실제 소비자가 없어 제거했다.

금광 사건 `eafp_japan.2203`은 임의의 state-region 주입을 사용하지 않는다. `geographic_region_japan`에 속하고 편입되었으며 기존 금광이 없고 `building_gold_mine` 잠재량이 있는 주만 후보로 삼아 금광 1레벨을 생성한다.

## 3. 막부 데이터베이스 복구

다음 정의를 활성 파일에 복구했다.

- JE 그룹 `je_group_bakuhantaisei`
- 인물 이념 `ideology_kaikakuha`
- 인물 이념 `ideology_hoshuha`
- 인물 이념 `ideology_hitotsubashiha`
- 인물 이념 `ideology_nankiha`
- trigger localization `is_roju`
- trigger localization `is_rojushuza`
- trigger localization `is_tairo`
- trigger localization `has_bakufu_politician_mission`

4개 이념은 일본 또는 일본에서 발생한 내전국에서만 유효하고 자동 무작위 선택 weight는 0이다. 현행 엔진은 상위법의 variant인 `law_bakufu`를 이념 stance에 직접 넣는 것을 허용하지 않으므로 다음과 같이 `law_autocracy` 선호 강도로 파벌 차이를 표현했다.

| 이념 | `law_autocracy` stance |
|---|---|
| `ideology_hitotsubashiha` | `neutral` |
| `ideology_kaikakuha` | `approve` |
| `ideology_hoshuha` | `strongly_approve` |
| `ideology_nankiha` | `strongly_approve` |

삭제된 막부 정책 JE용 trigger localization과 `law_chusei`는 복원하지 않았다. 어떤 전역 on_action에도 연결되지 않았던 `japan_on_law_enactment_pass` 유휴 블록은 폐기된 `law_chusei` 파서 오류만 만들고 있어 제거했다.

## 4. 존황양이 운동과 보신전쟁

- 활성 `eafp_movement_sonno_joi` 참조를 모두 `movement_meiji_restorationist`로 바꿨다.
- `mitogaku_modifier`가 바닐라 유신 운동 지지에 연결되도록 `state_pop_support_movement_meiji_restorationist_mult` modifier type과 3개 언어 표시 문구를 추가했다.
- 보신전쟁은 더 이상 없는 국가 `c:NIP`를 만들거나 찾지 않는다.
- `japan_on_revolution_start`가 실제 유신 운동 내전국인 `scope:target`에 토막 JE를, 일본 원국에 사막 JE를 추가하고 서로를 JE target으로 저장한다.
- 보신전쟁 JE와 사건은 저장된 실제 상대국을 사용하며 상대 scope가 없을 때는 실행하지 않도록 방어했다.
- 항구·무역 중심지의 소유권도 `c:NIP` 대신 실제 내전 상대국에 부여한다.
- 옛 주간 `c:NIP` 탐색 polling은 삭제하고 `japan_on_revolution_start`, `japan_on_civil_war_won`을 실제 on_action 목록에 연결했다.

## 5. 현행 문법 이관

| 옛 표현 | 현행 처리 |
|---|---|
| `has_law_or_variant = law_type:law_bakufu` | `has_law = law_type:law_bakufu` |
| state scope의 `has_port = yes` | `is_coastal = yes` |
| `has_interest_marker_in_region = region_japan` | `region_northeast_asia` |
| state 집합용 `sr:region_japan` | `is_in_geographic_region = geographic_region_japan` 순회 |
| `has_potential_resource`에 building group 전달 | `building_gold_mine` building type 전달 |
| 삭제된 주에 `force_resource_discovery` | 실제 잠재 금광 후보에 금광 1레벨 생성 |

일본 전체 인구와 신토 인구 script value도 전략 지역 scope가 아니라 보유 주 가운데 `geographic_region_japan` 소속 주를 합산하도록 바꿨다.

## 6. 다이묘 충성도 effect

`add_eafp_japan_daimyo_loyalty_inverse` wrapper와 활성 호출을 제거했다. 총 34개 호출을 `add_eafp_japan_daimyo_loyalty` 직접 호출로 바꾸고, 기존 inverse 결과가 보존되도록 literal `VALUE`의 부호를 호출부에서 반대로 확정했다.

변환 규칙은 다음과 같다.

```text
inverse VALUE = -X  →  direct VALUE = +X
inverse VALUE = +X  →  direct VALUE = -X
```

계산식 블록을 scripted effect 인자로 넘기는 호출은 남기지 않았다. 따라서 내부의 `value`, `multiply`가 알 수 없는 effect argument로 해석되는 오류도 제거되었다.

## 7. 변수와 새 데이터베이스 키

### 7.1 새 영구 변수

이번 선택 구현에서 새로 추가한 country, state, character 영구 변수는 없다. save migration과 상태 복제용 변수를 만들지 않았다.

기존 변수 `boshin_war_happened`는 새 변수가 아니며, 실제 유신 운동 내전이 시작될 때 설정되도록 호출 위치만 정상화했다.

### 7.2 복구·추가한 키

| 종류 | 키 |
|---|---|
| JE 그룹 | `je_group_bakuhantaisei` |
| 인물 이념 | `ideology_kaikakuha`, `ideology_hoshuha`, `ideology_hitotsubashiha`, `ideology_nankiha` |
| trigger localization | `is_roju`, `is_rojushuza`, `is_tairo`, `has_bakufu_politician_mission` |
| modifier type | `state_pop_support_movement_meiji_restorationist_mult` |
| 주 modifier | `modifier_oversee_daimyo_domains_HOKUSHINETSU`, `modifier_oversee_daimyo_domains_TOKAI`, `modifier_reaffirm_daimyos_loyalty_HOKUSHINETSU`, `modifier_reaffirm_daimyos_loyalty_TOKAI` |
| 진행 막대 설명 | `bakuhantaisei_bakufu_authority_progress_bar_from_HOKUSHINETSU`, `bakuhantaisei_bakufu_authority_progress_bar_from_TOKAI` |

임무 사건 `eafp_japan.11`과 `eafp_japan.12`에도 두 주의 선택지·tooltip·character scope localization을 각각 추가했다.

## 8. 검증 결과

### 8.1 정적 검사

- 선택 구현이 수정한 활성 파일 25개: UTF-8 BOM + CRLF 확인
- 활성 `.txt` 19개: 원시 중괄호 개수 일치
- `git diff --check`: 오류 없음
- 활성 참조 0건: `STATE_CHUBU`, `INJECT:STATE_`, `c:NIP`, `eafp_movement_sonno_joi`, `add_eafp_japan_daimyo_loyalty_inverse`, 구식 `has_port`, 구식 `law_bakufu` trigger, `sr:region_japan`, `bg_gold_fields`
- 막부 JE 그룹, 4개 이념, 4개 trigger localization: 각 활성 정의 존재

### 8.2 실제 엔진 로딩

모든 DLC와 EAFP만 활성화한 뒤 `victoria3_win_console.exe -debug_mode`로 세 차례 데이터베이스·메인 메뉴 로딩을 수행했다.

| 실행 | 결과 |
|---|---|
| pass 1 | 선택 범위 주요 오류는 재발하지 않았으나 trigger localization 5회와 `law_chusei` 1회 발견 |
| pass 2 | 위 6건은 0건. 복구한 이념의 `law_bakufu` variant stance 경고 4건 발견 |
| pass 3 | 선택 범위 검색식 0건, 이념 variant 경고 0건 |

최종 로그:

- `scratch/japan_stage4_runtime_qa/selected_fix_pass3_error.log`
- `scratch/japan_stage4_runtime_qa/selected_fix_pass3_game.log`
- `scratch/japan_stage4_runtime_qa/selected_fix_pass3_debug.log`

검증을 위해 일시 변경한 `content_load.json`은 매 실행 후 백업 바이트와 동일하게 복원했고 Victoria 3 프로세스도 종료했다.

### 8.3 남은 비대상 오류

pass 3의 `error.log`에는 670줄이 남아 있다. 이번에 제외한 8번 및 일본 외 backlog가 포함되어 있으며 선택 구현의 완료 판정과 분리한다.

- 중복 localization 186건
- UTF-8 BOM 경고 19건
- unknown modifier type 12건
- invalid database object key 3건
- orphan event 12건
- 미사용 변수 경고 7건
- 인물 템플릿, GUI, asset 및 한국·몽골·중국 관련 기존 오류

이 로딩 검증은 데이터베이스와 메인 메뉴까지다. 1836 일본 선택 후 30일 진행, 보신전쟁 강제 발생, 사건 분기별 실행과 저장·재로드는 전체 P0/P1 오류가 정리된 뒤 별도 회귀 단계에서 수행해야 한다.
