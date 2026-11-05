# EAFP 미완성 콘텐츠 점검표

작성일: 2026-10-13 (한국 시간)  
점검 기준: 현재 로컬 작업 트리(류큐 처분 제거 반영), 기준 HEAD `bca4e683` (`조선 쟁탈 저널`)  
점검 방식: 활성 스크립트의 정의·호출·완료 처리, 현지화, `.disable` 파일, 기존 기획 문서를 정적으로 대조했다. 게임 실행 검증과 전체 엔진 문법 검사는 수행하지 않았다.

## 1. 읽는 법과 우선순위

현재 가장 명확한 미완성은 **간도 구상, 임시대총통, 신해혁명 일지의 일부 처리**다. 별도로 **번벌 정치, 만주 망명 조정, 막부 개혁 리워크, 조청전쟁 평가 개편**은 계획과 현재 구현 사이에 차이가 남아 있다.

이 문서는 아래 상태를 구분한다. 비활성 파일과 옛 현지화를 모두 구현해야 할 과제로 취급하지 않는다.

| 상태 | 판정 기준 |
| --- | --- |
| 구현 공백 확인 | 활성 파일의 핵심 처리 부재, 연결되지 않은 기능, 명시적인 임시 구현을 직접 확인 |
| 계획 미반영 | 기획은 있으나 해당 설계의 핵심 정의·연결이 현재 코드에 없음. 기존 기능 자체가 없다는 뜻은 아님 |
| 보류·비활성 | `.disable`, 강제 차단, 현지화만 존재. 복원·통합·폐기 여부를 먼저 정할 항목 |
| 문구·밸런스 보완 | 기능은 존재하지만 TODO 문구, 임시 수치, 자산 개선 표시가 남음 |
| 실행 검증 대기 | 코드가 있으며 실제 게임 결과를 확인해야 함. 미구현과 구분 |

우선순위는 작업 제안이다. **P1**은 활성 경로의 핵심 공백과 사용자에게 보이는 미작성 문구, **P2**는 후속 설계·밸런스·실행 검증, **P3**는 보류 콘텐츠와 잔여 데이터 정리다. 빈 `immediate`, 무효과 선택지, 빈 pulse 하나만으로는 미완성이라고 판정하지 않았다.

## 2. 활성 콘텐츠에서 확인한 구현 공백

### A01. 조선 — 간도 구상과 획득 버튼 연결 [P1]

- **현재 상태:** `je_gando_ambition`은 활성 `.txt`에 있고 진입·실패·7,300일 기한 조건이 있지만, `complete`와 `on_complete`가 비어 있다.
- **추가 확인:** `eafp_scripted_button_gando_ambition_gando_acquisition`에는 남만주의 지정 프로빈스를 조선 주로 만드는 효과가 이미 있다. 그러나 저널에 `scripted_button` 연결이 없고, 저장소의 다른 활성 스크립트·GUI에서도 해당 버튼 연결을 찾지 못했다. 따라서 영토 획득 효과 자체가 전혀 없는 것은 아니다.
- **현지화:** 저널 및 버튼의 자체 이름·설명 키 정의를 저장소 현지화에서 찾지 못했다.
- **남은 일:** 기존 획득 효과를 사용할지 결정하고 버튼·협상·완료 판정을 연결한다. 거절, 영토 소유자 변경, 전쟁·청 붕괴, 시간 초과에 대한 종료 처리를 정하고 문구를 추가한다.
- **완료 기준:** 정상 플레이에서 행동을 실행하고 실제 영토 결과에 맞게 저널이 종료되며, 관련 표시 키가 노출되지 않는다.
- **근거:** [간도 일지](../common/journal_entries/eafp_korean_reformation.txt#L1229), [간도 획득 버튼](../common/scripted_buttons/eafp_korean_reformation_buttons.txt#L182).

### A03. 중국 — 위안스카이·쑨원 임시대총통 [P1]

- **현재 상태:** `je_provisional_presidency_ysk`, `je_provisional_presidency_sys`는 `immediate`, `complete`, `on_complete`가 모두 비어 있는 골격이다.
- **진입은 존재:** `warlord_china_events.21`·`.22` 주변에서 두 일지를 실제 추가한다. 단순 보관 파일이 아니다.
- **현지화:** 두 일지의 `_goal`이 한국어·영어·중국어 간체 모두 `TODO`다.
- **남은 일:** 대통령 취임 후 목표, 정치 안정·제정 복귀 등 채택할 분기, 성공·실패·지도자 교체 시 종료와 후속 콘텐츠를 정한다.
- **완료 기준:** 취임부터 후속 정국까지 플레이 가능한 흐름이 있고, 목표 문구와 종료 판정이 일치한다.
- **근거:** [임시대총통 일지](../common/journal_entries/eafp_provisional_presidency.txt), [취임 연결](../events/warlord_china_events.txt#L1002), [목표 문구](../localization/korean/eafp_china_l_korean.yml#L1949).

### A04. 중국 — 신해혁명 일지의 후속 처리 [P1]

- **현재 상태:** `je_xinhai_revolution`은 중화민국 소멸을 완료 조건으로 삼지만 `on_complete`는 TODO이며 주간 pulse도 비어 있다. `je_xinhai_revolution_kmt`는 청 소멸 시 `revolutionary_prov_gov_var` 제거만 수행한다.
- **범위 주의:** 혁명 발생·청 멸망·공화국 수립·만주 몽진 이벤트는 별도로 구현되어 있다. 신해혁명 전체가 미구현이라는 뜻은 아니다.
- **남은 일:** 이벤트가 이미 맡은 처리를 추적한 뒤, 두 저널에 필요한 전쟁 종료·승패·정국 정리 역할을 확정한다. 중복 효과 없이 빈 완료 처리를 보완한다.
- **완료 기준:** 청 승리, 공화국 승리, 청의 만주 몽진 각각에서 저널과 관련 변수가 일관되게 종료·정리된다.
- **근거:** [신해혁명 일지 두 개](../common/journal_entries/eafp_00_warlord_china.txt#L390), [혁명 이벤트](../events/warlord_china_events.txt).

### A05. 조선 — 세도정치의 날치기 제정 [P2, 현재 강제 차단]

- **현재 상태:** 세도정치 무작위 분기에 `#날치기 제정 TODO`가 남아 있고, 조건에 `always = no`가 있다. 핵심 효과 위치는 `#이펙트 = yes` 주석이며, 나머지는 48개월 쿨다운과 알림뿐이다.
- **남은 일:** 채택할 법률·권한·비용·반발 효과를 설계해 구현하거나 분기와 알림을 보류 상태로 정리한다. 차단 조건만 제거해서는 완성되지 않는다.
- **근거:** [세도정치 효과](../common/scripted_effects/eafp_korea_effects.txt#L1378).

### A06. 중국 — 태평천국 후방 반란 선동 버튼 [P2, 연결 미확인]

- **현재 상태:** `Incite_rebellion_in_the_rear_button`은 TODO가 붙은 활성 정의이지만, 다른 활성 스크립트에서 연결을 찾지 못했다. 내용도 후방 반란 생성이 아니라 향용 등장 조건, 향용 소집 수정치, `china_warlord_explosion` 0.25 감소를 사용한다.
- **남은 일:** 의도한 반란 선동 행동을 정의하고 기존 태평천국 일지에 연결할지, 사용하지 않는 초안으로 정리할지 결정한다.
- **근거:** [버튼 정의](../common/scripted_buttons/eafp_taiping_buttons.txt#L131).

## 3. 기획과 현재 코드 사이에 남은 작업

| ID / 우선순위 | 항목 | 현재 확인한 상태 | 남은 작업과 근거 |
| --- | --- | --- | --- |
| B01 / P2 | 일본 번벌 정치 | 법률과 `hanbatsu_oligarchy_events.1`은 존재하지만 이를 운영하는 활성 저널·호출은 확인되지 않음. 기존 이벤트는 마지막 원로의 죽음과 무효과 선택지뿐 | 기한, 중재·타협 행동, 후속 체제 준비 및 결말 구현. [설계안](hanbatsu_oligarchy_journal_plan.md), [기존 이벤트](../events/eafp_jap_events/eafp_hanbatsu_oligarchy_events.txt), [현재 문서의 구분](japan_content.md#civil-politics) |
| B02 / P2 | 일본 막부 개혁 리워크 | 현재는 네 하위 개혁 완료로 `eafp_japan.2999`를 호출하며, 무효화에도 `bakufu_kaikaku_complete_var`를 설정함. 계획의 공무합체·공의여론 동시 추진과 결과 분리는 미반영 | 두 성공 결말과 진짜 실패를 분리하고, 명예로운 유신·황실 혼인·하위 과제의 종료 순서를 조정. [설계안](bakufu_reform_journal_rework_plan.md), [현재 일지](../common/journal_entries/eafp_japan.txt#L225) |
| B03 / P2 | 만주 망명 조정 | 몽진 시 황실 이전과 `imperial_family_exiled` 설정은 구현됨. 계획의 `je_manchu_exile_court` 정의는 없음 | 망명 조정 안정화, 외세 후견, 복벽·입헌·만주 국가화·퇴위 중 채택할 후속 경로를 구현. [구상](imperial_family_exiled_manchuria_content_plan.md), [몽진 처리](../events/warlord_china_events.txt#L806), [기존 만주 일지](../common/journal_entries/eafp_chinese_rule.txt#L72) |
| B04 / P2 | 조청전쟁 평가 개편 | 독립전쟁 일지, 주간 전쟁 지지 추적, 승패 이벤트는 활성 구현. 계획의 `eafp_joseon_qing_war_evaluation_progress_bar`는 활성 정의·참조가 없고 현재 저널에는 `status_desc`가 남아 있음 | 현재 전쟁 지지 방식 유지 여부를 먼저 정한 뒤, 계획을 채택한다면 월간 종합 평가 막대와 결말 조건으로 전환. [개편안](../scratch/joseon_qing_war_journal_design_plan.md), [현재 일지](../common/journal_entries/eafp_joseon_qing_war.txt), [승패 이벤트](../events/eafp_kor_events/eafp_joseon_qing_war_events.txt) |

## 4. 현지화·서술의 미완성

### 4.1 활성 경로에서 실제로 쓰는 TODO 문구 [P1]

다음 다섯 키는 한국어·영어·중국어 간체 파일 모두 값이 `TODO`다. 주석에만 TODO가 있는 경우와 구분했다.

| 키 | 현재 연결 | 필요한 작업 |
| --- | --- | --- |
| `CHI_missionaries.16.f` | [태평천국 선교사 사건](../events/heavenly_kingdom_events.txt#L2632), 태평천국 일지의 무작위 후보 | 사건 배경 서술 작성 |
| `boxer_rebellion_events.106.a` | [의화단 진압 완료 사건](../events/boxer_rebellion_events.txt#L1002), 청이 열강 편을 드는 일지에서 호출 | 선택지 문구 작성 |
| `chinese_westernization.463.f` | [민간 조폐 금지 사건](../events/eafp_chi_events/eafp_chinese_westernization_events.txt#L4027), 개혁 버튼에서 호출 | 사건 배경 서술 작성 |
| `je_provisional_presidency_ysk_goal` | A03의 위안스카이 일지 | 실제 목표 구현 후 목표 설명 작성 |
| `je_provisional_presidency_sys_goal` | A03의 쑨원 일지 | 실제 목표 구현 후 목표 설명 작성 |

현지화 원본: [한국어](../localization/korean/eafp_china_l_korean.yml), [영어](../localization/english/eafp_china_l_english.yml), [중국어 간체](../localization/simp_chinese/eafp_china_l_simp_chinese.yml).

### 4.2 문장은 있으나 재작성 표시가 남은 부분 [P2]

- [조선 해외 사절단 한국어 문구](../localization/korean/eafp_korean_foreign_mission_l_korean.yml#L33): `.2`~`.6`의 서술·선택지와 `.10`~`.15`, `.17`, `.18`의 서술 등에 `AI작, 수정 필요, TODO` 표시가 있다. 사절단 기능은 이미 구현되어 있으므로 문체·고증 검수 과제로 취급한다.
- [조선 철도 개혁 서술](../localization/korean/eafp_korean_reformation_l_korean.yml#L170): `eafp_korean_reformation_events.302.f2`에 TODO가 남으며 영어·중국어 간체에도 대응 주석이 있다.
- [중국 사건 문구](../localization/korean/eafp_china_l_korean.yml): `opium_wars.103.f`, `CHI_missionaries.14.t`, `chi_flavor.205.t`, `.206.t`, `chinese_westernization.299.t`, `.305.t` 등은 값이 존재한다. TODO 주석만으로 사건 미구현이라 판단하지 말고 작성 의도를 확인한다.

### 4.3 보관·비활성 콘텐츠의 문구 [P3]

- `concept_concession_desc`, `je_concessions_in_china_status_breakdown`: 조계지 콘텐츠의 설명 TODO. 전용 시스템의 비활성 상태와 함께 정리한다.
- `eafp_japan.1021.f`, `.1023.f`, `.1099.d`, `.1099.a`: 세 언어에 TODO가 남지만 해당 활성 이벤트 정의는 확인되지 않았다. 현재 일본 사건 파일에는 `.1021`, `.1023`이 없다는 주석도 있다. 활성 화면의 문구 결함으로 단정하지 않는다.
- `je_korean_seowon`: 세 언어에 이름·설명·목표가 있으나 활성 저널 정의는 찾지 못했다. 독립 콘텐츠를 추가할지, 기존 개혁에 통합된 옛 문구인지 결정해야 한다.
- 모든 빈 문자열을 일괄 채우지 않는다. 숨김 이벤트 선택지나 조건부 상태 표시를 위한 의도적인 공백일 수 있다.

## 5. 부분 구현·임시 조건·밸런스·자산 보완

| ID / 우선순위 | 항목 | 확인한 내용 | 후속 작업 / 근거 |
| --- | --- | --- | --- |
| C01 / P2 | 서태후 사건군 | 월간 `random_events`가 `100 = 0`과 TODO뿐. 쿠데타 `.5`의 trigger도 TODO. 다만 쿠데타 수치 갱신, 수치 1에서의 호출, 개혁 지지 `.6` 정기 호출은 존재 | 무작위 사건을 추가할지 정하고 쿠데타의 호출 조건과 이벤트 자체 검사를 정리. 전체 서태후 시스템 미구현으로 보지 않음. [일지](../common/journal_entries/eafp_dowager_cixi.txt#L85), [쿠데타](../events/eafp_chi_events/eafp_dowager_cixi_events.txt#L190) |
| C02 / P2 | 일본 개혁·막부 권위 수치 | 네 개혁 완료 수정치의 권위 월간 +5에 밸런스 TODO. 파벌 막대의 `divide = -50`, 이해집단 기여 `multiply = 1`에도 TODO | 정치 결말 소요 시간과 네 과제 동시 완료 시 누적 효과 측정. [수정치](../common/static_modifiers/EAFP_japan_modifiers.txt#L304), [파벌 막대](../common/scripted_progress_bars/eafp_bakufu_kaikaku_progress_bars.txt), [기여 계산](../common/scripted_effects/eafp_japan_effects.txt#L1602) |
| C03 / P2 | 일본 인사 영향력 | 인사 처리의 ±25 변화량에 TODO가 남음 | 중복 증감과 직위 교체 시 영향력 수명 확인. [on_action](../common/on_actions/japan_code_on_actions.txt#L350) |
| C04 / P2 | 일본 외교 요구 반응 | `japan_on_diplomatic_demand`가 상대의 `ai_strategy_economic_imperialism` 보유 여부를 임시 조건으로 사용 | 실제 외교 요구의 종류와 플레이어·AI 양쪽 적용 여부 확인. [임시 조건](../common/on_actions/japan_code_on_actions.txt#L858) |
| C05 / P2 | 정한론 진입 조건 | 비활성 표시 조건의 `japan_restoration_complete`에 임시 TODO. 실제 `possible`은 반조선 로비 검사 | 유신 결말별 접근 가능 시점과 로비 생성·소멸 시 동작을 정리. [정한론 일지](../common/journal_entries/eafp_japan.txt#L1097) |
| C06 / P2 | 중국 분열·만한 갈등 수치 | 분열 월간 수치 -0.0001/-0.0002, 만한 갈등 계산 계수 -0.02/-0.025/+0.025 및 0.1에 수치조정 TODO | 평시·위기·AI 플레이의 장기 추이를 측정하고 계수 확정. [중국 분열](../common/journal_entries/eafp_00_warlord_china.txt#L44), [만한 계산](../common/scripted_effects/eafp_manchus_and_han_effects.txt#L956) |
| C07 / P2 | 일본 사건 금액 | 일부 사건의 `multiply = 2000`에 TODO가 반복됨 | 국가 규모별 비용·보상이 적절한지 확인. [일본 사건](../events/eafp_jap_events/eafp_japan.txt#L4808) |
| C08 / P3 | 조선 후기 섭정 | 1925년 이후 임의 인물 생성·교체 분기에 TODO가 남음. 생성·교체 효과 자체는 존재 | 장기 군주정 플레이에서 역사 인물 소진 뒤 승계 방식을 확정. [생성](../common/scripted_effects/eafp_korea_effects.txt#L366), [교체](../common/scripted_effects/eafp_korea_effects.txt#L517) |
| C09 / P3 | 조선 전립 자산 | 장군 전립 `_04`가 병졸 전립 `_03_entity`를 공유하며 구분 추가 요청 주석이 남음 | 자산 분리 또는 공유 의도 확정 후 초상화 확인. [모자 정의](../gfx/portraits/accessories/eafp_headgear.txt#L28) |
| C10 / P3 | 사건 미디어·인물 조사 | 자유민권운동·대만 원정의 영상 지정, 중국 개혁 사건 파일 말미의 캉유웨이 조사 주석 등에 TODO가 남음 | 연출 교체와 인물 조사 범위를 별도 결정. [민권운동](../events/eafp_jap_events/eafp_liberty_civil_right_movement_events.txt#L58), [대만 원정](../events/eafp_jap_events/eafp_formosa_expedition_events.txt#L48), [조사 메모](../events/eafp_chi_events/eafp_chinese_westernization_events.txt#L4235) |

## 6. 보류·비활성 콘텐츠 목록

점검 시 `.disable` 파일은 50개였다. 아래는 대표적인 콘텐츠 단위 분류이며, 파일 수를 미완성 기능 수로 세지 않는다.

| 항목 | 비활성 근거 | 처리 방향 |
| --- | --- | --- |
| 중국 조계지 운영 시스템 | [조계지 저널](../common/journal_entries/eafp_concessions_in_china.disable), 계산 저널, 이벤트, 버튼, GUI, scripted GUI, on_action이 `.disable` | 재개한다면 관련 파일을 함께 검토하고 현행 조약·외교 체계와 통합. 옛 이벤트의 `multiply = 1 # TODO`도 재조정 |
| 중국 지정은 | [지정은 저널](../common/journal_entries/eafp_didingyin.disable) | 계산에 사용한 `NDefines.NEconomy.TRADE_ROUTE_ECONOMY_OF_SCALE_MAX_LEVEL`에 작동 여부 확인 TODO. 현행 경제 모델 적합성부터 확인 |
| 중국 신문화운동 | [신문화운동 저널](../common/journal_entries/eafp_new_culture_movement.disable) | `new_culture_movement_progress_bar` 선언과 `positivist_progress_bar` 완료 검사가 혼재하는 초안. 복원 전에 진행도·사건·결말 체계를 확정 |
| 동아시아 헌법 | [헌법 이벤트](../events/eafp_eastasian_constitution_events.disable) | 조선 군민동치 등 현행 제도 개혁과 역할 중복을 먼저 판단 |
| 조선 정일론 | [정일론 저널](../common/journal_entries/je_jeongillon.disable), 대응 진행도 막대 `.disable` | 구판 이벤트 참조를 포함한 별도 보류 콘텐츠. 현재 조선 개혁·해외 팽창 경로와 통합 여부 결정 |
| 베트남의 옛 캄보디아 상태 저널 | [비활성 초안](../common/journal_entries/eafp_revolt_in_vietnam.disable) | 프랑스 왕당파 효과·문구를 사용하는 초안이 남음. 현재 활성 [크메르 문제](../common/journal_entries/eafp_vietnam_journal.txt)와 구분하고 대체·폐기 여부 판단 |
| 일본 구판 저널·이벤트·인물·GUI | 메이지 유신, 보신전쟁, 자유민권운동, 정한론, 가라후토, 대만 원정 등에 `.disable` 존재 | 같은 기능의 활성 `.txt`가 다수 있으므로 구판 파일만 보고 복원 과제로 만들지 않음 |
| 몽골 일부 자산 구상 | [이관 판정](mongolia_content_implementation_plan.md#L717)의 홉스굴호 주 특성과 몽골 모자 정의가 보류 | 기능·적용 주·사료·초상화 검수 조건이 충족될 때 재검토 |

## 7. 구현은 있으나 검증·문서 동기화가 남은 부분

| 항목 | 확인 수준 | 남은 확인 |
| --- | --- | --- |
| 조선 쟁탈전 | [설계안](../scratch/scramble_for_korea_journal_design_plan.md#L3)에 2026-10-13 구현 및 정적 검증 완료, 게임 실행 미검증 명시. 활성 [일지](../common/journal_entries/eafp_scramble_for_korea.txt)와 이벤트 존재 | 관여국 추가·이탈, 국가별 GUI 행·스크롤, 동률 100, 조선 독립·승인 승리, 종주국 변경, 콜백 순서, DLC 호환성과 밸런스 |
| 몽골 젭춘담바·복드 칸 | [계획 문서](mongolia_content_implementation_plan.md#L326)에 게임 내 실행 검증 미완료 명시 | 새 게임·기존 저장, busy 해제와 불사 유지, 1836 초상화, 1843/1850/1874 교체, 독립 시 즉위, 공화정 전환, 1924 종료, 장군부 법 복귀 |
| 중국 용이변하 AI 개선 | [전용 경제 전략](../common/ai_strategies/eafp_chinese_westernization_strategies.txt)이 존재. [정치 전략](../common/ai_strategies/eafp_political_strategies.txt#L174)에 해군 현대화 중 함대 보정, 국제 위상 중 외교 예외, 비군주정에서도 저널 유지 조건이 반영됨 | [옛 계획](../scratch/chinese_westernization_ai_strategy_plan.md)의 ‘전용 전략 부재’ 등을 현재 결함으로 재사용하지 말 것. 실제 완료 연도·남은 조건·부채·AI 전략 선택률을 관전자 플레이로 측정 |
| 태평천국 두 일지 개편 | [모래 위의 집·내부 갈등](../common/journal_entries/eafp_taiping_administration.txt)과 [진행도 막대](../common/scripted_progress_bars/eafp_taiping_progress_bars.txt)가 존재 | [계획](../scratch/taiping_journal_design_plan.md)을 미착수 목록에서 분리하고 열의 소진·내분·휴전·청 멸망 결과의 실제 흐름을 검증 |
| 조선 설명·효과 일치 | [조선 콘텐츠 문서](joseon-content.md#L787)에 군정 시정의 군적/관청 조건, 삼정 완료 변수의 미리보기/실행 차이, 정변 안정화 유지 기간, 대만 양도 거절 시 완료 등의 차이가 기록됨 | 이 표의 항목은 기존 문서가 제시한 재검증 후보다. 최신 코드와 실제 의도를 다시 대조한 뒤 문구 수정 또는 효과 수정 여부 결정 |
| 일본 새 콘텐츠 전반 | [현재 콘텐츠 문서](japan_content.md#reference)는 소스 흐름도와 게임 내 스코프·발생 빈도 검증을 구분함 | 정상·실패·무효화·내전·국가 태그 변경 시나리오의 실행 확인. 저장소의 과거 오류 로그를 현재 결함 확정 근거로 재사용하지 않음 |

## 8. 미완성 목록에서 제외한 오탐

- `eafp_00_boxer_rebellion.txt` 첫 줄의 ‘비활성화’는 바닐라 `REPLACE:je_boxer_rebellion`에 대한 주석이다. 같은 파일의 `je_boxer_rebellion_pre`, 열강 편·의화단 편 일지와 이벤트는 존재한다. 의화단 전체가 비활성이라고 쓰지 않는다.
- `warlord_china_events.6`의 TODO만으로 팔기군 측 몽진이 미구현이라고 판정하지 않는다. 항복·몽진 선택과 황실 이전 효과가 있으며, 미구현 구상은 B03의 **몽진 이후 전용 콘텐츠**다.
- [몽골 재작업본 비교](mongol_rework_content_comparison.md)의 오류 목록은 옛 별도 재작업본 비교 결과다. 현재 팩의 오류 목록으로 그대로 옮기지 않는다.
- 몽골 캬흐타 협정·자치 위기·인민혁명 등은 [2026-09-29 이후 삭제 결정](mongolia_content_implementation_plan.md#L682)에 따른 범위 제외다. 삭제된 기획을 반드시 복원해야 할 미완성으로 세지 않는다.
- 일본 종교·재벌은 구판 EAFP 파일이 비활성이어도 현재 문서상 바닐라 콘텐츠 경로를 사용한다. 구판 파일을 되살리는 것이 기본 후속 작업은 아니다.
- `Todo`·`Todoroki` 같은 일본 인명, 문법 참고 문서의 TODO/TBD, 셰이더 내부 메모는 콘텐츠 TODO에서 제외했다.
- 빈 월간 pulse만 있는 베트남 크메르 문제나 별도 시간 초과 처리가 있는 태평천국 보조 일지는 그것만으로 미완성 판정을 하지 않았다.

## 9. 권장 작업 순서

- [ ] **1차 — 활성 핵심 공백:** A01 간도, A03 임시대총통, A04 신해혁명 일지의 역할과 완료 경로 확정.
- [ ] **2차 — 플레이어 노출 문구:** 활성 TODO 다섯 키와 A01의 저널·버튼 문구 보완. 세 언어를 함께 확인.
- [ ] **3차 — 실행 확인:** 조선 쟁탈전·몽골 승계와 기존 조선 문서의 설명/효과 차이를 재현하고 결과 기록.
- [ ] **4차 — 계획 적용:** 번벌 정치·막부 개혁·만주 망명 조정·조청전쟁 개편의 채택 범위를 정해 기존 시스템에 연결.
- [ ] **5차 — 수치·조건:** 중국 분열·만한 갈등·일본 권위와 인사 수치, 정한론·외교 요구의 임시 조건 검증.
- [ ] **6차 — 보류물 정리:** 비활성 파일과 미사용 현지화의 유지·통합·폐기 결정을 문서화.

각 항목의 완료 판정에는 해당 콘텐츠의 진입, 정상 종료, 실패·무효화, 상태 정리, 현지화, 게임 실행 결과를 필요한 범위에서 기록한다. 이 점검표는 코드로 확인한 공백과 후속 검증 목록이며, 모든 런타임 결함을 포괄하는 전수 테스트 결과는 아니다.
