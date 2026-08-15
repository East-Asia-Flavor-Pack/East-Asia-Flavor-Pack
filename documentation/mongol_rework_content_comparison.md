# 몽골 재작업 콘텐츠 비교

## 1. 비교 기준과 핵심 결론

- 비교 대상: 2026-08-15 현재 로컬의 `East-Asia-Flavor-Pack`(이하 **기존 팩**)과 `East-Asia-Flavor-Pack-Mongol_rework`(이하 **재작업본**)
- 판정 기준: 파일 이름이나 위치가 아니라 실제 게임 기능·설정·자산의 의미를 비교했다.
- 일반적인 버전 차이, 중국·일본·한국 콘텐츠 변경, 두 저장소에 실질적으로 같은 형태로 존재하는 기능은 몽골 신규 콘텐츠에서 제외했다.
- 상태 표기는 다음과 같다.
  - **연결됨**: 게임 시작 설정이나 다른 스크립트에서 직접 사용된다.
  - **부분 연결**: 일부 정의와 참조는 있으나 누락 또는 불일치가 있다.
  - **정의만 존재**: 정의 파일은 있으나 적용처나 호출처를 찾을 수 없다.
  - **빈 초안**: 파일만 있고 실질적인 내용은 없다.
  - **오류 가능**: 구문이나 식별자 문제 때문에 의도대로 동작하지 않을 가능성이 높다.

재작업본에만 있는 실질적인 몽골 콘텐츠는 크게 다음 네 묶음이다.

1. 몽골의 시작 영토·인구·경제 설정 변경
2. 몽골 고유 이해집단 명칭과 보르지긴·복드 계열 이념
3. 몽골 역사 인물 및 후기 지도자 후보
4. 복드 칸국 정부, 몽골 개념·수정치·주 특성·그래픽 초안

다만 완성도에는 큰 차이가 있다. 시작 영토와 일부 이해집단 설정은 실제 시작 역사에 연결되어 있지만, 정부 형태·개념·수정치·주 특성·여러 그래픽은 정의만 존재한다. 인물 파일과 일부 정치 정의에는 구문 오류, 중복 ID, 오탈자 및 누락된 정의가 있어 그대로 이관하면 안 된다.

## 2. 구현 상태 요약

| 콘텐츠 | 상태 | 재작업본의 주요 파일 | 판단 |
|---|---|---|---|
| 시작 영토 변경 | 연결됨 | `common/history/states/chi_states.txt` | 기존의 알타이 보유를 제거하고 흥안·톰스크를 몽골에 추가한다. |
| 시작 인구 변경 | 연결됨 | `common/history/pops/99_chi.txt` | 울리아수타이·우르가·투바의 인구를 재조정하고 톰스크 인구를 추가한다. |
| 시작 건물 변경 | 연결됨 | `common/history/buildings/chi_building.txt` | 울리아수타이와 우르가를 목축 중심으로 재구성한다. |
| 몽골 이해집단 명칭 | 연결됨 | `common/history/countries/mgl - china.txt`, `localization/korean/mgl_ideology_l_korean.yml` | 지주·전원 주민·군부에 몽골 고유 명칭을 지정한다. |
| 보르지긴 계열 이념 | 부분 연결 | `common/ideologies/mgl_ig_ideologies_flavored.txt`, `common/ideologies/mgl_leader_ideologies.txt` | 보르지긴·개혁파 보르지긴·황금씨족은 정의와 일부 적용처가 있다. 복드 및 오이라트 계열은 참조 불일치가 있다. |
| 복드 칸국 정부 | 오류 가능 | `common/government_types/00_jfp_mongolia.txt`, `localization/korean/mgg_l_korean.yml` | 정부 정의와 한국어 현지화는 있으나 국가 태그가 `MGR`로 적혀 있고 실제 적용처가 없다. |
| 시작 역사 인물 | 오류 가능 | `common/history/characters/mgl - mongolia.txt`, `localization/korean/Mongolian_name_l_korean.yml` | 룹산출팀과 셍게 린첸을 추가하려 하지만 중괄호가 불균형하고 이름 키도 일부 불일치한다. |
| 후기 지도자 템플릿 | 부분 연결 / 오류 가능 | `common/character_templates/character_templates_Mongolia.txt` | 수흐바타르·처이발상·체뎅발·복드 칸 후보가 있으나 템플릿 ID가 중복된다. |
| 몽골 게임 개념 | 정의만 존재 | `common/game_concepts/eafp_mongolia_concepts.txt` | 황금씨족·몽골의 분열·몽골 독립 운동 개념이 정의되지만 사용처와 현지화가 없다. |
| 몽골 수정치 | 정의만 존재 / 오류 가능 | `common/modifiers/jfp_mgl_modifiers.txt`, `localization/korean/mgl_modi_l_korean.yml` | 부족 체계·은 상납·가축 부족·광산 개발 수정치가 있으나 적용처가 없고 ID가 중복된다. |
| 몽골 주 특성 | 정의만 존재 | `common/state_traits/mongolia_traits.txt` | 오논강과 홉스굴호 특성이 있으나 주에 부여되지 않았고 현지화도 없다. |
| 몽골 시각 자산 | 부분 연결 / 정의만 존재 | `gfx/interface/icons/ideology_icons/`, `gfx/coat_of_arms/textured_emblems/mongolia.dds`, `gfx/event_pictures/quriltai.jpg` | 이념 아이콘은 사용되지만 문장과 쿠릴타이 그림은 참조되지 않는다. |
| 몽골 결정·이벤트 전용 파일 | 빈 초안 | `common/decisions/eafp_mongolia_decision.txt`, `localization/korean/mgl_event_l_korean.yml` | 두 파일 모두 실질적인 내용이 없다. |

## 3. 몽골 시작 설정 변경

### 3.1 영토

기존 팩과 재작업본 모두 몽골(`MGL`)을 청의 별도 종속국으로 시작시키지만, 보유 주가 달라진다.

| 구분 | 기존 팩 | 재작업본 |
|---|---|---|
| 공통 보유 | 울리아수타이, 우르가, 투바 | 울리아수타이, 우르가, 투바 |
| 기존 팩에만 있음 | 알타이 | - |
| 재작업본에만 있음 | - | 흥안, 톰스크 |

재작업본의 `common/history/states/chi_states.txt`는 흥안과 톰스크의 `region_state:CHI` 소유권을 `MGL`로 넘긴다. 반면 기존 팩에서 몽골 소유였던 알타이는 재작업본에서 몽골에 배정되지 않는다. 따라서 재작업의 핵심 영토 변화는 **알타이를 빼고 흥안·톰스크를 추가한 것**으로 요약할 수 있다.

흥안은 재작업본의 `map_data/state_regions/eafp_state_regions.txt`에서 주 전체가 다시 정의된다. 다만 이 파일에는 중국·만주 및 게임 버전 대응 변경도 섞여 있으므로, 전체 파일을 몽골 콘텐츠로 보아서는 안 된다.

### 3.2 인구

`common/history/pops/99_chi.txt`에서 확인되는 몽골 보유지의 주요 차이는 다음과 같다.

| 주 | 기존 팩 | 재작업본 | 변화 |
|---|---|---|---|
| 울리아수타이 | 몽골 62,039, 카자흐 68,136, 한 623, 러시아 500 | 몽골 270,000, 카자흐 13,000, 한 623 | 몽골 인구를 크게 늘리고 카자흐·러시아 인구를 축소 또는 제거한다. |
| 우르가 | 몽골 166,259, 한 996 | 몽골 340,000, 한 996 | 몽골 인구를 약 두 배로 늘린다. |
| 톰스크 | 몽골 소유 인구 블록 없음 | 타타르 36,000, 겔룩파 타타르 16,000 | 새 몽골 영토에 총 52,000명의 타타르 인구를 둔다. |
| 투바 | 투바 43,710, 몽골 5,290 | 투바 30,000, 몽골 2,000 | 두 집단 모두 감소한다. |

흥안의 소유권은 몽골로 넘기지만, 같은 인구 파일의 흥안 조정은 `region_state:CHI`를 대상으로 한다. 실제 역사 로딩 순서와 주 분할 결과에 따라 의도한 종교·직업 변환이 몽골 소유 지역에 적용되는지 별도 검증이 필요하다.

### 3.3 시작 경제와 시장 수도

- 울리아수타이는 재작업본에서 목축장 3단계로 명시된다.
- 우르가는 목축장 5단계만 남으며, 기존 팩에 있던 밀 농장 3단계 설정은 재작업본에서 사라진다.
- 소유권이 새로 추가된 흥안과 톰스크에는 재작업본의 몽골 전용 건물 블록이 없다. 다른 역사 파일이나 기본 게임 설정에서 넘어오는 건물에 의존한다.
- `common/history/countries/mgl - china.txt`의 시장 수도는 기존 팩의 `STATE_URGA`에서 재작업본의 `STATE_NORTHERN_MANCHURIA`로 바뀐다. 그러나 북만주는 같은 재작업본에서 만주(`MCH`) 소유로 설정되므로, 몽골이 소유하지 않은 주를 시장 수도로 지정하는 불일치일 가능성이 높다.

## 4. 몽골 고유 정치 콘텐츠

### 4.1 이해집단 명칭과 시작 적용

재작업본은 몽골의 기본 이해집단에 다음 고유 명칭을 부여한다.

| 기본 이해집단 | 고유 명칭 | 시작 적용 |
|---|---|---|
| 지주 | 야즈구르탄 | 적용됨 |
| 전원 주민 | 유목민 | 적용됨 |
| 군부 | 몽고팔기 | 적용됨. 주석에는 나이만 호슈로 변경할 예정이라고 적혀 있다. |
| 성직자 | 금강승 승려 | 기존 팩에도 있던 명칭이므로 신규로 계산하지 않는다. |
| 지식인 | 문인 | 기존 팩에도 있던 명칭이며, 재작업본에서는 이념만 추가된다. |

`localization/korean/mgl_ideology_l_korean.yml`에는 수몬 알바투·함질가·샤비라는 사회 계층 명칭도 있다. 주석상 “유목의 끝” 일지에서 사용할 구상이지만, 실제 이해집단 이름 변경이나 일지 구현은 발견되지 않아 현지화 초안으로 분류한다.

### 4.2 이념

- `ideology_borjigin`: 군주정·전제정·민족 국가를 강하게 선호하는 보르지긴 씨족 이념이다. 몽골 지주와 군부에 실제 추가된다.
- `ideology_borjigin_reform`: 군주제와 전제정을 선호하되 공화정·참정권·다문화에 대한 반대가 다소 완화된 개혁파 이념이다. 몽골 지식인에 실제 추가된다.
- `ideology_bogd`: 신정과 전제정을 강하게 지지하는 젭춘담바 후툭투 추종 이념이다. 정의는 있으나 시작 설정에서는 오탈자인 `ideology_vogd`를 참조하므로 적용되지 않을 가능성이 높다.
- `ideology_golden_horde`: 칭기스 칸과 보르지긴 계승을 강조하는 인물 이념이다. 셍게 린첸에게 지정되어 있지만 해당 역사 인물 파일 자체가 구문 오류 가능 상태다.
- `ideology_oirad`와 `ideology_oiradc`: 한국어 현지화와 시작 국가 파일의 참조는 있으나 실제 이념 정의를 찾을 수 없다.
- `ideology_russia_mgl`과 `ideology_china_mgl`: 친러파·친중파 현지화만 있고 정의나 적용처가 없다.

유목민 이해집단 특성 `ig_trait_nomad_mgl_1`~`3` 역시 한국어 이름과 설명만 있고 실제 특성 정의는 없다.

### 4.3 복드 칸국 정부

`common/government_types/00_jfp_mongolia.txt`에는 신정법 아래에서 세습되는 `gov_jasag` 정부가 정의되어 있다. 한국어 명칭은 “복드 칸국”이며, 젭춘담바 후툭투가 통치하는 체제로 설명된다.

그러나 다음 이유로 현재는 작동 가능한 콘텐츠로 보기 어렵다.

- 가능 조건이 몽골 태그 `MGL`이 아니라 존재하지 않는 것으로 보이는 `MGR`을 검사한다.
- 몽골의 시작법은 군주정이며, `gov_jasag`을 직접 적용하거나 전환하는 이벤트·결정이 없다.
- 정부 명칭과 설명 외에 통치자·후계자 칭호의 신규 현지화를 이 파일군에서 확인할 수 없다.

## 5. 몽골 인물 콘텐츠

### 5.1 시작 역사 인물

`common/history/characters/mgl - mongolia.txt`는 다음 두 인물을 추가하려 한다.

| 인물 | 역할 | 설정 |
|---|---|---|
| 룹산출팀 지그메드 | 성직자 이해집단 지도자 | 1815-01-01 출생, 제5대 젭춘담바 후툭투라는 주석이 있다. |
| 셍게 린첸 보르지긴 | 지주 이해집단 지도자 | 1811-07-24 출생, 황금씨족 이념을 사용한다. |

다만 파일의 `{`는 4개, `}`는 5개로 중괄호가 불균형하다. 첫 인물 뒤에서 `c:MGL` 범위를 닫은 뒤 두 번째 `create_character`가 국가 범위 밖에 놓여 있어, 파일 전체 또는 두 번째 인물이 정상 로딩되지 않을 가능성이 높다.

또한 기존 팩에도 `Sengge_Rinchen`이 청의 역사적 장군 템플릿으로 존재한다. 재작업본의 `Senggerinchen`은 몽골 지주 지도자로 별도 추가하려는 구현이므로 역할 변화는 신규지만, 인물 자체가 완전히 새로 도입된 것은 아니다.

이름 현지화에도 다음 불일치가 있다.

- 스크립트의 `Jigmed`와 현지화의 `Jjigmed`
- 스크립트의 `Borjigin`과 현지화의 `Borjigit`

### 5.2 후기 지도자 템플릿

`common/character_templates/character_templates_Mongolia.txt`에는 몽골의 후반기 이해집단 지도자로 등장할 후보가 정의되어 있다.

| 템플릿 | 이해집단 | 사용 기간 | 확률 |
|---|---|---|---|
| 담딘 수흐바타르 | 노동조합 | 1919-01-01 ~ 1923-01-01 | 80 |
| 허를러깅 처이발상 | 노동조합 | 1923-01-01 ~ 1936-01-01 | 80 |
| 욤자깅 체뎅발 | 군부 | 1933-01-01 ~ 1936-01-01 | 80 |
| 복드 칸 젭춘담바 후툭투 | 성직자 | 1911-01-01 ~ 1924-01-01 | 100 |

파일 주석은 향후 이들을 이벤트 생성 방식으로 바꿀 예정이라고 밝힌다. 현재도 이해집단 지도자 사용 조건이 있어 일부 연결은 되어 있지만 다음 문제가 있다.

- 체뎅발과 복드 칸 정의가 모두 `Tsedenbal_character_template`이라는 같은 최상위 ID를 사용한다. 뒤 정의가 앞 정의를 덮어쓰거나 중복 정의 오류가 발생할 수 있다.
- 젭춘담바 후툭투의 이름 현지화는 주석 처리되어 있다.
- 모든 인물의 특성 목록이 비어 있다.
- 체뎅발은 1916년생인데 1933년부터 군부 지도자로 등장할 수 있어 16~17세 지도자가 될 수 있다.

## 6. 정의 또는 자산만 존재하는 콘텐츠

### 6.1 게임 개념

`common/game_concepts/eafp_mongolia_concepts.txt`에는 다음 빈 개념 정의가 있다.

- 황금씨족(`concept_golden_horde`)
- 몽골의 분열(`concept_division_mongolia`)
- 몽골 독립 운동(`concept_mongolian_independence_movement`)

다른 스크립트의 참조와 현지화를 찾을 수 없으므로 현재 플레이어가 접할 수 있는 기능은 아니다.

### 6.2 수정치

`common/modifiers/jfp_mgl_modifiers.txt`의 의도는 다음과 같이 읽힌다.

- 부족 체계: 이주 유치 -50%
- 은 상납: 세금 낭비와 세입 감소
- 가축 부족: 더 큰 세금 낭비와 세입 감소
- 광산 개발 결과: 성공·보통·실패·사고에 따른 이주 유치 변화

그러나 어떤 이벤트·결정·일지·주 역사에서도 이 수정치를 적용하지 않는다. 또한 네 번째 광산 결과가 `great_migration_to_mongolian4`가 아니라 세 번째와 같은 `great_migration_to_mongolian3`으로 중복 정의되어 있으며, 현지화 파일에는 반대로 1~4가 각각 존재한다.

### 6.3 주 특성

`common/state_traits/mongolia_traits.txt`는 오논강과 홉스굴호에 각각 기반 시설 +10을 주는 특성을 정의한다. 하지만 `map_data/state_regions`나 주 역사에서 두 특성을 부여하지 않고, `localization/*/map/jfp_state_traits_*`에도 이름이 없다.

### 6.4 시각·외형 자산

- `gfx/interface/icons/ideology_icons/borjigin.dds`와 `bogd.dds`는 해당 이념 정의에서 실제 사용한다.
- `gfx/coat_of_arms/textured_emblems/mongolia.dds`는 문장·깃발 정의에서 참조되지 않는다.
- `gfx/event_pictures/quriltai.jpg`는 이벤트나 미디어 별칭에서 참조되지 않는다.
- `common/genes/eafp_genes_accessories_headgear.txt`에는 중앙아시아 모자를 사용하는 `mongolian_hats` 그룹이 추가되어 있으나, 저장소 안에서 해당 그룹을 직접 선택하는 다른 참조는 찾을 수 없다.

## 7. 미완성 및 오류 징후 목록

이관 전에 우선 확인하거나 수정해야 할 항목이다.

1. `common/history/characters/mgl - mongolia.txt`의 중괄호가 하나 더 닫혀 있다.
2. 체뎅발과 복드 칸이 동일한 `Tsedenbal_character_template` ID를 사용한다.
3. `gov_jasag` 조건의 `c:MGR`은 `c:MGL` 오탈자로 보인다.
4. 몽골 성직자 시작 설정의 `ideology_vogd`는 `ideology_bogd` 오탈자로 보인다.
5. `ideology_oirad`, `ideology_oiradc`, `ideology_russia_mgl`, `ideology_china_mgl`은 정의가 없거나 현지화만 존재한다.
6. `ig_trait_nomad_mgl_1`~`3`, 수몬 알바투·함질가·샤비는 현지화만 있고 실제 시스템 정의나 적용처가 없다.
7. `great_migration_to_mongolian3`가 두 번 정의되고 현지화의 `great_migration_to_mongolian4`와 연결되지 않는다.
8. 몽골 시장 수도가 몽골 소유가 아닌 북만주로 지정되어 있다.
9. `Jigmed`/`Jjigmed`, `Borjigin`/`Borjigit` 등 인물 이름 키가 일치하지 않는다.
10. 복드 칸국, 몽골 이념·수정치·인물 신규 현지화는 사실상 한국어에만 있다. 영어·중국어 등 다른 언어에서는 키가 그대로 노출될 수 있다.
11. `common/decisions/eafp_mongolia_decision.txt`와 `localization/korean/mgl_event_l_korean.yml`은 비어 있다.
12. 몽골 개념, 주 특성, 문장, 쿠릴타이 그림에는 적용처 또는 현지화가 없다.

## 8. 기존 팩에도 있어 신규로 보지 않은 항목

다음 항목은 재작업본에서 파일 경로나 구성 방식이 달라도 기존 팩에 실질적으로 같은 기능이 있으므로 신규 콘텐츠에서 제외했다.

- 청의 **외몽골 흡수** 결정과 `chi_military_headquarters.103` 이벤트
  - 결정: 양쪽 모두 `common/decisions/eafp_military_headquarters_decision.txt`
  - 이벤트: 기존 팩 `events/eafp_chi_events/eafp_chi_military_headquarters_events.txt`, 재작업본 `events/eafp_chi_military_headquarters_events.txt`
- 청과 몽골 사이의 `military_headquarters_china` 종속 관계 및 우호도 50
- 청이 외몽골을 흡수할 때 `MGL`을 합병하는 효과
- 청의 장군부 종속국일 때 몽골 국명을 울리아수타이로 바꾸는 동적 국명
  - 재작업본의 `common/dynamic_country_names/eafp_mgl.txt`는 전용 파일이지만, 같은 기능은 기존 팩의 `common/dynamic_country_names/eafp_china.txt`에도 있다.
- 울리아수타이·우르가·투바의 몽골 소유, 몽골 인구, 목축 경제라는 기본 틀
  - 재작업본에서 수치와 세부 구성이 달라진 부분만 신규 변경으로 계산했다.

반대로 기존 팩에는 군주정일 때의 “대몽골국”과 공산주의일 때의 “몽골 인민공화국” 동적 국명이 있지만 재작업본에서는 빠져 있다. 이는 재작업본의 신규 콘텐츠가 아니라 기존 기능의 누락 또는 퇴행에 해당한다.

## 9. 비교 범위의 한계

- 기존 팩 README는 v2.1.0 및 게임 1.10 대응을 표기하지만, 재작업본 README는 v1.1.0을 표기한다. 두 저장소 사이에는 몽골과 무관한 대규모 구조·버전 차이가 있다.
- 따라서 파일이 재작업본에만 있다는 이유만으로 신규 몽골 콘텐츠라고 판정하지 않았다.
- 이 문서는 저장소 내부의 정의·참조·현지화 관계를 정적 비교한 결과다. 실제 게임 실행 시의 로딩 순서, 중복 ID 처리 방식, 기본 게임 데이터와의 상호작용은 별도 실행 검증이 필요하다.
- 이 문서 작성 과정에서는 게임 스크립트나 자산을 수정하지 않았다.
