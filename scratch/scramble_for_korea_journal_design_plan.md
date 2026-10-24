# 조선 쟁탈 일지 구현 계획 — 다국가 참여·동적 custom_gui

작성 기준: 2026-10-12, 현재 로컬 EAFP 및 `Vic3-vanilla` 소스. **이 문서의 설계를 2026-10-13에 게임 스크립트로 구현했다.** 소스 기반 검증을 수행했으며 게임 내 실행은 미검증이다. 사용자 수정 사항에 따라 열강의 추가 참여와 국가별 동적 `custom_gui` 막대를 적용한다. 청·일 단일 경쟁 막대와 별도 조선 자주권 막대라는 이전 설계는 폐기한다. 활성화·참가와 이탈 조건·GUI 방식·개혁 보상·조선 독립 승리 조건·저항 -50%·청을 제외한 종주국 자동 승리·청을 포함한 세력 블록 지도자 보너스 월 +1은 요구사항이다. 국가 등급별 월간 수치·승리 후 보상 세부는 구현 제안이다.

수정 기준: 2026-10-13. **기존 체계의 수정·재사용을 우선하고, 필요한 상태와 실제로 반복되는 로직만 추가한다.** 이 원칙은 아래 데이터 구조·이벤트 전달·파일 구성에도 적용한다.

**2026-10-22 추가 계획:** 6절의 `scramble_for_korea_events.11`~`.22`는 역사 사건 12건의 **미구현 실행 명세**다. 13절에 공통 응답 `.23`과 트리거·modifier·지연 처리·정리 코드를 정의한다. 기존 구현 기록과 구분하며, 이번 수정은 설계 문서에만 적용한다. 기존 이벤트 1~7은 유지하고 8~10은 미배정으로 둔다.

### 구현 원칙

- 먼저 기존 정의·호출부·변수의 설정 및 제거 지점을 확인한다. 기존 일지·이벤트·버튼·modifier·script value의 담당 부분을 고치며, 같은 역할의 새 체계를 옆에 덧붙이지 않는다. 비활성 초안을 활성화할 때도 중복 정의를 남기지 않는다.
- 엔진의 JE 참여 상태, 기존 완료 변수, 실제 외교 관계와 modifier로 알 수 있는 상태는 다시 변수로 저장하지 않는다. 저장이 필요한 값과 한 번의 처리에만 필요한 계산값·이벤트 스코프를 구별한다.
- 한 곳에서만 사용하는 effect·trigger는 해당 JE 콜백·이벤트·버튼에 직접 작성한다. 코드 길이, 이름 붙이기, 향후 재사용 가능성만으로 `scripted_effect`·`scripted_trigger`를 만들지 않는다. **실제로 두 곳 이상에서 같은 의미와 스코프로 반복되는 로직**만 기존 정의의 재사용·수정을 먼저 검토한 뒤 추출한다. 단순 조건 한 줄을 감싸는 래퍼도 만들지 않는다.
- 새 변수는 기존 상태로 구분할 수 없는 이유, 저장 스코프, 쓰는 곳, 읽는 곳, 제거 시점을 설명할 수 있을 때만 추가한다. 캐시·보관 사본·이력 목록·처리 마커·영구 결과 기록을 예방적으로 만들지 않는다.
- 새 파일과 공통화 계층을 먼저 정하지 않는다. 기존 파일에서 요구 기능을 구현한 후 확인된 중복만 정리한다. 아래의 ‘공통 판정·처리’는 같은 규칙을 뜻하며 별도 scripted 정의 생성을 지시하지 않는다.

## 1. 핵심 구조

`je_scramble_for_korea`를 조선·청·일본과 조건을 충족한 다른 열강이 참여하는 국제 일지로 만든다.

- **조선:** 일지의 기본 관여국이다.
- **청:** `중국 붕괴 없음 AND (조선의 종주국 OR 승인국)`일 때만 관여국이 된다. 조건을 잃으면 기존 관여국에서도 제외한다.
- **일본:** `japan_restoration_complete 변수 있음 AND 승인국`일 때만 관여국이 된다. 조건을 잃으면 기존 관여국에서도 제외한다.
- **그 밖의 국가:** 열강이면서 한반도가 속한 전략 지역의 현재 이해관계가 3단계 이상이면 참가한다. 참가 후에는 2단계에서도 유지하고, 2 미만 또는 열강 지위 상실 시 이탈한다. 청·일은 이 일반 열강 분기로 우회 참가할 수 없다.
- **참여 기준과 영향력:** 현재 참여 여부는 **JE의 실제 관여국 상태**로 판정한다. 관여국이 되면 국가 변수 `scramble_for_korea_participants_influence`를 추가하고, 관여국에서 탈락하면 제거한다. 변수는 영향력 0–100만 저장하며 조선의 값은 자주권을 뜻한다. 변수의 존재로 관여국을 결정하거나 추가·제거하지 않는다. 별도 참여 플래그·전역 참가 목록·영향력 사본은 만들지 않는다.
- **동적 표시:** JE 관여국마다 한 행·한 막대를 생성하고 그 국가의 영향력 변수로 채움 정도를 표시한다. 영향력이 0이어도 행을 표시한다. 관여국인데 변수가 누락된 경우에는 변수를 보완하며, 관여국이 아닌데 변수가 남은 경우에는 변수를 제거한다.
- 모든 외국 참여국은 외교·투자·군사고문·조정 내 지원으로 경쟁한다. 조선은 제안에 대응하고 자체 개혁으로 자기 영향력을 높인다.
- 청·일·기타 열강의 승리와 조선 자주권 확보를 국가별 문구로 설명한다. 조선 소멸에 따른 경쟁 중단은 이벤트 없이 처리한다.

조선이 청의 종속국이어도 활성화하여 경쟁을 진행할 수 있다. **종주국 자동 승리는 현재 직접 종주국이 청이 아닐 때만 적용**한다. 시작부터 청 이외 국가의 종속국이면 첫 판정에서 해당 종주국 승리로 종료한다. 청은 종주국이라는 이유만으로 승리하지 않으며 영향력 승리 조건을 충족해야 한다. 청 종속 상태에서 다른 외국 관여국이 영향력으로 승리하면 종속관계를 그 승자에게 이전한다. 조선 자주권 확보는 **독립국 AND 승인국 AND 영향력 100**을 모두 요구하며 기존 단독 100·동률 보류 규칙을 적용한다. 조선의 ‘미승인’은 국가 유형이며 독립 여부와 별개다.

## 2. 바닐라에서 가져올 것

| 원본 | 실제 구현 | 조선에 적용할 방식 |
|---|---|---|
| [류큐 국제 일지](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/journal_entries/01_ryukyu_rivalry.txt:1) | 일·청·류큐 참여, 두 진행도, 네 버튼 | 국제 경쟁과 대응 이벤트 구조를 차용, 다국가 참여로 확장 |
| [진행도 정의](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/scripted_progress_bars/00_ep2_ryukyu_rivalry_progress_bars.txt:3) | 영향력 ±40, 해군력·관계·금전 이전·의무·개입·류큐 위신 반영 | 영향력 산정 소재만 차용, 수치는 국가 변수에 저장하고 custom_gui로 표시 |
| [자주권 진행도](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/scripted_progress_bars/00_ep2_ryukyu_rivalry_progress_bars.txt:362) | 영향력 -20~20에서 월 +0.5, 범위 밖에서는 정지 | 외세의 압력이 낮을 때 조선 영향력이 성장하도록 재설계 |
| [행동 버튼](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/scripted_buttons/ryukyu_rivalry_buttons.txt:1) | 종주권 재확인, 상인 회유, 방어 시찰, 키코에오오기미 예우 | 종주권·권익 주장, 상권 지원, 군사고문 제안, 조정 인사 포섭 |
| [이벤트 .1~.8](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/japan_events/ryukyu_rivalry_events.txt:1) | 상대국 대응·고문 도착·충돌·양국 승리·자주권 확보·시작 | 같은 상호작용 구조를 새 조선 이벤트 체인으로 작성 |
| [연간 충돌 처리](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/on_actions/00_on_actions_yearly.txt:556) | 양국 고문이 있으면 사고 유형 추첨, 5년 재발 방지, 양국에 .6 전달 | 실제 고문 파견국 중 두 국가를 선택해 충돌 생성, 조선도 대응 주체로 포함 |

바닐라의 승리 이벤트 `.5`는 승자의 기존 종속국이면 병합, 상대국 종속국이면 이전, 독립국이면 괴뢰국화한다. 자주권 이벤트 `.7`은 독립시키고 관련 금전 이전 조약에서 탈퇴한다. 이 효과를 그대로 복사하지 않는다. **조선의 기존 종속관계는 승리 판정 전까지 유지하고, 승리해도 자동 병합하지 않는다.**

바닐라의 DLC 표시 조건·이벤트 `dlc`·전용 영상도 별도로 확인한다. 조선 일지의 네 번째 발동 조건으로 DLC 보유를 추가하지 않도록, 기본 제공 아이콘·영상으로 대체 가능한 구성을 우선한다. 국제 일지 기능 자체의 DLC 의존성은 실제 실행 환경에서 확인한다.

## 3. 활성화 조건과 유신 일지 종료 판정

### 확정할 세 조건

| 요구 | 판정 |
|---|---|
| 청나라가 있고 중국 붕괴가 일어나지 않음 | `exists = c:CHI` 및 `NOT = { has_global_variable = china_shatters }` |
| 일본의 유신 일지가 종료됨 | 기존 `japan_restoration_complete`가 있음. 천황 복권 여부·종료 경로는 제한하지 않으며 새 변수 추가 없음 |
| 조선이 미승인국임 | `c:KOR = { is_country_type = unrecognized }` |

청은 현재 콘텐츠의 `CHI` 태그로 판정한다. 별도의 왕조·문화·법률 조건은 추가하지 않는다. [중국 붕괴 이벤트](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/events/warlord_china_events.txt:1125)는 실제로 글로벌 `china_shatters`를 설정한다.

### 기존 종료 변수 사용

[현재 유신 일지](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_00_meiji_restoration.txt:163)의 성공 경로는 `japan_emperor_restored`와 `japan_restoration_complete`를 설정한다. 다른 종료 경로도 기존 종료 변수를 공유한다.

- `japan_restoration_complete`는 막부 승리 `on_fail`과 군주제 폐지에 따른 `on_invalid`에서도 설정된다.
- `japan_emperor_restored`도 막부 승리 중 `kogi_yoron` 경로에서 설정된다.
- 이전 비활성 스크립트의 `meiji_restoration_complete` 글로벌 변수를 사용하면 현재 활성 콘텐츠와 맞지 않는다.

**새 변수는 추가하지 않는다.** 일본 측 활성화 요건은 기존 `japan_restoration_complete`의 존재만으로 판정하며 `japan_emperor_restored`는 요구하지 않는다. 유신 이후 경제·군사·외교 등 모든 후속 개혁 완료까지 요구하지 않는다. 기존 유신 일지·결과 이벤트에 기록용 코드를 추가하거나 기존 변수의 설정 의미를 바꾸지 않는다.

이 판정은 ‘유신 성공’이 아니라 **유신 일지 종료 기록**이다. 천황파 승리·공의여론뿐 아니라 **막부 유지·군주제 폐지로 일지가 끝나 종료 변수만 있는 경우도 포함**한다. 각 경로를 동일한 역사적 결과로 설명하지 않으며, 천황 복권 기록을 함께 요구하던 이전 설계는 폐기한다.

`possible`의 일본 스코프에서 기존 종료 변수를 직접 검사하고 일회성 scripted trigger로 감싸지 않는다. 새 성공 기록·자동 이행 변수·주기적 복원 로직은 만들지 않는다. 기존 저장도 같은 종료 변수 하나를 읽는다.

### possible 설계 예시

다음은 기존 변수만 사용하는 예정 코드다.

```txt
possible = {
    exists = c:CHI
    NOT = { has_global_variable = china_shatters }

    exists = c:JAP
    c:JAP = {
        has_variable = japan_restoration_complete
    }

    exists = c:KOR
    c:KOR = { is_country_type = unrecognized }

    NOT = { has_global_variable = scramble_for_korea_finished }
}
```

일본·조선의 존재 검사는 스코프 접근을 보장한다. 종료 후 재발동 방지에는 비활성 초안에 이미 있는 `scramble_for_korea_finished`를 재사용한다. 초기화는 국제 JE의 `immediate`에서 처리하며 기존 JE 활성 상태와 영향력 변수의 존재를 이용해 중복을 막는다. 별도 `started` 변수는 만들지 않는다.

`is_shown_when_inactive`에서는 세 조건의 충족 여부를 읽을 수 있게 한다. **일지 활성화 조건과 개별 국가의 관여 조건은 분리**한다. 일본의 종료 변수만 있어도 다른 활성화 조건이 맞으면 일지를 시작할 수 있지만, 일본의 관여에는 기존대로 종료 변수와 승인국 조건을 함께 요구한다. 따라서 시작 시에도 청·일의 관여 조건을 따로 검사하고, 무조건 세 나라를 등록하지 않는다. `japan_emperor_restored`는 활성화·관여 어느 쪽에도 요구하지 않는다.

### 참여 자격과 전략 지역

현재 바닐라의 [전략 지역 정의](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/strategic_regions/east_asia_strategic_regions.txt:31)에서 서울·부산·사리원·평양·양호는 `region_northeast_asia`에 속한다. EAFP의 [조선 봉기 일지](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_03_korea.txt:210)에도 같은 지역의 이해관계 3단계 판정이 있다. 따라서 현재 지도에서는 아래 조건으로 ‘한반도 지역 이해관계’를 구현한다. 이는 한반도만 분리된 지역이 아니라 동북아 전체를 대상으로 하는 현행 게임의 단위다. 한반도 전용 전략 지역이 생기면 해당 자격 판정의 지역 참조를 수정한다.

```txt
should_be_involved = {
    OR = {
        c:KOR ?= this
        AND = {
            c:CHI ?= this
            NOT = { has_global_variable = china_shatters }
            OR = {
                c:KOR ?= { is_subject_of = c:CHI }
                is_country_type = recognized
            }
        }
        AND = {
            c:JAP ?= this
            has_variable = japan_restoration_complete
            is_country_type = recognized
        }
        AND = {
            # 청·일은 국가별 조건을 일반 열강 조건으로 우회하지 않음
            NOR = {
                c:KOR ?= this
                c:CHI ?= this
                c:JAP ?= this
            }
            country_rank >= rank_value:great_power
            OR = {
                # 신규·재참가
                has_strategic_region_interest_tier = {
                    strategic_region = sr:region_northeast_asia
                    value >= 3
                }
                # 이미 참여 중이면 2단계에서도 유지
                AND = {
                    is_involved_in_journal_entry = je_scramble_for_korea
                    has_strategic_region_interest_tier = {
                        strategic_region = sr:region_northeast_asia
                        value >= 2
                    }
                }
            }
        }
    }
}
```

`should_be_involved`와 기존 관여국 제거 로직에 같은 국가별 분기를 적용한다. 청·일은 각 전용 조건을 등록·유지에 동일하게 사용하고, 열강 지위·지역 이해관계 단계는 요구하지 않는다. 청의 종주국 여부는 `c:KOR`가 `c:CHI`의 종속국인지로 확인한다. 승인 여부는 해당 국가 스코프에서 `is_country_type = recognized`로 확인한다.

그 밖의 열강만 **현재 비관여국은 3 이상에서 등록, 현재 관여국은 2 이상에서 유지**한다. 현재 참여 여부는 국가 스코프의 `is_involved_in_journal_entry = je_scramble_for_korea`로 판정한다. 이 트리거는 [로컬 문서](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/documentation/triggers.log:6679)에 정의되어 있다. 이해관계 2는 ‘미참여국은 참가 불가, 기존 참여국은 유지’인 구간이며 영향력 변수의 존재와 무관하다. 동일한 전체 조건이 실제로 반복될 때만 scripted trigger로 추출하고, 세력권 주도·문화·대륙·전략적 인접 조건은 추가하지 않는다.

### 참가·이탈·재참가

1. 시작 시 조선과 각 국가별 조건을 충족한 청·일·그 밖의 열강을 등록한다. 이후 주간 펄스에서 청의 붕괴·종주관계·승인 여부, 일본의 기존 완료 변수·승인 여부, 그 밖의 국가의 열강 지위·이해관계를 다시 검사한다.
2. 참가 조건에 따라 **먼저 JE 관여국으로 등록한 뒤**, 해당 국가에 `scramble_for_korea_participants_influence`를 추가한다. 이미 관여국이고 변수도 있으면 기존 값을 유지한다. 관여국인데 변수만 없으면 0으로 보완하고 시작 보너스는 재지급하지 않는다. 변수 누락을 이유로 관여국에서 제거하지 않는다. 등록 처리가 실제로 반복될 때만 scripted effect 추출을 검토한다.
3. 청은 `china_shatters`가 있거나 ‘조선 종주국’과 ‘승인국’이 모두 거짓이면 제외한다. 일본은 `japan_restoration_complete`가 없거나 승인국이 아니면 제외한다. 그 밖의 열강은 열강 지위를 잃거나 이해관계가 **2 미만**이면 제외하고, 3→2에서는 영향력·GUI 행·참여를 유지한다. 버튼·예약 이벤트·승리 판정도 이 국가별 유지 조건을 검사한다. 유지 조건을 잃은 국가는 동기화 전에도 행동·승리할 수 없으며, 청·일을 일반 열강 조건으로 재등록하지 않는다.
4. 이탈 조건에 따라 **먼저 JE 관여국에서 제거한 뒤**, 해당 국가의 `scramble_for_korea_participants_influence`를 제거한다. 변수만 남은 비관여국을 발견해도 재등록하지 않고 변수만 정리한다. 별도 점수 보관 변수는 만들지 않는다. 자기 고문 효과·미결 제안만 취소하며 다른 국가의 점수는 바꾸지 않는다.
5. 재참가는 새 등록으로 취급해 영향력을 0으로 시작한다. 첫 참가·재참가 이력을 구분하는 변수와 참가 보상은 두지 않는다. 반복 이탈·재참가로 초기 점수를 회복하는 것을 막기 위해 일지 시작 시 한 번만 초기 배치를 적용하고, 시작 후 합류는 모두 0으로 통일한다. 쿨다운은 이탈로 초기화하지 않고 원래 만료까지 유지한다.
6. 청·일을 포함한 외국 소멸은 해당 국가만 제거하며, 중국 붕괴는 청의 관여 자격만 상실시킨다. 남은 관여국끼리 경쟁을 계속한다. 청 이외의 현재 직접 종주국 자동 승리를 우선하고, 그 조건이 없으며 실제 관여국이 조선만 남으면 조선 승리로 끝낸다. 전체 종료 때 영향력 변수와 경쟁 전용 임시 효과를 정리한다.

기존 JE의 주간 `every_scope_je_involved` / `remove_involved_country` 처리를 수정하여 사용한다. `should_be_involved`의 자동 반영 범위를 확인하고 부족한 신규 참가 처리만 `add_involved_country`로 보완한다. **관여국 변경 → 변수 추가·제거 → 영향력 계산·승패 판정** 순서를 유지한다. 엔진이나 다른 이벤트가 관여국을 바꾼 경우에도 동일한 방향으로 누락·잔여 변수를 정리한다. 안전한 제거에 후보 목록이 필요하면 해당 처리 안의 임시 목록을 쓰며 영구 상태로 만들지 않는다.

## 4. 국가 변수·custom_gui·진행도

### 데이터 구조

| 저장 위치 | 이름 | 역할 |
|---|---|---|
| 현재 참여하는 각 국가 | `scramble_for_korea_participants_influence` | 영향력 0–100. JE 관여국이 되면 추가, 탈락·종료하면 제거. 참여 여부의 판정 원본으로 사용하지 않음 |
| 국제 JE | 엔진의 관여국 상태 | 현재 참여 여부의 유일한 기준. 국가별 변수 생명주기와 GUI 행은 이 상태를 따름 |
| 전역 | 기존 `scramble_for_korea_finished` | 종료·재발동 방지에 기존 플래그 재사용 |
| 처리·이벤트 스코프 | 승자·행위국·대상·변화량 | 해당 실행과 후속 이벤트에 필요한 범위에서 전달. 영구 전역 승자·결과 변수로 저장하지 않음 |

월간 변화는 같은 계산식을 월간 적용과 툴팁에서 읽고 영구 캐시를 두지 않는다. 툴팁은 지난달 적용 기록이 아닌 현재 조건의 예상 월간 증감을 표시한다. 고문 파견 기간은 실제 modifier의 존속 여부·기간을, 행동 대기는 버튼의 기존 쿨다운 기능을 우선 사용한다. 엔진 상태만으로 표현할 수 없는 미결 제안 잠금 등의 상태는 구현에서 필요가 확인된 최소 항목만 추가하고 만료·취소·종료 시 제거한다.

**JE 관여국 상태가 기준이고, 변수는 그 결과를 따른다.** 동기화 완료 후에는 관여국·변수 보유국·GUI 표시국이 일치하지만, 불일치를 고칠 때는 관여국 상태를 바꾸지 않고 변수를 추가·제거한다. 조선도 같은 기준을 쓴다. 참여 여부가 필요한 효과·이벤트는 `is_involved_in_journal_entry`로 검사한다. `has_variable` / `IsSet`은 변수 초기화 중복 방지·누락 검사·안전한 값 읽기에만 사용하며 참여 자격이나 참가·이탈을 결정하지 않는다.

기존 `scramble_for_korea_participants` 전역 목록은 병행하지 않는다. 그 목록의 참여 관리 역할은 엔진의 JE 관여국 상태가 담당하고, `scramble_for_korea_participants_influence`는 각 관여국의 숫자 데이터만 담당한다. 이미 활성화된 개발용 저장의 옛 목록과 신규 국가 변수를 그대로 호환된다고 가정하지 않는다. GUI에서 매 프레임 전 세계 국가를 검색하거나 상태를 수정하지 않는다.

```txt
# 아래 예시는 모두 대상 국가 스코프
# 실제 JE 관여국 상태에 맞춰 변수만 보완·정리하는 효과
if = {
    limit = {
        is_involved_in_journal_entry = je_scramble_for_korea
        NOT = { has_variable = scramble_for_korea_participants_influence }
    }
    set_variable = { name = scramble_for_korea_participants_influence value = 0 }
}
else_if = {
    limit = {
        NOT = { is_involved_in_journal_entry = je_scramble_for_korea }
        has_variable = scramble_for_korea_participants_influence
    }
    remove_variable = scramble_for_korea_participants_influence
}
# 이 효과에서는 JE 관여국을 추가하거나 제거하지 않음
```

### custom_gui 구현 방식

JE에 `widget = { gui = ... name = ... container = ... }`로 사용자 정의 GUI를 연결한다. 현재 [막번체제 일지](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_japan.txt:11)가 같은 연결 방식을 사용한다. 여기서 `custom_gui`는 이 사용자 정의 위젯을 뜻하며, 확인되지 않은 `custom_gui = ...` 키를 새로 가정하지 않는다.

[바닐라 국제 JE 화면](C:/Users/user/Documents/GitHub/Vic3-vanilla/gui/journal_entry.gui:691)은 실제로 `JournalEntry.GetInvolvedCountries`를 반복 표시한다. 이 엔진 목록이 행의 생성·제거를 결정하고 각 행의 `GetValue`는 영향력 변수만 읽는다. 변수의 `IsSet`으로 국가 행을 숨기거나 생성하지 않는다. 누락된 값의 읽기 보호는 표시 단계에서만 처리하고 실제 변수 보완은 게임 스크립트에서 수행한다. `GetGlobalList`는 사용하지 않는다.

막대는 [기존 변수 기반 GUI](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/gui/journal_entry_widgets/eafp_je_bakuhantaisei.gui:627)를 참고한다. 아래 코드는 바닐라의 관여국 반복 방식과 국가 변수 표시를 조합한 구현 초안이며, 실제 행의 Country 컨텍스트·레이아웃은 게임에서 검증한다.

```txt
# JE 내부: container는 실제 국제 일지 화면에서 검증
widget = {
    gui = "gui/journal_entry_widgets/eafp_je_scramble_for_korea.gui"
    name = "widget_je_scramble_for_korea_influence"
    container = "custom_widget_container_5"
}

# 위 GUI의 위젯 내부: 하나의 행 템플릿을 목록 수만큼 반복
flowcontainer = {
    direction = vertical
    datamodel = "[JournalEntry.GetInvolvedCountries]"
    item = {
        flowcontainer = {
            direction = vertical
            textbox = { text = "[Country.GetName]" }
            green_progressbar_horizontal = {
                blockoverride "values" {
                    min = 0
                    max = 100
                    value = "[Country.MakeScope.Var('scramble_for_korea_participants_influence').GetValue]"
                }
            }
        }
    }
}
```

기본 `scripted_progress_bar`로 국가별 막대를 열거하거나 청·일 합성 막대를 남기지 않는다. 국가별 GUI 정의도 복제하지 않는다. 실제 행에는 국기·국명·역할(조선 자주권/외국 영향력)·현재 값·월간 증감·변화 원인 툴팁을 표시하고, 색상 외에도 텍스트로 국가를 구별한다. 숫자와 막대 채움은 같은 국가 변수를 읽는다. GUI 새로고침이나 관전 국가 전환은 게임 상태를 수정하지 않는다.

행 순서는 기존 JE의 안정적인 순서를 사용하고 점수 변화마다 재정렬하지 않는다. 순서 보존을 위한 별도 이력 변수·GUI 전역 목록은 만들지 않는다. 최대 높이와 세로 스크롤을 두되 행 수 제한은 두지 않는다. **3국이면 3개, 영·러·미가 더 들어오면 6개, 한 국가 이탈 시 5개**가 표시된다. 관전국도 같은 JE 열거 결과에서 국가별 영향력 변수를 읽으며 `JournalEntry.GetCountry`를 참가국 저장소로 사용하지 않는다.

### 영향력 산정 제안

`I(c)`는 현재 참여국 c의 영향력 값이다. 각 값은 독립적인 0–100 수치이며 총합 100인 점유율이 아니다. 신규 참가·이탈만으로 기존 국가의 점수나 분모가 바뀌지 않는다. 상대 영향력 감소는 명시된 사건·행동에만 적용한다.

| 요소 | 외국 참여국 I(c) | 조선 I(KOR) |
|---|---|---|
| 일지 시작 시 초기 배치 | 기본 10. 이후 신규 합류·재참가는 모두 0. 종주국 초기 +20은 폐기. 청 이외 직접 종주국에만 자동 승리 적용 | 0 |
| 조선에 대한 금전 지원 | 실제 지급국에 월 최대 +1, 복수 조약 합산 후 상한 | — |
| 조선이 진 의무 | 채권국 월 +0.5 | — |
| 수락된 군사고문 | 파견국 월 +0.5, 24개월 | — |
| 외세 압력 억제 | — | 모든 외국 참여국의 영향력이 50 미만이면 월 +0.5 |
| 조선 국가 등급 | — | 강대국·미승인 강대국 월 +0.5, 개발도상국·미승인 지역국 월 +0.25, 열강 월 +0.75, 그 외 0. 서로 중첩하지 않음 |
| 조선의 세력 블록 소속 | 청을 포함한 외국 관여국이 자기 주도 세력 블록에 조선을 두면 월 +1 | — |
| 조선 하위 개혁 완료 | — | 사회·군사·경제·외교 각 일지 완료 시 +5, 합계 +20 |
| 조선 전체 개혁 완료 | — | 상위 `je_korean_reformation` 완료 시 별도 +10, 하위 보상과 합쳐 총 +30 |
| 사건·행동 | 지정된 행위국/대상국의 값에 증감, 기본 폭 2~5 | 수락·거부·자력 대응에 따라 증감 |

국가별 월간 지속 변화 합계는 -1~+1로 제한하고, 0–100 범위를 보장한다. 사건·개혁의 일회 변화는 별도다. 외국이 10에서 월 +1만 얻으면 100까지 90개월이다. 조선은 월 +0.5만 얻으면 200개월, 하위 개혁 +20만 반영하면 160개월, 상위까지 총 +30을 반영하면 140개월이다. 월간 등급 보너스는 제안 수치이고 세력 블록 월 +1·개혁 +5씩·전체 +10은 사용자 요구다. 세력 블록 +1도 다른 월간 항목과 합산한 뒤 기존 -1~+1 제한을 적용한다.

해군력과 조선과의 외교 관계 수치는 영향력 산정에서 제외한다. 월간 계산식·예상 증감 툴팁에도 해당 보너스를 남기지 않는다.

조선 등급은 [국가 등급 정의](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/country_ranks/00_country_ranks.txt:1)의 `great_power`, `major_power`, `unrecognized_major_power`, `minor_power`, `unrecognized_regional_power`를 사용한다. 미승인국도 해당 등급 보너스를 받을 수 있어야 한다. 원시 위신 수치나 세계 위신 순위를 직접 검사하지 않는다. 승인국이 된 독립 조선도 영향력 100에 도달해야 승리할 수 있으며, 그 전까지 등급 보너스 등 기존 산정과 경쟁을 계속한다.

세력 블록 보너스의 판정은 **영향력을 계산하는 외국 관여국** 스코프에서 다음과 같다. 같은 블록의 일반 회원국은 받지 않으며, 청도 블록 지도자이고 조선이 그 블록에 속하면 월 +1을 받는다. 블록 가입·탈퇴·지도자 변경은 다음 월간 산정에 반영하고 별도 보관 변수를 두지 않는다.

```txt
is_power_bloc_leader = yes
is_in_same_power_bloc = c:KOR
```

세력 블록 소속은 외교적 종속과 구별한다. 독립 조선도 다른 국가 주도 블록에 들어갈 수 있으며 이때는 월간 보너스만 발생한다. 청의 종속국인 조선도 경쟁을 계속하고, 청이 관여국이자 조선 소속 블록의 지도자이면 청에 월 +1을 적용한다. 청 이외 국가의 실제 종속국이 되면 점수 누적 대신 그 직접 종주국 자동 승리를 우선한다.

모든 국가의 월간 변화는 **같은 갱신 전 상태**를 기준으로 계산하고 전부 적용한 다음 승자를 판정한다. 현재 산식에서 다른 참가국의 영향력을 읽는 조선의 ‘모든 외국 50 미만’ 조건은 외국 점수를 바꾸기 전에 평가한다. 이처럼 읽기·적용 순서로 해결되는 계산에 국가별 영구 변화량 캐시를 만들지 않는다. 향후 서로의 갱신 전 값을 참조하는 항목이 늘어나면 그 실행 안에서만 임시 계산값을 사용한다.

기존 완료 개혁은 영향력 **최초 초기화 블록 안에서** `completed_je_korean_reformation_*` 네 개를 읽어 각각 +5, 상위 완료 변수 `korean_reformation_complete_var`가 있으면 별도 +10을 반영한다. 진행 중에는 하위 네 일지의 기존 `on_complete`에서 각각 +5, 상위 일지의 기존 `on_complete`에서 +10을 적용한다. 모두 조선이 쟁탈 JE 관여국이고 쟁탈이 종료되지 않았을 때만 지급한다. 보상은 범위 0–100에서 적용한다.

상위 +10은 하위 +20과 별개의 의도된 보상이다. 마지막 하위 완료와 상위 완료가 연속되면 그 시점에 합계 +15가 맞다. 별도 월간 완료 감시나 `*_counted` 변수를 추가하지 않는다. 완료 콜백은 보상을 적용한 뒤 기존 완료 변수를 설정하는 순서 등 실제 기존 흐름을 확인하여, 시작 초기화와 같은 시점의 보상이 두 번 들어가지 않게 한다. 이 보너스는 외세 참가 수와 무관하며, 이미 전체 개혁까지 끝난 조선의 초기 합계는 +30이다.

### 일지 활성 중 조선의 세력 블록 지렛대 저항

사용자가 지칭한 수치는 **세력 블록 지렛대 저항**(`country_leverage_resistance_mult`)이다. [바닐라 한국어 설명](C:/Users/user/Documents/GitHub/Vic3-vanilla/localization/korean/modifiers_l_korean.yml:2475)은 세력 블록의 초대에 필요한 지렛대 기준으로 설명한다. 요구값은 `-0.5`, 즉 이 modifier가 저항에 **-50%**를 제공하는 것이다. 가입 금지나 가입 확률 -50%가 아니라 블록의 초대에 대한 저항을 낮추는 효과이며, 최종 저항에는 다른 modifier도 합산된다.

[기존 modifier](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/static_modifiers/eafg_scramble_for_korea_modifiers.txt:17)의 `modifier_kor_foreign_influence`를 재사용하고 `country_leverage_resistance_mult = -0.1`을 `-0.5`로 변경한다. JE 활성화 시 **조선에만** 한 번 적용하고, 활성 기간 동안 유지하며 모든 승리·중단 경로에서 제거한다. 국제 JE의 모든 관여국에 일괄 적용되는 방식은 사용하지 않는다.

조선 저항 modifier는 활성화 시 적용하고 종료 시 정리한다. 즉시 종주국 승리로 끝나는 시작 상태에서도 종료 정리로 modifier가 남지 않아야 한다. 새로운 저항 변수·modifier 사본은 만들지 않는다.

### 행동

조선 쟁탈 일지의 행동 버튼은 사용하지 않는다. 자주 외교 버튼과 버튼 전용 외국 선두 계산을 제거했으며, 외국용 권익 주장·상권 지원·군사고문·조정 인사 포섭 버튼도 삭제된 상태다. 기존 저장의 자주 외교 행정 비용은 원래 기간과 종료 정리 처리를 유지한다.

## 5. 관련 일지와 기존 콘텐츠의 연결

이번 일지에 직접 연결할 기존 일지와 경계는 다음과 같다. 다른 조선 콘텐츠 전체의 내부 이벤트를 이 일지로 옮기지 않고, 확정된 완료 상태 또는 실제 외교 상태를 읽는다.

**조청전쟁 저널과는 연결하지 않는다.** 해당 저널의 존재·활성·완료·실패 여부나 전용 변수·이벤트 결과를 쟁탈 일지의 활성화·관여·영향력·정지·재개·승패 조건으로 사용하지 않는다. 양쪽 저널이나 이벤트를 서로 호출·완료·실패시키는 연결도 추가하지 않는다. 현재 전쟁 여부는 쟁탈 일지의 진행·행동·제안·승패 조건으로 사용하지 않는다. 현재 종속관계 등 외교 상태는 기존 규칙에 따라 확인한다.

| 기존 일지 | 연결 지점 | 계획 |
|---|---|---|
| `je_meiji_restoration` | 천황파 승리 `on_complete` → `meiji.1`, 막부 유지 `on_fail` → `ep2_meiji.8`, 공의여론 → `ep2_meiji.9`, 군주제 폐지 `on_invalid` | 기존 `japan_restoration_complete`만으로 일본 측 활성화 요건 판정. 기록 추가·기존 경로 수정 없음 |
| `je_korean_reformation` | 하위 네 일지 생성 및 `korean_reformation_complete_var` 설정 | 상위 완료 시 별도 조선 영향력 +10. 하위 네 개의 +20과 합산하여 총 +30 |
| `je_korean_reformation_society` | `completed_je_korean_reformation_society` | 조선 영향력 +5, 한 번 |
| `je_korean_reformation_military` | `completed_je_korean_reformation_military` | 같은 효과, 한 번 |
| `je_korean_reformation_economy` | `completed_je_korean_reformation_economy` | 같은 효과, 한 번 |
| `je_korean_reformation_diplomacy` | `completed_je_korean_reformation_diplomacy` | 같은 효과, 한 번 |
| `je_korean_foreign_mission` | 귀환 → `eafp_kor_foreign_mission.6` → 외교 개혁 조건에 기여 | 외교 개혁을 통해 간접 반영, 별도 중복 점수 없음 |
| `je_seikanron` | 반조선 로비·도발·외교 상태 | 독립적으로 유지. 동일 사건을 다시 발생시키거나 이 일지의 승리만으로 완료하지 않음 |

출처: [조선 개혁](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_korean_reformation.txt:1), [해외 사절단](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_korean_foreign_mission.txt:1), [정한론](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_japan.txt:1099).

```mermaid
flowchart TD
    M["je_meiji_restoration"] --> MS["천황파 승리 / meiji.1"]
    M --> KY["공의여론 / ep2_meiji.9"]
    M --> BK["막부 유지 / ep2_meiji.8"]
    M --> AB["군주제 폐지 / on_invalid"]
    MS --> JR["japan_restoration_complete 있음<br/>천황 복권 변수 불필요"]
    KY --> JR
    BK --> JR
    AB --> JR
    JR --> G{"청 존재 · 중국 붕괴 없음<br/>일본 유신 일지 종료 · 조선 미승인"}
    G -->|충족| S["je_scramble_for_korea"]
    R["je_korean_reformation"] --> R1["je_korean_reformation_society"]
    R --> R2["je_korean_reformation_military"]
    R --> R3["je_korean_reformation_economy"]
    R --> R4["je_korean_reformation_diplomacy"]
    R -->|상위 완료| RB["조선 영향력 +10<br/>하위 보상 포함 총 +30"]
    RB --> S
    F["je_korean_foreign_mission"] --> F6["eafp_kor_foreign_mission.6 / 귀환"]
    F6 -->|완료 조건 일부| R4
    R1 --> B["각 완료 상태당 1회<br/>조선 영향력 +5"]
    R2 --> B
    R3 --> B
    R4 --> B
    B --> S
    Q["je_seikanron / 기존 이벤트 체인 유지"] -.->|현재 외교 관계·조선 존속 상태만 관찰| S
```

## 6. 이벤트 전체 구성

현재 이벤트는 다음 7개다. 접두사는 모두 `scramble_for_korea_events`다. 중간 개입·제안·응답 이벤트 10개와 월간 무작위 사건 추첨은 삭제했다.

| ID | 내용 | 호출 경로 |
|---|---|---|
| `.1` | 풍전등화 | 조선 참가 통지 |
| `.2` | 한반도를 향한 야망 | 청·일 참가 통지 |
| `.3` | 조선 문제 | 기타 열강 참가 통지 |
| `.4` | 조선 자주권 확보 | 조선 승리 결과 통지 |
| `.5` | 새로운 패권국 | 청·일 이외 국가 승리 결과 통지 |
| `.6` | 일본 우세 확정 | 일본 승리 결과 통지 |
| `.7` | 청의 종주권 재확립 | 청 승리 결과 통지 |

전용 제안·응답 트리거, 제안 시작·종료·경쟁국 대응 effect와 경쟁국 선택용 script value도 삭제했다. 기존 저장에 남은 미결 제안 변수는 동기화·종료 시 제거한다. 월간 영향력 계산과 참가·승리 통지는 계속 실행한다.

### 추가 예정 이벤트 11~22 — 역사 사례 기반

기존 계획의 16·17번 사건을 제거하고, 18~24번을 두 칸씩 앞당겨 16~22번으로 배정한다. 현재 신규 계획은 11~22번의 총 12건이다. 접두사는 모두 `scramble_for_korea_events`이며 **본 사건 11~22와 보조 응답 23은 계획만 작성하며, 활성 이벤트·호출부·로컬 파일에는 아직 적용하지 않는다.** 8~10에는 이번 작업에서 사건을 배정하지 않는다. 아래 제목은 가제이며, 역사적 배경은 출처에 근거하고 선택지와 효과는 게임 설계 제안이다. 원문 인용이 확정되지 않았으므로 설명문을 사료의 직접 인용이나 확정 flavor text로 사용하지 않는다.

| 예정 ID | 제목 | 역사적 모티브 | 주요 선택 주체 |
|---|---|---|---|
| `.11` | 공사관으로 향하는 가마 | 아관파천, 1896년 | 조선, 보호를 제공할 외국 관여국 |
| `.12` | 누구의 뒤에 서야 하는가 | 박정양의 주미 공사 활동과 청의 영약삼단 요구, 1887~1889년 | 조선, 청, 사절을 접수할 관여국 |
| `.13` | 백성의 쌀인가, 상인의 계약인가 | 방곡령과 일본의 배상 요구, 1889~1893년 | 조선, 곡물 교역에 이해가 있는 외국 관여국 |
| `.14` | 우리 시장에 도는 남의 지폐 | 일본 제일은행권 발행과 통용 논란, 1902~1903년 | 조선, 금융 진출 외국 관여국 |
| `.15` | 전보는 어느 길로 가는가 | 서·남로 전선과 조선의 전신망 구축, 1885~1888년 | 조선, 전신 사업에 참여할 외국 관여국 |
| `.16` | 해관의 장부를 쥔 손 | 묄렌도르프의 고빙과 외국인 해관 운영, 1880년대 | 조선, 고문을 추천하는 외국 관여국 |
| `.17` | 철길의 주인은 누구인가 | 경인철도 부설권 허가와 양도, 1896~1898년 | 조선, 투자국, 이권 인수를 원하는 관여국 |
| `.18` | 산 아래 잠든 황금 | 운산 금광 채굴권 허가, 1895년 | 조선, 광산 투자를 제안하는 외국 관여국 |
| `.19` | 섬에 내려진 낯선 깃발 | 영국의 거문도 점령, 1885~1887년 | 조선, 점령국, 경쟁·중재 관여국 |
| `.20` | 벌목장의 포대 | 러시아의 용암포 진출과 군사기지화, 1903년 | 조선, 이권 보유국, 견제하는 관여국 |
| `.21` | 종로에 모인 목소리 | 만민공동회의 자주권 수호 운동, 1898년 | 조선, 철수·이권 회수 요구를 받는 관여국 |
| `.22` | 다른 나라에 허락했다면 | 최혜국 대우에 근거한 통상상 권리 균점 요구, 1880년대 | 조선, 기존 수혜국, 동등 대우를 요구하는 관여국 |
| `.23` (보조) | 외국의 응답 | 11~22의 제안에 대한 공통 수락·거부 | 제안을 받은 실제 외국 관여국 |

### 신규 사건의 확정 실행 규칙 — 2026-10-22 상세화

아래는 **구현용 스크립트 명세**다. 각 사건의 전문과 13절의 공통 정의를 함께 적용하면 트리거·스코프·선택 효과를 재설계할 필요가 없도록 작성한다. 아직 활성 게임 파일에는 넣지 않았으며 게임 실행 검증을 했다는 뜻은 아니다. 기존의 ‘높은 영향력’, ‘재정 비용’, ‘구현 시 결정’ 같은 제안은 아래 수치와 코드로 대체한다. 역사적 배경과 출처는 유지한다.

- **ID:** 본 사건은 11~22. 공통 외국 응답만 `.23`을 새로 예약한다. `.23`은 삭제했던 회담·철수 사건이 아니라 12개 본 사건의 동의/거부 처리용 보조 이벤트다. 독자 사업의 완공·환궁은 이름 있는 지연 on_action으로 처리하므로 추가 이벤트 ID를 만들지 않는다.
- **월간 호출:** 기존 JE의 `on_monthly_pulse.effect`에서 동기화와 모든 영향력 갱신을 마친 뒤 조선에 `sk_monthly_events`를 한 번 호출한다. 25% 확률로 현재 트리거와 cooldown을 만족하는 사건 중 하나를 동일 가중치 100으로 선택한다. 후보가 없으면 아무 일도 없다. 본 사건은 `cooldown = { days = 100000 }`로 게임 기간 중 한 번만 발생한다. 응답 `.23`에는 cooldown이 없다.
- **동시성:** 조선의 `sk_pending`은 선택 창/응답 대기 중인 사건 코드를 저장한다. 본 창은 11~22, 응답은 `사건 번호 × 10 + 선택 순번`이다. 예: 133은 `.13.c`. 최대 365일 후 만료하며 대기 중 새 본 사건을 추첨하지 않는다. 각 선택과 응답은 저장된 코드가 자기 사건과 일치하는지 재검사한다. 상대 이탈로 무효가 된 창은 취소/거절 선택 또는 잠금 만료 때 잠금을 해제하며, 이탈국을 즉시 재추첨하지 않는다. 기존 삭제 체인의 `scramble_for_korea_pending_offer`를 재사용하지 않으므로 현행 sync의 정리와 충돌하지 않는다.
- **금액·시간:** `add_treasury`는 일회성 파운드 금액이다. `country_tax_income_add = 100`은 주간 고정 수입 +100이다. 비용 선택은 표시와 실행 직전에 `gold_reserves >= 비용`을 검사한다. 외국의 계약 비용은 동의 시에만 차감한다. 거절·무효 응답에는 계약금과 영향력 보상이 없다. `days`는 180·365·730·1825처럼 명시하며, 이벤트 창의 `duration = 1`은 현재 참가 이벤트와 같은 값을 사용하고 이를 1일 지연으로 해석하지 않는다.
- **AI:** 각 본 사건 선택의 `ai_chance.base`는 코드에 고정한다. 공통 외국 응답은 수락 60, 거절 40이다. 수락 조건이 거짓이면 거절만 가능하다. 모든 창에 비용 없는 기본 선택 또는 무효 종료 선택이 있다.
- **스코프:** `sk_actor`는 주된 외국, `sk_rival`은 두 번째 외국, `sk_state`·`sk_building`·`sk_treaty`는 실제 대상이다. 이벤트의 `immediate`에서 결정하고 응답까지 그대로 전달한다. 응답에서 재추첨하거나 `scramble_winner`로 저장하지 않는다. `.14`·`.20`은 건물에서 외국 소유자를 찾으므로 `prev`가 어느 스코프인지 코드의 중첩을 유지해야 한다.
- **재검사:** 관여국 상태·국가별 유지 자격·영향력 변수·일지 종료 여부는 `sk_live_N`으로 다시 검사한다. 지위 상실·소멸·대상 주 상실·조약 소멸은 무효 처리한다. 최초 발생의 급진파·곡물 가격 등 일시적 조건은 창을 연 뒤 매번 재적용하지 않는다. 자금과 실제 건설/조약 권한은 사용 시 재검사한다.
- **영향력:** 기존 `scramble_for_korea_change_influence`를 재사용하여 0~100으로 제한한다. 외교 관계와 해군력은 월간 영향력 산정에 추가하지 않는다. 사건은 별도 승자를 확정하지 않고 현행 JE가 다음 검사에서 기존 승패 효과를 실행하게 한다. 현재 소스의 외국 승리 병합 처리 등은 이번 사건 명세의 변경 대상이 아니다.
- **장기 상태:** `sk_protector`, `sk_bank_partner`, `sk_customs_partner`, `sk_rail_partner`, `sk_mine_partner`, `sk_base_partner`는 실제 성립한 계약의 상대 국가를 저장한다. 이 상태는 점수 변수로 대체할 수 없다. `sk_job_코드`는 지연 작업의 중복 완료 방지용이다. 읽는 곳·만료·제거는 13절에 명시한다. 조청전쟁 저널과의 연결은 없다.
- **완공:** 외국이 이미 지급한 사업 자금은 그 국가가 이탈해도 환급하지 않는다. 전신·철도·자체 정비는 조선과 대상이 유효하면 계속 완공한다. 환궁만 보호국의 유효성도 요구한다. 일지 종료·조선 소멸로 취소한 사업은 환급하지 않고 점수도 지급하지 않는다. 완공한 철도 건물은 일지 종료 때 철거하지 않는다.


| 참고 바닐라 코드 | 이 계획에 사용하는 문법·구조 |
|---|---|
| [ryukyu_rivalry.1](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/japan_events/ryukyu_rivalry_events.txt:1) | 국가 스코프 저장, 외교 대응 선택, `levels_owned_by_country`, IG·국가 modifier |
| [ryukyu_rivalry.6·.7](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/japan_events/ryukyu_rivalry_events.txt) | `change_infamy`, `every_scope_treaty`, `withdraw` |
| [trade_route_events.2·.3](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/trade_route_events.txt:82) | 시장 간 `market_imports`, `mg:grain`의 `market_goods_pricier > 0.25` |
| [gg_korea.4](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/soi_events/00_ep1_korea_events.txt:226) | `radical_fraction`, 비주변 IG 조건, 청원에 대한 국내 정치 효과 |
| [trains.1](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/train_events.txt:1) | 조건과 같은 필터로 `random_scope_state`를 선택·저장 |
| [meiji.8](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/meiji_restoration.txt:1005) | 주 스코프에서 `create_building = { building = building_railway level = 1 }` |
| [production_tech_events.601](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/tech_events/production_tech_events.txt:980) | 기술·광산 유형·레벨 조건 |
| [통상특권 조약 판정](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/soi_events/00_lobbies_events_04.txt:444), [persia_events.4](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/soi_events/00_ep1_persia_events.txt:477) | 같은 인수의 `can_create_treaty` → 수락 후 `create_treaty` |
| [바닐라 on_action 문서](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/on_actions/_on_actions.md:33) | `trigger_event = { on_action = ... }`, `chance_to_happen`, 적격 이벤트 가중 추첨, 지연 호출 |
| [로컬 트리거 문서](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/documentation/triggers.log), [효과 문서](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/documentation/effects.log) | `can_construct_building`, `naval_power_projection`, `gold_reserves`, `save_scope_value_as`, 보관 스코프·modifier·조약 효과 |

위 바닐라는 문법과 처리 패턴의 근거다. 수치·발생 빈도·AI 가중치는 이 콘텐츠에 맞춰 아래처럼 확정한 설계값이며 바닐라의 동일 역사 사건을 복사했다는 뜻은 아니다.

### `.11` 공사관으로 향하는 가마

**역사적 배경:** 1896년 2월 11일 고종과 왕세자가 러시아 공사관으로 거처를 옮긴 아관파천을 모티브로 한다. 신변 보호를 얻는 선택이 외국의 정치적 영향력 확대와 연결되는 사건이다. 출처: [한국민족문화대백과사전 — 아관파천](https://encykorea.aks.ac.kr/Article/E0034214).

**확정 동작:** 급진파 20% 이상을 왕실 안전 위기의 판정으로 사용한다. 혁명 발생 자체는 필수 조건이 아니다. 피신 수락 후 365일에 환궁 효과를 한 번 적용한다. 거처 이전은 무료이며 정통성 +2/180일이다. 실제 수도·군주 위치·종속관계는 바꾸지 않는다.

**바닐라 참고:** ryukyu_rivalry.1; gg_korea.4.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.11.a` 공사관에 보호를 요청한다 | 40 | 외국 응답 .23 수락 후 실행 |
| `.11.b` 궁성 경비를 강화한다 | 40 | 조선 선택 시 실행 |
| `.11.c` 다른 궁으로 거처를 옮긴다 | 20 | 조선 선택 시 실행 |

```txt
scramble_for_korea_events.11 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.11.t
    desc = scramble_for_korea_events.11.d
    flavor = scramble_for_korea_events.11.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        has_law = law_type:law_monarchy
        radical_fraction = { value >= 0.20 }
        any_country = {
            sk_foreign_valid = yes
            var:scramble_for_korea_participants_influence >= 30
        }
        any_country = {
            sk_foreign_valid = yes
            var:scramble_for_korea_participants_influence >= 10
            count >= 2
        }
    }
    immediate = {
        set_variable = { name = sk_pending value = 11 days = 365 }
        random_country = {
            limit = { sk_foreign_valid = yes
        var:scramble_for_korea_participants_influence >= 30 }
            save_scope_as = sk_rival
        }
        random_country = {
            limit = { sk_foreign_valid = yes
        var:scramble_for_korea_participants_influence >= 10
        this != scope:sk_rival }
            save_scope_as = sk_actor
        }

    }
    # 공사관에 보호를 요청한다
    option = {
        name = scramble_for_korea_events.11.a

        ai_chance = { base = 40 }
        trigger = {
            sk_live_11 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 11 }
        }
        if = {
            limit = {
                sk_live_11 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 11 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 111 days = 365 } }
            save_scope_value_as = { name = sk_case value = 111 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 궁성 경비를 강화한다
    option = {
        name = scramble_for_korea_events.11.b

        ai_chance = { base = 40 }
        trigger = {
            sk_live_11 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 11 }
            c:KOR = { gold_reserves >= 25000 }
        }
        if = {
            limit = {
                sk_live_11 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 11 }
                c:KOR = { gold_reserves >= 25000 }
            }
            c:KOR = { add_treasury = -25000 }
            c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
            c:KOR = { add_modifier = { name = sk_guard days = 365 } }
            remove_variable = sk_pending
        }
    }
    # 다른 궁으로 거처를 옮긴다
    option = {
        name = scramble_for_korea_events.11.c
        default_option = yes
        ai_chance = { base = 20 }
        trigger = {
            sk_live_11 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 11 }
        }
        if = {
            limit = {
                sk_live_11 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 11 }
            }
            c:KOR = { add_modifier = { name = sk_relocation days = 180 } }
            remove_variable = sk_pending
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_11 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 11 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 11 }
            remove_variable = sk_pending
        }
    }
}
```

### `.12` 누구의 뒤에 서야 하는가

**역사적 배경:** 청은 박정양의 미국 공사 활동에 영약삼단을 요구했다. 청 공사관 선행 방문과 청 공사의 안내, 외교 석상에서의 서열, 중요 교섭의 사전 협의를 통해 조선의 독자 외교를 제한하려 한 사례다. 출처: [우리역사넷 — 박정양의 주미 외교와 청의 간섭](https://contents.history.go.kr/front/nh/view.do?levelId=nh_039_0030_0030).

**확정 동작:** 접수국은 청을 제외한 국제관계 기술 보유 관여국 중 균등 추첨한다. 독자 국서 제출의 비용은 외교력 -25/365일이다. 해외 사절단 일지·개혁 완료 변수를 사용하지 않는다.

**바닐라 참고:** ryukyu_rivalry.1.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.12.a` 청의 의전 요구를 따른다 | 40 | 조선 선택 시 실행 |
| `.12.b` 독자적으로 국서를 제출한다 | 35 | 조선 선택 시 실행 |
| `.12.c` 접수국에 독자 접견을 요청한다 | 25 | 외국 응답 .23 수락 후 실행 |

```txt
scramble_for_korea_events.12 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.12.t
    desc = scramble_for_korea_events.12.d
    flavor = scramble_for_korea_events.12.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        exists = c:CHI
        c:CHI = { sk_foreign_valid = yes OR = { c:KOR = { is_subject_of = c:CHI } var:scramble_for_korea_participants_influence >= 20 } }
        has_technology_researched = international_relations
        any_country = {
            sk_foreign_valid = yes
            NOT = { c:CHI ?= this }
            has_technology_researched = international_relations
        }
    }
    immediate = {
        set_variable = { name = sk_pending value = 12 days = 365 }
        c:CHI = { save_scope_as = sk_rival }
        random_country = {
            limit = {
                sk_foreign_valid = yes
                NOT = { c:CHI ?= this }
                has_technology_researched = international_relations
            }
            save_scope_as = sk_actor
        }

    }
    # 청의 의전 요구를 따른다
    option = {
        name = scramble_for_korea_events.12.a
        default_option = yes
        ai_chance = { base = 40 }
        trigger = {
            sk_live_12 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 12 }
        }
        if = {
            limit = {
                sk_live_12 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 12 }
            }
            c:KOR = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
            scope:sk_rival = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
            remove_variable = sk_pending
        }
    }
    # 독자적으로 국서를 제출한다
    option = {
        name = scramble_for_korea_events.12.b

        ai_chance = { base = 35 }
        trigger = {
            sk_live_12 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 12 }
        }
        if = {
            limit = {
                sk_live_12 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 12 }
            }
            c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
            scope:sk_rival = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
            c:KOR = { add_modifier = { name = sk_diplomatic_cost days = 365 } }
            remove_variable = sk_pending
        }
    }
    # 접수국에 독자 접견을 요청한다
    option = {
        name = scramble_for_korea_events.12.c

        ai_chance = { base = 25 }
        trigger = {
            sk_live_12 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 12 }
        }
        if = {
            limit = {
                sk_live_12 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 12 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 123 days = 365 } }
            save_scope_value_as = { name = sk_case value = 123 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_12 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 12 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 12 }
            remove_variable = sk_pending
        }
    }
}
```

### `.13` 백성의 쌀인가, 상인의 계약인가

**역사적 배경:** 함경도·황해도의 방곡령과 일본 상인의 손해배상 요구를 모티브로 한다. 식량 확보를 위한 수출 제한과 통상 조약·상인의 권익이 충돌한 사건이다. 출처: [우리역사넷 — 방곡령](https://contents.history.go.kr/mobile/kc/view.do?levelId=kc_i402320), [한국민족문화대백과사전 — 방곡령](https://encykorea.aks.ac.kr/Article/E0021663).

**확정 동작:** 조선이 자기 시장의 소유국일 때만 발생한다. 상대국도 자기 시장을 소유하고 조선 시장에서 곡물을 10단위 이상 수입해야 한다. 수출 금지 기능을 가정하지 않고 구휼 비용·농민 지지·외교 부담으로 방곡 분쟁의 결과를 표현한다. 선택으로 무역량이나 곡물 가격을 직접 고정하지 않는다.

**바닐라 참고:** trade_route_events.2 / .3; ep2_japan_events_03의 곡물 고가 사건.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.13.a` 구휼 비용을 부담하고 방곡 방침을 유지한다 | 35 | 조선 선택 시 실행 |
| `.13.b` 통상 요구를 받아들인다 | 40 | 조선 선택 시 실행 |
| `.13.c` 배상금 20,000을 제시한다 | 25 | 외국 응답 .23 수락 후 실행 |

```txt
scramble_for_korea_events.13 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.13.t
    desc = scramble_for_korea_events.13.d
    flavor = scramble_for_korea_events.13.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        capital.market = { owner = c:KOR mg:grain = { market_goods_pricier > 0.25 } }
        any_country = {
            sk_foreign_valid = yes
            capital.market = {
                owner = prev
                NOT = { this = c:KOR.capital.market }
                market_imports = { target = c:KOR.capital.market goods = grain value >= 10 }
            }
        }
    }
    immediate = {
        set_variable = { name = sk_pending value = 13 days = 365 }
        random_country = {
            limit = {
                sk_foreign_valid = yes
                capital.market = {
                    owner = prev
                    NOT = { this = c:KOR.capital.market }
                    market_imports = { target = c:KOR.capital.market goods = grain value >= 10 }
                }
            }
            save_scope_as = sk_actor
        }

    }
    # 구휼 비용을 부담하고 방곡 방침을 유지한다
    option = {
        name = scramble_for_korea_events.13.a

        ai_chance = { base = 35 }
        trigger = {
            sk_live_13 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 13 }
            c:KOR = { gold_reserves >= 15000 }
        }
        if = {
            limit = {
                sk_live_13 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 13 }
                c:KOR = { gold_reserves >= 15000 }
            }
            c:KOR = { add_treasury = -15000 }
            c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
            scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = -3 } }
            add_loyalists = { value = 0.02 pop_type = peasants }
            c:KOR = { add_modifier = { name = sk_diplomatic_cost days = 365 } }
            remove_variable = sk_pending
        }
    }
    # 통상 요구를 받아들인다
    option = {
        name = scramble_for_korea_events.13.b
        default_option = yes
        ai_chance = { base = 40 }
        trigger = {
            sk_live_13 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 13 }
        }
        if = {
            limit = {
                sk_live_13 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 13 }
            }
            c:KOR = { scramble_for_korea_change_influence = { AMOUNT = -3 } }
            scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
            add_radicals = { value = 0.02 pop_type = peasants }
            remove_variable = sk_pending
        }
    }
    # 배상금 20,000을 제시한다
    option = {
        name = scramble_for_korea_events.13.c

        ai_chance = { base = 25 }
        trigger = {
            sk_live_13 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 13 }
            c:KOR = { gold_reserves >= 20000 }
        }
        if = {
            limit = {
                sk_live_13 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 13 }
                c:KOR = { gold_reserves >= 20000 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 133 days = 365 } }
            save_scope_value_as = { name = sk_case value = 133 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_13 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 13 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 13 }
            remove_variable = sk_pending
        }
    }
}
```

### `.14` 우리 시장에 도는 남의 지폐

**역사적 배경:** 일본 제일은행이 1902년 은행권을 발행한 뒤 대한제국 정부와 상인들의 반발, 통용 금지와 1903년 금지 철회를 둘러싼 논란을 모티브로 한다. 출처: [우리역사넷 — 제일은행권과 화폐 정리](https://contents.history.go.kr/mobile/km/view.do?levelId=km_008_0050_0020_0030).

**확정 동작:** 금 보유고 100,000 미만과 조선 내 한 건물의 외국 소유 3레벨 이상을 함께 요구한다. 은행권 통용은 £25,000 지원과 주간 고정 수입 +100/730일로 구현하며 통화 종류를 새로 만들지 않는다. 자체 정비는 365일 뒤 영향력 +5와 주간 수입 +100/730일이다.

**바닐라 참고:** ryukyu_rivalry.1의 levels_owned_by_country; agitator_law_events_2의 add_treasury.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.14.a` 외국 은행권의 통용을 인정한다 | 40 | 외국 응답 .23 수락 후 실행 |
| `.14.b` 외국 은행권을 금지한다 | 35 | 조선 선택 시 실행 |
| `.14.c` 독자 화폐 정비에 40,000을 투입한다 | 25 | 조선 선택 시 실행 |

```txt
scramble_for_korea_events.14 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.14.t
    desc = scramble_for_korea_events.14.d
    flavor = scramble_for_korea_events.14.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        gold_reserves < 100000
        any_scope_building = {
            any_country = {
                sk_foreign_valid = yes
                prev = { levels_owned_by_country = { target = prev value >= 3 } }
            }
        }
    }
    immediate = {
        set_variable = { name = sk_pending value = 14 days = 365 }
        random_scope_building = {
            limit = {
                any_country = {
                    sk_foreign_valid = yes
                    prev = { levels_owned_by_country = { target = prev value >= 3 } }
                }
            }
            save_scope_as = sk_building
            random_country = {
                limit = {
                    sk_foreign_valid = yes
                    prev = { levels_owned_by_country = { target = prev value >= 3 } }
                }
                save_scope_as = sk_actor
            }
        }

    }
    # 외국 은행권의 통용을 인정한다
    option = {
        name = scramble_for_korea_events.14.a

        ai_chance = { base = 40 }
        trigger = {
            sk_live_14 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 14 }
        }
        if = {
            limit = {
                sk_live_14 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 14 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 141 days = 365 } }
            save_scope_value_as = { name = sk_case value = 141 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 외국 은행권을 금지한다
    option = {
        name = scramble_for_korea_events.14.b
        default_option = yes
        ai_chance = { base = 35 }
        trigger = {
            sk_live_14 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 14 }
        }
        if = {
            limit = {
                sk_live_14 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 14 }
            }
            c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
            scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = -3 } }
            add_radicals = { value = 0.01 }
            remove_variable = sk_pending
        }
    }
    # 독자 화폐 정비에 40,000을 투입한다
    option = {
        name = scramble_for_korea_events.14.c

        ai_chance = { base = 25 }
        trigger = {
            sk_live_14 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 14 }
            c:KOR = { gold_reserves >= 40000 }
        }
        if = {
            limit = {
                sk_live_14 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 14 }
                c:KOR = { gold_reserves >= 40000 }
            }
            c:KOR = { add_treasury = -40000 }
            c:KOR = {
                set_variable = sk_job_143
                trigger_event = { on_action = sk_finish_143 days = 365 }
            }
            remove_variable = sk_pending
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_14 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 14 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 14 }
            remove_variable = sk_pending
        }
    }
}
```

### `.15` 전보는 어느 길로 가는가

**역사적 배경:** 청과 연결된 서쪽 전신망과 조선의 남쪽 전신망 건설을 바탕으로, 통신망의 경로와 운영권이 외교적 의존에 미치는 영향을 다룬다. 출처: [국가기록원 — 전신 관련 기록](https://archives.go.kr/next/newsearch/listSubjectDescription.do?id=010910&pageFlag=A&sitePage=1-2-1), [한국민족문화대백과사전 — 전보총국](https://encykorea.aks.ac.kr/Article/E0049512).

**확정 동작:** 실제 기술 키는 electric_telegraph다. 대상은 조선의 편입주 한 곳이다. 모든 완공 효과는 해당 주의 기반시설 +5/1,825일로 고정한다. 전신 건물을 생성하지 않는다. 기존 대체국 선택은 국가 선택 창이 없는 일반 이벤트에서 확정적으로 처리하도록 공동 건설 선택으로 구체화한다.

**바닐라 참고:** trains.1의 주 선택; production_tech_events.601의 기술 조건.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.15.a` 외국망 연결을 제안한다 | 35 | 외국 응답 .23 수락 후 실행 |
| `.15.b` 공동 건설과 조선 측 관리를 제안한다 | 25 | 외국 응답 .23 수락 후 실행 |
| `.15.c` 국비 50,000으로 건설한다 | 30 | 조선 선택 시 실행 |
| `.15.d` 이번에는 보류한다 | 10 | 조선 선택 시 실행 |

```txt
scramble_for_korea_events.15 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.15.t
    desc = scramble_for_korea_events.15.d
    flavor = scramble_for_korea_events.15.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        has_technology_researched = electric_telegraph
        any_scope_state = {
            is_incorporated = yes
            NOT = { has_modifier = sk_telegraph }
        }
        any_country = {
            sk_foreign_valid = yes
            has_technology_researched = electric_telegraph
        }
    }
    immediate = {
        set_variable = { name = sk_pending value = 15 days = 365 }
        random_scope_state = {
            limit = {
                is_incorporated = yes
                NOT = { has_modifier = sk_telegraph }
            }
            save_scope_as = sk_state
        }
        random_country = {
            limit = {
                sk_foreign_valid = yes
                has_technology_researched = electric_telegraph
            }
            save_scope_as = sk_actor
        }

    }
    # 외국망 연결을 제안한다
    option = {
        name = scramble_for_korea_events.15.a

        ai_chance = { base = 35 }
        trigger = {
            sk_live_15 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 15 }
            c:KOR = { gold_reserves >= 10000 }
        }
        if = {
            limit = {
                sk_live_15 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 15 }
                c:KOR = { gold_reserves >= 10000 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 151 days = 365 } }
            save_scope_value_as = { name = sk_case value = 151 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 공동 건설과 조선 측 관리를 제안한다
    option = {
        name = scramble_for_korea_events.15.b

        ai_chance = { base = 25 }
        trigger = {
            sk_live_15 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 15 }
            c:KOR = { gold_reserves >= 25000 }
        }
        if = {
            limit = {
                sk_live_15 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 15 }
                c:KOR = { gold_reserves >= 25000 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 152 days = 365 } }
            save_scope_value_as = { name = sk_case value = 152 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 국비 50,000으로 건설한다
    option = {
        name = scramble_for_korea_events.15.c

        ai_chance = { base = 30 }
        trigger = {
            sk_live_15 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 15 }
            c:KOR = { gold_reserves >= 50000 }
        }
        if = {
            limit = {
                sk_live_15 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 15 }
                c:KOR = { gold_reserves >= 50000 }
            }
            c:KOR = { add_treasury = -50000 }
            c:KOR = {
                set_variable = sk_job_153
                trigger_event = { on_action = sk_finish_153 days = 365 }
            }
            remove_variable = sk_pending
        }
    }
    # 이번에는 보류한다
    option = {
        name = scramble_for_korea_events.15.d
        default_option = yes
        ai_chance = { base = 10 }
        trigger = {
            sk_live_15 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 15 }
        }
        if = {
            limit = {
                sk_live_15 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 15 }
            }
            remove_variable = sk_pending
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_15 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 15 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 15 }
            remove_variable = sk_pending
        }
    }
}
```

### `.16` 해관의 장부를 쥔 손

**역사적 배경:** 청의 이홍장이 추천한 독일인 묄렌도르프가 조선의 외교·통상 업무와 해관 운영에 관여한 사례를 모티브로 한다. 고문의 국적과 그를 추천한 국가의 이해관계는 구분한다. 출처: [한국학중앙연구원 한국외교사전 — 묄렌도르프](https://waks.aks.ac.kr/dir/achieveView.aspx?dataID=AKS-2007-HZ-2002_DIC%40FND_DIC_OKY_GOKS_0065).

**확정 동작:** 조선 소유 시장의 총 수출 100단위 이상을 해관 정비 수요로 삼는다. 전권 고문은 행정력 +25와 주간 수입 +100, 자문은 행정력 +25, 자체 정비는 180일 뒤 행정력 +50이다. 모두 730일 지속한다. 추천국을 sk_actor로 저장하며 고문의 국적에 점수를 주지 않는다.

**바닐라 참고:** 00_lobbies_events_04의 market_exports; ryukyu_rivalry.1.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.16.a` 고문에게 해관 운영을 맡긴다 | 35 | 외국 응답 .23 수락 후 실행 |
| `.16.b` 10,000에 기술 자문만 요청한다 | 25 | 외국 응답 .23 수락 후 실행 |
| `.16.c` 25,000으로 조선인 해관을 정비한다 | 30 | 조선 선택 시 실행 |
| `.16.d` 인사를 보류한다 | 10 | 조선 선택 시 실행 |

```txt
scramble_for_korea_events.16 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.16.t
    desc = scramble_for_korea_events.16.d
    flavor = scramble_for_korea_events.16.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        capital.market = { owner = c:KOR market_exports = { value >= 100 } }
        NOT = { has_variable = sk_customs_partner }
        any_country = {
            sk_foreign_valid = yes
            has_technology_researched = international_relations
        }
    }
    immediate = {
        set_variable = { name = sk_pending value = 16 days = 365 }
        random_country = {
            limit = {
                sk_foreign_valid = yes
                has_technology_researched = international_relations
            }
            save_scope_as = sk_actor
        }

    }
    # 고문에게 해관 운영을 맡긴다
    option = {
        name = scramble_for_korea_events.16.a

        ai_chance = { base = 35 }
        trigger = {
            sk_live_16 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 16 }
        }
        if = {
            limit = {
                sk_live_16 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 16 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 161 days = 365 } }
            save_scope_value_as = { name = sk_case value = 161 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 10,000에 기술 자문만 요청한다
    option = {
        name = scramble_for_korea_events.16.b

        ai_chance = { base = 25 }
        trigger = {
            sk_live_16 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 16 }
            c:KOR = { gold_reserves >= 10000 }
        }
        if = {
            limit = {
                sk_live_16 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 16 }
                c:KOR = { gold_reserves >= 10000 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 162 days = 365 } }
            save_scope_value_as = { name = sk_case value = 162 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 25,000으로 조선인 해관을 정비한다
    option = {
        name = scramble_for_korea_events.16.c

        ai_chance = { base = 30 }
        trigger = {
            sk_live_16 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 16 }
            c:KOR = { gold_reserves >= 25000 }
        }
        if = {
            limit = {
                sk_live_16 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 16 }
                c:KOR = { gold_reserves >= 25000 }
            }
            c:KOR = { add_treasury = -25000 }
            c:KOR = {
                set_variable = sk_job_163
                trigger_event = { on_action = sk_finish_163 days = 180 }
            }
            remove_variable = sk_pending
        }
    }
    # 인사를 보류한다
    option = {
        name = scramble_for_korea_events.16.d
        default_option = yes
        ai_chance = { base = 10 }
        trigger = {
            sk_live_16 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 16 }
        }
        if = {
            limit = {
                sk_live_16 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 16 }
            }
            remove_variable = sk_pending
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_16 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 16 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 16 }
            remove_variable = sk_pending
        }
    }
}
```

### `.17` 철길의 주인은 누구인가

**역사적 배경:** 1896년 미국인 모스가 경인철도 부설권을 얻었으나 자금 조달에 어려움을 겪었고, 이후 일본 측으로 부설권이 넘어간 사례를 모티브로 한다. 출처: [한국민족문화대백과사전 — 경인선](https://encykorea.aks.ac.kr/Article/E0002748).

**확정 동작:** 철도 없는 건설 가능 주 한 곳을 고른다. 365일 뒤에도 조선 소유·철도 없음·건설 가능이면 바닐라 meiji.8처럼 1레벨 철도를 생성한다. 이미 철도가 생겼거나 주를 잃었으면 추가 생성·완공 점수 없이 종료하며 계약금은 환급하지 않는다. 이 판본은 국가 간 자금 부담과 정치적 이권만 표현한다. 건물 지분의 강제 이전·제3국 매각 후속 사건은 포함하지 않는다.

**바닐라 참고:** meiji.8; documentation/effects.log의 create_building.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.17.a` 외자 부설 계약을 제안한다 | 35 | 외국 응답 .23 수락 후 실행 |
| `.17.b` 공동 출자 계약을 제안한다 | 25 | 외국 응답 .23 수락 후 실행 |
| `.17.c` 국비 75,000으로 건설한다 | 30 | 조선 선택 시 실행 |
| `.17.d` 건설을 보류한다 | 10 | 조선 선택 시 실행 |

```txt
scramble_for_korea_events.17 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.17.t
    desc = scramble_for_korea_events.17.d
    flavor = scramble_for_korea_events.17.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        has_technology_researched = railways
        any_scope_state = {
            NOT = { has_building = building_railway }
            can_construct_building = building_railway
        }
        any_country = {
            sk_foreign_valid = yes
            has_technology_researched = railways
        }
    }
    immediate = {
        set_variable = { name = sk_pending value = 17 days = 365 }
        random_scope_state = {
            limit = {
                NOT = { has_building = building_railway }
                can_construct_building = building_railway
            }
            save_scope_as = sk_state
        }
        random_country = {
            limit = {
                sk_foreign_valid = yes
                has_technology_researched = railways
            }
            save_scope_as = sk_actor
        }

    }
    # 외자 부설 계약을 제안한다
    option = {
        name = scramble_for_korea_events.17.a

        ai_chance = { base = 35 }
        trigger = {
            sk_live_17 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 17 }
            c:KOR = { gold_reserves >= 25000 }
        }
        if = {
            limit = {
                sk_live_17 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 17 }
                c:KOR = { gold_reserves >= 25000 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 171 days = 365 } }
            save_scope_value_as = { name = sk_case value = 171 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 공동 출자 계약을 제안한다
    option = {
        name = scramble_for_korea_events.17.b

        ai_chance = { base = 25 }
        trigger = {
            sk_live_17 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 17 }
            c:KOR = { gold_reserves >= 35000 }
        }
        if = {
            limit = {
                sk_live_17 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 17 }
                c:KOR = { gold_reserves >= 35000 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 172 days = 365 } }
            save_scope_value_as = { name = sk_case value = 172 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 국비 75,000으로 건설한다
    option = {
        name = scramble_for_korea_events.17.c

        ai_chance = { base = 30 }
        trigger = {
            sk_live_17 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 17 }
            c:KOR = { gold_reserves >= 75000 }
            exists = scope:sk_state
            scope:sk_state = { owner = c:KOR }
            scope:sk_state = {
                NOT = { has_building = building_railway }
                can_construct_building = building_railway
            }
        }
        if = {
            limit = {
                sk_live_17 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 17 }
                c:KOR = { gold_reserves >= 75000 }
                exists = scope:sk_state
                scope:sk_state = { owner = c:KOR }
                scope:sk_state = {
                    NOT = { has_building = building_railway }
                    can_construct_building = building_railway
                }
            }
            c:KOR = { add_treasury = -75000 }
            c:KOR = {
                set_variable = sk_job_173
                trigger_event = { on_action = sk_finish_173 days = 365 }
            }
            remove_variable = sk_pending
        }
    }
    # 건설을 보류한다
    option = {
        name = scramble_for_korea_events.17.d
        default_option = yes
        ai_chance = { base = 10 }
        trigger = {
            sk_live_17 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 17 }
        }
        if = {
            limit = {
                sk_live_17 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 17 }
            }
            remove_variable = sk_pending
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_17 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 17 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 17 }
            remove_variable = sk_pending
        }
    }
}
```

### `.18` 산 아래 잠든 황금

**역사적 배경:** 1895년 조선이 미국 측에 운산 금광 채굴권을 허가한 사건을 모티브로 한다. 기술·자본 도입과 장기적인 광산 이권 양여가 함께 이루어지는 선택이다. 출처: [한국학중앙연구원 한국외교사전 — 운산금광채굴권](https://waks.aks.ac.kr/dir/achieveView.aspx?dataID=AKS-2007-HZ-2002_DIC%40FND_DIC_OKY_GOKS_0138).

**확정 동작:** 실제 금광 1레벨 이상을 요구한다. 미발견 자원·금광 미보유 조선에는 발생하지 않는다. 장기 계약은 처리율 +10%, 공동 계약은 +5%, 직접 정비는 180일 뒤 +10%이며 1,825일 지속한다. 건물 소유권·지분별 배당률을 바꾸는 효과는 없다. 운산은 모티브이며 선택한 실제 금광의 지역명을 표시한다.

**바닐라 참고:** production_tech_events.601의 광산 선택; 02_event_modifiers의 building_throughput_add.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.18.a` 장기 채굴·설비 계약을 제안한다 | 35 | 외국 응답 .23 수락 후 실행 |
| `.18.b` 수익 배분 계약을 제안한다 | 25 | 외국 응답 .23 수락 후 실행 |
| `.18.c` 40,000으로 직접 설비를 정비한다 | 30 | 조선 선택 시 실행 |
| `.18.d` 채굴 계약을 보류한다 | 10 | 조선 선택 시 실행 |

```txt
scramble_for_korea_events.18 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.18.t
    desc = scramble_for_korea_events.18.d
    flavor = scramble_for_korea_events.18.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        any_scope_building = { is_building_type = building_gold_mine
        level >= 1 }
        NOT = { has_variable = sk_mine_partner }
        any_country = {
            sk_foreign_valid = yes
        }
    }
    immediate = {
        set_variable = { name = sk_pending value = 18 days = 365 }
        random_scope_building = { limit = { is_building_type = building_gold_mine
        level >= 1 } save_scope_as = sk_building }
        random_country = {
            limit = {
                sk_foreign_valid = yes
            }
            save_scope_as = sk_actor
        }

    }
    # 장기 채굴·설비 계약을 제안한다
    option = {
        name = scramble_for_korea_events.18.a

        ai_chance = { base = 35 }
        trigger = {
            sk_live_18 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 18 }
            c:KOR = { gold_reserves >= 10000 }
        }
        if = {
            limit = {
                sk_live_18 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 18 }
                c:KOR = { gold_reserves >= 10000 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 181 days = 365 } }
            save_scope_value_as = { name = sk_case value = 181 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 수익 배분 계약을 제안한다
    option = {
        name = scramble_for_korea_events.18.b

        ai_chance = { base = 25 }
        trigger = {
            sk_live_18 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 18 }
            c:KOR = { gold_reserves >= 20000 }
        }
        if = {
            limit = {
                sk_live_18 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 18 }
                c:KOR = { gold_reserves >= 20000 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 182 days = 365 } }
            save_scope_value_as = { name = sk_case value = 182 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 40,000으로 직접 설비를 정비한다
    option = {
        name = scramble_for_korea_events.18.c

        ai_chance = { base = 30 }
        trigger = {
            sk_live_18 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 18 }
            c:KOR = { gold_reserves >= 40000 }
        }
        if = {
            limit = {
                sk_live_18 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 18 }
                c:KOR = { gold_reserves >= 40000 }
            }
            c:KOR = { add_treasury = -40000 }
            c:KOR = {
                set_variable = sk_job_183
                trigger_event = { on_action = sk_finish_183 days = 180 }
            }
            remove_variable = sk_pending
        }
    }
    # 채굴 계약을 보류한다
    option = {
        name = scramble_for_korea_events.18.d
        default_option = yes
        ai_chance = { base = 10 }
        trigger = {
            sk_live_18 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 18 }
        }
        if = {
            limit = {
                sk_live_18 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 18 }
            }
            remove_variable = sk_pending
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_18 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 18 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 18 }
            remove_variable = sk_pending
        }
    }
}
```

### `.19` 섬에 내려진 낯선 깃발

**역사적 배경:** 영국이 러시아의 진출을 견제한다는 명분으로 1885~1887년 거문도를 점령한 사건을 모티브로 한다. 조선의 동의 없이 이루어진 점령과 그 철수를 둘러싼 외교 교섭을 다룬다. 출처: [한국민족문화대백과사전 — 거문도사건](https://encykorea.aks.ac.kr/Article/E0001825).

**확정 동작:** 조선 해안주·해군 투사력 양수인 영향력 20 이상 관여국·다른 관여국 한 나라가 필요하다. 발생 시 점령국에 위신 +5/730일의 거점 효과와 악명 +5, 조선 영향력 -5를 적용한다. 이는 사건으로 발생한 임시 군사 거점이며 지도상 점령·주 소유권·전선을 변경하지 않는다. 공동 항의의 수락은 중재국 +3, 조선 외교력 +25/365일까지만 주며 철수를 보장하지 않는다.

**바닐라 참고:** ryukyu_rivalry.6의 change_infamy; ryukyu_rivalry.1의 외교 대응.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.19.a` 점령국에 철수를 요구한다 | 40 | 외국 응답 .23 수락 후 실행 |
| `.19.b` 제3국에 공동 항의를 요청한다 | 35 | 외국 응답 .23 수락 후 실행 |
| `.19.c` 한시적인 주둔을 묵인한다 | 25 | 조선 선택 시 실행 |

```txt
scramble_for_korea_events.19 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.19.t
    desc = scramble_for_korea_events.19.d
    flavor = scramble_for_korea_events.19.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        any_scope_state = {
            is_coastal = yes
        }
        NOT = { has_variable = sk_base_partner }
        any_country = {
            sk_foreign_valid = yes
            naval_power_projection > 0
            var:scramble_for_korea_participants_influence >= 20
        }
        any_country = { sk_foreign_valid = yes count >= 2 }
    }
    immediate = {
        set_variable = { name = sk_pending value = 19 days = 365 }
        random_scope_state = {
            limit = {
                is_coastal = yes
            }
            save_scope_as = sk_state
        }
        random_country = {
            limit = {
                sk_foreign_valid = yes
                naval_power_projection > 0
                var:scramble_for_korea_participants_influence >= 20
            }
            save_scope_as = sk_actor
        }
        random_country = {
            limit = { sk_foreign_valid = yes this != scope:sk_actor }
            save_scope_as = sk_rival
        }
        scope:sk_actor = { add_modifier = { name = sk_base days = 730 } }
        c:KOR = { set_variable = { name = sk_base_partner value = scope:sk_actor days = 730 } }
        scope:sk_actor = { change_infamy = 5 }
        c:KOR = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
    }
    # 점령국에 철수를 요구한다
    option = {
        name = scramble_for_korea_events.19.a

        ai_chance = { base = 40 }
        trigger = {
            sk_live_19 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 19 }
        }
        if = {
            limit = {
                sk_live_19 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 19 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 191 days = 365 } }
            save_scope_value_as = { name = sk_case value = 191 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 제3국에 공동 항의를 요청한다
    option = {
        name = scramble_for_korea_events.19.b

        ai_chance = { base = 35 }
        trigger = {
            sk_live_19 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 19 }
        }
        if = {
            limit = {
                sk_live_19 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 19 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 192 days = 365 } }
            save_scope_value_as = { name = sk_case value = 192 }
            scope:sk_rival = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 한시적인 주둔을 묵인한다
    option = {
        name = scramble_for_korea_events.19.c
        default_option = yes
        ai_chance = { base = 25 }
        trigger = {
            sk_live_19 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 19 }
        }
        if = {
            limit = {
                sk_live_19 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 19 }
            }
            scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
            c:KOR = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
            remove_variable = sk_pending
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_19 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 19 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 19 }
            remove_variable = sk_pending
        }
    }
}
```

### `.20` 벌목장의 포대

**역사적 배경:** 1903년 러시아의 용암포 진출 과정에서 목재 사업과 토지 대여 문제가 군사 거점 구축으로 확대된 사례를 모티브로 한다. 출처: [한국민족문화대백과사전 — 용암포사건](https://encykorea.aks.ac.kr/Article/E0039596).

**확정 동작:** 해안주 벌목장 중 외국이 실제로 1레벨 이상 소유한 곳을 고른다. 양허를 새로 가정하지 않는다. 군사화 수락은 .19와 같은 거점 효과를 730일 적용한다. 개방 협상은 한 나라의 독점적 정치 영향력을 낮추는 처리이며 무역항 건물·조약항을 자동 생성하지 않는다. 행정 비용은 -25/365일이다.

**바닐라 참고:** ryukyu_rivalry.1의 소유 레벨; trains.1의 주 스코프.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.20.a` 군사 시설 확장 금지를 요구한다 | 40 | 외국 응답 .23 수락 후 실행 |
| `.20.b` 군사 거점 설치를 허용한다 | 25 | 조선 선택 시 실행 |
| `.20.c` 다른 관여국에도 상업 접근을 허용하도록 협상한다 | 35 | 외국 응답 .23 수락 후 실행 |

```txt
scramble_for_korea_events.20 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.20.t
    desc = scramble_for_korea_events.20.d
    flavor = scramble_for_korea_events.20.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        any_scope_building = {
            is_building_type = building_logging_camp
            state = { is_coastal = yes }
            any_country = {
                sk_foreign_valid = yes
                prev = { levels_owned_by_country = { target = prev value >= 1 } }
            }
        }
        NOT = { has_variable = sk_base_partner }
        any_country = { sk_foreign_valid = yes count >= 2 }
    }
    immediate = {
        set_variable = { name = sk_pending value = 20 days = 365 }
        random_scope_building = {
            limit = {
                is_building_type = building_logging_camp
                state = { is_coastal = yes }
                any_country = {
                    sk_foreign_valid = yes
                    prev = { levels_owned_by_country = { target = prev value >= 1 } }
                }
            }
            save_scope_as = sk_building
            random_country = {
                limit = {
                    sk_foreign_valid = yes
                    prev = { levels_owned_by_country = { target = prev value >= 1 } }
                }
                save_scope_as = sk_actor
            }
        }
        scope:sk_building.state = { save_scope_as = sk_state }
        random_country = {
            limit = { sk_foreign_valid = yes this != scope:sk_actor }
            save_scope_as = sk_rival
        }

    }
    # 군사 시설 확장 금지를 요구한다
    option = {
        name = scramble_for_korea_events.20.a

        ai_chance = { base = 40 }
        trigger = {
            sk_live_20 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 20 }
        }
        if = {
            limit = {
                sk_live_20 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 20 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 201 days = 365 } }
            save_scope_value_as = { name = sk_case value = 201 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 군사 거점 설치를 허용한다
    option = {
        name = scramble_for_korea_events.20.b
        default_option = yes
        ai_chance = { base = 25 }
        trigger = {
            sk_live_20 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 20 }
        }
        if = {
            limit = {
                sk_live_20 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 20 }
            }
            scope:sk_actor = { add_modifier = { name = sk_base days = 730 } }
            c:KOR = { set_variable = { name = sk_base_partner value = scope:sk_actor days = 730 } }
            scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 10 } }
            c:KOR = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
            remove_variable = sk_pending
        }
    }
    # 다른 관여국에도 상업 접근을 허용하도록 협상한다
    option = {
        name = scramble_for_korea_events.20.c

        ai_chance = { base = 35 }
        trigger = {
            sk_live_20 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 20 }
        }
        if = {
            limit = {
                sk_live_20 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 20 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 203 days = 365 } }
            save_scope_value_as = { name = sk_case value = 203 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_20 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 20 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 20 }
            remove_variable = sk_pending
        }
    }
}
```

### `.21` 종로에 모인 목소리

**역사적 배경:** 1898년 만민공동회가 러시아 군사교관·재정고문의 철수와 절영도 조차 반대 등 자주권 수호를 요구한 사례를 모티브로 한다. 출처: [우리역사넷 — 만민공동회](https://contents.history.go.kr/front/kc/printViewPopup.do?levelId=kc_i401700).

**확정 동작:** 급진파 15% 이상, 비주변 지식인, 실제 진행 중인 거점·해관·은행 계약 중 하나가 필요하다. 대상 우선순위는 군사 거점 → 해관 고문 → 은행이다. 한 번의 청원은 한 계약만 해제한다. 국내 개편은 권익을 회수하지 않으며 £10,000, 권위 -25/365일, 충성파 전환 1%, 조선 +2로 고정한다.

**바닐라 참고:** gg_korea.4의 급진파·IG 조건과 청원 선택.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.21.a` 고문·거점의 철수 협상을 요청한다 | 40 | 외국 응답 .23 수락 후 실행 |
| `.21.b` 민회 대표들과 국내 개편을 협의한다 | 40 | 조선 선택 시 실행 |
| `.21.c` 집회를 해산한다 | 20 | 조선 선택 시 실행 |

```txt
scramble_for_korea_events.21 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.21.t
    desc = scramble_for_korea_events.21.d
    flavor = scramble_for_korea_events.21.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        radical_fraction = { value >= 0.15 }
        ig:ig_intelligentsia = { ig_counts_as_marginal = no }
        OR = {
            AND = { exists = var:sk_base_partner var:sk_base_partner = { sk_foreign_valid = yes } }
            AND = { exists = var:sk_customs_partner var:sk_customs_partner = { sk_foreign_valid = yes } }
            AND = { exists = var:sk_bank_partner var:sk_bank_partner = { sk_foreign_valid = yes } }
        }
    }
    immediate = {
        set_variable = { name = sk_pending value = 21 days = 365 }
        if = {
            limit = { exists = var:sk_base_partner var:sk_base_partner = { sk_foreign_valid = yes } }
            var:sk_base_partner = { save_scope_as = sk_actor }
            save_scope_value_as = { name = sk_petition_kind value = 1 }
        }
        else_if = {
            limit = { exists = var:sk_customs_partner var:sk_customs_partner = { sk_foreign_valid = yes } }
            var:sk_customs_partner = { save_scope_as = sk_actor }
            save_scope_value_as = { name = sk_petition_kind value = 2 }
        }
        else_if = {
            limit = { exists = var:sk_bank_partner var:sk_bank_partner = { sk_foreign_valid = yes } }
            var:sk_bank_partner = { save_scope_as = sk_actor }
            save_scope_value_as = { name = sk_petition_kind value = 3 }
        }


    }
    # 고문·거점의 철수 협상을 요청한다
    option = {
        name = scramble_for_korea_events.21.a

        ai_chance = { base = 40 }
        trigger = {
            sk_live_21 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 21 }
        }
        if = {
            limit = {
                sk_live_21 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 21 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 211 days = 365 } }
            save_scope_value_as = { name = sk_case value = 211 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 민회 대표들과 국내 개편을 협의한다
    option = {
        name = scramble_for_korea_events.21.b

        ai_chance = { base = 40 }
        trigger = {
            sk_live_21 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 21 }
            c:KOR = { gold_reserves >= 10000 }
        }
        if = {
            limit = {
                sk_live_21 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 21 }
                c:KOR = { gold_reserves >= 10000 }
            }
            c:KOR = { add_treasury = -10000 }
            c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 2 } }
            add_loyalists = { value = 0.01 }
            c:KOR = { add_modifier = { name = sk_assembly_compromise days = 365 } }
            remove_variable = sk_pending
        }
    }
    # 집회를 해산한다
    option = {
        name = scramble_for_korea_events.21.c
        default_option = yes
        ai_chance = { base = 20 }
        trigger = {
            sk_live_21 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 21 }
        }
        if = {
            limit = {
                sk_live_21 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 21 }
            }
            add_radicals = { value = 0.03 }
            c:KOR = { add_modifier = { name = sk_guard days = 365 } }
            remove_variable = sk_pending
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_21 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 21 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 21 }
            remove_variable = sk_pending
        }
    }
}
```

### `.22` 다른 나라에 허락했다면

**역사적 배경:** 미국이 최혜국 대우 조항을 근거로 1883년 제2차 조영수호통상조약의 상업상 권리를 균점하려 한 사례를 모티브로 한다. 출처: [우리역사넷 — 조미 수호 통상 조약](https://contents.history.go.kr/front/hm/view.do?levelId=hm_115_0060).

**확정 동작:** 별도의 최혜국 법률 상태를 발명하지 않고 실제 trade_privilege 조약을 기준으로 동등 대우 요구를 구현한다. 기존 수혜국과 신규 요구국은 서로 다르다. 원조약은 통상특권 조항 하나뿐인 조약으로 한정하므로 철회 시 방위·투자 조항을 함께 없애지 않는다. 수락한 신규 조약의 구속 기간은 2년이며 2년 뒤 자동 해지는 아니다. 조선이 종속국이라 체결 권한이 없으면 can_create_treaty가 신규 체결 선택을 막는다.

**바닐라 참고:** 00_lobbies_events_04의 can_create_treaty; persia_events.4의 create_treaty; ryukyu_rivalry.7의 withdraw.

| 선택 | AI 가중치 | 처리 |
|---|---:|---|
| `.22.a` 동등한 통상 특권을 제안한다 | 35 | 외국 응답 .23 수락 후 실행 |
| `.22.b` 동등 대우 요구를 거절한다 | 40 | 조선 선택 시 실행 |
| `.22.c` 기존 수혜국에 특권 철회를 제안한다 | 25 | 외국 응답 .23 수락 후 실행 |

```txt
scramble_for_korea_events.22 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.22.t
    desc = scramble_for_korea_events.22.d
    flavor = scramble_for_korea_events.22.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    cooldown = { days = 100000 }
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
        has_technology_researched = international_relations
        any_scope_treaty = {
            any_scope_article = { count = 1 }
            any_scope_article = { has_type = trade_privilege source_country = c:KOR target_country = { sk_foreign_valid = yes } }
        }
        any_country = {
            sk_foreign_valid = yes
            NOT = { has_treaty_trade_privilege_with = { TARGET = c:KOR } }
            has_technology_researched = international_relations
        }
    }
    immediate = {
        set_variable = { name = sk_pending value = 22 days = 365 }
        random_scope_treaty = {
            limit = { any_scope_article = { count = 1 }
        any_scope_article = { has_type = trade_privilege source_country = c:KOR target_country = { sk_foreign_valid = yes } } }
            save_scope_as = sk_treaty
            every_scope_article = { target_country = { save_scope_as = sk_rival } }
        }
        random_country = {
            limit = { sk_foreign_valid = yes
        NOT = { has_treaty_trade_privilege_with = { TARGET = c:KOR } }
        has_technology_researched = international_relations this != scope:sk_rival }
            save_scope_as = sk_actor
        }

    }
    # 동등한 통상 특권을 제안한다
    option = {
        name = scramble_for_korea_events.22.a

        ai_chance = { base = 35 }
        trigger = {
            sk_live_22 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 22 }
            can_create_treaty = {
                first_country = c:KOR
                second_country = scope:sk_actor
                is_draft = no
                binding_period = { years = 2 }
                articles_to_create = {
                    { article = trade_privilege source_country = c:KOR target_country = scope:sk_actor }
                }
            }
        }
        if = {
            limit = {
                sk_live_22 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 22 }
                can_create_treaty = {
                    first_country = c:KOR
                    second_country = scope:sk_actor
                    is_draft = no
                    binding_period = { years = 2 }
                    articles_to_create = {
                        { article = trade_privilege source_country = c:KOR target_country = scope:sk_actor }
                    }
                }
            }
            c:KOR = { set_variable = { name = sk_pending value = 221 days = 365 } }
            save_scope_value_as = { name = sk_case value = 221 }
            scope:sk_actor = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    # 동등 대우 요구를 거절한다
    option = {
        name = scramble_for_korea_events.22.b
        default_option = yes
        ai_chance = { base = 40 }
        trigger = {
            sk_live_22 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 22 }
        }
        if = {
            limit = {
                sk_live_22 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 22 }
            }
            change_relations = { country = scope:sk_actor value = -10 }
            remove_variable = sk_pending
        }
    }
    # 기존 수혜국에 특권 철회를 제안한다
    option = {
        name = scramble_for_korea_events.22.c

        ai_chance = { base = 25 }
        trigger = {
            sk_live_22 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 22 }
        }
        if = {
            limit = {
                sk_live_22 = yes
                c:KOR = { has_variable = sk_pending var:sk_pending = 22 }
            }
            c:KOR = { set_variable = { name = sk_pending value = 223 days = 365 } }
            save_scope_value_as = { name = sk_case value = 223 }
            scope:sk_rival = {
                save_scope_as = sk_respondent
                trigger_event = { id = scramble_for_korea_events.23 popup = yes }
            }
        }
    }
    option = {
        name = scramble_for_korea_events.cancel
        default_option = yes
        ai_chance = { base = 100 }
        trigger = { NOT = { AND = {
            sk_live_22 = yes
            c:KOR = { has_variable = sk_pending var:sk_pending = 22 }
        } } }
        if = {
            limit = { has_variable = sk_pending var:sk_pending = 22 }
            remove_variable = sk_pending
        }
    }
}
```

## 7. 전체 진행·이벤트 흐름도

실선은 기존 일지의 설계 흐름이다. 점선은 외부 상태 변화 또는 ‘추가 계획’으로 표시한 미구현 사건 경로다. 11~22번은 아래 점선 경로에만 추가하며, 종료를 일으키지 않는 사건 선택은 공통 갱신 단계로 돌아간다.

### 참여국 목록과 GUI 동기화

```mermaid
flowchart TD
    T["시작 / 주간 동기화"] --> TAG{"국가별 분기"}
    TAG -->|조선| CORE["기본 관여국"]
    TAG -->|청| CHI{"중국 붕괴 없음 AND<br/>조선 종주국 또는 승인국?"}
    TAG -->|일본| JAP{"japan_restoration_complete 있음<br/>AND 승인국?"}
    CHI -->|예| JOIN
    JAP -->|예| JOIN
    CHI -->|아니오| EXIT
    JAP -->|아니오| EXIT
    TAG -->|그 밖의 국가만| ACTIVE{"현재 JE 관여국인가?"}
    ACTIVE -->|아니오| EL{"열강이며<br/>지역 이해관계 3단계 이상?"}
    ACTIVE -->|예| KEEP{"열강이며<br/>지역 이해관계 2단계 이상?"}
    CORE --> JOIN["JE 관여국으로 등록"]
    EL -->|예| JOIN
    EL -->|아니오| WAIT["미참여 유지"]
    KEEP -->|아니오| EXIT["JE 관여국에서 제거"]
    KEEP -->|예| RETAIN["관여국 유지 / 기존 영향력 유지<br/>변수 누락 시에만 보완"]
    JOIN --> INIT["등록된 국가에 영향력 변수 추가<br/>기존 값은 유지"]
    EXIT --> CLEAR["탈락국의 영향력 변수 제거"]
    WAIT --> CLEAR
    INIT --> GUI["custom_gui JE 관여국 반복<br/>관여국당 한 행·한 막대"]
    CLEAR --> GUI
    RETAIN --> GUI
    GUI --> VALUE["국가 변수 값으로 0~100 채움 표시<br/>0인 참가국도 표시"]
    SCORE["월간 계산·개혁 보상<br/>국가별 영향력 갱신"] --> VALUE
    EXIT -->|다음 주기에 국가별 재검사| TAG
```

### 모든 계획 이벤트와 결말

```mermaid
flowchart TD
    A{"활성화 3조건 충족?"} -->|아니오| WAIT["비활성 / 미충족 조건 표시"]
    A -->|예| JE["je_scramble_for_korea<br/>조선·국가별 적격 관여국 / 영향력 초기화"]
    JE --> MOD["조선 지렛대 저항 -50% 적용"]
    MOD --> ENTRY{"참가 국가"}
    ENTRY -->|조선| E1[".1 풍전등화"]
    ENTRY -->|청·일| E2[".2 한반도를 향한 야망"]
    ENTRY -->|기타 열강| E3[".3 조선 문제"]
    E2 --> LOOP
    E3 --> LOOP
    E1 --> LOOP["참여 목록 동기화 / 종료 사유 확인"]
    NEW["청의 붕괴·종주권·승인 여부<br/>일본의 완료 변수·승인 여부<br/>그 밖의 열강 지위·이해관계 변화"] -.-> SYNC["국가별 참가·이탈 / GUI 행 수 갱신"]
    SYNC -->|참가·재참가| ENTRY
    SYNC -->|그 외| LOOP
    EXT["국가 소멸 · 중국 붕괴<br/>종속관계 변경 · 조선 승인"] -.-> LOOP
    LOOP --> EXISTS{"조선 존재?"}
    EXISTS -->|아니오| ABORT
    EXISTS -->|예| SUBJECT{"조선이 종속국이고<br/>현재 직접 종주국이 청 이외 국가인가?"}
    SUBJECT -->|예| OVERLORD{"청 이외 직접 종주국 자동 승리<br/>관여 여부·점수·전쟁 무관"}
    OVERLORD -->|일본| E6
    OVERLORD -->|청·일 이외 국가| E5
    SUBJECT -->|독립 또는 청 종속| SOLO{"실제 관여국에 조선만 남음?"}
    SOLO -->|예| E4
    SOLO -->|아니오| WIN{"승패 조건 판정"}
    ABORT["조선 소멸로 경쟁 중단<br/>이벤트 없이 정리"]
    WIN -->|조선 독립 AND 승인 AND 영향력 단독 100| E4[".4 조선 자주권 확보"]
    WIN -->|일본 영향력 단독 100| E6[".6 일본 승리"]
    WIN -->|청 영향력 단독 100| E7[".7 청 승리"]
    WIN -->|다른 열강 영향력 단독 100| E5[".5 기타 국가 승리"]
    WIN -->|미충족 또는 100 동률| PLAY["국가별 월간 영향력"]
    PLAY --> MONTH["조선 국가 등급 반영<br/>조선 소속 블록 지도자 월 +1 · 청 포함<br/>갱신 전 상태 계산 후 일괄 적용"]
    MONTH --> LOOP
    PLAY -.->|추가 계획: 월간 갱신·종료 판정 후| CANDIDATES{"진행 중이며 사건 조건 충족?<br/>월 25% · 적격 후보 균등 추첨<br/>최대 1건 · 대기 중 추첨 없음"}
    CANDIDATES -.-> E11[".11 공사관으로 향하는 가마<br/>보호 요청 / 경비 강화 / 거처 이전"]
    CANDIDATES -.-> E12[".12 누구의 뒤에 서야 하는가<br/>청 의전 수용 / 독자 국서 / 접수국 지원"]
    CANDIDATES -.-> E13[".13 백성의 쌀인가, 상인의 계약인가<br/>방곡 유지 / 철회 / 배상 협상"]
    CANDIDATES -.-> E14[".14 우리 시장에 도는 남의 지폐<br/>통용 인정 / 금지 / 독자 정비"]
    CANDIDATES -.-> E15[".15 전보는 어느 길로 가는가<br/>기존망 / 공동 건설 / 자력 건설"]
    CANDIDATES -.-> E16[".16 해관의 장부를 쥔 손<br/>운영 위임 / 자문 한정 / 자체 정비"]
    CANDIDATES -.-> E17[".17 철길의 주인은 누구인가<br/>외자 부설 / 공동 출자 / 국영 건설"]
    CANDIDATES -.-> E18[".18 산 아래 잠든 황금<br/>채굴권 허가 / 조건 협상 / 직접 개발"]
    CANDIDATES -.-> E19[".19 섬에 내려진 낯선 깃발<br/>철수 요구 / 공동 항의 / 기한부 묵인"]
    CANDIDATES -.-> E20[".20 벌목장의 포대<br/>확장 금지 / 군사화 묵인 / 개방 협상"]
    CANDIDATES -.-> E21[".21 종로에 모인 목소리<br/>철수 협상 / 국내 개편 / 집회 해산"]
    CANDIDATES -.-> E22[".22 다른 나라에 허락했다면<br/>동등 대우 / 거부 / 특혜 재협상"]
    E11 -.-> RESPONSE
    E12 -.-> RESPONSE
    E13 -.-> RESPONSE
    E14 -.-> RESPONSE
    E15 -.-> RESPONSE
    E16 -.-> RESPONSE
    E17 -.-> RESPONSE
    E18 -.-> RESPONSE
    E19 -.-> RESPONSE
    E20 -.-> RESPONSE
    E21 -.-> RESPONSE
    E22 -.-> RESPONSE
    RESPONSE{"선택 결과"} -.->|일방 선택| APPLY["조건·비용 재검사 후 즉시 효과"]
    RESPONSE -.->|합의 필요| E23[".23 외국 응답<br/>수락 60 / 거절 40 · 코드 일치 검사"]
    E23 -.->|수락| APPLY
    E23 -.->|거절·무효| LOOP
    APPLY -.-> LOOP
    APPLY -.->|사업·환궁| JOBS["180일 또는 365일 뒤 명시된 on_action<br/>대상·중복 완료 재검사 · 완료 효과"]
    JOBS -.-> LOOP
    E6 --> FOREIGN["외국 승리 확정·종료 플래그 설정"]
    E5 --> FOREIGN
    FOREIGN --> TRANSFER{"청 종속 조선에 대한<br/>다른 관여국의 영향력 승리?"}
    TRANSFER -->|예| MOVE["청에서 승자에게 조선 종속관계 이전<br/>이전으로 인한 자동 승리 재호출 방지"]
    TRANSFER -->|아니오| OTHER["기존 종속 등급 유지 또는<br/>독립 조선의 종속관계 생성"]
    MOVE --> FCOMPLETE["complete / on_complete<br/>외국 승리 처리"]
    FCOMPLETE --> END["기존 JE 종료 콜백에서 1회 처리<br/>조선 저항 modifier·영향력 변수 정리"]
    OTHER --> FCOMPLETE
    E7 --> FCOMPLETE
    E4 --> KFAIL["fail / on_fail<br/>조선 승리 보상·결과 통지"]
    KFAIL --> END
    ABORT --> END
```

## 8. 승패와 예외 상태

현재 전쟁 여부와 무관하게 영향력·행동·신규 사건·제안 응답·승패 판정을 진행한다. 종료 판정은 엔진의 `complete` / `fail` / `invalid` 호출 순서에 맡기지 않는다. 아래 우선순위를 공통 판정에 명시하고, 각 트리거를 상호 배타적으로 만든다.

1. **관여국·변수 정리:** 기존 국가별 등록·유지 조건을 반영한다. 이는 영향력 경쟁의 참가 자격이며, 종주국 자동 승리의 자격 제한으로 사용하지 않는다.
2. **조선 소멸:** 조선이 존재하지 않으면 이벤트 없이 중단하고 종료 플래그와 임시 상태 정리만 처리한다. 소멸한 조선의 종주국을 추정하지 않는다.
3. **청 이외 종주국 자동 승리:** 조선이 존재하고 `is_subject = yes`이며 **현재 직접 종주국이 청이 아니면** 그 종주국을 승자로 확정한다. 영향력·관여국 여부·승인 여부·전쟁 여부와 무관하며 나머지 중단·점수 승리보다 우선한다. 유효한 종주국 스코프가 아직 확인되지 않는 과도 상태는 다음 판정까지 보류한다. 일본이면 `.6`, 청·일 이외 국가면 `.5`다. 청이 직접 종주국이면 이 분기를 건너뛰고 아래 단독 잔류·영향력 판정을 계속한다. 새로 청의 종속국이 된 경우도 같은 예외를 적용한다.
4. **외국 이탈과 조선 단독 잔류:** 청·일 소멸 또는 `china_shatters`로 전체 경쟁을 중단하지 않는다. 해당 국가를 제외하고 나머지 관여국끼리 계속한다. 종주국 자동 승리가 없고 실제 JE 관여국에 조선만 남으면 영향력·승인·독립·전쟁 여부와 무관하게 조선 승리(`.4`)로 처리한다. 탈락 예정 국가가 실제 관여국에서 제거되기 전에는 단독 잔류로 판정하지 않는다.
5. **조선 자주권 확보:** `is_subject = no` AND `is_country_type = recognized` AND 조선 영향력 100을 모두 충족하고, 기존 동률 규칙에 따라 조선만 단독 100이면 `.4`이다. 외국 관여국이 남아 있다면 승인 전환만으로는 종료하지 않는다.
6. **외국 영향력 승리:** 실제 유효 관여국 중 정확히 한 국가만 100이고 그 국가가 외국이면 해당 국가가 승리한다. 청·일이 전용 참여 조건을 잃으면 점수로는 승리할 수 없다. 일본이 실제 직접 종주국이면 3번이 적용되지만 청에는 이 예외가 없다. 조선의 독립·승인 요건이 미충족일 때 단독 100만으로 조선 승리를 처리하는 우회 분기를 두지 않는다.
7. **동률:** 같은 갱신에서 둘 이상이 100이면 경합을 계속한다. 상대 점수 감소·이탈로 단독 100이 되면 승리를 확정한다. 동률 중에도 대응 행동은 가능하며, 청 이외 직접 종주국이 생기면 3번으로 결론을 낸다. 청의 종주권만으로는 동률을 해소하지 않는다.

조선 승리는 두 경로다. **영향력 승리**는 `독립국 AND 승인국 AND 조선만 영향력 100`이며 전쟁 중에도 같은 조건으로 판정한다. **단독 잔류 승리**는 실제 JE 관여국에서 모든 외국이 제외되고 조선만 남은 경우이며, 영향력·승인·독립·전쟁 조건을 요구하지 않는다. 청 이외 직접 종주국의 자동 승리는 두 경로보다 우선한다. 어느 경로도 조선을 강제로 독립시키거나 승인국으로 변경하지 않는다. 활성화 시 미승인 조건은 진행 중 유지 조건으로 재사용하지 않는다.

청 이외 종주국의 자동 승리는 참가 등록과 별개다. 비관여 종주국을 승자로 알리기 위해 JE에 강제 등록하거나 영향력 변수를 만들지 않는다. 시작부터 조선이 청 종속이면 경쟁을 진행하고, 청 이외 국가의 종속이면 해당 직접 종주국이 승리한다. 청 종속 조선의 영향력 승리는 실제 독립 이후에만 가능하지만, 중국 붕괴 등으로 청을 포함한 모든 외국이 이탈하면 조선 단독 잔류 승리는 가능하다. 활성화 조건에 독립국 조건을 추가하지 않는다.

| 결말 | 외교 효과 제안 |
|---|---|
| 청 승리 | 영향력 승리만 가능. 이미 청 종속이면 기존 종속 등급 유지, 독립 조선이면 조공국 관계 제안값으로 생성. 청 위신·친청 지지 보상 |
| 일본 승리 | 종주국 자동 승리면 기존 종속 등급 유지. 청 종속 조선에 대한 영향력 승리면 청에서 일본으로 종속관계 이전. 독립 조선에 대한 영향력 승리면 보호국 관계 제안값으로 생성. 일본 위신·군부 만족 보상 |
| 기타 국가 승리 | 종주국 자동 승리면 기존 종속 등급 유지. 청 종속 조선에 대한 관여국의 영향력 승리면 청에서 승자로 종속관계 이전. 독립 조선에 대한 영향력 승리면 보호국 관계 제안값 적용. 실제 승자 스코프로 결과 전달 |
| 조선 승리 | 기존 독립·종속 관계와 승인 상태를 유지하고 자주권 확보 보상 적용. 영향력 승리와 모든 외국 이탈 후 단독 잔류 승리 모두 같은 결과 이벤트 사용 |
| 경쟁 중단 | 기존 외교·전쟁 결과를 유지하고 경쟁 전용 임시 상태만 정리 |

종속 관계 생성에는 현재 게임의 실제 지원 외교 관계 유형과 허용 조건을 확인한다. 조공국·보호국의 정확한 키와 `create_diplomatic_pact` 허용 조건을 구현 단계에서 검증한다. **청 종속 조선에 대해 다른 외국 관여국이 영향력으로 승리하면 조선의 종속관계를 청에서 승자에게 이전한다.** [류큐 승리 이벤트의 이전 처리](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/japan_events/ryukyu_rivalry_events.txt:401)를 따라 승자 국가 스코프에서 `transfer_subject = c:KOR`를 적용하는 안으로 잡는다. 이전은 기존 종속 등급을 유지하는 방향으로 구현·검증하며, 독립 후 새 종속관계를 만드는 분기와 구별한다. 기존의 ‘청 종속관계 유지·정치적 승리만 적용’ 안은 폐기한다. 청 이외 국가에 이미 종속된 경우에는 그 직접 종주국이 자동 승자다. 독립 조선에 대한 점수 승자가 관계 생성 권한을 갖지 못할 때의 정치적 승리 대안은 청 종속 조선의 이전에 적용하지 않는다.

독립 조선에 대한 외국 관여국의 영향력 승리 후 종속관계 생성은 류큐 모티브를 따른 설계 제안이며, 청 종속 조선의 관계 이전은 사용자 요구다. 먼저 기존 `scramble_for_korea_finished`로 종료를 잠근 뒤 관계를 생성하거나 이전하여, 변경된 종속관계가 다시 자동 승리·보상을 호출하지 않게 한다. 관계 변경 직전에 조선·승자의 존속과 현재 종주국을 재확인한다. 승리 직후 추가 거부·전쟁 체인은 1차 범위에 포함하지 않는다.

자주권 승리 시 모든 조약을 일괄 탈퇴시키지 않는다. 경쟁에서 새로 생성하고 추적한 임시 지원·고문 효과만 정리한다. 외부 시스템이 만든 조약·관계·정치 로비는 유지한다.

JE의 기술적 종료는 외국의 종주국 자동 승리·영향력 승리를 `complete` / `on_complete`, 조선의 영향력 승리·단독 잔류 승리를 `fail` / `on_fail`로 처리한다. 각 콜백에서 승자를 저장 스코프로 확정하고 보상·정리·결과 이벤트 전달을 실행한다. `custom_completion_header`는 외세 승리 조건, `custom_failure_header`는 조선 승리 조건을 표시한다. 청 이외 직접 종주국 자동 승리가 최우선이며, 그 외 조선 영향력 승리 조건과 외국 영향력 승리 조건이 동시에 성립하면 조선 승리를 우선하여 완료·실패의 중복 성립을 방지한다. `on_invalid`는 이벤트 없이 종료 플래그 설정과 임시 상태 정리만 실행한다. 이를 위한 영구 전역 변수나 일회성 scripted effect는 만들지 않는다. 각국 결과 이벤트는 플레이 국가에 맞는 승리·패배·관전 문구를 보여 주며 외교 효과를 다시 실행하지 않는다. 자동 승자가 비관여 종주국이면 해당 국가에도 결과를 한 번 전달한다.

## 9. 기존 초안에서 고칠 부분

[일지 구현](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_scramble_for_korea.txt:1)와 [이벤트 구현](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/events/eafp_scramble_for_korea_events.txt:1)의 기존 정의를 수정·활성화했다. JE ID·이벤트 네임스페이스·쓸 수 있는 기존 키를 유지하면서 다음 부분을 고친다.

- `is_subject = no`, 세력권 주도국 2개, 구 만주 관심 선언 조건을 제거한다. 조선은 기본 참여, 청·일은 전용 조건을 만족할 때만 참여, 나머지 열강은 동북아 이해관계 3 이상에서 참가·2 이상에서 유지하도록 대체한다. 일반 열강 분기에서 청·일 태그를 명시적으로 제외한다.
- 조선 승인국 전환이 `complete`와 `fail`에 동시에 걸리는 구조를 없앤다. 승인만으로 종료하지 않고 독립·승인·영향력 100과 동률 규칙을 함께 검사한다.
- 참가 통지는 조선 `.1`, 청·일 `.2`, 기타 열강 `.3`으로 분리한다. 기존 일본·청 승리 통지는 `.6`·`.7`로 옮기며, 참가 현지화와 주석은 사용자 제공 원문을 그대로 사용한다.
- 기존 `scramble_for_korea_participants` 전역 목록을 없애고 참여 관리는 JE 관여국 상태로 처리한다. 국가별 숫자 변수 `scramble_for_korea_participants_influence`는 관여국이 된 후 추가, 탈락한 후 제거한다. 변수로 관여국을 결정하는 역방향 로직·별도 영향력 사본은 두지 않는다. `scramble_for_korea_finished`는 재사용하고 수동 참가 카운터 `je_scramble_for_korea_participants_globalvar`는 제거한다.
- 이전 안의 S·A 변수, ±40 판정, `scripted_progress_bar` 원본 구조를 사용하지 않는다. 모든 사건은 지정된 국가 스코프의 `scramble_for_korea_participants_influence`에 증분을 적용한다.
- 청·일의 전용 관여 조건과 역사적 문구를 제외한 라이벌 선택, 영향력 승자, 고문·로비 대상은 실제 관여국을 대상으로 동적으로 처리한다. 종주국 자동 승자는 실제 종속관계에서 찾으며, 종료 통지는 관여국과 비관여 자동 승자에게 중복 없이 전달한다.

## 10. 구현 파일과 순서

아래 경로는 저장소 루트 기준의 구현 파일이며 **기존 정의를 고칠 위치부터 정하고 필요한 파일만 추가**한다. 아직 사용처가 정해지지 않은 빈 파일이나 일괄 분리용 파일을 만들지 않는다.

| 순서 | 파일 | 작업 |
|---|---|---|
| 1 | `common/journal_entries/eafp_00_meiji_restoration.txt` 및 기존 유신 결과 이벤트 | 읽기 전용 참조. 기존 종료 변수 확인, 성공 기록·설정 코드 추가 없음 |
| 2 | `common/journal_entries/eafp_scramble_for_korea.txt` | 기존 JE를 수정·활성화. 초기 개혁 보상·조선 저항 modifier·주간 참가 갱신·월간 계산·종료 처리를 각 콜백에 직접 배치. 시작과 갱신 시 실제 종주국 자동 승리를 우선 판정 |
| 2 | `common/journal_entries/eafp_korean_reformation.txt` | 기존 하위 네 완료 콜백에 각각 +5, 상위 완료 콜백에 +10 연결. 기존 완료 변수·일지 생성 구조 재사용, 초기 보상과 중복 방지 |
| 3 | `gui/journal_entry_widgets/eafp_je_scramble_for_korea.gui` | 기존 위젯 문법으로 국가별 행 표시. JE 참여국 직접 바인딩을 먼저 검증 |
| 3 | `common/scripted_buttons/eafp_korea_buttons.txt` | 쟁탈 일지 전용 행동 버튼은 모두 제거 |
| 3 | `events/eafp_scramble_for_korea_events.txt` | 기존 이벤트 수정·연결 후 부족한 ID만 추가. 이벤트 체인 스코프 전달 방식 재사용 |
| 3 | `common/script_values/earp_scramble_for_korea_values.txt` | 월간 계산과 툴팁이 공유하는 계산식 등 실제 공용 값만 배치. 해군력·대조선 관계 보너스 제외. 단 한 곳의 상수까지 모두 옮기지 않음 |
| 3 | `common/static_modifiers/eafg_scramble_for_korea_modifiers.txt` | 기존 `modifier_kor_foreign_influence`의 지렛대 저항을 -0.5로 변경. 일지 활성 중 조선에만 적용하고 모든 종료에서 제거. 기존 효과로 표현할 수 없는 고문·자주권·승패 효과만 추가 |
| 4 | `localization/korean/eafp_scramble_for_korea_l_korean.yml` | 기존 키 수정 및 새 기능에 필요한 문구 추가 |
| 5 | `documentation/joseon-content.md` | 구현 완료 후 실제 연결도와 설명 갱신 |

`scripted_effects`·`scripted_triggers` 전용 파일 생성은 확정 작업에서 제외한다. 구현 후 실제 중복이 확인되면 기존 관련 정의·파일을 먼저 확인하고, 재사용할 수 없을 때만 필요한 정의를 추가한다. `scripted_guis`도 GUI의 직접 바인딩과 기존 표시 조건으로 처리할 수 없는 요구가 확인될 때만 사용한다. 조건을 분리하기 위한 조건 파일이나 effect를 호출하기만 하는 래퍼를 만들지 않는다.

국가별 `scripted_progress_bars` 파일은 만들지 않는다. 실제 게임 상태인 국가 영향력 변수와 표시용 GUI를 구분한다. GUI 연결부터 작은 시제품으로 검증하여 조선·조건을 충족한 청일·그 밖의 관여국·0점 국가가 동일한 위젯에 나타나는지 확인한 뒤 이벤트를 연결한다.

종료 처리는 기존 국제 JE의 전체 `on_complete` / `on_fail` / `on_invalid`와 국가별 `*_all_involved` 콜백 구분을 따른다. 전체 콜백에서 승자를 이벤트 전달 스코프로 확정하고 기존 `scramble_for_korea_finished`를 설정하며 외교 효과는 한 번만 적용한다. 결과 통지는 JE 관여국 순회 또는 국가별 콜백 중 스코프 전달이 검증된 한 경로를 사용하며, 자동 승자가 비관여 종주국일 때만 별도로 한 번 통지한다. 승자를 강제 참가시키거나 영향력 변수를 만들지 않는다. 통지 대상과 승자 스코프를 전달한 뒤 생존 국가 중 영향력 변수를 가진 국가의 값과 경쟁 전용 임시 효과를 정리하고, 조선의 `modifier_kor_foreign_influence`도 제거한다. 시작 직후 종주국 승리로 끝날 때도 같은 정리를 수행한다. 순회용 영구 이력 목록이나 영구 결과 변수는 남기지 않는다. 완료·중단 양쪽에 같은 정리가 실제로 반복되면 그 부분만 scripted effect 추출 후보로 삼는다. 흐름도의 결말 이벤트 노드는 이 판정·통지 처리를 뜻한다.

월간 계산은 국제 JE의 전체 `on_monthly_pulse` 한 곳에 둔다. 로컬 `common/journal_entries/journal_entries.md`에 명시된 전체 콜백과 국가별 콜백의 역할을 따르고, 실행 횟수를 확인하기 전에 월별 처리 마커를 추가하지 않는다. 현재 참여국을 대상으로 갱신 전 값을 읽도록 계산 순서를 정한 뒤 모든 적용을 마치고 승패를 판정한다. 국가 변수는 게임 스크립트만 변경하며 UI 프레임·창 개폐·관전 전환에 따라 변하지 않는다. 지연 이벤트는 기존 종료 플래그, JE 진행 여부, 현재 자격과 이벤트 대상의 유효성을 검사한다.

## 11. 구현 완료 기준

| 검증 상황 | 기대 결과 |
|---|---|
| 청 존재, 붕괴 없음, 일본의 유신 종료 변수 있음, 조선 미승인 | 정확히 한 국제 일지 활성화 |
| 위 세 조건 중 각각 하나가 거짓 | 활성화되지 않음 |
| 천황파 승리·공의여론 경로에서 기존 종료 변수가 있음 | 다른 활성화 조건이 맞으면 활성화, 천황 복권 기록 검사·새 성공 변수 없음 |
| 막부 유지·군주제 폐지로 일지가 끝나 종료 변수만 있음 | 다른 활성화 조건이 맞으면 활성화 |
| 천황 복권 변수만 있고 유신 종료 변수는 없음 | 일본 측 활성화 요건 미충족으로 활성화되지 않음 |
| 조선이 청 종속, 일본이 세력권 비주도국·열강 미달 | 세 조건이 맞으면 활성화 후 경쟁 계속. 청 자동 승리 없음, 조선 저항 modifier 유지 |
| 다른 나라가 열강 + 이해관계 정확히 3 / 4 이상 | 참가하고 해당 국가 막대 생성 |
| 미참여 국가가 열강 + 이해관계 2 / 비열강 + 이해관계 3 | 신규 참가하지 않음 |
| 조선의 열강 지위·이해관계 미달 | 기본 관여국 유지 |
| 붕괴하지 않은 청이 조선 종주국이며 미승인국 | 청 참여 |
| 붕괴하지 않은 청이 승인국이며 조선 종주국은 아님 | 청 참여 |
| 붕괴하지 않은 청이 미승인국이며 조선 종주국도 아님 | 청 미참여. 기존 관여국이면 제거 후 영향력 변수 삭제 |
| 중국 붕괴 발생, 청의 종주권·승인 여부와 무관 | 청 관여국 제거·변수 삭제 후 남은 국가끼리 경쟁. 청 이외 직접 종주국이면 그 국가 자동 승리, 그렇지 않고 조선만 남으면 조선 승리 |
| 일본 완료 변수 있음 + 승인국, 천황 복권 변수 없음 | 일본 측 활성화 요건과 관여 조건 모두 충족 |
| 일본 완료 변수 있음 + 미승인국 | 다른 활성화 조건이 맞으면 일지는 활성화되지만 일본은 미관여 |
| 일본 완료 변수 없음 또는 미승인국 | 일본 미참여. 기존 관여국이면 제거 후 영향력 변수 삭제 |
| 전용 조건을 만족한 청·일이 열강 미달·이해관계 미달 | 청·일의 관여에는 해당 일반 열강 조건을 요구하지 않음 |
| 전용 조건을 잃은 청·일이 열강이며 이해관계 3 이상 | 일반 열강 분기로 우회 참가하지 않음 |
| 청이 승인국인 채 종주권 상실 / 미승인국인 채 종주권 상실 | 전자는 계속 관여, 후자는 관여국 제외 |
| 청·일의 관여 조건 상실과 영향력 100 도달이 동시에 발생 | 먼저 관여국 제외·변수 정리, 탈락국의 영향력 승리 없음. 일본이 직접 종주국이면 별도 자동 승리, 청은 제외 |
| 추가 열강의 이해관계 3→2→3 | 참여·기존 영향력·GUI 행 유지, 재등록·초기화 없음 |
| 추가 참여국의 이해관계 2→1 또는 0 | 먼저 JE 관여국에서 제거, 이어 영향력 변수 삭제. GUI는 관여국 탈락에 따라 행 제거 |
| 이탈한 열강의 이해관계 1→2→3 | 2에서는 미참여 유지, 3에서 재참가하며 영향력 0부터 |
| 추가 열강이 이해관계 2인 채 이벤트 응답·월간 갱신·100 도달 | 정상 응답·갱신·승리 판정. 신규 참가 기준 3을 재적용하지 않음 |
| 추가 열강의 지위 강등 | 이해관계가 2 이상이어도 기존 규칙대로 이탈 |
| 3국 / 6국 / 12국 표시 | 각각 3 / 6 / 12개 행, 스크롤 정상, 국가별 하드코딩 없음 |
| 실제 관여국의 영향력 0 / 50 / 100 | 모두 관여국 행 표시, 빈·반·가득 찬 막대 |
| 실제 관여국인데 영향력 변수 누락 | 참여·GUI 행 유지, 스크립트에서 변수 0으로 보완. 참가 보상 재지급 없음 |
| 비관여국인데 영향력 변수 잔존 | 변수 제거, 관여국 자동 등록·행 생성·영향력 승리 없음. 청 이외 직접 종주국의 자동 승리는 변수와 무관 |
| 이해관계 2인 관여국의 변수 누락 / 2인 비관여국의 변수 잔존 | 전자는 참여 유지 후 변수 보완, 후자는 미참여 유지 후 변수 제거. 변수 존재가 2단계 유지 여부를 결정하지 않음 |
| 엔진 또는 다른 이벤트에서 관여국 추가·제거 | 실제 관여국 변경을 따라 영향력 변수가 추가·제거됨 |
| 같은 국가 중복 등록 / 이탈 후 재참가 | 중복 등록은 점수 유지, 재참가는 0부터. 시작 초기 배치·참가 보상 재지급 없음, 쿨다운 유지 |
| 독립 조선이 개혁은 완료했으나 여전히 미승인 | 활성화, 하위 네 완료 각 +5와 상위 완료 +10으로 최초 영향력 +30 |
| 시작 전·후·최초 초기화와 같은 시점에 하위·상위 개혁 완료 | 기존 완료 변수와 완료 콜백으로 하위 각 +5, 상위 +10을 각각 한 번. 추가 counted 변수 없음 |
| 마지막 하위 개혁과 상위 개혁이 연속 완료 | 합계 +15를 반영하되 영향력 상한 100 적용 |
| 조선 국가 등급 변경 / 같은 등급 안에서 위신만 변동 | 등급별 배타적 월간 보너스 적용 / 위신 자체로는 보너스가 달라지지 않음 |
| 다른 산정 조건이 같은 상태에서 해군력·대조선 관계 수치만 변경 | 영향력 월간 증감 불변, 계산식·툴팁에 해당 보너스 없음 |
| 청을 포함한 외국 관여국이 조선과 같은 블록의 지도자 / 일반 회원국 | 지도자만 월 +1, 일반 회원국은 해당 보너스 없음 |
| 청이 조선의 종주국이며 같은 블록의 지도자 / 조선이 블록 탈퇴·지도자 변경 | 청 자동 승리 없이 블록 보너스 월 +1 / 다음 월간 계산에 실제 소속·지도자 반영 |
| 블록 보너스 +1과 다른 월간 증감 동시 발생 | 모든 항목 합산 후 기존 월간 -1~+1 제한 적용 |
| 일지 활성화·반복 갱신·기존 제안 이벤트 응답 | 조선에만 지렛대 저항 -50% 한 번 적용, 갱신·제안으로 중첩하거나 만료 기간을 덮어쓰지 않음 |
| 여러 국가 버튼 연속 클릭 / 저장 후 불러오기 | 쿨다운·목록·변수·미결 제안 유지, 중복 초기화·보상 없음 |
| 독립·승인 조선 / 청 / 일 / 기타 관여 열강 각각 단독 100 | 종주국 자동 승리·중단이 없으면 올바른 승자·결말 이벤트, 외교 효과 한 번 |
| 같은 월에 둘 이상 100 / 이미 100 동률 상태 | 목록 순서에 따른 승리 없음, 경합 표시·대응 가능, 단독 100이 되면 확정. 청 이외 직접 종주국이 생기면 자동 승리 우선, 청의 종주권은 동률을 해소하지 않음 |
| 독립 조선의 승인 전환과 외국 영향력 100 동시 | 조선이 100 미만이면 단독 100 외국의 승리, 조선도 100이면 동률 보류. 승인만으로 우선 승리 없음 |
| 독립·승인 조선의 영향력 99 / 독립·미승인 조선의 영향력 단독 100 | 외국 관여국이 남아 있다면 둘 다 영향력 승리 불가, 경쟁 계속. 승인 전환만으로 일지 무효화하지 않음 |
| 독립·승인 조선이 영향력 단독 100 도달 / 독립·단독 100 조선이 승인 획득 | 중단 사유가 없으면 모두 자주권 확보. 세 조건의 충족 순서 무관 |
| 승인국이며 영향력 단독 100인 조선이 청 종속 / 청 이외 국가 종속 | 외국 관여국이 남아 있다면 전자는 경쟁 계속, 후자는 직접 종주국 자동 승리. 모든 외국이 이탈한 전자는 조선 단독 잔류 승리 |
| 실제 조선 관련 전쟁 또는 관여국 간 전쟁 중 승리 점수 도달 | 평시와 같은 조건으로 점수 승리 판정. 종주국 자동 승리·단독 잔류 승리도 기존 규칙 적용 |
| 실제 외교·전쟁 상태는 그대로 두고 조청전쟁 저널 상태만 변경 | 쟁탈 일지의 활성화·관여·영향력·정지·재개·승패에 변화 없음, 상호 이벤트 호출 없음 |
| 실제 전쟁 시작·종료 / 종속관계 변경 | 전쟁 여부만으로 진행·행동·제안·승패가 달라지지 않음 / 종속관계에는 기존 규칙 적용 |
| 청 붕괴·청/일 소멸 / 조선 소멸 / 추가국 소멸 | 외국 이탈은 해당 국가만 정리하고 경쟁 유지. 조선 소멸만 중단. 청 이외 직접 종주국 자동 승리 우선, 그 외 조선만 남으면 조선 승리 |
| 조선이 청 이외 참여 열강 종속 / 청 이외 비참여국 종속 | 모두 현재 직접 종주국 자동 승리. 비관여 종주국 강제 등록·변수 추가 없이 결과 통지 |
| 청 이외 종주국 영향력 0·변수 없음·미승인·비열강 / 다단계 종속관계 | 자격·점수와 무관하게 자동 승리 / 직접 종주국으로 판정. 직접 종주국이 청이면 상위 국가가 누구든 자동 승리 없음 |
| 진행 중 새로 청 종속이 됨 / 청의 영향력 단독 100 | 종주권만으로는 자동 승리하지 않음 / 유효 관여국이고 중단 사유가 없으면 청의 영향력 승리 |
| 청 종속 조선에 대해 일본 또는 다른 외국 관여국이 영향력 승리 | 조선의 직접 종주국이 청에서 실제 승자로 변경되고 기존 종속 등급 유지. 이전·보상은 각각 한 번 |
| 외국의 자동 승리 / 독립 조선에 대한 영향력 승리 / 독립 조선의 관계 생성 권한 부족 | 각각 기존 종속 등급 유지 / 제안된 종속관계 생성 / 정치적 승리만 적용. 청 종속 조선의 이전에 마지막 대안을 재사용하지 않음, 자동 병합 없음 |
| 영향력 승리 효과로 종속관계 생성·이전 / 종료 후 예약 이벤트·재로딩 | 관계 변경 전 기존 종료 플래그 설정으로 이중 승리·이전·재발동 방지. 모든 영향력 변수·경쟁 전용 고문 효과·조선 저항 modifier 정리 |
| 조선·청·일·영국·러시아·관전국 전환, 멀티플레이 | 같은 참여국 목록·국가별 값, 타국 행에 플레이 국가 값이 반복되지 않음 |
| GUI 반복 개폐 / 목록 순서 변경 / 참가 수 증가 | 게임 수치·월간 갱신 횟수·전체 랜덤 사건 빈도 불변 |

정적 검증은 이벤트·현지화 키 참조, 중괄호, 잘못된 스코프, 활성 파일의 중복 정의를 확인한다. 추가된 각 변수는 기존 상태로 대체 가능한지와 쓰기·읽기·제거 위치를 확인한다. 새 scripted effect·trigger는 실제 호출부가 두 곳 이상인지, 동일한 의미의 중복을 줄이는지, 기존 정의를 재사용할 수 없는지 확인한다. 쓰이지 않는 옛 코드·참조와 새 코드가 병존하지 않도록 정리한다.

GUI 실행 검증은 국제 일지 위젯 컨테이너·JE 관여국 직접 바인딩·국가별 행 스코프·영향력 값 읽기·동적 행 제거·스크롤을 우선한다. 변수 누락·잔존이 관여국 상태나 행 수를 결정하지 않는지 확인한다. 새 성공 변수, 옛 참가 전역 목록, 별도 영향력 사본이 추가되지 않았는지도 확인한다. 실행 검증은 게임 로그와 위 시나리오로 진행한다. **스크립트 구현과 정적·조건 검증을 완료했으며, 게임 내 GUI·콜백 순서·DLC 호환성·밸런스는 아직 검증하지 않았다.**


### 신규 계획 11~22 및 보조 응답 23의 검증 기준

정적 점검은 문서 코드의 중괄호·12개 본 이벤트·응답 23·modifier·지연 on_action·참조 연결을 검사한다. 아래 게임 실행 검증은 구현 후 수행하며, 현재 통과했다고 표시하지 않는다.

| 상황 | 기대 결과 |
|---|---|
| 관여국 3·6·12개 / 후보 여러 건 | 월 25% 추첨 한 번, 적격 사건 가중치 각 100, 본 사건 반복 없음 |
| 본 창·외국 응답 대기 / 365일 잠금 만료 | 새 본 사건 없음 / 만료 후 재개, 옛 창은 코드 불일치로 효과 없음 |
| 외국 이탈·소멸·청 붕괴·자격 상실 | 응답 무효, 점수 변수 생성·계약비 차감 없음, 해당 계약·거점 정리 |
| 수락 직전 어느 한쪽 보유금이 비용 미만 | 수락 불가, 거절 가능; 양국 자금·점수 변경 없음 |
| 대상 건물 철거·주 양도·조약 철회 | 오래된 창/완공 콜백의 대상 효과 없음 |
| `.11` 보호 수락 → 365일 / 군주제 폐지 전 선택 | 유효 보호 관계에만 환궁 +3/-3 / 주 선택 무효 |
| `.12` 청 영향력 19·20, 청 종속 여부 | 독립 상태 19는 후보 불가, 20은 가능; 청 종속이면 점수 문턱 없이 가능 |
| `.13` 곡물 가격 정확히 +25%, 수입량 9·10 | 가격 +25%는 미발생, 초과여야 함; 수입량은 10부터 가능 |
| `.14` 외국 소유 2·3레벨 / 보유금 99,999·100,000 | 각각 3레벨·100,000 미만일 때만 후보 |
| `.15`·`.16` 비용·180/365일 완료·730/1825일 만료 | 정의된 스코프에만 modifier, 즉시 완공 보상 없음 |
| `.17` 완공 전 다른 경로로 철도 생성 | 건물 추가·국내 완공 영향력 보상 없음, 계약금 환급 없음 |
| `.18` 금광 없음·1레벨 / 건물 제거 | 금광 없는 조선 미발생 / 소멸 건물에 정비 효과 없음 |
| `.19` 점령 뒤 중재국 동의 | 공동 항의만 성립, 점령국 철수·영토 이전 없음 |
| `.20` 벌목장 외국 소유 0·1레벨 | 1부터 후보, 상업 투자 없이 군사화 상황을 만들지 않음 |
| `.21` 여러 종류의 계약 동시 보유 | 거점 → 해관 → 은행 중 하나만 선택·해제; 다른 계약 유지 |
| `.22` 다조항 조약 / 단일 통상특권 조약 | 전자는 철회 대상 후보 제외, 후자만 협상 가능; 신규 조약은 권한 검사 통과 필요 |
| 전체 종료 / 조선 소멸 | pending·job·계약 국가 스코프와 경쟁 modifier 정리; 이미 완성된 철도 유지 |
| 조청전쟁 일지 상태만 변경 | 본 사건·응답·완공 조건 불변 |

## 12. 이전 구현 기록과 실행 확인 범위

아래 기록 중 개입 이벤트·제안 잠금·외국 버튼 관련 내용은 2026-10-22 삭제 전 구현에 해당한다. 현재 이벤트 구성은 6절과 아래 삭제 기록을 따른다.

- 국제 JE의 초기 관여 콜백에서 최초 점수(외국 10, 조선 기존 개혁 최대 30)를 적용한다. 이후 참가 콜백은 0부터 시작하며, 주간·월간에 공유하는 동기화 처리로 자격을 갱신한다.
- 실제로 반복되는 자격·승리 검사와 점수 증감·동기화·종료 정리·제안 시작/닫기·결과 통지만 기존 `eafp_kor_triggers.txt`와 `eafp_korea_effects.txt`에 추가했다. 전용 scripted GUI나 진행도 정의는 추가하지 않았다.
- 추가 상태는 조선의 `scramble_for_korea_pending_offer` 한 개다. 엔진 문서에서 미결 이벤트를 취소·조회할 수단을 찾지 못했으므로 현재 제안국 스코프를 저장한다. 이탈·소멸 때 취소 flag 값으로 바꾸되 기존 창이 닫힐 때까지 잠금을 유지한다. 신규 제안은 그동안 차단하므로 재참가 후 옛 제안이 새 제안을 덮어쓰지 못한다. 각 창은 `duration = 1`, 전달은 지연 없이 이루어지며 잠금은 365일 후에도 만료한다. 정상 응답·취소·일지 종료에서도 제거한다. 별도 일련번호·참가 이력은 없다.
- 버튼은 엔진 `cooldown`을 사용한다. 상권·로비·개화 지원·거류민 협의 제안은 £10,000, 고문은 외교력 50/730일, 권익 주장은 외교력 50/1,095일, 자주 외교는 행정력 50/730일을 적용했다. 제안 거부는 이미 지출한 비용을 돌려주지 않는다. 절충은 양국 +1만 부여하고 고문·로비 등의 지속 효과를 만들지 않는다.
- 거류민 귀환 지원은 재정 비용과 국내 지지 효과로 표현하며 팝을 강제로 이동시키지 않는다. 고문단 충돌은 현재 고문 파견국 중 두 국가만 고른다.
- GUI는 JE 관여국 데이터 모델을 직접 반복한다. 국가별 역할·점수·현재 월간 예상 증감과 원인 툴팁을 표시하며 상위 일지 패널의 스크롤을 사용한다.
- 한국어·영어·중국어 간체 현지화가 연결되어 있다. 조청전쟁 저널·전용 변수·이벤트를 참조하지 않는다.
- 검증 명령: `python tools/validate_korea_scramble.py`. 인코딩·괄호·중복 정의·18개 이벤트 호출·현지화와 실제 트리거를 읽는 조건 사례를 검사한다. 게임 실행 파일/실행 환경을 확인하지 못했으므로 GUI 표시, 국제 JE 콜백 순서, 이벤트 만료 및 종속관계 이전 후 등급 유지는 게임 안에서 확인해야 한다.

### 2026-10-14 종료 조건 갱신

- 청·일 소멸과 중국 붕괴는 전체 중단 사유에서 제외했다. 최초 활성화 조건은 유지한다.
- 실제 JE 관여국에 조선만 남으면 청 이외 직접 종주국 자동 승리 다음 우선순위로 조선 승리를 처리한다. 영향력·승인·독립·전쟁 여부는 요구하지 않는다.
- 조선 소멸 시 중단 이벤트는 삭제하고 조용히 종료한다. `.4` 설명과 한·영·중 저널 안내를 두 조선 승리 경로에 맞췄다.

### 2026-10-21 전쟁 제한 제거

- 현재 전쟁 여부로 영향력 갱신·행동·사건·제안 응답·점수 승리를 중단하지 않는다.
- 전쟁 시작에 따른 미결 제안 취소와 전쟁 중단 상태 안내를 제거했다. 이탈·소멸·종료에 따른 기존 처리는 유지한다.

### 2026-10-22 중간 이벤트 삭제

- 재번호 부여 전 이벤트 4~13, 한·영·중 해당 로컬, 월간 사건 추첨과 외국용 이벤트 버튼 4개를 삭제했다.
- 이벤트 전용 제안·응답 트리거와 effect, 경쟁국 선택용 script value를 삭제했다.
- 월간 영향력, 조선 자주 외교 버튼, 참가·승리 이벤트 7개는 유지한다.
- 미결 제안 변수는 더 이상 생성하지 않으며 기존 저장에 남은 값은 동기화·종료 시 제거한다.

### 2026-10-22 이벤트 번호 정리

남은 이벤트를 기존 번호 순으로 1~7로 재번호 부여했다. 참가 통지 1~3은 유지하며, 조선 승리는 4, 기타 국가 승리는 5, 일본 승리는 6, 청 승리는 7이다. 이벤트 정의와 로컬 키도 번호순으로 정렬했다.

### 2026-10-22 역사 사건 추가 계획

아래 두 추가 기록의 번호·건수는 당시 기준이다. 현재 계획은 마지막 삭제·재번호 기록과 6절을 따른다.

직전 추천한 역사 사례 7건을 `scramble_for_korea_events.11`~`.17`로 배정했다. 6절에 출처·발생 조건·선택지·효과 제안, 7절에 사건별 흐름, 11절에 향후 검증 항목을 추가했다. 런타임 이벤트·로컬·호출부는 수정하지 않았으며, 이 기록은 구현 완료를 뜻하지 않는다.

### 2026-10-22 앞선 추천 사건 추가 반영

앞서 추천한 해관 고문, 철도 부설권, 운산 금광, 거문도 점령, 용암포 사건, 만민공동회, 최혜국 대우 요구를 18~24로 추가했다. 기존 계획 11~17은 유지하며 신규 계획은 총 14건이다. 각 사건의 출처·조건·선택지·효과와 흐름도·향후 검증 항목을 보완했으며, 이번에도 게임 스크립트와 로컬은 수정하지 않았다.

### 2026-10-22 계획 사건 16·17 삭제 및 재번호

기존 계획 16·17번 사건을 삭제하고 기존 18~24번을 16~22번으로 앞당겼다. 현재 신규 사건은 11~22번의 총 12건이다. 목록·상세 설명·상호 참조·흐름도·검증 항목을 함께 수정했으며, 게임 이벤트와 로컬 파일은 변경하지 않았다.

## 13. 사건 11~22의 공통 정의와 연결 코드

이 절은 6절 이벤트 전문이 참조하는 정의를 전부 제공한다. `sk_` 이름은 이번 계획에 추가할 실제 식별자다. 런타임 반영 때 생략하거나 번역하지 않는다. 현지화는 `.N.t/.d/.f`, 선택지 `.N.a`~`.d`, `scramble_for_korea_events.cancel`, 응답 `.23.t/.d/.d_응답코드/.f/.a/.b`, 아래 16개 modifier 이름·설명 키를 한·영·중 파일에 추가한다. 취소 문구는 ‘상황이 달라졌다.’, 응답 선택은 ‘수락한다.’와 ‘거절한다.’이다. `.23.d`는 `scope:sk_case`별 triggered_desc로 본 사건과 요구 조건을 보여주며, 아래 표의 코드·금액을 그대로 사용한다. 역사 원문 flavor 인용은 이 실행 명세에서 새로 창작하지 않는다.

### 13.1 트리거 — 기존 `eafp_kor_triggers.txt`에 추가

`sk_foreign_valid`는 현재 JE 관여 여부를 먼저 본다. 영향력 변수만 가진 비관여국을 다시 등록하지 않는다. `sk_world_valid`는 현재 소스의 종주국 승리·점수 종료가 예정되어 있으면 사건을 막는 용도이며 승리 규칙을 재정의하지 않는다.

```txt
sk_foreign_valid = {
    NOT = { c:KOR ?= this }
    is_involved_in_journal_entry = je_scramble_for_korea
    scramble_for_korea_eligible = yes
    has_variable = scramble_for_korea_participants_influence
}

sk_world_valid = {
    exists = c:KOR
    NOT = { has_global_variable = scramble_for_korea_finished }
    NOT = { scramble_for_korea_overlord_wins = yes }
    c:KOR = {
        is_involved_in_journal_entry = je_scramble_for_korea
        has_variable = scramble_for_korea_participants_influence
    }
    # Current runtime complete checks score_winner on any country.
    NOT = { any_country = { scramble_for_korea_score_winner = yes } }
    any_country = { sk_foreign_valid = yes }
}

sk_context_valid = {
    sk_world_valid = yes
    exists = scope:sk_actor
    scope:sk_actor = { sk_foreign_valid = yes }
    trigger_if = {
        limit = { exists = scope:sk_rival }
        scope:sk_rival = { sk_foreign_valid = yes }
    }
    trigger_if = {
        limit = { exists = scope:sk_state }
        scope:sk_state = { owner = c:KOR }
    }
}

sk_offer_valid = {
    sk_context_valid = yes
    exists = scope:sk_respondent
    scope:sk_respondent = { sk_foreign_valid = yes }
    exists = scope:sk_case
    c:KOR = {
        has_variable = sk_pending
        var:sk_pending = scope:sk_case
    }
    this = scope:sk_respondent
    OR = {
        AND = { c:KOR = { var:sk_pending = 111 } sk_live_11 = yes }
        AND = { c:KOR = { var:sk_pending = 123 } sk_live_12 = yes }
        AND = { c:KOR = { var:sk_pending = 133 } sk_live_13 = yes }
        AND = { c:KOR = { var:sk_pending = 141 } sk_live_14 = yes }
        AND = { c:KOR = { var:sk_pending = 151 } sk_live_15 = yes }
        AND = { c:KOR = { var:sk_pending = 152 } sk_live_15 = yes }
        AND = { c:KOR = { var:sk_pending = 161 } sk_live_16 = yes }
        AND = { c:KOR = { var:sk_pending = 162 } sk_live_16 = yes }
        AND = { c:KOR = { var:sk_pending = 171 } sk_live_17 = yes }
        AND = { c:KOR = { var:sk_pending = 172 } sk_live_17 = yes }
        AND = { c:KOR = { var:sk_pending = 181 } sk_live_18 = yes }
        AND = { c:KOR = { var:sk_pending = 182 } sk_live_18 = yes }
        AND = { c:KOR = { var:sk_pending = 191 } sk_live_19 = yes }
        AND = { c:KOR = { var:sk_pending = 192 } sk_live_19 = yes }
        AND = { c:KOR = { var:sk_pending = 201 } sk_live_20 = yes }
        AND = { c:KOR = { var:sk_pending = 203 } sk_live_20 = yes }
        AND = { c:KOR = { var:sk_pending = 211 } sk_live_21 = yes }
        AND = { c:KOR = { var:sk_pending = 221 } sk_live_22 = yes }
        AND = { c:KOR = { var:sk_pending = 223 } sk_live_22 = yes }
    }
}

sk_live_11 = {
    sk_context_valid = yes
    exists = scope:sk_rival
    c:KOR = { has_law = law_type:law_monarchy }
}

sk_live_12 = {
    sk_context_valid = yes
    exists = scope:sk_rival
    c:CHI = { sk_foreign_valid = yes }
}

sk_live_13 = {
    sk_context_valid = yes
}

sk_live_14 = {
    sk_context_valid = yes
    exists = scope:sk_building
    scope:sk_building = {
        owner = c:KOR
        levels_owned_by_country = { target = scope:sk_actor value >= 3 }
    }
}

sk_live_15 = {
    sk_context_valid = yes
    exists = scope:sk_state
    scope:sk_state = { owner = c:KOR }
}

sk_live_16 = {
    sk_context_valid = yes
}

sk_live_17 = {
    sk_context_valid = yes
    exists = scope:sk_state
    scope:sk_state = { owner = c:KOR }
}

sk_live_18 = {
    sk_context_valid = yes
    exists = scope:sk_building
    scope:sk_building = { owner = c:KOR }
}

sk_live_19 = {
    sk_context_valid = yes
    exists = scope:sk_state
    scope:sk_state = { owner = c:KOR }
    exists = scope:sk_rival
}

sk_live_20 = {
    sk_context_valid = yes
    exists = scope:sk_building
    scope:sk_building = {
        owner = c:KOR
        levels_owned_by_country = { target = scope:sk_actor value >= 1 }
    }
    exists = scope:sk_state
    scope:sk_state = { owner = c:KOR }
    exists = scope:sk_rival
}

sk_live_21 = {
    sk_context_valid = yes
    OR = {
        AND = { scope:sk_petition_kind = 1 c:KOR = { has_variable = sk_base_partner var:sk_base_partner = scope:sk_actor } }
        AND = { scope:sk_petition_kind = 2 c:KOR = { has_variable = sk_customs_partner var:sk_customs_partner = scope:sk_actor } }
        AND = { scope:sk_petition_kind = 3 c:KOR = { has_variable = sk_bank_partner var:sk_bank_partner = scope:sk_actor } }
    }
}

sk_live_22 = {
    sk_context_valid = yes
    exists = scope:sk_rival
    exists = scope:sk_treaty
    scope:sk_treaty = { binds = c:KOR binds = scope:sk_rival
        any_scope_article = { count = 1 }
        any_scope_article = { has_type = trade_privilege source_country = c:KOR target_country = { sk_foreign_valid = yes } }
    }
}

sk_offer_acceptable = {
    sk_offer_valid = yes
    OR = {
        AND = {
            c:KOR = { var:sk_pending = 111 }
            sk_live_11 = yes
        }
        AND = {
            c:KOR = { var:sk_pending = 123 }
            sk_live_12 = yes
        }
        AND = {
            c:KOR = { var:sk_pending = 133 }
            sk_live_13 = yes
            c:KOR = { gold_reserves >= 20000 }
        }
        AND = {
            c:KOR = { var:sk_pending = 141 }
            sk_live_14 = yes
            scope:sk_actor = { gold_reserves >= 25000 }
        }
        AND = {
            c:KOR = { var:sk_pending = 151 }
            sk_live_15 = yes
            c:KOR = { gold_reserves >= 10000 }
            scope:sk_actor = { gold_reserves >= 30000 }
            exists = scope:sk_state
            scope:sk_state = { owner = c:KOR }
        }
        AND = {
            c:KOR = { var:sk_pending = 152 }
            sk_live_15 = yes
            c:KOR = { gold_reserves >= 25000 }
            scope:sk_actor = { gold_reserves >= 15000 }
            exists = scope:sk_state
            scope:sk_state = { owner = c:KOR }
        }
        AND = {
            c:KOR = { var:sk_pending = 161 }
            sk_live_16 = yes
        }
        AND = {
            c:KOR = { var:sk_pending = 162 }
            sk_live_16 = yes
            c:KOR = { gold_reserves >= 10000 }
        }
        AND = {
            c:KOR = { var:sk_pending = 171 }
            sk_live_17 = yes
            c:KOR = { gold_reserves >= 25000 }
            scope:sk_actor = { gold_reserves >= 50000 }
            exists = scope:sk_state
            scope:sk_state = { owner = c:KOR }
            scope:sk_state = {
                NOT = { has_building = building_railway }
                can_construct_building = building_railway
            }
        }
        AND = {
            c:KOR = { var:sk_pending = 172 }
            sk_live_17 = yes
            c:KOR = { gold_reserves >= 35000 }
            scope:sk_actor = { gold_reserves >= 35000 }
            exists = scope:sk_state
            scope:sk_state = { owner = c:KOR }
            scope:sk_state = {
                NOT = { has_building = building_railway }
                can_construct_building = building_railway
            }
        }
        AND = {
            c:KOR = { var:sk_pending = 181 }
            sk_live_18 = yes
            c:KOR = { gold_reserves >= 10000 }
            scope:sk_actor = { gold_reserves >= 30000 }
            exists = scope:sk_building
            scope:sk_building = { owner = c:KOR }
        }
        AND = {
            c:KOR = { var:sk_pending = 182 }
            sk_live_18 = yes
            c:KOR = { gold_reserves >= 20000 }
            scope:sk_actor = { gold_reserves >= 20000 }
            exists = scope:sk_building
            scope:sk_building = { owner = c:KOR }
        }
        AND = {
            c:KOR = { var:sk_pending = 191 }
            sk_live_19 = yes
            c:KOR = { has_variable = sk_base_partner var:sk_base_partner = scope:sk_actor }
        }
        AND = {
            c:KOR = { var:sk_pending = 192 }
            sk_live_19 = yes
        }
        AND = {
            c:KOR = { var:sk_pending = 201 }
            sk_live_20 = yes
        }
        AND = {
            c:KOR = { var:sk_pending = 203 }
            sk_live_20 = yes
        }
        AND = {
            c:KOR = { var:sk_pending = 211 }
            sk_live_21 = yes
            OR = {
                AND = { scope:sk_petition_kind = 1 c:KOR = { has_variable = sk_base_partner var:sk_base_partner = scope:sk_actor } }
                AND = { scope:sk_petition_kind = 2 c:KOR = { has_variable = sk_customs_partner var:sk_customs_partner = scope:sk_actor } }
                AND = { scope:sk_petition_kind = 3 c:KOR = { has_variable = sk_bank_partner var:sk_bank_partner = scope:sk_actor } }
            }
        }
        AND = {
            c:KOR = { var:sk_pending = 221 }
            sk_live_22 = yes
            can_create_treaty = {
                first_country = c:KOR
                second_country = scope:sk_actor
                is_draft = no
                binding_period = { years = 2 }
                articles_to_create = {
                    { article = trade_privilege source_country = c:KOR target_country = scope:sk_actor }
                }
            }
        }
        AND = {
            c:KOR = { var:sk_pending = 223 }
            sk_live_22 = yes
            exists = scope:sk_treaty
            scope:sk_treaty = { binds = c:KOR binds = scope:sk_rival
                any_scope_article = { count = 1 }
                any_scope_article = { has_type = trade_privilege source_country = c:KOR target_country = { sk_foreign_valid = yes } }
            }
        }
    }
}
```

### 13.2 공통 외국 응답 — 기존 이벤트 파일에 추가

기존 `namespace = scramble_for_korea_events` 아래에 넣는다. 모든 합의 효과는 상대국 수락 옵션 안에서 한 번만 적용한다. `sk_case`는 이벤트 체인의 임시 수치이며 전역 변수로 저장하지 않는다.
| 응답 코드 | 원래 선택 | 수락 시 추가 검사 |
|---|---|---|
| `111` | `.11.a` | `sk_live_11` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `123` | `.12.c` | `sk_live_12` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `133` | `.13.c` | `sk_live_13` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `141` | `.14.a` | `sk_live_14` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `151` | `.15.a` | `sk_live_15` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `152` | `.15.b` | `sk_live_15` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `161` | `.16.a` | `sk_live_16` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `162` | `.16.b` | `sk_live_16` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `171` | `.17.a` | `sk_live_17` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `172` | `.17.b` | `sk_live_17` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `181` | `.18.a` | `sk_live_18` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `182` | `.18.b` | `sk_live_18` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `191` | `.19.a` | `sk_live_19` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `192` | `.19.b` | `sk_live_19` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `201` | `.20.a` | `sk_live_20` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `203` | `.20.c` | `sk_live_20` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `211` | `.21.a` | `sk_live_21` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `221` | `.22.a` | `sk_live_22` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |
| `223` | `.22.c` | `sk_live_22` 및 아래 `sk_offer_acceptable`에 적힌 보유금·대상·조약 권한 |

```txt
scramble_for_korea_events.23 = {
    type = country_event
    placement = ROOT
    title = scramble_for_korea_events.23.t
    desc = {
        first_valid = {
            triggered_desc = { trigger = { scope:sk_case = 111 } desc = scramble_for_korea_events.23.d_111 }
            triggered_desc = { trigger = { scope:sk_case = 123 } desc = scramble_for_korea_events.23.d_123 }
            triggered_desc = { trigger = { scope:sk_case = 133 } desc = scramble_for_korea_events.23.d_133 }
            triggered_desc = { trigger = { scope:sk_case = 141 } desc = scramble_for_korea_events.23.d_141 }
            triggered_desc = { trigger = { scope:sk_case = 151 } desc = scramble_for_korea_events.23.d_151 }
            triggered_desc = { trigger = { scope:sk_case = 152 } desc = scramble_for_korea_events.23.d_152 }
            triggered_desc = { trigger = { scope:sk_case = 161 } desc = scramble_for_korea_events.23.d_161 }
            triggered_desc = { trigger = { scope:sk_case = 162 } desc = scramble_for_korea_events.23.d_162 }
            triggered_desc = { trigger = { scope:sk_case = 171 } desc = scramble_for_korea_events.23.d_171 }
            triggered_desc = { trigger = { scope:sk_case = 172 } desc = scramble_for_korea_events.23.d_172 }
            triggered_desc = { trigger = { scope:sk_case = 181 } desc = scramble_for_korea_events.23.d_181 }
            triggered_desc = { trigger = { scope:sk_case = 182 } desc = scramble_for_korea_events.23.d_182 }
            triggered_desc = { trigger = { scope:sk_case = 191 } desc = scramble_for_korea_events.23.d_191 }
            triggered_desc = { trigger = { scope:sk_case = 192 } desc = scramble_for_korea_events.23.d_192 }
            triggered_desc = { trigger = { scope:sk_case = 201 } desc = scramble_for_korea_events.23.d_201 }
            triggered_desc = { trigger = { scope:sk_case = 203 } desc = scramble_for_korea_events.23.d_203 }
            triggered_desc = { trigger = { scope:sk_case = 211 } desc = scramble_for_korea_events.23.d_211 }
            triggered_desc = { trigger = { scope:sk_case = 221 } desc = scramble_for_korea_events.23.d_221 }
            triggered_desc = { trigger = { scope:sk_case = 223 } desc = scramble_for_korea_events.23.d_223 }
            desc = scramble_for_korea_events.23.d
        }
    }
    flavor = scramble_for_korea_events.23.f
    icon = "gfx/interface/icons/event_icons/event_map.dds"
    duration = 1
    trigger = { sk_offer_valid = yes this = scope:sk_respondent }
    option = {
        name = scramble_for_korea_events.23.a
        ai_chance = { base = 60 }
        trigger = { sk_offer_acceptable = yes }
        if = {
            limit = { sk_offer_acceptable = yes }
            if = {
                limit = { c:KOR = { var:sk_pending = 111 } }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 10 } }
                scope:sk_rival = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
                c:KOR = { add_modifier = { name = sk_refuge days = 366 } }
                c:KOR = { set_variable = { name = sk_protector value = scope:sk_actor days = 366 } }
                c:KOR = {
                    set_variable = sk_job_111
                    trigger_event = { on_action = sk_finish_111 days = 365 }
                }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 123 } }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 3 } }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 3 } }
                scope:sk_rival = { scramble_for_korea_change_influence = { AMOUNT = -3 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 133 } }
                c:KOR = { add_treasury = -20000 }
                scope:sk_actor = { add_treasury = 20000 }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 2 } }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 2 } }
                c:KOR = { add_loyalists = { value = 0.01 pop_type = peasants } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 141 } }
                scope:sk_actor = { add_treasury = -25000 }
                c:KOR = { add_treasury = 25000 }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                c:KOR = { add_modifier = { name = sk_bank days = 730 } }
                c:KOR = { set_variable = { name = sk_bank_partner value = scope:sk_actor days = 730 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 151 } }
                c:KOR = { add_treasury = -10000 }
                scope:sk_actor = { add_treasury = -30000 }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                c:KOR = {
                    set_variable = sk_job_151
                    trigger_event = { on_action = sk_finish_151 days = 180 }
                }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 152 } }
                c:KOR = { add_treasury = -25000 }
                scope:sk_actor = { add_treasury = -15000 }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 3 } }
                c:KOR = {
                    set_variable = sk_job_152
                    trigger_event = { on_action = sk_finish_152 days = 180 }
                }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 161 } }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = -3 } }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                c:KOR = { add_modifier = { name = sk_customs days = 730 } }
                c:KOR = { set_variable = { name = sk_customs_partner value = scope:sk_actor days = 730 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 162 } }
                c:KOR = { add_treasury = -10000 }
                scope:sk_actor = { add_treasury = 10000 }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 2 } }
                c:KOR = { add_modifier = { name = sk_customs_advice days = 730 } }
                c:KOR = { set_variable = { name = sk_customs_partner value = scope:sk_actor days = 730 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 171 } }
                c:KOR = { add_treasury = -25000 }
                scope:sk_actor = { add_treasury = -50000 }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                c:KOR = { set_variable = { name = sk_rail_partner value = scope:sk_actor days = 1825 } }
                c:KOR = {
                    set_variable = sk_job_171
                    trigger_event = { on_action = sk_finish_171 days = 365 }
                }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 172 } }
                c:KOR = { add_treasury = -35000 }
                scope:sk_actor = { add_treasury = -35000 }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 3 } }
                c:KOR = { set_variable = { name = sk_rail_partner value = scope:sk_actor days = 1825 } }
                c:KOR = {
                    set_variable = sk_job_172
                    trigger_event = { on_action = sk_finish_172 days = 365 }
                }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 181 } }
                c:KOR = { add_treasury = -10000 }
                scope:sk_actor = { add_treasury = -30000 }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = -3 } }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                scope:sk_building = { add_modifier = { name = sk_mine days = 1825 } }
                c:KOR = { set_variable = { name = sk_mine_partner value = scope:sk_actor days = 1825 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 182 } }
                c:KOR = { add_treasury = -20000 }
                scope:sk_actor = { add_treasury = -20000 }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 3 } }
                scope:sk_building = { add_modifier = { name = sk_mine_joint days = 1825 } }
                c:KOR = { set_variable = { name = sk_mine_partner value = scope:sk_actor days = 1825 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 191 } }
                scope:sk_actor = { remove_modifier = sk_base }
                c:KOR = { remove_variable = sk_base_partner }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 192 } }
                scope:sk_rival = { scramble_for_korea_change_influence = { AMOUNT = 3 } }
                c:KOR = { add_modifier = { name = sk_diplomatic_support days = 365 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 201 } }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = -3 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 203 } }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
                scope:sk_rival = { scramble_for_korea_change_influence = { AMOUNT = 2 } }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 2 } }
                c:KOR = { add_modifier = { name = sk_administration_cost days = 365 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 211 } }
                if = {
                    limit = { scope:sk_petition_kind = 1 }
                    scope:sk_actor = { remove_modifier = sk_base }
                    c:KOR = { remove_variable = sk_base_partner }

                }
                if = {
                    limit = { scope:sk_petition_kind = 2 }
                    c:KOR = { remove_modifier = sk_customs }
                    c:KOR = { remove_variable = sk_customs_partner }
                    c:KOR = { remove_modifier = sk_customs_advice }
                }
                if = {
                    limit = { scope:sk_petition_kind = 3 }
                    c:KOR = { remove_modifier = sk_bank }
                    c:KOR = { remove_variable = sk_bank_partner }

                }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = -5 } }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                c:KOR = { add_loyalists = { value = 0.02 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 221 } }
                create_treaty = {
                    first_country = c:KOR
                    second_country = scope:sk_actor
                    is_draft = no
                    binding_period = { years = 2 }
                    articles_to_create = {
                        { article = trade_privilege source_country = c:KOR target_country = scope:sk_actor }
                    }
                }
                scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = 3 } }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = -3 } }
            }
            if = {
                limit = { c:KOR = { var:sk_pending = 223 } }
                scope:sk_treaty = { withdraw = { country = c:KOR apply_break_penalties = no } }
                scope:sk_rival = { scramble_for_korea_change_influence = { AMOUNT = -3 } }
                c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 3 } }
            }
            c:KOR = { remove_variable = sk_pending }
        }
    }
    option = {
        name = scramble_for_korea_events.23.b
        default_option = yes
        ai_chance = { base = 40 }
        if = {
            limit = { sk_offer_valid = yes }
            change_relations = { country = c:KOR value = -5 }
        }
        if = {
            limit = {
                exists = c:KOR
                c:KOR = { has_variable = sk_pending var:sk_pending = scope:sk_case }
            }
            c:KOR = { remove_variable = sk_pending }
        }
    }
}
```

### 13.3 월간 추첨·사업 완료 — 기존 `common/on_actions/korea_code_on_actions.txt`에 추가

기존 조선 on_action 파일에 아래 이름 있는 정의를 추가한다. 기존 `korea_on_monthly_pulse_country`에 다시 연결하지 않으며, JE의 월간 콜백 한 곳에서만 호출한다. 이벤트 자체를 바닐라 전역 월간 목록에 추가하지 않는다. `on_action.effect`에서 만든 스코프는 같은 on_action의 `events` 목록에 전달되지 않으므로, 대상 선택은 반드시 6절 각 이벤트의 `immediate`에서 한다.

```txt
sk_monthly_events = {
    trigger = {
        c:KOR ?= this
        sk_world_valid = yes
        NOT = { has_variable = sk_pending }
    }
    random_events = {
        chance_to_happen = 25
        100 = scramble_for_korea_events.11
        100 = scramble_for_korea_events.12
        100 = scramble_for_korea_events.13
        100 = scramble_for_korea_events.14
        100 = scramble_for_korea_events.15
        100 = scramble_for_korea_events.16
        100 = scramble_for_korea_events.17
        100 = scramble_for_korea_events.18
        100 = scramble_for_korea_events.19
        100 = scramble_for_korea_events.20
        100 = scramble_for_korea_events.21
        100 = scramble_for_korea_events.22
    }
}

sk_finish_111 = {
    effect = {
        c:KOR ?= {
            if = {
                limit = { has_variable = sk_job_111 }
                remove_variable = sk_job_111
                if = {
                    limit = {
                        sk_world_valid = yes
                        exists = scope:sk_actor
                        scope:sk_actor = { sk_foreign_valid = yes }
                        c:KOR = { has_variable = sk_protector var:sk_protector = scope:sk_actor }
                    }
                    c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 3 } }
                    scope:sk_actor = { scramble_for_korea_change_influence = { AMOUNT = -3 } }
                    c:KOR = { remove_modifier = sk_refuge remove_variable = sk_protector }
                }
            }
        }
    }
}

sk_finish_143 = {
    effect = {
        c:KOR ?= {
            if = {
                limit = { has_variable = sk_job_143 }
                remove_variable = sk_job_143
                if = {
                    limit = {
                        sk_world_valid = yes
                    }
                    c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                    c:KOR = { add_modifier = { name = sk_currency days = 730 } }
                }
            }
        }
    }
}

sk_finish_151 = {
    effect = {
        c:KOR ?= {
            if = {
                limit = { has_variable = sk_job_151 }
                remove_variable = sk_job_151
                if = {
                    limit = {
                        sk_world_valid = yes
                        exists = scope:sk_state
                        scope:sk_state = { owner = c:KOR }
                    }
                    scope:sk_state = { add_modifier = { name = sk_telegraph days = 1825 } }
                }
            }
        }
    }
}

sk_finish_152 = {
    effect = {
        c:KOR ?= {
            if = {
                limit = { has_variable = sk_job_152 }
                remove_variable = sk_job_152
                if = {
                    limit = {
                        sk_world_valid = yes
                        exists = scope:sk_state
                        scope:sk_state = { owner = c:KOR }
                    }
                    c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 2 } }
                    scope:sk_state = { add_modifier = { name = sk_telegraph days = 1825 } }
                }
            }
        }
    }
}

sk_finish_153 = {
    effect = {
        c:KOR ?= {
            if = {
                limit = { has_variable = sk_job_153 }
                remove_variable = sk_job_153
                if = {
                    limit = {
                        sk_world_valid = yes
                        exists = scope:sk_state
                        scope:sk_state = { owner = c:KOR }
                    }
                    c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                    scope:sk_state = { add_modifier = { name = sk_telegraph days = 1825 } }
                }
            }
        }
    }
}

sk_finish_163 = {
    effect = {
        c:KOR ?= {
            if = {
                limit = { has_variable = sk_job_163 }
                remove_variable = sk_job_163
                if = {
                    limit = {
                        sk_world_valid = yes
                    }
                    c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                    c:KOR = { add_modifier = { name = sk_customs_domestic days = 730 } }
                }
            }
        }
    }
}

sk_finish_171 = {
    effect = {
        c:KOR ?= {
            if = {
                limit = { has_variable = sk_job_171 }
                remove_variable = sk_job_171
                if = {
                    limit = {
                        sk_world_valid = yes
                        exists = scope:sk_state
                        scope:sk_state = { owner = c:KOR }
                        scope:sk_state = {
                            NOT = { has_building = building_railway }
                            can_construct_building = building_railway
                        }
                    }
                    scope:sk_state = { create_building = { building = building_railway level = 1 } }
                }
            }
        }
    }
}

sk_finish_172 = {
    effect = {
        c:KOR ?= {
            if = {
                limit = { has_variable = sk_job_172 }
                remove_variable = sk_job_172
                if = {
                    limit = {
                        sk_world_valid = yes
                        exists = scope:sk_state
                        scope:sk_state = { owner = c:KOR }
                        scope:sk_state = {
                            NOT = { has_building = building_railway }
                            can_construct_building = building_railway
                        }
                    }
                    scope:sk_state = { create_building = { building = building_railway level = 1 } }
                }
            }
        }
    }
}

sk_finish_173 = {
    effect = {
        c:KOR ?= {
            if = {
                limit = { has_variable = sk_job_173 }
                remove_variable = sk_job_173
                if = {
                    limit = {
                        sk_world_valid = yes
                        exists = scope:sk_state
                        scope:sk_state = { owner = c:KOR }
                        scope:sk_state = {
                            NOT = { has_building = building_railway }
                            can_construct_building = building_railway
                        }
                    }
                    scope:sk_state = { create_building = { building = building_railway level = 1 } }
                    c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                }
            }
        }
    }
}

sk_finish_183 = {
    effect = {
        c:KOR ?= {
            if = {
                limit = { has_variable = sk_job_183 }
                remove_variable = sk_job_183
                if = {
                    limit = {
                        sk_world_valid = yes
                        exists = scope:sk_building
                        scope:sk_building = { owner = c:KOR }
                    }
                    c:KOR = { scramble_for_korea_change_influence = { AMOUNT = 5 } }
                    scope:sk_building = { add_modifier = { name = sk_mine days = 1825 } }
                }
            }
        }
    }
}
```

기존 JE의 `on_monthly_pulse.effect`에서 마지막 영향력 순회 **뒤**에 아래 한 줄을 넣는다. 승패 조건을 만족하면 위 on_action 트리거가 호출을 무효화한다.

```txt
c:KOR ?= { trigger_event = { on_action = sk_monthly_events } }
```

### 13.4 modifier 전문 — 기존 `eafg_scramble_for_korea_modifiers.txt`에 추가

기간은 각 `add_modifier` 호출에 명시되어 있다. 같은 이름을 중복 합산하지 않는다. 외국 거점의 위신 +5는 정치적 압력의 표현이고 실제 전투 능력 보너스가 아니다.

```txt
sk_refuge = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_legitimacy_base_add = 10
}

sk_guard = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_authority_add = 50
}

sk_relocation = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_legitimacy_base_add = 2
}

sk_diplomatic_cost = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_influence_add = -25
}

sk_diplomatic_support = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_influence_add = 25
}

sk_administration_cost = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_bureaucracy_add = -25
}

sk_assembly_compromise = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_authority_add = -25
}

sk_bank = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_tax_income_add = 100
}

sk_currency = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_tax_income_add = 100
}

sk_telegraph = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    state_infrastructure_add = 5
}

sk_customs = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_bureaucracy_add = 25
    country_tax_income_add = 100
}

sk_customs_advice = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_bureaucracy_add = 25
}

sk_customs_domestic = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_bureaucracy_add = 50
}

sk_mine = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    building_throughput_add = 0.10
}

sk_mine_joint = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    building_throughput_add = 0.05
}

sk_base = {
    icon = gfx/interface/icons/timed_modifier_icons/modifier_documents_positive.dds
    country_prestige_add = 5
}
```

### 13.5 저장 상태·이탈·종료 정리

| 상태 | 저장 위치·용도 | 제거 시점 |
|---|---|---|
| `sk_pending` | 조선, 본 사건/응답 코드. 선택 동시 실행과 오래된 응답 방지 | 선택 종결·거절·무효 취소·365일 만료·전체 종료 |
| `sk_protector` | 조선, 상대 국가 스코프; .11 환궁 | 366일 만료·상대 이탈·계약 해제·전체 종료 |
| `sk_bank_partner` | 조선, 상대 국가 스코프; .14 은행 계약·.21 청원 | 730일 만료·상대 이탈·계약 해제·전체 종료 |
| `sk_customs_partner` | 조선, 상대 국가 스코프; .16 해관 계약·.21 청원 | 730일 만료·상대 이탈·계약 해제·전체 종료 |
| `sk_rail_partner` | 조선, 상대 국가 스코프; .17 부설 참여 | 1825일 만료·상대 이탈·계약 해제·전체 종료 |
| `sk_mine_partner` | 조선, 상대 국가 스코프; .18 광산 참여 | 1825일 만료·상대 이탈·계약 해제·전체 종료 |
| `sk_base_partner` | 조선, 상대 국가 스코프; .19/.20 거점·.21 청원 | 730일 만료·상대 이탈·계약 해제·전체 종료 |
| `sk_job_111` | 조선, 365일 뒤 예약 콜백의 일회 실행 표시 | 콜백 진입 시 즉시 제거·전체 종료 |
| `sk_job_143` | 조선, 365일 뒤 예약 콜백의 일회 실행 표시 | 콜백 진입 시 즉시 제거·전체 종료 |
| `sk_job_151` | 조선, 180일 뒤 예약 콜백의 일회 실행 표시 | 콜백 진입 시 즉시 제거·전체 종료 |
| `sk_job_152` | 조선, 180일 뒤 예약 콜백의 일회 실행 표시 | 콜백 진입 시 즉시 제거·전체 종료 |
| `sk_job_153` | 조선, 365일 뒤 예약 콜백의 일회 실행 표시 | 콜백 진입 시 즉시 제거·전체 종료 |
| `sk_job_163` | 조선, 180일 뒤 예약 콜백의 일회 실행 표시 | 콜백 진입 시 즉시 제거·전체 종료 |
| `sk_job_171` | 조선, 365일 뒤 예약 콜백의 일회 실행 표시 | 콜백 진입 시 즉시 제거·전체 종료 |
| `sk_job_172` | 조선, 365일 뒤 예약 콜백의 일회 실행 표시 | 콜백 진입 시 즉시 제거·전체 종료 |
| `sk_job_173` | 조선, 365일 뒤 예약 콜백의 일회 실행 표시 | 콜백 진입 시 즉시 제거·전체 종료 |
| `sk_job_183` | 조선, 180일 뒤 예약 콜백의 일회 실행 표시 | 콜백 진입 시 즉시 제거·전체 종료 |

국가 이탈 처리의 `scramble_for_korea_clear_country` 끝에 다음을 추가한다. `root`나 `prev`에 의존하지 않고 이탈국을 임시 스코프에 저장한다. 조선 소멸 시 조선 측 변수는 엔진과 전체 종료 정리에 맡긴다. 이미 납부한 건설비·완성된 철도는 되돌리지 않는다.

```txt
save_scope_as = sk_departing
if = { limit = { has_modifier = sk_base } remove_modifier = sk_base }
c:KOR ?= {
    if = {
        limit = { has_variable = sk_protector var:sk_protector = scope:sk_departing }
        remove_variable = sk_protector
        remove_modifier = sk_refuge
        remove_variable = sk_job_111
    }
    if = {
        limit = { has_variable = sk_bank_partner var:sk_bank_partner = scope:sk_departing }
        remove_variable = sk_bank_partner
        remove_modifier = sk_bank
    }
    if = {
        limit = { has_variable = sk_customs_partner var:sk_customs_partner = scope:sk_departing }
        remove_variable = sk_customs_partner
        remove_modifier = sk_customs
        remove_modifier = sk_customs_advice
    }
    if = {
        limit = { has_variable = sk_rail_partner var:sk_rail_partner = scope:sk_departing }
        remove_variable = sk_rail_partner
    }
    if = {
        limit = { has_variable = sk_mine_partner var:sk_mine_partner = scope:sk_departing }
        remove_variable = sk_mine_partner
        every_scope_building = { remove_modifier = sk_mine remove_modifier = sk_mine_joint }
    }
    if = {
        limit = { has_variable = sk_base_partner var:sk_base_partner = scope:sk_departing }
        remove_variable = sk_base_partner
    }
}
```

전체 `scramble_for_korea_cleanup` 끝에는 다음을 추가한다. 모든 국가를 훑어 이미 양도된 주·건물에 남은 이번 사건 modifier도 제거한다. 신규 modifier는 모두 경쟁 전용 기간 효과로 정의하며, 종료 뒤 유지하는 별도 보상은 만들지 않는다.

```txt
c:KOR ?= {
    remove_variable = sk_pending
    remove_variable = sk_job_111
    remove_variable = sk_job_143
    remove_variable = sk_job_151
    remove_variable = sk_job_152
    remove_variable = sk_job_153
    remove_variable = sk_job_163
    remove_variable = sk_job_171
    remove_variable = sk_job_172
    remove_variable = sk_job_173
    remove_variable = sk_job_183
    remove_variable = sk_protector
    remove_variable = sk_bank_partner
    remove_variable = sk_customs_partner
    remove_variable = sk_rail_partner
    remove_variable = sk_mine_partner
    remove_variable = sk_base_partner
    if = { limit = { has_modifier = sk_refuge } remove_modifier = sk_refuge }
    if = { limit = { has_modifier = sk_guard } remove_modifier = sk_guard }
    if = { limit = { has_modifier = sk_relocation } remove_modifier = sk_relocation }
    if = { limit = { has_modifier = sk_diplomatic_cost } remove_modifier = sk_diplomatic_cost }
    if = { limit = { has_modifier = sk_diplomatic_support } remove_modifier = sk_diplomatic_support }
    if = { limit = { has_modifier = sk_administration_cost } remove_modifier = sk_administration_cost }
    if = { limit = { has_modifier = sk_assembly_compromise } remove_modifier = sk_assembly_compromise }
    if = { limit = { has_modifier = sk_bank } remove_modifier = sk_bank }
    if = { limit = { has_modifier = sk_currency } remove_modifier = sk_currency }
    if = { limit = { has_modifier = sk_customs } remove_modifier = sk_customs }
    if = { limit = { has_modifier = sk_customs_advice } remove_modifier = sk_customs_advice }
    if = { limit = { has_modifier = sk_customs_domestic } remove_modifier = sk_customs_domestic }
}
every_country = {
    if = { limit = { has_modifier = sk_base } remove_modifier = sk_base }
    every_scope_state = { if = { limit = { has_modifier = sk_telegraph } remove_modifier = sk_telegraph } }
    every_scope_building = {
        if = { limit = { has_modifier = sk_mine } remove_modifier = sk_mine }
        if = { limit = { has_modifier = sk_mine_joint } remove_modifier = sk_mine_joint }
    }
}
```

### 13.6 스코프·상태 판정의 세부 의미

- `.14`·`.20`의 `any_scope_building → any_country → prev → levels_owned_by_country.target = prev`에서 바깥 `prev`는 검사 중인 조선 건물, 가장 안쪽 `prev`는 검사 중인 외국이다. `immediate`에서도 같은 순서로 건물과 실제 투자국을 고른다. 창을 연 뒤 지분이 줄면 `sk_live_14/20`에서 다시 차단한다.
- 영향력 숫자는 조선과 해당 관여국만 변경한다. 관여국 이탈 후 같은 국가가 재참가한 경우 현재 자격을 충족하면 기존에 열린 유효 창에 응답할 수 있다. 본 사건의 100,000일 cooldown과 계약 변수는 재참가로 초기화하지 않으므로 동일 사건을 재추첨해 보상받을 수 없다.
- 구휼·은행권·군사 거점의 서술은 위 코드의 제한을 따른다. 실제 수출 금지, 통화 교체, 지도상 군사 점령이 일어났다는 게임 UI 안내를 붙이지 않는다. 철도 생성과 통상특권 조약 생성은 실제 엔진 효과다.
- 모든 지연 작업은 `sk_job_코드`를 먼저 지우고 유효성을 검사한다. 같은 콜백이 중복 호출되어도 두 번째는 보상을 주지 않는다. 완공 창을 추가로 띄우지 않으며 영향력·modifier 툴팁으로 결과를 표시한다.

### 13.7 구현 적용 순서와 확인 범위

1. 공통 트리거와 modifier를 등록하고, 6절의 12개 본 이벤트와 13.2의 응답 이벤트를 기존 이벤트 파일에 추가한다.
2. 기존 조선 on_action 파일에 정의를 추가하고 JE 월간 effect 마지막에 호출을 추가한다. 기존 주간·월간 sync, 참가·종료 콜백은 그대로 사용한다.
3. 국가 이탈·전체 종료 정리를 추가하고 한·영·중 현지화 키를 채운다. 이 문서의 선택지 표는 현지화 텍스트의 기준이다.
4. 이벤트 호출과 정의, modifier, 기술·건물·법률·조약 타입을 검사한다. 게임에서 12개 본 사건 및 응답·거절·이탈·완공·종료 시나리오를 확인한다.

코드는 로컬 바닐라와 엔진 문서를 근거로 작성한 구현 초안이다. 문서의 정적 일관성 확인과 게임 내 파서·GUI·예약 스코프 검증은 구분한다. 게임 실행 검증 전에는 ‘그대로 복사해 실행 검증 완료’라고 표시하지 않는다.

### 2026-10-22 바닐라 기반 상세 명세 갱신

6절의 사건 11~22를 실제 트리거·국가/대상 선정·선택지 효과·비용·AI 가중치가 있는 코드로 교체했다. 13절에는 보조 응답 23, 월간 추첨, 지연 콜백, 공통 조건, modifier 및 종료 정리 전문을 추가했다. 계획 문서만 변경했으며 활성 스크립트·로컬은 아직 적용하지 않았다.
