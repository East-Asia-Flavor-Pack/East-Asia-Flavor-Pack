# EAFP 조선 만주 컨텐츠 상세 설명

## 1. 설계 목적

이 문서는 EAFP에 추가된 조선 만주 컨텐츠의 현재 구조를 설명한다. 컨텐츠의 목표는 조선이 전쟁 저널을 통해 만주 정복을 시작하도록 강제하는 것이 아니라, 조선이 근대화와 군제 개혁을 어느 정도 진행한 뒤 만주에 대한 선제적 정책 저널을 받고, 이후 어떤 경로로든 만주 전역을 차지했을 때 만주 경영 저널이 이어지도록 하는 것이다.

핵심 흐름은 다음과 같다.

1. 조선이 "부국강병의 길" 계열 개혁을 어느 정도 진행한다.
2. `je_eafp_manchurian_policy`가 활성화된다.
3. 이 저널의 `immediate`에서 조선은 성경, 남만주, 북만주에 클레임을 얻는다.
4. 정책 시작 이벤트 `eafp_manchuria.10`이 발생한다.
5. 조선이 성경, 남만주, 북만주 전역을 소유하면 정책 저널이 완료된다.
6. 정책 완료 이벤트 `eafp_manchuria.11`이 발생하고, 완료 효과로 `je_eafp_manchurian_management`가 열린다.
7. 만주 경영 시작 이벤트 `eafp_manchuria.12`가 발생한다.
8. 만주 경영 저널은 도시화, 조선인 정착 비율, 세금 행정 조건을 요구한다.
9. 조건이 모두 충족되면 최종 이벤트 `eafp_manchuria.20`이 발생하고 만주 주들이 조선 행정권으로 정착된다.

이 설계는 "정복 시작" 컨텐츠가 아니라 "만주를 차지한 뒤 어떻게 안정적으로 경영할 것인가"에 집중한다. 다만 이전 계획과 달리 정책 저널 자체는 만주 점령 전에 선제적으로 등장하며, 그 역할은 전쟁을 직접 시작하는 것이 아니라 만주에 대한 클레임을 부여하는 것이다.

## 2. 추가 및 수정된 파일

### 2.1 저널

파일:

- `common/journal_entries/eafp_kor_manchuria_management.txt`

정의된 저널:

- `je_eafp_manchurian_policy`
- `je_eafp_manchurian_management`

`je_eafp_manchurian_policy`는 선제적 만주 정책 저널이다. 조선이 부국강병의 길을 어느 정도 완료했을 때 등장하며, 저널이 열리는 즉시 성경, 남만주, 북만주에 대한 클레임을 부여한다.

`je_eafp_manchurian_management`는 만주 전역을 차지한 뒤 열리는 경영 저널이다. 이 저널은 위젯을 사용하지 않으며, 경영 조건을 일반 저널 상태 설명과 트리거로 처리한다.

### 2.2 트리거

파일:

- `common/scripted_triggers/eafp_kor_manchuria_triggers.txt`

주요 트리거:

- `eafp_manchuria_is_core_manchurian_state`
- `eafp_manchuria_has_manchurian_state`
- `eafp_manchuria_owns_all_manchurian_states`
- `eafp_kor_manchuria_policy_prerequisite`
- `eafp_manchuria_development_ready`
- `eafp_manchuria_settlement_ready`
- `eafp_manchuria_administration_ready`
- `eafp_manchuria_management_ready`
- `eafp_manchurian_policy_actor`

`eafp_manchuria_owns_all_manchurian_states`는 조선이 다음 세 주권역을 모두 완전 소유하는지 확인한다.

- `STATE_SHENGJING`
- `STATE_SOUTHERN_MANCHURIA`
- `STATE_NORTHERN_MANCHURIA`

`eafp_kor_manchuria_policy_prerequisite`는 만주 정책 저널의 선행 조건이다. 다음 중 하나를 만족하면 된다.

- `korean_reformation_complete_var` 보유
- `completed_je_korean_reformation_military` 보유
- `korean_reformation_var`가 존재하고 값이 2 이상

즉 부국강병의 길 전체를 완전히 끝내지 않아도, 주요 개혁을 일정 수준 이상 진행하거나 군제 개혁을 완료하면 만주 정책 저널이 뜰 수 있다.

`eafp_manchuria_development_ready`는 만주의 개발 조건이다. 기존의 별도 변수 `eafp_manchuria_development_value`를 누적 버튼 수치로 쓰지 않고, 만주 주들의 실제 `total_urbanization` 합계를 값으로 사용한다. 현재 기준값은 60 이상이다.

`eafp_manchuria_settlement_ready`는 정착 조건이다. 성경, 남만주, 북만주 각각에서 조선 문화 인구 비율이 10% 이상이어야 한다.

`eafp_manchuria_administration_ready`는 행정 조건이다. 성경, 남만주, 북만주 각각에서 `tax_capacity >= tax_capacity_usage` 조건을 만족해야 한다.

`eafp_manchuria_management_ready`는 위 세 조건을 모두 묶은 최종 완료 조건이다.

### 2.3 스크립트 값

파일:

- `common/script_values/eafp_kor_manchuria_values.txt`

현재 남은 값:

- `eafp_manchuria_development_value`

이 값은 조선이 보유한 만주 핵심 세 주의 `total_urbanization`을 합산한다. 이전의 변수형 진행도 값들은 제거되었다.

제거된 값:

- `eafp_manchuria_settlement_value`
- `eafp_manchuria_administration_value`
- `eafp_manchuria_history_value`

정착은 조선 문화 인구 비율로 직접 판정하고, 행정은 세금 역량 조건으로 직접 판정하며, 북방사/역사 논증 루트는 제거되었기 때문이다.

### 2.4 스크립트 버튼

파일:

- `common/scripted_buttons/eafp_kor_manchuria_buttons.txt`

현재 남은 버튼:

- `button_je_eafp_manchuria_settlement`
- `button_je_eafp_manchuria_expand_arable_land`

`button_je_eafp_manchuria_settlement`는 한반도 내 조선인 농민 또는 노동자 POP 일부를 만주 핵심 주 중 하나로 옮긴다. 기존처럼 `eafp_manchuria.22` 이벤트를 호출하지 않는다. 버튼 효과 안에서 직접 한반도 주를 고르고, 그 안의 조선인 POP을 고른 뒤, 만주 주 하나를 대상으로 저장하여 `move_pop`을 실행한다.

이 버튼의 한반도 대상 주는 다음과 같다.

- `STATE_SEOUL`
- `STATE_PYONGYANG`
- `STATE_BUSAN`
- `STATE_YANGHO`

`button_je_eafp_manchuria_expand_arable_land`는 만주 개척 버튼이다. 홋카이도 및 국내 개간 컨텐츠에서 쓰는 `add_arable_land` 계열 효과를 참고하여, 성경, 남만주, 북만주의 주권역에 각각 경작 가능 토지 5를 추가한다.

제거된 버튼:

- `button_je_eafp_manchuria_bureau`
- `button_je_eafp_manchuria_develop_resources`
- `button_je_eafp_manchuria_integrate_administration`
- `button_je_eafp_manchuria_common_origin`

### 2.5 스크립트 효과

파일:

- `common/scripted_effects/eafp_kor_manchuria_effects.txt`

주요 효과:

- `eafp_kor_manchuria_check_journals`
- `eafp_manchurian_policy_add_involved_countries`
- `eafp_manchurian_management_add_involved_countries`

`eafp_kor_manchuria_check_journals`는 자동 저널 점검용 효과다. 조선이 선행 조건을 만족하고 아직 만주 클레임을 받은 적이 없으면 `je_eafp_manchurian_policy`를 추가한다. 조선이 만주 전역을 이미 보유하고 있고 정책 저널을 거친 상태라면 `je_eafp_manchurian_management`를 추가한다.

이 효과는 디버그 결정에서도 호출된다. 따라서 디버그로 만주 전역을 조선에 넘긴 뒤 저널 조건을 즉시 갱신할 수 있다.

### 2.6 이벤트

파일:

- `events/eafp_kor_events/eafp_kor_manchuria_events.txt`

현재 남은 이벤트:

- `eafp_manchuria.10`
- `eafp_manchuria.11`
- `eafp_manchuria.12`
- `eafp_manchuria.20`

`eafp_manchuria.10`은 만주 정책 저널 시작 이벤트다. 조선이 부국강병 조건을 만족해 만주 정책 저널을 열고, 성경/남만주/북만주에 대한 클레임을 얻었음을 알린다.

`eafp_manchuria.11`은 만주 정책 저널 완료 이벤트다. 조선이 만주 전역을 차지했으며, 이제 단순한 명분 제기에서 실제 경영 문제로 넘어간다는 내용을 다룬다.

`eafp_manchuria.12`는 만주 경영 저널 시작 이벤트다. 만주 전역이 조선 통치 아래 들어온 뒤 도시화, 정착, 세금 행정을 통해 북방을 실질적으로 묶어야 한다는 목표를 제시한다.

`eafp_manchuria.20`은 만주 경영 저널 완료 이벤트다. 선택지는 하나만 남겼고, 효과는 다음과 같다.

- 조선에 `eafp_manchurian_administration` 국가 모디파이어 부여
- 조선이 소유한 만주 핵심 주를 편입 주로 설정
- 각 만주 핵심 주에 `eafp_manchurian_integrated_state` 주 모디파이어 부여
- 각 만주 핵심 주에 조선 문화 공동체 추가
- 만주 문화 POP 일부 충성파 추가

제거된 이벤트:

- `eafp_manchuria.22`
- `eafp_manchuria.23`
- `eafp_manchuria.25`
- `eafp_manchuria.26`
- `eafp_manchuria.27`
- `eafp_manchuria.28`
- `eafp_manchuria.29`

이 이벤트들은 기존 버튼형 변수 진행도, 자원 개발, 행정 편입 선택지, 북방사 논증 루트와 연결되어 있었으므로 새 설계에서는 제거되었다.

### 2.7 모디파이어

파일:

- `common/static_modifiers/eafp_kor_manchuria_modifiers.txt`

현재 남은 모디파이어:

- `eafp_manchurian_administration`
- `eafp_manchurian_settlement_state`
- `eafp_manchurian_integrated_state`

제거된 모디파이어:

- `eafp_manchurian_local_brokers`
- `eafp_manchurian_common_origin_research`
- `eafp_manchurian_common_origin_state`
- `eafp_manchurian_development_state`

버튼과 이벤트 구조가 단순화되면서 더 이상 참조되지 않는 모디파이어는 제거했다.

### 2.8 위젯 및 커스텀 로컬라이제이션

삭제된 파일:

- `gui/journal_entry_widgets/eafp_manchuria_policy_widgets.gui`
- `common/customizable_localization/eafp_kor_manchuria_custom_loc.txt`

만주 경영 저널은 더 이상 커스텀 위젯을 사용하지 않는다. 기존 위젯은 개발, 정착, 행정, 역사 값을 시각적으로 보여주는 구조였으나, 현재 설계에서는 역사 값이 제거되고 정착/행정 조건도 실제 주 상태 판정으로 바뀌었기 때문에 위젯을 유지하지 않는다.

### 2.9 디버그 결정

파일:

- `common/decisions/eafp_debug_decision.txt`

디버그 결정:

- `eafp_debug_own_manchuria`

이 결정은 디버그 모드에서 조선 플레이어에게 표시된다. 성경, 남만주, 북만주 전역을 조선 소유로 넘긴 뒤 `eafp_kor_manchuria_check_journals = yes`를 호출한다.

목적은 `eafp_manchuria_owns_all_manchurian_states` 조건을 빠르게 만족시켜 만주 정책 및 만주 경영 저널 흐름을 테스트하는 것이다.

### 2.10 로컬라이제이션

파일:

- `localization/korean/eafp_kor_manchuria_l_korean.yml`
- `localization/english/eafp_kor_manchuria_l_english.yml`
- `localization/simp_chinese/eafp_kor_manchuria_l_simp_chinese.yml`

로컬라이제이션은 새 구조에 맞춰 정리했다. 제거된 버튼, 이벤트, 위젯, 역사 루트 키는 삭제하고 현재 쓰이는 저널, 버튼, 이벤트, 모디파이어, 디버그 결정 키만 남겼다.

## 3. 저널 상세 흐름

### 3.1 `je_eafp_manchurian_policy`

이 저널은 만주를 차지하기 전 등장하는 정책 저널이다. 표시 조건과 가능 조건은 조선이 `eafp_kor_manchuria_policy_prerequisite`를 만족하는 것이다.

저널이 활성화되면 `immediate`에서 다음 효과가 실행된다.

- `STATE_SHENGJING`에 조선 클레임 추가
- `STATE_SOUTHERN_MANCHURIA`에 조선 클레임 추가
- `STATE_NORTHERN_MANCHURIA`에 조선 클레임 추가
- `eafp_manchurian_claims_granted_var` 설정
- 관련 국가를 저널 involved 국가로 갱신
- `eafp_manchuria.10` 시작 이벤트 발생

완료 조건은 조선이 만주 핵심 세 주권역을 모두 완전 소유하는 것이다. 완료되면 만주 경영 저널이 추가되고 `eafp_manchuria.11` 완료 이벤트가 발생한다.

### 3.2 `je_eafp_manchurian_management`

이 저널은 만주 전역을 보유한 조선에게 열리는 경영 저널이다. 두 개의 버튼만 제공한다.

저널이 활성화되면 `immediate`에서 involved 국가를 갱신하고 `eafp_manchuria.12` 시작 이벤트를 발생시킨다.

- 조선인 이주 장려
- 만주 개척

완료 조건은 `eafp_manchuria_management_ready`다. 이 조건은 다음 세 조건을 모두 요구한다.

- 만주 총 도시화 합계 60 이상
- 성경, 남만주, 북만주 각각 조선 문화 인구 비율 10% 이상
- 성경, 남만주, 북만주 각각 세금 역량이 세금 역량 사용량 이상

완료되면 `eafp_manchuria.20` 이벤트가 발생한다.

## 4. 제거된 기존 구조

새 계획에 따라 다음 구조는 제거되었다.

1. 위젯 기반 만주 경영 현황판
2. 버튼으로 변수 값을 올리는 개발/정착/행정/역사 진행도
3. 북방사 논증 또는 공통 기원 연구 루트
4. 만주인을 조선의 주류 문화로 받는 선택지
5. 만주 자원 개발 이벤트 버튼
6. 만주 전담 관청 이벤트 버튼
7. 행정 편입 별도 버튼
8. `eafp_manchuria.22`, `.23`, `.25`, `.26`, `.27`, `.28`, `.29`

현재 구조는 실제 주 상태와 POP 비율을 더 많이 본다. 따라서 플레이어는 버튼을 반복해서 숫자를 올리는 방식보다, 만주에 도시화를 만들고 조선인 정착을 늘리며 세금 역량을 확보해야 한다.

## 5. 테스트 포인트

테스트 시 확인할 사항은 다음과 같다.

1. 조선이 부국강병 관련 선행 조건을 만족하면 `je_eafp_manchurian_policy`가 뜨는가.
2. 정책 저널이 열릴 때 성경, 남만주, 북만주에 조선 클레임이 생기는가.
3. 조선이 만주 전역을 소유하면 정책 저널이 완료되고 `je_eafp_manchurian_management`가 열리는가.
4. 위젯 없이 만주 경영 저널이 정상 표시되는가.
5. `button_je_eafp_manchuria_settlement`가 한반도 내 조선인 POP을 만주로 옮기는가.
6. `button_je_eafp_manchuria_expand_arable_land`가 성경, 남만주, 북만주의 경작 가능 토지를 늘리는가.
7. 각 만주 주의 조선 문화 인구 비율이 10% 이상일 때 정착 조건이 충족되는가.
8. 각 만주 주의 `tax_capacity >= tax_capacity_usage` 조건이 충족될 때 행정 조건이 충족되는가.
9. 세 만주 주의 `total_urbanization` 합계가 60 이상일 때 개발 조건이 충족되는가.
10. 모든 조건 충족 후 `eafp_manchuria.20`이 정상 발생하는가.

디버그 모드에서는 `eafp_debug_own_manchuria` 결정을 사용해 만주 전역 소유 조건을 빠르게 만들 수 있다.
