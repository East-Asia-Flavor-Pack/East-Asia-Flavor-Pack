# Vanilla 1.15.0 → 1.15.2 호환 작업 정리

- 비교 대상: `Vic3-vanilla` 커밋 `1cc4f518`(1.15.0) → `17bf4985`(1.15.2), 변경 파일 770개
- 비교 방법
  - 경로가 같아 모드가 바닐라 파일을 통째로 덮어쓰는 경우
  - `REPLACE:` / `INJECT:` 또는 같은 키로 재정의한 최상위 오브젝트 중 바닐라에서 내용이 바뀐 것
  - 바닐라에서 삭제된 키를 모드가 참조하는지
  - 로컬라이제이션(en/ko/zh): 모드가 덮어쓰는 키 중 바닐라에서 바뀐 것 → **0건**
  - GUI: 삭제된 type/template을 모드가 쓰는지 → **0건**
- `metadata.json`의 `supported_game_version`은 이미 `1.15.*`라서 수정할 필요가 없음

---

## A. 반드시 반영해야 하는 것 (모드가 바닐라 변경을 덮어서 지워버림)

> **적용 완료**: A1~A4 모두 반영함. A3의 `possible` 툴팁 구조는 모드 자체 로직을 유지하기 위해 적용하지 않음.
> 참고: 모드 버튼의 incident는 `show_as_tooltip`로 표시만 되고, `russo_chinese` 이벤트에서도 실제로 적용되지 않음(기존 동작).

### A1. `common/history/countries/chi - china.txt`, `jap - japan.txt` (경로 동일 → 바닐라 파일을 통째로 대체)

바닐라 1.15.2에서 시작 관세가 추가됐는데, 모드 파일이 덮어쓰고 있어 적용되지 않음.

- **CHI** (`set_import_tariff_level = { goods = g:opium ... }` 바로 아래)
  ```
  set_import_tariff_level = {
      goods = g:merchant_marine
      level = low_subventions
  }
  ```
- **JAP** (`set_tax_level = medium` 바로 아래)
  ```
  set_import_tariff_level = {
      goods = g:iron
      level = max_subventions
  }
  set_import_tariff_level = {
      goods = g:small_arms
      level = max_subventions
  }
  ```
  - 쇄국/막부 관련 무역 설정과 충돌하지 않는지 확인 필요(예: `law_canton_system` REPLACE, 사코쿠 무역 제한).

### A2. `REPLACE:country_is_valid_qing_treaty_partner`
파일: `common/scripted_triggers/eafp_russo_chinese_triggers.txt`

바닐라 변경 사항:
1. 문화 조건을 `custom_tooltip = { text = qing_treaty_partner_culture_tt ... }`로 감쌌음(툴팁만 바뀜).
2. **로직 수정**: `war_with_china_not_russia_tt` 조건
   ```
   # 1.15.0 (모드 현재)
   any_enemy_in_war = { NOT = { c:RUS ?= this } }
   # 1.15.2
   is_at_war = yes
   NOT = { any_enemy_in_war = { c:RUS ?= this } }
   ```
   예전 코드는 러시아와 다른 나라를 동시에 상대로 싸우는 중에도 참이 됐음. 1.15.2에서는 러시아와 전쟁 중이면 거짓.

→ 모드 쪽 수정(`je_warlord_china` / `china_explosion_point_75_tt` 분기)은 그대로 두고, 위 두 가지만 옮기면 됨. `qing_treaty_partner_culture_tt` 로컬 키는 바닐라에 있음.

### A3. `common/scripted_buttons/eafp_04_russia_buttons.txt` (REPLACE 3개)
`je_the_eastern_border_treaty_of_beijing`, `je_the_eastern_border_russia_chuguchak_protocol`, `je_the_eastern_border_treaty_of_aigun`

바닐라 변경 사항:
| 항목 | 1.15.0 | 1.15.2 |
|---|---|---|
| `possible`의 청 영토 조건 | `any_country_in_qing_empire = { ... country_is_valid_qing_treaty_partner = yes }` | `custom_tooltip = { text = qing_country_holds_{outer_manchuria/central_asia/amur}_tt  any_country_in_qing_empire = { ... save_temporary_scope_as = qing_treaty_partner } }` 아래 `scope:qing_treaty_partner ?= { country_is_valid_qing_treaty_partner = yes }` |
| `effect` 안의 `scope:donor_scope = {` | 그대로 | `scope:donor_scope ?= {` (null 스코프 오류 방지) |
| incident `value` | 10 / 15 / 10 | **5 / 5 / 5** |

→ 권장 작업
- `scope:donor_scope = {` → `?=`로 바꾸기(6군데). 모드 버전에서도 `random_country_in_qing_empire`가 아무것도 고르지 못하면 똑같이 오류가 남.
- incident 툴팁 값(모드는 `show_as_tooltip`로 표시만 함)을 5로 맞추기. 실제 incident를 어디서 적용하는지도 함께 확인.
- `possible` 툴팁 구조는 선택. 모드는 자체 `eafp_qing_treaty_partner` 로직을 쓰므로 그대로 둬도 동작함. 다만 바닐라처럼 `custom_tooltip`으로 감싸면 UI가 깔끔해짐(로컬 키는 바닐라에 있음).

### A4. `REPLACE:ai_strategy_maintain_mandate_of_heaven`
파일: `common/ai_strategies/eafp_political_strategies.txt`

바닐라에서 `max_regressiveness`에 다음이 추가됨:
```
if = {
    limit = { has_law_or_variant = law_type:law_factory_councils }
    add = 93
}
else_if = {
    limit = { has_revolutionary_socialist_laws = yes }
    add = 48
}
```
→ 결정: 서양화 add 분기 **뒤**에 넣고, 서양화 군사·정부개혁의 `multiply = 0`은 `else_if`로 체인에 연결함.
- 근거 1: 비슷한 근대화 전략인 바닐라 `ai_strategy_meiji_restoration`은 개혁 진행 여부와 관계없이 공장평의회 +70을 항상 적용함. 근대화 중이라도 혁명적 사회주의 법은 되돌릴 수 있게 하려는 의도.
- 근거 2: 바닐라 1.15.2의 첫 정치 전략은 `if = { 혁명적 법 }`, `if = { has_enactment_je_or_law_commitment multiply = 2 }`였던 것을 `else_if` 체인으로 바꿈. 혁명적 법이 있으면 개혁·약속 쪽 배수를 건너뛰게 한 것.
- 앞에 넣으면 `multiply = 0`이 +93을 지워서, 서양화 개혁 중에는 공장평의회를 폐지하지 않게 됨 → 바닐라 의도와 반대.

같은 파일의 `ai_strategy_meiji_restoration_kor`(바닐라 `ai_strategy_meiji_restoration` 복사본으로 보임)도, 바닐라 meiji_restoration에 추가된 다음 블록을 같이 넣는 것을 권장:
```
max_regressiveness = {
    value = 25
    if = { limit = { has_law_or_variant = law_type:law_factory_councils } add = 70 }
    else_if = { limit = { has_revolutionary_socialist_laws = yes } add = 25 }
}
```

---

## B. 자동으로 반영됨 (조치 불필요, 확인만)

| 모드 정의 | 바닐라 변경 | 상태 |
|---|---|---|
| `INJECT:*_party` (eafp_parties.txt) | 지배정당(SPS) 수정: `available_for_interest_group`, 점수에 `amendment_*_party_dominance` 추가 | 모드는 `name` 분기만 INJECT하므로 바닐라 변경이 그대로 유지됨 |
| ~~`INJECT:ai_strategy_default`~~ | 종속국 가치 계산, 보조금(조선소 추가), 라디오·전화·석유 수요 stance 등 | **판단 오류였음.** INJECT는 같은 이름의 필드를 통째로 바꾸므로 `recklessness` 기본값 1, `diplomatic_play_boldness` 기본값 50 등 바닐라 내용이 모든 나라에서 사라졌음. 파일을 지우고 군벌 몫은 `REPLACE:ai_strategy_unify_china`(eafp_diplomatic_strategies.txt, 바닐라 전체 사본이므로 바닐라 갱신 때 맞춰야 함), 청의 1차 아편전쟁 보정은 `ai_strategy_maintain_mandate_of_heaven`으로 옮김. 영국 쪽 보정과 조계 요구 외교전 AI 점수는 삭제(조계 AI는 `eafp_grant_concession` 조약 조항의 ai 블록만 씀) |
| `INJECT:da_decrease_autonomy` | `possible`에 `modifier:country_cannot_decrease_autonomy_bool ?= no` 추가 | `ai` 블록만 INJECT하므로 유지됨 |
| `00_code_on_actions_definition.txt`의 `on_character_death`, `on_new_ruler`, `on_law_checkpoint_advance/debate` | effect/events/on_actions 추가 | 모드는 `on_actions` 목록만 추가해서 병합됨 |
| 회사(eafp_companies_*) | 바닐라는 모든 회사 `possible`에 `any_scope_state = { state_region = ... is_incorporated = yes }` 추가 | 모드 회사는 이미 같은 패턴이라 수정할 필요 없음 |
| `history/buildings` (chi/jap/kor_building) | 바닐라 동아시아 건물 수치 변경 | 모드 파일은 MCH/MGL/XIN, 조선, 일본 일부 추가만 하므로 충돌하지 않음 |
| `history/pops` | 바닐라는 시베리아 주 순서만 바뀜(내용 변화 0) | 영향 없음 |
| `map_data/state_regions` | 구리 광산 상한 상향(쓰촨·윈난 4→10·장시·남안후이·홋카이도·간사이·규슈 등) | 모드는 state_regions를 덮어쓰지 않으므로 자동 반영됨 |

바닐라에서 **삭제된 키**(`on_diplo_play_subject_released*`, `diplo_play_subject_released*_notification`, `calculate_communism_progress`, `calculate_populism_progress`, `installed_regime`, `congress_poland.1000`)와 **삭제된 define**(`WAR_GOAL_REGIME_CHANGE_*`, `MANPOWER_RATIO_REQUIRED_TO_CLEAR_DEFEATED_ADMIRALS`, `COMPANY_TYPE_FORMABLE_MULTIPLE_FREE_SLOTS_FACTOR`), PM 필드 `low_pop_method`(→ `scoring_override`)는 모드에서 참조하는 곳이 **없음**.

---

## C. 밸런스·동작 검토 (오류는 아니지만 모드 콘텐츠에 영향)

### C1. 청 시작 건물 재배치 (`11_east_asia.txt`)
- **무기 공장**: 베이징 국영 4레벨 삭제 → 산둥 1, 즈리 1 (합계 4 → 2)
- 유리공장: 난징 10→3, 산둥 10→4, 장쑤 5→2, 구이저우 8→4, 즈리 6→0. 대신 여러 주에 2~4레벨씩 새로 분산됨
- 광둥: 무역센터 45→32, 비단 20→36, 차 10→21 / 푸젠·광시·사오저우 비단 감소, 장쑤·저장 차 15→12

모드에서 영향을 받는 곳:
- `chinese_westernization.305`(부임지 옮기기): `han_homelands` 안에 **국가가 100% 소유한 level ≥ 4** 산업 건물이 있어야 함. 1.15.0에서는 베이징 국영 무기공장 4레벨로 시작부터 충족됐지만, 1.15.2에서는 충족되지 않을 수 있음 → 발동 시점이 늦어지는지 확인.
- `eafp_chinese_westernization.txt`: 무기공장 `count >= 5`, `level >= 5` 조건이 있음. 시작 무기공장이 2개(각 1레벨)로 줄어서 난이도가 올라감.
- 조계(concessions) 산업 생성 로직(`eafp_concessions_effects.txt`)은 건물 타입을 동적으로 검사하므로 오류는 없음. 다만 광둥 무역센터 감소가 아편전쟁·조계 수익 밸런스에 영향을 줄 수 있음.

### C2. 일본 시작 건물
- 벌목장 증가(간사이 2→4, 간토 3→5, 교토 1→3 + PM `pm_saw_mills`, 시코쿠 1→3, 도카이 3→6)
- **규슈 항구 3→1**, 호쿠신에쓰 유리공장 1→0
- 모드 `jap_building.txt`(간토·규슈 섬유공장 추가)와 충돌은 없음. 다만 규슈 항구 감소가 나가사키·데지마 관련 사코쿠/개항 이벤트(`000_eafp_japan_overrides.txt`의 `building_port` 생성 부분)와 맞는지 확인.

### C3. 조약항 상속 이벤트 (`treaty_port_inheritance_events.1`)
- 거부(Renege) 시 "외국 세력이 항구 프로빈스를 일반 영토로 유지"하는 것으로 의미가 바뀜. 관계 -50과 부정적 촉매가 추가됨.
- 군벌 중국 → 재통일 과정에서 조약항이 있는 나라를 흡수할 때 이 이벤트가 뜰 수 있음. 모드 조계 시스템(`concessions_code_on_actions.txt`)과 함께 동작하는지 테스트.

### C4. 정권교체(regime change) 시스템 개편
- `law_groups`의 `affected_by_regime_change = yes` → `regime_change_min_progressiveness_difference = N`
- `da_power_bloc_force_regime_change`가 `can_regime_change`와 `regime_change_target_allowed_trigger`를 쓰도록 바뀌고 `installed_regime` 모디파이어가 삭제됨
- 모드는 law_group을 정의하지 않아서 오류는 없음. 다만 `identity_eafp_mandate_of_heaven` 블록에서 정권교체가 어떻게 동작하는지는 인게임에서 확인.

### C5. 일당제(`law_single_party_state`) 개편
- 조건이 "정부 내 정당 IG가 있고 반란 구성원이 없을 것"으로 바뀜. 효과는 `var:sps_dominant_party_ig_var`를 먼저 쓰고, 없으면 기존처럼 `ruler.interest_group`을 씀.
- `warlord_china_events.txt:70`의 `activate_law = law_type:law_single_party_state`는 대체 경로가 있어서 기존처럼 동작함. `eafp_chinese_westernization_events.txt:3376`의 `is_enacting_law` 체크도 영향 없음. 새 이벤트 `single_party_state.8/9`(입법 중 취소)가 중국 군벌 쪽에서 뜰 수 있으니 확인.

---

## D. 선택: 새 기능 활용

- `country_cannot_decrease_autonomy_bool` 모디파이어: 조공국·군사본부(`subject_type_military_headquarters_china`)의 자치권 감소를 막는 데 쓸 수 있음. 지금 모드는 `da_decrease_autonomy`에 AI 가중치 0만 INJECT하고 있음.
- `subject_join_initiator_trigger` (diplomatic play): 종속국이 개시국 편에 참여할 수 있는지 제한함. `REPLACE:dp_unify_china`에서 군벌 종속국 참여를 제어하는 데 쓸 수 있음.
- `scoring_override` (PM): AI가 특정 PM을 강제로 고르게 할 수 있음.

---

## E. 이번 비교 중 발견한 기존 버그 (1.15.2와 무관)

- ~~`common/parties/eafp_parties.txt:140` `INJECT:social_democrat_party`~~ → `INJECT:socialist_party`로 **수정 완료**. (바닐라 1.15.0과 1.15.2 모두 키 이름이 `socialist_party`임 → `INJECT:socialist_party`로 고쳐야 조선 사회당 이름이 적용됨(지금은 INJECT 대상이 없어 오류 로그가 남음).)
