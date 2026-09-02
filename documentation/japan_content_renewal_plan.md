# 일본 콘텐츠 리뉴얼 구현 계획

## 0. 최신 구현 결정: EAFP 직접 소유

2026-09-01의 최신 구현 지시에 따라 bridge·바닐라 상태 동기화 전제를 폐기했다. 이 결정은 이 문서 아래쪽에 남아 있는 bridge, 바닐라 정본 소유, 호환 adapter 관련 과거 계획보다 우선한다.

- 지원 대상은 EAFP를 활성화한 상태로 시작한 신게임뿐이다.
- EAFP는 메이지 5개 JE와 `je_taming_the_north`를 `REPLACE:`로 로드하지만, 각 정의의 내용 기준선은 현행 바닐라 JE 전문이다. `REPLACE:`는 배포 수단이지 EAFP식 간이 JE를 새로 설계한다는 뜻이 아니다.
- 4단계에서 각 `REPLACE:` 블록을 바닐라 1.13.11 정의의 모든 필드·버튼·widget·공식 이벤트·완료/실패/무효화 결과를 먼저 그대로 옮긴 뒤 EAFP가 추가·수정한 부분만 명시적으로 병합한다.
- 실행 중에는 별도 bridge를 통해 바닐라 일본 JE의 활성 상태, 완료 변수, 진행 막대와 내부 modifier를 읽지 않는다. 다만 구현 시점의 바닐라 JE 소스는 `REPLACE:` 정의를 만드는 기준본으로 사용한다.
- bridge scripted trigger·effect와 월간 bridge on_action을 사용하지 않는다.
- 류큐 조선 개입은 바닐라 류큐 경쟁과 분리된 EAFP 자체 진행도를 사용한다.
- 이전 EAFP 저장에 대한 migration은 구현하지 않는다.

구현 결과와 현재 변수 계약은 [`japan_stage3_bridge_report.md`](japan_stage3_bridge_report.md)를 정본으로 삼는다. 이 문서의 기존 호환 계층 세부안은 결정 이력으로만 보존한다.

## 1. 문서 목적과 기준선

이 문서는 현재 `East-Asia-Flavor-Pack`에 남아 있는 옛 일본 콘텐츠를 Victoria 3의 현행 일본 콘텐츠, 특히 `The Great Wave` DLC와 충돌하지 않도록 재설계하기 위한 구현 계획이다. 이번 단계에서는 게임 스크립트나 자산을 수정하지 않고, 콘텐츠 소유권·이관 범위·호환 계층·구현 순서·검증 기준을 확정한다.

비교 및 구현 기준은 2026-08-30 현재 로컬 작업 폴더다.

| 항목 | 기준 |
|---|---|
| 대상 저장소 | `East-Asia-Flavor-Pack` |
| 대상 모드 버전 | `2.2.0` |
| 대상 게임 버전 | `1.13.*` |
| 검증한 로컬 실행 파일 버전 | Victoria 3 `1.13.11` |
| 검증한 Steam 빌드 | `24799966` |
| 검증한 로컬 게임 데이터 | `D:\SteamLibrary\steamapps\common\Victoria 3\game` |
| DLC 전제 | 모든 공식 DLC 설치, 일본 콘텐츠는 `The Great Wave`의 `ep2_content` 필수 |
| 지원 범위 | 전체 DLC 활성 환경만 지원·검증하며 DLC 비보유 환경은 고려하지 않음 |
| 주요 국가 태그 | `JAP`, `RYU`, `KOR`, `CHI` |
| 신규 식별자 접두사 | `eafp_jap_` / 이벤트 네임스페이스 `eafp_jap` |
| 기본 언어 | 한국어·영어·중국어 간체 동시 제공 |

현재 [`.metadata/metadata.json`](../.metadata/metadata.json)은 `supported_game_version = 1.13.*`로 설정되어 있다. 반면 [`README.md`](../README.md)의 일부 버전 표기는 이전 버전에 머물러 있으므로, 일본 리뉴얼 릴리스 시 메타데이터와 문서의 버전 표기도 함께 동기화한다.

이 계획은 다음 원칙을 전제로 한다.

> EAFP는 모드를 활성화한 신게임의 일본 저널 상태와 후속 결과를 직접 관리하고, 옛 저널·이벤트·현지화를 최대한 원형대로 복원한다.

옛 일본 `.disable` 파일은 이번 리뉴얼의 주 구현 원본으로 취급한다. 구현을 시작할 때 현재 비활성인 일본 관련 파일을 먼저 전부 활성 확장자로 복사한다. 게임 스크립트 파일은 같은 경로·같은 basename의 `.txt`로, localization 파일은 엔진 형식에 맞는 `.yml`로 되살린다. 이 “무수정 활성 복원본”을 기준선으로 고정한 다음에만 활성 복사본을 수정한다. 일부 정의가 최종 삭제 대상이더라도 해당 `.disable` 파일을 처음부터 제외하지 않고, 먼저 전체를 복원한 뒤 활성 `.txt` 또는 `.yml` 안에서 정의와 참조를 제거·병합한다.

기본 방침은 저널 구조, 이벤트 선택지, 이벤트 순서, 현지화 문구와 고유 효과를 그대로 보존하는 것이다. 다만 이 문서가 명시한 지역 JE 7개, 정책·청원 JE 8개, 독립 덴포 기근 JE와 중복 인물 정의는 활성 복원 후 삭제하며 재사용 가능한 서사만 새 소유자에게 이관한다. 그 밖의 수정은 현행 문법으로의 기계적 변환, 바닐라와 충돌하는 키의 이름 변경, 폐지된 주·스코프 교체, 바닐라 DLC가 이미 소유하는 완료 결과의 동기화에 한정한다.

## 2. 조사 결과 요약

### 2.1 옛 일본 콘텐츠

옛 일본 콘텐츠의 대부분은 `.disable` 상태로 남아 있다.

- [`common/journal_entries/eafp_japan.disable`](../common/journal_entries/eafp_japan.disable)
  - 막번체제, 홋카이도, 덴포 기근, 막부 개혁, 개국, 군제, 재정, 보신전쟁, 자유민권운동, 정한론, 신토, 재벌, 류큐, 가라후토, 대만출병을 포함한다.
- [`common/journal_entries/eafp_bakufu_seisaku.disable`](../common/journal_entries/eafp_bakufu_seisaku.disable)
  - 막부 정책과 개혁 관련 보조 저널을 포함한다.
- `events/eafp_jap_events/*.disable`
  - 막부 인사, 계승, 모리슨호 사건, 존 만지로, 개항, 지진, 보신전쟁, 덴포 위기, 홋카이도, 신토, 정한론, 자유민권운동, 재벌, 가라후토, 대만출병 등의 사건을 포함한다.
- [`events/meiji_restoration.disable`](../events/meiji_restoration.disable)
  - `meiji.1`부터 `meiji.13`까지 현재 바닐라와 동일한 이벤트 네임스페이스를 사용한다.
- `common/character_templates/*.disable`
  - 대량의 옛 일본 인물 템플릿을 포함한다.

확인된 원본은 비활성 저널 44개, 비활성 이벤트 파일 12개의 이벤트 156개, 영어·한국어·중국어 간체 주 현지화 약 4,300개 키, 한국어 역사명 1,586개 키다. 모두 이관 manifest에는 등록하지만, 이번 수정으로 지역 막번체제 JE 7개, 막부 정책·청원 JE 8개, 독립 `je_tenpo_famine` 1개, `je_terakoya` 1개, 옛 `je_hokkaido` 1개, 옛 재벌 JE와 재벌 청원 JE 3개를 활성 대상에서 제외한다. 결과적으로 비활성 저널 44개 중 22개를 활성 JE로 복원·최신화하고 22개는 삭제 또는 바닐라 JE에 병합한다. `je_bakufu_seisaku`라는 단독 최상위 JE는 원본에 존재하지 않으므로 이 명칭은 8개 하위 JE와 공용 지원 자산 전체를 가리키는 삭제 범위로 사용한다.

### 2.2 현행 바닐라 일본 콘텐츠

Victoria 3 1.13.11과 `The Great Wave`는 다음 일본 시스템을 이미 제공한다.

- `je_sakoku`: 쇄국과 개항
- `je_tenpo_crisis`: 덴포 위기와 오시오의 난
- `je_meiji_restoration` 및 `je_meiji_*`: 메이지 유신, 경제·군사·외교 과제
- `ep2_meiji.*`: 보신전쟁과 막부 말기 정치 사건
- `je_taming_the_north`: 홋카이도 개발과 북방 문제
- 에조 공화국·하코다테·고료카쿠 관련 사건
- `je_shinbutsu_bunri` / `je_elevate_buddhism`: 종교 정책
- `je_zaibatsu`: 재벌 형성
- `je_ryukyu_rivalry`: 류큐를 둘러싼 청일 경쟁
- `je_iwakura_mission`: 이와쿠라 사절단
- `je_colonize_korea`: 조선 식민화
- 막부 계승 사건과 현행 일본 회사

따라서 EAFP가 같은 주제의 마스터 저널, 진행 변수, 전쟁 시스템, 이벤트 네임스페이스 또는 회사를 다시 정의하면 이중 진행과 패치 호환성 문제가 생긴다.

### 2.3 현재 활성 상태로 남은 충돌 요소

| 우선도 | 파일 또는 기능 | 문제 | 처리 방향 |
|---|---|---|---|
| P0 | [`common/country_definitions/eafp_countries.txt`](../common/country_definitions/eafp_countries.txt) | `REPLACE:JAP`로 바닐라 국가 정의 전체를 교체 | 전체 교체 제거 우선 |
| P0 | [`common/cultures/00_cultures_jap.txt`](../common/cultures/00_cultures_jap.txt) | `REPLACE:japanese`가 현행 바닐라 필드를 누락 | 생성형 패치 또는 교체 제거 |
| P0 | [`localization/english/replace/jap_replace_l_english.yml`](../localization/english/replace/jap_replace_l_english.yml) | 현행 `je_meiji_main`, `meiji.*` 문구를 옛 내용으로 덮음 | 문구를 legacy 키로 보존한 뒤 직접 덮어쓰기만 제거 |
| P0 | 중국어 일본 교체 로컬라이징 | 영어 파일과 같은 위험 | 문구를 legacy 키로 보존한 뒤 직접 덮어쓰기만 제거 |
| P0 | [`common/journal_entries/eafp_01_ryukyu_rivalry.txt`](../common/journal_entries/eafp_01_ryukyu_rivalry.txt) | 바닐라 `je_ryukyu_rivalry` 전체 재정의 | 조선 개입을 사이드카로 분리 |
| P0 | [`common/history/military_formations/06_military_formations_asia.txt`](../common/history/military_formations/06_military_formations_asia.txt) | 바닐라 아시아 편제 파일 경로를 통째로 가림 | EAFP 추가분만 별도 파일로 분리 |
| P1 | [`common/political_movements/eafp_ideological_movements.txt`](../common/political_movements/eafp_ideological_movements.txt) | 자유민권운동은 활성화될 수 있지만 연결 JE는 비활성 | 복원된 원본 JE와 다시 연결 |
| P1 | [`common/political_movement_pop_support/eafp_political_movement_pop_support.txt`](../common/political_movement_pop_support/eafp_political_movement_pop_support.txt) | 비활성 JE 참조가 남음 | 복원된 기존 JE 키로 참조 활성화 |
| P1 | [`common/diplomatic_plays/eafp_diplomatic_plays.txt`](../common/diplomatic_plays/eafp_diplomatic_plays.txt) | `dp_boshin_war`가 바닐라 내전 생성과 충돌 | 옛 조건·툴팁용 wrapper로 보존하고 실제 내전은 DLC에 위임 |
| P1 | [`common/modifier_type_definitions/eafp_modifier_types.txt`](../common/modifier_type_definitions/eafp_modifier_types.txt) | 옛 막번체제·계승·자유민권 수정치가 남음 | 원본 이관 후 충돌 키만 이름 변경 |
| P1 | [`common/ai_strategies/eafp_admin_strategies.txt`](../common/ai_strategies/eafp_admin_strategies.txt) | 조선 전략 안에 옛 일본 JE 판정이 남음 | 연결 계층으로 이동 또는 제거 |

## 3. 핵심 설계 결정

1. **옛 EAFP 콘텐츠는 기본적으로 보존하되 명시적 삭제 목록을 우선한다.** 지역 막번체제 JE 7개, 막부 정책·청원 JE 8개, 독립 `je_tenpo_famine`, `je_terakoya`, 옛 `je_hokkaido`, 옛 재벌 JE·청원 JE 3개는 삭제·병합한다. 옛 홋카이도 사건과 후속 북방 JE는 바닐라 `je_taming_the_north`에서 이어지며, 재벌 시스템은 바닐라 `je_zaibatsu`와 바닐라 공식 회사만 사용한다.
2. **바닐라는 정사 상태의 단일 진실 공급원이다.** 쇄국, 덴포 위기, 메이지 유신, 보신전쟁, 홋카이도, 종교, 재벌, 류큐, 이와쿠라 사절단, 조선 식민화의 최종 정권·영토·전쟁 결과는 바닐라가 소유한다.
3. **살아남는 옛 JE만 DLC 동기화형 동반 저널로 복원한다.** 원래 진행 막대와 사건 풀을 유지하되 바닐라 JE의 활성·완료·실패 상태에 맞춰 열리고 닫히게 한다. 삭제 대상으로 지정된 JE의 서사는 상위 EAFP JE나 대응 바닐라 JE로만 이관한다.
4. **바닐라 JE를 `REPLACE:`한 경우에는 바닐라 전문 위에 EAFP 차이만 병합한다.** `je_meiji_restoration`, `je_meiji_main`, `je_meiji_economy`, `je_meiji_army`, `je_meiji_diplomacy`, `je_taming_the_north`와 4단계에서 새로 교체하는 `je_tenpo_crisis`는 바닐라 1.13.11 정의를 필드 단위로 전부 복원한 뒤 EAFP 사건·변수·후속 JE 연결만 추가한다. 바닐라 버튼·widget·DLC 분기·공식 이벤트·완료/실패/timeout/invalid 결과를 EAFP 간이 로직으로 대체하지 않는다. 옛 `je_zaibatsu`는 이름을 바꿔 보존하지 않고 관련 청원·사건과 함께 제거한다.
5. **옛 현지화 문구는 기본적으로 그대로 사용한다.** 키를 바꾼 항목만 기계적으로 새 키에 복사하고, 문법이 깨진 동적 스코프와 명백한 오탈자만 수정한다.
6. **옛 이벤트의 서사와 선택지는 유지한다.** DLC와 같은 사건을 다루는 경우 삭제하지 않고 바닐라 사건의 선행·후속·대체 풍미 사건으로 연결하며, 중복되는 기계적 보상만 제거한다.
7. **바닐라 내부 변수 접근은 연결 계층으로 치환한다.** 옛 본문의 호출 위치는 유지하되 deprecated 변수·효과를 wrapper trigger와 effect로 바꾼다.
8. **기존 on_action에는 목록만 추가한다.** 바닐라 on_action의 `trigger` 또는 `effect` 블록을 중복 정의하지 않는다.
9. **전체 DLC 보유만 지원한다.** DLC 비활성 분기, 축소 모드, 대체 시작 조건과 DLC 없는 세이브 검증은 만들지 않는다.
10. **리뉴얼 적용 후 시작한 신게임만 지원한다.** 이전 EAFP 세이브를 변환하는 migration, cleanup, 진행도 승계와 중복 인물 재결속은 구현하지 않는다.
11. **옛 지역 JE의 계산 구조는 바닐라 다이묘 인물 구조로 교체한다.** 지역별 loyalty·independency·goryo 막대 대신 각 주의 저택을 보유한 다이묘 인물의 `loyalty` 하나만 사용한다.
12. **모든 일본 `.disable` 파일을 먼저 활성 복원한 뒤 수정한다.** 스크립트는 `.txt`, localization은 `.yml` 활성 복사본을 만들고, 무수정 복원 기준선과 후속 수정 내역을 분리한다. 선택적으로 필요한 파일만 골라 새로 작성하는 방식은 사용하지 않는다.
13. **원본 `.disable` 파일은 이관 대조본으로 보존한다.** 원본은 직접 수정하거나 삭제하지 않는다. 활성 복사본과 원본의 차이는 별도 이관 명세에 기록하고, 리뉴얼 완료 후에도 회귀 비교 자료로 남긴다.

## 4. 콘텐츠 소유권 매트릭스

| 콘텐츠 영역 | 최종 소유자 | EAFP 처리 |
|---|---|---|
| 쇄국·개항 | 바닐라가 최종 개항 상태 소유 | 옛 개항·모리슨호·양이 사건과 JE를 DLC 동반 콘텐츠로 보존 |
| 덴포 위기 | 바닐라 `je_tenpo_crisis`가 JE 전체 소유 | `je_tenpo_famine`을 삭제하고 그 사건·기근·구휼 내용을 바닐라 JE에 병합 |
| 메이지 유신 | 바닐라가 정권 교체와 공식 과제 소유 | 메이지 main·economy·army·diplomacy를 현행 바닐라 정의로 갱신하고 EAFP 사건 연결만 병합 |
| 보신전쟁 | 바닐라가 내전 생성·종전 소유 | 옛 좌막·도막 JE와 7개 사건을 전황·전후처리 동반 체인으로 보존 |
| 쇼군·천황 승계 | 바닐라가 실제 통치자 승계 소유 | 옛 승계 이벤트 문구·선택지는 자문·파벌·후속 사건으로 보존 |
| 홋카이도·에조·사할린 | 바닐라 `je_taming_the_north`가 홋카이도 개발과 공식 결과 소유 | 옛 `je_hokkaido`는 삭제하고 `hokkaido.1-6`, `je_karafuto` 등 후속 북방 콘텐츠만 바닐라 JE 진행·성공 뒤 이어지도록 연결 |
| 신불분리·종교정책 | 바닐라가 공식 종교 분기 소유 | 옛 `je_shinto`와 2개 사건을 사회 반응 트랙으로 보존 |
| 재벌 | 바닐라 `je_zaibatsu`와 공식 회사가 전부 소유 | 옛 재벌 JE, 청원 JE 3개, `zaibatsu_events.1-4`, 전용 trigger·modifier·localization을 제거 |
| 류큐 경쟁 | 바닐라가 최종 귀속 소유 | 옛 일본·청 처분 JE와 현행 조선 개입 내용을 동반 저널로 보존 |
| 이와쿠라 사절단 | 바닐라 소유 | 직접 중복 JE는 만들지 않되 옛 메이지 외교 사건을 후속 풍미로 연결 |
| 조선 식민화 | 바닐라 `je_colonize_korea`가 최종 식민화 소유 | 옛 정한론 JE와 13개 사건 전체를 정치 선행·반발 체인으로 보존 |
| 자유민권운동 | EAFP 소유 | 옛 JE와 9개 사건을 현행 운동 스코프만 수정해 복원 |
| 대만출병 | EAFP 소유 | 옛 JE와 2개 사건을 원형 중심으로 복원 |
| 막부 관료·번정치 | EAFP `je_bakuhantaisei`와 바닐라 다이묘 인물 시스템 | 지역 JE·goryo·independency를 삭제하고 저택 소유 다이묘의 `loyalty`로 세금·정치 반응 계산 |
| 막부 개혁 과제 | EAFP | `je_bakufu_kaikaku` 계열을 현행 메이지 main·economy·army·diplomacy 구조에 맞춰 최신화 |

## 5. 바닐라 연결 계층

### 5.1 제안 파일

```text
common/
  scripted_triggers/
    eafp_japan_vanilla_bridge.txt
  scripted_effects/
    eafp_japan_vanilla_bridge_effects.txt
  on_actions/
    eafp_japan_on_actions.txt
  journal_entries/
    eafp_japan_legacy.txt
    eafp_meiji_current_compatibility.txt
  scripted_values/
    eafp_japan_daimyo_loyalty_values.txt
events/
  eafp_jap_events/
    eafp_japan_legacy.txt
    eafp_boshin_war_legacy.txt
    eafp_tenpo_crisis_integrated_events.txt
    eafp_hokkaido_legacy.txt
    eafp_shinto_events_legacy.txt
    eafp_liberty_civil_right_movement_events_legacy.txt
    eafp_seikanron_events_legacy.txt
    eafp_karafuto_events_legacy.txt
    eafp_formosa_expedition_events_legacy.txt
  eafp_meiji_restoration_legacy.txt
documentation/
  japan_content_renewal_plan.md
  japan_vanilla_compatibility_matrix.md
  japan_legacy_content_migration_manifest.md
```

실제 구현 시 기존 저장소의 파일 분리 방식과 충돌하지 않는 범위에서 세분화한다.

### 5.2 제안 scripted trigger

| 트리거 | 목적 |
|---|---|
| `eafp_japan_is_bakufu_era` | 막부법, 국가 상태, 유신 진행 종합 판정 |
| `eafp_japan_is_open` | 쇄국·고립주의·국경 정책 종합 판정 |
| `eafp_japan_tenpo_crisis_active` | 현행 덴포 위기 활성 여부 |
| `eafp_japan_tenpo_reformer_faction` | 바닐라 개혁파를 EAFP 히토쓰바시·개혁파 판정으로 반환 |
| `eafp_japan_tenpo_conservative_faction` | 바닐라 보수·강경파를 EAFP 난키·보수파 판정으로 반환 |
| `eafp_japan_restoration_active` | 현행 메이지 주요 JE 진행 여부 |
| `eafp_japan_restoration_finished` | 유신 또는 대체 정권 안정화 여부 |
| `eafp_japan_ryukyu_rivalry_active` | 류큐 경쟁 진행 여부 |
| `eafp_japan_korea_colonization_active` | 조선 식민화 진행 여부 |
| `eafp_japan_can_start_freedom_movement` | 자유민권운동 통합 개시 조건 |
| `eafp_japan_can_start_seikanron` | 정한론 통합 개시 조건 |
| `eafp_japan_state_has_valid_manor_daimyo` | 주의 저택 보유 다이묘 스코프가 유효한지 판정 |
| `eafp_japan_daimyo_is_disloyal` | 캐시된 저택 보유자 충성도가 40 미만인지 판정 |
| `eafp_japan_daimyo_is_loyal` | 캐시된 저택 보유자 충성도가 65 초과인지 판정 |

판정 우선순위는 국가 생존·독립·내전 여부, 법률과 통치 원칙, 활성 또는 완료된 바닐라 DLC JE, 안정적으로 확인된 바닐라 변수 순으로 둔다. 모든 DLC가 존재한다고 가정하므로 기능 부재를 위한 대체 판정은 만들지 않는다. 개별 EAFP 이벤트는 `meiji_var` 같은 내부 변수를 직접 참조하지 않고 연결 트리거만 호출한다.

### 5.3 EAFP 소유 변수

- `eafp_jap_legacy_restoration_progress`: 옛 `shogunate_var`를 대체하는 EAFP companion 전용 진행도
- `eafp_jap_seen_meiji_restoration`, `eafp_jap_seen_meiji_main`: 월간 bridge가 바닐라 JE의 active→closed 전환을 판정하기 위한 shadow flag
- `eafp_jap_meiji_companion_completed`: 공식 유신 결과를 건드리지 않는 EAFP 동반 트랙 종료 flag
- `eafp_jap_bakufu_sidecar_completed`
- `eafp_jap_freedom_movement_result`
- `eafp_jap_seikanron_result`
- `eafp_jap_formosa_expedition_result`
- 바닐라 `cached_daimyo_loyalty`를 직접 확장할 수 없을 때만 사용하는 namespaced 주별 충성도 캐시
- 고유 사건의 단발성 발동·쿨다운 변수

옛 콘텐츠가 이미 사용하던 EAFP 변수는 신게임에서 다시 시작되는 콘텐츠가 실제로 사용하는 경우에만 유지한다. 바닐라 유신·보신전쟁·류큐 결과를 직접 결정하던 변수는 “EAFP 동반 트랙 진행도”로 의미를 제한하고, 바닐라 상태를 쓰는 효과는 연결 effect로 치환한다. 삭제된 옛 재벌 변수는 활성 정의와 신규 호출부에서 제거하며 기존 세이브의 값을 정리하는 별도 effect는 만들지 않는다.

## 6. 전체 DLC 필수 전제

### 6.1 지원 환경

- 모든 공식 DLC가 활성화된 환경만 지원한다.
- 일본 리뉴얼은 `The Great Wave`의 현행 JE·이벤트·인물·회사·법률이 항상 존재한다고 가정한다.
- DLC 보유 여부에 따른 `trigger_if`, 대체 JE, 축소 사건 풀과 폴백 인물을 만들지 않는다.
- `has_dlc_feature = ep2_content`는 로직 분기용이 아니라 잘못된 설치를 조기에 차단하는 방어 판정으로만 둘 수 있다.
- 모드 설명과 배포 문서에 전체 DLC 필수 조건을 명시한다.

### 6.2 DLC 결과와의 동기화

- 바닐라 JE가 시작되면 대응하는 옛 EAFP 동반 JE를 원래 구조에 가깝게 시작한다.
- 옛 EAFP JE가 먼저 목표를 달성해도 정권·영토·전쟁의 공식 결과는 바닐라 JE가 결정한다.
- 바닐라 JE가 완료·실패·무효화되면 대응 EAFP JE도 정해진 완료·실패·정리 분기로 이동한다.
- 옛 이벤트가 바닐라 사건과 같은 역사적 사건을 다루면, 바닐라 사건의 선행 또는 후속 사건으로 한 번만 발동한다.
- DLC 비활성 신게임과 세이브는 테스트 매트릭스에서 제외한다.

### 6.3 `.disable` 전면 활성 복원 절차

1차 파일명·경로 조사에서 일본 콘텐츠로 식별된 `.disable` 파일은 47개였다. 참조 그래프 조사에서 막번체제 진행 막대·버튼·scripted GUI, 원로회의 GUI, 쿠로후네 한국어 문구, 일본 인물 설명 현지화 6개를 추가해 최종 복원 기준선은 53개로 확정했다. 분류는 `common` 33개, `events` 12개, `localization` 7개, `gui` 1개다. 이후 일본 전용 간접 의존 파일이 새로 발견되면 manifest에 추가하고 같은 복원 절차를 적용한다.

복원 순서는 다음과 같이 고정한다.

1. 모든 대상 `.disable` 파일의 상대 경로, 크기, 체크섬과 활성 목적 경로를 `japan_legacy_content_migration_manifest.md`에 기록한다.
2. `common/**`, `events/**`와 history 등 게임 스크립트는 내용을 바꾸지 않고 동일 경로의 `.txt` 활성 복사본으로 만든다.
3. `localization/**`는 내용을 바꾸지 않고 동일 경로의 `.yml` 활성 복사본으로 만든다. 사용자가 지정한 “`.txt`로 되살린다”는 원칙은 스크립트 파일에 적용하고, localization만 엔진이 요구하는 `.yml`을 사용한다.
4. 두 character template 파일을 포함한 일본 인물 파일도 예외 없이 먼저 활성 복원한다. 중복 인물 삭제는 그 다음 수정 단계에서 수행한다.
5. 활성 복사본을 아직 수정하지 않은 상태를 별도 기준 커밋 또는 체크섬 묶음으로 고정한다.
6. 전면 복원 상태로 게임을 한 번 로드해 duplicate key, invalid scope, missing reference, localization 충돌 로그를 수집한다. 이 로그는 삭제 대상 파일을 건너뛸 근거가 아니라 후속 수정 목록의 입력으로 사용한다.
7. 이후의 모든 저널 삭제·바닐라 병합·ID 변경·중복 인물 통합·문법 갱신은 활성 `.txt`/`.yml` 복사본에만 적용한다.
8. 각 수정 뒤 원본 `.disable`과 활성 파일을 diff해 `원형 유지`, `현행화`, `다른 JE로 이관`, `명시적 삭제` 단위로 변경 사유를 기록한다.

복원 단계에서는 스크립트가 중복되거나 오류를 내더라도 내용을 선별 삭제하지 않는다. “전체 원본을 활성 파일로 되살린 상태”와 “충돌을 해결한 최종 상태”를 분리해 남기는 것이 목적이다. 다만 실제 배포본과 정상 플레이 검증은 수정 완료된 활성 파일만 대상으로 한다.

## 7. 옛 콘텐츠 이관 계획

### 7.1 저널별 처리 유형

옛 일본 저널은 키 하나마다 다음 처리 유형 중 하나를 지정한다.

| 처리 유형 | 의미 |
|---|---|
| 원형 보존 재가동 | 기존 키·진행·사건 호출·현지화를 유지하고 현행 문법만 고친다. |
| 키 변경형 보존 | 바닐라와 정확히 충돌하는 키만 `eafp_jap_legacy_*`로 바꾸고 나머지 본문은 유지한다. |
| DLC 동기화형 보존 | 옛 JE의 진행과 사건은 유지하되 개시·완료·실패를 대응 바닐라 DLC JE에 연결한다. |
| 결과부 치환 | 옛 JE를 유지하면서 정권·영토·전쟁을 직접 바꾸는 결과만 연결 effect로 교체한다. |
| 현행 ID 매핑형 보존 | 사라진 주·법률·스코프만 현재 ID로 바꾸고 원래 구조는 유지한다. |
| 바닐라 최신화형 병합 | 현행 바닐라 JE 정의를 기준본으로 삼고 EAFP 사건·효과 연결만 추가한다. |
| 바닐라 JE로 병합 후 삭제 | 옛 독립 JE를 제거하고 그 사건·진행 요소를 지정된 바닐라 JE 안으로 이동한다. |
| 명시적 삭제 | JE와 전용 버튼·진행 막대·효과·트리거·현지화를 활성 대상에서 제거한다. |
| 활성 재정의 제거 | 현재 활성된 바닐라 키 재정의를 제거하고 필요한 EAFP 확장만 별도 JE로 옮긴다. |

삭제는 원칙적으로 최후 수단이지만 이번 수정에서 지정된 지역 JE, 막부 정책·청원 JE, `je_tenpo_famine`과 `je_terakoya`에는 예외를 적용한다. 삭제된 JE의 전용 UI·계산 자산도 함께 제거하되 재사용 가치가 있는 사건 문구는 지정된 바닐라 JE 또는 상위 EAFP JE로 병합할 수 있다. 모든 삭제·병합은 `japan_legacy_content_migration_manifest.md`에 원본 키와 새 목적지를 기록한다.

### 7.2 `eafp_00_meiji_restoration.disable`

이 파일은 4단계에서 현행 바닐라 JE를 기준으로 다시 생성하는 `REPLACE:` 파일이다. `je_terakoya`는 전용 지원 자산과 함께 제거하고 대체 legacy JE를 만들지 않는다. 나머지 메이지 5개 JE는 별도 legacy JE로 분리하지 않는다. 각 블록에는 바닐라 1.13.11 정의 전문을 먼저 유지하고, EAFP 옛 사건·현지화·고유 보상·추적 변수 중 비충돌 부분만 주석으로 구분한 추가 구간에 병합한다.

#### 7.2.1 `je_terakoya`

- **처리:** 명시적 삭제
- **활성 키:** 없음
- `REPLACE:je_terakoya` 정의를 제거하며 `je_eafp_jap_legacy_terakoya` 같은 대체 JE를 만들지 않는다.
- `common/history/countries/jap - japan.txt`의 `add_journal_entry = { type = je_terakoya }`를 제거한다.
- `modifier_jap_terakoya`, `modifier_legacy_of_terakoya`와 전용 tooltip·이벤트·effect·trigger·현지화는 전체 참조를 조사한 뒤 다른 콘텐츠가 사용하지 않으면 함께 제거한다. 공용 자산이면 `je_terakoya` 분기만 삭제하고 살아남는 호출자는 namespaced 공용 자산으로 이관한다.

#### 7.2.2 `je_meiji_restoration`

- **처리:** 바닐라 최신화형 `REPLACE:` + EAFP 차이 병합
- **활성 키:** `REPLACE:je_meiji_restoration`
- 바닐라의 세 scripted button, 천황·다이묘 widget, 천황·다이묘 갱신, 다이묘 충성도 캐시, 유신운동 생성, `restoration_timer_var`, 월간 공식 사건 풀, 황실·막부 승리, 공무합체·공의여론, invalid와 공식 결과를 전문 그대로 기준선에 둔다.
- 바닐라 `on_complete`의 공식 effect 뒤에는 `eafp_jap_restoration_finished`와 `eafp_jap_meiji_legacy.1`을, `on_fail/on_invalid` 뒤에는 `eafp_jap_restoration_failed`만 부가 추적으로 병합한다. EAFP의 단순 6개월 진행도, 하위 메이지 JE 직접 추가, 정권·영토·공식 완료 변수 재지급은 바닐라 로직과 중복되므로 독립 대체 로직으로 유지하지 않는다.

#### 7.2.3 `je_meiji_main`

- **처리:** 바닐라 최신화형 병합
- **활성 키:** `REPLACE:je_meiji_main`
- 바닐라 1.13.11의 두 버튼, 12년 timeout, `meiji_var`, 경제·군사·이와쿠라 완료 조건, 완료·부분 진행·무진행 결말과 `meiji.2/4/5/6/14` 호출을 모두 유지한다. 모든 DLC가 있다는 전제이므로 공식 완료 조건은 `iwakura_mission_finished` 분기를 그대로 사용한다.
- EAFP의 `eafp_jap_meiji_main_finished`, `eafp_jap_meiji_legacy.2/4/5/6`과 관련 현지화는 공식 사건을 제거하지 않는 추가 effect·추가 사건 풀로 병합한다. EAFP 경제·군사·외교 완료 flag 세 개만으로 본 JE를 끝내는 기존 간이 완료 조건은 사용하지 않는다.

#### 7.2.4 `je_meiji_economy`

- **처리:** 바닐라 최신화형 병합
- **활성 키:** `REPLACE:je_meiji_economy`
- 현행 바닐라의 로비 노출, 채무 불이행 금지, 편입 주의 도시 중심지 5단계, 철도 보급률 70%, `completed_je_meiji_economy`와 `meiji_var` 처리, `meiji.7-8` 사건 풀을 그대로 둔다.
- EAFP의 `eafp_jap_meiji_economy_finished`, `eafp_jap_meiji_legacy.7/8`과 비중복 보상만 공식 `on_complete` 및 연간 사건 풀 뒤에 추가한다. 본 JE의 공식 완료 조건이나 공식 변수를 EAFP flag로 바꾸지 않는다.

#### 7.2.5 `je_meiji_army`

- **처리:** 바닐라 최신화형 병합
- **활성 키:** `REPLACE:je_meiji_army`
- 현행 바닐라의 농노제·농민 징집병 폐지, 군부 비정부, 나폴레옹 전쟁술, 사무라이 훈련·무조직 PM 제거, 비정규 보병 비율 조건과 `completed_je_meiji_army`, `meiji_var`, `meiji.3/9/10` 호출을 그대로 둔다.
- EAFP의 `eafp_jap_meiji_army_finished`, `eafp_jap_meiji_legacy.3/9/10`은 공식 완료·연간 pulse 뒤에 추가한다. 공식 `meiji.3`을 EAFP 사건으로 치환하거나 EAFP invalid 조건을 덧붙여 바닐라보다 일찍 저널을 닫지 않는다.

#### 7.2.6 `je_meiji_diplomacy`

- **처리:** 바닐라 최신화형 병합
- **활성 키:** `REPLACE:je_meiji_diplomacy`
- 현행 바닐라의 전통주의 폐지, 독립, 승인국 조건과 `completed_je_meiji_diplomacy`·`meiji_var`, `meiji.11/12` 사건 풀을 그대로 둔다. 전체 DLC 환경의 `je_meiji_main` 완료는 이 JE 대신 이와쿠라 사절단을 요구하지만 외교 JE 자체는 공식 선택 과제로 유지한다.
- EAFP의 `eafp_jap_meiji_diplomacy_finished`, `eafp_jap_meiji_legacy.11/12`와 비중복 보상만 추가한다. 공식 완료 조건·공식 변수·사건을 EAFP 버전으로 교체하지 않는다.

### 7.3 `eafp_japan.disable`

#### 7.3.1 `je_bakuhantaisei`

- **처리:** 원형 보존 재가동 + 다이묘 충성도 구조로 재작성
- **활성 키:** 기존 `je_bakuhantaisei` 유지
- 전국 단위의 노중·대노 인사, 다이묘 감독, 파벌 경쟁과 사건 호출은 유지한다. 7개 지역 하위 JE 연결, 지역별 loyalty·independency·goryo 진행 막대는 제거하고, 바닐라 다이묘 캐시를 읽는 전국 요약 UI로 바꾼다. 자체 유신·정권 교체 효과는 바닐라 메이지 결과를 읽는 연결 effect로 치환한다.

#### 7.3.2 `je_bakuhantaisei_TOHOKU`

- **처리:** 명시적 삭제
- **새 대응:** `je_bakuhantaisei` + 도호쿠 각 주 저택 보유자의 `loyalty`
- JE, 지역 진행 막대, 주간 loyalty·independency·goryo 계산을 제거한다. 도호쿠라는 범위는 사건 대상 주를 고르는 필터로만 남기며 세금과 정치 반응은 각 주의 다이묘 충성도에서 계산한다.

#### 7.3.3 `je_bakuhantaisei_KANTO`

- **처리:** 명시적 삭제
- **새 대응:** `je_bakuhantaisei` + 간토 각 주 저택 보유자의 `loyalty`
- 간토 직할지·다이묘 충성 JE와 상지령 전용 연결을 제거한다. 에도·개항 관련 사건은 상위 JE에 남기되 해당 주 저택 보유자의 충성도만 조건과 세금 산식에 사용한다.

#### 7.3.4 `je_bakuhantaisei_CHUBU`

- **처리:** 명시적 삭제
- **새 대응:** `je_bakuhantaisei` + 도카이·호쿠신에쓰 등 현행 주별 저택 보유자의 `loyalty`
- `STATE_CHUBU` 묶음, 저널과 진행 효과를 모두 제거한다. 현행 주는 각각 독립적으로 저택 보유자를 해석하므로 중부 합산값이나 등가 보정값을 만들지 않는다.

#### 7.3.5 `je_bakuhantaisei_KANSAI`

- **처리:** 명시적 삭제
- **새 대응:** `je_bakuhantaisei` + 간사이 각 주 저택 보유자의 `loyalty`
- 별도 지역 JE와 진행 막대는 제거한다. 교토 조정·오사카 경제권 사건 본문은 상위 JE 사건 풀에 이관하고, 조건·세금·반응은 실제 대상 주의 저택 보유자 충성도를 읽는다.

#### 7.3.6 `je_bakuhantaisei_KYUSHU`

- **처리:** 명시적 삭제
- **새 대응:** `je_bakuhantaisei` + 규슈 각 주 저택 보유자의 `loyalty`
- 사쓰마·히젠 관련 사건은 상위 JE 또는 보신전쟁 후속 사건으로 이관하되 지역 JE와 직할지·independency 계산은 제거한다. 보신전쟁 편 선택은 바닐라가 캐시한 해당 다이묘 충성도와 공식 내전 상태만 읽는다.

#### 7.3.7 `je_bakuhantaisei_CHUGOKU`

- **처리:** 명시적 삭제
- **새 대응:** `je_bakuhantaisei` + 주고쿠 각 주 저택 보유자의 `loyalty`
- 조슈의 존왕양이·막부 반대 사건은 상위 JE 또는 바닐라 조슈·보신전쟁 체인에 이관한다. 별도 진행 막대는 없으며 조슈 정벌·보신전쟁 반응은 해당 주 저택 보유자의 충성도를 사용한다.

#### 7.3.8 `je_bakuhantaisei_SHIKOKU`

- **처리:** 명시적 삭제
- **새 대응:** `je_bakuhantaisei` + 시코쿠 각 주 저택 보유자의 `loyalty`
- 지역 JE와 진행 막대를 제거한다. 도사 번 인물·자유민권운동 사건은 원래 호출 순서를 보존해 상위 JE에 이관하고, 현행 인물 중복 검사와 저택 보유자 충성도 조건을 적용한다.

#### 7.3.9 `je_hokkaido`

- **처리:** JE 완전 삭제 + 사건·후속 JE 재배치
- **활성 키:** 없음. 바닐라 `je_taming_the_north`만 북방 개발의 마스터 JE로 사용
- 옛 `je_hokkaido` 정의, history 시작 호출, `hokkaido_progress_bar`와 네 전용 JE 버튼은 제거한다. 옛 JE가 시작 시 부여하던 마쓰마에·장소청부제 상태는 바닐라 초기화와 중복 적용하지 않는다.
- `hokkaido.5-6`은 `je_taming_the_north` 진행 중의 EAFP 월간 풍미 사건 풀로 옮기고, `hokkaido.2-4`의 성곽 건설 선택지는 전용 버튼 대신 바닐라 JE 진행 중 조건부로 한 번 시작되는 사건 연쇄로 보존한다.
- `hokkaido.1`은 바닐라 JE 성공을 감지한 뒤 한 번 발생하는 북방 후일담·후속 체인 개방 사건으로 바꾼다. 바닐라 완료 보상, 에조 결과와 사할린 소유권을 중복 지급하지 않는다.
- `je_karafuto`를 첫 번째 명시적 후속 JE로 삼고, `eafp_jap_taming_north_completed`가 설정된 뒤에만 표시·개시한다. 기존의 “이미 사할린 일부를 소유해야 시작” 조건은 제거하고, 일본의 홋카이도 지배와 사할린의 유효한 소유·식민·러시아 관여 상태를 조건으로 사용해 바닐라 북방 개발에서 자연스럽게 이어지게 한다.
- `REPLACE:je_taming_the_north`는 바닐라의 일본·에조 표시/가능 조건, 다섯 scripted button, 공식 카운터 세 개, `ainu_friendship_var`, `hokkaido_events.1/7/8`, 사할린 추가 목표, 완료 보상과 실패 결과를 전문 그대로 포함한다. 그 위에만 EAFP `hokkaido.2-6` 진행 중 사건, `hokkaido.1` 완료 후일담, `je_karafuto` 개방과 `eafp_jap_taming_north_completed/failed` 추적을 추가한다. EAFP의 독자 36개월 진행도와 `eafp_jap_ainu_friendship`은 바닐라 공식 카운터를 대체하지 않는다.

#### 7.3.10 `je_tenpo_famine`

- **처리:** 바닐라 JE로 병합 후 삭제
- **새 대응:** 현행 바닐라 `je_tenpo_crisis`
- 독립 JE 키, 전용 기근 진행 막대와 완료·실패 처리를 제거한다. 구휼·쌀값·이주·지역 불안의 `tenpo_famine.1-6`과 결말 `.99`는 바닐라 JE의 개시·월간 사건 풀·완료·12년 timeout 분기로 이관한다. 오시오의 난은 바닐라 `tenpo_events.2`를 두 번 일으키지 않고 옛 사건을 선행 선택지 또는 후속 풍미 사건으로만 연결한다. 기존 `reduce_nidome*` 버튼은 전부 제거한다.
- 바닐라의 개혁파 목표는 EAFP `is_hitotsubashiha`가 판정하는 개혁파(`ideology_kaikakuha`, `ideology_hitotsubashiha`)에, 보수·강경파 목표는 `is_nankiha`가 판정하는 보수파(`ideology_hoshuha`, `ideology_nankiha`)에 대응시킨다. `tenpo_outcome_reformer_var`와 `tenpo_outcome_hardliner_var` 결과가 각각 해당 파벌의 영향력·찬반 반응을 한 번만 갱신하게 한다.

#### 7.3.11 `je_bakufu_kaikaku`

- **처리:** 현행 메이지 구조 최신화형 보존
- **활성 키:** 기존 `je_bakufu_kaikaku` 유지
- 현행 `je_meiji_main`의 12년 생명주기, 하위 과제 완료 집계, 부분 성공·무진행 결말과 버튼 배치를 기준으로 다시 작성한다. 삭제되는 네 정책 JE와 네 청원 JE는 요구 조건에서 제거하고, `je_bakufu_kaikoku`·`je_bakufu_guntai`·`je_bakufu_zaisei` 및 막부 고유 내부 권위 과제인 `je_bakufu_naibu`를 집계한다. 개혁파·보수파 사건과 관료 인사 서사는 유지하되 정권 교체는 바닐라가 소유한다.

#### 7.3.12 `je_bakufu_kaikoku`

- **처리:** 현행 `je_meiji_diplomacy` 대응 최신화
- **활성 키:** 기존 `je_bakufu_kaikoku` 유지
- 사용자 지정 목록에는 빠져 있지만 기능상 외교 과제의 직접 대응물이므로 유지한다. 현행 `je_meiji_diplomacy`의 전통주의 폐지·독립·승인국 조건과 바닐라 `je_sakoku`의 개항 결과를 기준으로 갱신하고, 옛 개국 사건·현지화·파벌 반응은 한 번만 적용한다.

#### 7.3.13 `je_bakufu_guntai`

- **처리:** 현행 `je_meiji_army` 대응 최신화
- **활성 키:** 기존 `je_bakufu_guntai` 유지
- 현행 군사 과제의 농노제·농민 징집병 폐지, 군부 비정부, 나폴레옹 전쟁술, 사무라이 훈련·무조직 PM 제거, 비정규 보병 비율 조건을 막부 시대에 맞게 사용한다. 막부군·유력 번 경쟁, 외국 교관과 사무라이 반발 사건은 보존하되 바닐라 `je_meiji_army`의 완료 변수를 직접 쓰지 않는다.

#### 7.3.14 `je_bakufu_naibu`

- **처리:** 현행 `je_meiji_main` 생명주기 대응 최신화
- **활성 키:** 기존 `je_bakufu_naibu` 유지
- 현행 `je_meiji_main`의 timeout·부분 완료·국가 상태 무효화 규칙에 맞추되, 경제·군사·외교와 중복되지 않는 막부 고유 내부 권위 과제로 둔다. 막부 권력 유지 사건은 보존하고 성공 시 EAFP 내부 권위·파벌 보상만 지급하며 바닐라 유신을 차단하거나 완료시키지 않는다.

#### 7.3.15 `je_bakufu_zaisei`

- **처리:** 현행 `je_meiji_economy` 대응 최신화
- **활성 키:** 기존 `je_bakufu_zaisei` 유지
- 현행 경제 과제의 채무 불이행 금지, 편입 주 도시 중심지 5단계, 철도 보급률 70% 구조를 막부 개혁의 기준으로 사용한다. 옛 GDP·통화·세입·부채 사건은 보존하되 삭제되는 신화폐 정책 JE를 요구하지 않으며, 유신 후에는 바닐라 `je_meiji_economy`와 중복 진행하지 않게 정리한다.

#### 7.3.16 `je_eafpjap2310`

- **처리:** 원형 보존 재가동
- **활성 키:** 기존 `je_eafpjap2310` 유지
- 숫자형 ID를 포함한 별도 사임 요구 JE, 대상 인물 스코프와 기한을 유지한다. 현지화의 파벌 표기가 실제 원본 이벤트 호출과 일치하는지만 교정한다.

#### 7.3.17 `je_eafpjap2311`

- **처리:** 원형 보존 재가동
- **활성 키:** 기존 `je_eafpjap2311` 유지
- `je_eafpjap2310`과 별개의 파벌 사임 요구 JE를 원형대로 유지한다. 대상 인물이 DLC 인물과 중복 생성되지 않도록 인물 스코프 획득부만 수정한다.

#### 7.3.18 `je_boshin_war_sabaku`

- **처리:** DLC 동기화형 보존 + 결과부 치환
- **활성 키:** 기존 `je_boshin_war_sabaku` 유지
- 좌막파 전용 전황·점령 진행과 관련 사건을 보존한다. 자체 외교전 생성·강제 종전·정권 변경만 바닐라 보신전쟁의 막부 측 스코프와 결과를 읽는 effect로 치환한다.

#### 7.3.19 `je_boshin_war_tobaku`

- **처리:** DLC 동기화형 보존 + 결과부 치환
- **활성 키:** 기존 `je_boshin_war_tobaku` 유지
- 도막파 전용 전황 JE, 전후 인사와 `boshin_war.1-11` 호출 구조를 보존한다. 내전·정권 교체 결과는 바닐라가 처리하고 옛 JE는 전황 표시와 EAFP 후속 사건만 담당한다.

#### 7.3.20 `je_liberty_civil_right_movement`

- **처리:** 원형 보존 재가동
- **활성 키:** 기존 `je_liberty_civil_right_movement` 유지
- JE 본문, 진행도, 9개 `liberty_civil_right_movement_events.*` 사건과 현지화를 그대로 이관한다. 정치운동 스코프와 법률 ID만 현행 시스템에 맞추고, 기존 활성 `eafp_movement_liberty_civil_right`와 다시 연결한다.

#### 7.3.21 `je_seikanron`

- **처리:** 원형 보존 재가동 + 결과부 치환
- **활성 키:** 기존 `je_seikanron` 유지
- JE 진행, 정한파·온건파 갈등, `seikanron_events.1-15`와 `.99`, 현지화를 모두 유지한다. 조선 병합·전쟁 개시 결과만 바닐라 `je_colonize_korea`와 현행 외교전으로 넘긴다.

#### 7.3.22 `je_shinto`

- **처리:** DLC 동기화형 보존 + 결과부 치환
- **활성 키:** 기존 `je_shinto` 유지
- 옛 국교화·신토 진행 막대, `shinto_events.1`과 `.99`, 결정·버튼·현지화를 보존한다. 공식 종교 분기는 `je_shinbutsu_bunri` 또는 `je_elevate_buddhism` 결과에 동기화한다.

#### 7.3.23 `je_zaibatsu`

- **처리:** 완전 삭제
- **활성 키:** 없음. 바닐라 `je_zaibatsu`만 사용
- 옛 진행도, 회사 수 계산, 산업가 명칭 변경, `zaibatsu_cooperation_modifier`, `is_zaibatsu_company`, `zaibatsu_events.1-4`와 전용 현지화를 모두 제거한다. 공식 재벌 확립·억제 결과와 사건은 바닐라 콘텐츠만 담당한다.

#### 7.3.24 `je_zaibatsu_petition_government`

- **처리:** 완전 삭제
- **활성 키:** 없음
- 옛 재벌 모체 JE와 함께 정의, 변수, 완료·실패 효과, 사건 호출과 현지화를 제거한다.

#### 7.3.25 `je_zaibatsu_petition_rice`

- **처리:** 완전 삭제
- **활성 키:** 없음
- 쌀 가격 청원 JE의 정의, 진행 변수, 보상·실패 효과, 사건 호출과 현지화를 제거한다.

#### 7.3.26 `je_zaibatsu_petition_remove_monopoly`

- **처리:** 완전 삭제
- **활성 키:** 없음
- 독점 철폐 청원 JE의 정의, 진행 변수, 보상·실패 효과, 사건 호출과 현지화를 제거한다.

#### 7.3.27 `je_ryukyu_disposition`

- **처리:** DLC 동기화형 보존 + 결과부 치환
- **활성 키:** 기존 `je_ryukyu_disposition` 유지
- 일본 측 류큐 처분 진행, 협상 문구와 조선·서구 반응 연결을 유지한다. 자체 병합 외교전과 최종 귀속 효과만 바닐라 `je_ryukyu_rivalry` 결과를 읽도록 바꾼다.

#### 7.3.28 `je_ryukyu_disposition_chi`

- **처리:** DLC 동기화형 보존 + 결과부 치환
- **활성 키:** 기존 `je_ryukyu_disposition_chi` 유지
- 청 측 류큐 보호 JE, 협상·개입 문구와 선택지를 유지한다. 전쟁과 최종 귀속만 바닐라 경쟁 결과에 동기화하고 조선 반응은 기존 EAFP 체인으로 보존한다.

#### 7.3.29 `je_karafuto`

- **처리:** DLC 동기화형 보존 + 결과부 치환
- **활성 키:** 기존 `je_karafuto` 유지
- 옛 가라후토 개척 목표, `karafuto_events.1`과 현지화를 유지하되 독립적인 시작 JE로는 사용하지 않는다. 바닐라 `je_taming_the_north` 성공 뒤 설정되는 `eafp_jap_taming_north_completed`를 필수 조건으로 하고, `hokkaido.1` 후일담 또는 북방 bridge effect가 한 번만 추가한다. 영유권·소유권 보상은 바닐라 홋카이도·에조·사할린 상태와 충돌하지 않는 외교 보상으로 치환한다.

#### 7.3.30 `je_formosa_expedition`

- **처리:** 원형 보존 재가동 + 결과부 치환
- **활성 키:** 기존 `je_formosa_expedition` 유지
- 탐사 진행 막대, `formosa_expedition_events.1-2`, 버튼과 현지화를 유지한다. 즉시 영유권 효과만 현행 류큐 경쟁·대만 소유국·조선과 청의 외교 상태를 확인하는 제한적 명분 또는 외교 위기로 바꾼다.

### 7.4 `eafp_bakufu_seisaku.disable`

이 파일의 네 정책 JE와 네 청원 JE는 전부 삭제한다. 원본에는 `je_bakufu_seisaku`라는 독립 최상위 JE가 없으므로, 이 이름은 아래 8개 JE와 그 시작 버튼·청원 판정·진행 막대·완료 및 timeout 현지화를 묶어 가리키는 삭제 범위다. 재사용 가치가 있는 사건 문구는 `je_bakufu_kaikaku` 또는 바닐라 `je_tenpo_crisis` 사건 풀로 옮길 수 있지만 삭제된 JE를 조건으로 삼아서는 안 된다.

#### 7.4.1 `je_bakufu_seisaku_new_currency`

- **처리:** 명시적 삭제
- **활성 키:** 없음
- JE, 10년 기한, 시작 버튼, 진행 막대와 전용 완료·timeout 판정을 제거한다. 악화 주조·귀금속·물가·세입 사건 문구는 `je_bakufu_zaisei`의 선택 사건으로만 이관한다.

#### 7.4.2 `je_bakufu_seisaku_junochisui`

- **처리:** 명시적 삭제
- **활성 키:** 없음
- JE, 10년 기한, 시작 버튼과 전용 농업·기근 계산을 제거한다. 치수·관개·흉작 대비 서사는 바닐라 `je_tenpo_crisis`의 구휼·기근 사건 후보로만 이관한다.

#### 7.4.3 `je_bakufu_seisaku_agechirei`

- **처리:** 명시적 삭제
- **활성 키:** 없음
- JE, 직할지 진행 비율, 10년 기한과 시작 버튼을 제거한다. 상지령·연안 방비 사건은 `je_bakufu_kaikaku`의 다이묘 충성도 사건으로 이관하며 goryo나 지역 independency를 다시 만들지 않는다.

#### 7.4.4 `je_bakufu_seisaku_kokishukusei`

- **처리:** 명시적 삭제
- **활성 키:** 없음
- 독립 JE, 시작 버튼과 완료 조건을 제거한다. 강기숙정·부패 단속·상업 규제·민중 반발 사건은 `je_bakufu_kaikaku`의 파벌 사건 풀로 이관할 수 있다.

#### 7.4.5 `je_bakufu_seisaku_new_currency_petition`

- **처리:** 명시적 삭제
- **활성 키:** 없음
- 청원 JE와 기한을 제거한다. `eafp_japan.2302`는 보수파의 재정 요구 사건으로 상위 개혁 JE에 재배치하거나, 다른 사건과 완전히 중복되면 manifest에 삭제 사유를 남긴다.

#### 7.4.6 `je_bakufu_seisaku_junochisui_petition`

- **처리:** 명시적 삭제
- **활성 키:** 없음
- 청원 JE와 전용 기근·농업 판정을 제거한다. `eafp_japan.2303`는 보수파의 구휼 요구 사건으로 바닐라 덴포 위기 또는 상위 개혁 JE에 재배치한다.

#### 7.4.7 `je_bakufu_seisaku_agechirei_petition`

- **처리:** 명시적 삭제
- **활성 키:** 없음
- 청원 JE와 에도·교토 전용 진행 판정을 제거한다. `eafp_japan.2304`의 유력 번 반발은 실제 대상 주 저택 보유자의 충성도를 읽는 상위 JE 사건으로 재배치한다.

#### 7.4.8 `je_bakufu_seisaku_kokishukusei_petition`

- **처리:** 명시적 삭제
- **활성 키:** 없음
- 청원 JE를 제거한다. `eafp_japan.2305`의 보수파·개혁파·상인·민중 반응은 `je_bakufu_kaikaku`의 일반 파벌 사건으로 재배치하거나 중복 시 삭제한다.

### 7.5 활성 `eafp_01_ryukyu_rivalry.txt`

#### 7.5.1 `je_ryukyu_rivalry`

- **처리:** 활성 재정의 제거
- **새 대응:** 바닐라 `je_ryukyu_rivalry` + `je_eafp_ryukyu_intervention`
- 현재 EAFP가 바닐라 키를 그대로 재정의해 조선 개입을 추가하는 구조를 제거한다. 바닐라 JE는 원본 그대로 로드하고, 조선의 중립·청 지지·일본 지지·독자 중재는 별도 EAFP 사이드카가 담당한다. 엔진 UI 제약 때문에 재정의가 불가피하다고 확인된 경우에만 기준 버전·원본 체크섬·변경 구간·자동 diff를 갖춘 명시적 호환 패치로 예외 처리한다.

### 7.6 최소 수정 예외

명시적 삭제 대상을 제외한 다음 항목은 표시된 최소 변경으로 보존한다.

- [`events/meiji_restoration.disable`](../events/meiji_restoration.disable)의 `meiji.1-13`: 바닐라 현행 메이지 JE의 사건 풀·후속 사건으로 병합하고 정확히 충돌하는 이벤트 ID만 `eafp_jap_meiji_legacy`로 변경
- 옛 `je_meiji_main`·`economy`·`army`·`diplomacy`: 별도 legacy JE를 만들지 않고 현행 바닐라 정의로 최신화
- 옛 보신전쟁 JE·이벤트: 내전 생성·강제 종전 effect만 바닐라 결과 동기화로 치환
- 옛 쇄국·모리슨호·개항 사건: 바닐라 사건의 선행·후속 체인으로 연결
- 옛 덴포 기근 사건: 독립 `je_tenpo_famine` 없이 바닐라 `je_tenpo_crisis`에 병합
- 옛 `je_hokkaido`: 삭제하고 사건·성곽 연쇄·가라후토 후속 JE만 바닐라 `je_taming_the_north` 진행·성공 뒤 연결
- 옛 가라후토·신토 JE: 대응 DLC JE와 병행하거나 그 완료 뒤 이어지는 동반 트랙으로 재가동
- 옛 재벌 JE·청원 JE·사건: 보존 예외에서 제외하고 완전 삭제, 바닐라 재벌 체인만 사용
- 쇼군·천황 승계 사건: DLC 인물을 중복 생성하지 않고 기존 인물 스코프를 받아 원문 선택지를 실행
- 바닐라와 중복되는 인물 템플릿: 옛 정의를 삭제하고 identity map·resolver로 모든 effect와 trigger가 바닐라 인물을 참조하게 변경
- 지역 막번체제 계산: 7개 하위 JE, `STATE_CHUBU` 합산, loyalty·independency·goryo 막대를 제거하고 주별 저택 보유자 충성도로 치환
- 막부 정책·청원: 8개 JE와 전용 UI·판정을 삭제하고 재사용 사건만 상위 JE 또는 덴포 위기로 이관
- `dp_boshin_war`: 독립 외교전 생성기로는 사용하지 않지만 옛 이벤트의 표시·조건 호환용 식별자가 필요하면 namespaced scripted trigger 또는 effect로 보존

### 7.7 전기 막부 사이드카

목표는 바닐라 쇄국·덴포 위기·메이지 유신 사이의 역사적 공백을 EAFP 특유의 관료정치와 번정치 풍미로 채우는 것이다.

복원 범위:

- 노중과 대노 임명
- 히토쓰바시파와 난키파의 관료 갈등
- 번 통제와 막부 재정 논쟁
- 해방(海防)·군제·연안 방비를 둘러싼 정책 사건
- 바닐라에 없는 존 만지로 등의 고유 풍미
- 번과 막부 사이의 충성·개혁 갈등

전국 `je_bakuhantaisei`, 최신화한 막부 개혁 과제, 파벌·인물 사건은 유지한다. 지역 JE·정책 청원 JE·goryo·independency는 제거하고, 각 주 저택 보유자의 충성도를 정치 반응과 세금의 단일 입력으로 쓴다. 유신·개항·내전·승계의 공식 결과는 바닐라 DLC에 동기화한다. `JAP`가 생존하고 막부 체제일 때 원래 사건 순서를 최대한 보존하되, 바닐라 유신이 시작되면 각 살아남은 JE의 완료·실패 사건을 거쳐 정리한다.

### 7.8 자유민권운동

유신 이후 일본의 입헌정치·민권·집회의 자유를 둘러싼 옛 JE와 9개 사건을 원형 중심으로 복원한다. 바닐라의 일반 정치운동을 별도로 복제하지 않고 기존 EAFP 운동이 현행 운동 스코프를 사용하도록 연결부만 수정한다.

개시 조건:

- `eafp_japan_restoration_finished = yes`
- 일본이 생존하고 독립 또는 충분한 자치 상태
- 적절한 문해율·도시화·자유주의 지지
- 이미 완료 또는 영구 탄압된 EAFP 자유민권운동이 아님
- 같은 목표의 바닐라 운동이 있다면 별도 중복 운동을 만들지 않음

진행 요소:

- 지식인·소시민·농민의 지지
- 집회의 자유와 검열 법률
- 선거권과 의회 확대
- 정부 탄압과 정치적 폭력
- 이타가키 등 고유 인물
- 자유주의 운동의 급진화 또는 제도권 편입

성공·타협·탄압·혁명·국가 소멸을 모두 종료 경로로 둔다. 모든 경로에 완료·실패·무효화 조건을 제공해 운동과 JE가 영구 잔류하지 않게 한다.

### 7.9 정한론

옛 정한론 JE, 13개 본 사건과 결말 사건, 정한파·온건파 선택지와 현지화를 모두 복원한다. 정한론은 메이지 정권 내부의 외교 노선 분열을 유지하면서 바닐라 조선 식민화의 정치적 선행 체인으로 연결한다.

- 사이고 계열 강경파와 오쿠보 계열 신중파의 대립
- 군부·사무라이·지식인·산업가의 태도
- 정부 정통성, 급진도, 인물 퇴진
- 사족 불만과 후속 반란 위험
- 조선의 외교적 반응

EAFP 정한론은 조선을 직접 합병하거나 자체 식민화 진행도를 만들지 않는다. 강경파 승리는 바닐라 `je_colonize_korea`의 개시 가능성, 외교 압박 또는 제한적인 외교 목표로 연결한다. 조선 식민화의 실제 성공·동화·완료 판정은 바닐라가 소유한다. 조선이 이미 멸망·합병·종속된 경우에는 대체 종료를 제공한다.

### 7.10 류큐 경쟁과 조선 개입

현재의 바닐라 `je_ryukyu_rivalry` 복사본을 다음 구조로 바꾼다.

1. 연결 트리거로 바닐라 류큐 경쟁의 활성 여부를 판정한다.
2. 조선이 적절한 조건을 만족하면 `je_eafp_ryukyu_intervention`을 별도로 생성한다.
3. 조선은 중립, 청 지지, 일본 지지, 독자 중재 중 가능한 선택지를 고른다.
4. 결과는 조선의 관계·위신·로비·향후 외교 상태에 적용한다.
5. 류큐의 최종 귀속과 바닐라 진행 막대는 바닐라가 처리한다.

바닐라 JE에 직접 버튼을 삽입해야만 기존 UX를 유지할 수 있다면 다음 조건 아래에서만 전체 JE 호환 패치를 허용한다.

- 파일 머리에 기준 바닐라 버전과 원본 경로 기록
- EAFP 변경 구간을 주석으로 표시
- 호환성 매트릭스에 예외 등록
- 원본 체크섬과 자동 diff 검사 추가
- 바닐라 패치 후 재검증 전까지 릴리스 금지

### 7.11 대만출병

대만출병은 바닐라에 완전히 같은 구조가 없으므로 옛 JE, 진행 막대, 버튼, 이벤트 2개와 현지화를 원형대로 복원한다.

- 일본의 개항 또는 유신 상태
- 류큐의 생존·종속·합병 상태
- 대만 소유국과 외교 관계
- EAFP 대만 콘텐츠의 진행 상태
- 일본이 이미 대만을 소유하는지 여부
- 동일 사건의 발동·완료 여부

원래 조사와 원정 흐름은 유지한다. 다만 즉시 영구 영유권이나 무료 합병을 주는 결과가 있다면 해당 결과부만 현행 외교 명분·외교 위기·바닐라 류큐 상태와 연동되도록 치환한다.

### 7.12 재벌과 회사

미쓰이·미쓰비시·만철·스미토모·야스다는 바닐라 회사를 사용한다. 조히코, 제일국립은행 등 바닐라에 없는 후보만 이관을 검토한다.

고유 회사는 바닐라 `je_zaibatsu`를 직접 완료시키거나 재벌 진행 변수를 조작하지 않는다. 정상적인 설립·번영·파산 메커니즘으로만 병존시키며, 옛 EAFP 재벌 JE·사건의 후속 연결은 만들지 않는다.

### 7.13 인물과 자산

1. 옛 이벤트가 참조하는 모든 인물 템플릿을 이관 목록에 포함한다.
2. 바닐라에 같은 인물이 있으면 옛 템플릿 정의를 활성화하지 않고 삭제 대상에 등록하며, identity map이 바닐라 템플릿을 정본으로 반환한다.
3. 바닐라에 없는 인물은 기존 EAFP ID·DNA·초상화·현지화를 유지해 활성화한다.
4. 생성 effect는 먼저 살아 있는 바닐라 정본 인물을 찾고, 없을 때도 옛 템플릿이 아니라 바닐라 템플릿을 생성한다. 모든 `has_template`, saved scope, 변수, 역할 부여 trigger/effect를 정본 ID 또는 resolver로 치환한다.
5. 옛 템플릿에만 있던 특성·이념이 서사상 필요하면 같은 인물의 중복 정의 대신 사건 effect로 정본 인물에 조건부 부여한다.
6. 옛 국기·아이콘·메시지·수정치·버튼·진행 막대는 연결 콘텐츠가 있는 경우에만 이관한다. 삭제된 지역·정책 JE, goryo와 `reduce_nidome` 전용 자산은 예외다.

### 7.14 이벤트 파일별 이관

비활성 이벤트 156개는 전부 이관 manifest에 등록해 “그대로 활성”, “다른 JE로 재배치”, “바닐라 사건에 흡수”, “중복으로 삭제” 중 하나를 지정한다. 재사용 이벤트는 원래 파일과 ID·순서를 최대한 유지하고 필요한 경우 활성 파일명에만 `_legacy`를 붙인다.

| 원본 파일 | 이벤트 수 | 이관 방침 |
|---|---:|---|
| `events/meiji_restoration.disable` | 13 | 현행 메이지 네 JE의 사건 풀·후속 체인에 맞춰 최신화하고, 바닐라와 정확히 중복되는 ID만 namespaced ID로 재배치 |
| `eafp_japan.disable` | 91 | 네임스페이스와 ID를 최대한 유지하되 지역 JE·정책 JE 의존 호출은 상위 막번체제·막부 개혁·덴포 위기로 재배치하고 중복 인물 생성은 제거 |
| `eafp_boshin_war.disable` | 7 | 이벤트 본문과 선택지 유지, 외교전 생성·종전·정권 효과만 바닐라 보신전쟁 스코프로 치환 |
| `eafp_tenpo_famine_events.disable` | 7 | 독립 JE 없이 바닐라 `je_tenpo_crisis`의 개시·월간·완료·timeout 사건으로 병합하며 오시오 사건은 중복 발동 금지 |
| `eafp_hokkaido.disable` | 6 | JE 없이 전부 보존: `.2-.6`은 `je_taming_the_north` 진행 중 사건, `.1`은 성공 후일담과 `je_karafuto` 개방 사건으로 재배치 |
| `eafp_shinto_events.disable` | 2 | 전부 유지하고 바닐라 종교 분기 결과를 읽도록 수정 |
| `eafp_zaibatsu_events.disable` | 4 | 활성 복원 기준선만 보존하고 활성 `.txt`, 호출, JE와 localization은 삭제 |
| `eafp_liberty_civil_right_movement_events.disable` | 9 | 원형 복원, 정치운동·법률 스코프만 현행화 |
| `eafp_seikanron_events.disable` | 13 | 원형 복원, 직접 정복 결과만 바닐라 조선 식민화로 연결 |
| `eafp_karafuto_events.disable` | 1 | 원형 복원, 사할린 소유·영유권 결과만 현행화 |
| `eafp_formosa_expedition_events.disable` | 2 | 원형 복원, 대만 소유국·류큐 경쟁 스코프만 현행화 |
| `eafp_hanbatsu_oligarchy_events.disable` | 1 | 원형 복원하고 자유민권운동·정한론의 후속 종료에 연결 |

이벤트 수정 우선순위는 다음과 같다.

1. 원래 ID·제목·설명·선택지·발동 순서 유지
2. 바닐라와 정확히 겹치는 네임스페이스만 변경
3. 사라진 trigger·effect·scope를 wrapper로 교체
4. DLC 사건과 같은 역사 사건은 선행 또는 후속으로 한 번만 발동
5. 정권·영토·전쟁·인물 중복 생성 효과만 제거 또는 치환
6. 원래 수치 보상은 중복 적용 여부를 검사한 뒤 가능한 한 유지

### 7.15 현지화 이관

| 원본 파일 | 확인 키 수 | 이관 방침 |
|---|---:|---|
| `localization/english/eafp_japan_l_english.disable` | 1,447 | 확장자를 `.yml`로 바꾸고 기존 문구를 기본값으로 사용 |
| `localization/korean/eafp_japan_l_korean.disable` | 1,459 | 확장자를 `.yml`로 바꾸고 기존 문구를 기본값으로 사용 |
| `localization/simp_chinese/eafp_japan_l_simp_chinese.disable` | 1,447 | 확장자를 `.yml`로 바꾸고 기존 문구를 기본값으로 사용 |
| `localization/korean/japan_historical_names_l_korean.disable` | 1,586 | 한국어 역사명 풀로 복원하고 현행 바닐라 이름과 중복만 검사 |
| `localization/korean/replace/jap_replace_l_korean.disable` | 10 | 바닐라 키를 덮지 않고 이름을 바꾼 EAFP 메이지 JE·이벤트 키로 복사 |

현지화는 문체를 새로 쓰지 않는다. 다음 경우에만 수정한다.

- 이벤트·JE 키가 충돌 회피를 위해 바뀐 경우
- 현행 엔진에서 동적 스코프 문법이 깨지는 경우
- 원문과 이벤트 선택지가 명백히 불일치하는 경우
- 한국어·영어·중국어 간체 중 한 언어에 키가 누락된 경우
- 바닐라 `replace` 키를 그대로 활성화하면 DLC 문구를 덮는 경우
- 삭제된 지역 JE 7개, 정책·청원 JE 8개, goryo·independency·지역 진행 막대와 `reduce_nidome*` 버튼에만 쓰이는 경우

키 변경은 `legacy_localization_key_map`에 원본 키와 활성 키를 1:1로 기록한다. 원문은 주석이나 별도 이관 manifest에 남기고, 파일 인코딩은 UTF-8 BOM과 CRLF를 유지한다.

### 7.16 보조 파일 이관

다음 비활성 보조 파일을 포함한 일본 관련 `.disable` 파일은 살아남는 정의의 유무와 관계없이 먼저 활성 복원한다. 복원 후 살아남는 저널과 재배치되는 이벤트가 참조하는 정의는 원형 유지가 기본이다.

- `common/scripted_triggers/eafp_jap_triggers.disable`
- `common/scripted_effects/eafp_japan_effects.disable`
- `common/on_actions/japan_code_on_actions.disable`
- `common/scripted_buttons/eafp_japan_buttons.disable` 중 살아남는 막부 개혁 버튼
- 막부 개혁·신토·대만출병 진행 막대 중 살아남는 JE가 실제로 참조하는 정의. `je_hokkaido` 삭제와 함께 `hokkaido_progress_bar`는 제거한다.
- 일본 수정치·메시지·상호작용·결정·회사·custom localization

다음 자산은 명시적으로 제거한다.

- 7개 지역 JE의 정의·호출·지역 loyalty·independency·goryo 진행 막대와 계산 effect·trigger·scripted value·modifier·tooltip·현지화
- `reduce_nidome_TOHOKU/KANTO/CHUBU/KANSAI/KYUSHU/CHUGOKU/SHIKOKU`와 `reduce_nidome2_*`를 합한 14개 버튼, 모든 호출과 버튼 현지화
- 8개 막부 정책·청원 JE의 시작 버튼, 청원 trigger, 진행 막대, 완료·timeout 전용 effect와 현지화
- 삭제된 JE만 참조하는 고아 on_action과 SGUI

그 밖의 보조 파일도 모두 확장자만 활성화한 시험 기준선에서 오류를 수집한 뒤, 활성 복사본의 오류가 발생한 줄과 명시적 삭제 자산만 수정한다. 처음부터 “사용할 정의만” 새 파일로 옮기는 선별 활성화는 금지한다.

### 7.17 다이묘 저택 충성도와 세금 계산

`je_bakuhantaisei`의 지역 정치는 바닐라 다이묘 인물 시스템을 정본으로 사용한다. 현행 바닐라의 `country_calculate_and_cache_daimyo_loyalties_per_state`를 호출해 `building_manor_house`를 holding으로 가진 살아 있는 magnate와 그 인물의 `daimyo_var`가 가리키는 주를 연결하고, 주에 저장된 `cached_daimyo_loyalty`를 읽는다.

처리 순서는 다음과 같다.

1. `je_meiji_restoration_update_daimyos` 또는 동등한 바닐라 갱신 effect를 먼저 실행한다.
2. 각 일본 편입 주에서 저택을 보유한 현존 다이묘와 `daimyo_var`의 일치를 검증한다.
3. 유효한 소유자가 하나면 그 인물의 `loyalty` 0~100을 해당 주의 단일 정치·세금 입력값 `L`로 사용한다.
4. 한 주에 유효한 저택 보유자가 여러 명이면 저택 소유 지분 가중평균을 사용한다. 엔진이 지분을 노출하지 않으면 가장 큰 holding을 가진 인물, 동률이면 prominence가 높은 인물을 정본 소유자로 고르는 결정적 규칙을 사용한다.
5. 유효한 소유자가 없으면 바닐라 다이묘 배정·캐시를 한 번 재실행한다. 그래도 없으면 EAFP 세금 수정치를 적용하지 않고 진단 로그를 남기며 임의 인물을 만들지 않는다.

충성도 구간은 바닐라의 사용례에 맞춰 `L < 40`은 불충, `40 <= L <= 65`는 중립, `L > 65`는 충성으로 통일한다. 종전의 `independency` 변수는 만들지 않으며 반막부 사건 확률·보신전쟁 반응·청원 반발도 모두 이 구간 또는 연속값 `L`을 사용한다.

세금은 옛 시스템의 최대 25% 누수를 유지하면서 다음 하나의 산식으로 통일한다.

```text
주 세금 보존율 = 0.75 + 0.25 * (L / 100)
주 세금 누수율 = 0.25 * (1 - L / 100)
```

따라서 충성도 0인 주는 산출 세금의 75%를 보존하고, 충성도 100인 주는 100%를 보존한다. 계산은 주별 modifier 하나로만 반영하며 지역 JE, `goryo`, `independency`, `reduce_nidome`와 어떤 숨은 보정도 중첩하지 않는다.

### 7.18 중복 인물 제거와 참조 통합

중복 여부는 표시명만이 아니라 역사적 인물, 생년, 역할, template ID와 바닐라 생성 경로를 함께 비교해 판정한다. 결과는 `japan_legacy_character_identity_map.md`에 `옛 EAFP 템플릿 → 바닐라 정본 템플릿 → 참조 파일 → 보존할 EAFP 고유 속성` 형식으로 기록한다.

1차 정적 대조에서는 옛 최상위 일본 템플릿 973개와 현행 바닐라 일본 템플릿 112개를 비교했다. 접두사·`_template`을 제거하고 이름 토큰 순서를 정규화했을 때 EAFP 정의 64개가 바닐라 정본 62명과 일치했다. 여기에 성씨 대신 황실명 `yamato`를 쓰는 `ninko`, `komei`, `meiji`, `taisho`, `showa` 5개를 의미상 중복으로 추가한다. 따라서 구현 착수 시 최소 69개 EAFP 정의·67명 정본을 우선 제거·통합 대상으로 확정하고, 일본어 표기·생년·역할 비교로 나머지 후보를 추가한다.

핵심 수동 매핑 예시는 다음과 같다.

| 옛 EAFP 정의 | 바닐라 정본 |
|---|---|
| `eafp_jap_tokugawa_iesada_template` | `JAP_iesada_tokugawa` |
| `eafp_jap_tokugawa_iemochi_template` / `eafp_tokugawa_iemochi` | `JAP_iemochi_tokugawa` |
| `eafp_jap_tokugawa_yoshinobu_template` | `JAP_yoshinobu_tokugawa` |
| `eafp_jap_tokugawa_iesato_template` | `JAP_iesato_tokugawa` |
| `eafp_jap_ninko_template` / `komei` / `meiji` / `taisho` / `showa` | 대응 `JAP_*_yamato` 템플릿 |
| `eafp_jap_mizuno_tadakuni_template` | `JAP_tadakuni_mizuno` |
| `eafp_jap_hotta_masayoshi_template` / `eafp_hotta_masayoshi` | `JAP_masayoshi_hotta` |
| `eafp_jap_ii_naoaki_template` | `JAP_ii_naoaki` |
| `eafp_ii_naosuke` | `JAP_ii_naosuke` |
| `eafp_iwakura_tomomi` | `JAP_iwakura_tomomi` |
| `eafp_sakamoto_ryoma` | `JAP_sakamoto_ryoma` |
| `eafp_yamagata_aritomo` / `eafp_ito_hirobumi` | 대응 `JAP_*` 템플릿 |

- 정확한 중복은 EAFP character template 정의를 활성화하지 않고 제거한다.
- 모든 이벤트, scripted effect, scripted trigger, history, on_action, JE와 saved scope의 옛 ID 참조를 바닐라 ID 또는 공용 resolver로 교체한다.
- 인물 생성 effect는 살아 있는 정본 인물을 먼저 찾고, 부재 시 바닐라 템플릿으로만 생성한다. legacy 템플릿 fallback은 두지 않는다.
- EAFP 고유 특성·이념·파벌 역할은 정본 인물에게 조건부 effect로 한 번만 적용한다.
- EAFP에만 있는 인물은 기존 템플릿과 자산을 유지하되 정본 인물과 같은 역할 슬롯을 중복 점유하지 않게 검사한다.
- 인물 통합은 신게임의 정의·생성·참조 경로에만 적용한다. 구버전 세이브에 이미 존재하는 중복 인물·saved scope·변수·관직·파벌 역할을 재결속하거나 제거하는 effect는 만들지 않는다.
- 다이묘, 쇼군·천황 승계, 덴포 파벌, 메이지·보신전쟁 사건은 identity map 적용 뒤 모두 회귀 시험한다.

## 8. 활성 충돌 정리

### 8.1 `REPLACE:JAP`

- 바닐라 일본 정의와 EAFP 정의의 실제 차이를 자동 비교한다.
- `religion = shinto`가 없어도 시작 종교·법률·사건이 정상인지 테스트한다.
- 차이가 불필요하면 `REPLACE:JAP`를 제거한다.
- 특정 EAFP 판정만 필요하다면 국가 정의 전체 교체 대신 scripted trigger 또는 초기화 효과를 사용한다.
- 전체 교체가 불가피하면 기준 버전과 자동 diff가 있는 생성형 호환 패치로 관리한다.

### 8.2 `REPLACE:japanese`

1. 기존 문화 정의를 교체하지 않고 이름을 추가할 수 있는 현행 문법을 먼저 확인한다.
2. 부분 확장이 불가능하면 바닐라 일본 문화 정의를 원본으로 삼아 EAFP 인명만 주입하는 생성형 파일을 사용한다.

생성형 파일은 바닐라의 모든 비인명 필드와 현행 외교조약 인장 텍스처를 보존해야 한다. 기준 바닐라 버전·원본 체크섬을 기록하고, 인명 풀 이외의 수동 변경을 금지한다.

### 8.3 메이지 로컬라이징

- 영어·중국어 활성 `replace` 파일과 한국어 비활성 `replace` 파일의 옛 문구를 먼저 원문 보관 manifest에 복사한다.
- `je_meiji_main/economy/army/diplomacy`의 표시 문구는 현행 바닐라 키와 의미를 유지하고, 옛 EAFP 문구 중 재사용하는 부분만 최신화한 설명·사건 키에 병합한다. 바닐라 최신 필드를 지우는 전면 `replace`는 남기지 않는다.
- 옛 `meiji.*` 사건 중 바닐라와 ID·기능이 정확히 충돌하는 것만 `eafp_jap_meiji_legacy.*`로 바꾸고 현행 메이지 사건 풀에 연결한다.
- `dyn_c_japan_shogunate` 같은 명칭 변경은 폐기하지 않고 EAFP 사건 내부의 표시명 또는 조건부 dynamic name으로 이관한다.
- 한국어·영어·중국어의 원본-활성 키 매핑을 비교해 모든 옛 문자열에 대응 활성 키가 존재하게 한다.

### 8.4 아시아 군사 편제

- 바닐라와 EAFP의 `06_military_formations_asia.txt`를 비교한다.
- EAFP의 조선 추가분을 별도 파일로 이관한다.
- 바닐라 경로를 가리는 EAFP 복사본을 제거한다.
- 일본 편제는 바닐라 원본이 그대로 로드되는지 확인한다.

### 8.5 고아 정의

- `dp_boshin_war`는 독립 외교전 정의로 재사용하지 않되 옛 조건·툴팁을 연결하는 namespaced wrapper로 보존
- 옛 수정치는 먼저 전부 활성 이관하고 충돌 키만 이름 변경
- 비활성 JE를 참조하던 정치운동 지지도 규칙은 살아남는 원래 JE 또는 지정된 바닐라 JE에 다시 연결
- 삭제된 지역·정책 JE만 참조하는 수정치·버튼·진행 막대·로비 현지화는 함께 제거
- 조선 AI 전략의 옛 일본 판정을 연결 계층으로 이동 또는 제거

## 9. 지원 세이브 정책

일본 콘텐츠 리뉴얼은 **리뉴얼 적용 후 시작한 신게임만 지원**한다. 리뉴얼 이전 EAFP 세이브를 새 구조로 변환하는 save migration은 구현하지 않는다.

- `eafp_jap_content_version`, v3/v4 migration effect와 migration runner를 만들지 않는다.
- 삭제된 JE·modifier·변수·saved scope를 탐지하거나 정리하기 위한 tombstone 정의와 legacy footprint 판정을 만들지 않는다.
- 옛 메이지·홋카이도·덴포·지역·정책·데라코야·재벌 진행도를 새 JE나 namespaced 변수로 승계하지 않는다.
- migration 목적으로 바닐라 JE를 강제 추가·완료하거나 옛 보상·영토·인물 상태를 소급 적용하지 않는다. `je_taming_the_north` 역시 바닐라의 신게임 개시 조건으로만 시작한다.
- 중복 인물 제거는 신게임에서 정의와 호출 경로를 정본화하는 정적 작업으로 한정한다. 기존 세이브에 이미 생성된 중복 인물·역할·saved scope는 재결속하지 않는다.
- 리뉴얼 이전 세이브의 로드 성공, 고아 JE 정리, 진행도 보존과 결과 일치는 지원·검증 항목에서 제외한다.
- 리뉴얼 버전으로 시작한 캠페인의 저장·재로드 안정성은 일반 회귀 검증으로 다루되, 이를 구버전 세이브 migration으로 간주하지 않는다.

## 10. 구현 단계와 통과 조건

### 0단계: 기준선과 호환성 명세

- [x] 바닐라 일본 JE·사건·변수·회사·인물 목록 고정
- [x] 옛 EAFP 일본 콘텐츠 기능별 목록 작성
- [x] 비활성 이벤트 156개와 현지화 원본 파일별 수량 목록 작성
- [x] `japan_vanilla_compatibility_matrix.md` 작성
- [x] `japan_legacy_content_migration_manifest.md` 설계
- [x] 바닐라 전체 복사 파일과 `replace` 파일 목록 작성
- [x] 기준 파일 체크섬 또는 diff 절차 마련

통과 조건: 모든 일본 기능에 소유자와 처리 방향이 지정되고 활성 충돌 파일이 빠짐없이 목록화되어 있다.

### 1단계: 일본 `.disable` 파일 전면 활성 복원

- [x] 일본 관련 `.disable` 파일과 간접 의존 파일 최종 목록 확정: 53개
- [x] 각 원본의 상대 경로·체크섬·활성 목적 경로 manifest 등록
- [x] `common`·`events`·history 스크립트를 같은 경로의 `.txt`로 무수정 복사
- [x] localization 파일을 같은 경로의 `.yml`로 무수정 복사
- [x] 인물 템플릿을 포함한 삭제·중복 예정 파일도 예외 없이 활성 복원
- [x] 수정 전 활성 복원 기준선 체크섬 작성
- [x] 전면 복원 상태의 최초 오류 로그와 중복 키 보고서 저장
- [x] 원본 `.disable` 파일이 수정되지 않았는지 확인

통과 조건: manifest에 등록된 모든 일본 `.disable` 파일에 내용이 동일한 활성 `.txt` 또는 `.yml` 복사본이 존재하고, 후속 수정 전 기준선과 최초 로드 로그가 보존되어 있다.

### 2단계: P0 충돌 제거

- [x] 메이지 JE·이벤트의 바닐라 키·경로 덮어쓰기 제거
- [x] 메이지 DLC localization 직접 덮어쓰기 문구를 legacy 키로 이관
- [x] 국가·국기 `REPLACE:JAP` 제거
- [x] 일본 문화 정의를 현행 바닐라 기준 생성형 패치로 갱신
- [x] 류큐 JE 전체 재정의를 EAFP 조선 개입 사이드카로 분리
- [x] 옛 EAFP 재벌 JE·청원 JE·이벤트·전용 지원 자산 제거 및 `company_sumitomo` 바닐라 정본화
- [x] 아시아 군사 편제 전체 복사본을 한국 추가분과 비일본 변경으로 분해
- [x] README·Steam 설명·메타데이터 버전 표기 동기화
- [x] P0 전후 정적 diff와 Victoria 3 초기 로드 비교 보고서 작성

통과 조건: 바닐라 일본 국가·국기·메이지·류큐·재벌·회사·군사 편제 정본이 정상 로드되고, EAFP가 의도적으로 유지하는 일본 문화 생성형 패치를 제외하면 일본 관련 `REPLACE:`·동일 키·동일 경로 전체 복사가 없다. 최초 로드에서 확인된 `je_ryukyu_rivalry`, `je_zaibatsu`, `company_sumitomo` 중복과 메이지 원본 경로 가림이 사라지며, 바닐라 비인명 문화 필드가 모두 보존되어야 한다.

#### 2.0 범위와 구현 순서

P0는 “바닐라 정본을 로드 순서에서 되찾는 단계”다. 옛 콘텐츠의 세부 문법과 게임플레이를 모두 고치지 않고, 동일 경로·동일 키·`REPLACE:`로 바닐라 콘텐츠를 가리는 문제부터 제거한다.

구현 순서는 다음과 같이 고정한다.

1. `japan_stage1_initial_load_report.md`의 중복·경로 가림 오류를 P0 기준선으로 고정한다.
2. 메이지 이벤트의 동일 경로 가림을 먼저 제거한다.
3. 국가·국기·메이지 JE의 `REPLACE:`를 제거한다.
4. 류큐 동일 키는 sidecar로 전환하고, 옛 재벌 체인은 제거하며, 중복 회사는 바닐라 정본 참조로 전환한다.
5. 일본 문화 생성형 패치를 현행 바닐라 기준으로 다시 만든다.
6. 아시아 군사 편제 전체 복사본을 제거하고 EAFP 추가분을 별도 파일로 분리한다.
7. localization과 문서 버전을 정리한다.
8. 정적 검사 후 Victoria 3를 다시 초기 로드해 P0 전후 로그를 비교한다.

다음 작업은 P0에서 수행하지 않는다.

- 7개 지역 막번체제 JE와 goryo·independency 제거
- 다이묘 저택 충성도·세금 공식 구현
- 막부 정책·청원 JE 8개 제거
- 덴포 기근 사건의 바닐라 JE 병합
- 옛 이념·주·국가 ID의 전체 치환
- 중복 인물 69개 이상의 일괄 제거

이 항목들은 P0에서 바닐라 정본을 되찾은 뒤 3·4·8단계에서 처리한다. 다만 P0 파일을 로드하지 못하게 만드는 직접 중복 참조는 임시 namespaced adapter로 연결할 수 있다.

#### 2.1 변경 전 안전장치와 산출물

- 53개 무수정 활성 복원본의 SHA-256은 `japan_legacy_content_migration_manifest.md`에 남겨둔다.
- P0에서 수정하는 파일마다 `원본 .disable → 무수정 활성본 → P0 결과` 3방향 diff를 기록한다.
- 새 문서 `documentation/japan_p0_collision_resolution.md`에 충돌 키, 바닐라 소유자, EAFP 새 목적지, 변경 파일과 검증 결과를 기록한다.
- 삭제가 필요한 활성 복원본은 원본 `.disable`을 지우지 않는다. Git에서 활성 파일을 rename·분리하거나 정의 블록을 제거해 회귀 비교가 가능하게 한다.
- 각 작업 묶음은 아래 순서대로 독립 검증하며, 다음 묶음에서 이전 묶음의 오류가 재발하면 진행하지 않는다.

#### 2.2 메이지 JE·이벤트 정본 복구

대상 파일:

- `common/journal_entries/eafp_00_meiji_restoration.txt`
- `common/history/countries/jap - japan.txt`
- `events/meiji_restoration.txt`
- `localization/english/replace/jap_replace_l_english.yml`
- `localization/korean/replace/jap_replace_l_korean.yml`
- `localization/simp_chinese/replace/jap_replace_l_simp_chinese.yml`
- 세 언어 `eafp_japan_l_*.yml`

현재 문제는 두 종류다. JE 파일은 `REPLACE:je_terakoya`, `REPLACE:je_meiji_restoration`, `REPLACE:je_meiji_main/economy/army/diplomacy`로 바닐라 정의를 교체한다. 이벤트 파일은 바닐라와 같은 `events/meiji_restoration.txt` 경로와 `meiji.1-13` 네임스페이스를 사용해 바닐라 1.13.11의 `meiji.1-14` 파일 전체를 가린다.

구현 작업:

1. `events/meiji_restoration.txt`를 바닐라와 겹치지 않는 `events/eafp_jap_events/eafp_meiji_restoration_legacy.txt`로 이동한다.
2. namespace를 `eafp_jap_meiji_legacy`로 바꾸고 `meiji.1-13`을 `eafp_jap_meiji_legacy.1-13`으로 일괄 매핑한다.
3. 이벤트 내부의 자기 호출, JE 호출, on_action, scripted effect와 localization 키를 새 ID로 함께 바꾼다. 바닐라 `meiji.*` 호출이 필요한 곳은 명시적 bridge effect를 거쳐 호출한다.
4. `je_terakoya`는 정의 자체를 삭제하고 대체 legacy JE를 만들지 않는다. `common/history/countries/jap - japan.txt`의 시작 호출, 전용 modifier·tooltip·event·effect·trigger·localization 참조도 함께 제거한다. 옛 세이브 cleanup이나 대체 상태 이관 effect는 만들지 않는다.
5. 옛 `je_meiji_restoration`만 `je_eafp_jap_legacy_meiji_restoration`으로 바꿔 EAFP 동반 JE로 보존한다.
6. 옛 `je_meiji_main/economy/army/diplomacy` 정의는 P0 활성 파일에서 제거한다. 이 네 키는 바닐라만 정의하게 하고, EAFP 사건 연결은 후속 호환 파일의 on_action·event pool adapter로 추가한다.
7. 새 legacy JE에서 바닐라 완료 변수나 정권 교체를 직접 쓰는 effect는 P0에서는 비활성 wrapper로 바꾸고 3단계에서 구현한다.
8. 세 언어 `replace/jap_replace`에서 `je_meiji_main`, `meiji.1.*`, `meiji.2.a`와 같은 바닐라 키를 제거한다.
9. 보존 대상인 옛 메이지 문구는 `je_eafp_jap_legacy_*`, `eafp_jap_meiji_legacy.*` localization으로 복사한다. `je_terakoya` 전용 문구는 재사용 호출이 없는 것을 확인한 뒤 삭제 목록에 기록한다.
10. `dyn_c_japan_shogunate`는 바닐라 replace에서 제거하고 필요한 EAFP 표시명은 별도 namespaced custom localization으로 이전한다.

정적 완료 조건:

- 활성 파일에 `REPLACE:je_meiji_`, `namespace = meiji`가 없으며 `je_terakoya` 정의·시작 호출·전용 자산 참조가 0개다.
- 모드의 `events/meiji_restoration.txt`가 존재하지 않고 바닐라 동경로 파일이 로드된다.
- `meiji.1-14`는 바닐라에서만 정의되고, 옛 13개 사건은 `eafp_jap_meiji_legacy.1-13`으로 한 번씩 정의된다.
- 세 언어 replace 폴더가 바닐라 `je_meiji_*`, `meiji.*` 문자열을 직접 덮지 않는다.

#### 2.3 일본 국가·국기 `REPLACE:JAP` 제거

대상 파일:

- `common/country_definitions/eafp_countries.txt`
- `common/flag_definitions/eafp_jap_flag_definitions.txt`

국가 정의의 EAFP `JAP` 블록은 바닐라 1.13.11과 비교하면 사실상 `religion = shinto`만 추가하고 국가 전체를 교체한다. 이 전체 교체 때문에 향후 바닐라가 국가 필드를 추가할 때 누락될 수 있다.

구현 작업:

1. `eafp_countries.txt`에서 `REPLACE:JAP` 블록 전체를 제거해 바닐라 `JAP` 정의를 그대로 로드한다.
2. 시작 종교가 실제 history·법률·인구·DLC 초기화로 올바르게 정해지는지 확인한다.
3. EAFP만의 신토 초기화가 여전히 필요하면 국가 정의가 아니라 `on_game_start` 단발 effect 또는 국가 history의 최소 필드로 옮긴다. 바닐라 시작 상태와 동일하면 해당 추가 자체를 폐기한다.
4. 국기 파일의 `REPLACE:JAP`도 제거한다. 현행 바닐라의 쇄국·개항 도쿠가와기, 태군정, 불교·신토 신정, 군사정권·공화정·파시스트·공산주의 분기를 정본으로 사용한다.
5. EAFP의 `bakufu_kaikaku_complete_var`, `meiji_var` 기반 국기 분기는 바닐라 법률 기반 분기와 중복되므로 P0에서는 사용하지 않는다. 고유 국기 자산은 삭제하지 않고 후속 풍미 확장 후보로만 남긴다.
6. 같은 파일의 `RYU`, `NIP`, `JSN` 정의는 별도 블록으로 분리해 P0 일본 정본 수정과 섞이지 않게 한다. 존재하지 않는 `NIP`·`JSN`의 처리 자체는 4단계 국가 ID 이관에서 결정한다.

완료 조건:

- 활성 `common/**`에 일본 국가 또는 국기를 대상으로 하는 `REPLACE:JAP`가 없다.
- 바닐라 `JAP`의 `color`, `country_type`, `social_hierarchy`, `tier`, `cultures`, `capital`이 원본과 일치한다.
- 쇄국 막부, 개항 막부, 태군정, 제정, 공화정, 군사정권, 불교·신토 신정 국기 조건이 바닐라와 동일하게 남는다.

#### 2.4 일본 문화 생성형 호환 패치

대상 파일:

- `common/cultures/00_cultures_jap.txt`
- 바닐라 `common/cultures/00_cultures.txt`의 `japanese` 블록

옛 EAFP의 대규모 일본 이름 풀은 보존해야 하지만 현재 `REPLACE:japanese`는 현행 바닐라의 비인명 필드를 누락할 수 있다. 단순히 `REPLACE:`를 제거하면 같은 문화 키가 중복되고, 파일을 삭제하면 옛 이름 풀이 사라진다. 따라서 이 한 항목만 의도적인 생성형 `REPLACE:japanese` 예외로 관리한다.

생성 규칙:

1. 기준 바닐라 파일 경로·게임 버전·SHA-256을 생성 파일 머리와 호환성 문서에 기록한다.
2. 바닐라 `japanese` 블록을 기준으로 복사하고 `color`, `religion`, `heritage`, `language`, `traditions`, `name_format`, `obsessions`, `taboos`, `graphics`, 외교조약 인장 texture 등 모든 비인명 필드를 그대로 보존한다.
3. 남녀 이름과 성씨 목록만 바닐라 목록과 EAFP 목록의 안정적 합집합으로 생성한다.
4. 중복은 대소문자·공백·장음 표기 정규화 후 제거하되 실제로 다른 철자를 임의 통합하지 않는다.
5. 바닐라 이름을 먼저 유지하고 EAFP 고유 이름을 원본 순서로 뒤에 추가한다.
6. 생성 결과에서 이름 목록 외 필드의 semantic diff가 0인지 자동 검사한다.
7. 바닐라 원본 SHA-256이 바뀌면 생성 작업과 검증이 실패하도록 한다.

완료 조건:

- `REPLACE:japanese`는 이 생성 파일 한 곳에만 존재한다.
- 바닐라와의 semantic diff는 이름 배열에만 존재한다.
- 바닐라 이름 누락 0개, EAFP 이름 누락 0개, 생성 결과 내부 중복 0개다.
- 현행 `graphics`와 외교조약 인장 texture를 포함한 비인명 필드가 모두 보존된다.

#### 2.5 류큐 경쟁 전체 재정의 제거

대상 파일:

- `common/journal_entries/eafp_01_ryukyu_rivalry.txt`
- `common/scripted_buttons/eafp_ryukyu_buttons.txt`
- `events/eafp_ryukyu_events.txt`
- 세 언어 `eafp_ryukyu_l_*.yml`

구현 작업:

1. EAFP 파일에서 `je_ryukyu_rivalry` 전체 정의를 제거해 바닐라 JE가 유일한 정본이 되게 한다.
2. 조선의 개입 선택은 `je_eafp_ryukyu_intervention`이라는 별도 sidecar JE로 재구성한다.
3. sidecar는 바닐라 `je_ryukyu_rivalry`가 활성이고 조선이 관련 조건을 만족할 때 한 번만 생성한다.
4. 기존 조선 버튼은 sidecar에만 표시한다. 필요한 경우 `je:je_ryukyu_rivalry` 스코프를 통해 바닐라 진행 막대에 제한된 수치만 전달하되 최종 승패·영토 귀속·JE 완료 effect는 호출하지 않는다.
5. `eafp_ryukyu_events.txt`의 이벤트는 중립·청 지지·일본 지지·독자 중재 결과만 소유한다.
6. 바닐라 JE가 완료·실패·무효화되면 sidecar도 즉시 정리하고 재생성 방지 플래그를 남긴다.
7. 기존 localization의 `$je_ryukyu_rivalry$` 표시는 바닐라 키를 그대로 참조하되 EAFP sidecar의 제목·상태·버튼은 namespaced 키를 사용한다.

완료 조건:

- `je_ryukyu_rivalry` 정의는 바닐라에만 존재한다.
- `je_eafp_ryukyu_intervention` 없이 조선 버튼·사건이 발동하지 않는다.
- 일본 승리·청 승리·기한 종료·류큐 소멸 경로에서 sidecar가 고아로 남지 않는다.
- 초기 로드 로그의 `Duplicated key je_ryukyu_rivalry`가 사라진다.

#### 2.6 옛 재벌 체인 제거와 스미토모 회사 정본화

대상 파일:

- `common/journal_entries/eafp_japan.txt`
- `common/company_types/eafp_companies_japan.txt`
- `common/scripted_triggers/eafp_jap_triggers.txt`
- `common/static_modifiers/EAFP_japan_modifiers.txt`
- `events/eafp_jap_events/eafp_zaibatsu_events.txt`
- 세 언어 `eafp_japan_l_*.yml`

구현 작업:

1. 옛 `je_zaibatsu` 및 이전 P0에서 임시 사용한 `je_eafp_jap_legacy_zaibatsu` 정의를 제거한다.
2. `je_zaibatsu_petition_government`, `je_zaibatsu_petition_rice`, `je_zaibatsu_petition_remove_monopoly` 정의와 진행 변수를 제거한다.
3. 활성 `eafp_zaibatsu_events.txt`를 삭제하고 `zaibatsu_events.1-4` 호출 및 고아 `.101` localization까지 제거한다. 원본 `.disable`은 이관 대조본으로만 보존한다.
4. 재벌 체인 전용 `is_zaibatsu_company` trigger와 `zaibatsu_cooperation_modifier`를 제거한다.
5. EAFP `company_sumitomo` 정의를 제거하고 바닐라 공식 회사 정의는 그대로 사용한다.
6. EAFP 고유 `company_zohiko`, `company_daiichi_kokuritsu_bank`는 재벌 JE와 분리된 일반 고유 회사로 유지하되 현행 건물·상품·potential trigger를 별도 검증한다.
7. 세 언어 localization에서 옛 재벌 JE·청원·사건·전용 modifier 키를 제거하고 바닐라 제목·설명을 덮지 않는다.

완료 조건:

- `je_zaibatsu`와 `company_sumitomo` 정의는 바닐라에만 존재한다.
- 활성 EAFP 파일에 옛 재벌 JE 4개, `zaibatsu_events`, 전용 trigger·modifier·localization 참조가 0개다.
- 초기 로드 로그의 두 duplicated key 메시지가 사라진다.

#### 2.7 아시아 군사 편제 전체 복사본 분리

대상 파일:

- `common/history/military_formations/06_military_formations_asia.txt`
- 바닐라 동경로 파일

현재 diff는 세 부분이다.

- 중국 정홍기 HQ를 `region_northeast_asia`에서 `region_north_china`로 바꾼 1건
- 중국 부대의 `STATE_OUTER_MANCHURIA`를 `STATE_YUNNAN`으로 바꾼 1건
- 152줄 규모의 조선군·수군 초기 편제 추가

구현 작업:

1. 바닐라 동경로를 가리는 EAFP `06_military_formations_asia.txt`를 제거한다.
2. 조선 추가 블록만 `common/history/military_formations/eafp_korea_military_formations.txt`로 옮기고 독립 `MILITARY_FORMATIONS = { c:KOR ?= { ... } }` 구조로 만든다.
3. 조선 함대의 unit type·service type·state·장군 transfer가 1.13.11 문법에 맞는지 검증한다. 최초 로드의 fleet combat unit 오류도 이 파일에서 해결한다.
4. 중국의 두 줄 변경은 일본 P0와 분리한다. 현행 바닐라 오류 수정으로 더 이상 필요하지 않으면 폐기하고, 필요성이 확인되면 중국 전용 history/on_action 보정으로 별도 설계한다. 이 두 줄 때문에 바닐라 전체 파일 복사를 유지하지 않는다.
5. 바닐라 파일 SHA-256이 호환성 기준선과 같은지 검사해 원본이 그대로 로드되는지 확인한다.

완료 조건:

- 모드에 `common/history/military_formations/06_military_formations_asia.txt`가 없다.
- 조선 편제는 신게임에서 정확히 한 번 생성되고 바닐라 일본·중국 편제는 바닐라 원본과 일치한다.
- `create_military_formation ... Combat units are not applicable for fleets` 오류가 사라진다.

#### 2.8 README·메타데이터 동기화

현재 `.metadata/metadata.json`과 Steam 설명은 모드 `2.2.0`, 게임 `1.13.*`를 가리키지만 README는 `2.1.0`, `1.10.*`로 남아 있다.

구현 작업:

1. README를 모드 `2.2.0`, 게임 `1.13.*`, 모든 공식 DLC 필수로 갱신한다.
2. `.metadata/metadata.json`의 `version = 2.2.0`, `supported_game_version = 1.13.*`와 일치시킨다.
3. `steamdesc.txt`와 `changelog.txt`에 일본 리뉴얼이 전면 복원 기준선에서 진행 중임을 기록하되, P0만 끝난 상태를 전체 리뉴얼 완료로 표시하지 않는다.
4. 호환성 기준 바닐라 1.13.11과 Steam 빌드 번호는 개발 문서에만 기록하고 공개 지원 범위는 `1.13.*`로 유지한다.

#### 2.9 검증 계획

정적 검사는 다음 순서로 수행한다.

1. `REPLACE:JAP`, `REPLACE:je_meiji_*`가 활성 일본 파일에서 0개인지 검사하고, `je_terakoya`, `je_eafp_jap_legacy_terakoya`, `modifier_jap_terakoya`, `modifier_legacy_of_terakoya`의 정의·호출·현지화가 0개인지 별도로 검사한다.
2. 의도적인 생성형 `REPLACE:japanese`가 정확히 1개인지 검사한다.
3. `je_ryukyu_rivalry`, `je_zaibatsu`, `company_sumitomo`, `meiji.*`의 활성 정의 수를 세어 바닐라 외 EAFP 중복이 없는지 확인한다.
4. 모드가 바닐라와 같은 상대 경로로 가리는 일본 파일이 `japan_p0_collision_resolution.md`의 승인된 예외 외에는 없는지 검사한다.
5. 세 언어 canonical 메이지 localization 키가 replace 폴더에 없는지 검사한다.
6. 일본 문화 생성 파일을 바닐라 원본과 semantic diff해 이름 목록 외 차이가 0인지 확인한다.
7. 원본 `.disable` 53개의 SHA-256이 1단계 manifest와 동일한지 다시 확인한다.

런타임 검사는 다음 경로로 수행한다.

1. 모든 DLC와 EAFP만 활성화한 별도 P0 검증 playset을 사용한다. 다른 Workshop 모드가 섞인 1단계 로그는 비교 기준으로만 사용한다.
2. `victoria3_win_console.exe -debug_mode`로 메인 메뉴 초기화를 완료한다.
3. `error.log`, `debug.log`, `game.log`, `database_conflicts.log`를 `documentation/japan_p0_*` 이름으로 보존한다.
4. `Duplicated key je_ryukyu_rivalry`, `je_zaibatsu`, `company_sumitomo`가 0개인지 확인한다.
5. 바닐라 `meiji.14`, 현행 메이지 JE 6개, 바닐라 일본 국기·문화 필드가 데이터베이스에 존재하는지 확인한다.
6. 1836 일본 신게임에서 국가·문화·국기·초기 편제·쇄국·메이지 선행 조건이 바닐라 기준으로 표시되고, 데라코야 JE와 전용 수정치가 시작 시점 및 이후 플레이에서 생성되지 않는지 확인한다.
7. 청·조선의 초기 편제가 중복 생성되지 않는지 확인한다.
8. P0 이후에도 남는 옛 이념·`NIP`·지역 JE 오류는 후속 단계 backlog로 분리하되, 새 duplicate key·missing vanilla field·동일 경로 shadow 오류는 허용하지 않는다.

#### 2.10 권장 변경 단위

1. `P0 restore vanilla Meiji ownership`
   - 메이지 JE `REPLACE:` 제거, 이벤트 path·namespace 이동, localization namespacing
2. `P0 restore vanilla Japan country and flags`
   - 국가·국기 `REPLACE:JAP` 제거와 최소 초기화 분리
3. `P0 regenerate Japanese culture compatibility patch`
   - 바닐라 필드 보존, 이름 풀 안정적 합집합, checksum guard
4. `P0 split Ryukyu intervention sidecar`
   - 바닐라 류큐 JE 정본 복구와 조선 개입 분리
5. `P0 remove legacy Zaibatsu and canonicalize Sumitomo`
   - 옛 재벌 JE·청원·이벤트·전용 자산 제거와 바닐라 회사 참조
6. `P0 split Asian military formation history`
   - 바닐라 전체 복사 제거, 조선 추가분 분리, 중국 변경 별도 판정
7. `P0 metadata and validation`
   - README·메타데이터 동기화, 정적 검사, 초기 로드 비교 보고서

### 3단계: 연결 계층과 정본화

#### 3.0 현재 상태와 단계 경계

2단계 종료 시점에는 예정했던 `eafp_japan_vanilla_bridge.txt`, 연결 effect 파일과 전용 on_action 파일이 아직 존재하지 않는다. `common/on_actions/japan_code_on_actions.txt`는 1단계에서 원형 복원됐지만 `00_code_on_actions_definition.txt`의 일본 연결은 모두 주석 상태다. 또한 `je_eafp_jap_legacy_meiji_restoration`은 `possible = { always = no }`인 휴면 JE이고, 옛 메이지 사건 13개는 namespaced 이벤트 파일로 옮겨졌지만 여전히 바닐라 변수·JE를 직접 쓰는 구간이 남아 있다. 따라서 기존 완료 표시는 잘못된 선행 표기이며 아래 항목을 실제 구현 대상으로 되돌린다.

- [x] `common/scripted_triggers/eafp_japan_vanilla_bridge.txt` 구현
- [x] `common/scripted_effects/eafp_japan_vanilla_bridge_effects.txt` 구현
- [x] `common/scripted_effects/eafp_japan_character_bridge_effects.txt` 구현
- [x] `common/on_actions/eafp_japan_on_actions.txt` 구현과 최소 전역 연결
- [x] 전체 DLC 전제의 바닐라-EAFP 상태 adapter 구현
- [x] 옛 `je_hokkaido` 삭제와 바닐라 북방 체인 연결 구현
- [x] 중복 인물 identity map과 신게임 정본 참조 구현
- [ ] 신게임 반복 저장·로드 및 bridge idempotency 검증

3단계는 연결 API, P0 이관과 옛 `je_hokkaido`의 바닐라 북방 체인 병합을 구현한다. 구버전 세이브 변환은 범위에 포함하지 않는다. 다음 작업은 4단계 소유이므로 이 단계에서 실행하지 않는다.

- 7개 지역 막번체제 JE, goryo·independency와 `reduce_nidome*` 제거
- 8개 막부 정책·청원 JE 제거
- `je_tenpo_famine` 삭제와 7개 기근 사건의 실제 재배치
- 저택 보유 다이묘 충성도 기반 세금 공식 적용
- `japan_code_on_actions.txt` 전체 재활성화

3단계에서는 P0에서 제거한 항목을 다시 다루지 않고 신게임에서 호출 가능한 정의와 연결만 정리한다. 4단계 삭제분 역시 별도 migration 없이 활성 정의·history·on_action·호출 그래프에서 제거한다. 옛 재벌 JE·청원·이벤트는 bridge 대상이 아니며 어떤 형태의 companion이나 tombstone JE로도 되살리지 않는다.

#### 3.1 산출물과 파일별 책임

| 파일 | 책임 | 직접 허용되는 바닐라 접근 |
|---|---|---|
| `common/scripted_triggers/eafp_japan_vanilla_bridge.txt` | 바닐라 일본 상태를 안정적인 EAFP 판정으로 변환 | `has_journal_entry`, 현행 법률, 공식 완료 변수와 script value 읽기만 허용 |
| `common/scripted_effects/eafp_japan_vanilla_bridge_effects.txt` | 동반 JE 시작·종료, EAFP 결과 플래그 설정, 안전한 사건 예약 | 공식 JE add/remove와 구버전 상태 변환 금지 |
| `common/scripted_effects/eafp_japan_character_bridge_effects.txt` | 신게임의 바닐라 정본 인물 탐색과 정상 생성 경로의 saved scope 저장 | 바닐라 인물 템플릿과 공식 인물 역할 참조 |
| `common/on_actions/eafp_japan_on_actions.txt` | 신게임 월간 상태 동기화 | bridge effect만 호출하고 콘텐츠 로직이나 migration runner를 직접 갖지 않음 |
| `common/on_actions/00_code_on_actions_definition.txt` | `on_monthly_pulse_country`에 전용 일본 on_action 한 줄만 등록 | 기존 옛 일본 on_action의 일괄 주석 해제 금지 |
| `common/journal_entries/eafp_00_meiji_restoration.txt` | 휴면 companion의 개시·진행·종료 조건을 bridge trigger로 교체 | 공식 정권 교체·과제 완료 effect 금지 |
| `common/journal_entries/eafp_japan.txt` | 옛 `je_hokkaido` 제거, `je_karafuto`를 바닐라 북방 JE 성공 후속으로 전환 | 바닐라 북방 JE 재정의 금지 |
| `common/history/countries/eafp_japan_legacy.txt` | 옛 `je_hokkaido` 시작 호출 제거 | 바닐라 `je_taming_the_north`를 신게임 history에서 강제 추가 금지 |
| `common/scripted_progress_bars/eafp_hokkaido_progress_bars.txt` | 활성 파일 삭제, 원본 `.disable`만 대조본으로 보존 | 해당 없음 |
| `common/scripted_buttons/eafp_japan_buttons.txt` | 옛 홋카이도 JE 전용 버튼 4개 제거, 고유 성곽 선택지는 사건으로 이동 | 바닐라 북방 버튼 복제 금지 |
| `events/eafp_jap_events/eafp_meiji_restoration_legacy.txt` | 옛 13개 사건을 공식 메이지 단계의 풍미 사건으로 전환 | 공식 변수 write를 제거하고 bridge effect만 호출 |
| `events/eafp_jap_events/eafp_hokkaido.txt` | 옛 6개 사건을 바닐라 JE 진행 중·성공 후 위치로 재배치 | 바닐라 `hokkaido_events.*`와 ID·보상 중복 금지 |
| 세 언어 `eafp_japan_l_*.yml` | bridge tooltip과 namespaced 메이지 사건 문구 | 바닐라 localization key 덮어쓰기 금지 |
| `documentation/japan_stage3_bridge_report.md` | 상태 계약, 인물 identity map, 신게임 fixture 결과, 로그 checksum 기록 | 해당 없음 |

#### 3.2 구현 전 고정할 기준선

1. Victoria 3 1.13.11의 `00_meiji_restoration.txt`, `07_tenpo_crisis.txt`, `07_sakoku.txt`, `01_ryukyu_rivalry.txt`, `07_korea_colonization.txt`, 관련 script value·effect 파일의 SHA-256을 compatibility matrix에 기록한다.
2. 활성 EAFP 일본 스크립트에서 바닐라 소유 JE, 변수, global variable, 인물 템플릿을 읽거나 쓰는 모든 위치를 `read`, `write`, `create`, `remove`, `scope save`로 분류한다.
3. `events/eafp_jap_events/eafp_meiji_restoration_legacy.txt`의 13개 이벤트에는 선택지별 상태 변화 표를 작성한다. 바닐라 정권·법률·통치자·공식 과제·AI 전략을 바꾸는 effect는 제거 대상으로, EAFP 전용 풍미·일시 modifier·서사 플래그는 보존 대상으로 표시한다.
4. 1836 신게임에서 유신·북방·류큐의 시작 직전과 직후 상태를 재현할 테스트 시나리오를 마련한다. 모든 fixture는 리뉴얼 빌드에서 새로 만든다.
5. `.disable` 53개 checksum과 P0 로그를 다시 확인해 3단계가 원본 대조본을 변경하지 않는 것을 보장한다.

#### 3.3 bridge trigger 계약

trigger는 국가 scope에서 호출하는 것을 원칙으로 하고 이름은 전부 `eafp_japan_`으로 시작한다. 개별 이벤트는 아래 trigger를 사용하며 바닐라 내부 키를 다시 직접 읽지 않는다.

| trigger | `yes` 판정 | 사용처 |
|---|---|---|
| `eafp_japan_is_valid_country` | `JAP`가 존재하고 현재 scope이며 무효한 분리국·혁명국이 아님 | 모든 bridge의 선행 조건 |
| `eafp_japan_is_bakufu_era` | 막부 통치 법률·통치자 상태이며 유신 이후 상태가 아님 | 전기 막부 사건과 companion 개시 |
| `eafp_japan_is_open` | 바닐라 쇄국 JE 결과 또는 현행 무역·국경 법률상 개항 | 흑선·개항·외교 사건 |
| `eafp_japan_tenpo_crisis_active` | `has_journal_entry = je_tenpo_crisis` | 4단계 기근 사건 재배치의 단일 입구 |
| `eafp_japan_tenpo_reformer_faction` | `tenpo_reformer_goals_completed > tenpo_hardliner_goals_completed` | 히토쓰바시·개혁파 대응 |
| `eafp_japan_tenpo_conservative_faction` | `tenpo_hardliner_goals_completed > tenpo_reformer_goals_completed` | 난키·보수파 대응 |
| `eafp_japan_tenpo_balanced_factions` | 두 바닐라 script value가 같음 | 어느 쪽에도 이중 보상을 주지 않는 중립 경로 |
| `eafp_japan_restoration_active` | `je_meiji_restoration` 활성 | legacy restoration companion 동기화 |
| `eafp_japan_restoration_finished` | 공식 restoration JE가 없고 `je_meiji_main` 또는 확정된 유신 후 상태가 존재 | companion 종료와 후속 사건 개방 |
| `eafp_japan_meiji_main_finished` | bridge가 `je_meiji_main` 활성 상태를 관측한 뒤 JE가 닫혔고 공식 과제 또는 후속 상태가 존재 | `.2` 후일담과 EAFP 메이지 트랙 종료 |
| `eafp_japan_meiji_economy_finished` | `completed_je_meiji_economy` | 경제 풍미 사건 해금 |
| `eafp_japan_meiji_army_finished` | `completed_je_meiji_army` | 사무라이·군제 풍미 사건 해금 |
| `eafp_japan_meiji_diplomacy_finished` | 전체 DLC 환경의 `iwakura_mission_finished`와 현행 공식 후속 상태 | 외교·철도 풍미 사건 해금 |
| `eafp_japan_taming_north_active` | `has_journal_entry = je_taming_the_north` | `hokkaido.2-6` 사건 풀과 북방 진행 상태 동기화 |
| `eafp_japan_taming_north_succeeded` | active 상태를 과거에 관측했고 JE가 닫힌 뒤 `modifier_northern_learnings` 또는 동등한 공식 성공 상태가 존재 | `hokkaido.1` 후일담과 `je_karafuto` 개방 |
| `eafp_japan_taming_north_failed` | active 상태를 과거에 관측했고 JE가 닫혔으며 일본이 홋카이도 주를 상실 | EAFP 북방 사건 예약 취소와 cleanup |
| `eafp_japan_ryukyu_rivalry_active` | `je_ryukyu_rivalry` 활성이고 관련 국가 scope 유효 | 기존 조선 sidecar의 공통 판정 |
| `eafp_japan_korea_colonization_active` | `je_colonize_korea` 활성 | 정한론 후속 연결 |

바닐라 script value와 완료 변수는 이 bridge 파일에서만 읽는다. 공식 key가 패치로 변경되면 checksum guard와 정적 검색이 먼저 실패하게 만들고, 이벤트 쪽에 폴백 복제 로직을 넣지 않는다.

#### 3.4 bridge effect 계약

| effect | 입력/선행 조건 | 결과 | 금지 사항 |
|---|---|---|---|
| `eafp_japan_sync_vanilla_state_effect` | 유효한 `JAP` country | 아래 세부 sync effect를 고정 순서로 호출 | 정권·영토·법률 직접 변경 금지 |
| `eafp_japan_sync_meiji_companion_effect` | 유신 active/finished 판정 | companion 1회 개시, 진행 중단 또는 EAFP 전용 결말 플래그 설정 | `meiji_restoration_complete`, `meiji_var`, 공식 완료 변수 write 금지 |
| `eafp_japan_sync_meiji_tasks_effect` | 공식 과제 완료 변수 읽기 | namespaced EAFP 후속 사건 해금 플래그만 설정 | 공식 과제 JE 재추가·강제 완료 금지 |
| `eafp_japan_schedule_legacy_meiji_event_effect` | 사건별 선행 bridge trigger와 미발동 플래그 | 동일 사건을 한 번만 예약 | 월간 반복 예약, 바닐라 `meiji.*` 직접 호출 금지 |
| `eafp_japan_sync_northern_legacy_effect` | 바닐라 북방 JE active/succeeded/failed 판정 | 진행 중 사건 예약, 성공 후 `hokkaido.1`과 `je_karafuto`를 한 번만 연결 | 옛 `je_hokkaido` 재생성, 바닐라 완료 보상·영토 결과 복제 금지 |
| `eafp_japan_sync_ryukyu_sidecar_effect` | 바닐라 류큐 JE와 RYU/JAP/CHI scope 유효 | 조선 sidecar의 시작·무효화 상태만 정리 | 공식 승패 progress·귀속 변경 금지 |
| `eafp_japan_validate_bridge_state_effect` | debug 검증 때만 호출 | 모순 상태를 debug log용 플래그로 기록 | 플레이 효과나 보상 지급 금지 |

모든 동기화 effect는 같은 게임 상태에서 두 번 호출해도 두 번째 호출의 상태 변화가 0이어야 한다. 사건 예약 전용 flag는 예약 직전에 설정한다.

#### 3.5 on_action 구조

1. `eafp_japan_on_monthly_pulse_country` 하나를 새 파일에 정의하고 `c:JAP ?= THIS`와 국가 생존 판정으로 제한한다.
2. 실행 순서를 `신게임 정본 인물 scope 확인 → 바닐라 상태 sync → 사건 예약 → debug sanity check`로 고정한다.
3. `00_code_on_actions_definition.txt`의 기존 `on_monthly_pulse_country` 목록에 위 on_action 한 줄만 추가한다.
4. 옛 `japan_on_monthly_pulse_country`, `japan_on_character_death`, `japan_on_new_ruler` 등은 그대로 비연결 상태로 둔다. 1,300줄 이상의 옛 on_action을 일괄 활성화하면 지역 JE·중복 인물·구형 이념 오류가 동시에 돌아오므로 금지한다.
5. 즉시 동기화가 꼭 필요한 EAFP JE의 `on_complete/on_fail/on_invalid`에서는 bridge effect를 직접 호출하고, 바닐라 JE 완료 감지는 최대 한 달 지연을 허용한다. 바닐라 파일에 on_action을 삽입하거나 전체 파일을 복사하지 않는다.
6. 월간 pulse의 AI·플레이어 결과가 같아야 하며 UI 팝업 여부만 사건별로 구분한다.

#### 3.6 save migration 제외 규칙

3단계에는 구버전 세이브를 판별하거나 변환하는 스크립트를 넣지 않는다.

- `eafp_jap_content_version`, `eafp_japan_run_v*_migration_effect`와 migration 전용 on_action을 정의하지 않는다.
- 삭제된 `je_terakoya`, 옛 재벌·홋카이도 JE, 구형 `shogunate_var`, modifier와 버튼 변수의 존재를 검사하지 않는다.
- legacy footprint를 근거로 바닐라 `je_taming_the_north`나 메이지 JE를 추가·완료하지 않는다.
- 옛 진행도·영구 보상·사할린 claim·인물 역할을 새 상태로 복사하거나 소급 지급하지 않는다.
- 4단계 삭제 대상도 v4 cleanup 없이 신게임의 활성 정의와 호출부에서만 제거한다.
- 리뉴얼 빌드에서 시작한 캠페인의 재로드 시 bridge 단발 flag가 유지되고 사건이 중복되지 않는지만 검증한다.

#### 3.7 메이지 companion과 13개 사건 연결

`je_eafp_jap_legacy_meiji_restoration`은 바닐라 유신의 결과를 복제하는 JE가 아니라 옛 EAFP 풍미 사건을 묶는 동반 트랙으로만 사용한다.

1. `possible = { always = no }`를 `eafp_japan_restoration_active = yes` 및 EAFP 미완료 플래그 조건으로 교체한다.
2. `shogunate_var`는 `eafp_jap_legacy_restoration_progress`로 namespacing하고 공식 유신 JE가 active인 달에만 증가시킨다.
3. companion 자체 목표를 달성해도 공식 정권 교체를 실행하지 않는다. 바닐라 유신 완료를 감지하면 companion의 성공·무효화 분기를 결정하고 EAFP 후속 사건만 연다.
4. `eafp_jap_meiji_legacy.1-13`의 title·desc·option localization을 같은 namespace로 옮겨 바닐라 `meiji.*` 문구에 의존하지 않게 한다.
5. 사건별 처리 방향은 다음과 같이 고정한다.

| 사건 | 옛 역할 | 3단계 처리 |
|---|---|---|
| `.1` | 천황 집권, 통치자 생성, 공식 과제 시작 | 바닐라 유신 완료 뒤 발생하는 풍미 사건으로 축소; 통치자 생성·정권·법률·공식 JE 추가·공식 변수 write 제거 |
| `.2` | 개혁 완료 | 공식 메이지 main 완료 상태를 읽는 후일담으로 전환; 세계 변수와 보상 중복 제거 |
| `.3` | 사무라이의 몰락 | 공식 군사 과제 완료 뒤 1회 발생; 공식 완료 변수·이념 강제 변경을 제거하고 고유 선택지만 유지 |
| `.4-.6` | 서양 군사고문·사절단·외자 | 외교 과제 active/finished bridge에 연결; 공식 과제 진행도 write 제거 |
| `.7-.8` | 외국 철도기사·군용철도 | 경제·군사 과제 조건을 bridge로 읽고 EAFP 단발 flag만 사용 |
| `.9-.10` | 폐도·사학교 | 공식 군사 과제 및 사무라이 상태 뒤 풍미 사건으로 유지; 동일 modifier·급진파 효과 중복 여부 대조 |
| `.11-.12` | 항구 사건·쇄국 기사 | `eafp_japan_is_open`과 외교 과제 상태에 연결; 옛 개항 변수 직접 접근 제거 |
| `.13` | 홋카이도·강제 개항 보조 | 바닐라 북방·개항 상태의 후속 풍미로 제한; AI 전략과 강제 개항 변수 write 제거 |

각 사건에서 살아남는 effect는 `EAFP 고유 서사`, `EAFP 고유 일시 modifier`, `namespaced 단발 flag` 중 하나여야 한다. 바닐라 정권·법률·통치자·회사·영토·공식 JE·공식 완료 변수를 쓰는 effect는 허용하지 않는다.

#### 3.8 덴포·북방·류큐·조선 adapter 준비

- 덴포 faction adapter는 바닐라 `tenpo_reformer_goals_completed`와 `tenpo_hardliner_goals_completed`만 비교한다. 개혁파 우세는 EAFP 히토쓰바시·개혁파, 강경파 우세는 난키·보수파, 동률은 균형 분기로 반환한다.
- 3단계에서는 `tenpo_famine.*`를 아직 호출하지 않는다. 단지 4단계가 사용할 trigger 계약과 테스트만 완성한다.
- 옛 `je_hokkaido`는 3단계에서 삭제한다. 신게임 history의 시작 호출, 전용 진행 막대, `make_into_shogunate_domain_button`, `strengthen_merchant_surveillance_button`, `encourage_ezo_japanization_button`, `construct_hokkaido_castle_button`을 함께 제거한다.
- 바닐라 `je_taming_the_north`가 active가 되면 `eafp_jap_seen_taming_north`를 설정한다. active→closed 전환 뒤 `modifier_northern_learnings`가 확인되면 `eafp_jap_taming_north_completed`, 홋카이도 상실이 확인되면 `eafp_jap_taming_north_failed`를 한 번만 설정한다.
- 옛 홋카이도 사건은 다음 위치로 재배치한다.

| 사건 | 새 위치 | 중복 방지 |
|---|---|---|
| `hokkaido.1` | 바닐라 JE 성공 직후 북방 후일담과 `je_karafuto` 개방 | 사할린 claim·완료 modifier를 자동 지급하지 않고 `eafp_jap_hokkaido_1_fired` 사용 |
| `hokkaido.2-4` | 바닐라 JE 진행 중 홋카이도 도시화·통합 조건을 만족하면 시작되는 1회성 성곽 사건 연쇄 | 제거된 성곽 버튼 변수는 사건 단계 flag로 변환하고 바닐라 농업·아이누 버튼 효과와 겹치지 않게 함 |
| `hokkaido.5` | 바닐라 JE 진행 중 아이누 긴장 조건의 저빈도 월간 사건 | 바닐라 아이누 사건·modifier와 동시 발동 금지, cooldown 유지 |
| `hokkaido.6` | 바닐라 JE 진행 중 우호적 아이누 관계 조건의 저빈도 월간 사건 | 바닐라 `ainu_friendship_var`를 읽되 직접 쓰지 않고 1회/cooldown flag 사용 |

- `je_karafuto`와 이후 추가되는 모든 EAFP 북방 후속 JE는 `eafp_jap_taming_north_completed`를 공통 필수 조건으로 사용한다. 바닐라 북방 JE 실패·홋카이도 상실·JAP 소멸 시에는 시작하지 않으며, 이미 진행 중인 후속 JE는 명시적 invalid 분기로 닫는다.
- 기존 `je_eafp_ryukyu_intervention`의 바닐라 JE 직접 판정은 bridge trigger로 치환하되 progress 전달과 최종 귀속 소유권은 바꾸지 않는다.
- 자유민권운동·정한론이 `je_meiji_*` 또는 `je_colonize_korea`를 직접 읽는 위치를 bridge trigger로 치환한다. 해당 콘텐츠의 결과나 밸런스는 이 단계에서 재설계하지 않는다.

#### 3.9 인물 identity map과 신게임 정본 참조

1. 바닐라 일본 character template과 활성 EAFP template을 `역사 인물`, `생년`, `가문`, `역할`, `초상 DNA` 기준으로 대조해 `바닐라 정본 ID → 옛 EAFP ID 목록` 표를 stage 3 보고서에 만든다.
2. 바닐라에 같은 인물이 있는 모든 쌍은 바닐라를 정본으로 고정한다. 바닐라에 없는 EAFP 인물만 고유 인물로 유지한다.
3. 각 핵심 인물마다 `기존 정본 인물 찾기 → 없으면 바닐라 template로 생성 → 정본 scope 저장` 순서의 resolver effect를 만든다. EAFP 중복 template를 새로 생성하는 fallback은 두지 않는다.
4. history·event·effect·trigger의 옛 EAFP 인물 ID는 인물별 명시적 mapping을 통해 정본 ID로 치환한다. 새 캠페인에서 생성되는 saved scope와 character 변수만 정본을 가리키게 한다.
5. 구버전 세이브에 이미 생성된 중복 인물, 역할과 saved scope를 탐지·은퇴·재결속하는 로직은 만들지 않는다.
6. 물리적인 중복 template 정의 삭제와 모든 69개 이상 참조의 최종 치환은 8단계에서 완료하되, 3단계 종료 시 메이지 bridge가 다루는 핵심 인물은 신게임에서 전부 resolver를 통해서만 접근해야 한다.

#### 3.10 구현 순서와 독립 검증 단위

1. `Stage 3 inventory and vanilla checksum guard`
   - 바닐라 상태 키 checksum, 직접 참조 목록, 사건·인물 mapping 문서화
2. `Stage 3 read-only bridge triggers`
   - trigger 파일만 추가하고 기존 이벤트 동작은 바꾸지 않은 채 scripted trigger 오류 0건 확인
3. `Stage 3 idempotent bridge effects`
   - namespaced EAFP flag만 쓰는 effect 구현, 같은 effect 2회 실행 결과 비교
4. `Stage 3 minimal Japan on_action`
   - 월간 전용 on_action 한 줄 연결, 옛 `japan_code_on_actions`는 비연결 유지
5. `Stage 3 merge legacy Hokkaido into Taming the North`
   - 옛 `je_hokkaido`·history 호출·진행 막대·전용 버튼 제거, 6개 사건과 `je_karafuto`의 바닐라 북방 JE 연결
6. `Stage 3 Meiji companion adapter`
   - 휴면 JE 활성 조건, 진행 변수 namespacing, 사건 13개 직접 write 제거와 localization 이동
7. `Stage 3 character identity bridge`
   - 핵심 중복 인물 정의·참조 정본화와 신게임 resolver 검증
8. `Stage 3 regression and bridge report`
   - 전체 DLC 신게임 초기 로드, 새 캠페인의 저장·재로드, 24개월 반복 진행, 로그·checksum 보존

각 작업 단위는 이전 단위의 정적·초기 로드 결과가 유지될 때만 다음으로 넘어간다. bridge trigger 단계에서 effect를 함께 넣거나, 신게임 on_action 연결 전에 미검증 상태 변경 effect를 실행하지 않는다.

#### 3.11 검증 매트릭스

| 시나리오 | 확인 사항 |
|---|---|
| 1836 신규 JAP | 삭제 JE 생성 0, 옛 재벌 사건 0, bridge 보상 0 |
| 1836 신게임의 바닐라 북방 JE | 옛 `je_hokkaido` 0, 진행 중 `hokkaido.2-6` 도달 가능, 바닐라 버튼·보상 변화 0 |
| 신게임의 바닐라 북방 JE 성공·실패 분기 | 성공 시에만 `hokkaido.1`과 `je_karafuto` 개방, 실패·홋카이도 상실 시 후속 JE 0 |
| 신게임의 바닐라 유신 직전·직후 | companion과 `.1` 후일담 각각 최대 1회, 통치자·정권 중복 생성 0 |
| 신게임의 메이지 경제·군사·외교 과제별 분기 | 대응 풍미 사건만 열리고 공식 완료 변수·보상은 불변 |
| 신게임의 바닐라 덴포 위기 진행 | 개혁/강경/균형 adapter 값이 공식 script value 비교와 일치, 기근 사건은 아직 미발동 |
| 신게임의 류큐 경쟁 진행 | 조선 sidecar만 동기화되고 일본·청 승패 progress에 추가 변화 없음 |
| 신게임에서 발생한 JAP 내전·합병·해방 상태 | 잘못된 국가 scope에서 companion·사건 발동 0 |
| 리뉴얼 빌드에서 시작한 동일 캠페인 2회 재로드 + 24개월 | 사건 재예약 0, EAFP/바닐라 보상 중복 0 |

정적 검사는 다음을 자동 집계한다.

- bridge 파일 외부의 `meiji_var`, `meiji_restoration_complete`, `completed_je_meiji_*`, `tenpo_*_goals_completed` 직접 참조
- 활성 옛 재벌 JE·`zaibatsu_events`·전용 trigger·modifier·localization 참조
- `je_terakoya`와 대체 legacy JE 정의·호출
- `je_hokkaido`, `hokkaido_progress_bar`, 네 옛 홋카이도 JE 버튼의 활성 정의·호출
- `hokkaido.1-6`과 `je_karafuto`에서 `eafp_japan_taming_north_*` bridge를 거치지 않는 직접 북방 상태 참조
- 바닐라 JE·이벤트·on_action 동일 경로 복사와 `REPLACE:`
- bridge·resolver key 중복, 중괄호, UTF-8 BOM, localization key 누락
- `eafp_jap_content_version`, `*_migration_effect`, migration runner와 legacy footprint 판정의 부재
- 원본 `.disable` 53개 checksum 변화

#### 3.12 완료 조건

1. 모든 공식 DLC + EAFP만 활성화한 신게임 초기 로드에서 bridge 관련 missing key, invalid scope, orphan event, duplicate key가 0건이다.
2. 개별 EAFP 이벤트와 JE는 바닐라 내부 상태를 직접 읽거나 쓰지 않고 문서화된 bridge trigger/effect만 호출한다.
3. 옛 재벌 콘텐츠, `je_terakoya`, 옛 `je_hokkaido`는 신게임에서 생성되지 않는다.
4. `hokkaido.1-6`과 `je_karafuto`는 바닐라 `je_taming_the_north`의 진행·성공 상태를 통해서만 도달하며 실패·홋카이도 상실 경로에서는 시작되지 않는다.
5. 바닐라 유신·메이지 과제·덴포·북방·류큐·조선 식민화의 공식 상태와 보상은 EAFP bridge 실행 전후가 동일하다.
6. save migration 변수·effect·runner·tombstone과 legacy footprint 판정이 구현되지 않는다.
7. 핵심 중복 인물 참조는 신게임에서 정본 resolver를 사용하며 중복 템플릿으로 인물이 이중 생성되지 않는다.
8. 4단계 삭제 대상은 3단계 종료 시 아직 원형 상태를 유지하며 4단계 정적 삭제 목록으로만 기록된다.
9. `documentation/japan_stage3_bridge_report.md`에 파일 diff, 상태 계약, identity map, 신게임 fixture 결과와 최종 로그 checksum이 기록된다.

### 4단계: 전기 막부 재구성

실제 1.13.11 `-debug_mode` 실행에서 수집한 오류의 해결 순서·파일별 수정안·재검증 절차는 [japan_stage4_runtime_error_resolution_plan.md](japan_stage4_runtime_error_resolution_plan.md)에 분리해 기록한다. 현재 7개 바닐라 기반 `REPLACE:` JE 본체에서는 직접 파싱 오류가 확인되지 않았으며, 런타임 수정은 삭제된 state/country key와 옛 막부 지원 계층부터 수행한다.

- [x] **`REPLACE:` 저널의 바닐라 기준선 재구성**
  - 대상은 현재 활성 `REPLACE:je_meiji_restoration`, `REPLACE:je_meiji_main`, `REPLACE:je_meiji_economy`, `REPLACE:je_meiji_army`, `REPLACE:je_meiji_diplomacy`, `REPLACE:je_taming_the_north`와 덴포 병합을 위해 4단계에서 추가할 `REPLACE:je_tenpo_crisis`다.
  - 각 대상의 현행 바닐라 1.13.11 블록을 시작 중괄호부터 끝 중괄호까지 별도 기준본으로 추출하고 checksum과 원본 경로를 `japan_legacy_content_migration_manifest.md`에 기록한다.
  - EAFP 활성 블록을 바닐라 전문으로 먼저 교체한 뒤 EAFP 추가·수정분을 `EAFP DELTA BEGIN/END` 주석 구간에만 다시 적용한다. 런타임 bridge나 바닐라 JE 상태 조회는 만들지 않는다.
  - 보존 대상 바닐라 필드는 icon/group뿐 아니라 `is_shown*`, `possible`, `immediate`, 모든 pulse, scripted button, widget, modifier, `complete/fail/invalid/timeout`, 각 `on_*`, outcome 설명, 변수 처리, 공식 사건, 보상, `transferable`, `can_revolution_inherit`, pin·weight를 포함한다.
  - EAFP 차이는 `추가 사건`, `추가 추적 변수`, `추가 후속 JE`, `의도적 조건 수정`, `의도적 보상 수정`으로 분류한다. 추가형은 바닐라 effect 뒤에 합성하고, 수정형은 원래 바닐라 필드·변경 이유·대체 코드·영향 경로를 manifest에 1건씩 기록한 경우에만 허용한다.
  - 공식 이벤트를 EAFP 이벤트로 바꾸지 않고 둘 다 필요한 경우 공식 이벤트를 먼저 유지한 뒤 fire-once guard가 있는 EAFP 후속 사건을 호출한다. 공식 변수·modifier·영토·정권·전쟁 결과를 EAFP가 두 번 지급하지 않는다.
  - JE 제목·설명·조건 툴팁은 바닐라 localization을 기본으로 유지한다. EAFP가 새로 추가한 사건·추적 상태·후속 JE는 기존 EAFP localization을 최대한 재사용하고, 바닐라 JE localization 자체를 수정해야 할 때만 원본 문구와 변경 문구를 delta manifest에 함께 기록한다.
- [x] **저널별 `REPLACE:` 병합**
  - `je_meiji_restoration`: 바닐라 유신 버튼·widget·천황/다이묘 갱신·정치운동·황실 및 막부 승리·invalid 결과를 유지하고, EAFP 완료/실패 추적 flag와 `eafp_jap_meiji_legacy.1`만 해당 공식 종료 처리 뒤에 추가한다.
  - `je_meiji_main`: 바닐라 `meiji_var`, 경제·군사·이와쿠라 조건, 두 버튼, 12년 timeout, `meiji.2/4/5/6/14`를 유지하고 EAFP main 완료 flag와 `eafp_jap_meiji_legacy.2/4/5/6`만 추가한다.
  - `je_meiji_economy`: 바닐라 완료 조건·`meiji_var`·`completed_je_meiji_economy`·`meiji.7/8`을 유지하고 EAFP 완료 flag와 legacy 사건만 추가한다.
  - `je_meiji_army`: 바닐라 완료 조건·`meiji_var`·`completed_je_meiji_army`·`meiji.3/9/10`을 유지하고 EAFP 완료 flag와 legacy 사건만 추가한다.
  - `je_meiji_diplomacy`: 바닐라 완료 조건·`meiji_var`·`completed_je_meiji_diplomacy`·`meiji.11/12`를 유지하고 EAFP 완료 flag와 legacy 사건만 추가한다.
  - `je_taming_the_north`: 바닐라 일본/에조 분기, 다섯 버튼, 공식 세 카운터, 아이누 우호도, 사할린 추가 목표, `hokkaido_events.1/7/8`과 보상을 유지한다. EAFP `hokkaido.2-6`은 진행 중 보조 사건으로, `hokkaido.1`과 `je_karafuto`는 공식 성공 뒤 후속으로 추가한다.
  - `je_tenpo_crisis`: 바닐라 modifier·세 버튼·목표 집계·12년 timeout·`tenpo_events` 사건과 결과를 모두 유지한 `REPLACE:` 정의를 만들고 `tenpo_famine.1-6/.99` 및 개혁파/보수파 대응만 추가한다.
- [x] 7개 `je_bakuhantaisei_*` 지역 JE 제거
- [x] 지역 loyalty·independency·goryo 계산을 저택 보유 다이묘 `loyalty`로 교체
- [x] 주 세금 누수 공식을 저택 보유자 충성도 기반으로 교체
- [x] `reduce_nidome*` 14개 버튼과 호출·현지화 제거
- [x] 8개 막부 정책·청원 JE와 전용 지원 자산 제거
- [x] `je_bakufu_kaikaku/kaikoku/guntai/naibu/zaisei`를 현행 메이지 구조에 맞춰 최신화
- [x] `je_tenpo_famine`을 삭제하고 7개 사건을 바닐라 `je_tenpo_crisis`에 병합
- [x] 덴포 개혁파↔히토쓰바시·개혁파, 보수·강경파↔난키·보수파 adapter 구현
- [x] `eafp_japan.*` 91개 사건의 삭제 JE 의존 참조 재배치
- [x] 중복 인물 템플릿 제거와 effect·trigger 정본화
- [x] 살아남는 JE의 종료·무효화 조건 구현

통과 조건: 삭제 대상으로 지정된 JE·goryo·independency·`reduce_nidome` 참조가 0개이며, 살아남는 막부 사건은 바닐라 덴포·메이지·다이묘 구조에서 도달 가능하고 공식 유신 결과를 중복 생성하지 않는다. 모든 일본 `REPLACE:je_*`는 기준 바닐라 전문과 구조적으로 동일한 본체를 가지며, 차이는 manifest에 기록된 EAFP delta뿐이어야 한다.

### 5단계: 자유민권운동

- [x] 완성된 JE 구현
- [x] 원본 9개 이벤트와 세 언어 현지화 이관
- [x] 일반 정치운동과 중복 방지
- [x] 인물·법률·IG 지지 연결
- [x] 성공·타협·탄압·혁명 결과 구현
- [x] 기존 활성 운동과의 중복 생성 방지

통과 조건: JE 없는 운동이 생성되지 않고 모든 분기에 도달 가능한 종료가 있다.

### 6단계: 정한론

- [x] 정권 내부 파벌 갈등 구현
- [x] 원본 13개 본 사건·결말 사건과 세 언어 현지화 이관
- [x] 강경파·온건파·사무라이 불만 구현
- [x] 바닐라 `je_colonize_korea` 연결
- [x] 조선 측 반응 구현
- [x] 조선 상태별 대체 종료 구현

통과 조건: EAFP가 조선 식민화 진행을 복제하지 않으며 조선의 상태가 달라도 JE가 정체되지 않는다.

### 7단계: 류큐·대만 상호작용

- [x] 조선 류큐 개입 사이드카 구현
- [x] 바닐라 류큐 결과와 후속 효과 연결
- [x] 대만출병 개시 조건 재작성
- [x] 청·조선·서구 열강 반응 구현
- [x] 단발성·쿨다운·중복 방지 구현

통과 조건: 바닐라 류큐 JE의 전체 재정의 없이 작동한다. 불가피한 예외에는 호환성 문서와 diff 검사가 존재한다.

### 8단계: 회사·인물·자산·로컬라이징

- [x] 바닐라 중복 회사는 alias·조건부 생성으로 연결
- [x] EAFP 고유 회사와 원본 회사 사건 이관
- [ ] 인물 identity map 작성 및 중복 EAFP 템플릿 제거
- [ ] 옛 이벤트·effect·trigger·history의 인물 참조를 정본 인물 resolver로 이관
- [ ] 수정치·버튼·진행 막대·자산의 보존·재배치·삭제 대응표 작성
- [ ] 비활성 한국어·영어·중국어 현지화 원본 이관과 삭제 전용 키 정리

통과 조건: 중복 인물과 회사가 없고 모든 플레이어 노출 신규 키가 세 언어에 존재한다.

### 9단계: 통합 검증과 릴리스

- [x] 정적 중복·참조 검사
- [ ] 오류 로그 검사
- [ ] 전체 DLC 활성 신게임
- [ ] 리뉴얼 버전에서 시작한 캠페인의 저장·재로드 검사
- [ ] 주요 역사·대체역사 경로 플레이
- [ ] 여러 시드의 AI 관전
- [ ] 멀티플레이 동기화 검사
- [x] 문서와 버전 표기 갱신
- [ ] 원본 대비 저널·이벤트·현지화의 보존·재배치·삭제 manifest 검증

통과 조건: 아래 11절의 완료 기준을 모두 만족한다.

## 11. 검증 매트릭스

### 11.1 정적 검사

- [ ] manifest의 모든 일본 `.disable` 원본에 대응하는 최초 활성 `.txt` 또는 `.yml` 복원본 체크섬이 기록되어 있다.
- [ ] 최초 활성 복원본은 확장자를 제외하면 원본 `.disable`과 byte 또는 정규화된 텍스트 기준으로 동일하다.
- [ ] 원본 `.disable` 파일의 체크섬은 구현 전 기준선과 동일하며 직접 수정·삭제된 파일이 없다.
- [ ] 최종 활성 파일의 모든 차이가 `현행화`, `병합`, `ID 변경`, `명시적 삭제` 중 하나로 diff manifest에 설명되어 있다.
- [x] 바닐라와 중복되는 활성 최상위 일본 키가 0개다.
- [x] 예외 키는 호환성 매트릭스에 이유와 기준 버전이 기록되어 있다.
- [x] `.disable` 파일에만 정의된 키를 활성 파일이 참조하지 않는다.
- [x] 활성 일본 스크립트에 7개 지역 JE 키가 없다. `STATE_CHUBU`를 포함한 주 지역 키는 저널 상태가 아니라 저택 소유 다이묘를 찾는 대상 식별자로만 남긴다.
- [x] 8개 `je_bakufu_seisaku_*` 키와 단독 `je_bakufu_seisaku` 참조가 없다.
- [x] `je_tenpo_famine` 정의·참조는 없고 원본 7개 사건은 바닐라 `je_tenpo_crisis`에서 도달 가능하다.
- [x] `je_terakoya`, 대체 legacy JE, history 시작 호출, 전용 수정치·효과·트리거·현지화가 활성 파일에 없다.
- [x] `goryo`, 지역 `independency`, `reduce_nidome*` 정의·호출·현지화가 없다.
- [x] `je_meiji_restoration/main/economy/army/diplomacy`, `je_taming_the_north`와 교체 시 `je_tenpo_crisis`의 버튼·widget·조건·변수·pulse·공식 사건·완료/실패/timeout/invalid·결과 설명이 기준 바닐라 정의와 일치하고, manifest에 승인된 EAFP 추가·수정 구간만 diff로 남는다.
- [x] 각 일본 `REPLACE:je_*`마다 바닐라 원본 경로·게임 버전·checksum·EAFP delta 목록이 있으며, 바닐라 필드 삭제나 치환은 승인된 `의도적 수정` 항목 외에는 0건이다.
- [x] `je_bakufu_kaikaku/kaikoku/guntai/naibu/zaisei`가 문서의 메이지 대응 구조를 따른다.
- [x] 옛 `je_zaibatsu`, 재벌 청원 JE 3개, `zaibatsu_events`, 전용 trigger·modifier·localization이 활성 파일에서 제거되어 있다.
- [x] 옛 `je_hokkaido`, history 시작 호출, `hokkaido_progress_bar`, 전용 버튼 4개가 활성 파일에서 제거되어 있다.
- [x] `hokkaido.1-6`과 `je_karafuto`가 바닐라 `je_taming_the_north`의 진행·성공 상태를 통해서만 도달한다.
- [ ] 44개 비활성 저널이 22개 활성·최신화와 22개 삭제·병합으로 빠짐없이 manifest에 분류되어 있다.
- [x] 156개 비활성 이벤트 모두 활성 대응 ID 또는 명시적 기술 예외가 있다.
- [ ] 옛 버튼·진행 막대·수정치·회사·인물 템플릿이 보존·재배치·삭제 중 하나로 manifest에 등록되어 있다.
- [x] 바닐라와 중복되는 활성 EAFP 인물 템플릿이 0개이고 모든 legacy 인물 참조가 정본 ID 또는 resolver를 사용한다.
- [x] 문서화되지 않은 바닐라 전체 파일 복사본이 없다.
- [x] 로컬라이징 `replace`의 옛 문구가 legacy 키로 보존되고 바닐라 DLC 키 직접 덮어쓰기는 남아 있지 않다.
- [ ] 영어·한국어·중국어 간체 원본 키마다 대응 활성 키, 재배치 키 또는 명시적 삭제 기록이 있다.

### 11.2 주요 플레이 경로

| 분류 | 시험 경로 |
|---|---|
| 역사적 유신 | 개항 → 메이지 유신 → 보신전쟁 → 에조 처리 |
| 막부 존속 | 공무합체 또는 막부 승리 |
| 대체 정권 | 공의여론·비역사적 일본 체제 |
| 쇄국 | 장기 쇄국과 외세 압력 |
| 덴포 | 개혁파 승리·보수/강경파 승리·균형·12년 기한 종료·오시오 사건 단발성 |
| 막번체제 | 저택 소유자 충성도 0·39·40·65·66·100, 소유자 부재·복수 소유자, 세금 보존율 경계값 |
| 종교 | 신불분리·불교 우대 |
| 재벌 | 재벌 육성·억제 |
| 류큐 | 일본 승리·청 승리·조선 개입·조선 중립 |
| 정한론 | 강경파 승리·온건파 승리·사족 급진화 |
| 조선 | 독립·종속·멸망·이미 일본 지배 |
| 대만 | 청·일본·다른 열강의 소유 |
| 북방 | 바닐라 `je_taming_the_north` 진행·성공·실패, 일본 통제·에조 분리·사할린 타국 소유, 성공 후 `je_karafuto` 개방·실패 후 미개방 |
| 실패 상태 | 일본 종속·내전·합병·정권 붕괴 |

### 11.3 환경과 저장·재로드

- [ ] 모든 공식 DLC 활성 신게임
- [ ] 리뉴얼 버전 신게임에서 메이지·류큐·재벌·조선 식민화 JE 진행 상태를 만든 뒤 저장·재로드
- [ ] 리뉴얼 버전 신게임에서 북방 JE 진행·성공·실패 상태를 만든 뒤 저장·재로드
- [ ] 리뉴얼 이전 EAFP 세이브는 지원·검증 대상에서 제외되었는지 배포 문서에 명시
- [ ] 1836-1880 AI 관전 여러 시드
- [ ] 멀티플레이 동기화

## 12. 최종 완료 기준

1. `error.log`와 `game.log`에 신규 `eafp_jap` 관련 missing key, duplicate key, invalid scope 오류가 없다.
2. 바닐라 쇄국·덴포·메이지·`je_taming_the_north`·종교·재벌·류큐·이와쿠라·조선 식민화 JE가 정상 개시·종료된다.
3. EAFP가 바닐라 유신·보신전쟁·재벌·류큐 진행 변수와 핵심 인물을 덮어쓰지 않는다.
4. 동일 역사 사건이 바닐라와 EAFP에서 이중 발동하지 않는다.
5. 모든 EAFP 사이드카 JE에 성공·실패·무효화·비정상 국가 상태 종료 조건이 있다.
6. 모든 공식 DLC 활성 환경에서 옛 EAFP 동반 JE가 바닐라 DLC 흐름에 맞춰 개시·완료·실패한다.
7. 리뉴얼 이전 EAFP 세이브를 위한 migration 코드가 없고, 신게임 전용 지원 방침이 배포 문서에 명시된다.
8. 44개 비활성 저널은 22개 활성·최신화와 22개 삭제·병합으로, 156개 비활성 이벤트는 활성·재배치·흡수·삭제 중 하나로 모두 추적된다.
9. 옛 영어·한국어·중국어 간체 현지화 문구가 충돌 키 변경 외에는 원문 중심으로 보존된다.
10. 바닐라 패치 시 원본 교체 파일의 필드 차이를 자동으로 탐지할 수 있다.
11. EAFP의 살아남는 진행 막대·이벤트 선택지·현지화가 최대한 보존되면서 정권·영토·전쟁의 공식 결과는 바닐라 DLC와 충돌하지 않는다.
12. 7개 지역 JE, 8개 정책·청원 JE, 독립 `je_tenpo_famine`, `je_terakoya`, 옛 `je_hokkaido`, 옛 재벌 JE·청원 JE 3개, goryo, 지역 independency와 14개 `reduce_nidome*` 버튼이 활성 정의와 참조에서 완전히 사라진다. `je_terakoya`와 옛 `je_hokkaido`의 history 시작 호출·대체 legacy JE·전용 수정치·진행 막대·버튼·JE 전용 현지화 및 옛 `zaibatsu_events`도 남지 않는다. `hokkaido.1-6`과 후속 북방 콘텐츠의 현지화는 재배치 키로 보존한다.
13. 옛 `hokkaido.1-6`과 `je_karafuto`는 바닐라 `je_taming_the_north`의 진행·성공 상태에서만 이어지고, 바닐라 JE 실패 또는 홋카이도 상실 시 후속 북방 JE가 시작되지 않는다.
14. 바닐라 덴포 개혁파·보수/강경파가 EAFP 개혁파·보수파에 정확히 연결되고 각 결과의 보상이 한 번만 적용된다.
15. 모든 주의 막번체제 세금·정치 반응이 저택 보유 다이묘의 충성도만 사용하며 충성도 0~100 경계에서 문서의 산식과 일치한다.
16. 바닐라와 중복되는 EAFP 인물 정의가 없고, 신게임에서 생성되는 effect·trigger·saved scope가 동일한 바닐라 정본 인물을 가리킨다.
17. 현재 비활성인 모든 일본 관련 파일은 구현 초기에 `.txt` 또는 localization용 `.yml`로 전면 활성 복원되었으며, 무수정 복원 기준선·최초 오류 로그·원본 대비 최종 diff가 보존되어 있다.

## 13. 권장 변경 단위

1. `Japan legacy inventory and key mapping`
   - 모든 일본 `.disable` 파일의 전면 활성 복원, 기준 체크섬, 44개 저널·156개 이벤트·현지화의 보존·재배치·삭제 매핑
2. `Japan vanilla DLC bridge`
   - 전체 DLC·신게임 전제의 연결 계층, on_action과 결과 동기화
3. `Bakufu legacy journals and events`
   - 지역·정책·청원 JE 제거, 저택 보유자 충성도 계산, 막번체제·개혁 JE와 `eafp_japan.*` 사건 재배치
4. `Meiji, Boshin, Tenpo and northern legacy companions`
   - 현행 메이지 네 JE 최신화, 보신전쟁 동반 JE, 옛 `je_hokkaido` 삭제와 사건·가라후토 후속 체인의 바닐라 `je_taming_the_north` 연결, 덴포 기근 사건의 바닐라 JE 병합
5. `Political and religious legacy chains`
   - 자유민권운동·정한론·신토 원본 체인 복원, 옛 재벌 체인 삭제 확인
6. `Ryukyu and Formosa legacy integration`
   - 류큐 처분·조선 개입·대만출병 원본 체인과 DLC 결과 연결
7. `Japan legacy localization, characters and support files`
   - 세 언어 현지화, 역사명, 중복 인물 제거·identity map, 수정치·버튼·진행 막대 이관 및 삭제
8. `Japan full-DLC integration validation`
   - 원본 보존율, 전체 DLC 신게임 경로, 저장·재로드, AI, 멀티플레이 검증

구현은 모든 일본 `.disable` 파일을 먼저 같은 경로의 활성 `.txt` 또는 localization용 `.yml`로 무수정 복원하는 것에서 시작한다. 그 기준선을 고정한 뒤 활성 복사본을 파일 단위로 수정하며, 명시적 삭제 목록도 복원된 파일 안에서 정의와 참조 그래프를 함께 제거한다. 처음부터 살아남는 정의만 선별 복사하는 방식은 사용하지 않는다. 최종 목표는 전체 옛 원본을 실제 구현 출발점으로 삼으면서도 삭제가 지정된 중복 시스템을 최종 배포본에서 제거하고, 옛 사건·선택지·현지화를 가능한 한 현행 바닐라 일본 흐름 안에서 보존하는 것이다.
