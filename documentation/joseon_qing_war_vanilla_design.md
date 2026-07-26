# 조청전쟁 메커니즘 설계안 — 바닐라 패턴 기반

## 1. 설계 목표

이 설계는 조선(`KOR`)과 청(`CHI`)이 실제로 전쟁 상태에 들어갔을 때 조선에 활성화되는
`je_eafp_joseon_qing_war`를 대상으로 한다. 전쟁의 승패는 Victoria 3의 외교전·전쟁·강화
시스템이 결정하고, 저널은 다음 두 가지를 보완한다.

1. 조선이 강화에서 무엇을 얻고 잃었는지 정확히 판정한다.
2. 같은 군사적 결과라도 종전 당시 조선의 실제 전쟁 지지에 따라 전후 국내 정치의 결말을
   다르게 만든다.

저널 자체가 별도의 전쟁 지지도를 만들거나 승패를 대신 판정하지 않는다. 핵심 구조는
`전략적 전쟁 결과 × 조선의 실제 전쟁 지지`다.

## 2. 참고한 바닐라 구현

| 바닐라 파일 | 차용할 패턴 | 조청전쟁에서의 적용 |
| --- | --- | --- |
| `common/journal_entries/00_opium_wars.txt` | 대상 국가를 scope로 보존하고 실제 법·조약·조차지 결과로 완료를 판정 | 단순히 전쟁이 끝났는지가 아니라 조선·청 사이에 강제된 전쟁 목표를 판정 |
| `common/journal_entries/02_paraguay.txt` | 전쟁 결과 변수와 영토 상태를 함께 검사 | 범용 `recently_won_war` 대신 조청전쟁 전용 결과 변수를 사용 |
| `common/journal_entries/00_nursing.txt` | 저널 활성화 시 실제 전쟁을 saved scope로 보존 | 조선과 청이 모두 참가한 전쟁을 `joseon_qing_war`로 저장 |
| `events/japan_events/ep2_ezo_republic.txt` | 전쟁 scope에서 `has_war_support`로 국가별 전쟁 지지를 판정 | 종전 등급과 반복 사건 조건을 조선의 실제 전쟁 지지로 판정 |
| `localization/*/interfaces_l_*.yml` | `War.GetWarSupport(Country)`로 현재 전쟁 지지를 표시 | 저널 status text에 조선의 현재 전쟁 지지를 직접 표시 |
| `common/on_actions/00_code_on_actions.txt` | `on_capitulation`, `on_wargoal_enforced`, `on_war_end`에서 전쟁 결과 기록 | 조선·청 사이에 실제로 강제된 목표와 조선의 항복을 전용 변수로 기록 |

바닐라의 `recently_won_war`와 `recently_lost_war`는 5년 동안 유지되며 다른 전쟁에도 반응한다.
따라서 동시에 다른 전쟁을 치를 수 있는 조선에는 직접적인 승패 판정용으로 적합하지 않다.

## 3. 전체 상태 흐름

```text
조선의 대청 독립 외교전 개시
        │
        ▼
저널 자동 활성화 ── 적국 scope·전용 결과 변수 초기화
        │
        ├── 개전: 조선과 청이 참가한 전쟁 scope 저장
        ├── 상시: status text에 조선의 실제 전쟁 지지 표시
        ├── 간헐: 조건부 전쟁 사건과 선택으로 실제 전쟁 지지·modifier 변화
        └── on_action: 항복과 강제된 전쟁 목표를 전용 변수에 기록
        │
        ▼
조선과 청의 전쟁 종료
        │
        ├── 조선 목표만 강제: 공세적 승리
        ├── 양측 목표 없음: 현상 유지/방어 성공
        ├── 양측 목표 강제: 타협적 종전
        └── 청 목표 강제 또는 조선 항복·종속: 패전
        │
        ▼
전략적 결과 × 종전 당시 전쟁 지지로 전후 사건·보상 등급 결정
```

## 4. 저널 생명주기

### 4.1 활성화

별도의 껍데기 저널이나 `add_journal_entry` 없이 현재 구조처럼 `possible`을 사용한다.

```txt
is_shown_when_inactive = {
	c:KOR ?= THIS
	exists = c:CHI
	any_diplomatic_play = {
		initiator = c:KOR
		target = c:CHI
		is_diplomatic_play_type = dp_independence
	}
}

possible = {
	c:KOR ?= THIS
	exists = c:CHI
	OR = {
		has_war_with = c:CHI
		any_diplomatic_play = {
			initiator = c:KOR
			target = c:CHI
			is_diplomatic_play_type = dp_independence
		}
	}
}
```

`immediate`에서는 다음만 수행한다.

- `c:CHI`를 `qing_enemy`로 저장한다.
- 전쟁 개월 수와 조청전쟁 전용 결과 변수를 초기화한다.
- 이미 전쟁 중이면 조선과 청이 모두 참가한 전쟁을 `joseon_qing_war` scope로 저장하고 개전
  사건을 발생시킨다.
- 외교전 중 활성화됐다면 실제 개전 시 주간 pulse에서 같은 전쟁 scope를 저장하고 개전 사건을
  1회 발생시킨다.

이 구조는 첫 전쟁에 한정되지 않고 새로운 조청전쟁이 벌어질 때마다 다시 사용할 수 있다.

### 4.2 전용 결과 기록

다음 country variable을 사용한다.

| 변수 | 설정 시점 | 의미 |
| --- | --- | --- |
| `eafp_var_jqw_kor_enforced_goal` | `on_wargoal_enforced` | 조선 측 전쟁 목표 하나 이상이 청에 강제됨 |
| `eafp_var_jqw_qing_enforced_goal` | `on_wargoal_enforced` | 청 측 전쟁 목표 하나 이상이 조선에 강제됨 |
| `eafp_var_jqw_kor_capitulated` | `on_capitulation` | 조선이 전쟁 중 항복함 |
| `eafp_var_jqw_result` | 종전 직전 | 최종 전략적 결과 코드 |

`on_wargoal_enforced`는 바닐라와 동일하게 `ROOT`가 목표를 강제한 국가이고
`scope:target`이 목표를 강제당한 국가다. 조선이 해당 저널을 보유하고 있으며 두 scope가
조선과 청의 조합일 때만 전용 변수를 설정한다.

`on_capitulation`에서는 `ROOT = KOR`, 조선이 저널을 보유, 청과 전쟁 중인 경우만 항복 변수를
설정한다. 이 방식은 조선이 같은 시기에 치른 제3국과의 전쟁 결과가 섞이는 문제를 막는다.

### 4.3 종전 판정

전쟁 종료 뒤 결과는 다음 우선순위로 계산한다.

| 우선순위 | 조건 | 결과 코드 | 의미 |
| ---: | --- | ---: | --- |
| 1 | 조선이 청의 종속국이 됨, 조선 항복, 또는 청 목표만 강제됨 | `0` | 패전 |
| 2 | 조선과 청 양측의 목표가 모두 강제됨 | `1` | 타협적 종전 |
| 3 | 조선 목표만 강제됨 | `3` | 공세적 승리 |
| 4 | 어느 쪽 목표도 강제되지 않았고 조선이 청의 종속국이 아님 | `2` | 현상 유지/방어 성공 |

현재 구현처럼 `NOT = { has_war_with = c:CHI }`와 `NOT = { is_subject_of = c:CHI }`만으로
승전을 판정하면 백지평화도 공세적 승리로 처리된다. 위의 전용 결과 기록이 이를 해결한다.

저널의 `fail`은 전쟁이 끝난 뒤 종속·항복·청의 일방적 목표 강제를 직접 검사하고,
`on_fail`에서 결과 코드 `0`을 설정한다. `complete`는 전쟁이 끝났고 이 패전 조건이 아닌 경우만
참이 되며, `on_complete`에서 양측 결과 변수를 검사해 코드 `1`, `2`, `3`을 설정한다. 즉 결과
코드가 완료·실패 조건을 결정하는 순환 구조를 만들지 않는다.

청이 소멸했지만 조선이 생존하고 종속되지 않은 경우는 청 질서의 붕괴에 따른 방어 성공(`2`)으로
처리한다. 조선이 소멸하거나 저널 owner가 유효하지 않은 경우만 `invalid`에서 정리한다.

## 5. 핵심 수치: 조선의 실제 전쟁 지지

별도 progress bar나 평가 변수는 사용하지 않는다. 개전 시 저장한 `joseon_qing_war` scope에서
조선의 실제 `war support`를 직접 읽는다.

```txt
scope:joseon_qing_war = {
	has_war_support = {
		target = ROOT
		value >= 50
	}
}
```

저널 status text도 같은 scope를 사용한다.

```text
[SCOPE.sWar('joseon_qing_war').GetWarSupport(
	SCOPE.GetRootScope.GetCountry.Self
)|0+=]
```

종전 등급은 다음 세 구간으로 고정한다.

| 조선 전쟁 지지 | 결과 등급 | 승전 시 의미 |
| ---: | ---: | --- |
| `50 이상` | `3` | 가장 좋은 승리 결말 |
| `0 이상 50 미만` | `2` | 중간 승리 결말 |
| `0 미만` | `1` | 가장 나쁜 승리 결말 |

반복 사건의 기존 결속 증감은 같은 수치의 `add_war_war_support`로 전환한다. 따라서 사건 선택은
별도 평가 막대가 아니라 실제 항복 압력과 종전 결말에 동시에 영향을 준다.

## 6. 월간 사건 디렉터

`on_monthly_pulse.random_events`를 사용하되 바닐라 Opium Wars처럼 무발생 가중치를 높게 둔다.

```txt
random_events = {
	85 = 0
	5 = eafp_joseon_qing_war_events.10
	4 = eafp_joseon_qing_war_events.11
	3 = eafp_joseon_qing_war_events.12
	2 = eafp_joseon_qing_war_events.13
	4 = eafp_joseon_qing_war_events.14
}
```

모든 후보가 유효할 때 월간 사건 확률은 약 17.5%다. 실제로는 계절·점령·산업·낮은 전쟁 지지
조건과 개별 cooldown이 적용되므로 1년 전쟁에서 약 1~2개, 2년 전쟁에서 약 3~4개 사건을
경험하는 것을 목표로 한다.

### 6.1 사건 구성

| ID | 사건 | 핵심 trigger | 선택 구조 |
| --- | --- | --- | --- |
| `.10` | 의주의 보급로 | 전쟁 2개월 이상, 북부 주 보유 | 국고로 보급 `+4` / 지방 징발 `-3` / 운송망 정비 `+2`와 후속 시너지 |
| `.11` | 동장군 | 10~2월, 전쟁 4개월 이상 | 방한 물자 `+5` / 현지 징발 `-4` / 공세 지연 `+2`와 단기 공격 불이익 |
| `.12` | 포탄 속의 모래 | 군수 산업 보유, 전쟁 6개월 또는 전쟁 지지 60 미만 | 엄벌 `+3` / 은폐 `-6`와 후속 위험 / 조달 개편 `+6`와 큰 비용 |
| `.13` | 패전의 책임 | 전쟁 지지 40 미만, 점령 10% 초과, 또는 높은 전쟁 피로 | 순절 허용 `0` / 생존 문책 `+4` / 은폐 `-5` |
| `.14` | 북방의 피난 행렬 | 북부 황폐화 또는 적 점령 | 국가 구호 `+5` / 군수 우선 `-4` / 지방 분산 수용 `+2`와 관료제 비용 |

현재 `.14`의 일반적인 대화재는 `북방의 피난 행렬`로 교체하는 편이 전쟁 상태와 직접 연결되고
발생 조건도 명확하다. 기존 사건을 유지한다면 적 점령·군수 비리 은폐·군수 산업이 있는 주에만
발생하도록 제한한다.

### 6.2 사건 연결 규칙

- `.10`에서 운송망을 정비하면 `.11`의 방한 물자 비용을 절반으로 줄인다.
- `.12`에서 비리를 은폐하면 `.14`의 군수창 화재 설명과 불이익을 강화한다.
- `.13`에서 패전을 은폐하면 종전 등급이 2 이하일 때 추가 급진파를 만든다.
- 모든 연결 변수는 종전 또는 `on_invalid`에서 제거한다.
- 사건별 cooldown은 12~24개월로 두어 같은 전쟁 중 반복을 드물게 한다.

## 7. 전후 결말

결말은 전략적 결과를 먼저 정하고 종전 당시 전쟁 지지 구간으로 강도를 조절한다.

### 7.1 결과표

| 전략적 결과 | 높은 지지(`50+`) | 중간 지지(`0~49`) | 낮은 지지(`0 미만`) |
| --- | --- | --- | --- |
| 공세적 승리 | 대승 | 값비싼 승리 | 상처뿐인 승리 |
| 방어 성공 | 독립 수호 | 피로한 현상 유지 | 휴전 뒤의 혼란 |
| 타협적 종전 | 유리한 타협 | 불만스러운 강화 | 사실상의 굴욕 |
| 패전 | 질서 있는 수습 | 굴욕적 패전 | 국정 붕괴 |

### 7.2 효과 원칙

최종 positive modifier는 `eafp_modifier_joseon_qing_war_victory_unity`, negative modifier는
`eafp_modifier_joseon_qing_war_defeat_humiliation` 하나씩만 유지한다.

- 공세적 승리: 위신, 충성파, positive modifier 3~6년.
- 방어 성공: 소규모 충성파, positive modifier 2~4년. 공세적 승리보다 항상 약하다.
- 타협적 종전: 높은 지지면 짧은 positive modifier, 중간 지지면 중립, 낮은 지지면
  짧은 negative modifier를 준다.
- 패전: 급진파와 negative modifier 3~6년. 높은 지지는 피해를 줄이지만 패전을 보상으로
  바꾸지는 않는다.
- 전쟁 지지가 0 미만이면 승리 결과에서도 소규모 급진파를 남겨 `상처뿐인 승리`를 표현한다.

modifier의 수치 자체를 등급별로 복제하지 않고 기간과 즉시 충성파·급진파 규모만 바꾼다.

## 8. AI 원칙

- 파산 중이거나 금 보유고가 음수면 비용이 큰 선택 가중치를 크게 낮춘다.
- 적 점령이 20%를 넘으면 단기 군사 효과가 있는 선택을 선호한다.
- 급진파가 20%를 넘으면 지방 징발·민간 방치·은폐 선택을 기피한다.
- 전쟁 지지가 35 미만이면 개혁·구호 선택을 선호하되, 감당할 재정이 없으면 값싼 차선책을 고른다.
- AI 선택은 전쟁 지지만 최대화하지 않고 국가 파산과 군사적 패배를 함께 피하도록 한다.

## 9. 구현 파일 계획

| 파일 | 작업 |
| --- | --- |
| `common/journal_entries/eafp_joseon_qing_war.txt` | 전쟁 scope 저장, status text, 종전 결과와 전쟁 지지 등급 판정 |
| `common/on_actions/00_code_on_actions_definition.txt` | `on_capitulation` 연결 추가; 기존 `on_wargoal_enforced` 연결 활용 |
| `common/on_actions/eafp_code_on_actions.txt` | 조청전쟁 전용 강제 목표·항복 기록 |
| `events/eafp_kor_events/eafp_joseon_qing_war_events.txt` | 반복 사건이 실제 전쟁 지지를 변경하도록 개편 |
| `common/static_modifiers/eafp_joseon_qing_war_modifiers.txt` | 진행 구간 modifier 제거, 사건·종전 modifier만 유지 |
| `localization/korean/eafp_joseon_qing_war_l_korean.yml` | 전쟁 지지 status·결과·사건 설명 갱신 |
| `localization/simp_chinese/eafp_joseon_qing_war_l_simp_chinese.yml` | 동일 key의 중국어 현지화 갱신 |

## 10. 구현 순서

1. 전용 `on_wargoal_enforced`·`on_capitulation` 변수와 종전 판정을 먼저 구현한다.
2. 개전 시 조청전쟁 scope를 저장하고 status text에서 전쟁 지지를 표시한다.
3. 기존 사건의 결속 증감을 실제 전쟁 지지 증감으로 전환한다.
4. `.14`를 피난민 사건으로 교체하거나 현재 화재 사건의 조건을 강화한다.
5. 결과 코드와 전쟁 지지 구간을 결말 사건의 설명·즉시 효과·modifier 기간에 연결한다.
6. 모든 임시 변수와 modifier가 `on_complete`, `on_fail`, `on_invalid`에서 정리되는지 검증한다.

## 11. 검증 기준

- 조선이 다른 국가와 동시에 전쟁해도 조청전쟁 결과 변수가 오염되지 않는다.
- 백지평화, 조선 목표 강제, 청 목표 강제, 양측 목표 강제, 조선 종속의 다섯 경우가 구분된다.
- 1년 전쟁에서 사건이 평균 1~2개 정도 발생하고 동일 사건이 반복되지 않는다.
- 저널 status text가 저장된 조청전쟁의 조선 전쟁 지지와 같은 값을 표시한다.
- 종전 시 `50 이상`, `0~49`, `0 미만`이 각각 결과 등급 `3`, `2`, `1`로 이어진다.
- 종전 후 조청전쟁 전용 변수, 사건 연결 변수와 임시 modifier가 남지 않는다.
- 전쟁 지지가 높아도 패전이 승전 보상으로 바뀌지 않고, 지지가 낮은 승전에는 국내 후유증이 남는다.

## 12. 권장 MVP

첫 구현에서는 새 GUI, scripted button, 청 전용 저널을 추가하지 않는다. 조선 저널 하나,
저장된 전쟁 scope 하나, 기존 사건 5개, 전용 종전 판정만으로 완결한다. 청 측 플레이 경험은 이후
별도의 `청 조정의 대응` 사건 풀로 확장할 수 있지만, 핵심 결과 판정과 전쟁 지지 연동이 안정된 뒤
추가하는 것이 좋다.
