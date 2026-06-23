# 조선-청 전쟁 저널 설계안

## 범위

이 설계안은 조선(`KOR`)과 청(`CHI`) 사이에 전쟁이 발생했을 때 쓰이는 실제 전쟁 저널 1종을 다룬다.

- `je_eafp_joseon_qing_war`

껍데기 저널은 만들지 않는다. 전쟁 전 안내용 저널도 만들지 않고, 실제 저널이 `possible` 조건을 통해 전쟁 중에만 활성화되도록 설계한다.

## 설계 목표

- 조선과 청의 전쟁을 사대 질서의 붕괴 또는 재편으로 표현한다.
- `add_journal_entry`를 쓰지 않고, 저널의 `possible` 조건으로 활성화한다.
- 진행바는 추가하지 않는다.
- `status_desc`는 추가하지 않는다.
- 전쟁 중 월간 펄스로 반복 발생할 수 있는 사건들을 배치한다.
- 승전/패전 후에는 정치운동 기반 급진파·충성파 변화 modifier로 전후 정국을 표현한다.

## 저널 구조

### `je_eafp_joseon_qing_war`

실제 전쟁 저널. 조선이 청과 전쟁 중일 때 활성화된다.

권장 배치:

- 파일: `common/journal_entries/eafp_joseon_qing_war.txt`
- 그룹: `je_group_crises`
- 아이콘: `gfx/interface/icons/event_icons/event_military.dds`
- 진행바: 없음
- scripted button: 없음
- status desc: 없음
- 활성화 방식: `possible`

`is_shown_when_inactive`는 이 저널이 조선에게 후보로 보일 수 있게 하는 최소 관문으로만 둔다. 실제 활성화 판정은 `possible`에만 둔다.

의사코드:

```txt
je_eafp_joseon_qing_war = {
    icon = "gfx/interface/icons/event_icons/event_military.dds"
    group = je_group_crises

    is_shown_when_inactive = {
        c:KOR ?= THIS
        exists = c:CHI
    }

    possible = {
        c:KOR ?= THIS
        exists = c:CHI
        has_war_with = c:CHI
    }

    immediate = {
        c:CHI = { save_scope_as = qing_enemy }
        trigger_event = { id = eafp_joseon_qing_war_events.1 popup = yes }
    }

    complete = {
        exists = c:CHI
        NOT = { has_war_with = c:CHI }
        is_subject = no
    }

    fail = {
        OR = {
            is_country_alive = no
            AND = {
                exists = c:CHI
                NOT = { has_war_with = c:CHI }
                is_subject_of = c:CHI
            }
            AND = {
                exists = c:CHI
                NOT = { has_war_with = c:CHI }
                has_truce_with = c:CHI
                # 패배 판정 보조 조건은 실제 구현 때 전쟁 목표/종속 여부/전쟁 지지도 기반으로 보강
            }
        }
    }

    on_monthly_pulse = {
        random_events = {
            100 = 0
            10 = eafp_joseon_qing_war_events.10
            10 = eafp_joseon_qing_war_events.11
            10 = eafp_joseon_qing_war_events.12
            10 = eafp_joseon_qing_war_events.13
            10 = eafp_joseon_qing_war_events.14
            10 = eafp_joseon_qing_war_events.15
            10 = eafp_joseon_qing_war_events.16
        }
    }
}
```

주의: 이 저널은 `add_journal_entry`로 열지 않는다. `common/on_actions/korea_code_on_actions.txt`에 월간 감지 블록을 추가하지 않는다.

## 활성화 방식

기존 계획의 월간 펄스 감지 및 `add_journal_entry` 방식은 폐기한다.

새 방식:

- `is_shown_when_inactive`: 조선과 청이 존재하는지만 확인
- `possible`: 조선이 청과 전쟁 중인지 확인
- 전쟁이 시작되면 `possible`이 참이 되어 저널이 활성화
- 전쟁이 끝나면 `complete` 또는 `fail`로 전후 처리

권장 `possible` 조건:

- `c:KOR ?= THIS`
- `exists = c:CHI`
- `has_war_with = c:CHI`
- 선택 조건: 청이 중국 중앙정부 역할을 유지 중이거나, 조선이 청의 종속/조공 질서에서 벗어나는 상황

## 완료/실패 판정

### 완료

전쟁이 끝났고 조선이 독립적 지위를 유지했을 때 완료한다.

권장 완료 조건:

- `exists = c:CHI`
- `NOT = { has_war_with = c:CHI }`
- `is_subject = no`
- 선택 보강: 청과의 종속 관계가 없음, 조선 수도가 조선 통제하에 있음, 청이 조선에 강제 조약/종속 전쟁목표를 관철하지 못함

완료 효과:

- 완료 이벤트 발동: `eafp_joseon_qing_war_events.2`
- 변수 세팅: `completed_je_eafp_joseon_qing_war`
- 청과 관계 하락 또는 재정렬
- 승전 modifier 부여

### 실패

전쟁이 끝났고 조선이 청에게 굴복했거나, 종속/재종속 상태가 되었을 때 실패한다.

권장 실패 조건:

- 조선이 더 이상 존재하지 않음
- `NOT = { has_war_with = c:CHI }` AND `is_subject_of = c:CHI`
- 선택 보강: 청의 전쟁목표가 관철됨, 조선 수도가 장기간 점령됨, 조선이 전쟁 중 파산함

실패 효과:

- 실패 이벤트 발동: `eafp_joseon_qing_war_events.3`
- 변수 세팅: `failed_je_eafp_joseon_qing_war`
- 패전 modifier 부여
- 청과의 관계/종속 질서 강화

## 전쟁 중 반복 이벤트

전쟁 중 사건은 `on_monthly_pulse`의 `random_events`로 운용한다. 각 이벤트는 조건에 맞으면 여러 번 뜰 수 있게 하되, 너무 자주 뜨지 않도록 `chance_of_no_event` 또는 높은 `0` weight를 둔다.

### `eafp_joseon_qing_war_events.10` 의주의 보급로

전선 보급과 압록강 방어를 다룬다.

발동 조건:

- 조선과 청이 전쟁 중
- 조선이 디폴트 상태가 아님
- 북부/서북부 전선 관련 주가 조선 소유 또는 조선 통제

선택지:

- 군량을 집중한다: 군대 보급/방어 modifier, 대신 비용 또는 급진파 증가
- 지방에 부담을 넘긴다: 비용 감소, 대신 해당 주 급진파 증가
- 조정의 재정을 아낀다: 단기 안정, 대신 전쟁 수행 관련 불리한 modifier

### `eafp_joseon_qing_war_events.11` 피난민과 군량

전쟁 피해가 민생과 지방 행정에 미치는 영향을 다룬다.

발동 조건:

- 조선과 청이 전쟁 중
- 조선 주 중 하나가 점령, 황폐화, 급진파 증가 조건을 만족

선택지:

- 구휼미를 푼다: 해당 주 충성파 증가, 재정 부담
- 군량을 우선한다: 군사 modifier, 해당 주 급진파 증가
- 향촌 자치를 활용한다: 지주/보수 세력 영향 증가, 급진파 소폭 감소

### `eafp_joseon_qing_war_events.12` 의병과 상소

전쟁이 민족적 동원과 반청 정치운동을 자극하는 사건.

발동 조건:

- 조선과 청이 전쟁 중
- 급진파 또는 정치운동 지지가 일정 이상

선택지:

- 의병을 장려한다: 군사/방어 보너스, 정치운동 radicalism 증가 가능
- 상소를 수용한다: 충성파 증가, 보수 운동 pop attraction 증가
- 무장을 통제한다: 급진파 증가를 억제하지만 보수/민중 운동 불만 증가

### `eafp_joseon_qing_war_events.13` 동장군

혹한이 전선을 덮치며 보급과 병력 손실을 압박하는 사건.

발동 조건:

- 조선과 청이 전쟁 중
- 겨울철이거나 북부/서북부/만주 전선에서 교전 중
- 조선이 충분한 군수품을 확보하지 못했거나 전선 보급이 불안정하면 가중

선택지:

- 방한 물자를 우선 보급한다: 재정 부담, 병력 손실/사기 악화 완화
- 현지 징발을 허용한다: 보급 보너스, 해당 주 급진파 증가
- 공세를 늦춘다: 전쟁 수행 modifier 약화, 국내 급진파 증가 억제

### `eafp_joseon_qing_war_events.14` 포탄 속의 모래

방산비리와 부실 군수품 납품이 드러나는 사건.

발동 조건:

- 조선과 청이 전쟁 중
- 조선이 군수품 관련 건물 또는 무기 생산 기반을 보유
- 부패/낮은 행정력/재정 압박이 있으면 가중

선택지:

- 관련자를 엄벌한다: 권위 또는 관료제 비용, 충성파 증가와 부패 완화
- 급한 대로 덮는다: 단기 비용 감소, 군사 불리 modifier와 급진파 증가
- 군수 조달을 개편한다: 장기적 군수 보너스, 즉시 재정 부담

### `eafp_joseon_qing_war_events.15` 패장의 자결

패전한 지휘관이 책임을 지고 자결하거나, 조정이 책임 소재를 둘러싸고 흔들리는 사건.

발동 조건:

- 조선과 청이 전쟁 중
- 조선 측 장군이 존재
- 최근 전선 후퇴, 주 점령, 낮은 전쟁 지지도 같은 불리한 상황이면 가중

선택지:

- 충절을 기린다: 보수/왕당 계열 안정, 군부 사기 회복
- 책임을 물어 군제를 다잡는다: 군사 개혁 명분, 장군/군부 불만
- 패전을 덮고 넘어간다: 단기 안정, 정치운동 radicalism 증가

### `eafp_joseon_qing_war_events.16` 대화재

전쟁 중 포격, 방화, 피난민 혼란으로 도시 또는 보급 거점에 큰 화재가 발생하는 사건.

발동 조건:

- 조선과 청이 전쟁 중
- 조선의 도시화된 주, 항구, 수도, 전선 인접 주 중 하나가 위협받음
- 점령 또는 높은 황폐화가 있으면 가중

선택지:

- 구호와 진화를 우선한다: 해당 주 충성파 증가, 재정 부담
- 군수창을 먼저 지킨다: 군사 보급 보너스, 민간 급진파 증가
- 책임자를 처벌한다: 권위 소모, 정치운동 radicalism 억제

## 전후 modifier 설계

전후 효과는 즉발 `add_radicals`/`add_loyalists`만으로 처리하지 않고, 일정 기간 유지되는 modifier를 함께 사용한다. 기존 모드에서 쓰는 다음 modifier 계열을 활용한다.

- `state_radicals_from_political_movements_mult`
- `state_loyalists_from_political_movements_mult`
- `political_movement_radicalism_add`
- `political_movement_pop_attraction_mult`

### 승전 modifier

#### `eafp_modifier_joseon_qing_war_victory_unity`

조선이 독립을 지켜냈을 때 전국에 부여하는 단일 승전 modifier. 개혁파와 보수파를 별도 modifier로 나누지 않고, 전후 단결 효과를 하나로 통합한다.

효과 방향:

- `state_radicals_from_political_movements_mult = -0.15`
- `state_loyalists_from_political_movements_mult = 0.20`
- `political_movement_radicalism_add = -0.05`
- `political_movement_pop_attraction_mult = 0.05`
- 위신 또는 정통성 관련 보너스 소폭

기간:

- 5년

의도:

- 승전이 정치운동을 완전히 없애지는 않지만, 각 운동의 급진화를 누그러뜨리고 국가에 대한 충성파를 늘린다.

### 패전 modifier

#### `eafp_modifier_joseon_qing_war_defeat_humiliation`

패전 또는 재종속 시 전국에 부여하는 단일 패전 modifier. 개혁파와 보수파를 별도 modifier로 나누지 않고, 패전이 모든 정치운동을 불안정하게 만드는 효과로 통합한다.

효과 방향:

- `state_radicals_from_political_movements_mult = 0.25`
- `state_loyalists_from_political_movements_mult = -0.15`
- `political_movement_radicalism_add = 0.10`
- `political_movement_pop_attraction_mult = 0.10`
- 정통성/위신 관련 페널티

기간:

- 5년

의도:

- 패전이 "구질서의 무능", "외세에 대한 굴욕", "조정의 책임"으로 동시에 해석되며 정치운동 전반의 급진화를 부른다.

## 이벤트 설계

### `eafp_joseon_qing_war_events.1` 전쟁 발발

저널 `immediate`에서 발동한다.

효과:

- 청을 `qing_enemy`로 저장
- 전쟁의 정치적 의미를 안내
- 선택지 없이 확인용으로 처리하거나, 소규모 정통성/위신 변화 선택지를 둔다.

### `eafp_joseon_qing_war_events.2` 승리/독립 질서

전쟁 종료 후 조선이 독립을 유지했을 때 발동한다.

효과:

- `completed_je_eafp_joseon_qing_war` 변수 세팅
- `eafp_modifier_joseon_qing_war_victory_unity` 부여
- 즉발 충성파 소폭 추가 가능

### `eafp_joseon_qing_war_events.3` 패배/재종속

조선이 청에게 굴복했을 때 발동한다.

효과:

- `failed_je_eafp_joseon_qing_war` 변수 세팅
- `eafp_modifier_joseon_qing_war_defeat_humiliation` 부여
- 즉발 급진파 소폭 추가 가능

## 파일 작업 목록

1. `common/journal_entries/eafp_joseon_qing_war.txt`
   - `possible` 기반 실제 전쟁 저널 추가
   - 진행바와 `status_desc`는 추가하지 않음

2. `events/eafp_kor_events/eafp_joseon_qing_war_events.txt`
   - 발발, 승리, 패배 이벤트 추가
   - 전쟁 중 반복 이벤트 7개 추가

3. `common/static_modifiers/eafp_korea_rework_modi.txt` 또는 신규 modifier 파일
   - 승전/패전 정치운동 modifier 추가

4. `localization/korean/eafp_joseon_qing_war_l_korean.yml`
   - 한국어 loc 추가

5. `localization/english/eafp_joseon_qing_war_l_english.yml`
   - 영어 loc 추가

6. `localization/simp_chinese/eafp_joseon_qing_war_l_simp_chinese.yml`
   - 중국어 간체 loc 추가

## 로컬라이제이션 키 초안

저널:

- `je_eafp_joseon_qing_war`
- `je_eafp_joseon_qing_war_reason`
- `je_eafp_joseon_qing_war_goal`

이벤트:

- `eafp_joseon_qing_war_events.1.t`
- `eafp_joseon_qing_war_events.1.d`
- `eafp_joseon_qing_war_events.1.f`
- `eafp_joseon_qing_war_events.1.a`
- `eafp_joseon_qing_war_events.2.t`
- `eafp_joseon_qing_war_events.2.d`
- `eafp_joseon_qing_war_events.2.f`
- `eafp_joseon_qing_war_events.2.a`
- `eafp_joseon_qing_war_events.3.t`
- `eafp_joseon_qing_war_events.3.d`
- `eafp_joseon_qing_war_events.3.f`
- `eafp_joseon_qing_war_events.3.a`
- `eafp_joseon_qing_war_events.10.t`
- `eafp_joseon_qing_war_events.10.d`
- `eafp_joseon_qing_war_events.10.f`
- `eafp_joseon_qing_war_events.10.a`
- `eafp_joseon_qing_war_events.10.b`
- `eafp_joseon_qing_war_events.10.c`
- `eafp_joseon_qing_war_events.11.t`
- `eafp_joseon_qing_war_events.12.t`
- `eafp_joseon_qing_war_events.13.t`
- `eafp_joseon_qing_war_events.14.t`
- `eafp_joseon_qing_war_events.15.t`
- `eafp_joseon_qing_war_events.16.t`

modifier:

- `eafp_modifier_joseon_qing_war_victory_unity`
- `eafp_modifier_joseon_qing_war_defeat_humiliation`

## 구현 시 주의점

- `add_journal_entry`를 사용하지 않는다.
- 진행바를 추가하지 않는다.
- `status_desc`를 추가하지 않는다.
- 전쟁 중 반복 이벤트는 너무 자주 뜨지 않도록 `random_events`의 `0` weight를 높게 둔다.
- 반복 이벤트가 특정 상황에서만 의미가 있다면 이벤트 trigger에서 전선/점령/정치운동 조건을 걸어 자연스럽게 걸러낸다.
- 전후 급진파·충성파 처리는 즉발 효과와 modifier를 섞되, 핵심은 modifier가 담당하게 한다.
- 향후 조선이 대한제국으로 전환된 뒤에도 같은 태그 `KOR`를 유지한다면 그대로 동작한다. 태그 변경 가능성이 있다면 `country_has_primary_culture = cu:korean` 보조 조건을 추가한다.

## 추천 구현 순서

1. `possible` 기반으로 전쟁 중 저널이 활성화되는지 확인한다.
2. 발발/승리/패배 이벤트를 붙인다.
3. 전쟁 중 반복 이벤트를 월간 펄스에 연결한다.
4. 승전/패전 정치운동 modifier를 추가한다.
5. loc를 정리한다.
