# 조선-청 전쟁 저널 메커니즘 개편 설계안

## 1. 설계 범위

이 문서는 조선(`KOR`)과 청(`CHI`)이 양측 전쟁 지도자이며 조선 독립이 전쟁 목표인 전쟁에서 활성화되는
`je_eafp_joseon_qing_war`의 개편안을 다룬다.

기존 합의 사항은 그대로 유지한다.

- 껍데기 저널을 만들지 않는다.
- `add_journal_entry`를 사용하지 않는다.
- 실제 전쟁 여부를 `possible`에서 판정해 저널을 활성화한다.
- 전쟁 수행 점수는 단일 `scripted_progress_bar`로 표시한다.
- `status_desc`를 추가하지 않는다.
- scripted button을 추가하지 않는다.
- 승전 modifier는 전쟁 지지 구간에 따라 대승리, 값비싼 승리, 상처뿐인 승리로 나눈다.
- 패전 modifier는 `eafp_modifier_joseon_qing_war_defeat` 하나를 쓴다.

이번 개편의 핵심은 실제 전쟁 지지를 추적하고 종전 시점의 수치에 따라 전후 정치의 결과를
달리하는 전쟁 상황 시스템을 만드는 것이다.

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
- 점수는 progress bar로만 드러낸다.
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

전쟁 상황 판단에는 저널의 주간 pulse에서 갱신하는
`eafp_var_jqw_current_war_support` country variable을 사용한다.

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

이 문서에서 이후 사용하는 `평가 N 이상/미만` 조건은 모두 country variable 비교가 아니라
저널 scope의 `"scripted_bar_progress(eafp_joseon_qing_war_evaluation_progress_bar)"`
비교를 뜻한다.

### 3.2 월간 평가 계산

저널의 `on_weekly_pulse`에서 저장한 전쟁 scope를 통해 조선의 현재 전쟁 지지를 읽고,
`eafp_var_jqw_current_war_support`에 갱신한다. 저널 표시와 종전 분기는 이 주간 snapshot을
사용한다.

전황과 점령:

| 조건 | 월간 평가 변화 |
| --- | ---: |
| 조선의 enemy occupation이 없음, 전쟁 지지 50 이상 | `+1` |
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

실제 승패는 전쟁 종료와 종속 관계로 판정한다. 승전은 종전 당시 전쟁 지지에 따라 세
결말로 나뉘지만, 패전은 전쟁 지지와 무관하게 하나의 결말과 보상 강도를 사용한다.

## 4. 저널 생명주기

### 4.1 표시와 활성화

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

`is_shown_when_inactive`는 청의 종속국인 동안 항목을 노출한다. `possible`의 전용 trigger는
조선과 청이 모두 전쟁 지도자이고 조선이 청을 대상으로 `independence` 전쟁 목표를 가진
경우에만 저널을 활성화하며, 외교전 유형 자체는 제한하지 않는다.

### 4.2 `immediate`

저널이 활성화될 때 다음 작업을 한다.

1. `c:CHI`를 `qing_enemy` scope로 저장한다.
2. 이전 전쟁에서 남은 현재 전쟁 지지 snapshot을 제거한다.
3. 양국이 전쟁 지도자이며 조선 독립 목표가 있는 전쟁을 `joseon_qing_war` scope로 저장한다.
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

`on_complete`와 `on_fail`은 현재 전쟁 지지를 정리하고 각각 결말 사건 `.2`, `.3`을 호출한다.
`on_invalid`도 현재 전쟁 지지를 즉시 정리한다.

저널의 주간 pulse는 저장된 전쟁 scope에서 조선의 전쟁 지지를
`eafp_var_jqw_current_war_support`에 갱신한다. 완료 또는 실패 시 결말 사건은 이 변수를
확인한다. 전쟁 지지 50 이상, 0 이상 50 미만, 0 미만의 세 구간에 따라 설명,
충성파·급진파, modifier 종류와 기간을 결정한다. 저장된 전쟁 scope가 끝나면 조선이 청의
종속국인지 여부로 완료와 실패를 직접 판정하며, 별도의 결과·등급 변수를 만들지 않는다.

## 7. 전후 결말

### 7.1 승전

승전 시 전쟁 지지 구간에 맞는 modifier key를 각각 사용한다.

```txt
eafp_modifier_joseon_qing_war_great_victory
eafp_modifier_joseon_qing_war_costly_victory
eafp_modifier_joseon_qing_war_pyrrhic_victory
```

modifier의 기본 방향:

- 대승리: 정치운동의 급진파 억제와 충성파 증가, 위신과 정통성의 큰 상승
- 값비싼 승리: 대승리보다 완화된 정치적 결속과 위신·정통성 상승
- 상처뿐인 승리: 제한된 위신·정통성 상승과 함께 정치적 후유증 발생

| 승전 등급 | 조건 | modifier | 즉시 효과 | 기간 |
| --- | --- | --- | --- | --- |
| 대승리 | 전쟁 지지 50 이상 | `eafp_modifier_joseon_qing_war_great_victory` | 대규모 충성파 | 6년 |
| 값비싼 승리 | 전쟁 지지 0 이상 50 미만 | `eafp_modifier_joseon_qing_war_costly_victory` | 소규모 충성파 | 4년 |
| 상처뿐인 승리 | 전쟁 지지 0 미만 | `eafp_modifier_joseon_qing_war_pyrrhic_victory` | 소규모 급진파 | 2년 |

### 7.2 패전

패전 시 사용하는 modifier key도 하나뿐이다.

```txt
eafp_modifier_joseon_qing_war_defeat
```

modifier의 기본 방향:

- `state_radicals_from_political_movements_mult` 증가
- `state_loyalists_from_political_movements_mult` 감소
- `political_movement_radicalism_add` 증가
- 위신과 정통성 감소

| 패전 결말 | 조건 | 즉시 효과 | modifier 기간 |
| --- | --- | --- | --- |
| 굴욕적 패전 | 전쟁 지지와 무관 | 중간 규모 급진파 | 4년 |

패전은 전쟁 지지나 전쟁 기간에 따라 나누지 않으며, 단일 설명과 단일 modifier key를
사용한다.

## 9. 파일 작업 계획

1. `common/journal_entries/eafp_joseon_qing_war.txt`
   - `possible` 활성화 방식 유지
   - 평가 progress bar 연결
   - 현재 전쟁 지지의 주간 snapshot 갱신
   - 완료, 실패, 무효화 cleanup 추가

2. `common/scripted_progress_bars/eafp_joseon_qing_war_progress_bars.txt`
   - `eafp_joseon_qing_war_evaluation_progress_bar`
   - `start_value = 60`, `min_value = 0`, `max_value = 100`
   - 기간, 전황, 재정, 국내 피해, 사건 modifier별 `monthly_progress.add` 항목

3. `events/eafp_kor_events/eafp_joseon_qing_war_events.txt`
   - 개전, 승전, 패전 사건과 종전 효과 구현

4. `common/static_modifiers/eafp_joseon_qing_war_modifiers.txt`
   - 기존 승전·패전 단일 modifier 유지

5. 한국어, 영어, 중국어 간체 localization
   - progress bar 이름, 설명, 현재 점수 text 추가
   - 월간 점수 변동 원인별 desc 추가
   - 선택 결과에 평가 변화 tooltip 추가

## 10. 검증 항목

- `add_journal_entry`, `status_desc`, scripted button이 들어가지 않았는지 검색
- 평가 점수를 저장하는 country variable이 실제 구현 파일에 남지 않았는지 검색
- 주간 전쟁 지지 변수가 실제 전쟁 지지와 일치하고 status text에 표시되는지 확인
- 승전 시 전쟁 지지 50 이상, 0 이상 50 미만, 0 미만의 결말이 올바르게 선택되는지 확인
- 패전 시 전쟁 지지와 무관하게 단일 설명과 고정 효과가 적용되는지 확인
- 승전·패전·무효화 뒤 현재 전쟁 지지 변수와 임시 변수가 남지 않는지 확인
- 같은 save에서 두 번째 조청전쟁이 발생했을 때 변수가 정상 초기화되는지 확인
- 승전과 패전이 각각 단일 modifier key만 사용하는지 확인
- 한국어, 영어, 중국어 간체 localization key가 모두 존재하는지 확인

## 11. 기대되는 플레이 흐름

1. 조선과 청이 전쟁에 들어가면 저널이 자동 활성화된다.
2. 주간마다 현재 전쟁 지지가 저널에 갱신된다.
3. 실제 전쟁 결과가 승패를 결정하고, 승전 시 현재 전쟁 지지가 전후 보상 등급을 결정한다.

이 구조는 전쟁 결과를 임의 수치로 대체하지 않으면서도 전쟁 지지에 따른 전후
급진파·충성파 정치의 차이를 남긴다.
