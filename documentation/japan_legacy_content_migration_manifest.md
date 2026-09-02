# 일본 옛 콘텐츠 이관 Manifest

이 문서의 “이관”은 `.disable` 원본을 활성 파일로 복원하고 정의·키·현지화를 재배치하는 파일 단위 작업만 뜻한다. 리뉴얼 이전 세이브를 변환하는 save migration은 계획·구현 범위에 포함하지 않는다.

## 1. 기준과 상태 값

| 항목 | 값 |
|---|---|
| 조사일 | 2026-09-01 |
| 원본 파일 | 일본 관련 `.disable` 53개 |
| 원본 합계 크기 | 2,312,731 bytes |
| 활성 목적 | script `.txt` 45개, localization `.yml` 7개, GUI `.gui` 1개 |
| 원본 보존 | `.disable` 직접 수정·삭제 금지 |

상태 값은 `무수정 복원`, `현행화`, `병합`, `ID 변경`, `명시적 삭제`를 사용한다. 1단계에서는 모든 행을 `무수정 복원`으로 만든 뒤 SHA-256 동일성을 확인한다. 이후 단계의 변경은 같은 행의 최종 상태와 별도 diff 기록에 추가한다.

## 2. 대상 선정

파일명·경로에서 일본 콘텐츠로 식별된 47개에 다음 간접 의존 6개를 추가했다.

- `common/scripted_progress_bars/eafp_bakuhantaisei_progress_bars.disable`
- `common/scripted_buttons/eafp_bakuhantaisei_buttons.disable`
- `common/scripted_guis/eafp_bakuhantaisei_sgui.disable`
- `gui/eafp_council_of_elders.disable`
- `localization/korean/unused/kurofune_l_korean.disable`
- `localization/korean/EAFP_traits_l_korean.disable`

공용 한국·중국 초상화나 다른 국가 콘텐츠는 일본 전용 참조가 확인되지 않아 대상에서 제외했다. 이후 참조 그래프에서 일본 전용 간접 의존이 추가로 확인되면 새 행으로 등록한 뒤 동일한 복원 절차를 적용한다.

## 3. 파일별 복원 기준선

| 원본 | 활성 목적 | bytes | 원본 SHA-256 | 1단계 상태 |
|---|---|---:|---|---|
| `common/character_interactions/eafp_jap_character_interactions.disable` | `common/character_interactions/eafp_jap_character_interactions.txt` | 20985 | `7e71ec33a568a431b3acf43c9cbfb2f0a70ac13ff76cf09adaf48c742788f37b` | 무수정 복원 |
| `common/character_templates/eafp_character_templates_JAP.disable` | `common/character_templates/eafp_character_templates_JAP.txt` | 7868 | `eea1c4406ebf2da45c763e5a749bb543fba327b134b4be8386f32970ec181faf` | 무수정 복원 |
| `common/character_templates/EAFP_japan_character_templates.disable` | `common/character_templates/EAFP_japan_character_templates.txt` | 513767 | `9f7346b40cda4e35890b791527444740de2327a8563902b2747dc847305b51c6` | 무수정 복원 |
| `common/company_types/eafp_companies_japan.disable` | `common/company_types/eafp_companies_japan.txt` | 12492 | `575383c51f7774dec2a1a884e6deae9d2c4b9b669da09601389d71b6e7e45129` | 무수정 복원 |
| `common/customizable_localization/eafp_JAP_custom_loc.disable` | `common/customizable_localization/eafp_JAP_custom_loc.txt` | 4607 | `22e7c565d165da6558abeea0c9a67daa9a0ee87fa0cc78687c83f064e9daa712` | 무수정 복원 |
| `common/decisions/eafp_00_japan_shinto.disable` | `common/decisions/eafp_00_japan_shinto.txt` | 588 | `5469fbccb772929742456b92b9d39aa08b6a8f7b433a9d08da5a9f3ffb3d5563` | 무수정 복원 |
| `common/effect_localization/eafp_japan_effects_loc.disable` | `common/effect_localization/eafp_japan_effects_loc.txt` | 1492 | `ae05a2130df02c51afba0e5930f061b2cc19b6cefc96c82b419db72a46c9a741` | 무수정 복원 |
| `common/flag_definitions/eafp_jap_flag_definitions.disable` | `common/flag_definitions/eafp_jap_flag_definitions.txt` | 2423 | `462fecb505a92bc5bf1672830143b07e7256860f2e667dea36651b74c8fa9142` | 무수정 복원 |
| `common/history/buildings/jap_building.disable` | `common/history/buildings/jap_building.txt` | 2920 | `9a69506f37601039c27bb9fd62b68624557dac6d228a55f3c2c84317ae2a6260` | 무수정 복원 |
| `common/history/characters/jap - japan.disable` | `common/history/characters/jap - japan.txt` | 3305 | `098f7fee6d5efc866535d2b867ecbe98cb69dc6baa89f36986ce9950f98cc17f` | 무수정 복원 |
| `common/history/countries/jap - japan.disable` | `common/history/countries/jap - japan.txt` | 5422 | `f808b480104bfb8d67fcc45dc3933b738abbce5a61f6d54e72da7e5e00487931` | 무수정 복원 |
| `common/history/countries/ryu - japan.disable` | `common/history/countries/ryu - japan.txt` | 927 | `095cab84ef0149a9f81396fb42af33dd0e3fb1bb6ad2a7886e871f260cef0a75` | 무수정 복원 |
| `common/history/diplomacy/jap_relation.disable` | `common/history/diplomacy/jap_relation.txt` | 243 | `95fb31e674fe5816f951c780a4540625dcb2d76095e0ece1d4edd4abbe12b2f0` | 무수정 복원 |
| `common/history/pops/99_jap.disable` | `common/history/pops/99_jap.txt` | 981 | `4da29981bac82c97bf718fc6936e6b08c9e5bb2240a3c436d3671805d51a6965` | 무수정 복원 |
| `common/journal_entries/eafp_00_meiji_restoration.disable` | `common/journal_entries/eafp_00_meiji_restoration.txt` | 6828 | `7ad17dbee0b3d0d1f83a5c45035413f55e876ccb89005a5554533f5ab4e576e6` | 무수정 복원 |
| `common/journal_entries/eafp_bakufu_seisaku.disable` | `common/journal_entries/eafp_bakufu_seisaku.txt` | 17284 | `929e6b91155923cc65a6f348dee9af3aba41d434fc68b1345f17720f6896971e` | 무수정 복원 |
| `common/journal_entries/eafp_japan.disable` | `common/journal_entries/eafp_japan.txt` | 65105 | `8ca986e6f09f0d790e5180299b1cd62b44d8608c8d34e0afdb43192b549b9ac4` | 무수정 복원 |
| `common/messages/eafp_jap_messages.disable` | `common/messages/eafp_jap_messages.txt` | 2274 | `df8074b143462008eb5125c65ade093acbd1486c86dce15f61c0d811dc7cd74e` | 무수정 복원 |
| `common/on_actions/japan_code_on_actions.disable` | `common/on_actions/japan_code_on_actions.txt` | 37644 | `d0a286c55249ed205cd6a76d0afc01636953ff1d7245ade687e9392d6eecaae7` | 무수정 복원 |
| `common/script_values/earp_jap_values.disable` | `common/script_values/earp_jap_values.txt` | 11166 | `b5f5b347427c25de317e877bd46b0ccb6cd6825bc1cdf9b2978f617658af5058` | 무수정 복원 |
| `common/scripted_buttons/eafp_bakuhantaisei_buttons.disable` | `common/scripted_buttons/eafp_bakuhantaisei_buttons.txt` | 13537 | `76bf74a92d756dd2c4ccb9f14e0016fdcc006c3ed0760ce5643e7a33d13990fb` | 무수정 복원 |
| `common/scripted_buttons/eafp_japan_buttons.disable` | `common/scripted_buttons/eafp_japan_buttons.txt` | 10089 | `a9f6614c2824c5f3e62ecb4dff277c2bc5e73bb69cc1d27366644e7d5ae8a62e` | 무수정 복원 |
| `common/scripted_buttons/eafp_tenpo_famine_buttons.disable` | `common/scripted_buttons/eafp_tenpo_famine_buttons.txt` | 12045 | `310a422b8aeedd0782a4b821e0010258f73ec69290cb5de91bf180710658732d` | 무수정 복원 |
| `common/scripted_effects/eafp_japan_effects.disable` | `common/scripted_effects/eafp_japan_effects.txt` | 52789 | `539e5368e928f37e4ecd2710f3ba800b9e1e41f6105ae47965d93d99ce77ebfe` | 무수정 복원 |
| `common/scripted_guis/eafp_bakuhantaisei_sgui.disable` | `common/scripted_guis/eafp_bakuhantaisei_sgui.txt` | 7595 | `63e4cc7504acb6c7a3cf81b0619cf9f1579c326a58c3c44c8560f6d8890bbae1` | 무수정 복원 |
| `common/scripted_progress_bars/eafp_bakufu_kaikaku_progress_bars.disable` | `common/scripted_progress_bars/eafp_bakufu_kaikaku_progress_bars.txt` | 2342 | `265036fed7d4529217da2c2db8bb58e799eb78031ecf1d076ee65087f6a87ff2` | 무수정 복원 |
| `common/scripted_progress_bars/eafp_bakuhantaisei_progress_bars.disable` | `common/scripted_progress_bars/eafp_bakuhantaisei_progress_bars.txt` | 23787 | `3db69960ed4147e26eaeca6dccab194ebe2c2d086fada2d443d749953234368c` | 무수정 복원 |
| `common/scripted_progress_bars/eafp_formosa_expedition_progress_bars.disable` | `common/scripted_progress_bars/eafp_formosa_expedition_progress_bars.txt` | 445 | `dc9c198f1a76e3077d4b40fb1bccf170e660578dca8bc172c44710bdf3424d1b` | 무수정 복원 |
| `common/scripted_progress_bars/eafp_hokkaido_progress_bars.disable` | `common/scripted_progress_bars/eafp_hokkaido_progress_bars.txt` | 506 | `2bfe1a336a65c38f643ed89576d5714ec41eb68257665732be8565d643bbb5c3` | 무수정 복원 |
| `common/scripted_progress_bars/eafp_shinto_progress_bars.disable` | `common/scripted_progress_bars/eafp_shinto_progress_bars.txt` | 3428 | `b15aedd7a4a7b6cf1925dac6a05be1d98d434599120be46b272e3f03297b7e89` | 무수정 복원 |
| `common/scripted_triggers/eafp_jap_triggers.disable` | `common/scripted_triggers/eafp_jap_triggers.txt` | 1224 | `bbb19a1f6ce82f234f28863e992fbacd75fd40c3ee75925ba15d5b38758dc616` | 무수정 복원 |
| `common/static_modifiers/EAFP_japan_modifiers.disable` | `common/static_modifiers/EAFP_japan_modifiers.txt` | 31276 | `c12cdf27328fc42c70c167d753ad2c9af157d82e28eafa8b6158f6650cc490a3` | 무수정 복원 |
| `common/trigger_localization/eafp_japan_trigger_loc.disable` | `common/trigger_localization/eafp_japan_trigger_loc.txt` | 1270 | `8ae1d46c53c896b85ed05cb30e73651c34122302e6c358a78f186bd6347374d1` | 무수정 복원 |
| `events/eafp_jap_events/eafp_boshin_war.disable` | `events/eafp_jap_events/eafp_boshin_war.txt` | 39514 | `e1c15d27754d7359b9d0cbfe0badfaa26c80af9e49b1913759430a9ef829d517` | 무수정 복원 |
| `events/eafp_jap_events/eafp_formosa_expedition_events.disable` | `events/eafp_jap_events/eafp_formosa_expedition_events.txt` | 1248 | `2b286fa727974979b4441c1635dcb7b6c9db4ba830037988e6df7834dae20009` | 무수정 복원 |
| `events/eafp_jap_events/eafp_hanbatsu_oligarchy_events.disable` | `events/eafp_jap_events/eafp_hanbatsu_oligarchy_events.txt` | 596 | `0adcb233baf3db9ba8219754c98f0a69c9fe8d901e994aaac9da098824bdf971` | 무수정 복원 |
| `events/eafp_jap_events/eafp_hokkaido.disable` | `events/eafp_jap_events/eafp_hokkaido.txt` | 6111 | `97d8a25434277c1bb83120b889b8a74a5439c75e84645d1f81bbecc0bbadf7d5` | 무수정 복원 |
| `events/eafp_jap_events/eafp_japan.disable` | `events/eafp_jap_events/eafp_japan.txt` | 184241 | `8e6bfd60c052d16ee149f7f9d59c7e4193eb5326efffb0dbb207e9d1111ad6f9` | 무수정 복원 |
| `events/eafp_jap_events/eafp_karafuto_events.disable` | `events/eafp_jap_events/eafp_karafuto_events.txt` | 1136 | `78b07d407e86b6be657c6055f4650ee5c443ac96c1481c6429e027bf3708aa04` | 무수정 복원 |
| `events/eafp_jap_events/eafp_liberty_civil_right_movement_events.disable` | `events/eafp_jap_events/eafp_liberty_civil_right_movement_events.txt` | 13963 | `f95b1aa8319ccd5fb92f92e50be748e75f2a88f497dbd343b3f18e5f6379d0b6` | 무수정 복원 |
| `events/eafp_jap_events/eafp_seikanron_events.disable` | `events/eafp_jap_events/eafp_seikanron_events.txt` | 21585 | `dafbacc30955c587fb07c6e18a9c8969f8a870fc40ef631fa0d1c9883fc942c8` | 무수정 복원 |
| `events/eafp_jap_events/eafp_shinto_events.disable` | `events/eafp_jap_events/eafp_shinto_events.txt` | 2591 | `e786afcc01603b925369f04e555d147d0ff11ef2ee2ccaea9342de5758c69157` | 무수정 복원 |
| `events/eafp_jap_events/eafp_tenpo_famine_events.disable` | `events/eafp_jap_events/eafp_tenpo_famine_events.txt` | 8371 | `2ab4120deaf659aaf9c8bdd91ce80c7d11cf337c1fd04d80f18ca92d11ffea14` | 무수정 복원 |
| `events/eafp_jap_events/eafp_zaibatsu_events.disable` | `events/eafp_jap_events/eafp_zaibatsu_events.txt` | 8229 | `b34ad8c7f3c8de19e66861d73412b10b0f08f740c864ee1e912880fae025698e` | 무수정 복원 |
| `events/meiji_restoration.disable` | `events/meiji_restoration.txt` | 34984 | `98281ca54507aa4efbcea92e70cd92d9a00847f2eefb8137958e3cb869fcb8b3` | 무수정 복원 |
| `gui/eafp_council_of_elders.disable` | `gui/eafp_council_of_elders.gui` | 8789 | `aea188717d1784e063bed266851514d54e7d45b5b9327d07cd78a2dcbfbf9617` | 무수정 복원 |
| `localization/english/eafp_japan_l_english.disable` | `localization/english/eafp_japan_l_english.yml` | 204541 | `32afa795e492e16da628d369756576da5fadef258faf1c1b7af126febb547939` | 무수정 복원 |
| `localization/korean/eafp_japan_l_korean.disable` | `localization/korean/eafp_japan_l_korean.yml` | 214684 | `b9422045dfb56140c153777c668f97ae153ca7ad2745419f0e8d5d46c10cacb1` | 무수정 복원 |
| `localization/korean/EAFP_traits_l_korean.disable` | `localization/korean/EAFP_traits_l_korean.yml` | 430788 | `4064e4b966ee3d11a68410e14eb27e31fa3fc6e05b8a4d6260fc606cced85863` | 무수정 복원 |
| `localization/korean/japan_historical_names_l_korean.disable` | `localization/korean/japan_historical_names_l_korean.yml` | 54754 | `a4370365116f158fdc567b99dbcb7f8863f1b889ab696c59ba724ddc231d92c3` | 무수정 복원 |
| `localization/korean/replace/jap_replace_l_korean.disable` | `localization/korean/replace/jap_replace_l_korean.yml` | 882 | `ec478c8bd685203a26f5a7cbb8d9d64fa87450e647eb84c3e1728ab1abd6a539` | 무수정 복원 |
| `localization/korean/unused/kurofune_l_korean.disable` | `localization/korean/unused/kurofune_l_korean.yml` | 20975 | `65a09a8838408c09ccfda34f4e32cb7e0464ab4e3f64a04b0515877f3c8be6cb` | 무수정 복원 |
| `localization/simp_chinese/eafp_japan_l_simp_chinese.disable` | `localization/simp_chinese/eafp_japan_l_simp_chinese.yml` | 176095 | `1a0d7de658482033b7351e821698d1bb4bb532bcd1dda8fa0f6c4f116febe78e` | 무수정 복원 |

## 4. 콘텐츠 수량 기준선

| 항목 | 수량 | 처리 원칙 |
|---|---:|---|
| 비활성 JE 정의 | 44 | 22개 활성·최신화, 22개 삭제·바닐라 병합 (`je_terakoya`·옛 `je_hokkaido`·옛 재벌 JE 4개 포함) |
| 활성 재정의 JE | 1 (`je_ryukyu_rivalry`) | 바닐라 소유로 돌리고 EAFP 조선 개입 분리 |
| 비활성 이벤트 | 156 | 활성·재배치·흡수·삭제 중 하나로 추적 |
| 영어 주 현지화 | 1,447 | 원문 중심 복원 후 삭제 전용 키 정리 |
| 한국어 주 현지화 | 1,459 | 원문 중심 복원 후 삭제 전용 키 정리 |
| 중국어 간체 주 현지화 | 1,447 | 원문 중심 복원 후 삭제 전용 키 정리 |
| 한국어 역사명 | 1,586 | 바닐라 중복 이름만 대조 |

명시적 삭제·병합 22개는 지역 막번체제 JE 7개, 막부 정책·청원 JE 8개, 독립 `je_tenpo_famine` 1개, `je_terakoya` 1개, 옛 `je_hokkaido` 1개, 옛 `je_zaibatsu`와 재벌 청원 JE 3개로 고정한다. `je_terakoya`는 새 키로 이관하지 않으며 history 시작 호출과 전용 수정치·효과·트리거·현지화도 삭제 대상으로 추적한다. 옛 `je_hokkaido` 역시 새 JE로 이관하지 않고 history 시작 호출, `hokkaido_progress_bar`, 전용 버튼 4개를 삭제하되, 원본 `hokkaido.1-6`과 `je_karafuto`는 바닐라 `je_taming_the_north`의 진행·성공 상태에서 이어지도록 재배치한다. 옛 재벌 체인은 활성 `eafp_zaibatsu_events.txt`, `zaibatsu_events.1-4`, 고아 `.101` localization, `is_zaibatsu_company`, `zaibatsu_cooperation_modifier`까지 삭제하고 바닐라 `je_zaibatsu`와 공식 회사만 사용한다. 원본 `.disable` 파일들은 1단계 복원 증거와 회귀 대조를 위해 그대로 보존한다.

## 5. 검증 절차

1. 원본과 활성 목적 파일이 모두 존재하는지 확인한다.
2. 파일 크기와 SHA-256이 일치하는지 확인한다.
3. 원본 `.disable` 53개의 SHA-256이 이 표와 일치하는지 확인한다.
4. 최초 전면 복원 상태의 오류 보고서를 `documentation/japan_stage1_initial_load_report.md`에 기록한다.
5. 후속 수정은 활성 파일에서만 수행하고 원본은 회귀 대조본으로 유지한다.

## 6. 4단계 바닐라 기준선과 최종 분류

기준 게임 버전은 Victoria 3 1.13.11이며 모든 일본 관련 DLC가 활성인 환경만 지원한다.

| 바닐라 원본 | 원본 파일 SHA-256 | EAFP 활성 파일 | 활성 파일 SHA-256 | 상태 |
|---|---|---|---|---|
| `common/journal_entries/00_meiji_restoration.txt` | `aaaf94eb3c4acd16e2985381ef68f6cd1cf1ca8fa012002ad2305c24faa135d0` | `common/journal_entries/eafp_00_meiji_restoration.txt` | `4f56af7902b3d8d0b172a0203500e1a751c47a6f22275b8eb6bcb7c811249ee5` | 바닐라 5개 JE 전문 + 명시적 EAFP delta |
| `common/journal_entries/07_hokkaido.txt` | `867af26f75e9e3b4f90c603ddbf0e7b357eb57fb6b92ac0f7989b7756436724d` | `common/journal_entries/eafp_07_taming_the_north.txt` | `1f11e83ef110d84b7a92cdb2dacc710833a5c5cecd05106350b6a0f4a9ce7a6b` | 바닐라 전문 + 홋카이도·가라후토 후속 delta |
| `common/journal_entries/07_tenpo_crisis.txt` | `37e7bf5859dd585d512cfe0b39e7383765598b7e8b69d4d4bd48afbb76c90ac2` | `common/journal_entries/eafp_07_tenpo_crisis.txt` | `b59544ea914765a1412753c1e3d1efb8ca0fc803989e40e3929385452763f066` | 바닐라 전문 + 기근·파벌 delta |

각 활성 `REPLACE:` 블록에서 `EAFP DELTA BEGIN/END` 구간을 제거한 뒤 주석과 공백을 정규화하면 대응 바닐라 블록과 동일하다. 파일 SHA-256 차이는 `REPLACE:` 접두어, 설명 주석, EAFP delta 때문이다.

### 6.1 명시적 삭제

- 7개 지역 막번체제 JE와 지역 loyalty·independency·goryo 지원 자산
- 8개 막부 정책·청원 JE와 전용 시작 버튼·GUI·trigger localization
- 독립 `je_tenpo_famine`, `je_terakoya`, 옛 `je_hokkaido`
- 옛 재벌 JE·청원·사건
- `reduce_nidome*` 14개 버튼
- 바닐라 중복 EAFP 인물 템플릿 69개

### 6.2 재배치

- `tenpo_famine.1-6/.99` → `REPLACE:je_tenpo_crisis`
- `hokkaido.1-6`, `je_karafuto` → `REPLACE:je_taming_the_north`
- 정책 성공·실패 사건 `eafp_japan.2201-2233` → `eafp_japan.2302-2305` 직접 후속
- 지역 막번 사건 효과 → 저택 보유 magnate의 실제 loyalty
- 중복 인물 참조 → [바닐라 정본 매핑](japan_legacy_character_identity_map.md)

리뉴얼 이전 세이브에 대한 변수 변환, tombstone JE, migration on_action은 만들지 않았다.
