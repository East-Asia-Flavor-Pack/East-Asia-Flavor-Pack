# 조선-청 전쟁 저널 메커니즘 개편 설계안

## 1. 설계 범위

이 문서는 조선(`KOR`)과 청(`CHI`) 사이에 실제 전쟁이 벌어졌을 때 활성화되는
`je_eafp_joseon_qing_war`의 개편안을 다룬다.

기존 합의 사항은 그대로 유지한다.

- 껍데기 저널을 만들지 않는다.
- `add_journal_entry`를 사용하지 않는다.
- 실제 전쟁 여부를 `possible`에서 판정해 저널을 활성화한다.
- 전쟁 수행 점수는 단일 `scripted_progress_bar`로 표시한다.
- `status_desc`를 추가하지 않는다.
- scripted button을 추가하지 않는다.
- 승전 modifier는 `eafp_modifier_joseon_qing_war_victory_unity` 하나만 쓴다.
- 패전 modifier는 `eafp_modifier_joseon_qing_war_defeat_humiliation` 하나만 쓴다.
- 전쟁 중 반복 사건에는 각각 별도의 cooldown을 둔다.

이번 개편의 핵심은 단순한 월간 사건 추첨을 "전쟁 중 선택이 누적되고, 누적된 결과가
다른 사건과 전후 정치에 영향을 주는 전쟁 상황 시스템"으로 바꾸는 것이다.

## 2. 참고한 대규모 모드

### 2.1 Cold War Project

공개 출처:

- GitHub: <https://github.com/Cold-War-Project/CWP-Main>
- Steam Workshop: <https://steamcommunity.com/sharedfiles/filedetails/?id=2941771030>

분석 파일:

- `D:/SteamLibrary/steamapps/workshop/content/529340/2941771030/common/journal_entries/CWP_korean_war.txt`
- `D:/SteamLibrary/steamapps/workshop/content/529340/2941771030/common/journal_entries/CWP_decolonization.txt`
- `D:/SteamLibrary/steamapps/workshop/content/529340/2941771030/common/script_values/korean_reunification_values.txt`
- `D:/SteamLibrary/steamapps/workshop/content/529340/2941771030/events/CWP_events/korea_events/korean_war.txt`

차용할 요소:

- `possible`을 통한 동적 저널 활성화
- `immediate`에서 상황 변수를 초기화하는 방식
- pulse마다 script value를 더한 뒤 범위를 clamp하는 방식
- 여러 국내외 조건을 하나의 script value에 합산하는 방식
- 누적 수치의 문턱값에 따라 결말 효과를 다르게 적용하는 방식
- 한 사건의 선택이나 임시 변수가 다음 사건의 조건을 바꾸는 방식

변용:

- CWP의 세계 공유 긴장도와 여러 국가용 scripted button은 사용하지 않는다.
- 조선 플레이어에게 점수 progress bar와 기간 보조 카운터를 사용한다.
- 점수는 progress bar와 평가 단계 modifier로 함께 드러낸다.
- 전쟁 개시 자체는 CWP의 일부 저널처럼 `add_journal_entry`로 처리하지 않고
  기존 합의대로 `possible`만 사용한다.

### 2.2 Morgenröte

공개 출처:

- GitHub: <https://github.com/Morgenrote-Team/Morgenroete-Beta>
- Steam Workshop: <https://steamcommunity.com/sharedfiles/filedetails/?id=2889925770>

분석 파일:

- `D:/SteamLibrary/steamapps/workshop/content/529340/2889925770/common/journal_entries/mr_science_agassiz_journal_entries.txt`
- `D:/SteamLibrary/steamapps/workshop/content/529340/2889925770/common/journal_entries/mr_general_dufour_journal_entries.txt`
- `D:/SteamLibrary/steamapps/workshop/content/529340/2889925770/events/country_or_region_specific/dufour_events.txt`
- `D:/SteamLibrary/steamapps/workshop/content/529340/2889925770/common/journal_entries/mr_arts_gaudi_journal_entries.txt`

차용할 요소:

- 높은 무발생 확률을 둔 희소한 월간 사건 풀
- 사건별 명시적 `cooldown`
- 사건 선택이 지속 변수 또는 modifier를 바꾸고 이후 사건에 반영되는 구조
- 조건을 만족하는 사건만 무작위 풀에 남기는 자연스러운 사건 필터링
- 큰 사건 사이에 작은 사건을 배치해 장기 상황의 서사를 만드는 방식

변용:

- 연구 및 건설 progress는 단일 `전쟁 수행 평가` progress bar로 바꾼다.
- 별도 부담·결속 progress bar는 도입하지 않는다.
- 사건 수를 과도하게 늘리지 않고 기존 전쟁 사건 5개를 서로 연결한다.

## 3. 핵심 메커니즘

### 3.1 단일 전쟁 수행 평가 progress bar

평가 점수는 country variable이 아니라 저널 scope의 scripted progress bar가 보유한다.

| progress bar | 초기값 | 범위 | 의미 |
| --- | ---: | ---: | --- |
| `eafp_joseon_qing_war_evaluation_progress_bar` | 60 | 0-100 | 전황, 전쟁 기간, 군수, 재정, 민심을 합친 최종 평가 |

기간 계산에는 `eafp_var_joseon_qing_war_months` country variable을 보조 카운터로
사용한다. 이 변수는 전쟁 개월 수만 세며 평가 점수를 저장하지 않는다.

progress bar 기본 정의:

```txt
eafp_joseon_qing_war_evaluation_progress_bar = {
    name = "eafp_joseon_qing_war_evaluation_progress_bar"
    desc = "eafp_joseon_qing_war_evaluation_progress_bar_desc"
    second_desc = "eafp_joseon_qing_war_evaluation_progress_bar_value"

    default_green = yes

    start_value = 60
    min_value = 0
    max_value = 100

    monthly_progress = {
        # 전쟁 기간, 점령, 전쟁 지지도, 피로도, 재정, 황폐도,
        # 급진파, 사건 modifier를 각각 desc가 있는 add 항목으로 계산
    }
}
```

저널에는 다음 한 줄을 추가한다.

```txt
scripted_progress_bar = eafp_joseon_qing_war_evaluation_progress_bar
```

월간 pulse는 progress bar 점수에 따라 평가 단계 modifier를 하나만 유지한다.

| 평가 | 활성 modifier | 체감 |
| --- | --- | --- |
| 80-100 | `eafp_modifier_joseon_qing_war_momentum` | 전황과 국내 전쟁 수행이 안정적 |
| 55-79 | `eafp_modifier_joseon_qing_war_holding` | 대가를 치르면서도 전쟁을 감당함 |
| 30-54 | `eafp_modifier_joseon_qing_war_strained_effort` | 군수·재정·민심이 흔들림 |
| 0-29 | `eafp_modifier_joseon_qing_war_exhaustion` | 전쟁 수행 체계가 붕괴 직전 |

단계가 바뀌면 이전 단계 modifier를 제거하고 새 modifier 하나만 부여한다. 저널이 끝나면
네 modifier를 모두 제거한다.

이 문서에서 이후 사용하는 `평가 N 이상/미만` 조건은 모두 country variable 비교가 아니라
저널 scope의 `"scripted_bar_progress(eafp_joseon_qing_war_evaluation_progress_bar)"`
비교를 뜻한다.

### 3.2 월간 평가 계산

`monthly_progress`에서 아래 조건을 각각 독립된 `add` 항목으로 계산한다. progress bar의
월간 갱신은 저널의 `on_monthly_pulse`보다 먼저 실행되므로, 기간 보조 카운터는 해당
월이 시작될 때까지 완료된 개월 수를 나타내도록 구간을 작성한다. 저널 pulse에서는 계산이
끝난 뒤 전쟁 개월 수를 1 올린다.

전쟁 기간:

| 전쟁 개월 수 | 월간 평가 변화 |
| --- | ---: |
| 1-6개월 | `+1` |
| 7-12개월 | `-1` |
| 13-24개월 | `-2` |
| 25개월 이상 | `-4` |

전황과 점령:

| 조건 | 월간 평가 변화 |
| --- | ---: |
| 조선의 enemy occupation이 없음, 전쟁 12개월 이하 | `+1` |
| `enemy_occupation > 0.05` | `-5` |
| `enemy_occupation > 0.20` | 추가 `-8` |
| 조청전쟁의 조선 war support가 50 이상 | `+1` |
| 조청전쟁의 조선 war support가 0 이하 | `-3` |
| 조청전쟁의 조선 war exhaustion이 50 초과 | `-3` |

재정과 국내 피해:

| 조건 | 월간 평가 변화 |
| --- | ---: |
| `in_default = yes` | `-8` |
| 금 보유고가 한도에 도달 | `+1` |
| 관료제 적자 | `-2` |
| 조선 소유 주 가운데 `devastation > 20` 존재 | `-2` |
| 조선 소유 주 가운데 `devastation > 50` 존재 | 추가 `-4` |
| 급진파 비율 20% 이상 | `-2` |

지속 modifier:

| 조건 | 월간 평가 변화 |
| --- | ---: |
| `eafp_modi_joseon_qing_war_supply_focus` 보유 | `+2` |
| `eafp_modi_joseon_qing_war_procurement_reform` 보유 | `+1` |
| `eafp_modi_joseon_qing_war_bad_shells` 보유 | `-3` |
| `eafp_var_jqw_bad_shells_coverup` 보유 | `-2` |

### 3.3 사건 선택과 평가

반복 사건은 `scope:journal_entry`에 `add_progress`를 적용해 평가 점수를 직접 올리거나
내린다. 사건의 급진파·충성파, 재정, 군사 modifier 효과는 그대로 별도 적용하되 장기
보상 판정은 progress bar 점수에 합쳐진다.

```txt
scope:journal_entry = {
    add_progress = {
        name = eafp_joseon_qing_war_evaluation_progress_bar
        value = 8
    }
}
```

- 보급, 구호, 공개적 책임, 제도 개혁: 평가 상승
- 공세 지연처럼 단기 군사 손해로 장기 피해를 막는 선택: 소폭 상승
- 강제 징발, 민간 희생, 부패 은폐, 패전 은폐: 평가 하락
- 재정이 충분한 상태에서 비용을 지불해 문제를 해결: AI 가중치와 평가 모두 유리

이 평가는 실제 승패를 대신하지 않는다. 실제 승패는 전쟁 종료와 종속 관계로 판정하고,
평가와 전쟁 기간은 같은 승전 또는 패전 안에서 결과 등급과 보상 강도를 결정한다.

## 4. 저널 생명주기

### 4.1 표시와 활성화

```txt
is_shown_when_inactive = {
    c:KOR ?= THIS
    exists = c:CHI
    has_war_with = c:CHI
}

possible = {
    c:KOR ?= THIS
    exists = c:CHI
    has_war_with = c:CHI
}
```

`is_shown_when_inactive`에도 전쟁 조건을 넣어 평시 비활성 항목이 노출되지 않게 한다.
실제 활성화 방식은 별도 effect가 아니라 `possible` 판정이다.

### 4.2 `immediate`

저널이 활성화될 때 다음 작업을 한다.

1. `c:CHI`를 `qing_enemy` scope로 저장한다.
2. 전쟁 개월 수를 0으로 초기화한다.
3. 이전 전쟁에서 남을 수 있는 평가 단계 modifier와 임시 사건 변수를 정리한다.
4. `eafp_joseon_qing_war_events.1`을 popup으로 발동한다.

초기화는 매 조청전쟁마다 실행되므로 이 저널은 일회성 업적이 아니라 각 전쟁을 독립적으로
처리할 수 있다. 평가 점수 60은 progress bar의 `start_value`에서 자동 초기화된다.

### 4.3 완료, 실패, 무효화

완료:

- 청이 존재하지 않게 됨
- 또는 조선과 청의 전쟁이 끝났고 조선이 청의 종속국이 아님

실패:

- 전쟁이 끝난 뒤 조선이 청의 종속국이 됨

무효화:

- 조선이 존재하지 않게 됨
- 청 tag가 사라졌지만 정상적인 승전 처리를 할 수 없는 예외 상황
- 저장된 적 scope가 유효하지 않은 상태에서 전쟁도 끝남

`on_complete`와 `on_fail`은 임시 사건 변수와 단계 modifier를 정리하고 각각 결말 사건
`.2`, `.3`을 호출한다. `on_invalid`는 모든 평가·기간·임시 변수를 즉시 정리한다.

완료 또는 실패 시에는 저널이 제거되기 전에
`"scripted_bar_progress(eafp_joseon_qing_war_evaluation_progress_bar)"`와 전쟁 개월
수로 결과 등급을 계산하여 `eafp_var_jqw_result_grade`에 저장한다. 점수 자체를 country
variable로 복사하지 않는다. 결말 사건은 이 등급으로 설명, 충성파·급진파, modifier
기간을 결정하고 마지막 option에서 기간·등급 변수를 정리한다.

## 5. 월간 사건 디렉터

### 5.1 발생 빈도

Morgenröte의 희소 사건 풀을 차용한다.

```txt
on_monthly_pulse = {
    effect = {
        # progress bar 월간 갱신은 이 pulse보다 먼저 처리됨
        # 전쟁 개월 수 증가, 현재 점수에 맞는 단계 modifier 교체
    }
    random_events = {
        chance_to_happen = 100
        chance_of_no_event = {
            value = 78
        }

        10 = eafp_joseon_qing_war_events.10
        10 = eafp_joseon_qing_war_events.11
        10 = eafp_joseon_qing_war_events.12
        10 = eafp_joseon_qing_war_events.13
        10 = eafp_joseon_qing_war_events.14
    }
}
```

조건을 만족하는 사건이 충분히 있을 때 월간 popup 확률은 약 22%이며, 평균적으로
4-5개월마다 한 사건이 발생한다. 사건별 cooldown과 trigger가 추가로 걸러내므로 실제
빈도는 이보다 낮다.

### 5.2 번호 정리

기존 요청에 맞춰 옛 `.11` 피난민과 군량, 옛 `.12` 의병과 상소는 제거한다. 남은 사건은
`.10` 뒤에 빈 번호가 없도록 다음과 같이 재배치한다.

| 새 번호 | 사건 |
| --- | --- |
| `.10` | 의주의 보급로 |
| `.11` | 동장군 |
| `.12` | 포탄 속의 모래 |
| `.13` | 패장의 자결 |
| `.14` | 대화재 |

## 6. 반복 사건 설계

### 6.1 `.10` 의주의 보급로

역할:

- 기본 군수 사건
- 전쟁 수행 평가를 직접 회복하는 가장 안정적인 사건

발동 조건:

- 조선과 청이 전쟁 중
- 조선이 default 상태가 아님
- 평양 또는 사리원 가운데 조선 소유 주가 존재
- 평가가 75 미만이거나 해당 주의 devastation이 10 초과

cooldown:

```txt
cooldown = { months = 8 }
```

선택:

| 선택 | 즉시 효과 | 누적 효과 |
| --- | --- | --- |
| 전선에 군량 집중 | 재정 비용, 군사 보급 bonus | 평가 `+4` |
| 지방에 추가 부담 | 해당 주 군수 bonus, 농민 급진파 | 평가 `+1` |
| 운송망부터 정비 | 단기 군사 불이익, 행정 비용 | 평가 `+7`, 조달개혁 보유 시 추가 `+2` |

연계:

- 지방 부담 선택은 `.14` 대화재의 대상 주에 지방 불만 효과를 더한다.
- 운송망 정비는 `.11` 동장군의 피해 선택지를 완화한다.

### 6.2 `.11` 동장군

역할:

- 계절과 북부 전선을 반영하는 전쟁 환경 사건

발동 조건:

- `month <= 1` 또는 `month >= 10`
- 조선과 청이 전쟁 중
- 평양 또는 사리원 가운데 조선 소유 주가 존재
- 평가 70 미만 또는 북부 주 devastation 15 초과

cooldown:

```txt
cooldown = { months = 12 }
```

선택:

| 선택 | 즉시 효과 | 누적 효과 |
| --- | --- | --- |
| 방한 물자를 우선 보급 | 재정 비용, 병력 회복 bonus | 평가 `+8` |
| 현지 징발 허용 | 북부 군수 bonus, 농민 급진파 | 평가 `+1` |
| 공세를 늦춤 | 단기 offense 불이익, 인명 손실 완화 | 평가 `+5` |

연계:

- `.10`에서 운송망 정비를 택했다면 방한 물자 비용을 줄인다.
- 현지 징발을 반복하면 직접 급진파와 낮은 평가가 함께 남아 전후 보상에 불리하다.

### 6.3 `.12` 포탄 속의 모래

역할:

- 방산비리와 군수 산업의 질을 다루는 제도 사건
- 선택에 따라 `.14` 대화재 위험을 바꾸는 핵심 연계 사건

발동 조건:

- 조선과 청이 전쟁 중
- 조선에 `building_arms_industry`가 존재
- 평가 65 미만, default, 또는 `bad_shells` 관련 임시 변수를 보유

cooldown:

```txt
cooldown = { months = 18 }
```

선택:

| 선택 | 즉시 효과 | 누적 효과 |
| --- | --- | --- |
| 관계자를 엄벌 | 권위·관료제 비용, 군부와 산업가 반발 | 평가 `+5` |
| 전쟁이 끝날 때까지 은폐 | 단기 비용 회피, 군사 불이익 | 평가 `-12`, `eafp_var_jqw_bad_shells_coverup` 18개월 |
| 군수 조달 개편 | 큰 재정 비용, 단기 생산 불이익 | 평가 `+8`, 조달개혁 modifier |

연계:

- 은폐 변수 보유 시 평가 문턱값과 무관하게 `.14` 대화재의 발동 자격을 연다.
- 조달개혁 modifier는 월간 평가를 높이고 다음 `.12`의 발동 조건을 강화한다.

### 6.4 `.13` 패장의 자결

역할:

- 실제 불리한 전황에서만 등장하는 군 지휘부 책임 사건
- 군인의 충성과 군제 개혁 사이의 정치적 선택을 만든다.

발동 조건:

- 조선과 청이 전쟁 중
- 조선 장군이 존재
- 다음 중 하나를 만족:
  - 평가 35 이하
  - `enemy_occupation > 0.10`
  - 조청전쟁에서 조선의 war exhaustion이 35 초과

cooldown:

```txt
cooldown = { months = 24 }
```

선택:

| 선택 | 장군 처리 | 누적 효과 |
| --- | --- | --- |
| 충절을 기려 기록 | 장군 사망 | 평가 `+2`, 보수 정치운동 attraction 증가 |
| 죽음보다 책임을 묻는다 | 장군 생존, 인기 하락 | 평가 `+7`, 군제개혁 압력 |
| 패전을 은폐 | 장군 생존 | 평가 `-10`, 정치운동 radicalism 증가 |

구현 주의:

- 현재처럼 아무 전황 조건 없이 무작위 장군을 죽이지 않는다.
- 저장한 `defeated_general` scope가 option 실행 시에도 유효한지 확인한다.
- AI는 평가가 낮고 재정이 나쁠수록 군제개혁 선택의 가중치를 높인다.

### 6.5 `.14` 대화재

역할:

- 전쟁 피해, 부실 포탄, 군수창 우선주의가 민간 피해로 돌아오는 연계 사건

발동 조건:

- 조선과 청이 전쟁 중
- 조선 소유 주 가운데 devastation 10 초과인 주가 존재
- 다음 중 하나를 만족:
  - 평가 55 미만
  - `eafp_var_jqw_bad_shells_coverup` 보유
  - 북부 주 enemy occupation 발생

cooldown:

```txt
cooldown = { months = 18 }
```

대상 주 선택:

- devastation이 높은 주를 우선한다.
- arms industry, barracks, naval base가 있는 주의 가중치를 높인다.
- 은폐 변수가 있으면 해당 군수 산업 소재 주를 우선한다.

선택:

| 선택 | 즉시 효과 | 누적 효과 |
| --- | --- | --- |
| 구호와 진화를 우선 | 재정 비용, 해당 주 충성파 | 평가 `+8` |
| 군수창을 먼저 지킴 | 군사 bonus, 민간 급진파 | 평가 `-4` |
| 책임자를 처벌 | 권위·관료제 비용, 정치운동 안정 | 평가 `+4` |

연계:

- 부실 포탄 은폐 뒤 발생했다면 사건 설명을 별도 triggered desc로 바꾼다.
- 구호 우선 선택은 은폐 변수를 제거하지 않는다. 은폐의 정치적 책임은 전후까지 남긴다.

## 7. 전후 결말

### 7.1 승전

승전 시 사용하는 modifier key는 하나뿐이다.

```txt
eafp_modifier_joseon_qing_war_victory_unity
```

modifier의 기본 방향:

- `state_radicals_from_political_movements_mult` 감소
- `state_loyalists_from_political_movements_mult` 증가
- `political_movement_radicalism_add` 감소
- 위신과 정통성 증가

평가와 전쟁 기간에 따라 같은 modifier의 기간과 즉시 pop 효과만 바꾼다.

| 승전 등급 | 조건 | 즉시 효과 | modifier 기간 |
| --- | --- | --- | --- |
| 압도적 승리 | 평가 80 이상, 12개월 이내 | 대규모 충성파 | 6년 |
| 값비싼 승리 | 평가 65 이상, 24개월 이내 | 중간 규모 충성파 | 5년 |
| 피로스의 승리 | 평가 40 이상, 36개월 이내 | 소규모 충성파 | 4년 |
| 상처뿐인 승리 | 그 외 | 소규모 급진파, 위신 상승은 유지 | 3년 |

따라서 군사적으로 이겼더라도 민생을 소모하고 패전을 은폐한 국가는 완전한 국민 통합을
얻지 못한다. 장기전은 평가를 매달 낮추는 동시에 최상위 등급의 기간 제한에도 걸리므로
빠르고 안정적인 승리가 가장 큰 보상을 받는다. 별도의 개혁파·보수파 승전 modifier는
만들지 않는다.

### 7.2 패전

패전 시 사용하는 modifier key도 하나뿐이다.

```txt
eafp_modifier_joseon_qing_war_defeat_humiliation
```

modifier의 기본 방향:

- `state_radicals_from_political_movements_mult` 증가
- `state_loyalists_from_political_movements_mult` 감소
- `political_movement_radicalism_add` 증가
- 위신과 정통성 감소

| 패전 등급 | 조건 | 즉시 효과 | modifier 기간 |
| --- | --- | --- | --- |
| 질서 있는 수습 | 평가 70 이상, 24개월 이내 | 소규모 급진파 | 3년 |
| 굴욕적 패전 | 평가 45 이상, 36개월 이내 | 중간 규모 급진파 | 4년 |
| 국정 붕괴 | 평가 20 이상, 36개월 이내 | 대규모 급진파 | 5년 |
| 파국 | 그 외 | 최대 규모 급진파 | 6년 |

전쟁 수행 평가가 높았던 국가는 패배해도 충격을 더 짧게 수습할 수 있다. 반대로 장기전
끝에 패배하면 평가가 남아 있더라도 `파국`으로 처리한다. 패전 modifier 자체는 다른
이름으로 분리하지 않는다.

## 8. AI 선택 원칙

고정 `base`만 두지 않고 현재 상태를 가중치에 반영한다.

- 평가 35 미만: 평가를 즉시 회복하는 선택 선호
- 전쟁 12개월 초과: 보급, 구호, 공개 책임, 공세 지연 선택 선호
- default 상태: 재정 지출 선택 비선호
- 높은 군사 임금과 충분한 금 보유고: 보급·방한 물자·조달 개혁 선호
- 높은 정치운동 radicalism: 은폐와 강제 징발 비선호
- 청보다 군사력이 현저히 약함: 공세 지연과 군제 개혁 선호

AI 가중치는 사건의 서사를 보존하되, 파산 중인 AI가 매번 가장 비싼 선택을 골라 스스로
붕괴하는 상황을 피하도록 한다.

## 9. 파일 작업 계획

1. `common/journal_entries/eafp_joseon_qing_war.txt`
   - `possible` 활성화 방식 유지
   - 평가 progress bar 연결
   - 전쟁 개월 수 초기화 및 월간 증가 추가
   - 사건 풀을 `.10`-`.14`로 정리
   - 완료, 실패, 무효화 cleanup 추가

2. `common/scripted_progress_bars/eafp_joseon_qing_war_progress_bars.txt`
   - `eafp_joseon_qing_war_evaluation_progress_bar`
   - `start_value = 60`, `min_value = 0`, `max_value = 100`
   - 기간, 전황, 재정, 국내 피해, 사건 modifier별 `monthly_progress.add` 항목

3. `events/eafp_kor_events/eafp_joseon_qing_war_events.txt`
   - 옛 `.11`, `.12` 제거
   - 동장군 이하 사건을 `.11`-`.14`로 재번호
   - 사건별 trigger, cooldown, `add_progress`, AI 가중치 개편

4. `common/static_modifiers/eafp_joseon_qing_war_modifiers.txt`
   - 전쟁 수행 평가 단계 modifier 4종 추가
   - 기존 승전·패전 단일 modifier 유지
   - 반복 사건 modifier의 중복과 지속 시간을 정리

5. 한국어, 영어, 중국어 간체 localization
   - 변경된 사건 번호 반영
   - progress bar 이름, 설명, 현재 점수 text 추가
   - 월간 점수 변동 원인별 desc 추가
   - 전쟁 수행 평가 단계 modifier 이름 추가
   - 선택 결과에 평가 변화 tooltip 추가
   - `.14` 대화재의 은폐 연계 설명 추가

## 10. 검증 항목

- `add_journal_entry`, `status_desc`, scripted button이 들어가지 않았는지 검색
- 평가 점수를 저장하는 country variable이 실제 구현 파일에 남지 않았는지 검색
- 저널에 평가 progress bar가 정확히 한 번 연결되는지 확인
- progress bar가 60에서 시작하고 0-100 범위를 유지하는지 확인
- 반복 사건 ID가 `.10`, `.11`, `.12`, `.13`, `.14`로 연속되는지 확인
- 모든 반복 사건에 cooldown이 있는지 확인
- `month` 조건으로 동장군이 11월부터 2월 사이에만 발동하는지 확인
- 사건이 발동하지 않은 달에도 전쟁 개월 수와 progress bar 계산이 실행되는지 확인
- progress bar 월간 갱신이 저널 pulse보다 먼저 실행되는 순서가 기간 계산과 일치하는지 확인
- 전쟁 6, 12, 24, 36개월 경계에서 기간 보정이 의도대로 바뀌는지 확인
- 승전·패전 직전에 progress bar 점수로 결과 등급이 올바르게 snapshot되는지 확인
- 승전·패전·무효화 뒤 개월 수, 등급, 임시 변수, 단계 modifier가 남지 않는지 확인
- 같은 save에서 두 번째 조청전쟁이 발생했을 때 변수가 정상 초기화되는지 확인
- 부실 포탄 은폐가 대화재 조건과 설명에 반영되는지 확인
- 같은 승전·패전에서도 평가와 기간 조합에 따라 보상 등급이 달라지는지 확인
- 승전과 패전이 각각 단일 modifier key만 사용하는지 확인
- 한국어, 영어, 중국어 간체 localization key가 모두 존재하는지 확인

## 11. 기대되는 플레이 흐름

1. 조선과 청이 전쟁에 들어가면 저널이 자동 활성화된다.
2. 전쟁 초기에는 빠른 승리를 위한 평가 bonus가 있지만 장기화될수록 월간 감점이 커진다.
3. 4-6개월 간격으로 현재 상황에 맞는 사건이 발생한다.
4. 점령, devastation, 전쟁 지지도, war exhaustion, default, 재정과 사건 선택이 하나의 평가를 바꾼다.
5. 한 사건의 선택이 다른 사건의 조건과 설명을 바꾼다.
6. 실제 전쟁 결과가 승패를 결정하고, 최종 평가와 전쟁 기간이 전후 보상 등급을 결정한다.

이 구조는 전쟁 결과를 임의 수치로 대체하지 않으면서도, 플레이어가 전쟁 중 내린 선택이
전후 급진파·충성파 정치에 남도록 만든다.
