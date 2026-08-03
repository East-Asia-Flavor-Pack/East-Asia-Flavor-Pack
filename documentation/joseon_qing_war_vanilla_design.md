# 조청전쟁 메커니즘 설계안 — 바닐라 패턴 기반

## 1. 설계 목표

이 설계는 조선(`KOR`)과 청(`CHI`)이 양측 전쟁 지도자이며 조선 독립이 전쟁 목표인 전쟁에서 활성화되는
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
| `common/journal_entries/00_nursing.txt` | 저널 활성화 시 실제 전쟁을 saved scope로 보존 | 양국이 전쟁 지도자이고 조선 독립 목표가 있는 전쟁을 `joseon_qing_war`로 저장 |
| `events/japan_events/ep2_ezo_republic.txt` | 전쟁 scope에서 `has_war_support`로 국가별 전쟁 지지를 판정 | 주간 pulse에서 조선의 실제 전쟁 지지를 변수로 저장 |
| `localization/*/agitators_4_l_*.yml` | country variable을 localization에서 수치로 표시 | 저널 status text에 저장된 전쟁 지지 변수를 표시 |

바닐라의 `recently_won_war`와 `recently_lost_war`는 5년 동안 유지되며 다른 전쟁에도 반응한다.
따라서 동시에 다른 전쟁을 치를 수 있는 조선에는 직접적인 승패 판정용으로 적합하지 않다.

## 3. 전체 상태 흐름

```text
조선과 청 사이의 전쟁 발발
        │
        ▼
저널 자동 활성화 ── 조청전쟁 scope 저장
        │
        ├── 개전: 양국이 전쟁 지도자이고 조선 독립 목표가 있는 전쟁 scope 저장
        ├── 매주: 실제 전쟁 지지를 country variable에 저장하고 status text에 표시
        └── 간헐: 조건부 전쟁 사건과 선택으로 실제 전쟁 지지·modifier 변화
        │
        ▼
조선과 청의 전쟁 종료
        │
        ├── 조선이 청으로부터 독립: 완료
        └── 조선이 청의 종속국: 실패
        │
        ▼
독립 여부 × 종전 당시 전쟁 지지로 전후 사건·보상 결정
```

## 4. 저널 생명주기

### 4.1 활성화

별도의 껍데기 저널이나 `add_journal_entry` 없이 현재 구조처럼 `possible`을 사용한다.

```txt
is_shown_when_inactive = {
	c:KOR ?= THIS
	exists = c:CHI
	is_subject_of = c:CHI
}

possible = {
	c:KOR ?= THIS
	exists = c:CHI
	any_scope_war = {
		eafp_jqw_is_joseon_independence_war_trigger = yes
	}
}
```

전용 trigger는 조선과 청이 모두 전쟁 지도자인지, 현재 전쟁의 목표 보유국과 대상국이 각각
조선과 청인지, 조선이 청을 대상으로 `independence` 전쟁 목표를 보유하는지를 확인한다.
외교전 유형 자체는 제한하지 않는다.

`immediate`에서는 다음만 수행한다.

- `c:CHI`를 `qing_enemy`로 저장한다.
- 현재 전쟁 지지 snapshot과 조청전쟁 임시 변수를 초기화한다.
- 양국이 전쟁 지도자이며 조선 독립 목표가 있는 전쟁을 `joseon_qing_war` scope로 저장하고 개전 사건을
  발생시킨다.
- 이후 주간 pulse에서 조선의 현재 전쟁 지지를
  `eafp_var_jqw_current_war_support`에 갱신한다.

이 구조는 첫 전쟁에 한정되지 않고 새로운 조청전쟁이 벌어질 때마다 다시 사용할 수 있다.

### 4.2 저장된 전쟁 scope

개전 시 양국이 전쟁 지도자이며 조선이 청을 대상으로 독립 전쟁 목표를 가진 전쟁을
`joseon_qing_war`로 저장한다. 전쟁이 진행되는
동안에는 scope가 존재하며, 해당 전쟁이 끝나면 scope가 더 이상 유효하지 않게 된다. 저널은
`NOT = { exists = scope:joseon_qing_war }`를 공통 종전 조건으로 사용한다.

### 4.3 종전 판정

저장된 전쟁 scope가 끝난 뒤 결과는 조선과 청의 종속 관계만으로 판정한다.

| 조건 | 판정 |
| --- | --- |
| 청이 소멸했거나 조선이 청의 종속국이 아님 | 완료 |
| 청이 존재하며 조선이 청의 종속국임 | 실패 |

전쟁 목표 관철이나 항복 여부를 별도로 기록하지 않으므로 백지평화라도 조선이 독립을 유지하면
완료되며, 조선이 청의 종속국으로 남거나 다시 종속되면 실패한다.

## 5. 핵심 수치: 조선의 실제 전쟁 지지

별도 progress bar는 사용하지 않는다. 개전 시 저장한 `joseon_qing_war` scope에서 매주
조선의 실제 `war support`를 읽어 `eafp_var_jqw_current_war_support`에 저장한다. 저널 표시와
종전 분기는 모두 이 변수를 읽는다.

```txt
set_variable = {
	name = eafp_var_jqw_current_war_support
	value = "scope:joseon_qing_war.has_war_support(root)"
}
```

저널 status text도 같은 변수를 사용한다.

```text
[SCOPE.GetRootScope.GetCountry.MakeScope.Var(
	'eafp_var_jqw_current_war_support'
).GetValue|0+=]
```

종전 등급은 다음 세 구간으로 고정한다.

| 조선 전쟁 지지 | 결말 구간 | 승전 시 의미 |
| ---: | --- | --- |
| `50 이상` | 상 | 가장 좋은 승리 결말 |
| `0 이상 50 미만` | 중 | 중간 승리 결말 |
| `0 미만` | 하 | 가장 나쁜 승리 결말 |

## 6. 전후 결말

결말은 전략적 결과를 먼저 정한다. 승전은 종전 당시 전쟁 지지 구간으로 강도를
조절하지만, 패전은 전쟁 지지와 무관한 단일 결말과 고정 효과를 사용한다.

### 6.1 결과표

| 전략적 결과 | 높은 지지(`50+`) | 중간 지지(`0~49`) | 낮은 지지(`0 미만`) |
| --- | --- | --- | --- |
| 공세적 승리 | 대승 | 값비싼 승리 | 상처뿐인 승리 |
| 방어 성공 | 독립 수호 | 피로한 현상 유지 | 휴전 뒤의 혼란 |
| 타협적 종전 | 유리한 타협 | 불만스러운 강화 | 사실상의 굴욕 |
| 패전 | 질서 있는 수습 | 굴욕적 패전 | 국정 붕괴 |

### 6.2 효과 원칙

승전 modifier는 전쟁 지지 구간에 맞춰 `eafp_modifier_joseon_qing_war_great_victory`,
`eafp_modifier_joseon_qing_war_costly_victory`,
`eafp_modifier_joseon_qing_war_pyrrhic_victory`로 나누며, 패전에는
`eafp_modifier_joseon_qing_war_defeat`를 사용한다.

- 공세적 승리: 위신, 충성파, positive modifier 3~6년.
- 방어 성공: 소규모 충성파, positive modifier 2~4년. 공세적 승리보다 항상 약하다.
- 타협적 종전: 높은 지지면 짧은 positive modifier, 중간 지지면 중립, 낮은 지지면
  짧은 negative modifier를 준다.
- 패전: 급진파와 negative modifier 3~6년. 높은 지지는 피해를 줄이지만 패전을 보상으로
  바꾸지는 않는다.
- 전쟁 지지가 0 미만이면 승리 결과에서도 소규모 급진파를 남겨 `상처뿐인 승리`를 표현한다.

modifier의 정치운동·위신·정통성 효과와 지속 기간을 각 결과의 강도에 맞게 차등화한다.

## 7. AI 원칙

- 파산 중이거나 금 보유고가 음수면 비용이 큰 선택 가중치를 크게 낮춘다.
- 적 점령이 20%를 넘으면 단기 군사 효과가 있는 선택을 선호한다.
- 급진파가 20%를 넘으면 지방 징발·민간 방치·은폐 선택을 기피한다.
- 전쟁 지지가 35 미만이면 개혁·구호 선택을 선호하되, 감당할 재정이 없으면 값싼 차선책을 고른다.
- AI 선택은 전쟁 지지만 최대화하지 않고 국가 파산과 군사적 패배를 함께 피하도록 한다.

## 8. 구현 파일 계획

| 파일 | 작업 |
| --- | --- |
| `common/journal_entries/eafp_joseon_qing_war.txt` | 전쟁 scope 저장, 주간 전쟁 지지 변수 갱신과 status text |
| `events/eafp_kor_events/eafp_joseon_qing_war_events.txt` | 개전·승전·패전 사건과 종전 효과 |
| `common/static_modifiers/eafp_joseon_qing_war_modifiers.txt` | 종전 및 이전 저장 호환용 modifier 유지 |
| `localization/korean/eafp_joseon_qing_war_l_korean.yml` | 전쟁 지지 status와 결과 설명 갱신 |
| `localization/simp_chinese/eafp_joseon_qing_war_l_simp_chinese.yml` | 동일 key의 중국어 현지화 갱신 |

## 9. 구현 순서

1. 양국이 전쟁 지도자이며 조선 독립 목표가 있는 전쟁만 조청전쟁 scope로 저장하고 주간 pulse에서 전쟁 지지 변수를 갱신·표시한다.
2. 저장된 전쟁 scope의 종료와 조청 종속 관계로 완료·실패를 판정한다.
3. 결과와 전쟁 지지 구간을 결말 사건의 설명·즉시 효과·modifier 기간에 연결한다.
4. 현재 전쟁 지지 변수가 `on_complete`, `on_fail`, `on_invalid`에서 정리되는지 검증한다.

## 10. 검증 기준

- 조선이 다른 국가와 동시에 전쟁해도 저장된 조청전쟁 scope의 종료만 판정한다.
- 종전 뒤 조선이 청으로부터 독립이면 완료되고 청의 종속국이면 실패한다.
- 저널의 주간 전쟁 지지 변수가 저장된 조청전쟁의 실제 값과 일치하고 status text에 표시된다.
- 종전 시 `50 이상`, `0~49`, `0 미만`이 각각 결과 등급 `3`, `2`, `1`로 이어진다.
- 종전 후 현재 전쟁 지지 변수가 남지 않는다.
- 전쟁 지지가 높아도 패전이 승전 보상으로 바뀌지 않고, 지지가 낮은 승전에는 국내 후유증이 남는다.

## 11. 권장 MVP

첫 구현에서는 새 GUI, scripted button, 청 전용 저널을 추가하지 않는다. 조선 저널 하나,
저장된 전쟁 scope 하나와 전용 종전 판정만으로 완결한다. 청 측 플레이 경험은 이후
별도의 `청 조정의 대응` 사건 풀로 확장할 수 있지만, 핵심 결과 판정과 전쟁 지지 연동이 안정된 뒤
추가하는 것이 좋다.
