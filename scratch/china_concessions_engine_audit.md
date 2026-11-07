# 조계지 기업·건물 엔진 기능 조사

조사일: 2026-11-08. 대상은 로컬 Victoria 3 **1.15.0**과 현재 모드다. `logs/code_revisions.log`의 `game_branch: release/1.15.0` 및 읽기 전용으로 확인한 `러시아_1857_01_01.v3`의 버전이 일치한다. `documentation`의 효과·트리거·target 로그는 2026-11-05 생성본이다.

이번 작업은 설치 파일·문서·GUI·기존 저장 데이터 조사다. 게임을 실행하거나 새 실험 저장을 만들지 않았고 기존 저장도 수정하지 않았다. 아래의 「공개 경로를 찾지 못함」은 조사한 인터페이스 범위의 결론이며 엔진 내부에서 절대 불가능하다는 증명은 아니다.

**후속 사용자 결정 반영:** 국가별 건물 분리는 제외하고 주별 공유 조계지 건물을 유지한다. 자동 투자는 저널에서 후보를 계산한 뒤 민간 큐에 등록한다. 도심지가 감소해도 기존 건물을 유지하므로 강제 축소 cap은 요구사항에서 제외했다. 현재 코드의 실행 순서와 제한은 [설계 계획](china_concessions_design_plan.md)을 따른다. 아래 엔진 제약 중 기업별 지분 반환·생산 중단과 큐의 재원/기업 귀속은 여전히 별도 검증 대상이다.

## 1. 결론

**기업의 정상 민간 건설을 그 기업의 조계가 있는 실제 state에만 한정하는 기능은 현재 확인한 공개 스크립트로 구현 경로를 확정할 수 없다.** 국가별 투자자 조건·건물별 건설 가능 조건·기업 본사 위치·AI 건설 우선순위는 제공되지만, 이들을 조합해 특정 기업 하나만 제한할 근거는 부족하다.

반면 이전 계획에서 미확인으로 남겼던 다음 부분은 근거를 확보했다.

- `create_building.add_ownership.company`로 기업 유형·국가·레벨을 지정하는 바닐라 사용 예시.
- 일반 기업 유형을 여러 국가가 동시에 보유하는 실제 저장 사례.
- GUI에서 소유 기업과 소유 레벨을 읽을 수 있는 데이터 경로.
- 회사 설립·해산 callback의 root 국가와 `scope:company` 계약.
- 조약 파기 전용 callback 및 남은 구속 기간 조회 경로.

새로 발견한 제약은 회사 본사당 최소 실제 자산 5레벨과 설립/해산 쿨다운이다. 「조계지 1레벨 = 무역소 5레벨 능력」은 「기업 자산 5레벨」과 같지 않다.

## 2. 민간 건설 지역 제한 검토

| 후보 기능 | 확인된 범위 | 조계 기업만 특정 주에 제한할 수 있는가? |
| --- | --- | --- |
| company `building_types`, `extension_building_types` | 산업 유형 목록 | 지역 조건이 아님 |
| company `can_establish_in` | 기업 본사 건물이 위치할 수 있는 state 검사 | 기존 기업의 모든 건설 대상 검사라는 근거 없음 |
| `set_company_state_region` | 기업 본사 위치 설정 | 투자 대상 whitelist가 아님 |
| `ai_construction_targets.state_trigger` | 설립하려는 기업을 위해 국가 AI가 건설할 주를 우대 | 민간 건설에도 가중치가 있지만 특정 기업의 강제 금지는 아님 |
| building `can_build_private` | 바닐라 무역소에서 state 및 `scope:investor_country` 사용 | 기업 scope가 확인되지 않아 같은 국가의 모든 민간 투자자에 영향 |
| `set_available_for_autonomous_investment` / `unset_available_for_autonomous_investment` | state×building type의 자율 투자 대상 여부 | 특정 기업 인자 없음. 다른 투자자의 공장 건설도 건드림 |
| 투자 헌장 | 해외 지역 본사를 설치할 수 있게 함 | 조계 state 목록을 받는 헌장이 아님 |
| 외국 투자권 조약 | 국가 간 투자 접근 | 개별 기업·state 제한 아님 |
| `start_privately_funded_building_construction` | state에서 특정 building type의 민간 건설 시작 | 투자 기업 지정·귀속 보장이 문서화되어 있지 않음 |
| 본사 주 투자 가중치 | `OWNER_COMPANY_OWN_STATE_MULT = 100.0` | 선택 가중치이며 본사 밖 금지 조건이 아님 |

근거 파일:

- [기업 정의 문서](</D:/SteamLibrary/steamapps/common/Victoria 3/game/common/company_types/companies.md:41>): `can_establish_in`; 56행 이하 `ai_construction_targets`는 설립 준비 중 AI 설명.
- [건설 트리거](</D:/SteamLibrary/steamapps/common/Victoria 3/game/common/scripted_triggers/00_building_triggers.txt:1>): 광동 체제/쇄국 무역소 제한에서 `scope:investor_country` 사용.
- [AI 설정](</D:/SteamLibrary/steamapps/common/Victoria 3/game/common/defines/00_ai.txt:851>): 국가 AI의 기업 설립 목표 가중치. 945행은 본사 주 소유 기업 선택 가중치.
- [투자 헌장](</D:/SteamLibrary/steamapps/common/Victoria 3/game/common/company_charter_types/00_company_charter_types.txt:1>)과 [외국 투자권](</D:/SteamLibrary/steamapps/common/Victoria 3/game/common/treaty_articles/07_foreign_investment_rights.txt:1>).
- [생성 효과 문서](../documentation/effects.log): 자율 투자 가능 여부 및 민간 건설 시작 효과.

### 투자 재원 정정

바닐라 [지역 본사 개념 설명](</D:/SteamLibrary/steamapps/common/Victoria 3/game/localization/english/concepts_l_english.yml:282>)에 따르면 해외 지역 본사는 소재국 투자풀을 사용해 건설하고, 배당 일부를 원소속국 투자풀에 재투자한다. 따라서 이전 계획의 「실제 회사 자금으로 건설」이라는 표현은 독립적인 기업 금고를 뜻하지 않도록 고쳤다. 기업 소유 지분, 자금 출처, 공사 실행 주체는 분리해서 확인해야 한다.

### 기존 저장에서 확인한 범위

1.15.0 저장 `러시아_1857_01_01.v3`에서 회사 본사의 assets → building_ownership_manager → 실제 건물을 추적했다.

| 기업 본사 | 본사 state ID | 다른 주의 소유 자산 예시 |
| --- | ---: | --- |
| `building_company_dmc`, building ID 323 | 9 | state 444의 방직공장 5레벨, state 442의 석탄 광산 18레벨 |
| `building_company_john_cockerill`, building ID 440 | 476 | state 477의 무역소 7레벨 및 1847.10.16 설립 자동차 산업 건물 2레벨 |

이는 본사 소재 주와 기업 소유 자산 소재 주가 같아야 한다는 불변식이 없음을 보여준다. 해당 공장의 최초 건설자나 매입 경로는 이 기록만으로 확정할 수 없으며, 「민간 건설 지역 제한 불가」의 단독 증거로 사용하지 않는다.

### 채택하지 않은 우회안

- 국가 단위로 민간 건설을 막기: 해당 국가의 다른 기업/금융 지구 투자까지 제한하므로 요구 범위가 달라진다.
- 국가 비용을 차감하고 회사 소유 공장 즉시 생성: 위치·귀속은 지정할 수 있지만 정상 민간 건설을 구현한 것이 아니다.
- 회사의 조계 주 우선순위를 높이기: 우대일 뿐 다른 주 건설 금지가 아니다.
- 비조계 주의 산업 건설을 전부 막기: 중국과 다른 국가의 정상 민간 경제까지 훼손한다.

이 중 어느 것도 사용자 요구와 동일한 방식으로 기본 계획에 채택하지 않았다.

## 3. 실제 회사 소유권: 생성은 근거 발견, 부분 제거는 미확인

### 생성 문법

바닐라 [벨기에 건물 역사](</D:/SteamLibrary/steamapps/common/Victoria 3/game/common/history/buildings/00_west_europe.txt:5346>)는 다음 형식을 사용한다.

```paradox
create_building = {
    building = "building_steel_mill"
    add_ownership = {
        company = {
            type = company_john_cockerill
            country = "c:BEL"
            levels = 2
        }
    }
}
```

[알래스카 건물 역사](</D:/SteamLibrary/steamapps/common/Victoria 3/game/common/history/buildings/05_north_america.txt:445>)에도 `company_russian_american_company` / `c:RUS` / `levels` 지정 사례가 있다. 생성 로그는 회사 분기를 누락했으므로 로그에 없다는 이유로 지원 부재라고 결론 내리지 않는다. 주의 현재 owner와 회사 소속국이 같아야 한다고 가정하지 않는다.

이 문법으로 조계지에 `type=company_eafp_concession`, `country=scope:concession_holder`, `levels=1`을 지정하는 계획으로 구체화했다. 아직 캠페인 중 동적 국가 스코프 및 기존 건물의 추가 레벨 동작은 실행하지 않았다.

### 조회와 제거

- `company_owned_levels`: 회사 전체 자산 레벨. 주·건물 필터를 받는 함수가 아니다.
- `levels_owned_by_country`/`fraction_of_levels_owned_by_country`: 특정 건물의 국가 전체 투자자 지분 비교. 해당 국가의 전용 기업만 분리하지 못한다.
- `BuildingOwnership.GetLevel`: GUI에서 정확한 소유 레벨을 표시 가능. 이를 서버의 script value 함수로 호출할 수 있다는 뜻은 아니다.
- `remove_building`: 해당 state의 건물 전체 제거. 한 회사 지분만 줄이는 효과가 아니다.
- `create_building.level`: 기존 레벨과 지정값 중 큰 값을 사용하므로 축소 효과로 사용할 수 없다.
- 소유 기업별 -N레벨, 회사 지분만 이전/축소하는 공개 효과는 조사 범위에서 찾지 못했다. `add_ownership`의 음수 레벨을 지원한다고 추측하거나 전체 삭제 후 타국 지분을 재생성하지 않는다.

따라서 공유 건물 구조의 일부 국가 반환은 아직 확정할 수 없다. 도심지 감소 후 cap 축소는 후속 사용자 결정에 따라 구현 대상에서 제외하고 기존 건물을 보존한다.

## 4. 기업 수명·최소 자산·슬롯·해산

### 일반 기업 유형과 국가별 회사

바닐라 `99_basic_companies.txt`의 `flavored_company = no`를 사용한다. 같은 저장에서 `company_basic_forestry`가 국가 ID 80·10·24·41·42·87에 동시에 존재했다. `company_basic_fabrics`, `company_basic_agriculture_1`도 여러 국가의 인스턴스를 확인했다. 국가별 전용 회사 1개에 공통 일반 기업 유형을 쓰는 구조는 실제 근거가 있다.

### 최소 자산과 초기 부여 순서

[경제 defines](</D:/SteamLibrary/steamapps/common/Victoria 3/game/common/defines/00_defines.txt:692>)는 `COMPANY_MINIMUM_LEVELS_PER_HQ = 5`를 설립/유지 최소 자산으로 설명한다. 설립 실패 안내에는 한 주에 해당 국가 또는 그 민간 투자자가 보유하고, 아직 다른 기업 소유가 아닌 자산 조건도 있다.

[벨기에 국가 역사](</D:/SteamLibrary/steamapps/common/Victoria 3/game/common/history/countries/bel - belgium.txt:29>)는 `add_company` 후 `set_company_state_region`을 사용한다. 그러나 역사 생성 순서가 캠페인 중 자산 0 회사의 생성·유지를 보장하지는 않는다. 첫 조계 1레벨만 가진 회사를 엔진이 유지하는지, 국내 적격 자산을 자동 편입하는지, 글로벌 최소값을 바꾸지 않고 성립하는지 실행 시험해야 한다.

### callback과 슬롯

[바닐라 on-actions](</D:/SteamLibrary/steamapps/common/Victoria 3/game/common/on_actions/00_code_on_actions.txt:3830>)가 다음을 명시한다.

```text
on_company_established: root = 회사 소속 국가, scope:company = 설립된 회사
on_company_disbanded: root = 회사 소속 국가, scope:company = 해산된 회사
```

슬롯 보정 `country_max_companies_add = 1`은 국가 modifier로 적용할 수 있다. 회사 modifier로 직접 붙이는 것으로 설명하지 않는다. `add_modifier` 문서의 지원 scope에 company는 없으며, 번영 조건의 `prosperity_modifier`로 처리하면 상시 슬롯 보정이 아니다.

설립 후 해산 제한 60개월, 해산 후 재설립 제한 48개월이 기본 설정에 있다. 스크립트 `add_company/remove_company`가 이를 우회하는지, 삭제 callback에서 회사가 여전히 유효한지 시험해야 한다.

### 일반 산업 지분이 남은 해산

[해산 UI 안내](</D:/SteamLibrary/steamapps/common/Victoria 3/game/localization/english/interfaces_l_english.yml:152>)는 회사 자산 이전과 국유화 보상 비용을 명시한다. 반면 `remove_company` 효과 설명에는 그 비용·귀속 규칙이 없다. UI 명령의 동작을 스크립트 효과에 그대로 일반화할 수 없으므로 자산·국고·건설 대기열의 전후 비교를 런타임 시험으로 남겼다.

## 5. cap·위신 중단·무역 기능·반환 사유

| 과제 | 조사 결과 | 계획 반영 |
| --- | --- | --- |
| 신규/확장 cap | 건물 `level` 직접 조회와 기존 state scope 판정 경로 있음 | 모든 추가 진입점에서 `T+1≤U` 재검사 유지 |
| 도심지 감소 후 cap | 감소·삭제 hook은 미확인이나 사용자 결정으로 자동 축소 불필요 | 기존 건물·지분 유지, 초과 표시, 추가 설치·확장만 차단 |
| `on_investment_decreased` 활용 | 바닐라 root가 Institution | 건물/기업 지분 감소 hook으로 사용 금지 |
| max-level 설정 | building `has_max_level`, group `stateregion_max_level`은 제한 단위 설정 | 도심지 연동 cap이나 기업별 축소를 자동 제공한다고 가정 금지 |
| 공유 건물의 일부 지분 정지 | `deactivate_building`은 state 내 특정 building type 전체를 대상으로 함 | 위신이 낮은 한 국가 때문에 타국 지분까지 정지하지 않음. 분리 구조는 사용자 지시로 제외. 특권 한정 중단은 미확정 |
| 무역소 5레벨 역할 | 고용·state 무역능력·투입재의 바닐라 수치 확인 | 5배 PM 설계 유지. 신설 그룹의 실제 무역수입 참여는 실행 시험 |
| 파기 원인 | `on_break`는 구속 기간 중 의도적 파기, `on_withdrawal`과 함께 실행 | 반환 처리 한 곳 유지. callback 순서를 가정해 뒤에서 삭제 전 레벨을 읽지 않음 |
| 조약 구속 기간 | article→treaty→remaining_binding_period 연결 있음 | 철회 중 강제/정상 판정에 사용할 후보. 자동 종료·순서 시험 필요 |
| 해제 충격 중첩 | modifier 적용 자체는 지원. 같은 키의 손실별 중첩/독립 만료는 확인하지 않음 | 작은 손실이 큰 이전 충격을 덮지 않는지 실제 시험 |

`on_building_expanded`는 root=Building으로 주석이 있으나 도시화에 따른 자동 도심지 갱신에서도 항상 실행된다는 근거는 없다. 임의의 `on_building_downsized`를 작성해 연결됐다고 가정하지 않는다.

## 6. custom GUI 경로

[건물 상세 GUI](</D:/SteamLibrary/steamapps/common/Victoria 3/game/gui/building_details_panel.gui:1879>)는 `Building.GetBuildingOwnerships`를 순회한다. [기업 GUI](</D:/SteamLibrary/steamapps/common/Victoria 3/game/gui/company_panel.gui:1620>)는 `Building.GetBuildingAssets`와 `BuildingOwnership.GetLevel`을 사용한다. 생성된 GUI 데이터 문서에서도 다음을 확인했다.

```text
Company.GetBuilding / Company.GetRegionalHQs
Building.GetCompany / Building.GetBuildingOwnerships / Building.GetBuildingAssets
BuildingOwnership.GetOwnerBuilding / GetOwnerCountry / GetOwnedBuilding / GetLevel
```

따라서 주별 조계 건물을 찾아 소유 항목을 순회하고, 소유 본사/지역 본사의 Company를 통해 기업·국가·레벨을 표시하는 경로가 있다. `Building.GetCompany`는 모든 생산 건물에 회사 소유자가 단일값으로 있다는 뜻이 아니므로, 먼저 소유 항목의 owner building을 따라가야 한다. 한 회사의 여러 소유 항목을 합산하는 UI와 표시용 소유 유형 필터를 별도 검증한다.

`BuildingOwnership`의 GUI 함수가 존재하더라도 게임 효과용 스코프/순회자가 자동으로 생기는 것은 아니다. GUI 숫자를 비용·cap 판정의 신뢰 원본으로 보내지 않는다. 표시 구현과 서버 실행 검증을 분리한다.

## 7. 남은 실험과 구현 결정

우선 시험 가능한 항목은 다음과 같다. 아직 실행하지 않았다.

1. 빈 자산/슬롯 만원 국가에 전용 일반 회사 추가, 본사 위치 지정, 회사 소유 조계지 1레벨 생성. 하루·한 달 후 회사와 지분 확인.
2. 두 국가 회사의 같은 주 지분 1·2레벨 생성, 한 회사에 +1 추가. 원본 회사 유형·국가·지분·타국 레벨 보존 확인.
3. 두 일반 회사가 같은 국가에 있는 상황에서 전용 회사만 정확히 귀속되는지 확인.
4. 일반 무역소 5레벨과 조계지 1레벨을 동일 PM·고용 비율·시장 조건으로 비교. 실제 무역수입과 다른 무역소의 수입 배분도 확인.
5. 마지막 조계 해제 후 일반 공장 자산이 남은 회사의 해산. 국고 보상, 자산 이전, 대기 공사, callback 유효성, 즉시 재설립 여부 확인.
6. 정상 철회·구속 기간 중 파기·자동 종료의 callback 순서와 기간값을 기록. 같은 반환에 효과가 두 번 적용되지 않도록 확인.
7. 독립적인 두 해제 충격의 modifier 크기·중첩·만료를 확인.

기업 기본 자율 투자의 지역 강제·부분 철거·지분별 생산 정지는 먼저 지원 경로 또는 별도 설계 결정이 필요하다. cap 감소 시 자동 철거는 더 이상 요구하지 않는다. 테스트를 반복하는 것만으로 없는 인터페이스가 생기지는 않는다. 전용 회사/건물 생성과 표시만 성공한 상태를 전체 요구사항 구현 완료로 보지 않는다.


## 8. 저널 민간 큐 방식의 추가 확인과 검증 계약

- `documentation/effects.log:42586`: `start_privately_funded_building_construction = building_barracks`, 지원 scope는 state, 값은 building type. 지역은 호출 state로 지정 가능하지만 투자 국가·기업·재원 인자는 문서에 없다.
- `documentation/event_targets.log:1407`: 국가의 `num_queued_private_constructions` 수치 조회. 국가 전체 총계이므로 주/건물별 중복 확인을 대체하지 않는다.
- `documentation/triggers.log:15134`: building의 `is_under_construction`. 대기만 하는 항목을 포함하는지 시험해야 한다.
- `documentation/triggers.log:13591`: 국가 `investment_pool` 잔액 비교. 미래 전체 건설비나 특정 기업 독립 금고를 뜻하지 않는다.

프로토타입은 조계가 있는 중국 주에 이미 있는 산업의 +1 민간 건설을 등록하고 다음을 기록한다: 큐 소속국, 실제 투자풀, 진행 중/대기 중 판정, 완공 소유 국가·기업, 실제 증가 레벨, 저널 밖 기업 자동 투자. 중국 소유 주에서 실행했다고 외국 조계 기업에 자동 귀속된다고 가정하지 않는다. 서로 다른 두 조계 기업이 같은 주에 있는 경우에도 반복한다.

완공까지 시간과 민간 자금이 실제로 사용되는지, 같은 주에 매월 대기 공사를 중복 적재하지 않는지, 권리 반환 후 다른 민간 투자자의 공사를 건드리지 않고 신규 등록을 중단하는지 확인한다. 특정 큐 항목의 취소/귀속 지정 API를 찾지 못하면 그 부분을 미해결로 남긴다. 현재까지 이 프로토타입은 실행하지 않았다.


## 9. 게임 검증 생략 후 코드 구현 반영 — 2026-11-08

사용자가 게임 검증 없이 코드 구현을 요청했다. 아래는 정적 구현 상태이며 앞 절의 미실행 실험이 통과했다는 뜻이 아니다.

- 기존 조약 지급을 회사 소유 조계지 +1로 전환하고 첫 회사 생성·마지막 권리 소멸 시 해산·슬롯 보정을 연결했다. 첫 1레벨 설립과 쿨다운은 미검증이다.
- GUI와 AI가 같은 유료 확장 효과를 사용한다. cap은 실제 건물 레벨에서 계산하며 도심지 감소로 건물을 철거하지 않는다.
- 국가별 보유 레벨은 `levels_owned_by_country` 비교를 이용한 임시 32회 이진 탐색으로 산출한다. 회사별 조회가 아니므로 반환 잔여 자산·재획득 뒤에는 전용 회사 지분과 다를 수 있다.
- 강제 반환의 관계/위신은 레벨·도심지 대비 비율에 비례한다. 국가의 만료 변수 `concession_loss_prestige_snapshot`은 이미 삭제한 과거 손실을 기억하기 위해서만 필요하다. 730일 동안 가장 강한 충격을 유지하고 modifier가 없으면 정리한다.
- 공유 건물에 다른 권리가 남으면 자산을 보존한다. 마지막 주 권리가 사라질 때만 전체 건물을 제거한다. 부분 소유권 철거는 해결하지 못했다.
- 모든 보유국이 비활성일 때 전체 건물을 정지한다. 일부만 비활성이면 그 국가의 특권만 정지하며 생산·일반 배당은 개별 정지하지 못한다.
- 기존 월간 pulse에 18종 산업의 순이익/레벨 점수와 건설·대기 검사, state scope 민간 큐 등록을 연결했다. 지역은 저널이 선택하지만 재원과 완공 기업을 지정하지 못한다. 회사 전문 업종은 조계지만 등록했다.
- 실패한 회사/지분 생성은 권리를 등록하지 않고 안내한다. 조약 항목 자체의 자동 취소는 구현하지 않았다.
- 정적 검사기는 정의·참조·3개 언어·인코딩·PM 수치·자산 경로·큐 분기와 기존 경로 연결을 검사한다. 게임 실행·콘솔 실험·저장 변경은 이번 요청에서 생략한다.
