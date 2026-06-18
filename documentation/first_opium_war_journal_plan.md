# 1차 아편전쟁 강제 저널 설계안

## 목표

청나라 게임 초반의 아편전쟁을 바닐라의 일반 `opium_wars` 체인에 맡기지 않고, 청나라 전용 관리 저널이 시간 흐름에 따라 아편 논쟁, 임칙서 파견, 영국과의 충돌, 전쟁 강제, 전후 처리를 순서대로 통제하게 만든다.

핵심 목표는 다음과 같다.

- 게임 초반 영국 대 청나라 상황에서 바닐라 `je_opium_obsession` / `je_opium_wars`가 먼저 뜨지 않게 막는다.
- 청나라에는 새 관리 저널 `je_qing_opium_obsession`을 띄운다.
- 새 저널은 `scripted_progress_bar`를 사용해 시간 진행을 관리한다.
- 저널은 청나라 히스토리에서 직접 추가해 1836년 시작 시점부터 확정적으로 열린다.
- `opium_wars_start_var`를 시작 시점에 설정하고, `opium_wars.1`에서 해당 변수를 가진 청나라는 제외한다.
- 새 저널은 1836년부터 일정한 사건 체인을 진행해 1839년 전후로 아편 금지 논쟁을 결론낸다.
- 엄금론 선택 시 영국과의 1차 아편전쟁을 사실상 강제한다.
- 이금론 선택 시 전쟁은 피할 수 있지만 큰 내부 비용과 이후 서구 압력의 다른 경로를 남긴다.
- 바닐라 아편전쟁의 기존 변수와 결말 이벤트를 최대한 재사용하고, 신규 전용 변수는 가능한 한 만들지 않는다.

## 현재 코드 상태

이미 존재하는 관련 파일:

- `common/journal_entries/eafp_00_opium_wars.txt`
  - 바닐라 `je_opium_wars`를 `REPLACE`하고 있다.
  - 영국이 청나라를 상대로 `je_opium_wars`를 완료했을 때 조선 및 타국 반응 이벤트를 추가한 상태다.
- `events/opium_wars_events.txt`
  - 바닐라 `opium_wars.1`부터 `.8`까지를 사실상 덮어쓰고 있다.
  - `opium_wars.2` 뒤에 `opium_wars.101`~`.103` 회피 방지 이벤트가 추가되어 있다.
  - 현재 구조에서는 바닐라 `opium_wars.1`이 청나라에 뜬 뒤 `opium_wars.2`가 영국 `je_opium_wars`를 열 수 있다.
- `common/journal_entries/eafp_qing_opium_wars.disable`
  - 청나라 전용 `je_qing_opium_obsession` 초안이 있다.
  - `first_opium_war.1`, `.6`, `.7`, `.8`, `.9`를 사용하도록 되어 있다.
- `events/eafp_chi_events/eafp_first_opium_war_events.disable`
  - `first_opium_war` 네임스페이스 초안이 있다.
  - `.1`, `.6`, `.7`, `.8`은 구현되어 있으나, 로컬라이제이션에 있는 `.2`, `.3`, `.4`, `.9`는 이벤트 구현이 아직 없다.
- `localization/*/eafp_china_l_*.yml`
  - `je_qing_opium_obsession` 및 `first_opium_war.1`~`.4`, `.6`~`.9` 로컬라이제이션 일부가 이미 들어 있다.
- `common/diplomatic_plays/eafp_diplomatic_plays.txt`
  - `dp_first_opium_war`가 이미 정의되어 있다.
  - 현재는 렌즈 선택 불가, 영국 대 청나라 전용 강제 플레이용으로 쓰기 좋다.

## 전체 구조

### 저널

메인 관리 저널은 `je_qing_opium_obsession`을 사용한다.

역할:

- 청나라 전용 초반 역사 저널.
- 실제 진행도는 `scripted_progress_bar`로 표시한다.
- 월간 펄스에서 논쟁 이벤트와 중독/밀수 이벤트를 섞어 발생시킨다.
- 타임아웃 또는 특정 단계 도달 시 `first_opium_war.9`를 발동해 황제의 결단을 요구한다.
- 결단 결과에 따라 전쟁 강제 루트 또는 이금론 루트로 종료한다.

권장 위치:

- `common/journal_entries/eafp_qing_opium_wars.txt`
  - 기존 `.disable` 파일을 그대로 활성화하지 말고, 설계에 맞게 정리한 새 파일로 전환한다.

권장 기본값:

- `group = je_group_qing`
- `icon = gfx/interface/icons/event_icons/event_military.dds`
- `timeout = 1095` 또는 `1460`
  - 3~4년 사이에 황제 결단까지 도달.
- `scripted_progress_bar = eafp_first_opium_war_debate_progress_bar`
  - 저널의 시간 진행, 단계 이벤트, 결단 조건은 이 바를 단일 기준으로 삼는다.
- `is_shown_when_inactive`
  - `THIS = c:CHI`
  - `game_date < 1841`
  - `NOT = { has_variable = opium_wars_won }`
  - `NOT = { has_variable = opium_wars_gave_in }`
  - `NOT = { has_variable = lost_opium_wars }`
  - `NOT = { has_modifier = opium_wars_lost }`
- `possible`
  - 청나라가 존재하고 독립국일 것.
  - `c:GBR` 존재.
  - 이미 영국과 전쟁 중이거나 휴전 중이면 시작하지 않거나, 별도 복구 이벤트로 처리.

### 바닐라 체인 차단

바닐라 자동 아편전쟁은 `events/opium_wars_events.txt`의 `opium_wars.1`에서 시작한다.

차단 방식:

- 새 저널 시작 시 청나라에 `opium_wars_start_var`를 설정한다.
- `opium_wars.1` 트리거에서 `opium_wars_start_var`를 가진 청나라는 제외한다.

예상 조건:

```txt
NOT = {
    AND = {
        THIS = c:CHI
        has_variable = opium_wars_start_var
    }
}
```

효과:

- 청나라 초반에는 바닐라 `je_opium_obsession`이 열리지 않는다.
- 따라서 영국에 바닐라 `je_opium_wars`도 자동으로 열리지 않는다.
- `opium_wars_start_var`는 바닐라 자동 시작 차단용으로 남겨둔다.

주의:

- `opium_wars.1` 전체를 막으면 다른 비인정국 아편전쟁 체인까지 죽을 수 있으므로 청나라만 예외 처리한다.
- 이미 있는 `je_opium_wars` `REPLACE`는 전후 타국 반응 때문에 유지한다.

## 시간 흐름

### 1단계: 1836년 시작, 아편 위기

시작 조건:

- 청나라 히스토리에서 `je_qing_opium_obsession`을 직접 추가한다.
- 대상 파일은 `common/history/countries/chi - china.txt`다.
- 월간 온액션으로 여는 방식은 쓰지 않는다.

초기 효과:

- `set_variable = opium_wars_start_var`
  - 바닐라 `opium_wars.1`의 청나라 발동 차단용.
- `set_variable = opium_wars_target`
  - 바닐라 후속 이벤트/툴팁 호환용. 이 변수는 청나라에 둔다.
- `add_modifier = { name = opium_wars_addiction_modifier days = long_modifier_time }`
- 한족 문화에 아편 집착이 없다면 `cu:han = { add_cultural_obsession = opium }` 검토.

즉시 발동 이벤트:

- `first_opium_war.1`: 아편 위기 시작 알림.
- `eafp_first_opium_war_debate_progress_bar`는 저널 생성 시 `start_value`에서 시작한다.

### Scripted Progress Bar

파일:

- `common/scripted_progress_bars/eafp_first_opium_war_progress_bars.txt`

진행도:

- `eafp_first_opium_war_debate_progress_bar`
- `start_value = 0`
- `min_value = 0`
- `max_value = 100`
- `default = yes`
- `monthly_progress`에서 기본 +3을 준다.
- 36개월 전후에 결단으로 넘어가도록 `100` 도달을 목표로 한다.

진행도 원칙:

- 논쟁 단계 이벤트는 전용 변수가 아니라 이 progress bar의 수치 구간으로 판단한다.
- 한번만 떠야 하는 이벤트는 이벤트 자체의 `cooldown = { days = stupidly_long_modifier_time }` 또는 국가 모디파이어로 중복을 막는다.
- 저널은 `scripted_bar_progress(eafp_first_opium_war_debate_progress_bar)`가 100에 도달하면 `first_opium_war.9`를 발동한다.

### 2단계: 1836-1838년, 조정 논쟁

월간 펄스:

- `scripted_progress_bar`가 매월 진행된다.
- 진행도 임계값에 따라 논쟁 사건을 발생시킨다.

권장 사건:

- `first_opium_war.2`: 허내제의 상소, 이금론 제기. 진행도 20 이상.
- `first_opium_war.3`: 원옥린의 반박, 엄금론 강화. 진행도 45 이상.
- `first_opium_war.4`: 허구의 상소, 이금론 모순 지적. 진행도 70 이상.

각 사건 효과:

- 선택지는 하나만 둬도 된다. 이 저널은 플레이어 선택형 정책 저널이라기보다 시간 관리 저널이다.
- 사건마다 별도 여론 변수를 쌓지 않는다.
- 필요하면 짧은 기간의 모디파이어로만 분위기를 표현한다.
- 선택지를 둘 경우에도 AI는 역사적 엄금론으로 강하게 유도한다.

월간 랜덤 사건:

- 기존 초안의 `first_opium_war.6`, `.7`, `.8`을 사용한다.
- 단, 이 사건들은 scripted progress bar를 직접 바꾸지 않고 분위기와 피해를 표현하는 보조 사건으로 둔다.

### 3단계: 1839년 전후, 황제의 결단

발동 조건:

- 저널 타임아웃.
- 또는 `scripted_bar_progress(eafp_first_opium_war_debate_progress_bar) >= 100`.
- 또는 `game_date >= 1839.1.1`이고 progress bar가 충분히 진행된 상태.

이벤트:

- `first_opium_war.9`: 황제의 결단.

선택 A: 엄금론

- 임칙서 파견.
- 아편 금지 강화.
- 영국과 관계 악화.
- 영국 `je_opium_wars` 또는 강제 외교전으로 이어질 상태를 만든다.

권장 효과:

```txt
add_banned_goods = g:opium
c:GBR = {
    set_variable = opium_wars_aggressor
    change_relations = { country = c:CHI value = -50 }
}
trigger_event = { id = first_opium_war.10 days = { 30 90 } }
```

선택 B: 이금론

- 전쟁 강제 루트는 종료.
- 큰 정통성/권위/급진파/천명 피해를 부여한다.
- 이후 서구 압력과 내부 혼란은 `opium_wars_gave_in` 및 장기 모디파이어로 표현한다.

권장 효과:

```txt
set_variable = opium_wars_gave_in
add_modifier = {
    name = eafp_legalized_opium_shame
    days = very_long_modifier_time
}
add_radicals = { value = large_radicals }
```

추가 고려:

- 이금론을 선택해도 `opium_wars_gave_in`을 세팅하면 바닐라 AI/정치 전략과 호환된다.
- 청나라 전용 후속 콘텐츠도 가능하면 `opium_wars_gave_in`을 기준으로 분기한다.

### 4단계: 엄금론 후 충돌 고조

새 이벤트 후보:

- `first_opium_war.10`: 임칙서 광동 도착.
- `first_opium_war.11`: 호문소연 / 외국 상인의 반발.
- `first_opium_war.12`: 영국의 최후통첩.
- `first_opium_war.13`: 전쟁 개시.

역할:

- 엄금론을 선택한 뒤 바로 전쟁을 걸기보다 1~3개월 간격으로 사건을 보여준다.
- 플레이어에게 "이제 전쟁이 온다"는 신호를 준다.
- 영국이 존재하고 전쟁/휴전 중이 아니라면 강제 외교전을 시작한다.

영국 전쟁 강제 방식:

1. 가능하면 `dp_first_opium_war`를 사용한다.
2. 외교전 시작 효과가 불안정하면 바닐라 `je_opium_wars`를 영국에 추가하고, 기존 `opium_wars.101`~`.103` 회피 방지 이벤트를 보조로 둔다.

권장 구조:

```txt
c:GBR = {
    save_scope_as = opium_wars_aggressor_country
    set_variable = opium_wars_aggressor
    add_journal_entry = {
        type = je_opium_wars
        target = c:CHI
    }
}
c:CHI = {
    set_variable = opium_wars_target
}
```

그 뒤 강제 전쟁은 다음 둘 중 하나로 구현한다.

- `dp_first_opium_war` 시작 효과를 확인해 직접 외교전을 연다.
- 또는 영국 AI가 `je_opium_wars`를 통해 treaty port / free trade / investment rights를 요구하도록 유도하고, 휴전 회피는 기존 `opium_wars.101`~`.103`가 막는다.

## 완료와 실패

### 엄금론 루트 완료

청나라가 승리하거나 영국이 요구를 달성하지 못하면:

- `opium_wars.3` 또는 청나라 전용 승리 이벤트로 처리.
- `opium_wars_won` 설정.
- `opium_wars_addiction_modifier` 제거.
- 아편 집착 제거.
- `chi_add_1_fragile_unity`는 현재 모드에서 제거된 흐름과 충돌할 수 있으므로 사용하지 않는다.

### 엄금론 루트 실패

영국이 다음 중 하나를 달성하면 실패:

- 청나라가 자유무역 채택.
- 영국이 조약항 획득.
- 영국이 투자권 등 조약권 획득.

처리:

- 기존 `opium_wars.4`와 `opium_wars.5`를 최대한 재사용한다.
- `lost_opium_wars` 설정.
- `opium_wars_lost` 모디파이어 부여.
- 이후 태평천국, 중국 선교, 2차 아편전쟁 조건이 정상적으로 이어지게 한다.

### 이금론 루트 종료

전쟁은 피하지만 "성공"으로 보지 않는다.

처리:

- `opium_wars_gave_in` 설정.
- 청나라 내부 불안정, 정통성, 권위, 조세/무역 관련 장기 모디파이어 부여.
- 2차 아편전쟁/서구 압력 콘텐츠가 너무 일찍 막히지 않도록 `lost_opium_wars`는 부여하지 않는다.

## 필요한 파일 작업

### 1. 저널

파일:

- `common/journal_entries/eafp_qing_opium_wars.txt`

작업:

- `.disable` 초안을 기반으로 `je_qing_opium_obsession` 재작성.
- `scripted_progress_bar = eafp_first_opium_war_debate_progress_bar`를 사용한다.
- `current_value` / `goal_add_value` 방식은 쓰지 않는다.
- `on_monthly_pulse`에서 단계 이벤트와 보조 이벤트 호출.
- `on_timeout`에서 `first_opium_war.9` 호출.
- 완료/무효 조건에 `opium_wars_won`, `opium_wars_gave_in`, `lost_opium_wars`, 청나라 소멸, 영국 소멸, 이미 전쟁 중인 예외를 반영.

### 2. Scripted Progress Bar

파일:

- `common/scripted_progress_bars/eafp_first_opium_war_progress_bars.txt`

작업:

- `eafp_first_opium_war_debate_progress_bar` 추가.
- 월간 기본 진행과 reason localization 추가.
- 결단 임계값은 100으로 둔다.
- 이벤트 단계는 progress bar 구간으로만 판정한다.

### 3. 이벤트

파일:

- `events/eafp_chi_events/eafp_first_opium_war_events.txt`

작업:

- `.disable` 초안을 활성 파일로 전환.
- 이미 있는 `.1`, `.6`, `.7`, `.8` 정리.
- 로컬라이제이션만 있고 구현이 없는 `.2`, `.3`, `.4`, `.9` 추가.
- 엄금론 이후 `.10`~`.13` 신규 이벤트 추가.

### 4. 바닐라 아편전쟁 덮어쓰기

파일:

- `events/opium_wars_events.txt`

작업:

- `opium_wars.1` 트리거에 `opium_wars_start_var`를 가진 청나라 예외 추가.
- `opium_wars.2`는 일반국용으로 유지하되, 청나라 전용 체인이 영국 `je_opium_wars`를 열 때 필요한 변수와 호환되도록 둔다.
- 기존 `opium_wars.101`~`.103`은 유지. 다만 새 체인에서는 발동 시점을 `first_opium_war.13` 이후로 조정할 수 있다.

### 5. 시작 조건

파일 후보:

- `common/history/countries/chi - china.txt`
- 또는 `common/on_actions/china_code_on_actions.txt`

권장:

- 역사 파일에서 게임 시작 시 `add_journal_entry = { type = je_qing_opium_obsession }` 추가.
- 같은 시작 블록에서 `set_variable = opium_wars_start_var`도 설정한다.

이유:

- 가장 예측 가능하다.
- 청나라 시작 콘텐츠임이 명확하다.
- 월간 온액션으로 뒤늦게 여는 것보다 바닐라 `opium_wars.1`보다 먼저 상태를 고정하기 쉽다.

### 6. 로컬라이제이션

파일:

- `localization/korean/eafp_china_l_korean.yml`
- `localization/english/eafp_china_l_english.yml`
- `localization/simp_chinese/eafp_china_l_simp_chinese.yml`

작업:

- 현재 있는 키를 재사용한다.
- 새 이벤트 `.10`~`.13` 키 추가.
- 저널 진행도/완료/실패/툴팁 키 추가.
- scripted progress bar 이름과 월간 진행 사유 키 추가.
- `je_qing_opium_obsession_status`는 현재 단계를 표시하도록 커스텀 로컬라이제이션을 붙일 수 있다.

### 7. 모디파이어

파일 후보:

- `common/static_modifiers/eafp_chi_modifiers.txt`

추가 후보:

- `eafp_legalized_opium_shame`
- `eafp_strict_opium_prohibition`
- `eafp_linxexu_in_guangdong`
- `eafp_opium_crisis_unrest`

주의:

- 이미 바닐라의 `opium_wars_addiction_modifier`, `opium_wars_lost`, `opium_ban_authority`가 있으므로 중복되는 장기 효과는 최소화한다.

## 변수 설계

원칙:

- 신규 전용 변수는 가능한 한 쓰지 않는다.
- 시간 진행은 `eafp_first_opium_war_debate_progress_bar`가 담당한다.
- 단계 이벤트 중복 방지는 이벤트 `cooldown` 또는 짧은 모디파이어로 처리한다.
- 후속 콘텐츠 분기는 바닐라 호환 변수와 모디파이어를 우선 사용한다.

바닐라 호환 변수:

- `opium_wars_start_var`
- `opium_wars_target`
- `opium_wars_aggressor`
- `opium_wars_won`
- `opium_wars_gave_in`
- `lost_opium_wars`

신규 전용 변수:

- 기본 설계에서는 만들지 않는다.
- 꼭 필요할 때만 1개 정도의 영구 완료 변수 대신 바닐라 변수 조합을 먼저 검토한다.

정리 원칙:

- `opium_wars_start_var`는 바닐라 `opium_wars.1` 차단용으로 남긴다.
- 바닐라 호환 변수는 `opium_wars.3`~`.5`가 참조하므로 너무 일찍 제거하지 않는다.
- `opium_wars_won`, `opium_wars_gave_in`, `lost_opium_wars`, `opium_wars_lost`를 종료 상태 판정에 재사용한다.

## AI와 역사성

청나라 AI:

- `first_opium_war.9`에서 엄금론 선택 확률을 95 이상으로 둔다.
- 이금론은 플레이어 대체역사용 선택지로 둔다.

영국 AI:

- 전쟁 거부 선택지를 사실상 막는다.
- 이미 `events/opium_wars_events.txt`에서 `opium_wars.2.b`의 AI 확률이 0으로 되어 있으므로 새 체인에서도 같은 방향을 유지한다.

전쟁 강제:

- 영국과 청나라가 휴전 중이라면 기존 `opium_wars.101`~`.103` 흐름처럼 휴전 파기 이벤트를 사용한다.
- 영국이 다른 큰 전쟁 중인 경우에도 역사 강제 목적이면 전쟁을 미루지 않는다.
- 단, 영국이 사라졌거나 청나라가 사라진 경우에는 저널을 무효화한다.

## 구현 순서

1. 청나라 히스토리에서 `opium_wars_start_var` 설정과 `je_qing_opium_obsession` 추가를 넣는다.
2. `opium_wars.1`에 `opium_wars_start_var`를 가진 청나라 예외를 넣어 바닐라 초반 발동을 막는다.
3. `eafp_first_opium_war_debate_progress_bar`를 추가한다.
4. `je_qing_opium_obsession`을 활성 파일로 옮기고 `scripted_progress_bar` 중심으로 정리한다.
5. `first_opium_war.2`, `.3`, `.4`, `.9`를 구현한다.
6. 엄금론 이후 충돌 고조 이벤트 `.10`~`.13`을 구현한다.
7. 전쟁 강제 방식으로 `dp_first_opium_war` 직접 사용 가능 여부를 확인한다.
8. 직접 외교전 시작이 불안정하면 영국 `je_opium_wars` 추가 + 기존 회피 방지 이벤트 방식으로 구현한다.
9. 신규 로컬라이제이션과 모디파이어를 추가한다.
10. `rg`로 중복 키, `.disable` 참조, 미구현 loc 키를 확인한다.
11. 게임 로그에서 이벤트 ID, 저널 키, 스코프 오류를 확인한다.

## 검증 체크리스트

- 1836년 청나라 시작 시 `je_qing_opium_obsession`만 떠야 한다.
- 1836년 청나라 시작 시 `opium_wars_start_var`가 설정되어 있어야 한다.
- `je_qing_opium_obsession`에 `eafp_first_opium_war_debate_progress_bar`가 표시되어야 한다.
- 같은 상황에서 바닐라 `je_opium_obsession`은 청나라에 뜨지 않아야 한다.
- 영국에도 초반부터 바닐라 `je_opium_wars`가 자동으로 뜨지 않아야 한다.
- 1836~1839년 사이 `first_opium_war.2`~`.4`가 한 번씩 발생해야 한다.
- 결단 이벤트 `first_opium_war.9`가 progress bar 100 도달, 1839년 전후, 또는 저널 타임아웃에 발생해야 한다.
- 엄금론 선택 시 영국과 청나라 사이 전쟁 또는 전쟁 강제 저널이 확정적으로 열려야 한다.
- 영국 승리 시 `opium_wars_lost`, `lost_opium_wars`가 정상 설정되어야 한다.
- 청나라 승리 시 `opium_wars_won`과 아편 집착 제거가 정상 처리되어야 한다.
- 이금론 선택 시 전쟁은 발생하지 않되 `opium_wars_gave_in`이 설정되어 반복 발동을 막아야 한다.
- 2차 아편전쟁, 태평천국, 중국 선교 저널이 `opium_wars_lost` / `lost_opium_wars` 조건에 따라 정상적으로 이어져야 한다.

## 결정이 필요한 부분

- 새 저널 이름을 기존 `je_qing_opium_obsession`으로 유지할지, 더 명시적인 `je_first_opium_war_countdown` 같은 이름으로 바꿀지 결정해야 한다.
- `dp_first_opium_war`를 직접 외교전 시작에 사용할 수 있는지 실제 스크립트 효과 확인이 필요하다.
- 이금론 선택 시 어떤 장기 패널티를 줄지 정해야 한다.
- 엄금론 루트에서 전쟁 전까지 플레이어가 할 수 있는 준비 행동을 넣을지 정해야 한다.
  - 예: 해군 증강, 광동 방비, 임칙서 지원, 상인 단속.
  - 강제 전쟁 저널이면 선택지는 최소화하고 사건 연출 중심으로 가는 편이 안정적이다.
