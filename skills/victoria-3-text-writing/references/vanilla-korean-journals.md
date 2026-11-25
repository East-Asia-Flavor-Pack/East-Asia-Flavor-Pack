# 바닐라 한국어 저널 문안

Victoria 3 **1.15.2 (Ivan-Chai)** 기준이다. 경로는 설치 폴더의 `game/`에서 시작하며, 한국어 YML 파일은 모두 `localization/korean/` 아래에 있다. 저널은 여러 달 또는 여러 해 동안 같은 항목을 다시 열어 본다. 제목은 항목을 식별하고, 이유는 왜 개입하는지 설명하며, 상태·진행·결말은 열어 본 시점에 맞는 정보를 준다.

## 한 저널에서 제목·이유·상태 읽기

`common/journal_entries/00_taiping.txt` 273행의 `je_taiping`에는 별도의 `reason`이나 `status_desc` 지정이 없다. 다음 세 줄이 각각 다른 자리에 쓰인다. `content_1_l_korean.yml` 180–182행.

```yml
l_korean:
 je_taiping: "태평천국 운동 분쇄"
 je_taiping_status: "태평천국 운동을 진압해야 한다."
 je_taiping_reason: "광신자들이 우리의 정당한 통치에 반기를 들고 일어났다! 반란군을 철저하게 짓밟아야 한다."
```

- **제목**은 대상 ‘태평천국 운동’에 목표 ‘분쇄’를 붙인 명사구다. 제목의 출처는 `je_taiping`이라는 항목 자체다. 이벤트처럼 `title = …`나 `.t`를 따로 붙이지 않는다.
- **이유**의 ‘우리의 정당한 통치’는 청 조정이 상황을 보는 방식이다. ‘광신자들’과 ‘철저하게 짓밟아야 한다’도 이 화자의 어휘다. 반란군 시점의 항목으로 옮길 때는 적과 아군을 다시 짚는다. EAFP에서도 당대 세력의 가치 판단을 인용·서술하는 주체가 드러나게 쓴다.
- **상태**는 해결해야 할 과제를 한 문장으로 되짚는다. 이 항목에서는 현재 수치도, ‘… 중’ 같은 명사형 어미도 필요하지 않다. 반면 여러 단계가 있는 항목은 아래의 `status_desc`처럼 단계별로 갈라 쓸 수 있다.

### 자동으로 찾는 키와 스크립트가 지정하는 키

| 표시 위치 | 키를 찾는 순서 | 확인할 사례 |
|---|---|---|
| 활성 항목 제목 / 종결 목록의 제목 | 활성 제목은 저널 ID 자체다. 종결 목록은 스코프 없이 이름을 읽으므로 동적 제목에는 정적인 `<ID>_concluded`를 마련한다. | `je_meiji_main`은 `[ROOT.Var('emperor_var').GetCharacter.GetFirstName] 복권`, `je_meiji_main_concluded`는 ‘황실 복권’이다. `common/journal_entries/00_meiji_restoration.txt` 883행, `content_1_l_korean.yml` 642–643행. |
| 이유 | 명시한 `reason`이 있으면 그 키 또는 분기를 따른다. 필드가 생략되면 `[JournalEntry.GetReason]`은 `<ID>_reason`을 읽는다. | `je_sakoku`는 이유를 별도 지정하지 않는다. ‘쇄국’ 아래의 `je_sakoku_reason`은 제한된 항구 교류, 오래 유지된 질서, 외압이 가져올 변화 순으로 쓴다. `common/journal_entries/07_sakoku.txt`의 `je_sakoku`, `ep2_sakoku_l_korean.yml` 2–3행. |
| 상태 | `status_desc`가 있으면 그 분기를 따른다. 생략되면 `[JournalEntry.GetStatusDesc]`은 `<ID>_status`를 찾는다. | 위 태평천국 사례는 기본 키를 쓴다. `je_divided_monarchists`는 별도 키 `status_dynasty_cementing_fra`를 쓴다. |
| 일반 진행 표시 | `progress_desc`를 지정할 수 있다. 생략되면 `[JournalEntry.GetProgressDesc]`의 기본 키는 `<ID>_progress`다. 수치 막대의 표시 여부와 계산식은 해당 저널 정의를 본다. | `je_cement_the_rightful_dynasty`는 일반 진행 막대에 `progress_desc` 분기를 지정한다. 별도로 등록하는 `scripted_progress_bar`의 `desc`는 해당 막대 정의에서 찾는다. |

기본 조회 규약은 배포된 `common/journal_entries/journal_entries.md` 6–8, 234–238, 251–254, 400–404행에 명시되어 있다. 화면에서도 `gui/journal_entry.gui` 355–356, 693, 765–766행이 상태·이유·진행을 각각 읽는다. 상태와 진행 문구는 빈 문자열이면 해당 표시를 숨기는 조건이 있다. 표에 나온 기본 키를 모든 저널에 일괄 생성할 필요는 없다.

## 이유의 화자와 조건부 문단

- **짧은 국정 판단.** `je_opium_obsession_reason`은 중독자가 늘어난 사실에서 ‘이 국가적 수치를 빠르게 수습해야 한다.’로 나아간다. 반대로 아편 수출국의 `je_opium_wars_reason`은 무역을 유지할 경제적 이해를 말한다. 같은 사태에서도 저널을 소유한 쪽에 따라 주어와 목표가 다르다. `common/journal_entries/00_opium_wars.txt`의 `je_opium_obsession`과 `je_opium_wars`, `content_1_l_korean.yml` 505–506, 519–520행.
- **역사 설명과 시스템 안내가 함께 있는 경우.** `je_ryukyu_rivalry_reason`은 슈리 궁정과 두 이웃 국가의 관계를 ‘-습니다’체로 서술한다. 두 문단 뒤 `\n$TOOLTIP_DELIMITER$\n`부터 `@warning!`으로 실패 조건을, `@information!`으로 환심을 살 방법을 열거한다. 이 원문에서 `\n\n`은 역사 서술의 문단 경계, `\n`은 안내의 행 경계다. 외교 관계는 문장으로 설명하고, 수치·조건은 다시 찾기 쉬운 줄로 둔다. 원문의 1609년 침공은 역사 서술의 근거를 따로 확인할 대상이고, 적극성 100%는 이 저널의 막대와 결말 조건에서 확인할 게임 수치다. 같은 파일 70행의 `#je_ryukyu_rivalry_goal`은 주석이다. `common/journal_entries/01_ryukyu_rivalry.txt`의 `je_ryukyu_rivalry`, `ep2_01_l_korean.yml` 68–70행.
- **상태에 따라 이유가 바뀌는 경우.** `je_ukraine_cultural_renaissance`의 `reason → first_valid`는 `hromada_var`와 `prosvita_var`가 모두 없을 때 기본 서술을 고른다. 이후 흐로마다에 대한 허용·감시·억압 분기, 프로스비타에 대한 후원·자체 조달·억압 분기가 순서대로 온다. 처음 참인 분기의 값 하나가 선택된다. `common/journal_entries/08_cultural_renaissances.txt` 112–146행, `ip5_06_l_korean.yml` 3–11행.

마지막 사례의 허용 분기는 아래처럼 원래 서술과 안내를 재사용한다. `$…$` 안에는 실제 한국어 키가 있고, 그 밖에 지금 선택된 정책의 결과 한 문장만 덧붙인다. 이때 기본 사유를 고치는 일과 허용 분기의 의미를 고치는 일은 서로 다른 편집이다.

```yml
 je_ukraine_cultural_renaissance_reason_hromada_permitted: "$je_ukraine_cultural_renaissance_reason$\n\n$je_ukraine_cultural_renaissance_hromada_info$ 이 사회는 자유로운 운영이 허용될 것입니다."
```

## 목표·상태·진행률의 문법

**목표는 도달점이다.** `je_sol_1`의 `outcome → trigger → custom_tooltip`은 `text = je_sol_goal_desc`를 사용한다. 한국어 값은 ‘국내의 `[concept_sol]`을 3만큼 개선해야 한다.’다. `current_value`는 평균 생활 수준이고 `goal_add_value`가 `3`이므로 기준값에서 3만큼 높이는 상대 목표다. ‘생활 수준 3 달성’이라고 쓰면 조건이 달라진다. 목표를 쓸 때는 비교 대상, 기준 시점, 절댓값·증가분, 단위를 계산식과 대조한다. `common/journal_entries/00_standard_of_living.txt` 49–60, 98–104행, `content_104_l_korean.yml` 162행.

**기간에는 누적과 연속의 차이가 있다.** `je_opium_obsession`은 월간 처리에서 아편 금지·평화 조건이 맞을 때 카운터를 1 올린다. 이 블록에는 조건이 틀린 달에 카운터를 초기화하는 분기가 없다. 목표 증가분은 60이고 월 단위로 표시한다. 한국어 `je_opium_obsession_goal`에도 ‘총 5년’과 ‘방해받을 수 있음’이 함께 들어 있다. 완료 시점에는 금지 여부와 평화 상태도 다시 검사한다. 이 키가 YML에 있다는 사실과 어떤 GUI가 그 키를 직접 호출하는지는 별도 근거가 필요하다. `common/journal_entries/00_opium_wars.txt` 17–49, 120–131행, `content_1_l_korean.yml` 507행. 일반 저널 목록의 진행 표시와 목표 툴팁은 `gui/journal.gui` 1081–1082행의 `GetProgressDesc`와 `GetGoalDesc`에서 확인할 수 있다.

**상태는 지금 어느 단계인지, 진행 문구는 목표를 향해 어떻게 움직이는지를 알려 준다.** `je_divided_monarchists`의 첫 상태 분기는 왕조 공고화 저널이 활성일 때 `status_dynasty_cementing_fra`를 골라 집권 가문이 주도권을 공고히 한다고 표시한다. 반면 별도 저널 `je_cement_the_rightful_dynasty`는 `is_progressing = yes`이고 정부 정통성이 90 이상일 때 `je_cement_the_rightful_dynasty_progressing_fast`를, 이어지는 75 이상 분기에서는 `…_normal`을 고른다. 높은 값이 두 수치 조건을 모두 만족하므로 순서가 중요하다. `…_fast`의 한국어는 ‘왕조의 통치에 의심의 여지가 없다.’로 끝난다. 수치 대신 정치적 의미를 말하는 진행 문구의 실제 예다. `common/journal_entries/01_french_monarchism.txt` 58–65, 328–347행, `agitators_3_l_korean.yml` 153행, `agitators_1_l_korean.yml` 103–104행.

**별도로 정의한 진행 막대**는 저널 → 막대 ID → 막대 정의의 `name`·`desc` 순서로 읽는다. `je_ryukyu_rivalry`는 환심과 적극성 막대를 따로 등록한다. 적극성 막대의 이름과 표시 문구는 다음과 같다. `common/journal_entries/01_ryukyu_rivalry.txt` 11–12행, `common/scripted_progress_bars/00_ep2_ryukyu_rivalry_progress_bars.txt` 368–375행, `ep2_ryukyu_rivalry_l_korean.yml` 6–7행.

```yml
 je_ryukyu_rivalry_progress_bar: "류큐 #tooltippable;tooltip:ryukyu_rivalry_assertiveness_tt #b 적극성#!#!"
 je_ryukyu_rivalry_progress_bar_desc: "류큐가 중립을 주장함 #v [JournalEntry.GetCurrentBarProgress(ScriptedProgressBar.Self)|%]#!"
```

안쪽 `#b`와 바깥 툴팁 영역에는 각각 닫는 `#!`가 필요하다. `ryukyu_rivalry_assertiveness_tt`의 설명은 별도 파일 `ep2_01_l_korean.yml` 77행에 있다. 표시 문구의 `ScriptedProgressBar.Self`는 해당 막대를 가리키고 `|%`는 백분율 서식이다. 같은 저널의 환심 막대는 `desc`와 `second_desc`로 양쪽 국가명을 따로 표시한다. 막대마다 어떤 양 또는 대상을 보여 주는지 정의를 확인한다. `common/scripted_progress_bars/00_ep2_ryukyu_rivalry_progress_bars.txt` 3–6행, `ep2_ryukyu_rivalry_l_korean.yml` 3–5행.

## 버튼·조건 툴팁·결말

**쇄국 저널의 버튼.** `common/journal_entries/07_sakoku.txt` 15행의 `scripted_button = je_sakoku_stop_being_closed_button`을 따라가면 `common/scripted_buttons/sakoku_buttons.txt` 1–19행에서 레이블·설명·조건과 실행 효과를 확인할 수 있다.

| 확인할 곳 | 이 버튼에서의 의미 | 한국어 예제 |
|---|---|---|
| `name` | 플레이어가 할 일 | `je_sakoku_stop_being_closed_button`은 `[GetLawType('law_sakoku').GetName] 철회`라는 행동명이다. |
| `desc` | 지금 이 결정을 내리는 상황과 비용·위험 | 같은 이름에 `_desc`가 붙은 키에서 외국의 압력과 옛 법을 지지하는 사람들의 반발을 설명한다. |
| `visible`, `possible → custom_tooltip → text` | 버튼이 보이고 실행 가능한 조건 | 양쪽에서 `je_sakoku_maybe_we_should_open_up` 변수를 검사한다. 툴팁 키 `faced_sufficient_pressure_to_abolish_sakoku_tt`의 한국어는 ‘압력을 가하고 있음’으로 끝난다. |
| `effect → trigger_event` | 누르면 실제로 일어나는 일 | 버튼은 `ep2_sakoku.2`를 연다. 구체적인 통상법은 그 이벤트의 선택지에서 정한다. 버튼 설명에 한 법의 채택을 기정사실로 쓰지 않는다. |

버튼 이름과 설명은 `ep2_sakoku_l_korean.yml` 5–6행, 조건 툴팁은 `ep2_04_l_korean.yml` 718행, 후속 선택지는 `events/japan_events/ep2_sakoku_events.txt`의 `ep2_sakoku.2`와 `ep2_sakoku_l_korean.yml` 26–28행에서 확인할 수 있다.

**결말의 조건, 효과, 종결문.** `je_ryukyu_rivalry`의 일본 승리 `outcome`은 달성 조건의 머리말(`header`), 달성 시 효과의 머리말(`effect_header`), 종결 후 표시할 한 줄(`conclusion_desc`)을 각각 명시한다. 다음은 이 결말이 사용하는 세 키의 원문이다. `common/journal_entries/01_ryukyu_rivalry.txt` 102–115행, `ep2_01_l_korean.yml` 71–72, 82행.

```yml
 je_ryukyu_rivalry_victory_japan: "#b 일본#! 승리 달성 조건:\n"
 je_ryukyu_rivalry_on_japan_victory: "#b 일본#! 승리 시:\n$EFFECT$"
 je_ryukyu_rivalry_victory_japan_conclusion_desc: "$concept_journal_entry$이 #b 일본#! 승리로 종료되었습니다"
```

첫 머리말 아래의 실제 조건은 `trigger`가 제공한다. 이 결말에서는 환심 막대가 40 이상인지 검사하고 `ryukyu_influence_victory_japan_tt`로 조건을 설명한다. 두 번째 값의 `$EFFECT$`는 호출 측이 채우는 효과 문구 자리이므로 그대로 둔다. 마지막 값은 이미 끝난 결과를 말한다. 종결 목록용 제목 `<ID>_concluded`와도 용도가 다르다. 쇄국처럼 공통 키 `je_standard_completion_header`·`je_standard_on_completion_header`·`je_standard_completion_conclusion_desc`를 쓰는 저널도 있다. `common/journal_entries/07_sakoku.txt` 30–34행, `journal_entries_l_korean.yml` 48–53행, `gui/journal_entry.gui` 126행.

## 설치본에서 다시 확인하기

`game/`에서 저널 ID로 정의를 열고, 지정된 버튼·막대·결말 키를 해당 정의와 한국어 파일까지 한 단계씩 따라간다. 기본 키는 스크립트에 문자열이 나타나지 않을 수 있으므로 기본 조회 규약과 GUI도 함께 본다.

```powershell
rg -n '^\s*je_ryukyu_rivalry\s*=' common/journal_entries
rg -n '^\s*je_ryukyu_rivalry_progress_bar\s*=' common/scripted_progress_bars
rg -n '^\s*je_ryukyu_rivalry(_reason|_progress_bar(_desc)?|_on_japan_victory)?:[0-9]*\s*"' localization/korean
```
