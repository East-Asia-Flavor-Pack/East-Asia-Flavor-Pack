# 중국 조계지 건물·기업 개편 계획과 구현 명세

수정일: 2026-11-08. 사용자 지시에 따라 게임 검증 없이 코드 연결을 진행했다. 조약 지급 경로는 전용 기업 소유 조계지 +5다. 아래는 현재 코드의 동작 명세다. 지원 경로가 확인되지 않은 부분은 11절에 구분한다. 설치 파일·생성 문서 조사 근거는 [엔진 조사 기록](china_concessions_engine_audit.md)에 보존한다.

2026-11-10 변경: 중국 소유국 국고에서 조계 보유국 국고로 매주 돈을 직접 옮기던 이전금(`concession_payment`/`concession_paid` modifier)을 정의·번역·구 세이브 정리까지 모두 삭제했다. 보유국 수익은 조계지 무역과 조계회사 배당뿐이다. 7절 참조.

2026-11-11 변경(증가 = 건물 유지·보유국 지분 덮어쓰기): 아래 내용이 4·5절의 「기존 건물에 `add_ownership` 추가」 서술보다 우선한다. 기준 코드는 사용자가 되돌린 `6997c6dc` 설계이며, 그 위에 이 변경만 얹었다. 같은 날 한때 쓰던 「스냅샷 → `remove_building` → 재생성」 방식은 사용자 지시로 폐기했다.
- `eafp_concession_add_company_level = { LEVELS }`(저널 +5 버튼·AI 확장·조약 +5 지급 공용)는 `remove_building`을 쓰지 않는다. 사용자 확인에 따라 `create_building`의 레벨은 기존 건물에 더해지지 않고 그 국가 지분을 덮어쓰므로, 보유국 지분을 새 총량으로 한 번에 덮어쓴다.
  1. 주 변수 맵 `eafp_concession_rebuild_map`을 비우고 키 = 보유국 스코프 → 현재 보유국 소유 레벨(`levels_owned_by_country` 32회 이진 탐색, 공용 효과 `eafp_concession_measure_country_levels`)을 저장한다. 새 보유국·새 건물이면 항목이 없다(0).
  2. 그 항목에 LEVELS를 더하고 새 총량을 `scope:concession_expected_levels`로 남긴다.
  3. `eafp_concession_rebuild_owner_levels`가 `switch = { trigger = scope:eafp_rebuild_remaining 5 = {…} 10 = {…} … 500 = {…} }`로 같은 case를 골라 `eafp_concession_rebuild_chunk = { LEVELS = n }`을 실행하고, 이것이 `create_building`을 한 번 호출한다. 조계회사가 있으면 회사 소유, 없으면 국가 소유다. 건물이 있으면 `reserves = 0`(엔진이 기존값과의 최대값 유지 → 현금보유고 변화 없음), 새 건물이면 `reserves = 1`.
  4. 보유국 소유가 기대 총량에 못 미치면 debug_log를 남기고 맵을 비운다.
- 조계 레벨은 지급·확장 모두 5단위이므로 저장값은 항상 5의 배수라고 본다(사용자 결정). 그 외 값이나 500 초과는 switch에 case가 없어 덮어쓰지 않는다(fallback 없음).
- 주 분할 보정(2026-11-11): `on_state_created`·`on_state_owner_change`(`eafp_concessions_state_changed`)에서 같은 state region의 조계지가 있는 모든 주에 `eafp_concession_round_ownership_effect`를 실행한다. 각 국가 소유 레벨을 재서 5의 배수가 아니면 가장 가까운 5의 배수(`divide = 5 round = yes multiply = 5`)로 `create_building` 한 번에 덮어쓴다(7 → 5, 8 → 10, 13 → 15). 1~2레벨은 0이 아니라 5로 올린다. 0으로 덮어써 소유자를 없애는 방법은 확인되지 않았기 때문이다. `remove_building`은 쓰지 않으며, 보정 후 권리 정리(refresh)를 실행한다. 반올림으로 도심지 상한을 넘을 수 있으나 상한은 진입 조건이므로 기존 건물은 유지한다.
- 성공 판정: 지급·확장 모두 「총레벨 증가」 대신 보유국 소유 ≥ `scope:concession_expected_levels`로 판정한다. 확장 비용은 이 조건이 맞을 때만 차감한다.
- 건물을 지우지 않으므로 다른 국가 지분·근로자·현금보유고·생산 방식·보조금은 그대로다. 따라서 `flag:cash_reserve` 저장, 생산 방식·보조금 복원, 미귀속 레벨 보정 단계는 삭제했다. `remove_building`은 반환(마지막 권리 소멸)과 권리 없는 주 정리에만 남는다.
- 확장 단위: 저널 버튼·AI 확장 모두 +5레벨(`eafp_concession_add_company_level = { LEVELS = 5 }`), 도심지 상한 여유 5레벨이 필요하다(`eafp_concession_free_capacity >= 5`). 비용 `eafp_concession_expansion_cost`는 레벨당 £50,000 × 5 = 클릭 1회 £250,000이다(2026-11-11 사용자 결정).
- 버튼 툴팁은 `custom_tooltip = { text = eafp_concession_expand_effect_tt ... }`로 감싸 「자국 지분만 덮어쓰고 나머지는 유지」를 안내한다.
- 함께 고친 버그: 새 건물 PM으로 존재하지 않는 `pm_eafp_concession_trade_quantity_normal`을 지정하던 것을 `pm_eafp_concession`·`pm_trade_center_trade_quantity_normal`로 바꿨다.
- 제한(미검증): 「덮어쓰기」 동작은 사용자 확인에 근거하며 엔진 문서는 기존 건물에서 레벨이 max(기존, 지정값)이라고만 적는다. 보유국 소유를 국가 합계로 읽으므로 그 국가의 금융지구·장원 등 다른 소유 형태 지분이 있으면 기대 총량 계산에 포함된다. `create_building`이 기존 건물의 생산 방식을 `activate_production_methods` 값으로 바꿀 수 있다. 변수 맵 값으로 숫자를 쓰는 형식은 바닐라(`value = year`, `variable_map(name|key)`)를 따랐다.

2026-11-12 변경(2차 아편전쟁·조계 요구 AI):
- `dp_second_opium_war`: `requires_interest_marker = no`, `initiator_can_add_war_goals = yes`, `target_can_add_war_goals = yes`. 참전 허용(`additional_involvement_trigger`)은 열강 전체 또는 화북(`sr:region_north_china`)에 이해관계가 있는 국가다. 양측이 전쟁 목표를 추가할 수 있으므로 회유 제안에 조계 등 요구를 담을 수 있다.
- 영국의 톈진(`STATE_BEIJING`의 항구) 조계는 외교전 생성 직후 `enforce_treaty_article`·`primary_demand = yes`로 추가된다. 조건을 못 맞추면 debug_log를 남긴다.
- 도달 조건 분리: `eafp_concession_can_grant` = `eafp_concession_can_receive` + 도달(해당 전략지역 이해관계 **또는** 주 소유국과 외교전 적대·전쟁 중). 이전에는 이해관계만 인정해 영국이 화북 이해관계가 없으면 톈진 요구가 빠졌다. 지급 효과는 도달을 빼고 `eafp_concession_can_receive`만 재검사한다(협상·요구 시점에 이미 통과했고, 조약 발효 시점에는 외교전이 끝났을 수 있으므로).
- 조계 항목 AI: flags에 바닐라 조약항과 같은 `hostile`·`ai_consider_threaten_naval_hostilities` 추가. `evaluation_chance`는 열강 0.3(기타 0.1). 수락 점수에 도시 규모(도심지 레벨 × 2, 최대 40, `EAFP_CONCESSION_AI_CITY`)를 더한다(내주는 쪽은 음수). `wargoal_score_multiplier`는 수취국이 열강이면 +1, 2차 아편전쟁에서 내주는 쪽과 적대 중이면 +2, 영국의 톈진이면 +3(바닐라 홍콩 패턴). 전쟁 목표 기동 비용 10 → 5.
- 미검증: 엔진이 enforce 전쟁 목표 실행 시 `state_valid_trigger`를 다시 검사하는지, `hostile` 플래그의 정확한 AI 효과는 게임에서 확인하지 않았다.

2026-11-12 변경(번역 파일 통합): 조계 번역을 언어마다 `localization/<언어>/eafp_concessions_in_china_l_<언어>.yml` 한 파일로 모았다. `eafp_concessions_buildings_l_*` 전체(36개)와 `eafp_china_l_*`의 「# 중국 조계지」 구역(115개)을 옮겨 151개이며, 원래 파일의 구역과 `eafp_concessions_buildings_l_*` 파일은 삭제했다. 키·값은 그대로이고 출처 주석은 해당 키(`je_concessions_in_china_reason`)에 붙어 있다. 순서는 세 언어가 같다: 개념 → 건물·생산 방식·회사·modifier → 조약 항목 → 외교전·전쟁 목표(조계 요구, 조계 반환) → 저널 → 저널 위젯(주 행, 소유 지분, 확장 버튼) → 월간 사건 200~207. 이후 미사용 문구 50개(구 버전 저널 2, 비활성 이벤트 1001~1006, 주석 처리된 `concession_state_modifier`·`concession_building_modifier`, 옛 위젯 문구, 어디서도 쓰지 않는 `STATE_CONCESSION`)를 삭제해 언어마다 101개가 남았고, 검사기가 이 파일의 모든 키가 실제로 쓰이는지(코드 참조, 다른 문구의 `$키$`·SelectLocalization 분기, 로드되는 이벤트, 스크립트 정의 이름) 확인한다. `qing_owns_all_concessions_tt`는 그 구역 밖의 청 관련 툴팁이라 `eafp_china_l_*`에 남겼다.

2026-11-12 변경(회사 소유 전용): 조계지 레벨은 조계회사 소유만 존재한다. 저널 화면은 소유 항목을 회사 하나로만 해석한다(국유·기타 건물 분기와 번역 `eafp_concession_country_asset`·`_private_asset`·`_other_asset` 삭제). 스크립트에서도 조약 지급의 회사 설립 절차를 `eafp_concession_ensure_company`(회사 슬롯 modifier → `add_company` → 수도 state region에 본사)로 떼어 내, 지급 효과와 모든 조계지 `create_building`(`eafp_concession_rebuild_create`)이 함께 쓴다. 회사가 없는 소유국은 먼저 회사를 만들고, 그래도 실패하면 국유로 대신 주지 않고 레벨을 만들지 않은 채 debug_log를 남긴다. 주간 refresh는 조계권이 없는 국가의 조계회사를 해산하므로, 권리 없는 국가에 회사를 만들면 곧 해산된다(현재 흐름에서는 모든 소유국이 권리를 가진다).

2026-11-12 변경(위젯 틀·상세 배경): `widget_eafp_concessions`를 바닐라 저널 칸(설명·관여국)과 같게 `default_list_position`, 고정 폭 510(`@panel_width_minus_30`), `entry_bg` 외곽선으로 만들었다. 안쪽 여백 5를 두어 주 행은 500, 펼친 상세는 여백 10을 빼고 480 폭이다. 펼친 상세 칸에는 건물 브라우저의 건설 영역과 같은 `dark_area` 배경을 깔았다.

2026-11-12 변경(위젯 위치·저널 설명): 저널 위젯을 `custom_widget_container_5`(저널 설명 바로 아래, 관여국 목록 위)에 둔다. 「현재 N개 주에 조계지가 있다.」 문장은 저널 상태(`je_concessions_in_china_status`, `status_desc`가 없을 때 엔진이 읽는 기본 키)에 3개 언어로 두고 설명(`_reason`)에서는 뺐으며, N은 위젯 행과 같은 목록 `concession_candidate_states_gvarlist`의 크기다.

2026-11-12 변경(현금보유고·위젯 정리): 조계지 건물을 새로 세울 때(첫 지급, 지분별 반환 뒤 재생성) `reserves = 0`으로 만든다. 이전의 「새 건물은 `reserves = 1`」 규칙을 대체한다. 기존 건물에 덮어쓸 때도 0을 넘겨 엔진 규칙(기존값과 지정값 중 큰 값)에 따라 현재 현금보유고를 건드리지 않는다. 저널 위젯 `widget_eafp_concessions`에는 `eafp_concession_state_rows`만 남기고 상단 제목·안내·빈 목록 문구와 그 번역(`eafp_concession_overview_heading`·`_hint`·`eafp_concession_empty_overview`)을 삭제했다.

2026-11-12 변경(확장 버튼 툴팁): 바닐라 저널 행동 버튼 툴팁(`SCRIPTED_ACTION_TOOLTIP`)과 같은 형식으로 `eafp_concession_expand_button_tt`를 쓴다. `#header` 제목 → 설명 → `$TOOLTIP_DELIMITER$` → 조건(`IsValidTooltip`, 바닐라 체크 표시) → `#title 효과:#!` → 효과(`ExecuteTooltip`). 조건 문구 4개는 바닐라 트리거 문체(한국어 「~이어야 함」, 영어 「We must …」, 중국어 「我们必须…」)로 바꿨다. 효과는 `custom_tooltip` 한 줄(자국 지분 +5 크기)과, 스크립트 GUI의 `show_as_tooltip` 안 `add_treasury`가 그리는 바닐라 국고 줄(표시 전용, 실제 과금은 확장 효과 안에서 레벨 증가 후)이다.

2026-11-12 변경(이동 버튼 툴팁): 주·조계지 건물·국가·회사로 가는 네 버튼은 일반 문구 툴팁 대신 바닐라 객체 툴팁(`FancyTooltip_State`·`FancyTooltip_Building`·`FancyTooltip_Country`·`FancyTooltip_Company`)을 `tooltipwidget`으로 띄운다. 건물 버튼은 `State.GetBuilding('building_eafp_concession')`를 datacontext로 받아 `Building` 기준으로 열고 툴팁을 띄운다. 쓰지 않게 된 `eafp_concession_goto_*_tt` 번역 4개는 삭제했다.

2026-11-12 변경(저널 GUI 정리): 주별 상세 칸에는 「국가별 소유 지분」(막대 + 소유 목록)과 조계 확장 버튼만 남겼다. 상한 상태 문구·상한 막대, 권리 보유국 목록과 그 번역(`eafp_concession_rights_heading`·`eafp_concession_holder_row`)은 삭제했다. 막대의 각 조각에는 소유국 국기 버튼(`OpenCountryPanel`)과, 소유 건물이 회사이면 회사 로고 버튼(`Company.GetCompanyType.GetIcon`, `OpenCompanyPanel`)을 함께 둔다. 행 머리의 「현재 / 상한」 글자에는 `eafp_concession_cap_tt` 툴팁으로 상한 = 도심지 레벨 × 5 계산, 현재 레벨, 여유·초과 상태(`$eafp_concession_cap_status$`), 신규 획득·확장에 5레벨 여유가 필요한 이유와 도심지 감소 시 기존 건물 유지를 설명한다.

2026-11-12 변경(위신 조건 삭제): 7절의 「주 소유국 위신이 보유국보다 높으면 확장·사건 자격 중단」보다 우선한다. 두 국가의 위신 우위와 상관없이 조계가 작동한다. `eafp_concession_active`, `eafp_concession_active_holder_count`, 월간 사건의 보유국 선택, 저널 자동 투자 조건에서 위신 비교를 모두 뺐다. 저널 화면의 작동 상태 표시(작동 보유국·무역소 환산 요약, 보유국별 작동/중단 표시와 위신 툴팁, 위신 값)와 `eafp_concession_holder_active_gui`, 관련 번역 키를 삭제했고, 권리 목록은 「국기 + 국가 이름」만 보여 준다. 확장 조건 툴팁에서도 위신 문구를 뺐다. 강제 반환 시의 위신 손실(`eafp_concession_forced_loss`)은 그대로 둔다.

2026-11-12 변경(저널 GUI): 9절의 「한 주만 펼침」 아코디언보다 우선한다. 바닐라 건물 브라우저(건물 유형별 묶음 행)처럼 조계 주 목록을 보여 주고, 각 행 머리에 「국기 + 주 이름」·「현재 조계지 / 상한」과 주 화면(`button_icon_goto`)·조계지 건물 화면(무역소 아이콘 버튼)으로 가는 버튼을 둔다. 행마다 `GetVariableSystem.Toggle(Concatenate('eafp_concession_state_', State.GetIDString))`로 독립적으로 접고 펼친다(기본 접힘). 펼치면 맨 위에 바닐라 위상 우위 막대(`leverage_stacked_barchart`)·건물 소유 막대처럼 `v3_stacked_barchart` 하나로 국가별 소유 지분을 그린다. 조각은 `Building.GetBuildingOwnerships`의 소유 항목마다 하나이고 폭은 `GetOwnershipRatio`, 색·국기는 소유 국가(국유는 `GetOwnerCountry`, 회사·금융지구 등은 `GetOwnerBuilding.GetOwner`)의 지도 색이다. 그 아래에 같은 색 표식이 붙은 소유 목록, 상한 상태·막대, 작동 요약, 권리, 확장 버튼을 이어 둔다. 용량 툴팁(`eafp_concession_capacity_tt`), 도시 건물 주간 순이익 카드(`eafp_concession_profit_heading`·`_value`·`eafp_concession_economy_tt`), 잔존 지분 안내(`eafp_concession_shared_assets_note`), 자동 투자 안내(`eafp_concession_private_investment_label`·`_tt`)는 사용자 지시로 화면과 번역에서 삭제했다. 자동 투자와 `eafp_concession_state_profit`(AI 확장 정렬) 자체는 그대로 동작한다. 한 국가가 회사와 국유로 나눠 가지면 같은 색 조각이 둘로 보인다(GUI에서 국가별 합산 불가). 렌더링은 게임에서 확인하지 않았다.

2026-11-12 변경(영향력·관여): 조계 항목 `cost`를 바닐라 `treaty_port`와 같은 50(영향력, 유지비는 `maintenance_paid_by = target_country`로 보유국 부담)으로 했다. 지급 효과가 권리를 등록한 직후 보유국에 그 주 전략지역 관여 +1000(`add_involvement`)을 준다. 지급이 실패하면 관여도 주지 않는다.

2026-11-12 변경(조계 요구 외교전):
- 바닐라 `dp_take_treaty_port`·`dp_open_market`처럼 외교 렌즈에서 시작하는 `dp_eafp_demand_concession`(「조계 요구」)을 추가했다. 요구를 먼저 보내고, 상대가 받아들이면 주요 전쟁 목표가 즉시 집행되며, 거부하면 그 요구를 주요 전쟁 목표로 하는 외교전이 시작된다(바닐라 요구 단계를 그대로 쓰며 `on_demand_accepted`는 비워 둔다).
- 시작 조건: 비분권 국가, 공격적 외교전 허용, 열강, 대상과 종속 관계 없음, 관계 차단 없음, 대상이 조계 적격 주(`eafp_concession_eligible_state`)를 보유.
- 전쟁 목표 `eafp_demand_concession`(`kind = custom`, 주 대상, `control_target_state`, `requires_interest`·`can_add_for_other_country`로 회유 제안에도 쓸 수 있음). 가능·유효 조건은 대상 국가 소유 주이면서 `eafp_concession_can_grant = { HOLDER = root }`. 기동 비용은 조약항과 같은 인구 비례식, 악명 5.
- 집행(`on_enforced`)은 `create_treaty`(`is_draft = no`, 구속 5년)로 대상국 → 보유국 `eafp_grant_concession` 항목이 든 조약을 즉시 발효시킨다. 지급·저널 추가는 조약의 `on_entry_into_force`가 하므로, 전쟁으로 얻은 조계도 조약 기반이며 탈퇴 조건·철회 반환이 그대로 적용된다. 조약 이름 `eafp_concession_treaty_name`.
- AI: `ai_strategy_default`의 `wargoal_scores`에 INJECT로 `eafp_demand_concession`을 추가했다. 받을 수 있는 열강이면 40 + 도심지 레벨 × 3(최대 60), 강압 가능 거리면 +20.
- 미검증: 요구 수락 시 엔진이 custom 전쟁 목표의 `on_enforced`를 실행하는지, `create_treaty`로 만든 조약에서 `on_entry_into_force`가 실행되는지, AI가 custom 전쟁 목표 키로 `wargoal_scores`를 읽는지는 게임에서 확인하지 않았다.

최신 수량 변경: 조계 1레벨 = 무역소 1레벨, 새 국가의 주별 조계권 획득마다 +5레벨, 주별 상한 = 도심지 ×5. 이미 조계지 건물이 있는 주에도 새 보유국의 회사 지분 5레벨을 더한다. 저널 유료 확장은 기존 +1레벨·£50,000을 유지한다. 반환 충격의 분모는 실제 도심지 레벨을 유지하고 상한 계산과 분리한다. 구 세이브의 기존 레벨 자동 증설은 하지 않는다.

## 1. 구현 범위

| 요구 | 현재 코드 |
| --- | --- |
| 국가별로 건물을 분리하지 않음 | 실제 state마다 공통 `building_eafp_concession`, 복수 국가 회사의 지분 |
| 무역소 대체 | 조계 1레벨에 바닐라 무역소 1레벨 상당 고용·무역 처리능력·투입량 |
| 조약 획득 | 기존 조약 발효 효과에서 회사 생성 및 회사 소유 +5, 성공 후 권리 등록 |
| 회사 수명 | 보유국마다 공통 일반 기업 유형 1개, 첫 설치 시 생성·마지막 권리 소멸 시 해산 |
| 기업 슬롯 | 회사 존재 중 국가에 `country_max_companies_add = 1`, 번영도와 무관 |
| 저널 확장 | 보유국 국고 £250,000, 실제 +5 성공 후 과금. AI도 같은 효과 |
| 도시 한도 | 신규 획득 `T + 5 ≤ 5U`, 저널 확장 `T + 1 ≤ 5U`. 이후 U 감소 시 기존 건물 유지 |
| 자동 산업 투자 | 국제 저널 월간 계산으로 적격 조계 주마다 최대 1레벨 민간 건설 큐 등록 |
| 현황 GUI | 실제 총량·cap·여유·초과·무역소 환산·회사 소유 항목·국가 권리·확장 버튼 |
| 반환 충격 | 반환 전 국가 소유 레벨과 도심지 대비 비율에 따른 관계·위신 손실 |
| 미지원 부분 | 공유 지분의 소유자별 철거/생산 정지, 민간 공사의 회사 지정은 11절 참조 |

관내18성은 `geographic_region_china_proper`, 권리 저장 단위는 실제 state다. 특약 버튼, 소·중·대 구분, 긴장도, 운영 방침, 공공조계, 규모별 주권 침해, 거점 프로빈스, 개정번호·지급완료·세이브 버전 변수와 구 세이브 변환은 추가하지 않는다. 국가별 건물 유형 풀도 사용하지 않는다.

기존 조약·전쟁 목표·월간 사건과 국제 저널을 수정한다. 새 국가별 저널이나 정기 타이머를 만들지 않는다. 저널에는 `possible`을 추가하지 않고 조약 발효 시 `add_contextless_journal_entry`로 추가한다.

## 2. 전체 흐름

```mermaid
flowchart TD
    A[조계 조약 발효] --> B{대상과 권리 및 cap 유효?}
    B -->|아니오| X[지급하지 않음]
    B -->|예| C{전용 회사 존재?}
    C -->|아니오| D[기업 슬롯 +1 후 회사 생성 및 본사 지정]
    C -->|예| E[회사 소유 조계지 +5]
    D --> E
    E --> F{회사와 실제 레벨 증가 확인?}
    F -->|아니오| F1[실패 안내와 빈 회사 정리]
    F -->|예| G[권리 등록 및 저널 현황 갱신]
    G --> H[주별 cap과 회사별 소유 항목 표시]
    H --> I[플레이어 또는 AI 확장]
    I --> J{작동 조건과 cap 및 국고 충족?}
    J -->|예| J1[회사 소유 +1 성공 후 국고 차감]
    G --> K[월간 사건 후 조계 주의 산업 수익 계산]
    K --> K1{노동력과 기반시설 및 건설 조건 충족?}
    K1 -->|예| K2[민간 큐에 최대 1레벨 등록]
    K2 --> K3[엔진이 재원과 완공 소유권 처리]
    G --> U{도심지 감소로 cap 초과?}
    U -->|예| U1[기존 건물 유지 및 추가 설치와 확장 차단]
    G --> L[조약 종료 또는 사건과 전쟁으로 반환]
    L --> M[반환 직전 국가 소유 레벨 산출 및 권리 제거]
    M --> N{그 주에 다른 권리가 남음?}
    N -->|예| N1[공유 자산 보존: 소유자별 철거 미지원]
    N -->|아니오| N2[조계지 건물 전체 제거]
    N1 --> O[강제 반환이면 규모별 관계와 위신 손실]
    N2 --> O
    O --> P{그 국가에 다른 조계권이 남음?}
    P -->|예| P1[회사 유지]
    P -->|아니오| P2[회사 해산 및 슬롯 보정 제거]
```

## 3. 원본 데이터와 계산

- 권리: state의 기존 `concession_owner_varlist`.
- 회사: 국가마다 일반 유형 `company_eafp_concession` 인스턴스. 국가 scope에서 `company:company_eafp_concession` 조회.
- 총량 T: 실제 조계지 building의 전체 레벨. **반환 후 공유 건물에 남은 잔여 자산도 포함한다.**
- U: 같은 실제 state의 도심지 레벨 합계. cap C는 `5U`이며 `eafp_concession_urban_cap`이 반환한다. 실제 도심지 레벨은 `eafp_concession_urban_levels`로 별도 조회한다.
- 여유: `max(5U-T, 0)`. 초과: `max(T-5U, 0)`. 무역소 환산: `T`.
- GUI 회사 보유량: `Building.GetBuildingOwnerships`의 실제 회사 소유 항목별 `BuildingOwnership.GetLevel`.
- 기존 `concession_candidate_states_gvarlist`는 주간 및 권리 변경 시 다시 만드는 파생 순회 목록이다.

총량·cap·회사 보유량·주간 수익을 영속 숫자로 복제하지 않는다. 반환 시에는 `levels_owned_by_country` 비교 트리거를 이용한 32회 이진 탐색으로 해당 국가 소유 레벨을 구한다. 범위는 0부터 해당 건물의 실제 레벨까지다. 이는 **기업 하나가 아니라 그 국가의 모든 소유분**이며, 반환 잔여 자산이나 재획득이 있으면 전용 기업 지분과 다를 수 있다. 해당 차이는 11절의 제한이다.

새 영속 변수는 국가의 `concession_loss_prestige_snapshot` 하나다. 자산과 권리를 제거한 뒤에는 이전 손실 강도를 복구할 수 없으므로 현재 적용 중인 과거 위신 충격을 저장한다. 730일 만료이며 modifier가 없으면 기존 refresh에서 제거한다. 지급·규모·cap 장부로 사용하지 않는다. 나머지 신규 손실 계산은 효과 체인의 임시 scope value다.

## 4. 조계지 건물과 회사

| 일반 무역 PM 기준 | 무역소 1레벨 | 조계지 1레벨 |
| --- | ---: | ---: |
| 사무원 | 800 | 800 |
| 상점 주인 | 200 | 200 |
| 주간 거래 수 | 1 | 1 |
| 무역 처리능력 | 10 | 10 |
| 일반 무역량의 상선 투입 | 4 | 4 |
| 기반시설 사용량 | 0.5 | 0.5 |

외부무역 원칙과 무역량 생산 방식도 대응 PM을 사용한다. 바닐라의 level/workforce scaling과 기술·원칙 조건을 유지하고 unscaled 비율도 원본과 동일하다. 최초 5레벨의 총 처리능력은 무역소 5레벨 상당이며 실제 매출·이익을 보장하지 않는다. 무역능력은 소재 주의 시장에, 배당은 실제 소유자에게 적용되는 엔진 경로다.

회사는 `flavored_company = no`, 수동 설립 조건은 차단하고 스크립트로 생성한다. 본사는 보유국 수도의 state region에 지정한다. `building_types`에는 조계지만 등록한다. 회사 존재에 따라 슬롯 +1을 유지하고 마지막 권리 소멸 시 `remove_company`를 호출한다. 일반 공장을 직접 제거하지 않는다. 해산 자산 처리와 비용은 엔진에 맡기며 실제 동작은 미검증이다.

최소 자산 5레벨·설립/해산 쿨다운이 동적 `add_company`에 미치는 영향은 미검증이다. 신규 권리의 기본 지급량은 5레벨이지만 회사 생성 시점의 최소 자산 검사 통과는 미검증이다. 전세계 define은 변경하지 않는다. 회사와 실제 레벨 증가를 확인한 후 권리를 등록하고 실패 시 안내하며 빈 회사·슬롯을 정리한다. 실패한 조약 항목의 자동 삭제는 구현하지 않았으므로 안내는 항목 제거 후 재협상을 요청한다.

## 5. 조약 지급·저널 확장·cap

신규 설치는 기존 중국 소유·관내18성·비무역항·열강·이해관계·미보유 조건에 유효 수도와 신규 지급에 필요한 cap 여유 5레벨을 추가한다. 조약 입력 및 발효 효과에서 같은 조건을 재검사한다.

회사 생성 후 `create_building.add_ownership.company`에 유형·보유국·5레벨을 전달한다. 기존 건물이 있으면 해당 건물에 추가하며 기존 PM을 초기화하지 않는다. 새 건물에만 일반 무역량 PM을 지정한다.

`eafp_concession_add_company_level`은 신규 지급과 확장이 공유하며 `LEVELS = 5`와 `LEVELS = 1`을 각각 전달한다. `eafp_concession_expand_effect`는 플레이어 GUI와 월간 AI가 공유한다. 실제 actor의 기존 권리·위신·회사·보유분·여유 cap·국고를 효과 안에서 다시 검사하고 총레벨 증가 후에만 £50,000을 차감한다. AI는 매월 보유국당 최대 한 번, 조건을 충족하고 도시 순이익이 양수인 주 중 순이익이 큰 주를 선택한다.

cap은 진입 조건이다. U가 10에서 7 또는 0이 되어도 T=50과 기존 권리·회사는 유지한다. 초과량만 표시하고 신규 증가를 막는다. cap 초과만으로 영업·산업 투자·반환 충격을 발생시키지 않는다. 기존 주 상속 경로는 권리만 승계하며 건물 보상을 재지급하지 않는다.

## 6. 저널의 민간 산업 투자

기존 국제 저널의 월간 사건 처리 **이후** 실제 후보 주를 한 번씩 순회한다. 국가별 반복으로 같은 주에 여러 공사를 등록하지 않는다.

1. 작동 중인 권리와 회사, 실제 조계지 레벨이 존재해야 한다.
2. 주의 기반시설 여유와 실업률이 양수이고 주 소유국 투자풀 잔액이 양수여야 한다. 투자풀 잔액은 전체 공사비 확보 보장이 아니다.
3. 이미 존재하는 18종 적격 산업 중 `weekly_profit > 0`, 레벨 > 0, `level_after_queued_constructions = level`, `is_under_construction = no`, `can_queue_building_levels = 1`, state의 업종별 `can_construct_building`을 검사한다.
4. `weekly_profit / max(level,1)`이 높은 건물 하나를 선택한다. 미래 추가 레벨의 예상 이익이 아니라 현재 평균 수익 지표다.
5. 해당 state에서 `start_privately_funded_building_construction = building_type`을 한 번 호출한다. 업종별 명시 분기를 사용한다.
6. 공사 진행·재원 지출·완공 소유권은 엔진이 처리한다. 무료 공장 생성이나 별도 국고 지원은 없다.

대상 18종: 식품, 방직, 가구, 유리, 공구, 제지, 화학, 폭약, 합성, 제철, 발동기, 자동차, 전기, 조선, 무기, 대포, 군수품, 예술 학교. 아직 없는 산업, 도심지, 본사·금융지구·장원, 조계지·무역소, 행정·군사 시설은 후보가 아니다. 수입 산정용 도시 건물 필터는 별도로 유지한다.

등록 효과에는 투자 회사나 국가를 지정하는 문서화된 인자가 없다. 따라서 **이 코드는 조계 소재 주의 민간 공사 등록이며 조계회사의 직접 소유를 보장하지 않는다.** 기존 공사 식별·선택 취소 경로도 추가하지 않았다. 권리 소멸 후 신규 등록은 중단하지만 이미 등록한 공사는 엔진 큐에 남는다. 저널 외 회사 자율 투자의 지역 제한을 구현했다고 설명하지 않는다.

## 7. 위신과 국고 이전 삭제

주 소유국 위신이 보유국보다 높으면 그 보유국의 확장·사건 자격을 중단한다. 동률은 작동한다. 저널 산업 투자는 작동 중인 보유국이 하나 이상 있을 때만 진행한다. 권리와 cap 점유는 중단 중에도 유지한다.

공유 건물은 정지하지 않는다.

**주간 이전금은 삭제했다(2026-11-10).** 중국 소유국 국고에서 보유국 국고로 돈을 직접 옮기는 경로가 없다.

- 삭제: script value `eafp_concession_host_debit`·`eafp_concession_state_debit`·`eafp_concession_holder_credit`, refresh 효과의 `concession_payment`(중국 지출)·`concession_paid`(보유국 세입) modifier 부여, 조약 AI 평가의 `EAFP_CONCESSION_AI_INCOME` 항목, 저널의 「주 소유국 주간 부담」 카드와 보유국별 「주간 수취」 표시.
- 삭제: 구 세이브 정리용 `remove_modifier`와 `eafp_chi_modifiers.txt`의 두 modifier 정의, 3개 언어의 `concession_payment`·`concession_paid` 번역. 구 세이브에 이미 붙은 modifier의 처리는 엔진에 맡긴다.
- 유지: `eafp_concession_state_profit`(GUI 표시·AI 확장 대상 정렬)과 `eafp_concession_state_share`(사건 200번대에서 **보유국이 주 소유국에 지급**하는 일회성 배상액 산정). 후자는 반복 이전이 아니며 방향도 반대다.
- 보유국 수익은 조계지 건물의 무역과 조계회사 배당 등 엔진 경로뿐이다.

## 8. 반환과 규모별 충격

모든 반환은 공통 효과를 사용하며 `FORCED = yes/no`를 명시한다. 권리가 이미 없으면 재실행하지 않는다. 변경 전 국가 소유 레벨 L과 `share = L / max(U,1)`을 임시 값으로 산출한다.

- 월간 강제 반환과 반환 전쟁 결과: 강제 처리.
- 조약 철회: 철회국이 현재 주 소유국이고 남은 구속 기간이 양수이면 강제, 나머지는 정상 처리.
- 탈퇴 조건(2026-11-11, 바닐라 `treaty_port`와 동일한 `can_withdraw`): 조계를 내준 쪽(source, 중국 측)은 보유국보다 국가 등급이 높을 때만 탈퇴할 수 있고, 미승인국은 승인국 보유국을 상대로 탈퇴할 수 없다. 보유국(target)은 언제든 탈퇴할 수 있다.
- 지분별 반환(2026-11-11): 조약 철회·파기·사건·전쟁으로 한 보유국의 권리가 끝나고 그 주에 다른 권리가 남으면 `eafp_concession_remove_holder_share`가 반환국 지분만 없앤다. 엔진에 소유자별 레벨 제거 효과가 없으므로 반환국을 뺀 모든 국가의 소유 레벨을 `eafp_concession_rebuild_map`(키 = 국가)에 저장하고 `remove_building` 후 5단위 switch로 국가마다 `create_building`을 한 번씩 다시 호출한다. 재건축이므로 남은 국가의 근로자는 다시 고용되고 현금보유고(새 건물 1)·생산 방식(기본값)·보조금은 초기화된다. 5의 배수가 아니거나 500을 넘는 지분은 재생성되지 않는다. 마지막 권리가 끝나면 이전처럼 건물 전체를 철거한다.
- `on_break`에는 반환을 중복 배치하지 않는다. 실제 철회 처리는 `on_withdrawal` 한 곳이다.
- 정상 반환은 추가 외교 충격이 없다. cap 감소는 반환 자체를 발생시키지 않는다.

강제 반환 수치는 다음과 같다.

```text
관계 하락 = min(50, 2L + 10 × share)
위신 감소 = min(30, L + 5 × share), 730일
```

U=10에서 L=1이면 관계 -3·위신 -1.5, L=5이면 -15·-7.5다. 관계 하락은 각 반환마다 적용한다. 위신은 가장 강한 미만료 충격 하나를 유지한다. 더 큰 손실은 강도와 730일을 갱신하고 작은/동일 손실은 기존 강도·만료를 낮추거나 연장하지 않는다.

권리 제거 후 그 주의 다른 권리가 없으면 공유 조계지 전체를 제거한다. 다른 권리가 남으면 다른 국가 자산을 훼손하지 않도록 건물을 남긴다. **이 경우 반환국 자산 일부도 남는 제약이 있다.** 어느 국가의 마지막 전체 권리가 소멸하면 그 회사는 해산한다. 일반 산업 건물은 직접 철거하지 않는다.

## 9. 저널 GUI

국제 저널 한 곳에 500px 폭의 주별 카드를 표시한다. 카드 제목을 누르면 해당 주의 상세 정보가 펼쳐지고 다른 주는 접힌다. 선택은 `GetVariableSystem.SetOrToggle`과 실제 `State.GetIDString`을 사용하는 클라이언트 UI 상태다. 게임 변수·저장 이력·회사별 목록 캐시는 추가하지 않는다.

- 기본 카드: 주 소유국 국기·주 이름, 조계 총량/도심지 5배 cap, 여유·가득 참·초과 상태, 점유 막대, 도시 건물 주간 순이익, 활성 보유국 수·무역소 환산량. (주 소유국 주간 부담 카드는 이전금 삭제와 함께 제거)
- 막대는 `T / max(5U,1)`을 0~1로 제한한다. 초과 시 붉은 막대와 실제 초과 레벨을 함께 표시하며 U=0에도 나누기 오류가 없다. 기존 건물 보존 규칙은 변하지 않는다.
- 상세 권리 목록: 국가별 작동 여부·위신. (주간 수취액 표시는 이전금 삭제와 함께 제거)
- 상세 자산 목록: `Building.GetBuildingOwnerships`의 모든 항목을 순회해 회사·국유·회사 없는 민간 소유를 구분하고 각 항목의 레벨·실제 소유 비중을 표시한다. 회사 본사/지역 본사의 여러 항목을 국가별 합계인 것처럼 오표시하지 않는다. 긴 이름은 말줄임과 전체 이름 툴팁을 제공한다.
- 동작: 주·조계지 건물 패널 바로가기, 자신의 조계 +1 확장 버튼. 확장 조건은 기존 서버 trigger와 효과를 유지하고 권리/위신·cap·국고·소유분의 조건을 번역된 툴팁으로 보여 준다.
- 비어 있는 상태: 조계권이 없을 때 빈 목록 대신 조약으로 조계를 획득하면 표시된다는 안내를 제공한다.
- 반환 잔여 자산과 민간 큐 설명은 상세 영역에 배치한다. 화면 금액은 현재 순이익 기준임을 전체 안내에 명시한다.

### 참고한 로컬 GUI

1. Community Mod Framework 1.67.2의 `gui/com_journal_injects/buildings.gui`: 건물 카드와 직접 이동 버튼, 명확한 데이터 컨텍스트. 외부 모드의 전용 type이나 저장 변수를 의존성으로 가져오지 않았다.
2. new_korea_mod의 `gui/journal_entry_widgets/nkm_manchuria_policy_widgets.gui`: 일정 폭의 두 열 지표와 제목/값 구분.
3. `3338630543/gui/journal_entry_widgets/moh_china_widgets.gui`: 저널 삽입 객체와 정보 계층. 인물 전용 배경·대형 초상화는 이 현황표에는 적용하지 않았다.
4. EAFP의 만한·막번 저널: `section_header_button`과 UI 전용 펼침 상태.
5. 바닐라 `gui/building_details_panel.gui`: 실제 `BuildingOwnership`의 국유/민간 구분과 레벨·소유 비율. `gui/shared/buttons.gui`·`progressbars.gui`: 바닐라 버튼·진행 막대의 블록 정의.

경로 1은 로컬 워크숍 `3385002128`, 경로 2는 `3740653311`에서 읽었다. 사용한 GUI 데이터 함수는 저장소의 `documentation/data_types*.txt`와 교차 확인했다. 게임 실행 및 실제 렌더링 검증은 사용자 지시에 따라 생략한다.

## 10. 수정 경로와 정적 검증

| 경로 | 역할 |
| --- | --- |
| `common/building_groups`, `buildings`, `production_methods`, `production_method_groups`의 `eafp_concessions_*` | 공유 건물과 무역소 동일 수치 PM |
| `common/company_types/eafp_concessions_companies.txt` | 공통 회사 유형 |
| `common/static_modifiers/eafp_concessions_modifiers.txt` | 회사 슬롯·반환 위신 modifier |
| `common/scripted_effects/eafp_concessions_effects.txt` | 부여·확장·반환·refresh·수명 |
| `common/scripted_triggers/eafp_concessions_triggers.txt` | 기존 권리·작동 조건과 신규 cap·회사 조건 |
| `common/script_values/eafp_concessions_values.txt` | 실제 레벨·cap·손실·비용·산업 수익 |
| `common/journal_entries/eafp_concessions_in_china.txt` | 기존 주간 정합화, 월간 사건·투자·AI 확장 |
| 기존 조약·전쟁 목표 파일 | 공통 부여·반환 연결 |
| 기존 scripted GUI와 journal widget | 현황·소유 항목·확장 |
| `localization/*/eafp_concessions_in_china_l_*.yml` (한국어·영어·중국어 간체) | 조계 번역 전체 |
| `tools/validate_china_concessions.py` | 참조·중복·인코딩·수치·연결 정적 검사 |

정적 검증 명령:

```powershell
& 'C:/Users/KHG/AppData/Local/Programs/Python/Python310/python.exe' -B tools/validate_china_concessions.py --game-root 'D:/SteamLibrary/steamapps/common/Victoria 3/game'
git diff --check
```

검사기는 정의/참조·3개 언어·BOM/CRLF·자산 존재·무역소 동일 수치 PM·최초 5레벨·도심지 5배 cap·18종 큐 분기·명시적 반환 사유·공용 확장 과금을 확인한다. 정적 성공은 엔진 파싱·경제·GUI 동작 성공과 같지 않다. 이번 요청에서는 게임 실행, 저장 변경, 콘솔 probe, 런타임 로그 검증을 하지 않는다. scratch probe들은 자동 호출되지 않는 실험 자료다.

## 11. 남은 제한과 향후 실행 확인 항목

1. 소유자별 공유 레벨 철거 API를 찾지 못했다. 다른 권리가 남으면 반환 자산이 남고 cap을 계속 점유한다. 같은 국가 재획득 시 과거 잔여 자산까지 국가 보유량/다음 충격 계산에 들어갈 수 있다. 음수 `add_ownership`이나 공유 건물 삭제·재생성을 사용하지 않는다.
2. 공유 건물의 지분별 생산·배당 정지는 미구현이다. 개별 특권 정지와 전체 비활성일 때 건물 정지만 구현했다.
3. 민간 큐의 회사 지정과 회사 기본 자율 투자 지역 제한은 미구현이다. 완료 산업이 조계회사에 귀속된다고 보장하지 않는다. 반환 후 기존 민간 공사도 별도 취소하지 않는다.
4. 첫 5레벨 회사 설립/유지·즉시 재설립·해산 자산 및 비용, 동적 회사 소유 +1과 신설 무역 건물의 실제 수입, GUI 데이터 경로와 표시, 큐 대기 중복 조건, 조약 철회 시 남은 구속 기간 조회는 게임에서 미검증이다.

향후 게임 검증을 허용할 때는 첫 생성→동일 주 복수 회사→유료 확장→cap 감소 보존→민간 공사 대기/완공→부분 반환→마지막 권리와 회사 해산→재획득 순서로 확인한다. 현재 코드는 위 제한을 감춘 완전한 소유자별 철거·회사 직접 투자 구현으로 간주하지 않는다.
