# `joseon-confucian-absolutism` 브랜치 계획: 「유학의 왕국」 저널 수정안 (예치의 길과 용하변이 법률)

> 기준: `main`(76f2c15f)에서 분기
> 수정 대상: 기존 조선 저널 `je_korean_confu` 「유학의 왕국」 (`common/journal_entries/eafp_korean_journal.txt:1382`)
> 참고 원형: 바닐라 오스트리아 `je_austrian_neo_absolutism`(신 절대주의) → `law_neo_absolutism`

## 한눈에 보기

새 저널을 따로 만들지 않고, 기존 「유학의 왕국」에 **두 번째 결말**을 더한다.

- **개화의 길 (기존)**: 세계 인식 막대가 1000에 이르면 「새로운 물결」(`eafp_kor_mainline.171`)로 끝난다. 지금 저널이 가진 유일한 결말이다.
- **예치(禮治)의 길 (신규)**: **정통 유교 체제**(전제정치·과거·유교·서원)를 지키며 완료 조건 8개 중 6개를 갖춘 달이 **60개월(5년)** 쌓이면 끝난다. 전제정치(`law_autocracy`)를 **조선 전용 하위 법률 용하변이(用夏變夷)**로 바꾼다. 이 법률은 전제정치의 정치적 성격을 물려받되, 효과는 **종교 개종과 문화 동화**에 집중한다.

두 길은 **경주**한다. 무역과 기술이 세계 인식을 끌어올리는 동안, 조선은 체제를 지킨 채 예치의 조건을 채워야 한다. 네 체제 가운데 하나라도 고쳐져 있는 동안은 예치의 정착이 멈춘다. 체제를 되돌리면 쌓인 개월 수에서 이어서 센다.

예치 쪽 진행은 바닐라 「덴포 위기」(`je_tenpo_crisis`)처럼 저널 본문의 **체크박스 목록**과 **정착 기간(개월)**으로 보여 준다. 새 막대나 버튼은 없다.

| 구분 | 바닐라 오스트리아 | 수정된 「유학의 왕국」 |
|---|---|---|
| 저널 | `je_austrian_neo_absolutism` 신 절대주의 | 기존 `je_korean_confu` **유학의 왕국**을 수정 (새 저널 없음) |
| 활성화 | 게임 시작부터 | 그대로. 조선 히스토리(`kor - korea.txt:102`)에서 추가 |
| 결말 | 성공 1개 / 실패 | **개화의 길**(기존) / **예치의 길**(신규) / 무효(기존, 국교가 유교가 아님) |
| 유지할 체제 | 전제정치 + 비밀경찰 | 예치의 길을 위해 **전제정치 + 과거 관료제 + 유교 국교 + 서원 수정안** |
| 지지 세력 | 소부르주아가 정부에서 강력 | 따로 두지 않는다. 완료 조건 「유림의 지지」가 대신한다 |
| 진행 표시 | 헌정 압력 막대 (100 도달 시 실패) | 기존 **세계 인식 막대**(개화의 길) + 예치 **체크박스**와 정착 기간 `N/60개월` |
| 버튼 | 교황 정교협약 / 봉건 의무 폐지 / 왕령지 자치 폐지 | 기존 「집중 교화」만. 새 버튼 없음 |
| 예치 완료 | 6개 중 4개 충족 즉시 | **8개 중 6개를 갖춘 달이 60개월** (3.4·3.5절) |
| 예치 실패 | 헌정 압력 100 등 | 세계 인식 1000(개화 결말)에 먼저 이르면 예치의 길도 끝난다. **유지 조건 상실**은 실패가 아니라 정착을 멈출 뿐이다 (3.6절) |
| 보상 법률 | `law_neo_absolutism` (관료 정치력, 권위) | `law_eafp_yongha_byeoni` **용하변이(用夏變夷)**, 개종·동화 특화 |

---

## 1. 바닐라 원형 분석 (`05_austria_journal_entries.txt`)

| 요소 | 바닐라 구현 | 조선판에서 가져올 것 |
|---|---|---|
| `possible` | 전제정치·비밀경찰 유지, 왕령지/동군연합 종속국 없음, 소부르주아 강력 | 체제 유지 조건 구조만 가져와 **정착 기간이 늘 수 있는 조건**으로 쓴다. 유학의 왕국은 히스토리에서 바로 추가되므로 시작 조건과 지지 세력 조건은 두지 않는다 |
| `immediate` | 시작 시 GDP를 `austrian_gdp_var`에 저장 | 유학의 왕국의 **첫 월간 처리**에서 GDP × 1.5 목표값을 저장한다. 이 저널은 히스토리에서 GDP가 계산되기 전에 추가되므로 `immediate`에서는 GDP가 0이다. 덴포 위기도 같은 이유로 `tenpo_gdp_goal`을 게임 시작 후 on_action에서 저장한다 |
| `modifiers_while_active` | `modifier_austrian_state_police` | 기존 `eafp_modi_confucian_state` 「성리학 국가」를 그대로 쓴다 |
| 진행 막대 | `default_bad` 헌정 압력. 매달 여러 요인으로 증감, 100이면 실패 | **기존 세계 인식 막대가 이 역할을 맡는다.** 1000에 이르면 개화 결말로 저널이 끝나 예치의 길도 사라진다. 예치 쪽 진행은 막대 없이 체크박스와 정착 개월 수로 보여 준다 (3.4절) |
| 버튼 3개 | 누르면 변수 설정 + 막대 ±10 + 부수 효과 | **가져오지 않음.** 기존 「집중 교화」 버튼만 남고, 버튼 몫의 완료 조건은 국가 상태 조건으로 바꾼다 |
| 성공 | `calc_true_if amount >= 4` → `austria_events.1` 팝업에서 `law_neo_absolutism` 즉시 시행 선택, 전역 변수로 법률 노출 | 완료 조건을 갖춘 달이 60개월(5년) 쌓이면 성공. 노출 조건은 **국가 변수**로 (조선 전용이므로) |
| 실패 | 막대 100 / 헝가리 동군연합 / 전제정치·비밀경찰 상실 | 세계 인식 1000(개화 결말). 유지 조건 상실·군주제 상실·종속국화는 그동안 정착을 멈출 뿐 길을 닫지 않는다 |
| 법률 | `parent = law_autocracy`, `requires_law_or = law_monarchy`, `law_autocracy`의 `is_visible`에서 숨김 처리 | 같은 구조. 단 **`law_autocracy`는 재정의하지 않음** (4.4절) |

---

## 2. 기존 조선 콘텐츠와의 관계

새 체계를 따로 만들기보다 이미 있는 조선 상태를 조건과 입력값으로 재사용한다.

| 기존 요소 | 위치 | 이 저널에서의 쓰임 |
|---|---|---|
| `law_scholar_bureaucrats` (과거 관료제) | `common/laws/eafp_bureaucracy.txt` | 유지 조건 |
| `amendment_seowon` (서원 수정안) | `common/amendments/eafp_amendments_historical.txt:68`, 시작 설정 `kor - korea.txt` | 유지 조건. 이 수정안 자체가 개종·동화 +20%를 주므로 용하변이 법률과 성격이 이어진다 |
| `eafp_var_sam_all_clear` (삼정의 문란 해결) | `eafp_korean_journal.txt:764` 등 | 완료 조건 하나로 그대로 사용 |
| `je_sedo_politics` (세도정치) | `eafp_korean_journal.txt:1124` | 이 저널이 끝났으면 완료 조건 「세도정치 종식」 충족 |
| `je_korean_confu` 「유학의 왕국」 + `eafp_progress_bar_confu` (세계 인식) | `eafp_korean_journal.txt:1382`, 막대 `eafp_kor_progress_bars.txt:642` | **수정 대상.** 예치의 길을 두 번째 결말로 더한다 (3장) |
| 근대 개혁 저널 `je_korean_reformation_*` | `eafp_korean_reformation.txt` | **연결하지 않는다.** 두 저널은 서로 영향 없이 함께 진행할 수 있다 |

---

## 3. 저널 수정: `je_korean_confu` 유학의 왕국에 예치의 길 더하기

### 3.1 지금의 유학의 왕국과 바뀌는 점

| 요소 | 지금 | 수정 후 |
|---|---|---|
| 막대 | 세계 인식 `eafp_progress_bar_confu` (0~1000). 매달 기본 +2.5, 무역(최대 +20), 기술 습득 시 +20, 쇄국·전통주의·국교 법률마다 -5, AI +7.5 | **그대로** |
| 결말 | 세계 인식 1000 → `eafp_kor_mainline.171` 「새로운 물결」 | 그대로 두고 헤더만 「개화의 길 달성 조건 / 달성 시」로 구분. **예치의 길 결말을 추가** |
| 무효 | 국교가 유교가 아님 | 그대로. 예치 변수 정리만 더한다 |
| 버튼 | 「집중 교화」 | 그대로 |
| 월간 처리 | 천주교 확산, 선교사 생성, 무작위 이벤트 | 그대로 두고 **예치의 길 확인**(유지 조건 검사, 정착 기간 세기)을 더한다 |
| 본문 | 서학을 둘러싼 조정의 논쟁, 천주교 역병 설명 | 그대로 두고 끝에 **예치의 길 단락과 체크리스트**를 붙인다 |

### 3.2 흐름

```mermaid
flowchart TD
    START["게임 시작: 조선(KOR)<br/>je_korean_confu 추가<br/>(첫 달에 GDP 목표값 저장)"] --> JE["유학의 왕국"]
    JE --> BAR["세계 인식 막대 (기존)<br/>무역·기술로 오르고<br/>쇄국·전통주의·국교로 내려감"]
    BAR -- "1000 도달" --> OPEN["개화의 길 (기존)<br/>새로운 물결 .171"]
    JE --> PILLAR{"매달 확인<br/>군주제·전제정치·과거·유교·서원 유지<br/>청 이외 국가의 종속국 아님?"}
    PILLAR -- "하나라도 어긋남" --> S["정착 기간 그대로<br/>(쌓인 개월 수는 유지)"]
    PILLAR -- "유지" --> COND{"완료 조건<br/>8개 중 6개 충족?"}
    COND -- "충족" --> M["정착 기간 +1개월"]
    COND -- "미충족" --> S
    M -- "60개월 (5년) 도달" --> WIN["예치의 길<br/>예악이 바로 서다 (eafp_kor_mainline.172)<br/>용하변이 시행"]
    JE -- "국교가 유교가 아님 (기존)" --> INV["무효"]
```

### 3.3 체제 유지 조건

**유지 조건**: 아래 네 가지를 모두 지키는 달에만 정착 기간이 늘 수 있다. 하나라도 어긋나면 그동안은 정착이 멈추고, 되돌리면 이어서 센다(3.6절).

| 조건 | 판정 |
|---|---|
| 전제정치 | `has_law_or_variant = law_type:law_autocracy` |
| 과거 | `has_law = law_type:law_scholar_bureaucrats` |
| 유교 | `has_law = law_type:law_state_religion` 이고 `country_has_state_religion = rel:confucian` |
| 서원 | `any_active_law = { has_amendment = amendment_type:amendment_seowon }` (모드의 기존 `has_amendment` 사용법과 같다) |

이 밖에 **군주제**(`law_monarchy`, 용하변이 법률의 `requires_law_or`)를 잃거나 **청 이외 국가의 종속국**이 되어도 똑같이 멈춘다. 이 여섯 판정은 scripted trigger `eafp_yechi_pillars_kept` 하나로 묶어, 월간 처리와 체크리스트 요약 줄 두 곳에서 쓴다.

유학의 왕국은 게임 시작 때 히스토리에서 바로 추가되므로, 앞선 계획의 시작 조건(`possible`)과 지지 세력 조건(유림 또는 양반이 정부에서 강력)은 두지 않는다. 체제를 떠받치는 세력의 지지는 완료 조건 「유림의 지지」(3.5절 5번)가 맡는다.

조선 히스토리 파일은 종교 법률을 직접 지정하지 않으므로, 기본값이 `law_state_religion`인지 구현 전에 확인한다. 서원 수정안은 히스토리에서 교육 법률 그룹에 붙이는데 정의상 `parent = law_state_religion`이므로, 실제로 어느 법률에 붙는지도 구현 전에 확인한다.


### 3.4 조건 체크리스트와 정착 기간

예치 쪽에는 새 막대를 두지 않는다. 바닐라 「덴포 위기」(`je_tenpo_crisis`)와 모드의 「삼정이정청」(`je_samjeong_ijeongcheong`)처럼, 유학의 왕국 본문(`je_korean_confu_reason`) 끝에 **조건마다 체크박스**를 붙여 보여 주고, 목록 맨 위 한 줄에 **충족한 조건 수**와 **정착 기간**을 함께 적는다. 개월 수는 조건을 6개 이상 갖춘 달만 센다.

게임 안에서는 대략 이렇게 보인다(☑ = `checkbox_ticked`, ☐ = `checkbox_unticked`).

```
예치의 길
전제 정치, 사대부제, 국교, 서원 가운데 하나라도 고치면 예치의 길이 닫힌다.
☑ 완료 조건을 6개 이상(현재 6/8) 갖춘 채 23/60개월을 지냄
• ☑ GDP가 £1.2M 이상임
• ☐ 삼정의 폐단이 전부 혁파됨
• ☑ 청의 종속국이 아니거나 청이 무너졌으며, 강대국 이상임
• ☑ 세도정치가 끝남
• ☑ 성리학자 세력이 정부에 있고 승인도가 10 이상임
• ☐ 한국 본토 밖의 주 하나 이상에서 한국 문화 인구가 50% 이상임
• ☑ 문해율이 30% 이상임
• ☑ 인구의 90% 이상이 유교를 믿음
```

| 항목 | 방식 |
|---|---|
| 조건 체크박스 | 조건마다 custom loc 하나. 충족이면 `checkbox_ticked`, 아니면 `checkbox_unticked` (바닐라 키, 세 언어 모두 있음) |
| 충족 개수 | 스크립트 값 `eafp_yechi_conditions_completed` (0~8) |
| 정착 기간 | 국가 변수 `eafp_var_yechi_months`. 유학의 왕국 `on_monthly_pulse`에서 체제를 유지하고(`eafp_yechi_pillars_kept`) 충족 개수가 6 이상이면 +1 |
| 조건·체제가 깨졌을 때 | 그달은 늘지 않는다. **쌓인 개월 수는 그대로** 남고, 조건을 다시 갖추면 이어서 센다 |
| 완료 | `eafp_var_yechi_months >= 60` |

**정의가 한 곳에만 있도록** 조건 8개를 각각 scripted trigger로 만든다. 각 트리거는 스크립트 값(개수 세기)과 체크박스 custom loc 두 곳에서 쓴다. 덴포 위기는 체크박스 판정과 개수 판정을 따로 적어 "둘을 맞춰 고칠 것"이라는 주석을 달아 두었는데, 트리거로 묶으면 그럴 필요가 없다.

```
# common/scripted_triggers/eafp_kor_triggers.txt
eafp_yechi_cond_gdp = {
	has_variable = eafp_var_yechi_gdp_goal
	gdp >= var:eafp_var_yechi_gdp_goal
}
eafp_yechi_cond_samjeong = { has_variable = eafp_var_sam_all_clear }
eafp_yechi_cond_sojunghwa = { ... }
eafp_yechi_cond_sedo = { NOT = { has_journal_entry = je_sedo_politics } }
eafp_yechi_cond_devout = { ... }
eafp_yechi_cond_iyeok = { ... }
eafp_yechi_cond_literacy = { literacy_rate >= 0.3 }
eafp_yechi_cond_confucian = { ... }
# 판정 내용은 3.5절 표
```

```
# common/script_values/eafp_kor_values.txt
eafp_yechi_conditions_completed = {
	value = 0
	if = { limit = { eafp_yechi_cond_gdp = yes } add = 1 }
	if = { limit = { eafp_yechi_cond_samjeong = yes } add = 1 }
	# ... 8개 모두 같은 형식
}
```

```
# common/customizable_localization/eafp_KOR_custom_loc.txt
eafp_yechi_checkbox_gdp = {
	type = country
	text = {
		trigger = { eafp_yechi_cond_gdp = yes }
		localization_key = checkbox_ticked
	}
	text = {
		localization_key = checkbox_unticked
	}
}
# 조건 8개 + 맨 위 요약 줄(eafp_yechi_checkbox_conditions, 체제를 유지하고 지금 6개 이상이면 체크)까지 9개
```

유학의 왕국 본체에는 아래를 더한다. 기존 코드는 그대로 둔다.

```
je_korean_confu = {
	...
	outcome = {	# 개화의 길 (기존 결말, 헤더만 바꿈)
		header = je_korean_confu_blossom_cond_header
		effect_header = je_korean_confu_blossom_header
		...
		effect = {
			eafp_effect_confu_cleanup = yes
			trigger_event = { id = eafp_kor_mainline.171 }
			...
		}
	}

	outcome = {	# 예치의 길 (신규)
		header = je_korean_confu_yechi_cond_header
		effect_header = je_korean_confu_yechi_header
		color = "gold_positive"
		conclusion_desc = je_standard_completion_conclusion_desc
		trigger = {
			custom_tooltip = {
				text = eafp_yechi_settled_tt
				has_variable = eafp_var_yechi_months
				var:eafp_var_yechi_months >= 60
			}
		}
		effect = {
			eafp_effect_confu_cleanup = yes
			trigger_event = { id = eafp_kor_mainline.172 popup = yes }
		}
	}

	outcome = {	# 무효 (기존)
		...
		effect = { eafp_effect_confu_cleanup = yes }
	}

	on_monthly_pulse = {
		effect = {
			... 기존 천주교 처리 ...
			# 예치의 길
			if = {	# 첫 달에 한 번
				limit = { NOT = { has_variable = eafp_var_yechi_gdp_goal } }
				set_variable = { name = eafp_var_yechi_gdp_goal value = { value = gdp multiply = 1.5 } }
				set_variable = { name = eafp_var_yechi_months value = 0 }
			}
			if = {
				limit = {
					eafp_yechi_pillars_kept = yes
					eafp_yechi_conditions_completed >= 6
				}
				change_variable = { name = eafp_var_yechi_months add = 1 }
			}
		}
		events = { ... 기존 ... }
	}
}
```

- **결말 정리 효과 묶기**: 지금 두 outcome(완료·무효)이 똑같은 정리(천주교 역병 모디파이어 제거, 무역 변수 제거, 선교사 제거)를 반복한다. 예치 결말까지 세 곳이 되므로 scripted effect `eafp_effect_confu_cleanup`으로 묶고, 예치 변수 두 개(`eafp_var_yechi_gdp_goal`, `eafp_var_yechi_months`)도 여기서 지운다.
- 체제가 어긋나도 길은 닫히지 않는다. 이벤트나 세계 인식 변화도 없고, 그달 정착 기간만 늘지 않는다.
- 바닐라 덴포 위기처럼 GDP는 **목표값 자체**(첫 달 GDP × 1.5)를 저장한다. 그래야 본문에 목표 금액을 `[…Var('eafp_var_yechi_gdp_goal').GetValue|k0]`로 바로 보여 줄 수 있다. 게임 시작 직후에는 GDP가 계산되기 전이라 `immediate`가 아니라 첫 월간 처리에서 저장하고, 정착 개월 수도 그때 0으로 둔다. 그래서 첫 달 전까지는 본문의 GDP 목표가 0으로 보인다.
- 정착 기간은 막대가 없으므로 변수에 담아야 한다. 조건이 깨져도 쌓인 값이 남아야 해서 현재 상태로 다시 계산할 수 없다.
- 기간(5년)은 초안이다.

### 3.5 완료 조건 (8개 중 6개)

체제를 유지하는 동안, 국가 상태 조건 8개 가운데 **6개 이상**을 갖춘 달에만 정착 기간이 늘어난다. 각 조건은 괄호 안의 이름으로 `eafp_yechi_cond_*` scripted trigger가 되고(3.4절), 저널 본문에 체크박스 한 줄씩으로 보인다. GDP 목표값 말고는 모두 현재 상태를 직접 읽는다.

**부국강병·체제**

| # | 조건 | 판정 (초안) | 비고 |
|---|---|---|---|
| 1 | **부국(富國)** (`_gdp`): GDP가 시작 시점의 1.5배 이상 | `gdp >= var:eafp_var_yechi_gdp_goal` (첫 달 GDP × 1.5) | 바닐라와 같은 배율. 덴포 위기처럼 목표값을 저장해 본문에 금액을 보여 준다 |
| 2 | **삼정 해결** (`_samjeong`) | `has_variable = eafp_var_sam_all_clear` | 기존 변수 재사용 |
| 3 | **소중화 계승** (`_sojunghwa`): 청의 종속국이 아니거나 청 붕괴 후(`china_shatters`), 독립국이고 위상 `major_power` 이상 | `is_subject = no` + 국가 위상 | 바닐라의 "열강 3위 + 프로이센 견제" 대응 |
| 4 | **세도정치 종식** (`_sedo`) | `NOT = { has_journal_entry = je_sedo_politics }` | 외척 세도가를 누르고 군주 중심 체제를 세운 상태. `je_korean_fading_power`가 쓰는 판정과 같다 |
| 5 | **유림의 지지** (`_devout`): 유림이 정부에 있고 승인도 10 이상 | `ig:ig_devout = { is_in_government = yes  ig_approval >= 10 }` | 체제를 떠받치는 사림의 지지 |

**교화·동화**

| # | 조건 | 판정 (초안) | 비고 |
|---|---|---|---|
| 6 | **이역 동화(異域同化)** (`_iyeok`): 한국 본토 밖의 주를 하나 이상 가지고, 그 주의 한국 문화 비율 50% 이상 | `any_scope_state = { NOT = { is_homeland_of_country_cultures = root }  culture_percent_state = { target = cu:korean value >= 0.5 } }` | 간도·만주 등. 고향 땅 동화(`state_allow_assimilation_in_homeland_bool`)와 짝을 이루어 **용하변이와 가장 직접 이어지는 조건** |
| 7 | **서원 교육 성과** (`_literacy`): 문해율 30% 이상 | `literacy_rate >= 0.3` | 서원을 지킨 교육의 결과 |
| 8 | **교화(敎化)** (`_confucian`): 국내 인구의 유교 신자 비율 90% 이상 | `religion_percent_country = { target = rel:confucian value >= 0.9 }` | 개종 성과 |

**구현 전 확인할 점**

- **세도정치 종식**: `je_sedo_politics`는 성공해도 남기는 변수가 없다(`eafp_var_je_sedo_politics_balance`를 지운다). 그래서 성공과 무효 종료를 구분하지 못하고 "저널이 끝났음"으로만 판정한다. 성공만 인정하려면 성공 효과에 변수 하나를 추가해야 하는데, 기존 `je_korean_fading_power`가 같은 판정을 쓰므로 그대로 따른다.
- **이역 동화**: 조선 본토의 주는 모두 한국 문화의 고향이라 해당하지 않는다. 시작 시점 조선이 본토 밖 주를 갖고 있지 않은지 확인한다.
- **기준값**: 문해율 30%, 유교 90%, 이역 동화 50%는 초안이다. 1836년 조선의 실제 문해율과 신자 비율을 게임에서 확인하고 조정한다.

### 3.6 예치의 정착이 멈추거나 끝나는 경우

| 결과 | 조건 | 처리 |
|---|---|---|
| 정착 멈춤 | 유지 조건(전제정치·과거·유교·서원) 중 하나라도 어긋남, 군주제 상실, 또는 청 이외 국가의 종속국이 됨 | 그동안 정착 기간이 늘지 않는다. 쌓인 개월 수는 남고, 체제를 되돌리면 이어서 센다. 이벤트·세계 인식 변화 없음 |
| 저널 종료 | 세계 인식 1000 (개화 결말) / 국교가 유교가 아님 (무효) | 기존 결말대로 저널이 끝나고, 정리 효과가 예치 변수도 지운다 |

예치의 길은 **닫히지 않는다.** 저널이 이어지는 한 언제든 체제를 되돌려 정착을 이어 갈 수 있고, 저널은 개화의 길·예치의 길·무효 가운데 하나로 끝난다.

서원 수정안은 의회 절차로 폐지될 수 있고, AI는 `ai_will_revoke` 조건(국교·양심의 자유 법률이 아닐 때)에서 폐지한다. 폐지되면 정착이 멈추므로 저널 본문의 예치 단락에 경고를 적어 둔다.

### 3.7 이벤트 설계 (`events/eafp_kor_events/eafp_kor_mainline.txt`)

예치 결말 이벤트 하나만 둔다. 유학의 왕국 이벤트(`eafp_kor_mainline.120`~`.171`)와 같은 `eafp_kor_mainline` 네임스페이스에 두고, 번호는 개화 결말 `.171` 바로 뒤의 `.172`다. 예치의 길이 닫힐 때는 이벤트를 띄우지 않는다(3.6절).

선택지는 서로 정반대가 아니라, **같은 결말을 받아들이면서 강조점만 다르게** 짰다.

#### `eafp_kor_mainline.172` 예악이 바로 서다 (예치의 길 결말)

유학의 왕국의 예치 결말에서 바닐라 `austria_events.1`처럼 팝업으로 띄운다. 어느 선택지를 골라도 용하변이를 시행한다. 차이는 교화를 **밖(이역)으로 넓히느냐, 안(백성)에서 다지느냐**다.

| | 공통 효과 |
|---|---|
| 해금 | 국가 변수 `eafp_var_yechi_law_unlocked` 설정 (전제정치로 되돌린 뒤에도 법률 화면에 남게 함) |
| 법률 | `activate_law = law_type:law_eafp_yongha_byeoni` |

| 선택지 | 방향 | 모디파이어 (`long_modifier_time`, 10년) | 효과 (초안) |
|---|---|---|---|
| `.oa` 중화의 도로 이역을 바꾸리라 | 새로 얻은 땅의 동화 | `eafp_modi_yechi_iyeok_gyohwa` **이역 교화(異域敎化)** | `state_assimilation_mult` +0.25, `country_authority_add` +50 |
| `.ob` 안을 먼저 바로 세운 뒤에 밖을 교화하리라 | 국내 개종과 교육 | `eafp_modi_yechi_hyangdang_gyohwa` **향당 교화(鄕黨敎化)** | `state_conversion_mult` +0.25, `state_education_access_add` +0.05, `interest_group_ig_devout_approval_add` +2 |

AI 가중치는 이역(만주·간도 등)의 주를 가지고 있으면 `.oa`, 아니면 `.ob` 쪽으로 준다. 이역의 주 보유 판정은 scripted trigger `eafp_yechi_has_iyeok_state`로 둔다.

모디파이어 2개는 모두 `common/static_modifiers/eafp_korea_rework_modi.txt`에 추가한다. 아이콘은 「유학의 왕국」 모디파이어와 같은 `gfx/interface/icons/religion_icons/confucianism.dds`를 기본으로 쓴다. 모디파이어 키 이름은 `documentation/modifiers.log`에서 확인했다.

```
eafp_modi_yechi_iyeok_gyohwa = {	# 예치 성공 .a
	icon = gfx/interface/icons/religion_icons/confucianism.dds
	state_assimilation_mult = 0.25
	country_authority_add = 50
}
eafp_modi_yechi_hyangdang_gyohwa = {	# 예치 성공 .b
	icon = gfx/interface/icons/religion_icons/confucianism.dds
	state_conversion_mult = 0.25
	state_education_access_add = 0.05
	interest_group_ig_devout_approval_add = 2
}
```

### 3.8 이벤트 텍스트 예제

이벤트와 모디파이어 2개 이름의 현지화 초안이다. 모디파이어 설명(`_desc`)은 게임에서 쓰이지 않으므로 두지 않는다. 키는 같은 네임스페이스의 기존 유학의 왕국 이벤트와 같은 `.mt/.md/.mf/.oa/.ob` 규칙을 따른다.

`.172`의 플레이버는 『맹자』 「등문공 상」의 실제 구절(법률 이름의 출전)이다.

**한국어** (`localization/korean/eafp_kor_rework_l_korean.yml`에 추가)

```yaml
eafp_kor_mainline.172.mt: "예악이 바로 서다"
 eafp_kor_mainline.172.md: "[ROOT.GetCountry.GetName]의 조정이 끝내 조종의 법도를 고치지 아니하고 나라를 부강하게 하다. 이에 예로 다스리는 법을 나라의 큰 법으로 삼기로 하였으나, 교화를 안에서부터 펼칠지 밖에서부터 펼칠지를 두고 신료들의 의논이 갈리다."
 eafp_kor_mainline.172.mf: "\"나는 중화의 도로 오랑캐를 변화시켰다는 말은 들었어도, 오랑캐에게 변화되었다는 말은 듣지 못하였다.\"\n\n— 『맹자』 「등문공 상」"
 eafp_kor_mainline.172.oa: "중화의 도로 이역을 바꾸리라."
 eafp_kor_mainline.172.ob: "안을 먼저 바로 세운 뒤에 밖을 교화하리라."

 eafp_modi_yechi_iyeok_gyohwa: "이역 교화"
 eafp_modi_yechi_hyangdang_gyohwa: "향당 교화"
```

**영어** (`localization/english/eafp_kor_rework_l_english.yml`에 추가)

```yaml
eafp_kor_mainline.172.mt: "Rites Restored"
 eafp_kor_mainline.172.md: "The court of [ROOT.GetCountry.GetName] has made the realm rich and strong without altering a single statute of the founding kings. It now resolves to make rule by ritual the great law of the land, yet the ministers are divided on whether its civilizing work should begin at home or beyond the frontier."
 eafp_kor_mainline.172.mf: "\"I have heard of men using the doctrines of our great land to change barbarians, but I have never yet heard of any being changed by barbarians.\"\n\n— Mencius, Teng Wen Gong I (trans. James Legge)"
 eafp_kor_mainline.172.oa: "We shall transform the frontier by the Way of the civilized."
 eafp_kor_mainline.172.ob: "First set our own house in order, then civilize what lies beyond."

 eafp_modi_yechi_iyeok_gyohwa: "Civilizing the Frontier"
 eafp_modi_yechi_hyangdang_gyohwa: "Civilizing the Villages"
```

**중국어 간체** (`localization/simp_chinese/eafp_kor_rework_l_simp_chinese.yml`에 추가)

```yaml
eafp_kor_mainline.172.mt: "礼乐复正"
 eafp_kor_mainline.172.md: "[ROOT.GetCountry.GetName]朝廷终未更改祖宗之法，而国以富强。于是议以礼治为国之大典，然教化当先行于内抑或先及于外，群臣议论不一。"
 eafp_kor_mainline.172.mf: "“吾闻用夏变夷者，未闻变于夷者也。”\n\n——《孟子·滕文公上》"
 eafp_kor_mainline.172.oa: "用夏变夷，教化四方。"
 eafp_kor_mainline.172.ob: "先正其内，而后化其外。"

 eafp_modi_yechi_iyeok_gyohwa: "异域教化"
 eafp_modi_yechi_hyangdang_gyohwa: "乡党教化"
```

구현 시 확인할 점:

- 실제 파일은 UTF-8 BOM, CRLF로 저장한다. 이벤트 키는 `eafp_kor_mainline.171` 키 바로 뒤에, 모디파이어 이름은 `eafp_modi_confucian_state_reverse` 바로 뒤에 둔다.
- 영어 `.172.mf`는 James Legge의 1861년 번역(퍼블릭 도메인)이다. 구현 전에 원문 대조로 문구를 한 번 더 확인한다.
- 모디파이어 값은 초안이다. 특히 `country_weekly_innovation_add` +5는 1830~60년대 조선의 주간 혁신 수치와 비교해 조정한다.

### 3.9 저널 텍스트 예제

유학의 왕국 현지화에서 바꾸거나 더할 부분이다. 저널 이름(`je_korean_confu`)과 기존 본문은 그대로 둔다.

**키 구성**

| 용도 | 키 | 파일 | 비고 |
|---|---|---|---|
| 본문 | `je_korean_confu_reason` | 기존 `eafp_kor_rework_l_*.yml` | 기존 본문(서학 논쟁, 천주교 역병) **뒤에** 예치의 길 단락을 이어 붙인다 |
| 결말 조건 헤더 | `je_korean_confu_blossom_cond_header`, `je_korean_confu_yechi_cond_header` | 기존 `eafp_kor_rework_l_*.yml` | 결말이 둘이 되므로 두 outcome의 `header`를 표준 「완료 조건:」 대신 길 이름으로 바꾼다 |
| 결말 효과 헤더 | `je_korean_confu_blossom_header`, `je_korean_confu_yechi_header` | 같은 파일 | 두 outcome의 `effect_header`를 표준 「완료 시:」 대신 길 이름으로 바꾼다. 바닐라 `je_standard_on_completion_header`처럼 `$EFFECT$`를 담는다 |
| 예치 결말 조건 | `eafp_yechi_settled_tt` | 같은 파일 | 예치 outcome의 "정착 기간 60개월" 조건 |

체크리스트는 덴포 위기·삼정이정청처럼 조건 8줄을 따로 키로 빼지 않고 본문에 바로 쓴다. 각 줄 앞의 체크박스는 `GetCustom('eafp_yechi_checkbox_*')`, 충족 개수는 `ScriptValue('eafp_yechi_conditions_completed')`, 정착 기간은 `Var('eafp_var_yechi_months')`로 읽는다. 삼정 줄은 기존 `$je_korean_land_problem_complete_cond_tt$`를 끌어다 쓴다.

`$law_autocracy$`(전제 정치), `$law_scholar_bureaucrats$`(사대부제), `$law_state_religion$`(국교), `$amendment_seowon$`(서원), `$ig_confucian_k$`(성리학자)는 기존 현지화 키를 끌어다 쓴다. 세 언어 모두에 키가 있는 것을 확인했다. 한국어 문장은 키 바로 뒤에 조사가 붙지 않도록 짰다.

앞선 계획에서 따로 쓴 예치 저널의 제목·로비·교서 형식 본문과 시작 조건 툴팁(`je_eafp_yechi`, `_lobby`, `_seowon_tt`, `_support_tt`)은 쓰지 않는다. 유학의 왕국의 기존 본문이 같은 내용(서학을 두고 갈린 조정)을 이미 담고 있기 때문이다.

**한국어**

```yaml
# eafp_kor_rework_l_korean.yml — 기존 je_korean_confu_reason 값 끝에 이어 붙임
"(기존 본문)...$eafp_modi_catholic_plague_desc$\n\n#bold 예치의 길#!\n$law_autocracy$, $law_scholar_bureaucrats$, $law_state_religion$, $amendment_seowon$ 가운데 하나라도 고치면 예치의 길이 닫힌다.\n[SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_conditions')] 완료 조건을 #v 6#!개 이상(현재 #v [SCOPE.GetRootScope.GetCountry.MakeScope.ScriptValue('eafp_yechi_conditions_completed')|0]#!/#v 8#!) 갖춘 채 #v [SCOPE.GetRootScope.GetCountry.MakeScope.Var('eafp_var_yechi_months').GetValue|0]#!/#v 60#!개월을 지냄\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_gdp')] [concept_gdp]가 @gdp!#v [SCOPE.GetRootScope.GetCountry.MakeScope.Var('eafp_var_yechi_gdp_goal').GetValue|k0]#! 이상임\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_samjeong')] $je_korean_land_problem_complete_cond_tt$\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_sojunghwa')] 청의 종속국이 아니거나 청이 무너졌으며, 독립국으로서 #bold 강대국#! 이상의 위상을 가짐\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_sedo')] 세도정치가 끝남\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_devout')] #bold $ig_confucian_k$#! 세력이 정부에 있고 승인도가 #v 10#! 이상임\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_iyeok')] 한국 본토 밖의 주 하나 이상에서 한국 문화 인구가 #v 50%#! 이상임\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_literacy')] 문해율이 #v 30%#! 이상임\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_confucian')] 인구의 #v 90%#! 이상이 유교를 믿음"

# eafp_kor_rework_l_korean.yml — 세계 인식 막대 키 뒤에 추가
 je_korean_confu_blossom_cond_header: "#b 개화의 길#! 달성 조건"
 je_korean_confu_yechi_cond_header: "#b 예치의 길#! 달성 조건"
 je_korean_confu_blossom_header: "#b 개화의 길#! 달성 시:\n$EFFECT$"
 je_korean_confu_yechi_header: "#b 예치의 길#! 달성 시:\n$EFFECT$"
 eafp_yechi_settled_tt: "예치의 정착이 #v 60#!개월(#v 5#!년)에 이름"
```

**영어**

```yaml
# eafp_kor_rework_l_english.yml — appended to the existing je_korean_confu_reason value
"(existing text)...$eafp_modi_catholic_plague_desc$\n\n#bold The Path of Rule by Ritual#!\nAltering any of $law_autocracy$, $law_scholar_bureaucrats$, $law_state_religion$, $amendment_seowon$ closes this path.\n[SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_conditions')] At least #v 6#! completion conditions met (currently #v [SCOPE.GetRootScope.GetCountry.MakeScope.ScriptValue('eafp_yechi_conditions_completed')|0]#!/#v 8#!) for #v [SCOPE.GetRootScope.GetCountry.MakeScope.Var('eafp_var_yechi_months').GetValue|0]#!/#v 60#! months\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_gdp')] [concept_gdp] is @gdp!#v [SCOPE.GetRootScope.GetCountry.MakeScope.Var('eafp_var_yechi_gdp_goal').GetValue|k0]#! or above\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_samjeong')] $je_korean_land_problem_complete_cond_tt$\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_sojunghwa')] Not a subject of Qing, or Qing has collapsed, and holds at least #bold Major Power#! rank as an independent country\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_sedo')] In-law government has come to an end\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_devout')] The #bold $ig_confucian_k$#! are in government with approval of at least #v 10#!\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_iyeok')] At least #v 50%#! of the population is Korean in at least one state outside the Korean homeland\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_literacy')] Literacy is at least #v 30%#!\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_confucian')] At least #v 90%#! of the population is Confucian"

# eafp_kor_rework_l_english.yml — added after the worldview bar keys
 je_korean_confu_blossom_cond_header: "Conditions for the #b Path of Enlightenment#!"
 je_korean_confu_yechi_cond_header: "Conditions for the #b Path of Rule by Ritual#!"
 je_korean_confu_blossom_header: "Upon achieving the #b Path of Enlightenment#!:\n$EFFECT$"
 je_korean_confu_yechi_header: "Upon achieving the #b Path of Rule by Ritual#!:\n$EFFECT$"
 eafp_yechi_settled_tt: "Rule by ritual has taken root for #v 60#! months (#v 5#! years)"
```

**중국어 간체**

```yaml
# eafp_kor_rework_l_simp_chinese.yml — 接在现有 je_korean_confu_reason 值的末尾
"(现有正文)...$eafp_modi_catholic_plague_desc$\n\n#bold 礼治之路#!\n$law_autocracy$、$law_scholar_bureaucrats$、$law_state_religion$、$amendment_seowon$中任何一项一经更改，礼治之路即告关闭。\n[SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_conditions')] 满足至少#v 6#!项完成条件（当前#v [SCOPE.GetRootScope.GetCountry.MakeScope.ScriptValue('eafp_yechi_conditions_completed')|0]#!/#v 8#!），已持续#v [SCOPE.GetRootScope.GetCountry.MakeScope.Var('eafp_var_yechi_months').GetValue|0]#!/#v 60#!个月\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_gdp')] [concept_gdp]达到@gdp!#v [SCOPE.GetRootScope.GetCountry.MakeScope.Var('eafp_var_yechi_gdp_goal').GetValue|k0]#!以上\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_samjeong')] $je_korean_land_problem_complete_cond_tt$\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_sojunghwa')] 不是清朝的附庸，或清朝已经崩溃，且作为独立国家至少拥有#bold 强国#!地位\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_sedo')] 势道政治已经终结\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_devout')] #bold $ig_confucian_k$#!在政府中且认可度至少为#v 10#!\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_iyeok')] 朝鲜本土以外至少一个州的朝鲜文化人口达到#v 50%#!以上\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_literacy')] 识字率至少为#v 30%#!\n• [SCOPE.GetRootScope.GetCountry.GetCustom('eafp_yechi_checkbox_confucian')] 至少#v 90%#!的人口信仰儒教"

# eafp_kor_rework_l_simp_chinese.yml — 添加在世界认知进度条键之后
 je_korean_confu_blossom_cond_header: "#b 开化之路#!达成条件"
 je_korean_confu_yechi_cond_header: "#b 礼治之路#!达成条件"
 je_korean_confu_blossom_header: "达成#b 开化之路#!时：\n$EFFECT$"
 je_korean_confu_yechi_header: "达成#b 礼治之路#!时：\n$EFFECT$"
 eafp_yechi_settled_tt: "礼治之定达到#v 60#!个月（#v 5#!年）"
```

구현 시 확인할 점:

- 기존 본문 끝이 `$eafp_modi_catholic_plague_desc$`인지 영어·중국어 파일에서도 확인하고, 그 뒤에 붙인다.
- 개화의 길 헤더 문구는 기존 결말의 동작(세계 인식 1000)을 바꾸지 않는다. header·effect_header 키만 바뀐다.

---

## 4. 법률 설계: `law_eafp_yongha_byeoni` 용하변이(用夏變夷)

### 4.1 이름: 용하변이(用夏變夷)와 검토한 후보

**용하변이로 확정했다.** 아래 표는 검토했던 후보 기록이다.

| 후보 | 출전 | 원문 | 뜻과 어울림 |
|---|---|---|---|
| **용하변이(用夏變夷)** | 『맹자』 등문공 상 | 吾聞用夏變夷者 未聞變於夷者也 | 중화의 문명으로 오랑캐를 바꾼다. 조선 후기 소중화 의식의 핵심 구절이라 **동화 특화 법률과 가장 직접 맞는다** |
| **화민성속(化民成俗)** | 『예기』 학기 | 君子如欲化民成俗 其必由學乎 | 백성을 교화해 풍속을 이룬다. 교육·교화를 통한 개종·동화라는 점이 드러난다. 어감이 온건하다 |
| **일도동속(一道同俗)** | 『예기』 왕제 | 一道德以同俗 | 도덕을 하나로 하여 풍속을 같게 한다. 종교(도덕)와 문화(풍속)를 함께 통일한다는 점에서 두 효과를 모두 담는다 |
| **동문동궤(同文同軌)** | 『중용』 28장 | 車同軌 書同文 行同倫 | 수레 궤도·문자·윤리를 하나로. 제도적 통일 느낌이 강해 문화 동화 쪽에 무게가 실린다 |
| **왕화(王化)** | 『시경』 모시서 | 正始之道 王化之基 | 임금의 덕이 퍼져 교화된다. 가장 짧고 전제정치 하위 법률이라는 점이 잘 드러난다 |
| 소중화(小中華) | 조선 후기 문집·실록의 자칭 | — | 청 대신 문명을 잇는다는 이념. 법률보다는 국가 정체성에 가까워 이름으로는 덜 맞는다 |

용하변이는 동화 특화가 가장 선명하고, 이름 자체가 "중화(유교)로 이적을 바꾼다"는 법률 효과를 설명한다.

### 4.2 정의 초안

```
law_eafp_yongha_byeoni = {
	group = lawgroup_distribution_of_power
	parent = law_autocracy
	icon = (전용 아이콘 또는 autocracy.dds 임시)
	progressiveness = -100
	requires_law_or = { law_monarchy }
	is_visible = {
		OR = {
			has_law = law_type:law_eafp_yongha_byeoni
			has_variable = eafp_var_yechi_law_unlocked
		}
	}
	on_activate = { scripted_effect_parties_disappearence = yes }
	modifier = { ... 아래 표 ... }
	ai_enact_weight_modifier = { 바닐라 neo_absolutism과 동일 방식 }
	ai_impose_chance = { value = 0 }
}
```

### 4.3 모디파이어 초안

| 분류 | 모디파이어 | 값 (초안) | 의도 |
|---|---|---|---|
| 전제정치 기본 | `country_legitimacy_headofstate_add` | 30 | 바닐라 전제정치와 동일 |
| | `country_legitimacy_govt_total_clout_add` | 120 | 동일 |
| | `country_legitimacy_ideological_incoherence_mult` | 0.5 | 동일 |
| | `country_authority_add` | 200 | 전제정치(200) 유지. 신 절대주의(250)보다 낮게 |
| 정치 세력 | `interest_group_ig_devout_pol_str_mult` (유림 IG 정치력) | +0.25 | 관료 대신 유림이 체제의 축 |
| | `country_aristocrats_pol_str_mult` | 0.5 | 전제정치와 동일 |
| **동화·개종** | `state_conversion_mult` | +0.5 | 국교(유교) 개종 가속. 서원 수정안(+0.2)과 합산 |
| | `state_assimilation_mult` | +0.5 | 주 문화 동화 가속. 서원 수정안(+0.2)과 합산 |
| | `country_allow_conversion_second_rate_citizen_bool` / `..._open_prejudice_bool` | yes | 낮은 수용도 집단도 개종 대상에 포함 |
| | `country_allow_assimilation_second_rate_citizen_bool` / `..._open_prejudice_bool` | yes | 낮은 수용도 집단도 동화 대상에 포함 |
| **유학의 왕국 계승** | `state_pop_support_law_freedom_of_conscience_add` / `state_pop_support_law_total_separation_add` | -0.5 | 예치 결말로 저널이 끝나면 「성리학 국가」(`eafp_modi_confucian_state`)가 사라지므로, 같은 값을 법률이 이어받는다 |
| | `state_allow_assimilation_in_homeland_bool` | yes | 간도·만주 등 다른 민족의 본거지에서도 동화. 만주 진출(`je_gando_ambition`, `je_eafp_manchurian_policy`)과 맞물려 강력하다 |

별도의 대가 모디파이어는 두지 않는다. 법률의 부담은 전제정치에서 물려받는 IG 입장(전제정치에 반대하는 IG의 불만)으로만 남는다.

모디파이어 이름과 수용도 bool의 기본 동작은 `documentation/modifiers.log`와 바닐라 `00_discrimination` 관련 파일로 구현 전에 검증한다.

### 4.4 기존 법률 체계와의 연결

| 위치 | 바닐라 처리 | 이 법률의 처리 |
|---|---|---|
| `law_autocracy`의 `is_visible` | `law_neo_absolutism`, `law_bakufu`일 때 숨김 | **재정의하지 않는다.** 새 법률을 쓰는 동안에도 전제정치가 법률 화면에 보이고, 다시 전제정치로 되돌리는 제정도 가능하다. 바닐라 파일과 충돌하지 않는다 |
| `01_economic_system.txt` 명령 경제 `unlocking_laws` | `law_neo_absolutism` 명시 | 새 법률은 명시되지 않으므로 명령 경제 불가. 전통 체제 성격상 그대로 둔다 |
| `00_code_on_actions.txt` 법률 변경 시 봄 혁명 변수 정리 | 유형 명시 | 조선은 해당 변수와 무관하므로 수정하지 않는다 |
| `law_eafp_military_headquarters` | 같은 전제정치 하위 법률 | 충돌 없음. 대상 국가가 다르다 |

---

## 5. 변경 예정 파일

| 파일 | 내용 |
|---|---|
| `common/journal_entries/eafp_korean_journal.txt` | **수정** `je_korean_confu`: 예치 결말 outcome, 결말 헤더, `on_monthly_pulse` 예치 확인 (3.4절) |
| `common/scripted_effects/eafp_korea_effects.txt` | 결말 정리 효과 `eafp_effect_confu_cleanup` (기존 두 outcome의 중복 정리 + 예치 변수 정리) |
| `common/scripted_triggers/eafp_kor_triggers.txt` | 완료 조건 8개 `eafp_yechi_cond_*` (스크립트 값과 체크박스 두 곳에서 사용), 예치 결말 이벤트 AI용 `eafp_yechi_has_iyeok_state` |
| `common/script_values/eafp_kor_values.txt` | 충족 개수 `eafp_yechi_conditions_completed` |
| `common/customizable_localization/eafp_KOR_custom_loc.txt` | 체크박스 `eafp_yechi_checkbox_*` 9개 (조건 8개 + 맨 위 요약 줄) |
| `common/amendments/eafp_amendments_historical.txt` | 서원 수정안 `ai_will_revoke`에 "유학의 왕국 진행 중" 예외 |
| `common/laws/eafp_distribution_of_power.txt` | 새 법률 추가 |
| `common/static_modifiers/eafp_korea_rework_modi.txt` | 예치 결말 이벤트 선택지 모디파이어 2개 (3.7절) |
| `events/eafp_kor_events/eafp_kor_mainline.txt` | 예치 결말 `.172` 이벤트를 `.171` 뒤에 추가 |
| `localization/{korean,english,simp_chinese}/eafp_kor_rework_l_*.yml` | `je_korean_confu_reason` 끝에 예치의 길 단락, 결말 헤더·법률·이벤트·모디파이어·툴팁 문자열 추가 |
| `gfx/interface/icons/law_icons/` | (선택) 법률 아이콘 |

새 상태는 세 가지만 둔다: GDP 목표값, 정착 개월 수, 법률 해금 변수. 정착 개월 수는 막대가 없고 조건이 깨져도 쌓인 값이 남아야 해서 변수가 필요하다. 나머지는 모두 기존 상태(법률, 수정안, 기존 변수·저널, IG 승인도, 문해율, 문화·신자 비율)를 직접 읽는다.

---

## 6. 결정 사항

| 항목 | 결정 |
|---|---|
| 저널 | 새 저널 없이 기존 `je_korean_confu` 「유학의 왕국」에 예치의 길을 더한다 |
| 결말 | 개화의 길(기존, 세계 인식 1000) / 예치의 길(신규) / 무효(기존). 두 길이 경주한다 |
| 법률 이름 | 용하변이(用夏變夷), `law_eafp_yongha_byeoni` (출전: 『맹자』 등문공 상) |
| 활성화 시점 | 게임 시작부터 (유학의 왕국과 같음) |
| 유지 조건 | 군주제·전제정치·과거·유교·서원 유지, 청 이외 국가의 종속국 아님. 어긋나 있는 동안은 정착이 멈추고, 되돌리면 이어서 센다. 길이 닫히지 않으며 이벤트·세계 인식 변화도 없다 |
| 시작·지지 조건 | 두지 않음. 지지는 완료 조건 「유림의 지지」가 맡는다 |
| 버튼 | 새 버튼 없음. 기존 「집중 교화」만 남는다 |
| 완료 조건 | 8개 중 6개: 부국, 삼정 해결, 소중화 계승, 세도정치 종식, 유림의 지지, 이역 동화, 서원 교육 성과, 교화(유교 비율) |
| 완료 방식 | 새 막대 없음. 완료 조건 6개 이상을 갖춘 달이 60개월(5년) 쌓이면 예치 결말. 조건이 깨지면 개월 수가 늘지 않고, 쌓인 값은 유지 |
| 진행 표시 | 유학의 왕국 본문 끝에 덴포 위기식 체크박스 목록. 맨 위 한 줄에 충족 개수(N/8)와 정착 기간(N/60개월) |
| 근대 개혁 저널과의 관계 | 함께 진행 가능. 서로 영향 없음 |
| `law_autocracy` 처리 | 재정의하지 않고 그대로 둔다 |
| 고향 땅 동화 | `state_allow_assimilation_in_homeland_bool = yes` 포함 |
| AI 조선 | AI도 진행한다. 예치 결말 이벤트에서는 이역의 주가 있으면 `.oa`, 없으면 `.ob`를 고르며, 법률에는 바닐라 신 절대주의처럼 `ai_enact_weight_modifier`를 준다. AI가 서원 수정안을 폐지하지 않도록 유학의 왕국이 진행 중인 동안 `ai_will_revoke`를 막는다 |

---

## 7. 작업 순서

1. 법률 `law_eafp_yongha_byeoni` 정의와 현지화 (변수 조건으로 노출 확인)
2. 완료 조건 트리거 `eafp_yechi_cond_*` 8개와 스크립트 값 `eafp_yechi_conditions_completed`
3. 체크박스 custom loc `eafp_yechi_checkbox_*`
4. 결말 정리 효과 `eafp_effect_confu_cleanup`로 기존 두 outcome의 중복 정리 묶기
5. 유학의 왕국 수정 (예치 결말 outcome, 결말 헤더, `on_monthly_pulse` 예치 확인)
6. 서원 수정안 `ai_will_revoke`에 예치의 길 예외 추가
7. 예치 결말 이벤트
8. 현지화 3개 언어 (UTF-8 BOM, CRLF): 기존 유학의 왕국 현지화 파일에 추가
9. 검증
   - 키 중복·누락 현지화 `rg` 확인, 게임 실행 후 `error.log` 확인
   - 1836년 문해율·신자 비율 확인 후 기준값 조정
   - 체크박스가 조건에 맞게 바뀌는지
   - 콘솔로 조건을 채워 정착 기간이 매달 늘고, 조건이 깨지면 멈추며, 60개월에 예치 결말이 나는지
   - 유지 조건이 어긋나면 정착 기간이 멈추고 요약 줄 체크가 풀리는지, 되돌리면 이어서 세는지
   - 세계 인식 1000 도달 시 기존 개화 결말이 그대로 동작하고 예치 변수가 지워지는지

