# 조청전쟁 목표별 타임어택 저널 설계안

## 1. 문서 목적

이 문서는 조청전쟁의 세부 작전 목표마다 독립된 기한형 저널을 만들고, 제한 시간 안에
목표를 달성하면 저장된 조청전쟁의 실제 전쟁 지지가 상승하도록 설계한다.

별도의 작전 점수와 progress bar는 사용하지 않는다. 부모 저널은 전쟁 전체와 종전 결과를
관리하고, 목표 저널은 각 작전의 성공·시간초과·전쟁 지지 변화를 담당한다.

```text
부모 저널: 조청전쟁
        │
        ├── 목표 저널 1: 압록강 너머의 교두보
        │       ├── 성공 → 전쟁 지지 상승 → 목표 저널 2A
        │       └── 시간초과 → 전쟁 지지 하락 → 목표 저널 2B
        │
        ├── 목표 저널 2A/2B
        │       └── 성공·시간초과 → 목표 저널 3
        │
        ├── 목표 저널 3: 직예로 가는 길
        │       └── 성공·시간초과 → 목표 저널 4
        │
        └── 목표 저널 4: 황도의 성문
                └── 타임어택 연쇄 종료
```

## 2. 기존 조청전쟁 구조와의 관계

기존 부모 저널 `je_eafp_joseon_qing_war`의 역할은 유지한다.

- 조선과 청이 전쟁 지도자인 독립전쟁에서만 활성화된다.
- 실제 전쟁이 시작된 뒤에만 나타난다.
- 조청전쟁을 `joseon_qing_war` scope로 저장한다.
- 매주 조선의 실제 전쟁 지지를 `eafp_var_jqw_current_war_support`에 저장한다.
- 저장된 전쟁이 끝난 뒤 조선의 독립 여부로 완료와 실패를 나눈다.
- 승전은 전쟁 지지 `50 이상`, `0 이상 50 미만`, `0 미만`의 세 결말로 나눈다.
- 패전은 전쟁 지지와 무관한 단일 결말을 사용한다.

새 목표 저널은 부모 저널의 종전 판정을 바꾸지 않는다. 목표 성공과 시간초과가 실제 전쟁
지지를 움직여 기존 승전 결말 구간에 영향을 준다.

## 3. 카이저라이히 참고 사례

### 3.1 민감기 의군

민감기 의군은 해안 접근로와 복건·감남을 제한 시간 안에 확보하는 임무를 받는다. 영토와
남경을 확보하면 사기를 얻고, 사기가 낮아지면 전투력과 병력이 붕괴한다.

| 목표 | 기한 | 성공 효과 | 실패 처리 |
| --- | ---: | --- | --- |
| 해안 접근로 확보 | 14일 | 안정도, 장비, 중앙위원회 귀환 | 정치력 손실 후 임무 재시작 |
| 복건 확보 | 60일 | 통제권, 안정도, 장비 | 성공 보상 상실 |
| 감남 확보 | 60일 | 통제권, 안정도, 장비 | 성공 보상 상실 |

조청전쟁에는 지도 위 목표를 독립된 타이머 저널로 보여 주고, 성공과 실패가 실제 전쟁 지지를
바꾸는 방식으로 변용한다.

### 3.2 신강 전쟁

신강 군벌은 하나의 전쟁에서 서로 다른 기한의 공세·방어·내정 임무를 동시에 경험한다.

- 300일 안에 신강 통일
- 200일 동안 디화 방어
- 55일 안에 장배원 문제 처리

조청전쟁에도 공세 실패 뒤 본토 수습 목표를 제공한다. 첫 목표 실패가 전체 시스템 종료로
이어지지 않고 다른 성격의 저널을 활성화한다.

### 3.3 청의 국경 임무

카이저라이히 청의 `Eyes on the Border`는 실패하면 `Fangs on the Border`로 이어져 더 큰
군사 위기를 발생시킨다. 조청전쟁에는 이 연쇄 실패 구조를 차용하여 1단계 성공 시 공세 유지
저널을, 실패 시 본토 수습 저널을 활성화한다.

## 4. 저널 구성

### 4.1 부모 저널

```text
je_eafp_joseon_qing_war
```

부모 저널은 전쟁 scope, 현재 전쟁 지지 표시, 종전 판정만 관리한다. 세부 작전 타이머와
작전 성공 조건은 부모 저널의 `on_weekly_pulse`에 넣지 않는다.

### 4.2 목표 저널

| 단계 | 저널 ID | 기한 | 성공 시 | 시간초과 시 |
| ---: | --- | ---: | ---: | ---: |
| 1 | `je_eafp_jqw_bridgehead` | 182일 | 전쟁 지지 `+10` | 전쟁 지지 `-5` |
| 2A | `je_eafp_jqw_hold_liaodong` | 84일 | 전쟁 지지 `+5` | 전쟁 지지 `-5` |
| 2B | `je_eafp_jqw_recover_front` | 112일 | 전쟁 지지 `+5` | 전쟁 지지 `-10` |
| 3 | `je_eafp_jqw_road_to_zhili` | 224일 | 전쟁 지지 `+10` | 전쟁 지지 `-5` |
| 4 | `je_eafp_jqw_gates_of_beijing` | 280일 | 전쟁 지지 `+15` | 전쟁 지지 `-5` |

한 번에 1개의 목표 저널만 활성화한다. 2A와 2B는 상호 배타적이다.

## 5. 활성화 방식

### 5.1 `add_journal_entry`를 사용하지 않음

부모 저널과 마찬가지로 목표 저널도 `add_journal_entry`로 생성하지 않는다.

각 목표 저널은 다음 조건이 모두 참일 때 자동 활성화된다.

1. 조선 국가임
2. 부모 조청전쟁 저널이 활성 상태임
3. 유효한 조청전쟁이 실제로 진행 중임
4. `eafp_var_jqw_objective_stage`가 해당 저널의 단계와 일치함

```txt
is_shown_when_inactive = {
	c:KOR ?= THIS
	has_journal_entry = je_eafp_joseon_qing_war
	var:eafp_var_jqw_objective_stage = 1
}

possible = {
	c:KOR ?= THIS
	has_journal_entry = je_eafp_joseon_qing_war
	var:eafp_var_jqw_objective_stage = 1
	any_scope_war = {
		eafp_jqw_is_joseon_independence_war_trigger = yes
	}
}
```

목표 저널이 비활성 상태로 미리 보이지 않게 하려면 `is_shown_when_inactive`에도 단계 조건을
넣는다. 단계가 바뀌는 순간 해당 목표만 표시되고 활성화된다.

### 5.2 단계 변수

목표 연쇄에는 하나의 country variable만 사용한다.

| 값 | 의미 |
| ---: | --- |
| `1` | 압록강 너머의 교두보 |
| `2` | 요동의 깃발 |
| `3` | 무너진 전선 수습 |
| `4` | 직예로 가는 길 |
| `5` | 황도의 성문 |
| `6` | 모든 타임어택 목표 종료 |

부모 저널의 `immediate`에서 다음 값을 설정한다.

```txt
set_variable = {
	name = eafp_var_jqw_objective_stage
	value = 1
}
```

각 목표 저널의 `on_complete`와 `on_timeout`은 전쟁 지지를 변경한 뒤 다음 단계 값을
설정한다. 단계 변경과 다음 목표 조건 설정은 같은 effect 안에서 처리한다.

## 6. 목표 저널의 전쟁 scope

부모 저널에 저장된 scope는 목표 저널에 자동으로 공유된다고 가정하지 않는다. 각 목표 저널은
활성화될 때 같은 전쟁을 자체 `joseon_qing_war` scope로 저장한다.

```txt
immediate = {
	random_scope_war = {
		limit = {
			eafp_jqw_is_joseon_independence_war_trigger = yes
		}
		save_scope_as = joseon_qing_war
	}
}
```

이후 해당 목표 저널의 `complete`, `on_complete`, `on_timeout`, `invalid`는 자신이 저장한
전쟁 scope만 사용한다.

전쟁 지지는 반드시 저장된 war scope에서 직접 변경한다.

```txt
scope:joseon_qing_war = {
	add_war_war_support = {
		target = ROOT
		value = 10
	}
}
```

`eafp_var_jqw_current_war_support`를 직접 더하거나 빼지 않는다. 이 변수는 부모 저널이 실제
전쟁 지지를 읽어 표시하는 snapshot이다.

## 7. 공통 목표 저널 생명주기

모든 목표 저널은 다음 구조를 공유한다.

```txt
je_eafp_jqw_example = {
	icon = "gfx/interface/icons/event_icons/event_military.dds"
	group = je_group_crises

	is_shown_when_inactive = {
		# 부모 저널과 단계 조건
	}

	possible = {
		# 부모 저널, 단계, 실제 전쟁 조건
	}

	immediate = {
		# 같은 조청전쟁 scope 저장
		# 필요한 목표 state scope 저장
	}

	complete = {
		exists = scope:joseon_qing_war
		# 작전 성공 조건
	}

	on_complete = {
		# 실제 전쟁 지지 상승
		# 다음 단계 설정
		# 저널 전용 임시 변수 정리
	}

	timeout = 182

	on_timeout = {
		# 전쟁이 아직 진행 중일 때만 실제 전쟁 지지 하락
		# 다음 단계 설정
		# 저널 전용 임시 변수 정리
	}

	invalid = {
		OR = {
			NOT = { has_journal_entry = je_eafp_joseon_qing_war }
			NOT = { exists = scope:joseon_qing_war }
			NOT = { var:eafp_var_jqw_objective_stage = 1 }
		}
	}

	on_invalid = {
		# penalty 없이 저널 전용 임시 변수만 정리
	}

	can_deactivate = no
}
```

`timeout`은 일 단위 고정값을 사용한다. 별도의 남은 주 변수는 만들지 않으며 게임의 기본
저널 타이머 UI가 남은 시간을 표시한다.

## 8. 세부 목표 저널

### 8.1 압록강 너머의 교두보

```text
je_eafp_jqw_bridgehead
```

| 항목 | 내용 |
| --- | --- |
| 단계 | `1` |
| 기한 | 182일 |
| 기본 목표 | 조선 측이 `STATE_SHENGJING`을 통제 |
| 성공 | 조선 전쟁 지지 `+10`, 단계 `2` |
| 시간초과 | 조선 전쟁 지지 `-5`, 단계 `3` |

`STATE_SHENGJING`이 개전 시 청의 소유가 아니면 저널 `immediate`에서 다음 순서로 대체
목표를 저장한다.

1. 청이 소유한 조선 인접 주
2. 청이 소유한 만주 지역의 해안 주
3. 유효한 목표가 없으면 저널을 `invalid` 처리하고 단계 `3`으로 전환

세 번째 경우에는 플레이어가 달성할 수 없는 목표였으므로 전쟁 지지 penalty를 주지 않는다.

### 8.2 요동의 깃발

```text
je_eafp_jqw_hold_liaodong
```

| 항목 | 내용 |
| --- | --- |
| 단계 | `2` |
| 기한 | 84일 |
| 목표 | 교두보를 8주 연속 통제 |
| 성공 | 조선 전쟁 지지 `+5`, 단계 `4` |
| 시간초과 | 조선 전쟁 지지 `-5`, 단계 `4` |

이 저널만 `on_weekly_pulse`를 사용한다.

```text
조선 측이 목표 주 통제 → 유지 횟수 +1
청 측이 목표 주 탈환 → 유지 횟수 0
유지 횟수 8 이상 → complete
```

연속 유지 횟수는 `eafp_var_jqw_liaodong_hold_weeks`에 저장하고 완료·시간초과·invalid에서
항상 제거한다.

### 8.3 무너진 전선 수습

```text
je_eafp_jqw_recover_front
```

| 항목 | 내용 |
| --- | --- |
| 단계 | `3` |
| 기한 | 112일 |
| 목표 | 조선 본토의 적 점령 제거 및 `STATE_PYONGYANG` 회복 |
| 성공 | 조선 전쟁 지지 `+5`, 단계 `4` |
| 시간초과 | 조선 전쟁 지지 `-10`, 단계 `4` |

국가 단위 `enemy_occupation` 값과 평양 controller를 함께 확인한다. 국가 단위 점령 수치가
저널 trigger에서 안정적으로 작동하지 않으면 조선 핵심 state region의 controller를 직접
확인하는 scripted trigger로 대체한다.

### 8.4 직예로 가는 길

```text
je_eafp_jqw_road_to_zhili
```

| 항목 | 내용 |
| --- | --- |
| 단계 | `4` |
| 기한 | 224일 |
| 기본 목표 | 조선 측이 `STATE_ZHILI`를 통제 |
| 성공 | 조선 전쟁 지지 `+10`, 단계 `5` |
| 시간초과 | 조선 전쟁 지지 `-5`, 단계 `5` |

이전 목표가 끝나기 전에 이미 직예를 점령했다면 저널 활성화 직후 `complete`가 참이 되어
성공한다. 빠른 진격을 단계형 구조 때문에 무효화하지 않는다.

`STATE_ZHILI`가 개전 시 청의 소유가 아니면 청 수도와 요동 사이에 있는 청 소유 주를
대체 목표로 저장한다. 북경까지 이미 조선 측이 통제하고 있으면 즉시 성공으로 처리한다.

### 8.5 황도의 성문

```text
je_eafp_jqw_gates_of_beijing
```

| 항목 | 내용 |
| --- | --- |
| 단계 | `5` |
| 기한 | 280일 |
| 기본 목표 | 조선 측이 `STATE_BEIJING`을 통제 |
| 성공 | 조선 전쟁 지지 `+15`, 단계 `6` |
| 시간초과 | 조선 전쟁 지지 `-5`, 단계 `6` |

청이 수도를 옮겨도 원칙적으로 북경을 목표로 한다. 북경이 개전 시 청의 소유가 아니면 해당
저널 `immediate`에서 청의 현재 수도 state를 대체 목표로 저장한다.

단계 `6`에는 대응하는 목표 저널이 없으므로 타임어택 연쇄가 종료된다. 부모 조청전쟁 저널은
전쟁이 끝날 때까지 계속 유지된다.

## 9. 전쟁 지지 변화 총량

| 경로 | 전쟁 지지 순변화 |
| --- | ---: |
| 모든 공세 목표 성공 | `+40` |
| 교두보 성공, 유지 실패, 이후 성공 | `+30` |
| 교두보 실패, 전선 수습 성공, 이후 성공 | `+25` |
| 교두보와 수습 실패, 이후 성공 | `+10` |
| 모든 목표 시간초과 | `-25` |

전쟁 지지가 상한에 도달한 상태에서 얻은 초과 보너스는 저장하지 않는다. 별도 점수나
보너스 예치 변수를 만들지 않는다.

## 10. 부모 저널의 주간 처리

목표 성공과 시간초과는 각 목표 저널이 처리한다. 부모 저널의 `on_weekly_pulse`는 실제
전쟁 지지를 표시 변수에 저장하는 기존 역할만 수행한다.

```txt
if = {
	limit = {
		exists = scope:joseon_qing_war
	}
	set_variable = {
		name = eafp_var_jqw_current_war_support
		value = "scope:joseon_qing_war.has_war_support(root)"
	}
}
```

목표 저널의 `on_complete`나 `on_timeout`으로 전쟁 지지가 바뀌면 부모 저널의 다음 주간
pulse에서 status text가 갱신된다. 즉시 갱신이 필요하면 목표 저널 효과 마지막에 같은
snapshot 저장 effect를 호출하되, 실제 전쟁 지지 변경보다 먼저 실행하면 안 된다.

## 11. 시간초과와 invalid의 구분

### 11.1 시간초과

목표 기한이 끝났고 조청전쟁이 계속 진행 중일 때만 `on_timeout` penalty를 적용한다.

```txt
on_timeout = {
	if = {
		limit = {
			exists = scope:joseon_qing_war
			has_journal_entry = je_eafp_joseon_qing_war
			any_scope_war = {
				eafp_jqw_is_joseon_independence_war_trigger = yes
			}
		}
		scope:joseon_qing_war = {
			add_war_war_support = {
				target = ROOT
				value = -5
			}
		}
		set_variable = {
			name = eafp_var_jqw_objective_stage
			value = 3
		}
	}
}
```

### 11.2 invalid

다음 경우에는 목표를 조용히 제거하고 penalty를 주지 않는다.

- 부모 조청전쟁 저널이 완료·실패·invalid됨
- 저장된 전쟁이 이미 끝남
- 외부 정리 effect로 목표 단계가 바뀜
- 목표 state가 존재하지 않고 대체 목표도 선택할 수 없음

전쟁이 목표 타이머보다 먼저 끝났다는 이유로 이미 확정된 강화 결과의 전쟁 지지를 다시
낮추지 않는다.

### 11.3 같은 날짜의 종전과 시간초과

엔진 처리 순서에 의존하지 않도록 `on_timeout` 내부에서 부모 저널, 저장된 전쟁 scope,
현재 진행 중인 조청전쟁의 존재를 모두 다시 검사한다. 저널의 `invalid` 조건만 믿고 무조건
penalty를 적용하지 않는다.

## 12. 목표 저널 UI

부모 저널은 현재 전쟁 지지와 종전 결말 구간을 계속 표시한다.

각 목표 저널은 다음 항목만 보여 준다.

```text
압록강 너머의 교두보

청군의 동원이 끝나기 전에 요동에 확고한 교두보를 마련해야 한다.

완료 조건
☐ 조선 측이 봉천을 통제

성공
전쟁 지지 +10

시간초과
전쟁 지지 -5
```

- 남은 시간은 저널의 기본 timeout UI로 표시한다.
- 별도의 `status_desc`는 추가하지 않는다.
- 성공 효과는 `event_outcome_completed_effect_desc`로 표시한다.
- 시간초과 효과는 `event_outcome_timeout_effect_desc`로 표시한다.
- 효과 설명에는 실제 `add_war_war_support`와 같은 값이 나타나야 한다.

부모 저널의 progress description은 기존처럼 하나의 text 안에서 다음 세 결말 구간을
체크 박스로 표시한다.

```text
☐ 전쟁 지지 50 이상: 가장 좋은 승리 결말
☑ 전쟁 지지 0 이상 50 미만: 중간 승리 결말
☐ 전쟁 지지 0 미만: 가장 나쁜 승리 결말
```

## 13. 중복 활성화와 중복 지급 방지

- 단계 변수 하나만 현재 목표를 가리킨다.
- 각 목표 저널의 `possible`은 자신의 단계에서만 참이다.
- `on_complete`와 `on_timeout`은 전쟁 지지 변경과 단계 변경을 같은 블록에서 수행한다.
- 완료된 목표 단계로 되돌아가는 effect를 만들지 않는다.
- 목표 저널마다 `can_deactivate = no`를 사용한다.
- 반복 전쟁이 시작될 때 단계 변수를 반드시 `1`로 초기화한다.

완료·실패 flag는 기본 설계에서 사용하지 않는다. 단계 변수와 활성 저널 자체가 현재 상태를
충분히 표현한다. 디버깅 로그나 과거 목표 이력을 UI에 표시해야 할 때만 별도 flag를 추가한다.

## 14. 동맹군과 대체 목표

조선은 전쟁 지도자이므로 조선 측 점령지가 조선 controller로 기록되는지 우선 확인한다.
동맹국 controller로 기록되는 경우에는 다음 scripted trigger를 만든다.

```text
목표 state controller가 조선임
또는
목표 state controller가 저장된 전쟁에서 조선과 같은 편인 참가국임
```

동맹군이 먼저 점령했다는 이유로 목표 저널이 완료 불가능해져서는 안 된다.

대체 목표는 각 목표 저널의 `immediate`에서 해당 저널 scope에 저장한다. 부모 저널의 saved
scope를 목표 저널에서 직접 참조하는 구조는 피한다.

## 15. 정리 처리

부모 저널의 `on_complete`, `on_fail`, `on_invalid`에서 다음 변수를 제거한다.

```text
eafp_var_jqw_objective_stage
eafp_var_jqw_liaodong_hold_weeks
```

목표 저널은 부모 저널의 부재를 `invalid`로 감지해 자동 제거된다. 부모 저널에서
`remove_journal_entry`를 호출하지 않는다.

각 목표 저널의 `on_invalid`에서도 자신이 사용하는 임시 유지 횟수와 보조 변수를 정리한다.

## 16. AI 처리

목표 저널은 AI가 별도 버튼을 누르지 않아도 완료할 수 있어야 한다.

- 적 주 점령
- 점령한 교두보 유지
- 본토의 적 점령 제거
- 적 수도 압박

AI도 플레이어와 동일한 전쟁 지지 보너스와 penalty를 받는다. 조선 AI가 거의 항상 목표를
실패한다면 자동 성공을 주지 말고 목표 저널의 `timeout`만 20~25% 늘린다.

## 17. 구현 파일 계획

| 파일 | 작업 |
| --- | --- |
| `common/journal_entries/eafp_joseon_qing_war.txt` | 부모 조청전쟁 저널의 단계 초기화와 종전 정리 |
| `common/journal_entries/eafp_joseon_qing_war_objectives.txt` | 서로 독립된 목표 저널 5개 정의 |
| `common/scripted_triggers/eafp_kor_triggers.txt` | 단계별 활성화, 목표 점령, 동맹군 통제 trigger |
| `common/scripted_effects/eafp_korea_effects.txt` | 전쟁 지지 변경, 단계 전환, 목표 상태 정리 effect |
| `events/eafp_kor_events/eafp_joseon_qing_war_events.txt` | 종전 사건에서 목표 변수 정리 확인 |
| `localization/english/eafp_joseon_qing_war_l_english.yml` | 목표 저널 제목·설명·효과 |
| `localization/korean/eafp_joseon_qing_war_l_korean.yml` | 동일 key의 한국어 현지화 |
| `localization/simp_chinese/eafp_joseon_qing_war_l_simp_chinese.yml` | 동일 key의 중국어 현지화 |

`common/scripted_progress_bars`에는 새 파일을 만들지 않는다.

## 18. 구현 순서

1. 부모 저널에서 목표 단계 `1` 초기화와 종전 정리를 추가한다.
2. 목표 저널 공통 `possible`, 전쟁 scope 저장, invalid 구조를 만든다.
3. 교두보 저널과 2A·2B 분기를 구현한다.
4. 직예·북경 저널과 대체 목표 선택을 구현한다.
5. 각 저널의 `timeout`, `on_complete`, `on_timeout` 전쟁 지지 효과를 연결한다.
6. 부모 저널 종료 시 모든 목표 저널이 penalty 없이 invalid되는지 확인한다.
7. 한국어·영어·중국어 localization을 추가한다.

## 19. 검증 기준

- 실제 조청전쟁이 시작되면 부모 저널과 1단계 목표 저널이 활성화된다.
- 외교전 단계에서는 부모·목표 저널이 활성화되지 않는다.
- 각 세부 목표가 독립된 저널과 독립된 timeout을 갖는다.
- `add_journal_entry`를 사용하지 않고 `possible`과 단계 변수로 목표 저널이 활성화된다.
- 동시에 둘 이상의 목표 저널이 활성화되지 않는다.
- 1단계 성공은 2A, 시간초과는 2B 저널을 활성화한다.
- 2A와 2B 종료 후에는 모두 3단계 저널로 이어진다.
- 목표 성공과 시간초과는 표시 변수가 아닌 실제 war scope의 전쟁 지지를 변경한다.
- 각 성공·시간초과 효과는 한 번만 적용된다.
- 목표 저널 활성화 전에 이미 달성한 빠른 진격도 즉시 완료된다.
- 목표 기한은 별도 주 수 변수가 아니라 JE 기본 timeout으로 표시된다.
- 종전과 목표 시간초과가 같은 날짜여도 종료된 전쟁에 penalty를 적용하지 않는다.
- 부모 저널 종료 시 활성 목표 저널이 조용히 invalid된다.
- 승전 option은 변경된 실제 전쟁 지지의 `50 이상`, `0~49`, `0 미만` 구간을 사용한다.
- 패전은 전쟁 지지와 무관한 단일 결말을 유지한다.
- 반복 조청전쟁에서 목표 단계와 유지 횟수가 초기화된다.

## 20. 참고 자료

- [Kaiserreich 공식 공개 저장소: Left Kuomintang 결정 파일](https://github.com/Kaiserreich/Kaiserreich-HOI4/blob/master/common/decisions/CHI%20decisions%20%28Left%20Kuomintang%29.txt)
- [Kaiserreich Wiki: MinGan Insurgent Zone/Paths](https://kaiserreich.fandom.com/wiki/MinGan_Insurgent_Zone/Paths)
- [Kaiserreich 공식 공개 저장소: Xinjiang 결정 파일](https://github.com/Kaiserreich/Kaiserreich-HOI4/blob/master/common/decisions/SIK%20decisions%20%28Xinjiang%29.txt)
- [Kaiserreich Wiki: Qing Empire/Paths](https://kaiserreich.fandom.com/wiki/Qing_Empire/Paths)
- Victoria 3 바닐라 `common/journal_entries/journal_entries.md`
- Victoria 3 바닐라 `events/technology_events.txt`: `technology_events.30`
- Victoria 3 바닐라 `events/tech_events/aviation.txt`: `aviation.1`
