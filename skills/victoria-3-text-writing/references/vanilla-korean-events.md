# 바닐라 한국어 이벤트 문안

Victoria 3 **1.15.2 (Ivan-Chai)**의 배포 파일을 기준으로 한다. 아래 경로는 설치 폴더의 `game/` 기준이며, `*_l_korean.yml` 파일명은 `localization/korean/` 아래를 가리킨다. 행 번호는 이 버전의 위치이고 다른 버전에서는 이벤트 ID와 키로 다시 찾는다.

## 한 창의 네 필드 읽기

`events/japan_events/ep2_sakoku_events.txt`의 `ep2_sakoku.2`는 쇄국을 끝내기로 한 막부가 새 통상법을 정하는 이벤트다. 어느 정책을 채택할지는 선택 전까지 열려 있다. 같은 사건이 네 필드에서 어떻게 달라지는지 `ep2_sakoku_l_korean.yml` 23–28행과 대조한다.

| 화면 | 스크립트와 한국어 키 | 실제 문안에서 읽을 점 |
|---|---|---|
| 제목 | `title = ep2_sakoku.2.t` | ‘자물쇠 따기’. 문을 여는 행위를 비유하는 명사구다. 주체와 정책은 바로 아래 설명이 밝혀 준다. |
| 설명 | `desc = ep2_sakoku.2.d` | 안팎의 소란 → 막부의 판단 → 쇄국의 즉각적인 종료 추진 순이다. ‘밀어붙이기로 했다’는 이미 내린 결정이다. 후속 통상법까지 정해졌다고 쓰면 세 선택지와 모순된다. |
| 풍미문 | `flavor = ep2_sakoku.2.f` | 세관을 가득 채운 상인들, 질문에 답하지 못하는 관료, 관료의 속생각 순이다. 상인은 결과를 알고 싶어 하고 관료도 답을 모른다. 설명의 정치적 결정을 한 인물이 겪는 곤란으로 보여 준다. |
| 선택지 | 각 `option` 블록의 `name = ep2_sakoku.2.a`, `.b`, `.c` | 중상주의에 미래를 거는 선언, 자유무역에 대한 다짐, 보호무역에 대한 신중론이다. 세 문장을 나란히 읽으면 무엇을 택하는지 알 수 있다. |

기본 창 `gui/eventwindow.gui` 49, 241, 255, 276, 291행을 보면 제목에는 `[EventWindow.GetTitle]`, 굵은 본문에는 `[EventWindow.GetDescription]`, 그 아래에는 `[EventWindow.GetFlavor]`가 들어간다. 버튼에는 `[EventOption.GetText]`, 툴팁에는 `[EventOption.GetDesc]`를 쓴다. 이 창에서 설명 전체를 굵게 만드는 서식은 GUI가 맡는다. 옵션 레이블을 쓸 때는 선택 후 효과를 모두 한 줄로 옮길 필요가 없다.

### 네 줄이 모두 쓰이는 짧은 원문

`krakatoa.2`에서는 영향을 받은 주를 `tsunami_state`로 저장한다. 제목은 파도를, 설명은 피해 지역과 원인을, 풍미문은 목격자가 기억하는 침묵을 담는다. 유일한 선택지는 국가 정책 대신 비탄을 표현한다. `option`의 `show_as_tooltip`이 피해 효과를 보여 주므로 레이블에서 재난을 명령하는 동사를 쓸 이유가 없다. `events/krakatoa_events.txt` 278–326행, `content_104_l_korean.yml` 1052–1055행.

```yml
 krakatoa.2.t: "파도의 밤"
 krakatoa.2.d: "굴뚝보다 높은 파도가 몰아치면서 [SCOPE.sState('tsunami_state').GetName] 주가 황폐해졌다. 화산 폭발이 불러온 끔찍한 결과였다."
 krakatoa.2.f: "\"나는 그 침묵을 절대 잊지 못할 것 같다.\""
 krakatoa.2.a: "이 비극을 말로 표현할 길이 없구나."
```

### 제목과 설명

- **제목의 출처**는 사건을 식별할 단서다. 쇄국 이벤트는 비유를 택했지만, `ep2_sakoku.3.t`는 `[SCOPE.sCharacter('morrison_incident_country_namesake').GetLastNameNoFormatting] 사건`으로 표시한다. 해당 이벤트의 `immediate`가 외국 장군을 골라 같은 이름으로 저장한다. 실제 역사에서 통용되는 사건명이 있어도 이 분기에서는 게임이 선택한 인물의 성을 쓴다. `events/japan_events/ep2_sakoku_events.txt` 157–162, 221–231행과 `ep2_sakoku_l_korean.yml` 29–30행.
- **문장 부호**도 제목의 뜻에 따른다. `strike.1.t`의 ‘파업!’은 사건의 발생을 알리고, `bic_breakup.1.t`의 ‘영국 지배의 종말?’은 결말을 열어 둔다. 짧은 명사구에 온점을 붙이지 않는 관례와 양립한다. `events/strike_events.txt` 및 `events/bic_breakup.txt` 각 8행, `content_1_l_korean.yml` 232, 1769행.
- **설명의 출처**는 방금 성립한 상황, 영향을 받는 대상, 아직 해결되지 않은 갈등이다. `opium_wars.1.d`는 ‘아편 중독으로 `[ROOT.GetCountry.GetName](이)가` 황폐해지고 있다.’로 시작한다. 이어 중독된 문화 집단과 공급국을 지목한다. `immediate`에서 무역 시장의 소유국을 `opium_exporter`로, 아편에 집착하는 주류 문화 중 하나를 `addicted_culture`로 저장한다. 그래서 중국·영국 같은 고정 국명 없이도 누가 영향을 받고 누가 공급하는지 표현할 수 있다. `events/opium_wars_events.txt` 4–10, 76–112행, `content_1_l_korean.yml` 508–510행.
- **조사와 시제**는 실제 대입값을 넣어 읽는다. 위 설명의 `[SCOPE.sCountry('opium_exporter').GetName](은)는`처럼 가변 명칭 직후에 조사 표기를 붙인다. `ep2_sakoku.3.d`의 선박명은 `#italic [SCOPE.sCharacter('morrison_incident_country_namesake').GetLastNameNoFormatting]#!(은)는`처럼 강조를 닫은 뒤 조사를 붙인다. 진행 중인 중독에는 ‘-고 있다’, 이미 벌어진 통상 분쟁에는 ‘시도했다’·‘악화했다’가 쓰인다. `content_1_l_korean.yml` 509행, `ep2_sakoku_l_korean.yml` 30행.
- **설명의 화자**에는 1인칭도 있다. `opium_wars.3.d`와 `.d2`는 모두 ‘우린 극기 정신을 발휘한 끝에’로 시작한다. 가해국 변수 보유국이 있으면 전자는 그 국가를 지목하고, 뒤의 기본 분기는 ‘열강’이라고만 한다. 국가의 시점으로 승리를 회고하는 설명과 플레이어가 지금 내릴 결정은 구별할 수 있다. `events/opium_wars_events.txt` 318–341행, `content_1_l_korean.yml` 522–525행.

### 풍미문과 인용의 출처

| 형식 | 한국어 원문에서 확인할 표지 | 작성할 때의 판단 |
|---|---|---|
| 장면과 대화 | `ep2_sakoku.2.f`는 세관 풍경을 평서형 과거로 서술한다. 관료의 직접화법에는 `\"`를 쓰고, `\n\n`으로 문단을 가르며, 마지막 생각은 `#italic`과 `#!` 사이에 둔다. | 서술자와 발화자의 말높임을 따로 고른다. 이 장면에는 작가명이나 문헌 표기가 없다. 새로 만든 대화에 역사 인물의 이름을 출전으로 붙이지 않는다. |
| 한 인물의 관찰 | `ep2_sakoku.3.f`에서 배가 돌아서길 바라는 사람은 해안 포대 지휘관이다. 앞선 `.d`는 무단 교역과 관계 악화를 설명한다. | 현장 인물이 볼 수 있는 배와 포대에 시점을 둔다. 그가 알 수 없는 외교적 결과는 설명에 맡긴다. |
| 출전이 표시된 인용 | `japan_politics.1.f`의 값 안에는 `\n\n—후쿠자와 유키치, \"학문의 권장\"`이 있고, 닫는 따옴표 밖에는 `# Translated by Eiichi Kiyooka`라는 제작진 주석이 있다. | 게임에 표시되는 저자·작품과 파일에만 남는 번역 관련 메모를 구분한다. 이 주석만으로 한국어 번역자를 특정할 수 없다. EAFP에서 실존 인물의 말을 직접 인용하려면 해당 문헌과 사용할 판본에서 문구·귀속을 확인한다. |
| 각색한 문서 | `japan_monarchy.5.f`는 `#bold 황실 칙령#!\n\n`으로 시작하고 새 연호와 인물 이름을 대입한다. 값 뒤의 영문 주석은 일세일원 칙령을 축약했다고 밝힌다. | 칙령의 1인칭·선포형을 살린다. 게임 진행에 따라 바뀌는 이름을 넣은 축약문을 사료의 정확한 전사로 소개하지 않는다. |

장면의 호출은 `events/japan_events/ep2_sakoku_events.txt`의 `ep2_sakoku.2`와 `ep2_sakoku.3`, 값은 `ep2_sakoku_l_korean.yml` 25, 31행이다. 인용과 칙령의 호출은 각각 `events/japan_events/ep2_japan_political_events.txt` 12행과 `events/japan_events/ep2_imperial_events.txt` 448행, 값은 `ep2_04_l_korean.yml` 4, 390행이다.

### 선택지의 문법과 선택 결과

**접미사가 충돌하는 실제 사례.** `strike.2`의 설명은 `strike.2.desc`, 풍미문은 `strike.2.flavor`다. `strike.2.d`와 `strike.2.f`는 각각 ‘근로자 보호법 통과를 약속한다.’와 ‘사회 보장 제도 확장을 약속한다.’라는 네 번째·여섯 번째 선택지다. 설명과 풍미문으로 분류하면 노동자가 하는 말과 정부가 하는 약속의 화자까지 바뀐다. `events/strike_events.txt` 128–134, 156–228행, `content_1_l_korean.yml` 237–246행.

다음은 `content_1_l_korean.yml` 511–512행의 두 레이블이다. `l_korean:` 아래에서 키와 값을 한 물리적 줄에 쓴다.

```yml
l_korean:
 opium_wars.1.a: "우리가 나서야 해!"
 opium_wars.1.b: "그렇다고 [SCOPE.sCountry('opium_exporter').GetName]의 노여움을 살 순 없어."
```

`events/opium_wars_events.txt`의 `opium_wars.1`에서 `.a`는 `je_opium_obsession`을 추가해 개입을 시작한다. `.b`는 아편 중독 변화 요인을 더 길게 적용하고 급진파를 늘린다. ‘나서야 해!’와 ‘노여움을 살 순 없어’는 각각 개입 의지와 외교적 우려를 말한다. 두 구어체 어미는 선택하는 쪽의 태도를 드러낸다. 레이블만 읽은 사람이 예상하는 행동을 실제 효과와 대조한다.

`ep2_sakoku.2`에서는 `.a`(기본값)가 `law_mercantilism`을, `.b`가 `law_free_trade`를, `.c`가 `law_protectionism`을 채택한다. `.b`와 `.c`에는 각각 `exists = scope:free_trade_ig`와 `exists = scope:protectionism_ig` 조건이 있다. `trigger`는 선택 가능 조건, `activate_law`는 선택 결과, `ai_chance`는 AI의 선택 가중치다. 번역할 때는 각 `option`에 지정된 요소를 확인하고, 다른 선택지가 보인다는 전제 없이 각 레이블을 읽어 본다. `events/japan_events/ep2_sakoku_events.txt` 65–115행, `ep2_sakoku_l_korean.yml` 26–28행.

### 조건부 제목·설명·풍미문

| 이벤트 | 스크립트가 고르는 키 | 문안을 검토할 때 놓치기 쉬운 점 |
|---|---|---|
| `hokkaido_events.1` | `title` 안의 `first_valid → triggered_desc → desc`는 일본(`c:JAP ?= ROOT`)이면 `hokkaido_events.1.t` ‘여덟 번째 도’, 에조(`c:EZO ?= ROOT`)면 `hokkaido_events.1.t_1` ‘북부의 관문’을 고른다. 설명도 `.d`와 `.d_1`로 갈리고 풍미문은 `.f` 하나를 공유한다. | 안쪽 필드 이름이 `desc`여도 바깥 필드가 `title`이면 제목이다. 두 제목 분기에는 무조건 참인 마지막 항목이 없다. `events/japan_events/ep2_hokkaido_events.txt` 10–42행, `ep2_02_l_korean.yml` 154–158행. |
| `ep2_meiji.41` | 제목은 `ep2_meiji.4.t`를 재사용한다. 설명과 풍미문은 각각 `first_valid`를 평가한다. 막부법, 정부 내 전직 쇼군, 대군정 중 하나가 성립하면 `.41.d`·`.41.f`를, 그 뒤의 `always = yes` 분기는 `.41.d_1`·`.41.f_1`을 쓴다. | 앞에서는 유신파가 막부에 맞서고, 뒤에서는 존왕양이 세력이 외국인 추방을 거부한 정부에 맞선다. 두 설명의 주체를 바꾸면 분기의 정치적 의미가 뒤집힌다. 선택지는 별도의 `ep2_meiji.41.a`·`ep2_meiji.41.b`다. `events/japan_events/ep2_meiji_restoration.txt` 408–452, 500–505행, `ep2_04_l_korean.yml` 58, 63–68행. |

## 설치본에서 다시 확인하기

`game/`에서 아래처럼 이벤트 정의와 번역을 따로 찾는다. 첫 검색으로 찾은 이벤트 블록에서 필드의 우변, 조건, 저장한 스코프, 선택 결과를 읽는다. 이어서 두 번째 검색으로 실제 키와 한국어 문안을 확인한다. 패치로 번호나 파일이 달라지면 해당 블록의 우변으로 검색식을 갱신한다.

```powershell
rg -n '^\s*ep2_sakoku\.2\s*=' events
rg -n '^\s*ep2_sakoku\.2\.(t|d|f|[abc]):[0-9]*\s*"' localization/korean
```
