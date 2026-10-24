# 현재 error.log 재검토 — 2026-10-24 12:35 기준

## 후속 수정 현황

이 보고서 작성 뒤 사용자가 요청한 만주·GUI·모델 LOD·번역 중복 수정을 적용했다. 아래 로그 집계는 수정 전 스냅샷이며, 게임을 재실행한 결과는 아니다.

- 만주 네 반복문의 소유국 판정을 `limit`으로 옮겼다. `THIS`가 후보 주가 아닌 호출 국가를 가리키도록 `PREV = { PREV.owner = THIS }`로 비교한다. 반복문 이름과 기존 정착 조건·효과는 유지한다.
- 일반 container 네 곳의 고정 `size` 템플릿을 최소 폭 613으로 바꿔 내용에 따른 높이 계산을 유지했다. 기존 flowcontainer 설정은 유지했다. 본문 14인 헤더 두 정의의 최소 글자 크기는 12로 낮췄다.
- 에도성 한 개·경복궁 두 개 mesh 정의에서 추가 LOD 전환 설정을 제거했다. 기본 mesh만 사용하는 바닐라 Petra 설정을 대조했으며, mesh·재질·텍스처 파일 자체는 변경하지 않았다.
- 일본 인명 중복 정의 177개를 제거했다. 모든 고유 키와 각 키의 첫 정의 값을 보존했다. 서로 다른 표기가 섞인 21개 키도 첫 표기를 유지했다. 예: `kenjiro`는 켄지로, `matsudaira`는 마츠다이라.
- 몽골 국명 네 키는 한국어·영어·중국어 각각 기존 값 그대로 `replace/eafp_mongolia_names_l_*.yml`로 옮겼다. 새로운 게임 문구는 작성하지 않았다.
- 정적 확인 통과: 수정 모드 텍스트 15개의 BOM·CRLF·괄호, 소유국 조건 네 곳, GUI 크기·상속된 글자 크기, mesh 경로, 중복 제거 후 고유 인명 보존, 이동한 국명 값 보존, 제외 파일 및 정당 파일 무변경. `git diff --check`도 통과했다.
- 게임 내 만주 버튼 실행, GUI 렌더링, LOD 경고 소멸은 재실행 후 확인이 필요하다. 지정한 세 제외 항목은 유지했다.

## 기준과 범위

- 로그: `C:/Users/KHG/Documents/Paradox Interactive/Victoria 3/logs/error.log`, 96,185바이트, 마지막 기록 12:35:30.
- 분석 범위: 12:20:21~12:35:30, 597줄, 타임스탬프가 붙은 오류·경고 **585건**. 반복과 후속 검증 실패가 포함되므로 고유 결함 수가 아니다.
- 게임: 1.13.11. 활성 모드: CMF + EAFP. EAFP 로드 경로는 현재 저장소를 가리키는 심볼릭 링크다.
- 현재 소스 기준: Git `86bca008`, 분석 시작 시 작업 트리는 깨끗했다. 과거 수정 보고서와 달리 현재 정당은 `INJECT`이고 인명·국명 중복도 실제 파일에 남아 있다. 이번 보고서는 현재 파일과 새 로그를 기준으로 한다.
- **분석만 수행했다. 코드·번역·세이브·그래픽은 변경하지 않았다.** 새 문구를 추가했던 변경의 롤백 상태도 유지한다.
- **`building_gaudi_gyeong`, `rel:donghak`, 명품 도자기는 수정 대상에서 제외한다.** 해당 로그 6건은 집계에만 포함한다.

## 전체 분류

| 분류 | 기록 수 | 현재 판단 |
|---|---:|---|
| 세이브의 빈 참조 | 283 | 별도 세이브 문제 조사 |
| 번역 중복 | 185 | 일본 인명 177 + 몽골 국명 8 |
| 문구 누락·툴팁/GUI 문자열 | 34 | 신규 문구 작성 없이 목록만 관리 |
| 불필요한 일지 목표 번역 | 17 | 실제 참조와 표시 방식에 따라 정리 |
| 이벤트 ID 중복 | 24 | EAFP 의도적 override 23 + CMF 1 |
| 정당 동적 이름 병합 | 11 | 현재 소스에서도 원인 확인 |
| GUI 크기·글자 크기 | 8 | EAFP가 사용하는 바닐라 템플릿 조합 확인 |
| 만주 `Unknown effect owner` | 4 | 소유국 조건 위치 오류 |
| 모델 LOD | 3 | 이전 LOD 정리 후에도 지속 |
| CMF 중복 effect | 2 | 외부 모드 제공 파일 |
| 변수 사용 경고 | 2 | WCR·보신전쟁 기록 |
| 고립 이벤트 | 5 | 호출 없는 정의, 임의 발동 금지 |
| `PdxDebugConstants` | 1 | 엔진 진단, 원인 미확정 |
| 사용자 지정 제외 항목 | 6 | 변경하지 않음 |
| **합계** | **585** | |

## 우선 확인할 코드 오류

### 1. 만주 소유국 제한 — 4건, 가장 우선

로그 209, 236~237, 242행. 위치는 다음과 같다.

- `events/eafp_kor_events/eafp_kor_manchuria_events.txt:80`
- `common/scripted_buttons/eafp_kor_manchuria_buttons.txt:29`, `:112`
- `common/journal_entries/eafp_kor_manchuria_management.txt:115`

`random_state_in_dongbei`와 `every_state_in_dongbei` 자체는 이제 인식된다. 지역 정의도 `common/geographic_regions/eafp_geographic_regions.txt:1`에 존재한다. 문제는 이전 수정에서 `owner = THIS`를 반복 효과의 본문에 직접 넣은 것이다. 엔진은 이를 조건이 아니라 실행할 효과로 읽고 거부한다.

**수정 방향:** 요청한 반복문 이름은 유지하고 소유국 판정을 반복문의 `limit` 안에 배치해야 한다. 정착 버튼에는 이미 `limit`가 있으므로 그 안에 합치고, 나머지 세 곳에는 조건 블록이 필요하다. `THIS`가 실제 호출 국가를 가리키는지도 호출 스코프와 함께 검증해야 한다. 현재 소유국 필터는 유효하지 않으므로 타국 소유 주까지 영향을 받는지 실행 범위를 우선 점검한다. 이번에는 수정하지 않았다.

### 2. 정당 이름 병합 — 11건

로그 195~205행. `common/parties/eafp_parties.txt`의 정당 11개가 `INJECT`로 기존 `name.first_valid`와 별개의 `first_valid`를 추가한다. 엔진은 `There should be only one special desc`를 출력한다.

**수정 방향:** 기존 한국 정당 이름을 그대로 사용하면서 동적 이름 블록을 하나로 합친다. 기본 정당 이름 분기와 가입 조건·가중치·색상은 보존해야 한다. 오류를 없애기 위해 새 정당명이나 설명 문구를 만들 필요는 없다. 현재 파일의 시작 행은 1, 14, 27, 46, 60, 73, 86, 99, 113, 127, 140이다.

### 3. GUI 글자 크기·container 크기 — 새로 확인된 8건

로그 590~597행, 모두 12:35:30에 발생했다. 오류 위치가 바닐라 템플릿이라고 해서 바닐라만의 문제로 분류하면 안 된다.

- **글자 크기 4건:** `gui/shared/backgrounds.gui:240`의 `default_header`가 `elide_fontsize_min`을 사용한다. 해당 템플릿은 `fontsize_min = 14`이다. EAFP의 `gui/eafp_council_of_elders.gui:249`와 `gui/journal_entry_widgets/eafp_je_bakuhantaisei.gui:249`는 이 헤더의 `text_size`를 `fontsize_medium`으로 바꾸는데, 실제 값도 14다. 따라서 최소 크기와 본문 크기가 같아 `0 < fontsize_min < 14` 조건을 위반하는 조합이 확인된다. 사용하는 EAFP 헤더에서 최소 크기를 본문보다 작게 하거나 본문 크기를 조정하고 표시를 확인한다. 네 인스턴스 각각의 호출 경로까지 실행 추적한 것은 아니다.
- **container 크기 4건:** `gui/block_windows.gui:16`의 `sidepanel_plus_sidebar_size`에는 `size = { 613 0 }`가 있다. EAFP가 이 템플릿을 `container`에 적용하는 곳은 `gui/eafp_council_of_elders.gui:18`, `gui/eafp_eastasian_expansionism.gui:18`, `gui/journal_entry_widgets/eafp_je_bakuhantaisei.gui:18`, `:408` 등이다. 자식에 맞춰 크기가 정해지는 container에 고정 크기를 주는 것이 경고 원인이다. EAFP의 해당 사용처에서 고정 폭을 맡는 widget과 내용 container의 크기 규칙을 정리하고, 실제 네 경고를 만든 인스턴스를 확인한다.

### 4. 모델 LOD — 3건

로그 191~193행. 경복궁 mesh 두 인스턴스와 에도성 mesh 한 인스턴스에서 `has fewer LOD meshes than expected`가 남는다.

현재 asset에는 이미 `index = 0` 항목 하나만 남아 있다. 따라서 중복 LOD 항목을 또 제거하라는 이전 처방은 현재 상태에 맞지 않는다. mesh가 실제로 내보낸 LOD 수와 엔진이 `lod_percentages`로 요구하는 구조를 대조해야 한다. LOD 블록 생략 또는 mesh 재내보내기 중 어느 쪽이 맞는지는 뷰어/실행 확인 후 결정한다. 정확한 mesh 내부 원인은 아직 확정하지 않았다. `building_gaudi_gyeong` 참조 변경은 이 작업과 별개이며 제외한다.

## 번역과 표시 경고

### 중복 185건

- `localization/korean/japan_historical_names_l_korean.yml`: 중복되는 키 153종, 초과 정의 177개. 예를 들어 `kenjiro`가 69, 95, 780행에 존재하며 표기도 켄지로/겐지로로 다르다. 같은 키를 하나로 정리하되 충돌하는 기존 표기는 선택이 필요하다.
- `localization/english/eafp_mongolia_l_english.yml:33` 및 한국어 같은 파일 33행부터 국명 네 키가 바닐라와 중복된다. `dyn_c_great_mongolian_state`, 그 형용사, `dyn_c_mongolian_peoples_republic`, 그 형용사다. 기존 번역을 보존한 의도적 교체라면 `replace/`로 옮기는 방법을 검토한다.

### 누락·잘못된 문자열 34건

사용자가 새 문구 추가를 롤백했으므로 아래 항목은 **미해결 목록만 작성**했다. 먼저 기존 번역 키의 오타·이름 불일치와 비활성 콘텐츠 여부를 확인해야 한다.

- 동아시아 팽창주의 GUI: `je_eastasian_expansionism_country_owns_entire_strategic_region_tt`, `je_eastasian_expansionism_country_or_subject_owns_entire_strategic_region_tt`.
- 간도 버튼: `eafp_scripted_button_gando_ambition_gando_acquisition`, 그 `_desc`; 조건 툴팁 `war_with_china_not_korea_tt`, `owes_korea_obligation_tt`. 두 조건은 각각 후속 PostValidate 실패도 출력하므로 단순 이름 누락보다 우선 확인한다. 위치는 `common/scripted_buttons/eafp_korean_reformation_buttons.txt:183`, `:184`, `:223`, `:231`.
- 진행 막대: `new_culture_movement_progress_bar`, 그 `_desc`.
- 인물 특성: `kor_hwan_slot_1`~`kor_hwan_slot_6`.
- 일지 목표: `je_chinese_missions_goal`, `je_chinese_educational_mission_goal`, `je_reconstruct_summer_palace_goal`.
- 일지 제목·사유: `je_xinhai_revolution`, `je_xinhai_revolution_kmt`, `je_gando_ambition`, `je_scholar_bureaucrats` 및 각각의 `_reason`; `je_hui_revolt_pre_reason`.
- 디버그 사건: `events/eafp_debug.txt:108`, `:109`와 선택지의 직접 문자열 세 개를 번역 키로 해석하면서 실패한다. 원래 직접 문자열로 롤백된 상태다.
- 바닐라 GUI: `INTEREST_TIER_MARKER_STRATEGIC_REGION`, `FLEET_NO_INTERCEPT_TARGETS`; `custom_tooltip.gui:8801`의 `#v [State.GetName]#!`는 누락된 이름이 아니라 `text`/`raw_text` 사용 문제다.

### 불필요한 일지 목표 번역 17건

로그 255~277행. 대상 `_goal`의 일지 ID는 `je_dowager_cixi`, `je_bakuhantaisei`, `je_bakufu_zaisei`, `je_formosa_expedition`, `je_korean_kings_health`, `je_yangjeon`, `je_korean_imsul_boom`, `je_king_cheoljong_education`, `je_korean_regent`, `je_korean_regent_inactive`, `je_sedo_politics`, `je_korean_confu`, `je_rlg_seoul_gyeongbokgung_poor`, `je_seoul_improvement_project`, `je_provisional_presidency_ysk`, `je_provisional_presidency_sys`, `je_eafp_taiwan_pioneer`다. 다른 문구에서 재사용 중인 키까지 일괄 삭제하지 말고, 실제 참조가 있으면 기존 내용 그대로 일반 툴팁 키로 분리하는 방식이 적절하다.

## 세이브·호환성·기타

- **빈 참조 283건:** 로그 306~588행, 12:21:33~12:21:35의 로드 구간. 파일명이 비어 있고 줄 번호가 수백만 단위다. 이전 조사에서 같은 줄 번호가 가리키는 세이브에 빈 `modifier`와 비활성 일지의 빈 `type`가 확인됐다. 이번에는 세이브를 다시 수정하거나 283개를 개별 복구하지 않았다. 같은 모드 조합의 새 게임과 기존 세이브 로드를 구분해 재현 여부를 확인해야 한다.
- **이벤트 중복 24건:** `events/000_eafp_japan_overrides.txt`의 일본 바닐라 override 23개와 CMF의 `regency.1` 한 개. ID 변경으로 경고만 없애면 기존 호출이 끊어질 수 있으므로 실제 우선순위와 override 동작을 확인한다.
- **CMF 중복 effect 2건:** `cmf_heir_blocker.txt`, `com_formation_event_blocker.txt`. 현재 로그는 마지막 effect를 사용한다고 명시한다. 외부 모드의 바닐라 효과 보존 여부를 별도로 확인한다.
- **고립 이벤트 5개:** `boxer_rebellion_events.4`, `eafp_ryukyu.4`, `chi_flavor.9`, `hanbatsu_oligarchy_events.1`, `eafp_japan.9`. 미완성/이전 경로가 섞여 있으므로 임의 발동 조건을 추가하지 않는다.
- **변수 경고 2건:** `WCR_westernized_nation`은 설정되지 않는다는 경고가 있지만 현재 EAFP·설치본·CMF의 활성 txt/gui 검색에서 경로를 찾지 못했다. 원인은 미확정이다. `boshin_war_happened`는 `events/000_eafp_japan_overrides.txt:323`, `:488`에서 설정되지만 활성 사용처가 없다는 경고다. 역사 기록의 필요성을 검토한 뒤 유지/정리한다.
- **엔진 경고 1건:** `PdxDebugConstants`의 원인은 현재 근거로 특정할 수 없다.
- **제외 6건:** `building_gaudi_gyeong` 두 위치의 본 오류와 후속 실패 4건, `rel:donghak` 1건, 명품 도자기 수 제한 1건. 수정하지 않는다.

## 이전 로그 대비와 작업 순서

이번 로그에는 대만 `formosa_survey_modifier` 제거 반복, 몽골 이해집단 지도자 지정 실패, 조계 외교전 구문 오류, 중국 청구권 스코프 오류, 잘못된 수정치·BOM 경고가 보이지 않는다. 해당 실행 경로가 모두 재현됐다는 뜻은 아니므로, 로그 부재만으로 기능 검증 완료를 선언하지 않는다.

우선순위는 **만주 소유국 필터 → 정당 이름 병합 → EAFP GUI 크기 규칙 → LOD 확인**이다. 번역 중복·일지 목표 정리는 기존 문구만 보존하면서 별도로 수행할 수 있다. 새 문구 작성과 세이브 복구는 구분해서 다룬다. 이번 재검토에서는 이 보고서만 추가했다.
