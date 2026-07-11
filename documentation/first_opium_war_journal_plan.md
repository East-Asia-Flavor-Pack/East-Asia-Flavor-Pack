# 1차 아편전쟁 선형 구현 계획

## 목표

기존 분기형 1차 아편전쟁 계획은 전부 폐기한다. 새 구현은 하나의 저널과 짧은 선형 이벤트 체인으로 구성한다.

핵심 흐름:

```txt
first_opium_war_1
  -> first_opium_war_2
  -> first_opium_war_3
  -> first_opium_war_4
  -> first_opium_war_5
  -> first_opium_war_9
      -> 엄금론: first_opium_war_90 -> 광동 단속 사건 체인 -> 영국의 최후통첩 또는 굴욕적 배상조약
      -> 이금론: first_opium_war_100 -> 이금론 저널 -> first_opium_war_101 또는 first_opium_war_102
```

실제 Victoria 3 이벤트 ID는 기존 namespace 규칙에 맞춰 선형 본체는 `first_opium_war.1`, `first_opium_war.2`, `first_opium_war.3`, `first_opium_war.4`, `first_opium_war.5`, `first_opium_war.9`, `first_opium_war.90`부터 `.99`, `first_opium_war.100`, `first_opium_war.101`, `first_opium_war.102`, 엄금론 보조 분기 이벤트 `first_opium_war.110`부터 `.113`을 사용한다. 단, 아편 중독 저널의 월간 반복 이벤트로 쓰이는 `first_opium_war.6`, `.7`, `.8`은 보조 이벤트로 유지하고, 엄금론 사건 체인 또는 `이금론` 부칙 폐지 시 재사용하는 기존 `영국의 최후통첩` 이벤트 `first_opium_war.12`도 유지한다. 문서에서 `first_opium_war_1`처럼 쓰는 이름은 읽기용 별칭이다.

## 기본 원칙

- 플레이어 선택으로 큰 분기를 만들지 않는다.
- `first_opium_war.1`부터 `.5`까지는 다음 이벤트 하나만 호출한다.
- `first_opium_war.9`에서만 엄금론과 이금론 두 선택지로 갈라진다.
- 엄금론 선택은 즉시 전쟁을 만들지 않고, `first_opium_war.90`에서 흠차대신 임명과 현지 관료 유예 중 하나를 고른 뒤 광동 단속 사건 체인으로 들어간다.
- `찰스 엘리엇의 아편 국유화`에서 함정임을 간파하면 곧바로 배상 협상으로 가지 않고, 영국 정부 배상 책임을 분리하려는 보조 체인 `first_opium_war.110-.111`을 거친다.
- 현지 관료 유예를 선택하면 곧바로 토머스 쿠츠 호 사건으로 가지 않고, 현지 단속의 지연과 결서 제출 문제를 다루는 보조 체인 `first_opium_war.112-.113`을 거친다.
- 이금론 루트는 `first_opium_war.100` 후속 이벤트와 `이금론` 저널을 통해 처리한다.
- `first_opium_war.6`, `.7`, `.8`은 선형 본체에서 호출하지 않고, `이금론` 저널의 `on_monthly_pulse`에서만 아편 중독 반복 이벤트로 사용한다.
- `first_opium_war.12`는 새 선형 본체에 끼워 넣지 않고, 엄금론 사건 체인의 전쟁 합류점 또는 `이금론` 부칙 폐지 시 기존 `영국의 최후통첩` 이벤트로 재사용한다.
- AI와 플레이어 모두 같은 역사적 순서를 따른다.
- 전쟁 발발 외 결말은 `first_opium_war_9`에서 이금론을 선택한 뒤, 후속 이벤트와 `이금론` 저널을 성공시켰을 때만 얻을 수 있다.
- 국내 아편 재배 보조 저널은 제거하지 않고, 이름과 진입 맥락을 `이금론` 저널로 바꿔 그대로 재사용한다.
- `이금론` 저널이 시작되면 `광동체제` 법률에 `이금론` 부칙을 붙여, 합법화의 재정 이익과 행정/정통성 비용을 법률 효과로 표현한다.
- scripted progress bar는 유지할지 재검토하되, 선형 체인에서는 필수 요소가 아니다.

## 저널 구조

### `je_qing_opium_obsession`

역할:

- 청나라에 시작부터 부여되는 1차 아편전쟁 전조 저널.
- 시작 즉시 `first_opium_war.1`을 호출한다.
- 저널은 이벤트 체인이 끝나거나 전쟁 diplomatic play가 생성되면 완료된다.

초안:

```txt
je_qing_opium_obsession = {
    icon = "gfx/interface/icons/event_icons/event_military.dds"
    group = je_group_qing

    immediate = {
        trigger_event = { id = first_opium_war.1 popup = yes }
    }

    complete = {
        OR = {
            has_variable = opium_wars_target
            has_variable = opium_wars_gave_in
            has_variable = opium_wars_won
            has_variable = lost_opium_wars
            has_modifier = opium_wars_lost
        }
    }

    invalid = {
        OR = {
            NOT = { exists = c:CHI }
            NOT = { THIS = c:CHI }
            NOT = { exists = c:GBR }
        }
    }

    weight = 10000
    should_be_pinned_by_default_uninvolved_or_context = yes
}
```

## 이벤트 체인

```mermaid
flowchart TD
    JE["je_qing_opium_obsession"] --> E1["first_opium_war_1: 아편 위기"]
    E1 --> E2["first_opium_war_2: 이금론 상소"]
    E2 --> E3["first_opium_war_3: 엄금론 반박"]
    E3 --> E4["first_opium_war_4: 엄금론 확정"]
    E4 --> E5["first_opium_war_5: 광동 파견"]
    E5 --> E9["first_opium_war_9: 최종 정책 선택"]
    E9 -- "엄금론" --> STRICT["엄금론 선택"]
    E9 -- "이금론" --> LEGAL["이금론 선택"]
    STRICT --> E90["first_opium_war_90: 엄금 실행 방식"]
    E90 -- "흠차대신 임명" --> COMM["흠차대신 임명"]
    E90 -- "현지 관료 유예" --> LOCAL["현지 관료 유예"]
    COMM --> E91["first_opium_war_91: 13행 봉쇄"]
    LOCAL --> E96["first_opium_war_96: 현지 단속 유예"]
    E91 --> E92["first_opium_war_92: 엘리엇의 아편 국유화"]
    E92 -- "아편 받기" --> E93["first_opium_war_93: 호문소연"]
    E92 -- "함정임을 간파" --> E110["first_opium_war_110: 배상 책임 분리"]
    E110 -- "서면 책임 분리 요구" --> E111["first_opium_war_111: 무배상 처분안"]
    E110 -- "논쟁 중단 후 몰수" --> E93
    E111 -- "최소 배상 봉합" --> E98["first_opium_war_98: 배상 협상"]
    E111 -- "전면 거부" --> ULT2["first_opium_war_12: 영국의 최후통첩"]
    E93 --> E94["first_opium_war_94: 임유희 사건"]
    E96 --> E112["first_opium_war_112: 현지 단속 지연"]
    E112 -- "결서 제출 요구" --> E113["first_opium_war_113: 결서 제출 문제"]
    E112 -- "현지 재량 확대" --> E97["first_opium_war_97: 토머스 쿠츠 호"]
    E113 -- "결서 선박 수용" --> E97
    E113 -- "선단 전체 압박" --> ULT2
    E94 -- "공급 완전 차단" --> ULT2
    E94 -- "제한 대응" --> E97
    E97 -- "배신 이용" --> E98
    E97 -- "영국 선단 전체 압박" --> ULT2
    E98 -- "배상과 제한 통상 수용" --> TREATY["first_opium_war_99: 굴욕적 배상조약"]
    E98 -- "거부" --> ULT2
    TREATY --> GIVEIN["opium_wars_gave_in"]
    ULT2 --> DP["dp_first_opium_war"]
    LEGAL --> E100["first_opium_war_100: 이금론 시행 조건"]
    E100 --> LJE["이금론 저널"]
    LJE -- "성공 조건 달성" --> E101["first_opium_war_101: 이금론 성공"]
    LJE -- "제한 시간 실패" --> E102["first_opium_war_102: 이금론 실패"]
    LJE -- "부칙 폐지" --> ULT["first_opium_war_12: 영국의 최후통첩"]
    E101 --> GIVEIN
    E102 --> ULT
    ULT --> DP
```

### `first_opium_war_1`

실제 ID: `first_opium_war.1`

역할:

- 청나라의 아편 위기가 더 이상 방치할 수 없는 상태임을 알린다.
- `opium_wars_start_var`가 이미 설정되어 바닐라 아편전쟁 시작 이벤트가 뜨지 않는다는 전제를 둔다.

효과:

- 필요한 초기 변수만 설정한다.
- 다음 이벤트 `first_opium_war.2`를 예약한다.

```txt
trigger_event = { id = first_opium_war.2 days = { 30 60 } }
```

### `first_opium_war_2`

실제 ID: `first_opium_war.2`

역할:

- 허내제의 이금론을 보여준다.
- 기존 복잡한 합법화 분기로 넘어가지 않고, 조정 논쟁의 한 단계로만 사용한다.

효과:

- 위기 압력 또는 논쟁 분위기를 약간 증가시킨다.
- 다음 이벤트 `first_opium_war.3`을 예약한다.

```txt
trigger_event = { id = first_opium_war.3 days = { 30 60 } }
```

### `first_opium_war_3`

실제 ID: `first_opium_war.3`

역할:

- 원옥린 등 엄금론자의 반박을 보여준다.
- 이금론이 정치적으로 밀려나는 과정을 표현한다.

효과:

- 아편 금지 방향을 강화한다.
- 다음 이벤트 `first_opium_war.4`를 예약한다.

```txt
trigger_event = { id = first_opium_war.4 days = { 30 60 } }
```

### `first_opium_war_4`

실제 ID: `first_opium_war.4`

역할:

- 허구의 반박 또는 조정 내 엄금론 결집을 보여준다.
- 청 조정이 사실상 엄금 정책으로 기울었음을 확정한다.

효과:

- `add_banned_goods = g:opium`
- 다음 이벤트 `first_opium_war.5`를 예약한다.

```txt
trigger_event = { id = first_opium_war.5 days = { 30 60 } }
```

### `first_opium_war_5`

실제 ID: `first_opium_war.5`

역할:

- 임칙서 파견 또는 광동 단속 착수를 표현한다.
- 호문소연, 외국 상관 봉쇄, 영국 배상 요구를 여기서 압축하지 않고, 이후 엄금론 사건 체인에서 별도 이벤트로 처리한다.

효과:

- 청나라 쪽 위기 압력을 크게 높인다.
- 영국 측 최종 반응을 기다리지 않고 다음 이벤트 `first_opium_war.9`로 이어간다.

```txt
trigger_event = { id = first_opium_war.9 days = { 60 120 } }
```

### `first_opium_war_9`

실제 ID: `first_opium_war.9`

역할:

- 청 조정의 최종 정책 선택을 처리한다.
- 선택지는 엄금론 하나와 이금론 하나만 둔다.
- 엄금론은 역사적 선택지이며, 곧바로 전쟁을 만들지 않고 `first_opium_war.90`에서 실행 방식을 고르게 한다.
- 이금론은 플레이어 전용 선택지이며, 즉시 전쟁을 피하지만 완전한 비전쟁 결말을 바로 주지는 않는다.
- 이금론을 택하면 후속 이벤트에서 아편 시장 가격, 금 보유, 이해집단 지지도를 안정시켜야 한다는 조건을 설명하고, `이금론` 저널을 연다.
- 기존 복잡한 영국 이벤트 체인은 사용하지 않는다.

선택지 A: 엄금론

- 기본 선택지.
- AI 선택 확률 100%.
- 후속 이벤트 `first_opium_war.90`을 호출한다.
- 전쟁 diplomatic play는 아직 생성하지 않는다.

핵심 효과:

```txt
option = {
    name = first_opium_war.9.a
    default_option = yes
    trigger_event = { id = first_opium_war.90 days = { 7 14 } }
    ai_chance = { base = 1 }
}
```

선택지 B: 이금론

- 플레이어 전용 선택지.
- AI 선택 확률 0%.
- 아편 금지를 해제한다.
- `opium_wars_gave_in`은 아직 설정하지 않는다.
- 후속 이벤트 `first_opium_war.100`을 호출한다.
- 후속 이벤트에서 `이금론` 저널을 열고, 그 저널을 성공시켜야 비전쟁 결말에 도달한다.

핵심 효과:

```txt
option = {
    name = first_opium_war.9.b
    trigger = { is_ai = no }
    if = {
        limit = { is_banning_goods = opium }
        remove_banned_goods = g:opium
    }
    add_modifier = {
        name = eafp_legalized_opium_shame
        days = very_long_modifier_time
    }
    trigger_event = { id = first_opium_war.100 days = { 7 14 } }
    ai_chance = { base = 0 }
}
```

### `first_opium_war_90`

실제 ID: `first_opium_war.90`

역할:

- 엄금론을 택한 뒤 단속 실행 방식을 고르는 이벤트다.
- 선택지는 `흠차대신 임명`과 `현지 관료들에게 책임을 묻고 유예 기간을 주어 스스로 단속을 강화하게 한다` 두 가지다.
- 두 선택지 모두 광동 단속 사건 체인으로 이어지지만, 사건의 시작점과 전쟁 압력 증가 속도가 다르다.
- AI는 역사적 선택인 흠차대신 임명을 고른다.

선택지 A: 흠차대신 임명

- 기본 선택지.
- AI 선택 확률 100%.
- 임칙서 파견을 표현한다.
- 강경한 중앙 특명 단속이므로 위기 압력을 크게 올린다.
- 다음 이벤트 `first_opium_war.91`을 호출한다.

핵심 효과:

```txt
option = {
    name = first_opium_war.90.a
    default_option = yes
    add_banned_goods = g:opium
    add_modifier = {
        name = eafp_imperial_commissioner_opium_crackdown
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.91 days = { 15 30 } }
    ai_chance = { base = 1 }
}
```

선택지 B: 현지 관료 유예

- 플레이어 전용 완충 선택지.
- AI 선택 확률 0%.
- 광동 등 현지 관료들에게 책임을 묻고 일정 유예 기간을 주어 자체 단속을 강화하게 한다.
- 즉시 봉쇄로 튀지는 않지만, 영국과 밀수망의 반발은 결국 누적된다.
- `normal_modifier_time` 동안 현지 단속 modifier를 주고, 다음 이벤트 `first_opium_war.96`을 호출한다.
- 이 선택지는 전쟁을 피하는 선택지가 아니라 사건 순서와 협상 가능성을 바꾸는 선택지다.

핵심 효과:

```txt
option = {
    name = first_opium_war.90.b
    trigger = { is_ai = no }
    add_banned_goods = g:opium
    add_modifier = {
        name = eafp_local_official_opium_grace_period
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.96 days = { 60 120 } }
    ai_chance = { base = 0 }
}
```

### `first_opium_war_91`

실제 ID: `first_opium_war.91`

제목 초안: `13행 전면 봉쇄 및 인질화 조치`

역할:

- 흠차대신이 광동에 도착한 뒤 외국 상관과 13행 상인들을 압박하는 단계다.
- 역사 루트는 상관 봉쇄, 통신 차단, 행상 책임 추궁, 사실상의 인질화 조치로 위기를 급격히 끌어올린다.
- 완화 선택지는 물자 공급과 협상 창구를 남겨 이후 배상 협상으로 갈 여지를 만든다.

선택지 A: 13행 전면 봉쇄 및 인질화 조치

- AI 역사 선택지.
- 위기 압력을 크게 올린다.
- 찰스 엘리엇이 상인 보호와 정부 보상을 명분으로 개입할 수 있게 한다.
- 다음 이벤트 `first_opium_war.92`를 호출한다.

```txt
option = {
    name = first_opium_war.91.a
    default_option = yes
    add_modifier = {
        name = eafp_thirteen_factories_blockade
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.92 days = { 15 30 } }
    ai_chance = { base = 1 }
}
```

선택지 B: 압박하되 교섭 창구는 남긴다

- 플레이어 전용 완화 선택지.
- 위기 압력은 오르지만 봉쇄 강도는 낮다.
- 다음 이벤트 `first_opium_war.92`를 호출하되, 이후 `함정임을 간파` 선택지의 설득력이 커지는 맥락으로 쓴다.

```txt
option = {
    name = first_opium_war.91.b
    trigger = { is_ai = no }
    add_modifier = {
        name = eafp_limited_factory_pressure
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.92 days = { 30 60 } }
    ai_chance = { base = 0 }
}
```

### `first_opium_war_92`

실제 ID: `first_opium_war.92`

제목 초안: `찰스 엘리엇의 아편 국유화`

역할:

- 찰스 엘리엇이 영국 상인의 아편을 영국 정부 명의로 넘기게 하며, 사적 밀수품을 국가 배상 문제로 바꾸는 사건이다.
- 이 이벤트가 엄금론 루트의 핵심 분기점이다.

선택지 A: 아편을 받는다

- AI 역사 선택지.
- 영국 정부가 보상 책임을 떠안은 아편을 청이 접수한다.
- 다음 이벤트 `first_opium_war.93` 호문소연으로 이어진다.

```txt
option = {
    name = first_opium_war.92.a
    default_option = yes
    add_modifier = {
        name = eafp_opium_surrender_accepted
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.93 days = { 15 30 } }
    ai_chance = { base = 1 }
}
```

선택지 B: 함정임을 간파한다

- 플레이어 전용 선택지.
- 아편을 즉시 접수하지 않고, 민간 밀수품과 영국 정부 보상 책임을 분리하려 시도한다.
- 곧바로 배상 협상으로 가지 않고, 영국 정부의 배상 책임을 부정하거나 축소하려는 보조 체인으로 이동한다.
- 다음 이벤트 `first_opium_war.110`을 호출한다.

```txt
option = {
    name = first_opium_war.92.b
    trigger = { is_ai = no }
    add_modifier = {
        name = eafp_opium_surrender_trap_seen
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.110 days = { 15 45 } }
    ai_chance = { base = 0 }
}
```

### `first_opium_war_110`

실제 ID: `first_opium_war.110`

제목 초안: `영국 정부 배상 책임의 분리`

역할:

- `first_opium_war.92.b`에서 엘리엇의 함정을 간파했을 때 발생하는 첫 보조 이벤트다.
- 청 조정은 아편을 곧바로 접수하지 않고, 영국 상인의 사적 밀수품과 영국 정부 명의의 배상 책임을 분리하려 한다.
- 이 루트는 전쟁을 쉽게 피하는 길이 아니라, 시간을 벌면서 영국의 명분을 줄이는 고난도 완화 루트다.

선택지 A: 영국 정부가 밀수 책임을 서면으로 부인하게 한다

- 플레이어 전용 완화 선택지.
- 엘리엇에게 영국 정부가 아편 보상 책임을 공식적으로 떠안지 않는다는 서면을 요구한다.
- 다음 이벤트 `first_opium_war.111`을 호출한다.

```txt
option = {
    name = first_opium_war.110.a
    trigger = { is_ai = no }
    add_modifier = {
        name = eafp_separated_british_compensation_liability
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.111 days = { 15 45 } }
    ai_chance = { base = 0 }
}
```

선택지 B: 논쟁을 중단하고 아편을 몰수한다

- 완화 루트를 포기하고 역사적 강경 루트로 복귀하는 선택지다.
- 청이 결국 아편을 접수해 폐기하므로 `first_opium_war.93` 호문소연으로 이어진다.

```txt
option = {
    name = first_opium_war.110.b
    default_option = yes
    add_modifier = {
        name = eafp_opium_surrender_accepted_late
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.93 days = { 15 30 } }
    ai_chance = { base = 1 }
}
```

### `first_opium_war_111`

실제 ID: `first_opium_war.111`

제목 초안: `무배상 처분안`

역할:

- 영국 정부 배상 책임을 분리한 뒤, 몰수 아편을 사적 밀수품으로 처리하려는 협상 단계다.
- 청은 제한 통상 보장과 낮은 수준의 체면 손상을 대가로 사건을 봉합할 수 있지만, 영국이 요구하는 보상 명분은 완전히 사라지지 않는다.
- 이 이벤트는 `굴욕적 배상조약`으로 가는 협상 루트와, 협상 결렬 후 `영국의 최후통첩`으로 가는 루트를 나눈다.

선택지 A: 제한 통상 보장과 최소 배상으로 봉합한다

- 플레이어 전용 비전쟁 루트 유지 선택지.
- 완전한 승리가 아니라 더 낮은 비용의 굴욕적 타협으로 간다.
- 다음 이벤트 `first_opium_war.98`을 호출한다.

```txt
option = {
    name = first_opium_war.111.a
    trigger = { is_ai = no }
    add_modifier = {
        name = eafp_minimized_opium_compensation_claim
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.98 days = { 15 45 } }
    ai_chance = { base = 0 }
}
```

선택지 B: 배상과 제한 통상 모두 거부한다

- 강경 복귀 선택지다.
- 영국은 청이 책임 회피와 통상 거부를 동시에 택했다고 보고 기존 `영국의 최후통첩` 이벤트로 이어진다.

```txt
option = {
    name = first_opium_war.111.b
    default_option = yes
    trigger_event = { id = first_opium_war.12 days = { 7 21 } }
    ai_chance = { base = 1 }
}
```

### `first_opium_war_93`

실제 ID: `first_opium_war.93`

제목 초안: `호문소연`

역할:

- 접수한 아편을 공개 폐기하는 사건이다.
- 플레이어 선택을 크게 두지 않고, 앞선 `아편 받기` 선택의 결과로 발생하는 합류 이벤트로 둔다.
- 전쟁 압력을 크게 올린 뒤 임유희 사건으로 이어진다.

```txt
option = {
    name = first_opium_war.93.a
    default_option = yes
    add_modifier = {
        name = eafp_humen_opium_destruction
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.94 days = { 60 120 } }
    ai_chance = { base = 1 }
}
```

### `first_opium_war_94`

실제 ID: `first_opium_war.94`

제목 초안: `임유희 살인 사건`

역할:

- 구룡 인근에서 임유희(林維喜)가 사망하고, 청이 범인 인도를 요구하지만 영국 측이 인도를 거부하는 사건이다.
- 이 사건은 호문소연 이후의 외교 위기를 무력 충돌 직전으로 밀어붙이는 분기점이다.

선택지 A: 영국 선단에 식량 공급을 완전히 차단한다

- AI 역사 선택지.
- 범인 인도 거부에 대한 강경 보복이다.
- 기존 `영국의 최후통첩` 이벤트 `first_opium_war.12`로 이어진다.

```txt
option = {
    name = first_opium_war.94.a
    default_option = yes
    add_modifier = {
        name = eafp_british_fleet_supply_cutoff
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.12 days = { 15 30 } }
    ai_chance = { base = 1 }
}
```

선택지 B: 범인 인도 요구는 유지하되 공급 차단은 제한한다

- 플레이어 전용 완화 선택지.
- 전쟁 압력을 낮추지는 못하지만, 즉시 최후통첩으로 가지 않고 토머스 쿠츠 호 사건으로 이어진다.

```txt
option = {
    name = first_opium_war.94.b
    trigger = { is_ai = no }
    add_modifier = {
        name = eafp_limited_response_to_lin_weixi_case
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.97 days = { 15 45 } }
    ai_chance = { base = 0 }
}
```

### `first_opium_war_96`

실제 ID: `first_opium_war.96`

제목 초안: `현지 관료들의 유예 단속`

역할:

- `first_opium_war.90.b`에서 현지 관료에게 책임과 유예 기간을 준 경우의 후속 이벤트다.
- 단속은 강화되지만 중앙 특명보다 느리고 균열이 생긴다.
- 곧바로 토머스 쿠츠 호 사건으로 가지 않고, 현지 단속 지연과 결서 제출 문제를 먼저 다룬다.

```txt
option = {
    name = first_opium_war.96.a
    default_option = yes
    add_modifier = {
        name = eafp_local_opium_crackdown_deadline
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.112 days = { 30 90 } }
    ai_chance = { base = 1 }
}
```

### `first_opium_war_112`

실제 ID: `first_opium_war.112`

제목 초안: `현지 단속 지연`

역할:

- 현지 관료에게 유예 기간을 준 결과, 단속 명령은 내려갔지만 실제 집행이 느려지는 상황을 다룬다.
- 광동 관료와 13행 상인들은 외국 상인과의 기존 거래 질서를 완전히 끊지 않으려 하고, 청 조정은 체면과 실효성 사이에서 다시 선택해야 한다.
- 이 이벤트는 현지 유예 루트가 단순한 평화 선택지가 아니라, 중앙 통제 약화와 외국 상인 이탈을 동반한다는 점을 보여준다.

선택지 A: 기한을 재확인하고 결서 제출을 요구한다

- 플레이어 전용 완화 루트 유지 선택지.
- 외국 상인에게 아편 금지 서약인 결서를 요구하고, 이를 따르는 선박만 통상 질서로 되돌리려 한다.
- 다음 이벤트 `first_opium_war.113`을 호출한다.

```txt
option = {
    name = first_opium_war.112.a
    trigger = { is_ai = no }
    add_modifier = {
        name = eafp_local_crackdown_deadline_reaffirmed
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.113 days = { 30 60 } }
    ai_chance = { base = 0 }
}
```

선택지 B: 현지 재량을 더 인정한다

- 유예를 더 주는 선택지지만, 결과적으로 영국 상인과 엘리엇 사이의 균열을 빠르게 드러낸다.
- 다음 이벤트 `first_opium_war.97` 토머스 쿠츠 호 사건으로 이어진다.

```txt
option = {
    name = first_opium_war.112.b
    default_option = yes
    add_modifier = {
        name = eafp_local_official_discretion_extended
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.97 days = { 15 45 } }
    ai_chance = { base = 1 }
}
```

### `first_opium_war_113`

실제 ID: `first_opium_war.113`

제목 초안: `결서 제출 문제`

역할:

- 현지 단속 유예 루트에서 결서를 제출한 선박과 엘리엇의 통제에 따르는 선박 사이의 균열을 다룬다.
- 토머스 쿠츠 호 사건으로 이어질 수 있는 직접 전 단계다.
- 청 조정은 결서 제출 선박을 선례로 삼아 제한 통상을 회복할지, 영국 선단 전체를 같은 압박 대상으로 묶을지 선택한다.

선택지 A: 결서 제출 선박만 받아들인다

- 플레이어 전용 완화 선택지.
- 영국 내부 균열을 이용해 토머스 쿠츠 호 사건으로 이어진다.
- 다음 이벤트 `first_opium_war.97`을 호출한다.

```txt
option = {
    name = first_opium_war.113.a
    trigger = { is_ai = no }
    add_modifier = {
        name = eafp_bond_submission_precedent
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.97 days = { 15 45 } }
    ai_chance = { base = 0 }
}
```

선택지 B: 결서 없이는 선단 전체를 압박한다

- 강경 복귀 선택지다.
- 현지 유예 루트가 실패하고, 기존 `영국의 최후통첩` 이벤트로 이어진다.

```txt
option = {
    name = first_opium_war.113.b
    default_option = yes
    add_modifier = {
        name = eafp_bond_submission_rejected_fleet_pressure
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.12 days = { 15 45 } }
    ai_chance = { base = 1 }
}
```

### `first_opium_war_97`

실제 ID: `first_opium_war.97`

제목 초안: `토머스 쿠츠 호 배신 사건`

역할:

- 토머스 쿠츠 호가 엘리엇의 지시를 거스르고 결서 제출 또는 통상 재개를 시도한 사건을 다룬다.
- 청 조정은 이를 영국 내부 균열로 이용할지, 배신을 받아들인 선례가 더 큰 분열을 부를 것을 우려해 강경 대응할지 선택한다.

선택지 A: 배신을 이용해 통상 질서를 다시 세운다

- 플레이어 전용 완화 선택지.
- 토머스 쿠츠 호의 협조를 근거로 제한 통상과 배상 협상으로 이동한다.
- 다음 이벤트 `first_opium_war.98`을 호출한다.

```txt
option = {
    name = first_opium_war.97.a
    trigger = { is_ai = no }
    add_modifier = {
        name = eafp_thomas_coutts_precedent
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.98 days = { 15 45 } }
    ai_chance = { base = 0 }
}
```

선택지 B: 엘리엇의 권위 뒤에 숨은 영국 선단 전체를 압박한다

- AI 역사 선택지.
- 토머스 쿠츠 호 사건이 평화 신호가 아니라 영국 내부 균열과 압박 심화의 계기가 된다.
- 기존 `영국의 최후통첩` 이벤트 `first_opium_war.12`로 이어진다.

```txt
option = {
    name = first_opium_war.97.b
    default_option = yes
    add_modifier = {
        name = eafp_rejected_thomas_coutts_precedent
        days = normal_modifier_time
    }
    trigger_event = { id = first_opium_war.12 days = { 15 45 } }
    ai_chance = { base = 1 }
}
```

### `first_opium_war_98`

실제 ID: `first_opium_war.98`

제목 초안: `배상 협상`

역할:

- `찰스 엘리엇의 함정`을 간파한 뒤 영국 정부 배상 책임 분리를 시도했거나, 토머스 쿠츠 호 사건을 이용했을 때 열리는 완화 루트다.
- 전쟁을 명예롭게 피하는 길이 아니라, 청이 배상과 제한 통상 보장을 받아들이는 굴욕적 타협 루트다.

선택지 A: 배상과 제한 통상 보장을 받아들인다

- 플레이어 전용 비전쟁 결말.
- 다음 이벤트 `first_opium_war.99` 굴욕적 배상조약으로 이어진다.

```txt
option = {
    name = first_opium_war.98.a
    trigger = { is_ai = no }
    trigger_event = { id = first_opium_war.99 days = { 7 14 } }
    ai_chance = { base = 0 }
}
```

선택지 B: 끝내 받아들일 수 없다

- 전쟁 루트 복귀 선택지.
- 기존 `영국의 최후통첩` 이벤트 `first_opium_war.12`로 이어진다.

```txt
option = {
    name = first_opium_war.98.b
    default_option = yes
    trigger_event = { id = first_opium_war.12 days = { 7 14 } }
    ai_chance = { base = 1 }
}
```

### `first_opium_war_99`

실제 ID: `first_opium_war.99`

제목 초안: `굴욕적 배상조약`

역할:

- 엄금론 루트에서 전쟁을 피할 수 있는 드문 결말이다.
- 청은 아편 단속 명분을 유지하지만, 영국 상인 손실 배상과 제한 통상 보장을 받아들인다.
- 좋은 결말이 아니라, 전쟁 대신 외교적 굴욕과 재정 부담을 택하는 결말이다.
- 메인 저널 완료를 위해 `opium_wars_gave_in`을 설정한다.

```txt
option = {
    name = first_opium_war.99.a
    default_option = yes
    set_variable = opium_wars_gave_in
    add_modifier = {
        name = eafp_humiliating_opium_indemnity_treaty
        days = very_long_modifier_time
    }
    ai_chance = { base = 1 }
}
```

### `first_opium_war_100`

실제 ID: `first_opium_war.100`

역할:

- 이금론을 택한 뒤 무엇을 해야 하는지 설명하는 후속 이벤트다.
- 조정이 외국 아편 의존과 은 유출을 끊으려면 아편 시장 가격을 안정시키고, 금 보유를 회복하며, 이해집단의 공개 반발을 억제해야 한다고 안내한다.
- 선택지는 하나만 둔다.

효과:

- `이금론` 저널을 추가한다.
- 이 저널은 기존 국내 아편 생산 저널의 timeout 구조를 바탕으로 하되, 완료 조건은 이금론 안정화 조건으로 바꾼다.
- 실제 법률 부칙 추가는 저널 시작 `immediate`에서 처리한다.

```txt
option = {
    name = first_opium_war.100.a
    default_option = yes
    add_journal_entry = { type = je_first_opium_war_legalization }
    ai_chance = { base = 1 }
}
```

## `이금론` 저널

실제 ID 초안: `je_first_opium_war_legalization`

표시 이름:

```yml
je_first_opium_war_legalization: "이금론"
```

역할:

- 기존 국내 아편 생산 저널의 제한 시간과 실패 구조를 재사용한다.
- 완료 조건은 국내 아편 생산량 자체가 아니라, 이금론이 실제로 시장과 재정을 안정시켰는지를 본다.
- 아편의 시장 가격이 base price의 120% 이하이고, 금 보유율이 충분하며, 모든 이해집단이 최소한 중립 이상이어야 한다.
- 이름과 설명만 `이금론` 정책 실행에 맞게 바꾼다.
- 새 저널은 기존 국내 아편 생산 저널의 timeout 구조를 옮겨오되, complete 조건은 새 조건으로 교체한다.
- 월간 반복 이벤트는 기존 국내 아편 생산 저널의 `first_opium_war.26` 대신 아편 중독 저널의 반복 이벤트 묶음을 그대로 사용한다.
- 저널 시작 시 `광동체제` 법률에 `이금론` 부칙을 추가한다.
- `이금론` 부칙이 폐지되면 저널은 invalid 처리된다.
- 이때 청나라가 여전히 `광동체제` 또는 `고립주의`를 유지 중이면 기존 `영국의 최후통첩` 이벤트 `first_opium_war.12`를 재사용해 전쟁 루트로 되돌린다.

법률 부칙:

- 부칙 ID 초안: `amendment_first_opium_war_legalization`
- 표시 이름: `이금론`
- 붙는 법률: `law_canton_system`
- 기본 parent 법률: `law_isolationism`
- 저널 시작 시 청나라의 활성 무역 법률이 `law_canton_system`일 때만 부칙을 추가한다.
- 효과는 국가가 아편을 제도권 안으로 끌어들였을 때의 주조 수익 증가, 행정 부담, 아편 수요 증가, 아편 수출 관세 상한 감소, 조정 정통성 손상, 유교/상인층 반발을 함께 표현한다.

부칙 정의 초안:

```txt
amendment_first_opium_war_legalization = {
    parent = law_isolationism

    allowed_laws = {
        law_canton_system
    }

    modifier = {
        country_minting_mult = 0.05
        country_bureaucracy_mult = -0.05
        state_buy_orders_opium_add = 100
        country_opium_max_export_tariffs_level_add = -2
        country_legitimacy_base_add = -10
        interest_group_ig_devout_approval_add = -5
        interest_group_ig_petty_bourgeoisie_approval_add = -5
    }

    possible = {
        c:CHI ?= THIS
    }

    ai_will_revoke = {
        always = no
    }
}
```

부칙 폐지 잔존 modifier:

- modifier ID 초안: `eafp_first_opium_war_legalization_repealed_decay`
- 역할: `이금론` 부칙을 폐지해도 이미 생긴 합법화의 행정 부담, 아편 수요, 정통성 손상, 이해집단 반발이 즉시 사라지지 않도록 표현한다.
- 효과는 `amendment_first_opium_war_legalization`의 modifier와 동일하게 둔다.
- 적용 방식은 `add_modifier`에서 `days = normal_modifier_time`, `is_decaying = yes`를 사용한다.

정의 초안:

```txt
eafp_first_opium_war_legalization_repealed_decay = {
    country_minting_mult = 0.05
    country_bureaucracy_mult = -0.05
    state_buy_orders_opium_add = 100
    country_opium_max_export_tariffs_level_add = -2
    country_legitimacy_base_add = -10
    interest_group_ig_devout_approval_add = -5
    interest_group_ig_petty_bourgeoisie_approval_add = -5
}
```

내용:

```txt
immediate = {
    if = {
        limit = { has_law = law_type:law_canton_system }
        active_law:lawgroup_trade_policy ?= {
            if = {
                limit = {
                    NOT = {
                        has_amendment = amendment_type:amendment_first_opium_war_legalization
                    }
                }
                add_amendment = {
                    type = amendment_first_opium_war_legalization
                    sponsor = PREV.ig:ig_landowners
                }
            }
        }
    }
}

complete = {
    custom_tooltip = {
        text = eafp_first_opium_war_legalization_opium_price_tt
        # market_goods_pricier <= 0.2: 현재 시장 가격이 base price보다 20% 초과로 비싸지 않음.
        mg:opium = { market_goods_pricier <= 0.2 }
    }
    gold_reserve_ratio >= 0.2
    custom_tooltip = {
        text = eafp_first_opium_war_legalization_ig_approval_tt
        NOT = {
            any_interest_group = {
                ig_approval < 0
            }
        }
    }
}

on_monthly_pulse = {
    random_events = {
        100 = 0
        10 = first_opium_war.6
        5 = first_opium_war.7
        5 = first_opium_war.8
    }
}

on_complete = {
    trigger_event = { id = first_opium_war.101 popup = yes }
}

on_timeout = {
    trigger_event = { id = first_opium_war.102 popup = yes }
}

invalid = {
    OR = {
        NOT = { exists = c:CHI }
        NOT = { THIS = c:CHI }
        has_variable = opium_wars_target
        has_variable = opium_wars_gave_in
        AND = {
            OR = {
                has_law = law_type:law_canton_system
                has_law = law_type:law_isolationism
            }
            active_law:lawgroup_trade_policy ?= {
                NOT = {
                    has_amendment = amendment_type:amendment_first_opium_war_legalization
                }
            }
        }
    }
}

on_invalid = {
    if = {
        limit = {
            OR = {
                has_law = law_type:law_canton_system
                has_law = law_type:law_isolationism
            }
            NOT = { has_variable = opium_wars_target }
            NOT = { has_variable = opium_wars_gave_in }
        }
        add_modifier = {
            name = eafp_first_opium_war_legalization_repealed_decay
            days = normal_modifier_time
            is_decaying = yes
        }
        trigger_event = { id = first_opium_war.12 popup = yes }
    }
}
```

성공:

- `first_opium_war.101`을 호출한다.
- 청나라에 `opium_wars_gave_in`을 설정한다.
- 아편 가격, 금 보유, 이해집단 지지도 조건을 모두 만족해 이금론이 관리 가능한 정책으로 자리잡았음을 보여준다.
- 아편 합법화/시장 안정 modifier를 부여한다.
- `je_qing_opium_obsession` 완료 조건을 만족한다.

실패:

- `first_opium_war.102`를 호출한다.
- 이금론은 실패하고 엄금론/전쟁 루트로 되돌아간다.
- 기존 `영국의 최후통첩` 이벤트 `first_opium_war.12`를 호출해 아편전쟁 루트로 합류한다.

부칙 폐지:

- 플레이어가 `이금론` 부칙을 폐지하면 `이금론` 저널은 invalid 된다.
- `on_invalid`는 `광동체제` 또는 `고립주의`가 유지 중인지 확인한다.
- 조건을 만족하면 `eafp_first_opium_war_legalization_repealed_decay`를 `normal_modifier_time` 동안 `is_decaying = yes`로 부여한다.
- 이어서 기존 이벤트 `first_opium_war.12`를 호출한다.
- `first_opium_war.12`는 이미 존재하는 `영국의 최후통첩` 이벤트로, 이후 영국 반응과 아편전쟁 루트로 이어진다.

월간 반복 이벤트:

- `first_opium_war.6`: 아편 수입/밀수 관련 외교 마찰 이벤트.
- `first_opium_war.7`: 아편 중독 회복 또는 관리 방향 이벤트.
- `first_opium_war.8`: 주 단위 아편 중독 피해 이벤트.
- 세 이벤트의 localization은 기존처럼 바닐라 `opium_wars.6`, `.7`, `.8` alias를 재사용한다.
- 세 이벤트는 삭제 대상이 아니라, 이금론 저널의 월간 반복 이벤트로 유지한다.

### `first_opium_war_101`

실제 ID: `first_opium_war.101`

역할:

- `이금론` 저널 성공 이벤트다.
- 아편 가격과 금 보유, 이해집단 지지도가 안정되어 이금론이 일단 관리 가능한 정책으로 자리잡았다는 결말을 보여준다.

효과:

- `opium_wars_gave_in`을 설정한다.
- 아편 금지는 해제 상태를 유지한다.
- 필요하면 `eafp_legalized_opium_shame` 또는 국내 아편 체제 modifier를 부여한다.

```txt
option = {
    name = first_opium_war.101.a
    default_option = yes
    set_variable = opium_wars_gave_in
    add_modifier = {
        name = eafp_legalized_opium_shame
        days = very_long_modifier_time
    }
}
```

### `first_opium_war_102`

실제 ID: `first_opium_war.102`

역할:

- `이금론` 저널 실패 이벤트다.
- 아편 가격 안정, 금 보유 회복, 이해집단 지지도 확보 중 하나 이상에 실패해 이금론이 무너지고, 위기가 다시 전쟁 루트로 돌아가는 상황을 보여준다.

효과:

- 기존 `영국의 최후통첩` 이벤트 `first_opium_war.12`를 호출한다.
- `first_opium_war.12` 이후 영국 반응과 아편전쟁 루트로 이어진다.

```txt
option = {
    name = first_opium_war.102.a
    default_option = yes
    trigger_event = { id = first_opium_war.12 popup = yes }
}
```

## 삭제할 요소

다음 요소는 새 선형 계획에서 제거한다.

- 기존 `first_opium_war.10`부터 `first_opium_war.52`까지의 분기형 체인
- 단, 새 선형 계획에서는 이금론 실행/성공/실패 이벤트를 `first_opium_war.100`, `.101`, `.102`로 새로 둔다.
- 기존 `first_opium_war.12`는 엄금론 사건 체인의 전쟁 합류점과 `이금론` 부칙 폐지 시 `영국의 최후통첩` 이벤트로 재사용하므로 삭제하지 않는다.
- `first_opium_war.12`가 의존하는 전쟁 연결 효과는 기존 이벤트 체인을 유지하거나, 구현 단계에서 `first_opium_war.12` 안에 직접 전쟁 생성 효과를 보강한다.
- `first_opium_war.90`부터 `.99`는 새 엄금론 사건 체인으로 추가한다.
- `first_opium_war.110`부터 `.113`은 엄금론 보조 분기 체인으로 추가한다.
- 기존 `je_first_opium_war_domestic_opium_substitution` ID
- 국내 아편 재배 성공/실패 루트의 기존 이름과 분기 구조
- 배상 타협 루트
- 국산 아편 체제 결말
- 월간 random event 기반 조정 논쟁 pulse

단, `굴욕적 배상조약`은 삭제 대상이 아니다. 기존의 느슨한 배상 타협 루트를 제거하고, 새 계획에서는 `first_opium_war.98`과 `.99`로 엄금론 사건 체인 안에 제한적으로 다시 둔다.

단, 국내 아편 생산 저널의 제한 시간과 실패 구조는 `이금론` 저널로 이름을 바꿔 재사용하되, 완료 조건은 아편 가격, 금 보유, 이해집단 지지도 조건으로 교체한다. localization이나 사료 기반 flavor text 중 재사용할 수 있는 내용은 `1`, `2`, `3`, `4`, `5`, `9`, `100`, `101`, `102`에 재배치할 수 있다. `6`, `7`, `8`은 새 선형 본체에 재배치하지 않고, 기존 바닐라 alias 기반 아편 중독 반복 이벤트 localization으로 유지한다.

## 안전장치

각 이벤트에는 다음 guard를 둔다.

청나라 이벤트:

```txt
trigger = {
    has_journal_entry = je_qing_opium_obsession
    NOT = { has_variable = opium_wars_target }
    NOT = { has_variable = opium_wars_gave_in }
}
```

전쟁 발발 선택지 guard:

```txt
trigger = {
    exists = c:CHI
    exists = c:GBR
    c:CHI = {
        has_journal_entry = je_qing_opium_obsession
        NOT = { has_variable = opium_wars_target }
        NOT = { has_variable = opium_wars_gave_in }
    }
    NOT = { is_diplomatic_play_enemy_of = c:CHI }
}
```

반복 호출 방지를 위해 모든 선형 이벤트에 긴 cooldown을 둔다.

```txt
cooldown = { days = stupidly_long_modifier_time }
```

## 구현 순서

1. 기존 분기형 이벤트 정의를 제거한다.
2. 선형 본체 이벤트는 `first_opium_war.1`, `.2`, `.3`, `.4`, `.5`, `.9`, `.90-.99`, `.100`, `.101`, `.102`, `.110-.113`만 남긴다.
3. 아편 중독 월간 반복 이벤트로 `first_opium_war.6`, `.7`, `.8`은 유지한다.
4. 부칙 폐지 시 재사용할 기존 `영국의 최후통첩` 이벤트 `first_opium_war.12`도 유지한다.
5. `.1`부터 `.5`까지는 기본 선택지 하나만 둔다.
6. `.1`부터 `.5`까지는 다음 이벤트 하나만 `trigger_event`로 예약하게 한다.
7. `je_qing_opium_obsession`의 monthly random events와 scripted progress bar 의존을 제거한다.
8. `je_first_opium_war_domestic_opium_substitution` ID는 제거하고, 제한 시간과 실패 구조만 `je_first_opium_war_legalization`으로 옮긴다.
9. `이금론` 저널 완료 조건을 아편 시장 가격 120% 이하, `gold_reserve_ratio >= 0.2`, 모든 이해집단 `ig_approval >= 0`으로 교체한다.
10. 아편 시장 가격 조건은 scripted trigger로 분리하지 않고, 저널 `complete` 안에 `mg:opium = { market_goods_pricier <= 0.2 }`로 직접 적는다.
11. `amendment_first_opium_war_legalization`을 추가하고, `parent = law_isolationism`, `allowed_laws = { law_canton_system }`로 둔다.
12. `eafp_first_opium_war_legalization_repealed_decay` modifier를 추가한다. 효과는 `이금론` 부칙과 같고, 부칙 폐지 시 `normal_modifier_time` 동안 `is_decaying = yes`로 적용한다.
13. `이금론` 저널 `immediate`에서 `lawgroup_trade_policy`의 활성 법률에 부칙을 추가한다.
14. `이금론` 저널 `invalid`는 `광동체제` 또는 `고립주의` 유지 중 `이금론` 부칙이 사라진 경우를 잡는다.
15. `이금론` 저널 `on_invalid`는 decay modifier를 부여하고 기존 `first_opium_war.12`를 호출한다.
16. `이금론` 저널 `on_monthly_pulse`에 아편 중독 저널과 같은 반복 이벤트 `first_opium_war.6`, `.7`, `.8`을 넣는다.
17. localization에서 삭제된 이벤트 키를 제거한다.
18. 남긴 이벤트의 title, desc, flavor, option을 순서대로 재정렬한다.
19. `first_opium_war.9`에서 엄금론과 이금론 두 선택지를 처리한다.
20. 엄금론 선택지는 전쟁 diplomatic play를 직접 만들지 않고 `first_opium_war.90`을 호출한다.
21. `first_opium_war.90`은 흠차대신 임명과 현지 관료 유예 중 하나를 고르게 한다.
22. `first_opium_war.90.a` 흠차대신 임명은 AI 역사 선택지이며 `first_opium_war.91`로 이어진다.
23. `first_opium_war.90.b` 현지 관료 유예는 플레이어 전용 선택지이며 `first_opium_war.96`으로 이어진다.
24. `first_opium_war.91`은 `13행 전면 봉쇄 및 인질화 조치`와 완화 선택지를 처리한다.
25. `first_opium_war.92`는 찰스 엘리엇의 아편 국유화 후 아편 넘기기를 처리한다. `아편 받기`는 `.93` 호문소연으로, `함정임을 간파`는 `.110` 영국 정부 배상 책임 분리로 간다.
26. `first_opium_war.110`은 영국 정부 배상 책임 분리를 처리한다. 서면 책임 분리 요구는 `.111`로, 논쟁 중단 후 몰수는 `.93` 호문소연으로 간다.
27. `first_opium_war.111`은 무배상 처분안을 처리한다. 제한 통상과 최소 배상 봉합은 `.98` 배상 협상으로, 전면 거부는 기존 `.12` 영국의 최후통첩으로 간다.
28. `first_opium_war.93`은 호문소연을 처리하고 `.94` 임유희 사건으로 이어진다.
29. `first_opium_war.94`는 임유희 살인 사건과 범인 인도 거부를 처리한다. 식량 공급 완전 차단은 기존 `.12` 영국의 최후통첩으로, 제한 대응은 `.97` 토머스 쿠츠 호 사건으로 간다.
30. `first_opium_war.96`은 현지 관료 유예 단속 후 `.112` 현지 단속 지연으로 간다.
31. `first_opium_war.112`는 현지 단속 지연을 처리한다. 기한 재확인과 결서 제출 요구는 `.113`으로, 현지 재량 확대는 `.97` 토머스 쿠츠 호 사건으로 간다.
32. `first_opium_war.113`은 결서 제출 문제를 처리한다. 결서 제출 선박만 받아들이면 `.97`로, 선단 전체 압박은 기존 `.12` 영국의 최후통첩으로 간다.
33. `first_opium_war.97`은 토머스 쿠츠 호 배신 사건을 처리한다. 이를 이용하면 `.98` 배상 협상으로, 거부하면 기존 `.12` 영국의 최후통첩으로 간다.
34. `first_opium_war.98`은 배상 협상을 처리한다. 배상과 제한 통상 보장을 받아들이면 `.99` 굴욕적 배상조약으로, 거부하면 기존 `.12` 영국의 최후통첩으로 간다.
35. `first_opium_war.99`는 굴욕적 배상조약 결말이며 `opium_wars_gave_in`을 설정한다.
36. 이금론 선택지는 아편 금지를 해제하고 `first_opium_war.100`을 호출한다.
37. `first_opium_war.100`은 `이금론` 저널을 연다.
38. `이금론` 저널 성공 시 `.101`, 실패 시 `.102`를 호출한다.
39. `.101`은 `opium_wars_gave_in`을 설정한다.
40. `.102`는 기존 `.12` 영국의 최후통첩을 호출한다.
41. 오류 검사를 수행한다.

## 오류 검사

잔여 분기 이벤트 확인:

`first_opium_war.6`, `.7`, `.8`은 삭제 대상이 아니라 `이금론` 저널의 아편 중독 월간 반복 이벤트로 남긴다. `first_opium_war.12`도 엄금론 사건 체인의 전쟁 합류점 또는 부칙 폐지 시 기존 `영국의 최후통첩` 이벤트로 재사용한다. `first_opium_war.90-.99`와 `.110-.113`은 새 엄금론 사건 체인으로 남긴다. 따라서 잔여 분기 이벤트 확인 정규식에서는 `.6`, `.7`, `.8`, `.12`, `.90-.99`, `.110-.113`을 제외하고, 기존 분기 체인의 나머지만 잡는다.

```powershell
rg -n "first_opium_war\.(10|11|1[3-9]|2[0-9]|3[0-9]|4[0-9]|5[0-2])\b" common events localization documentation
```

남아야 하는 이벤트 확인:

```powershell
rg -n "first_opium_war\.(1|2|3|4|5|6|7|8|9|12|9[0-9]|10[0-2]|11[0-3])\b" events localization documentation
```

구버전 보조 저널 ID 제거 확인:

```powershell
rg -n "je_first_opium_war_domestic_opium_substitution" common events localization documentation
```

새 이금론 저널 확인:

```powershell
rg -n "je_first_opium_war_legalization|이금론" common events localization documentation
```

이금론 완료 조건 확인:

```powershell
rg -n "mg:opium|market_goods_pricier <= 0.2|gold_reserve_ratio|ig_approval < 0|eafp_first_opium_war_legalization_opium_price_tt|eafp_first_opium_war_legalization_ig_approval_tt" common events localization documentation
```

이금론 부칙 확인:

```powershell
rg -n "amendment_first_opium_war_legalization|law_canton_system|law_isolationism|state_buy_orders_opium_add|country_opium_max_export_tariffs_level_add" common events localization documentation
```

이금론 부칙 폐지 invalid 확인:

```powershell
rg -n "eafp_first_opium_war_legalization_repealed_decay|on_invalid|has_amendment = amendment_type:amendment_first_opium_war_legalization|trigger_event = \\{ id = first_opium_war\\.12|is_decaying = yes" common events localization documentation
```

최종 선택지 효과 확인:

```powershell
rg -n "first_opium_war\\.(90|91|92|93|94|96|97|98|99|110|111|112|113|12)|dp_first_opium_war|create_diplomatic_play|opium_wars_target|opium_wars_aggressor|opium_wars_gave_in|eafp_legalized_opium_shame|eafp_imperial_commissioner_opium_crackdown|eafp_local_official_opium_grace_period|eafp_thirteen_factories_blockade|eafp_opium_surrender_trap_seen|eafp_separated_british_compensation_liability|eafp_minimized_opium_compensation_claim|eafp_local_crackdown_deadline_reaffirmed|eafp_bond_submission_precedent|eafp_humen_opium_destruction|eafp_british_fleet_supply_cutoff|eafp_humiliating_opium_indemnity_treaty|je_first_opium_war_legalization" events/eafp_chi_events/eafp_first_opium_war_events.txt
```

기본 구조 검사:

- 이벤트 파일 brace balance가 0인지 확인한다.
- 정의되지 않은 `trigger_event` target이 없는지 확인한다.
- localization 중복 key가 없는지 확인한다.
- `git diff --check`를 실행한다.
- `.txt`, `.yml`, `.md` 파일의 UTF-8 BOM + CRLF 상태를 확인한다.
- 게임 실행 후 `error.log`에서 unknown event, missing localization, invalid scope, invalid diplomatic play 오류를 확인한다.

## 최종 기대 흐름

청나라 시작:

1. `je_qing_opium_obsession` 추가.
2. `first_opium_war.1` 발생.
3. 조정 논쟁 이벤트 `2`, `3`, `4`가 순차 발생.
4. 광동 단속 이벤트 `5` 발생.
5. 최종 정책 선택 이벤트 `9` 발생.
6. `9.a` 엄금론 선택 시 `first_opium_war.90`이 발생한다.
7. `first_opium_war.90`에서 흠차대신 임명을 고르면 `first_opium_war.91` 13행 봉쇄 사건으로 간다.
8. `first_opium_war.90`에서 현지 관료 유예를 고르면 `first_opium_war.96` 현지 단속 유예 사건으로 간다.
9. `first_opium_war.91`에서 13행 전면 봉쇄 및 인질화 조치를 택하면 `first_opium_war.92` 엘리엇의 아편 국유화 사건으로 간다.
10. `first_opium_war.92`에서 아편을 받으면 `first_opium_war.93` 호문소연으로 이어진다.
11. `first_opium_war.92`에서 함정임을 간파하면 `first_opium_war.110` 영국 정부 배상 책임 분리 사건으로 간다.
12. `first_opium_war.110`에서 영국 정부 책임 분리 서면을 요구하면 `first_opium_war.111` 무배상 처분안으로 가고, 논쟁을 중단하고 몰수하면 `first_opium_war.93` 호문소연으로 돌아간다.
13. `first_opium_war.111`에서 제한 통상과 최소 배상으로 봉합하면 `first_opium_war.98` 배상 협상으로 가고, 배상과 제한 통상을 모두 거부하면 기존 `first_opium_war.12` 영국의 최후통첩으로 간다.
14. `first_opium_war.93` 호문소연 이후 `first_opium_war.94` 임유희 살인 사건이 발생한다.
15. `first_opium_war.94`에서 영국 선단 식량 공급을 완전히 차단하면 기존 `first_opium_war.12` 영국의 최후통첩으로 가고, 이후 아편전쟁 루트로 진행된다.
16. `first_opium_war.94`에서 제한 대응을 택하면 `first_opium_war.97` 토머스 쿠츠 호 배신 사건으로 간다.
17. `first_opium_war.96` 현지 관료 유예 루트는 `first_opium_war.112` 현지 단속 지연으로 간다.
18. `first_opium_war.112`에서 기한을 재확인하고 결서 제출을 요구하면 `first_opium_war.113` 결서 제출 문제로 가고, 현지 재량을 더 인정하면 `first_opium_war.97` 토머스 쿠츠 호 사건으로 간다.
19. `first_opium_war.113`에서 결서 제출 선박만 받아들이면 `first_opium_war.97` 토머스 쿠츠 호 사건으로 가고, 선단 전체를 압박하면 기존 `first_opium_war.12` 영국의 최후통첩으로 간다.
20. `first_opium_war.97`에서 토머스 쿠츠 호 사건을 이용하면 `first_opium_war.98` 배상 협상으로, 거부하면 기존 `first_opium_war.12` 영국의 최후통첩으로 간다.
21. `first_opium_war.98`에서 배상과 제한 통상을 받아들이면 `first_opium_war.99` 굴욕적 배상조약으로 끝난다.
22. `first_opium_war.98`에서 거부하면 기존 `first_opium_war.12` 영국의 최후통첩으로 가고, 이후 아편전쟁 루트로 진행된다.
23. `9.b` 이금론 선택 시 청나라는 아편 금지를 해제하고 `first_opium_war.100`을 받는다.
24. `first_opium_war.100`은 `이금론` 저널을 연다.
25. `이금론` 저널 시작 시 `광동체제` 법률에 `이금론` 부칙이 붙는다.
26. `이금론` 저널이 활성화된 동안 매월 아편 중독 반복 이벤트 `first_opium_war.6`, `.7`, `.8`이 아편 중독 저널과 같은 방식으로 수행된다.
27. 아편 가격이 base price의 120% 이하, `gold_reserve_ratio >= 0.2`, 모든 이해집단 지지도 0 이상을 동시에 만족하면 `이금론` 저널이 성공한다.
28. `이금론` 저널 성공 시 `first_opium_war.101`이 발생하고 `opium_wars_gave_in`을 받아 메인 저널 완료 조건을 만족.
29. `이금론` 저널 실패 시 `first_opium_war.102`가 발생하고 기존 `first_opium_war.12` 영국의 최후통첩으로 돌아간다.
30. `광동체제` 또는 `고립주의` 유지 중 `이금론` 부칙을 폐지하면 `이금론` 저널이 invalid 된다.
31. `on_invalid`는 `eafp_first_opium_war_legalization_repealed_decay`를 `normal_modifier_time` 동안 decay modifier로 부여한다.
32. 이후 기존 `영국의 최후통첩` 이벤트 `first_opium_war.12`가 발생하고, 여기서 아편전쟁 루트로 돌아간다.
