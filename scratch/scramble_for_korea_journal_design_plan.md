# Scramble for Korea Journal Design Plan

## 범위

이 계획서는 기존 비활성화 콘텐츠인 `je_scramble_for_korea`와 `scramble_for_korea_events`를 재활용하여 조선, 청나라, 일본이 한반도 영향권을 두고 경쟁하는 국제 저널을 재설계한다.

대상 핵심 파일:

- `common/journal_entries/eafp_scramble_for_korea.txt`
- `common/scripted_progress_bars/eafp_scramble_for_korea_progress_bars.txt`
- `common/scripted_effects/eafp_scramble_for_korea_effects.txt`
- `events/eafp_scramble_for_korea_events.txt`
- `localization/korean/eafp_scramble_for_korea_l_korean.yml`
- `localization/english/eafp_scramble_for_korea_l_english.yml`
- `localization/simp_chinese/eafp_scramble_for_korea_l_simp_chinese.yml`

기존 파일은 `.disable` 상태이므로, 구현 시에는 새 `.txt` 파일로 옮기거나 현재 비활성 파일을 활성화하면서 요구사항에 맞게 갈아엎는다.

## 핵심 목표

- 발동 조건은 일본이 근대화했고 조선은 근대화하지 못한 상태여야 한다.
- 저널은 `je_group_global_international_situations`에 속한 국제 저널이어야 한다.
- 청나라, 조선, 일본을 각각 대표하는 scripted progress bar 3개를 둔다.
- 한 세력의 진행도가 높아질수록 나머지 두 세력의 진행도는 깎인다.
- 어느 하나의 진행도가 최대치에 도달하면 저널은 종료된다.
- 조선 진행도가 최대치면 조선은 독립을 유지한다.
- 청나라 또는 일본 진행도가 최대치면 조선은 해당 국가의 영향권 또는 종속권으로 넘어간다.

## 기존 자산 활용

이미 존재하는 자산:

- `common/journal_entries/eafp_scramble_for_korea.disable`
  - `je_scramble_for_korea`
  - 국제 저널 그룹 사용
  - `should_be_involved`, `should_show_when_not_involved` 패턴 보유
- `events/eafp_scramble_for_korea_events.disable`
  - 선교 활동, 조선 내 외국 소유 건물, 조선 이주민, 군부 도발, 로비 형성 이벤트 초안 보유
  - 레버리지, 긴장도, 조선 내 외국 영향력 modifier를 이미 사용
- `localization/korean/eafp_scramble_for_korea_l_korean.yml`
  - `je_scramble_for_korea`
  - `je_scramble_for_korea_reason`
  - `scramble_for_korea_events.*` 일부 loc
  - 관련 modifier loc

재사용 방향:

- 기존 저널의 국제 저널 구조는 유지한다.
- 기존 이벤트는 진행도 조절 이벤트로 재배치한다.
- 기존 `power_bloc.add_leverage`, `change_tension`, `modifier_kor_foreign_influence`는 일본/청 진행도 상승의 보조 효과로 남긴다.
- 기존 “조선이 인정국이 되면 종료” 방식은 폐기하고, 세 진행도 중 하나가 최대치에 닿으면 종료하는 방식으로 바꾼다.

## 발동 조건

### 권장 조건

`possible`은 다음 조건을 모두 만족할 때만 참이 되도록 한다.

- `c:KOR` 존재
- `c:JAP` 존재
- `c:CHI` 존재
- 조선이 독립국이거나 최소한 청/일본의 직접 종속국은 아님
- 일본 근대화 완료
- 조선 근대화 미완료
- `scramble_for_korea_finished` 글로벌 변수가 없음

일본 근대화 완료 조건은 기존 일본 콘텐츠 기준으로 다음을 우선 사용한다.

```txt
has_global_variable = meiji_restoration_complete
```

주의: `events/meiji_restoration.disable`에서 `meiji_restoration_complete`는 두 방식으로 쓰인다.

- `meiji.1`에서는 일본 국가 변수로 세팅됨
- `meiji.2`에서는 글로벌 변수로 세팅됨

“일본이 완전히 근대화했다”는 요구에는 `meiji.2`의 글로벌 변수 쪽이 더 잘 맞는다. 다만 해당 일본 콘텐츠가 계속 비활성 상태라면 백업 조건으로 아래 중 하나를 고려한다.

```txt
c:JAP ?= {
    OR = {
        has_variable = meiji_restoration_complete
        AND = {
            has_variable = completed_je_meiji_economy
            has_variable = completed_je_meiji_army
            has_variable = completed_je_meiji_diplomacy
        }
        is_country_type = recognized
    }
}
```

조선 근대화 미완료 조건은 기존 조선 개혁 저널의 완료 변수인 `korean_reformation_complete_var`를 우선 사용한다.

```txt
c:KOR ?= {
    NOT = { has_variable = korean_reformation_complete_var }
}
```

보조 조건으로 조선이 아직 미승인국이면 더 명확하다.

```txt
c:KOR ?= {
    is_country_type = unrecognized
}
```

### 저널 발동 의사코드

```txt
possible = {
    NOT = { has_global_variable = scramble_for_korea_finished }

    exists = c:KOR
    exists = c:JAP
    exists = c:CHI

    has_global_variable = meiji_restoration_complete

    c:KOR ?= {
        is_country_alive = yes
        is_subject = no
        is_country_type = unrecognized
        NOT = { has_variable = korean_reformation_complete_var }
    }
}
```

## 국제 저널 구조

`je_scramble_for_korea`는 국제 저널로 유지한다.

```txt
je_scramble_for_korea = {
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    group = je_group_global_international_situations

    scripted_progress_bar = eafp_scramble_for_korea_qing_progress_bar
    scripted_progress_bar = eafp_scramble_for_korea_korea_progress_bar
    scripted_progress_bar = eafp_scramble_for_korea_japan_progress_bar

    should_be_involved = {
        OR = {
            c:KOR ?= this
            c:CHI ?= this
            c:JAP ?= this
        }
    }

    should_show_when_not_involved = {
        OR = {
            has_strategic_region_interest_tier = {
                strategic_region = sr:region_northeast_asia
                value >= 3
            }
            capital ?= {
                is_in_geographic_region = geographic_region_northeast_asia
            }
            country_rank >= rank_value:great_power
        }
    }
}
```

설계 의도:

- 실제 경쟁 당사자는 조선, 청나라, 일본 3국으로 고정한다.
- 러시아, 영국 등 다른 열강은 `should_show_when_not_involved`로 관전 가능하게만 두고 직접 진행도 바를 갖지 않는다.
- 이후 확장하고 싶으면 다른 열강은 이벤트 선택지로 특정 세력에 보정치를 주는 방식이 좋다.

## Scripted Progress Bars

새 파일:

```txt
common/scripted_progress_bars/eafp_scramble_for_korea_progress_bars.txt
```

공통 설정:

- `start_value = 33`
- `min_value = 0`
- `max_value = 100`
- 월간 갱신 사용
- 세 바의 합은 대략 100 전후를 유지하도록 설계
- 특정 세력이 성장하면 나머지 세력은 자동으로 감점

### `eafp_scramble_for_korea_korea_progress_bar`

조선의 독립 유지력이다.

상승 요인:

- 조선이 독립국
- 조선과 청/일본의 관계가 둘 다 낮지 않음
- 조선이 군대, 행정, 경제 개혁 일부를 진행
- 조선 내 급진파 비율이 낮음
- 조선이 외국 소유 건물과 레버리지 압박을 낮게 유지
- 조선이 `completed_je_korean_reformation_*` 하위 저널을 하나 이상 완료

하락 요인:

- 일본 진행도 높음
- 청나라 진행도 높음
- 조선 내 외국 영향력 modifier 존재
- 조선이 파산, 내전, 혁명, 대규모 급진파 상태
- 조선이 청 또는 일본과 전쟁에서 패배 중

의사코드:

```txt
eafp_scramble_for_korea_korea_progress_bar = {
    name = "eafp_scramble_for_korea_korea_progress_bar_name"
    desc = "eafp_scramble_for_korea_korea_progress_bar_desc"

    default = yes

    monthly_progress = {
        if = {
            limit = { has_journal_entry = je_scramble_for_korea }

            add = {
                desc = "eafp_scramble_for_korea_progress_base"
                value = 0.5
            }

            add = {
                desc = "eafp_scramble_for_korea_korea_from_reforms"
                value = 0
                if = { limit = { has_variable = completed_je_korean_reformation_society } add = 1 }
                if = { limit = { has_variable = completed_je_korean_reformation_military } add = 1 }
                if = { limit = { has_variable = completed_je_korean_reformation_economy } add = 1 }
                if = { limit = { has_variable = completed_je_korean_reformation_diplomacy } add = 1 }
            }

            add = {
                desc = "eafp_scramble_for_korea_korea_from_foreign_pressure"
                value = {
                    value = "scripted_bar_progress(eafp_scramble_for_korea_qing_progress_bar)"
                    add = "scripted_bar_progress(eafp_scramble_for_korea_japan_progress_bar)"
                    subtract = 66
                    multiply = -0.04
                }
            }
        }
    }

    start_value = 34
    min_value = 0
    max_value = 100
}
```

### `eafp_scramble_for_korea_qing_progress_bar`

청나라의 조선 재종속 또는 전통적 종주권 회복력이다.

상승 요인:

- 청나라가 조선과 좋은 관계
- 청나라가 조선을 방어하거나 조선 내 전쟁에 개입
- 청나라가 강대국 또는 열강 지위를 유지
- 청나라가 `je_chinese_westernization_international_prestige`를 진행 또는 완료
- 조선이 청나라 power bloc 또는 시장에 가까움
- 조선의 보수파, 양반, 유림 계열이 강함

하락 요인:

- 일본 진행도 높음
- 조선 진행도 높음
- 청나라가 아편전쟁, 태평천국, 군벌화, 중국 붕괴 상태
- 청나라가 전쟁배상, 내전, 파산 상태
- 일본과의 관계 악화 또는 일본 해군력 우세

의사코드:

```txt
eafp_scramble_for_korea_qing_progress_bar = {
    name = "eafp_scramble_for_korea_qing_progress_bar_name"
    desc = "eafp_scramble_for_korea_qing_progress_bar_desc"

    default_bad = yes

    monthly_progress = {
        if = {
            limit = { has_journal_entry = je_scramble_for_korea }

            add = {
                desc = "eafp_scramble_for_korea_qing_from_traditional_ties"
                value = 0.7
            }

            if = {
                limit = { c:CHI ?= { has_journal_entry = je_chinese_westernization_international_prestige } }
                add = {
                    desc = "eafp_scramble_for_korea_qing_from_westernization_prestige"
                    value = 0.8
                }
            }

            add = {
                desc = "eafp_scramble_for_korea_qing_from_rival_pressure"
                value = {
                    value = "scripted_bar_progress(eafp_scramble_for_korea_korea_progress_bar)"
                    add = "scripted_bar_progress(eafp_scramble_for_korea_japan_progress_bar)"
                    subtract = 66
                    multiply = -0.04
                }
            }
        }
    }

    start_value = 33
    min_value = 0
    max_value = 100
}
```

### `eafp_scramble_for_korea_japan_progress_bar`

일본의 조선 지배권 또는 보호국화 압력이다.

상승 요인:

- 일본 근대화 완료
- 일본이 인정국이고 군사/해군력이 청보다 우세
- 일본이 조선과 나쁜 관계 또는 조선에 claim 보유
- 일본 power bloc이 조선에 레버리지 우세
- 조선 내 개화파 지원 이벤트 성공
- 조선 내 일본 소유 건물 또는 일본 문화 pop 존재
- 청나라가 약화됨

하락 요인:

- 조선 진행도 높음
- 청나라 진행도 높음
- 일본이 전쟁, 파산, 내전, 낮은 정통성 상태
- 일본이 조선과 우호적이라 직접 지배 명분이 약함

의사코드:

```txt
eafp_scramble_for_korea_japan_progress_bar = {
    name = "eafp_scramble_for_korea_japan_progress_bar_name"
    desc = "eafp_scramble_for_korea_japan_progress_bar_desc"

    default_bad = yes

    monthly_progress = {
        if = {
            limit = { has_journal_entry = je_scramble_for_korea }

            add = {
                desc = "eafp_scramble_for_korea_japan_from_meiji"
                value = 1.0
            }

            if = {
                limit = {
                    c:JAP ?= {
                        NOT = { is_country_type = unrecognized }
                    }
                }
                add = {
                    desc = "eafp_scramble_for_korea_japan_from_recognition"
                    value = 0.5
                }
            }

            add = {
                desc = "eafp_scramble_for_korea_japan_from_rival_pressure"
                value = {
                    value = "scripted_bar_progress(eafp_scramble_for_korea_korea_progress_bar)"
                    add = "scripted_bar_progress(eafp_scramble_for_korea_qing_progress_bar)"
                    subtract = 66
                    multiply = -0.04
                }
            }
        }
    }

    start_value = 33
    min_value = 0
    max_value = 100
}
```

## 상호 견제 방식

단순한 월간 계산만으로는 세 바의 합이 정확히 100이 되지 않을 수 있다. 따라서 두 단계로 처리한다.

1. 각 scripted progress bar가 자기 상승/하락 요인을 계산한다.
2. `on_monthly_pulse`에서 보정 scripted effect를 실행해 세 바의 합이 너무 크게 벌어지지 않게 한다.

권장 effect:

```txt
eafp_scramble_for_korea_balance_progress_bars = {
    # 1. 세 바의 현재값 합계를 계산한다.
    # 2. 합계가 100보다 높으면 가장 낮은 바가 아니라, 현재 상승폭이 없는 바들에서 우선 차감한다.
    # 3. 합계가 100보다 낮으면 조선 바에 소량 보정한다. 이는 외세가 실질 성과를 못 내면 기본값이 독립 유지 쪽으로 흐르게 하기 위함이다.
    # 4. 모든 바를 0-100 사이로 clamp한다.
}
```

실제 구현에서는 변수 기반 보정보다 scripted progress bar 자체의 음수 항목을 우선 사용한다. 단, 테스트에서 세 바가 동시에 상승하는 문제가 보이면 `set_bar_progress` 기반 보정 effect를 추가한다.

## 종료 조건과 결과

`complete`는 세 진행도 중 하나라도 100 이상이면 발동한다.

```txt
complete = {
    scope:journal_entry = {
        OR = {
            "scripted_bar_progress(eafp_scramble_for_korea_korea_progress_bar)" >= 100
            "scripted_bar_progress(eafp_scramble_for_korea_qing_progress_bar)" >= 100
            "scripted_bar_progress(eafp_scramble_for_korea_japan_progress_bar)" >= 100
        }
    }
}
```

`on_complete_all_involved`에서 실제 승자를 판정한다.

### 조선 승리: 독립 유지

조건:

```txt
scope:journal_entry = {
    "scripted_bar_progress(eafp_scramble_for_korea_korea_progress_bar)" >= 100
}
```

효과:

- `scramble_for_korea_finished` 글로벌 변수 세팅
- `c:KOR`에 `eafp_scramble_for_korea_independence_preserved` 변수 세팅
- 조선에 장기 독립/외교 보너스 modifier 부여
- 청나라와 일본에는 영향력 상실 modifier 부여
- 조선이 미승인국이면 바로 인정국으로 만들지는 않는다. 대신 인정국으로 가는 보정치 또는 이벤트 후속 체인을 둔다.

권장 서사:

- “조선은 두 제국의 틈바구니에서 외교 균형과 제한적 개혁으로 국권을 지켜냈다.”

### 청나라 승리: 조선이 청 영향권으로 넘어감

조건:

```txt
scope:journal_entry = {
    "scripted_bar_progress(eafp_scramble_for_korea_qing_progress_bar)" >= 100
}
```

효과:

- `scramble_for_korea_finished` 글로벌 변수 세팅
- `c:KOR`에 `eafp_scramble_for_korea_qing_victory` 변수 세팅
- 조선이 청의 종속국이 됨
- 일본에는 굴욕 또는 대륙 진출 좌절 modifier 부여
- 청에는 종주권 회복 modifier 부여

종속 형태 권장:

- 1순위: `tributary`
- 2순위: `protectorate`
- 만약 `tributary` subject type이 현재 빌드에서 불안정하면 `protectorate`로 대체한다.

의사코드:

```txt
c:CHI ?= {
    if = {
        limit = {
            can_have_as_subject = { who = c:KOR type = subject_type_tributary }
            c:KOR ?= { is_subject = no }
        }
        create_diplomatic_pact = {
            country = c:KOR
            type = tributary
        }
    }
}
```

### 일본 승리: 조선이 일본 영향권으로 넘어감

조건:

```txt
scope:journal_entry = {
    "scripted_bar_progress(eafp_scramble_for_korea_japan_progress_bar)" >= 100
}
```

효과:

- `scramble_for_korea_finished` 글로벌 변수 세팅
- `c:KOR`에 `eafp_scramble_for_korea_japan_victory` 변수 세팅
- 조선이 일본의 종속국이 됨
- 청에는 한반도 영향권 상실 modifier 부여
- 일본에는 대륙 교두보 확보 modifier 부여

종속 형태 권장:

- 1순위: `protectorate`
- 2순위: `puppet`
- 역사적 강제 병합까지 바로 가는 것은 너무 강하므로, 첫 결과는 보호국화로 두고 후속 저널 또는 외교 플레이로 병합을 처리한다.

의사코드:

```txt
c:JAP ?= {
    if = {
        limit = {
            can_have_as_subject = { who = c:KOR type = subject_type_protectorate }
            c:KOR ?= { is_subject = no }
        }
        create_diplomatic_pact = {
            country = c:KOR
            type = protectorate
        }
    }
}
```

## 월간 이벤트

기존 `scramble_for_korea_events.4`, `.5`, `.10`, `.11`, `.12`는 유지하되, 각 선택지가 진행도에 직접 영향을 주도록 바꾼다.

### `scramble_for_korea_events.1` 저널 시작

대상:

- 조선, 청, 일본 모두 팝업

효과:

- `korea_scope`, `qing_scope`, `japan_scope` 저장
- 세 진행도 초기값 세팅
- 조선에는 위기 알림
- 청/일본에는 경쟁 알림

### `scramble_for_korea_events.4` 조선에서의 선교 활동

기존 이벤트를 재활용한다.

선택지 방향:

- 후원한다: 일본 또는 서구식 개화 영향 상승, 조선 독립력 소폭 하락
- 거부한다: 조선 독립력 상승, 외세 진행도 하락
- 구체제에 영합한다: 청 진행도 상승, 일본 진행도 하락

### `scramble_for_korea_events.5` 외국 자본과 노동 문제

기존 “조선 건물 중 ROOT가 소유한 건물” 조건을 유지한다.

선택지 방향:

- 노동 조건 개선: 해당 외국 세력 진행도 상승, 조선 내 반외세 압력 완화
- 방치: 조선 독립력 또는 청/일본 반대 세력 진행도 상승

### `scramble_for_korea_events.10` 조선 이주민 문제

일본 또는 청 문화 pop이 조선에 있을 때 가중치를 둔다.

선택지 방향:

- 이주민 지원: 해당 세력 진행도 상승
- 본국 귀환 유도: 조선 독립력 상승
- 현지 동화 방치: 장기적으로 조선 독립력 소폭 상승

### `scramble_for_korea_events.11` 군부 도발

청과 일본 사이 긴장도 이벤트로 재정리한다.

선택지 방향:

- 강경 대응: 자기 진행도 상승, 상대 진행도 하락, 긴장도 상승
- 사과/수습: 조선 독립력 상승, 자기 진행도 하락
- 장교 포상: 자기 진행도 크게 상승, 상대와 긴장도 크게 상승

### `scramble_for_korea_events.12` 조선 내 정치 로비

기존 로비 생성 구상을 진행도 이벤트로 완성한다.

선택지 방향:

- 자금 지원: 자기 진행도 상승, 조선 독립력 하락
- 부패 폭로: 조선 독립력 상승, 해당 세력 진행도 하락

## Scripted Buttons

선택 사항이지만, 플레이어가 진행도에 능동적으로 개입할 수 있도록 세 국가별 버튼을 두면 좋다.

### 조선 버튼

- `button_je_scramble_for_korea_balance_diplomacy`
  - 청/일본 진행도를 둘 다 소폭 하락
  - 조선 진행도 상승
  - 비용: 권위 또는 관료력
- `button_je_scramble_for_korea_domestic_reform`
  - 조선 진행도 상승
  - 조건: 조선이 개혁 저널 일부 진행 중
  - 비용: 급진파 증가 또는 보수파 반발

### 청나라 버튼

- `button_je_scramble_for_korea_reaffirm_suzerainty`
  - 청 진행도 상승
  - 일본 진행도 하락
  - 비용: 관계 악화, 긴장도 상승

### 일본 버튼

- `button_je_scramble_for_korea_support_enlightenment`
  - 일본 진행도 상승
  - 조선 개화파 modifier 부여
  - 청 진행도 하락
  - 비용: 자금, 긴장도 상승

버튼은 필수 요구사항은 아니므로 1차 구현에서는 생략 가능하다. 다만 저널이 월간 랜덤 이벤트만으로 흘러가면 플레이어 체감이 약할 수 있어 2차 구현 대상으로 권장한다.

## 로컬라이제이션 키

기존 한국어 loc는 유지하고 아래 키를 추가한다.

저널:

- `je_scramble_for_korea`
- `je_scramble_for_korea_reason`
- `je_scramble_for_korea_status_korea_leading`
- `je_scramble_for_korea_status_qing_leading`
- `je_scramble_for_korea_status_japan_leading`
- `je_scramble_for_korea_result_korea`
- `je_scramble_for_korea_result_qing`
- `je_scramble_for_korea_result_japan`

진행도:

- `eafp_scramble_for_korea_korea_progress_bar_name`
- `eafp_scramble_for_korea_korea_progress_bar_desc`
- `eafp_scramble_for_korea_qing_progress_bar_name`
- `eafp_scramble_for_korea_qing_progress_bar_desc`
- `eafp_scramble_for_korea_japan_progress_bar_name`
- `eafp_scramble_for_korea_japan_progress_bar_desc`
- `eafp_scramble_for_korea_progress_base`
- `eafp_scramble_for_korea_korea_from_reforms`
- `eafp_scramble_for_korea_korea_from_foreign_pressure`
- `eafp_scramble_for_korea_qing_from_traditional_ties`
- `eafp_scramble_for_korea_qing_from_westernization_prestige`
- `eafp_scramble_for_korea_qing_from_rival_pressure`
- `eafp_scramble_for_korea_japan_from_meiji`
- `eafp_scramble_for_korea_japan_from_recognition`
- `eafp_scramble_for_korea_japan_from_rival_pressure`

진행도 desc는 기존 모드 패턴대로 현재 값을 표시한다.

```yml
eafp_scramble_for_korea_korea_progress_bar_desc: "$eafp_scramble_for_korea_korea_progress_bar_name$: #v [JournalEntry.GetCurrentBarProgress(ScriptedProgressBar.Self)|%1]#! ([JournalEntry.GetCurrentBarValue(ScriptedProgressBar.Self)|1]/100)"
```

## 구현 순서

1. `eafp_scramble_for_korea_progress_bars.txt` 추가
   - 조선, 청, 일본 progress bar 3개 작성
   - 진행도 desc loc 연결

2. `eafp_scramble_for_korea.txt` 작성
   - 기존 `.disable` 저널을 기반으로 국제 저널 구조 복원
   - 발동 조건을 일본 근대화/조선 미근대화로 교체
   - 세 progress bar 연결
   - `complete`를 세 바 중 하나가 100 이상인 조건으로 설정

3. `eafp_scramble_for_korea_effects.txt` 작성
   - 조선 승리, 청 승리, 일본 승리 effect 분리
   - 필요 시 bar 보정 effect 작성

4. `eafp_scramble_for_korea_events.txt` 활성화
   - 기존 `.disable` 이벤트를 재활용
   - 각 선택지에 `add_progress` 또는 `set_bar_progress` 효과 연결
   - 시작/종료 이벤트 추가

5. 로컬라이제이션 정리
   - 한국어 우선 작성
   - 영어/중국어는 최소 키 누락 없이 작성

6. 검증
   - `rg -n "je_scramble_for_korea|eafp_scramble_for_korea_.*progress_bar"`로 참조 확인
   - progress bar loc 누락 확인
   - 게임 실행 후 `error.log`에서 `Unknown scripted progress bar`, `Invalid scope`, `Missing localization` 확인

## 구현 시 주의점

- 조선이 이미 청 또는 일본의 종속국이면 저널이 새로 뜨지 않게 한다.
- 조선이 이미 `korean_reformation_complete_var`를 가졌다면 이 저널은 뜨지 않는다.
- 일본 근대화 조건은 `meiji_restoration_complete` 글로벌 변수 사용을 우선하지만, 일본 콘텐츠 활성화 상태에 따라 백업 조건을 둔다.
- 청나라가 존재하지 않으면 청 progress bar가 의미 없으므로 저널도 뜨지 않는 쪽을 기본값으로 한다.
- `complete` 하나로 세 결과를 모두 처리하면 UI상 “완료”로 통일된다. 조선 승리를 완료, 청/일본 승리를 실패로 보여주고 싶다면 `complete = 조선 100`, `fail = 청 또는 일본 100`으로 나누되, 청/일본 플레이어에게는 실패처럼 보일 수 있다.
- 종속국화 효과는 현재 subject type과 `can_have_as_subject` 지원 여부를 실제 게임 로그로 확인해야 한다.
- 세 progress bar가 동시에 100에 도달할 수 있는 극단 상황을 막기 위해 최종 판정은 우선순위를 둔다.
  - 1순위: 가장 높은 bar
  - 동률이면 조선 우선
  - 청/일본 동률이면 관계, 전쟁 승패, 군사력 비교로 결정

## 추천 최종 판정 우선순위

```txt
if korea >= 100 and korea >= qing and korea >= japan:
    Korea victory
else_if japan >= 100 and japan >= qing:
    Japan victory
else_if qing >= 100:
    Qing victory
```

동률에서 조선을 우선하는 이유는, 외세가 결정적 우위를 만들지 못했다면 조선의 독립 유지로 해석하는 편이 플레이 감각상 자연스럽기 때문이다.
