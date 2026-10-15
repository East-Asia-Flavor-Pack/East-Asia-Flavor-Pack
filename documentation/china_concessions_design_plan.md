# 중국 조계지 설계안

수정일: 2026-10-16. 사용자 지시에 따라 개항과 별도 이권 시스템을 제외하고 조계 자체의 효과에 집중한다. 1~8절은 설계 요약, 9절 이후는 코드 작성용 구현 명세다. 수치와 공식은 검증 전 게임 설계값이다. 이 문서 작성에서는 게임 스크립트를 변경하지 않는다.

## 1. 핵심 구조

관내18성의 각 게임 주에 여러 열강이 조계를 설치할 수 있다. 중국은 주 소유권을 유지하고 열강은 도시 일부에 조계권을 보유한다. 조계 자체가 경제 수입·위신·현지 영향력을 제공한다.

기본 흐름은 조계 획득 전쟁 목표 관철 또는 특약 정산 → 조계 설치·규모 설정 → 위신 조건에 따른 효과 적용 → 월간 갈등 이벤트 → 확대·전쟁·반환이다.

개항 여부, 통상 협정, 철도 연결 계약을 설치 조건으로 추가하지 않는다. 철도·광산·공장 사업권, 차관, 이권 입찰, 계약별 배당은 구현 대상에서 제외한다. 시정 정비는 조계 운영비를 들이는 관리 행동이며 별도 사업 계약이 아니다.

## 2. 역사 자료와 추상화

| 확인한 내용 | 반영할 점 |
| --- | --- |
| 1862년 영국 공사의 서신은 상하이 거류지와 영국 왕실에 대한 영토 이전을 구별한다. [FRUS 수록 서신](https://history.state.gov/historicaldocuments/frus1863p2/d257) | 중국의 주 소유권과 외국의 조계 행정권을 분리한다. |
| 1928년 상하이 공무국과 중국인 납세자 단체가 중국인 대표 선임에 합의했다. [Hansard](https://api.parliament.uk/historic-hansard/commons/1928/may/02/shanghai-municipal-council) | 중국인 대표 참여를 시정 개혁으로 둔다. |
| 1927년 한커우 반환 자료는 중국 시정기구의 과세와 잔존 영사재판권을 함께 다룬다. [FRUS 1927](https://history.state.gov/historicaldocuments/frus1927v02/d438) | 조계 시정권 반환이 모든 치외법권 폐지를 뜻하지는 않는다. |
| 1925년 상하이 사건 뒤 경찰 대응과 사망·부상 경위에 대한 국제 조사 논의가 있었다. [FRUS](https://history.state.gov/historicaldocuments/frus1925v01/d552) | 시위·경찰 대응·외교 위기를 사건으로 연결한다. |

외교문서는 해당 정부·외교관의 시각을 담는다. 그 안의 권리 주장을 정당성의 판정으로 사용하지 않는다. 지역별 조계의 제도 차이도 고려한다.

조계 시정 세입을 외국 정부 국고에 정기 송금하는 것은 그대로의 역사 재현이 아니다. 아래 수입 모델은 조계 보유의 경제적 이익을 국가 단위 게임으로 옮기는 추상화다. 시정 예산과 실제 민간기업 배당은 구별한다.

## 3. 대상 주와 조계 획득 경로

대상은 직례·산둥·산시(山西)·허난·섬서(陝西)·간쑤·장쑤·안후이·장시·저장·푸젠·후베이·후난·쓰촨·광둥·광시·윈난·구이저우의 중국 본토 부분이다. 역사적 성 18개를 게임 주 18개와 동일시하지 않는다. 만주·몽골·신장·티베트·대만은 제외한다.

설치된 게임의 `geographic_region_han_homelands`에는 만주의 `STATE_SHENGJING`과 대만의 `STATE_FORMOSA`도 포함되어 있다. 이 지역을 그대로 조건에 쓰지 않고 10절의 본토 26개 주 지역 목록과 대표 거점 프로빈스를 사용한다.

모든 대상 주를 같은 제도 아래 후보로 두고, 도시 규모와 경제성으로 효과와 AI 우선순위를 달리한다. 실제 조계가 없었던 지역의 설치는 대체역사다. 베이징 공사관 구역을 일반 상업 조계의 사례로 혼용하지 않는다.

- 신규 설치자는 원칙적으로 열강이며 해당 전략지역에 이해관계가 있어야 한다. 순위 하락만으로 기존 조계가 없어지지는 않는다.
- 중국 측 상대는 해당 주 소유 정부다. 청 태그에 한정하지 않아 군벌·혁명 정부에도 적용한다.
- 영토 소유국 자신에게 외국 조계권을 부여하지 않는다.
- 같은 국가의 같은 주 조계는 하나의 기록으로 합치고 추가 진출은 규모 확대로 표현한다.
- 같은 주에 여러 국가의 조계가 공존할 수 있으며, 각 조계는 해당 보유국이 개별 관리한다.

조계 획득은 전용 전쟁 목표 또는 특약 정산으로 처리한다. 전쟁 목표에서는 플레이어가 대상 주와 그 주 소유국을 지정하고 조계를 받을 국가를 명시한다. 외교전에서 해당 요구를 수락하고 물러서거나 평화 협정에서 목표가 관철될 때 지정된 국가에 조계를 설치한다. 영토 소유권은 이전하지 않는다. 일반적인 전쟁 승리만으로 조계를 지급하지 않으며, 별도 합의 버튼이나 지원 보상으로 직접 획득하는 경로는 두지 않는다.

특약 정산에서는 조계를 얻을 국가가 현재 주 소유국에 대해 가진 유효한 특약을 사용한다. 즉 주 소유국이 획득국에 특약을 빚진 방향이어야 한다. 획득국이 대상 주를 선택하고 설치 자격·현재 소유국·특약의 유효성과 방향·주 상한을 확인한 뒤, 조계 설치와 함께 해당 특약을 한 번 소비한다. 조건을 충족하지 못하면 조계를 설치하지 않고 특약도 소비하지 않는다. 획득 이후 작동 여부는 동일한 위신 조건으로 판정한다.

같은 국가가 같은 주에 이미 조계를 보유했다면 전쟁 목표와 특약 정산 모두 기존 조계의 확대로 처리하고 중복 기록을 만들지 않는다. 설치·확대 시 대상 주 소유국과 수혜국, 기존 조계 및 주 상한을 다시 확인한다. 목표가 관철되지 않은 백지 평화나 패배 자체는 조계권을 변경하지 않는다.

## 4. 조계 자체의 효과

조계는 현재 주 소유자의 위신이 조계 보유국의 위신보다 높으면 작동하지 않는다. 위신이 같거나 조계 보유국 쪽이 높으면 작동한다. 같은 주에 여러 국가의 조계가 있으면 보유국별로 따로 판정한다.

작동 중단 시 해당 조계의 수입·유지비·위신 보너스·도시 효과·주권 침해 효과·현지 관할 효과와 중국 측 재정 차감을 모두 해제하고 월간 갈등 이벤트 대상에서도 제외한다. 조계 기록과 규모는 유지하며, 위신 조건이 다시 충족되면 효과를 재개한다. 이는 반환이 아니므로 조계 반환 전쟁 목표의 대상에는 계속 포함된다. UI에는 현재 작동 여부와 양국의 위신을 표시한다.

아래 효과는 작동 중인 조계에만 적용한다.

| 효과 | 중국 측 해당 주 | 보유 열강 |
| --- | --- | --- |
| 상업·거류 활동 | 제한적인 도심 서비스 활동·이주 매력 증가 | 도시 규모에 비례한 조계 수입 |
| 외국 시정·과세 | 해당 도시 부분에 대한 중국 재정 수취 감소 | 유지비 차감 후 순수입 |
| 외국 행정권 | 주권 침해 부담 | 소규모 위신, 해당 주 분쟁의 당사자 지위 |
| 시정 정비 | 운영비 지출에 따른 도시 환경 개선 | 추가 운영비 부담 |
| 경찰·재판 관할 충돌 | 월간 이벤트에 따른 시위·관헌 충돌 | 영사 분쟁과 일시적 수익 감소 가능성 |

경제 효과는 도시 활동에 비례시킨다. 주 전체 농업·광업·제조업의 이익을 일괄 이전하지 않는다. 주 단위 modifier로 표현할 때에도 조계가 도시 일부라는 점을 반영해 작은 효과와 합산 상한을 사용한다.

상업 성장 효과는 시정 정비 수준과 이벤트의 기간제 효과에 따라 달라진다. 외국 통치 자체가 자동으로 치안을 개선하거나 급진파를 줄이지 않는다. 전국 기술 확산·공장 처리량·건설 속도를 조계 수만큼 중첩시키지 않는다.

시정 정비 비용은 외국에 실제 부담시키고 지출 중단 시 추가 효과도 끝낸다. 여러 조계의 효과는 합산 후 주 상한을 적용한다.

현지 영향력은 해당 주 사건에 참여할 자격이다. 국가 전체의 군사 통행권·자동 전쟁 개입·시장 편입을 부여하지 않는다.

## 5. 규모와 수입

조계 규모는 단계별 등급으로 구분하지 않는다. 작동 중인 조계의 규모가 커지면 수입·유지비·주권 침해가 함께 커진다. 확대는 기존 조계가 있는 주에 대한 조계 획득 전쟁 목표의 관철 또는 특약 정산으로 처리한다.

주 전체에 도시 규모에 따른 총 조계 규모 상한을 둔다. 작동이 중단된 조계도 권리가 남아 있으므로 설치·확대 상한에는 포함한다. 도시가 쇠퇴하면 기존 권리를 즉시 삭제하지 않고 추가 확대를 막고 수익 기반을 낮춘다.

설계식:

`주 총 조계 수입 = 기준 도시 세원 × 작동 중인 조계의 총 영향 비중`

`조계별 기본 배정 수입 = 주 총 조계 수입 × 해당 조계 규모 / 작동 중인 전체 조계 규모`

`보유국 순수입 = 이벤트의 기간제 효과를 반영한 배정 수입 - 시정·경비 유지비`

작동이 중단된 조계의 배정 수입과 유지비는 0이다. 작동 중인 조계가 하나도 없으면 주 총 조계 수입과 중국 측 재정 차감을 0으로 처리하고 배분 계산을 건너뛴다. 이벤트로 배정 수입이 바뀌면 중국 측 재정 차감도 같은 액수만큼 조정한다.

기준 도시 세원은 조계 효과 적용 전 도시 활동으로 추정한다. 실제 도시 세수 조회 가능 여부를 확인하고, 불가능하면 도시 건물 규모 등 사용 가능한 지표로 추정한다. UI에 추정치임을 표시하며 가용 재정 수취를 과도하게 넘지 않도록 상한을 검증한다.

중국 재정 차감 총액과 외국의 유지비 차감 전 배정 수입 총액은 일치시킨다. 재정 차감을 modifier와 별도 지급으로 두 번 적용하지 않는다. 기본 게임의 실제 기업 소유권·민간 배당은 건드리지 않으며 그 배당을 조계 수입에 재합산하지 않는다.

조계 보유국 수가 늘었다는 이유만으로 수입을 생성하지 않는다. 작동 중인 총 규모가 같으면 수입 기반도 같고 배분만 달라진다. 작은 도시의 조계는 유지비 때문에 적자가 가능하다. 국가 위신에는 상한이나 체감 효용을 둔다.

## 6. 월간 갈등 이벤트와 조계 반환 전쟁 목표

주권 침해는 작동 중인 조계의 총 규모와 행정 권한에 따른 효과로 표현한다. 별도의 긴장도 변수나 누적·감소·임계치 판정은 두지 않는다.

갈등은 월간 이벤트로 처리한다. 매월 작동 중인 조계가 있는 주별로 한 번 이벤트 후보를 평가하고, 사건별 기본 발생 확률과 실제 상황 조건에 따라 해당 조계와 당사국을 선택한다. 같은 주를 보유국마다 중복 추첨하지 않는다. 이벤트는 일회성 비용·관계 변화·급진파 변화·기간제 modifier 외에 자동 전쟁 개시나 조계 강제 반환도 결과로 직접 적용할 수 있다.

사건 후보는 범죄 용의자의 조계 도피, 외국 경찰과 중국 관헌의 충돌, 구역 확대 요구, 중국인 납세자의 대표권 요구, 시위와 발포 위기, 내전 피난민 유입이다. 공동 조사·보상·대표 참여·입경 제한·강경 대응 등을 선택하게 한다.

중국인 대표 참여는 월간 이벤트의 선택지로 두고 관계 개선이나 기간제 효과를 직접 부여한다. 중국 정부가 즉시 조계 행정을 지배하는 것과 동일시하지 않는다. 구역 확대는 조계 획득 전쟁 목표 또는 특약 정산으로 처리하며, 반환은 이벤트 결과로도 즉시 강제할 수 있다.

강경한 경찰 대응은 상시 치안 보너스 대신 사건 선택지로 둔다. 즉각적 질서 회복 가능성과 더 큰 반발·외교 위기를 함께 제시한다.

조계 반환은 전용 전쟁 목표 또는 월간 이벤트의 강제 반환 결과로 처리한다. 전쟁 목표에서는 주 소유국이 해당 조계 보유국을 상대로 대상 주와 반환할 조계의 보유국을 명시한다. 외교전에서 해당 요구를 수락하고 물러서거나 평화 협정에서 목표가 관철될 때 해당 조계 기록과 권리를 제거한다. 이벤트의 강제 반환은 전쟁 목표 관철 없이 지정된 조계의 기록과 권리를 즉시 제거한다. 특약 정산·보상 합의·별도 반환 협상으로 반환하는 경로는 두지 않는다. 목표가 관철되지 않은 백지 평화나 패배 자체는 조계권을 변경하지 않는다. 일정 기간 후 모든 조계가 자동 만료한다고 설정하지 않는다.

반환 시 외국 수입·유지비·위신·관할 권한과 중국의 조계 재정 차감이 끝난다. 시정 정비로 형성된 기반 효과는 일정 기간 전환 modifier로 남겨 이후 중국의 일반 행정으로 흡수한다. 건물·인구·민간 자산을 반환만으로 삭제하거나 몰수하지 않는다. 다른 국가의 조계는 영향을 받지 않는다.

전쟁 목표를 통한 획득·반환의 외교 비용은 해당 목표의 규칙으로, 특약을 통한 획득 비용은 특약 소비로 처리한다. 월간 이벤트의 전쟁 개시·강제 반환은 사건별 조건과 결과로 정의하며, 자동 결과나 선택지 결과 모두 허용한다. 전쟁 개시에는 당사국과 전쟁 목표를 명시하고 동일 당사국 사이에 같은 전쟁을 중복 생성하지 않는다. 강제 반환에는 대상 주와 조계 보유국을 명시하고 다른 조계에는 영향을 주지 않는다.

## 7. 구현 방향

기존 `concession_owner_varlist`, 중국·외국 양측 저널, 주별 보유국 국기 UI의 개념을 재사용한다. 기반 파일은 다음과 같다.

- `common/journal_entries/eafp_concessions_in_china.disable`
- `common/journal_entries/eafp_concession_calc.disable`
- `events/eafp_chi_events/eafp_concessions_in_china_events.disable`
- `common/scripted_buttons/eafp_concessions_in_china_buttons.disable`
- `common/on_actions/concessions_code_on_actions.disable`
- `gui/eafp_concessions_in_china_gui.disable`

보유국 수에 따라 주 내 여러 산업의 이익을 차감하는 옛 계산은 도시 세원·총 규모·유지비 중심으로 교체한다. 주석 처리된 modifier와 구판 경제 상수는 현행 호환성 확인 후 필요한 것만 복구한다.

저장 단위는 주 지역별 대표 거점과 그 안의 조계다. 각 조계에 보유국·규모·현재 중국 측 소유국을 기록한다. 사업 계약 목록은 만들지 않는다.

조계 획득·반환 전쟁 목표에 대상 주와 조계 보유국 또는 수혜국을 연결한다. 목표 관철 시 설치·확대·반환 효과를 실행하고 외교전 양보와 평화 협정 양쪽에서 동일하게 처리되는지 확인한다. 주 선택, 국가 스코프 전달, 위신 비교, 세원 조회, 서비스 modifier, 비용 정산은 구현 전 검증 대상이다.

특약 정산은 현재 주 소유국이 획득국에 빚진 특약의 조회·소비와 조계 설치·확대를 연결한다. 전쟁 목표와 같은 설치·확대 효과를 재사용하며, 성공한 정산에서만 특약을 한 번 소비한다. 월간 이벤트의 강제 반환도 전쟁 목표와 같은 반환 효과를 재사용해 기록·효과·정산을 함께 정리한다. 자동 전쟁용 API는 로컬 문서에서 확인했으며, 실제 호출 방향과 목표 전달은 16.3절의 실행 시험으로 검증한다.

월별 처리에서는 작동 중단된 조계를 포함한 모든 기존 조계의 현재 주 소유국과 양국 위신을 먼저 확인한다. 판정에 따라 효과를 해제하거나 재개한 뒤, 작동 중인 조계만 정산하고 월간 이벤트 후보로 삼는다. 같은 주를 국가마다 중복 계산하지 않으며 특정 AI 국가의 생존에 계산을 의존시키지 않는다. 내전 분할 시 실제 거점 소재 정부를 의무자로 삼고 판정 불가 시 효과·지급·이벤트를 보류한다. 점령과 정식 영토 이전을 구별하며 소유국 변경 시 위신 조건을 다시 확인하고 통일 시 중복을 제거한다.

AI는 순수입·전략적 가치·유지비·관계·양국 위신·전쟁 수행 능력으로 조계 획득·확대·반환 전쟁 목표를 평가한다. 특약을 통한 획득·확대는 특약의 보유 여부와 다른 사용처의 가치도 함께 평가한다. 유지 예산과 행동 대기 기간으로 무한 설치를 막는다. 내륙 주를 금지하는 대신 도시 수익에 따라 우선순위를 정한다.

구현 순서: 획득·반환 전쟁 목표와 특약 정산·대상 선택 → 위신에 따른 작동 판정 → 규모·도시 효과·수입·유지비 → 전쟁 개시·강제 반환을 포함한 월간 갈등 이벤트·대표 참여.

검증 항목: 획득·반환 목표의 외교전 양보 및 평화 협정 적용, 미관철 목표의 효과 미적용, 정확한 주·보유국 지정과 중복 획득 방지, 위신의 초과·동률·역전 시 작동 중단과 재개, 같은 주의 보유국별 독립 판정, 중단된 조계의 모든 효과·정산·이벤트 제외 및 반환 가능 여부, 조계 위신 보너스 해제·재적용에 따른 경계값 판정, 작동 중인 조계가 없을 때 0 처리, 중국 차감과 외국 총수입 일치, 주 효과 상한, 보유국 증가 시 수입 복제 방지, 월간 이벤트 중복 방지, 반환 시 효과 해제, 내전·통일·국가 소멸 승계, 세이브 재로드, AI의 적자 조계 유지 판단.

추가 검증 항목: 특약의 방향·유효성 확인, 성공 시 한 번 소비 및 실패 시 보존, 특약 획득에도 위신 조건 적용, 이벤트의 자동 전쟁 개시와 정확한 당사국·목표 지정, 전쟁 중복 생성 방지, 이벤트 강제 반환 시 지정 조계만 제거하고 효과·정산 해제.

## 8. 플레이 예시

영국이 한커우를 대표하는 주를 대상으로 조계 획득 전쟁 목표를 관철하면 영국 조계가 설치된다. 주 소유국의 위신이 영국보다 높지 않으면 중국에는 제한적인 도시 활동 효과와 재정 손실이 생기고, 영국은 조계 수입에서 유지비를 뺀 순수입과 소규모 위신을 얻는다.

프랑스는 주 소유국이 프랑스에 빚진 특약을 소비해 같은 주에 조계를 얻을 수 있다. 각 조계의 위신 조건을 따로 판정해 작동 중인 조계만 수입과 유지비를 정산한다. 갈등은 월간 이벤트로 발생하며, 중국인 대표 참여나 공동 조사 등의 선택에 따라 관계와 기간제 효과가 달라진다. 경찰 충돌 사건의 결과로 양국 간 전쟁이 자동으로 시작되거나, 특정 조계가 즉시 강제 반환될 수도 있다.

주 소유국의 위신이 영국보다 높아지면 영국 조계는 기록만 남고 효과·정산·월간 이벤트가 중단된다. 프랑스 조계의 작동 여부는 프랑스와의 위신 비교로 별도 결정한다. 이후 주 소유국이 영국에 대한 조계 반환 전쟁 목표를 관철하면 영국 조계권이 제거된다. 기존 도시와 주민은 그대로 남는다.

## 9. 구현 기준과 확인한 코드

### 9.1. 기준 환경과 명세 읽는 법

- 모드 루트: 이 저장소. 게임 루트: `D:/SteamLibrary/steamapps/common/Victoria 3/game`.
- 설치된 런처 설정의 `rawVersion`: `1.13.11`. 버전 확인 파일은 게임 폴더의 `../launcher/launcher-settings.json`이다.
- 아래의 **확인**은 로컬 파일·생성 문서에 문법 또는 사용례가 있다는 뜻이다. 이번 작업에서 게임을 실행해 검증했다는 뜻은 아니다.
- **구현안**은 이번 설계를 코드로 옮기기 위한 선택이다. **검증 필요**는 실행 전에 작은 시험 모드/디버그 세이브로 확인해야 하는 항목이다.
- `text` 코드 블록은 의사코드다. `paradox` 블록도 주석에 명시된 새 helper 정의가 있어야 실행되며, 그대로 붙여넣는 완성 코드로 취급하지 않는다.
- 소규모·중규모·대규모 등급, 운영 방침, 공공조계, 긴장도 변수는 만들지 않는다. 규모는 숫자로 저장하고 획득·확대로만 변경한다.
- 기존 `.disable` 파일은 설계 참고 자료다. 향후 구현 시 필요한 파일만 재작성·활성화하고, 비활성 파일 전체의 확장자를 일괄 변경하지 않는다.

### 9.2. 근거와 사용 범위

아래에서 `game/`는 위 게임 루트, 나머지는 저장소 루트 기준이다.

| 근거 파일 | 확인한 내용 | 적용 |
| `game/common/war_goal_types/war_goal_types.md` | `kind = custom`, `on_enforced`, `target_type`, 목표별 스코프 | 획득·반환 모두 직접 정의한 전쟁 목표 사용 |
| `game/common/war_goal_types/29_restore_union.txt` | 실제 `kind = custom`과 `on_enforced` 구현 | 기존 정복·굴욕 효과를 편법으로 빌리지 않음 |
| `game/common/war_goal_types/03_conquer_state.txt` | `target_type = state`, `scope:target_state`, `scope:target_country` | 획득 목표의 주 선택·검증 패턴 |
| `common/diplomatic_plays/diplomatic_plays.md` 및 `eafp_diplomatic_plays.txt` | 전쟁 목표를 지정하는 외교전 정의 | 조계 획득·반환 전용 외교전 연결 |
| `documentation/effects.log`의 `create_diplomatic_play`, `set_war` | 생성 시 `war` 항목, 외교전 스코프의 `set_war` | 월간 사건의 자동 전쟁 경로. 실제 호출 스코프는 시험 필요 |
| `events/eafp_chi_events/eafp_first_opium_war_events.txt:306` | `create_diplomatic_play`와 `add_war_goal`, `target_state` 사용 | 전쟁 목표 데이터 전달 참고 |
| `events/russo_chinese_events.txt:72` | 특약 채무국에서 `set_owes_obligation_to = { country = … setting = no }` | 특약 소비 방향과 문법 |
| `common/scripted_triggers/eafp_chinese_interregnum_triggers.txt:17` | 국가의 `.prestige` 직접 비교 | 국가 순위 대신 실제 위신 비교 |
| `documentation/event_targets.log`의 `p`, `state`, `owner` | 프로빈스 → 현재 state → 소유국 이동 | 분할 주에서도 거점의 실제 소유국을 찾음 |
| `common/on_actions/00_code_on_actions_definition.txt` | 글로벌 `on_monthly_pulse`와 기존 호출 목록 | 기존 월간 진입점에 조계 처리 하나만 연결 |
| `documentation/effects.log`의 `add_treasury` | 국가 국고 가감 | 월간 현금 정산. 별도 세금 modifier로 중복 차감하지 않음 |

생성 문서에는 `set_owes_obligation_to` 항목의 예제가 `set_owes_obligation`로 적힌 오기와 `change_relations`의 `tcountry` 표기가 있다. 이 경우 실제 게임/모드 사용례와 파서 검증을 우선한다. `create_diplomatic_play`도 생성 문서와 저장소의 호출 방향 설명이 다르므로 추측만으로 연결하지 않는다.

### 9.3. 기존 구현에서 교체할 부분

| 기존 위치 | 문제 또는 변경 필요점 | 새 처리 |
| `eafp_concession_calc.disable` | 임의 AI 국가를 계산 담당자로 지정 | 글로벌 월간 처리로 대체. `concession_calc_holder` 제거 |
| `concessions_in_china.1` | 보유국 수를 기준으로 여러 산업 이익 계산 | 거점 도심 규모와 조계별 권리 비중으로 계산 |
| `establish_concession_button` | 상대국을 무작위 선택하고 `ROOT`에 반대 방향 특약을 설정 | 국가·주를 사용자가 선택한 뒤 채무국의 기존 특약만 소비 |
| `return_concession_button` | 특약으로 반환하는 옛 경로 | 활성화하지 않음. 반환은 전쟁 목표 또는 월간 사건 |
| 옛 양보·항복 on-action | 일반 전쟁 결과로 조계를 자동 획득·반환 | 연결하지 않음. 해당 목표의 `on_enforced`만 사용 |
| 옛 혁명·분리독립 처리 | 분할된 state에 보유국 목록 복사 | 주 지역의 단일 거점 기록을 유지하고 소유국만 재조회 |
| 옛 `concession_state_modifier`, `concession_building_modifier` | 주석 처리된 구판 경제 효과·기업 지분 변경 | 새 상한과 비용 기준으로 교체. 기업 소유권 수정 금지 |
| 옛 GUI | state 목록과 보유국 국기 표시만 존재 | 주 지역/거점 행에 작동 조건·정산·행동을 추가 |

기존 `je_concessions_in_china`, `je_concessions_in_china2`, `concessions_in_china` 네임스페이스와 국기 목록 UI는 재사용한다. 기능의 새 버전을 별도 이벤트 체계로 병렬 운영하지 않는다.

## 10. 대상 주와 거점 매핑

### 10.1. 단일 목록

아래 26개는 기본 게임 `common/geographic_regions/04_geographic_regions_asia.txt`의 한족 본토 목록에서 `STATE_SHENGJING`, `STATE_FORMOSA`를 제외한 구현 대상이다. `STATE_NINGXIA`는 이 설계에서 역사적 간쑤 권역에 포함한다. 대표 프로빈스는 `map_data/state_regions/11_east_asia.txt`의 각 주 `city` 값이다. 실제 역사적 조계 위치와 일치한다는 뜻은 아니며, 주 단위 추상화와 소유국 판정에 쓰는 거점이다.

| 주 지역 ID | 생성용 식별자 | 대표 프로빈스 |
| --- | --- | --- |
| `STATE_BEIJING` | `beijing` | `x9BB46B` |
| `STATE_ZHILI` | `zhili` | `xF54194` |
| `STATE_SHANDONG` | `shandong` | `x9D1474` |
| `STATE_SHANXI` | `shanxi` | `xF87F8F` |
| `STATE_HENAN` | `henan` | `x5C5657` |
| `STATE_XIAN` | `xian` | `xA64E0F` |
| `STATE_GANSU` | `gansu` | `xA4641B` |
| `STATE_NINGXIA` | `ningxia` | `x769B1C` |
| `STATE_SUZHOU` | `suzhou` | `xB01101` |
| `STATE_NANJING` | `nanjing` | `x8111D0` |
| `STATE_JIANGSU` | `jiangsu` | `x11D080` |
| `STATE_SOUTHERN_ANHUI` | `southern_anhui` | `x36029B` |
| `STATE_NORTHERN_ANHUI` | `northern_anhui` | `x901159` |
| `STATE_JIANGXI` | `jiangxi` | `x1186AE` |
| `STATE_ZHEJIANG` | `zhejiang` | `x241F94` |
| `STATE_FUJIAN` | `fujian` | `xC4F2DB` |
| `STATE_WESTERN_HUBEI` | `western_hubei` | `x696991` |
| `STATE_EASTERN_HUBEI` | `eastern_hubei` | `xA6A054` |
| `STATE_HUNAN` | `hunan` | `x425FDF` |
| `STATE_SICHUAN` | `sichuan` | `x60E0D5` |
| `STATE_CHONGQING` | `chongqing` | `x6CAE25` |
| `STATE_SHAOZHOU` | `shaozhou` | `xA0C90D` |
| `STATE_GUANGDONG` | `guangdong` | `x2BDE7B` |
| `STATE_GUANGXI` | `guangxi` | `x37E3AC` |
| `STATE_YUNNAN` | `yunnan` | `x78DC66` |
| `STATE_GUIZHOU` | `guizhou` | `x096C00` |

이 표를 향후 `tools/data/china_concessions_regions.json`의 원본 데이터로 옮기고, 지역 분기·지역별 반환 목표·현지화의 반복 부분을 생성한다. 지도 변경 모드와 병용할 때는 매핑을 다시 검증한다. 지도 파일 자체를 덮어쓰지는 않는다.

### 10.2. 스코프 의미

- `concession_region`: `state_region`. 권리의 영속적인 공간 식별자.
- `concession_anchor`: 표에 지정한 province. 임의 도시나 인구가 가장 큰 state로 이동시키지 않는다.
- `concession_state`: 거점 province가 현재 속한 state.
- `concession_host`: 현재 `concession_state.owner`. 청 태그에 고정하지 않는다.
- `concession_holder`: 해당 조계의 외국 보유국. 한 지역에서 여러 국가가 각각 한 기록을 가진다.
- `concession_actor`: 버튼/전쟁 목표를 실행하는 국가. 반환 목표에서는 host, 획득 목표에서는 수혜국이 기본이다.

예를 들어 동부 후베이는 `p:xA6A054.state`와 그 소유국으로 판정한다. 점령군이 아니라 법적 `owner`를 사용한다. 거점이 조약항으로 분리되면 그 조약항 state를 중국 본토 조계의 의무자로 쓰지 않고 해당 지역 기록의 효과를 보류한다. 거점 없는 다른 본토 state에 부담을 임의 전가하지 않는다.

## 11. 저장 구조와 상태 수명

### 11.1. 실제 저장 모델

Jomini에 임의의 객체 사전이나 `(주, 국가)` 레코드가 있다고 가정하지 않는다. 주 지역의 국가 목록과 보유국의 지역별 정적 변수 키를 결합한다. `<region>`은 표의 생성용 식별자를 빌드 시 치환하는 자리표시자이며 런타임 문자열 조합이 아니다.

| 저장 위치 | 키 | 내용·필요 이유 | 초기화·제거 |
| --- | --- | --- | --- |
| 주 지역 | `concession_owner_varlist` | 해당 지역의 조계 보유국 목록. 기존 목록 이름 재사용 | 최초 획득 시 추가, 반환 시 그 국가만 제거 |
| 보유국 | `eafp_concession_extent_<region>` | 조계 권리 비중, 정수 basis point. 과거 획득·확대 결과이므로 저장 필요 | 첫 획득 500, 확대 시 가산, 반환 시 제거 |
| 보유국 | `eafp_concession_revision_<region>` | 획득·확대·반환 때 증가하는 번호. 오래 열린 이벤트가 재설치된 조계를 반환시키지 않게 함 | 최초 1, 변동 때 +1. 반환 뒤에도 번호 보존 |
| 보유국 | `eafp_concession_disruption_<region>` | 사건으로 생긴 일시적 수입 감소 기록 | 180일 만료값. 반환 시 제거 |
| 보유국 | `eafp_concession_representation_<region>` | 대표 참여를 허용한 사건의 일시적 결과 | 365일 만료값. 반환 시 제거 |
| 보유국 | `eafp_concession_works_<region>` | 비용을 내고 시정 정비한 기간제 효과 | 365일 만료값. 반환 시 전환 효과 처리 후 제거 |
| 보유국 | `eafp_concession_active_<region>` | 마지막 판정 시 작동 결과. 위신 효과를 갱신해도 같은 처리 중 재판정하지 않기 위한 스냅샷 | 재판정마다 덮어쓰기, 반환 시 제거 |
| 주 지역 | `eafp_concession_previous_host` | 소유국 변경 시 과거 국가에 붙은 합산 효과를 제거할 대상 | 처리 후 현재 host 저장, 조계가 없으면 정리 |
| 전역 | `eafp_concessions_schema_version` | 구 세이브의 일회성 이관 구분 | 새 구조 초기화 후 1. 월마다 증가시키지 않음 |

주 지역에서 변수·목록이 실제로 저장·재로드되는지는 첫 스모크 테스트에서 확인한다. 지원되지 않는 경우에만 기존 파일 주석의 `STATE_*_concession_owner_varlist` 전역 목록 방식으로 바꾸고, 두 저장 방식을 함께 유지하지 않는다. 국가 태그별 하드코딩 대신 국가 스코프를 목록 원소로 저장해 동적 국가도 처리한다.

도시 규모, 현재 host, 현재 위신, 국가 수, 주권 침해량은 직접 계산한다. 긴장·운영 방침·대표권 지분·의장국 변수는 없다. 화면용 `concession_candidate_states_gvarlist`는 재생성 가능한 표시 목록이며 권리의 원본이 아니다.

`ACTIVE`, `SUSPENDED_PRESTIGE`, `UNRESOLVED`, `ABSENT`는 아래 명세의 상태 이름이다. 별도 enum 변수로 중복 저장하지 않는다. 목록·extent·active와 현 스코프로 도출한다.

### 11.2. 상태 판정

| 조건 | 결과 | 권리·규모 | 정산·상시 효과·신규 사건 |
| --- | --- | --- | --- |
| 목록과 유효한 extent가 없음 | `ABSENT` | 없음 | 없음 |
| 거점·host를 찾지 못함, 거점이 조약항임 | `UNRESOLVED` | 보존 | 모두 보류 |
| host 위신 > holder 위신 | `SUSPENDED_PRESTIGE` | 보존 | 모두 0/해제 |
| host 위신 <= holder 위신 | `ACTIVE` | 보존 | 적용 |
| holder와 host가 같은 국가가 됨 | 권리 소멸 | 해당 기록 제거 | 일반 국내 지역으로 처리 |
| holder 소멸, 후계 승계 정보 없음 | 권리 소멸 | 해당 기록 제거 | 다른 외국에 무작위 승계하지 않음 |

기간제 사건 기록은 중단 중에도 남은 기간이 흐른다. 중단 중 modifier는 적용하지 않으며 재개 시 아직 유효한 기록만 반영한다. 사건의 이미 발생한 일회성 배상금·관계 변화·급진파 변화까지 되돌리지는 않는다.

### 11.3. 위신 판정 시점

정확히 `host.prestige > holder.prestige`일 때만 중단한다. 국가 순위나 기본 위신으로 대체하지 않는다. 비교에는 기존 조계 보너스를 포함한 판정 시작 시점의 표시 위신을 사용한다.

월간 처리 시작 때 관련 국가들의 위신을 먼저 임시 스냅샷으로 읽고, 모든 조계의 작동 여부를 산출한 다음 위신 modifier를 일괄 갱신한다. 조계 하나의 modifier를 바꾼 뒤 다음 조계의 위신을 읽으면 순회 순서가 결과를 바꾸므로 금지한다. 같은 처리 안에서 고정점을 찾으려고 반복 재계산하지 않는다.

획득·반환·소유국 변경 처리도 동일하게 전체 관련 조계의 판정과 modifier 갱신을 한 묶음으로 수행한다. 외부 위신 변화는 다음 월간 처리까지 반영되며, UI에 마지막 판정 기준임을 표시한다. 월 사이 즉시 반영이 필요해질 경우에만 검증된 위신 변경 hook을 추가한다. 판정 후 보너스 변화로 다음 달 경계값이 다시 바뀌는 경우는 실제 위신 규칙대로 처리하고 숨은 보정치나 유예 임계값은 추가하지 않는다.

## 12. 규모·효과·월간 정산

### 12.1. 첫 구현의 수치

아래 수치는 밸런스 초안이며 `common/script_values/eafp_concessions_values.txt`에서 한 번만 정의한다. 권리 비중은 면적 측량값이 아니라 도시 세원에 대한 조계 효과 비중이다. 500 단위 획득은 등급 구분이 아니며 소·중·대 표시나 단계별 효과표를 만들지 않는다.

| 기호/값 | 초기값 | 용도 |
| --- | --- | --- |
| `grant_bp` | 500 | 한 번 획득·확대로 증가하는 권리 비중, 5%p |
| `max_region_bp` | 2500 | 주 지역 권리 상한, 25% |
| `capacity_per_urban_level_bp` | 500 | 도심 레벨당 권리 수용량 |
| `base_monthly_per_urban_level` | £1,000 | 추정 월 도시 세원 |
| `fixed_monthly_cost` | £100 | 작동 중인 조계 한 곳의 기본 관리비 |
| `variable_cost_ratio` | 0.20 | 기본 배정 수입에 비례한 관리비 |
| `disruption_factor` | 0.50 | 갈등 사건의 180일 배정 수입 계수 |
| `representation_factor` | 0.90 | 대표 참여 365일 동안의 배정 수입 계수 |
| `works_extra_cost` | £100/월 | 시정 정비 365일 동안 추가 비용 |
| `prestige_per_grant` / `prestige_country_cap` | 1 / 10 | 작동 중인 권리 비중에 비례한 국가 위신, 합산 상한 |

`U`는 거점 state의 `building_urban_center` 레벨 합계다. 기존 코드의 `weekly_profit`이나 전체 주 GDP를 도시 세수라고 부르지 않는다. 도심 건물이 없으면 `U = 0`으로 처리한다. 도심 레벨 조회 문법은 `documentation/event_targets.log`의 `level`과 실제 건물 순회로 검증한다.

### 12.2. 산식

```text
capacity_bp = min(2500, 500 * U)
legal_total_bp = sum(extent of all valid holders, including suspended holders)
new acquisition allowed only if legal_total_bp + 500 <= capacity_bp

shrink_factor = 0 if legal_total_bp == 0
                else min(1, capacity_bp / legal_total_bp)
effective_bp[i] = extent[i] * shrink_factor
urban_base_monthly = 1000 * U

if active[i]:
    base_gross[i] = urban_base_monthly * effective_bp[i] / 10000
    event_factor[i] = (0.5 if disruption else 1) * (0.9 if representation else 1)
    gross[i] = floor(base_gross[i] * event_factor[i])
    cost[i] = floor(100 + 0.2 * base_gross[i] + (100 if works else 0))
    net[i] = gross[i] - cost[i]
else:
    gross[i] = cost[i] = net[i] = 0

host_debit = sum(gross[i])
holder_credit[i] = net[i]
```

도시 쇠퇴는 `shrink_factor`로 수입과 효과를 줄일 뿐 저장된 권리를 지우지 않는다. 중단된 국가의 권리 몫을 다른 국가에 재분배하지 않는다. 지급은 소수점 이하를 버린 동일한 `gross[i]`를 차감과 수취 계산에 사용한다. 유지비는 host의 수취가 아니라 운영 지출이다. 현금 흐름은 `host_debit = sum(holder_credit) + sum(cost)`를 만족한다.

예: `U=10`, 영국·프랑스가 각각 500bp이면 각 기본 수입은 £500, 유지비 £200, 순수입 £300이며 host 차감은 £1,000이다. 영국만 중단되면 영국은 모두 0, 프랑스는 그대로 £300, host 차감은 £500이다. 프랑스에 수입 50% 감소 사건이 생기면 수입 £250, 비용 £200, 순수입 £50, host 차감 £250이다. 작은 도시에서는 순수입이 음수일 수 있다.

실제 세수 상한을 조회할 수 있으면 전체 배정액이 해당 도시의 가용 수취를 넘지 않도록 같은 비율로 축소한다. 조회가 불가능한 첫 버전은 위 도심 레벨 기반 추정치와 25% 상한을 사용하고 UI에 **추정 도시 세원**이라고 쓴다. 실제 세수와 일치한다고 설명하지 않는다.

### 12.3. 효과 적용과 정산 방식

돈은 글로벌 월간 처리에서 `add_treasury`로 한 번만 이동한다. 금액 단위는 월 £로 통일하며 주간 modifier와 동시에 쓰지 않는다. `concession_payment`/`concession_paid`의 옛 재정 modifier는 활성화하지 않는다. 국고가 부족해도 지급을 임의로 중단하지 않고 기본 게임의 국고·부채 처리를 따른다.

상시 효과의 첫 구현안은 다음과 같다. 숫자는 합산된 작동 비중 `A = sum(effective_bp of active holders)/10000`에 곱한다.

| 대상 | 효과 | 초기 산식/제한 |
| --- | --- | --- |
| 보유국 | 위신 | 국가별 `min(10, sum(effective_bp/500))` |
| 거점 state | 이주 매력 | `state_migration_pull_mult = 0.2 * A` |
| 거점의 도심 건물만 | 서비스 생산 | `goods_output_services_mult = 0.1 * A`; 정비한 조계 비중에는 같은 비율 추가 |
| host | 주권 침해 표시 | 작동 비중 `A`를 저널에 표시. 별도 누적 점수나 긴장도 저장 안 함 |
| 반환 후 거점 state | 정비 전환 효과 | 정비 기록이 유효한 조계가 반환될 때 그 기여분의 이주 매력 효과를 180일만 유지 |

modifier의 적용 스코프와 `multiplier` 계산을 게임에서 확인한다. 도심 서비스 효과는 `building_urban_center`에만 적용하며 모든 서비스 업종에 일괄 보너스를 주지 않는다. 정비는 월간 사건에서 비용을 내고 얻는 기간제 결과이며 운영 방침 선택을 되살리지 않는다.

각 월 처리 전에는 이전 합산 modifier를 제거하고 새 합계로 하나씩 다시 적용한다. 같은 이름을 조계별로 여러 번 더해 마지막 국가만 남거나 중첩하지 않게 한다. 국가가 여러 지역의 조계를 보유하므로 위신은 국가 전체 합산 후 한 번 적용한다. 주 소유국도 다른 지역 조계 보유국일 수 있으므로 수입·지출을 모두 누적한 뒤 국가별 순액으로 처리한다.

월간 지급은 처리 시점에 작동 중인 조계의 해당 회차 지급이다. 월 중 획득·반환·중단 때 소급 지급이나 환수는 하지 않는다. UI 재계산, 이벤트 후 갱신, 세이브 로드에는 현금 지급 기능을 호출하지 않는다.

## 13. 공용 처리 계약과 월간 순서

### 13.1. 공용 helper

아래 이름은 새 구현의 제안 ID다. 여러 실제 호출처에서 공유되는 로직만 helper로 만든다. 매월 호출된다는 이유만으로 일회용 분기를 분리하지 않는다.

| helper | 입력 | 호출처 | 책임 |
| --- | --- | --- | --- |
| `eafp_concession_can_grant` | region, host, holder | 획득 목표, 특약 GUI | 실행에 필요한 지역·현재 소유·생존·상한 검증. 열강·이해관계는 각 경로의 등록 조건에서 추가 |
| `eafp_concession_grant_effect` | 같은 입력 + 획득 원인 | 전쟁 목표, 특약 처리 | extent 증가, 목록 등록, revision 증가, 효과 재계산 |
| `eafp_concession_return_effect` | region, holder, 선택적 예상 revision, 반환 원인 | 반환 목표, 월간 사건 | 지정 기록만 삭제하고 남은 조계 효과 재계산 |
| `eafp_concession_refresh_effect` | 관련 국가·지역 | 월간, 획득, 반환, 소유국 변경 | 위신 판정·합산 modifier·UI 갱신. 현금 지급과 사건 추첨 없음 |
| `eafp_concession_resolve_host` | 고정 REGION/ANCHOR 매개변수 | 모든 권리 변경·판정 | 거점 state/host 스코프를 다시 찾음 |

목록 등록 전에 중복 여부를 검사한다. 반환 helper는 대상이 이미 없으면 성공한 무동작으로 끝내며 다른 지역을 찾아 대신 반환하지 않는다. 특약 소비는 획득 helper 안에 넣지 않는다. 전쟁 목표 획득이 특약까지 지우는 일을 막기 위해 특약 경로의 외부 처리에서만 소비한다.

### 13.2. 월간 단일 진입점

`common/on_actions/00_code_on_actions_definition.txt`의 기존 글로벌 `on_monthly_pulse.on_actions`에 `china_concessions_on_monthly_pulse`를 한 번만 추가한다. 기존 중국 재통일 호출 등은 보존한다. 국가별 pulse와 계산 전용 저널에 같은 호출을 동시에 연결하지 않는다. 글로벌 루트에는 국가 `ROOT`가 없으므로 모든 국가 스코프를 명시한다.

```text
monthly:
    1. 26개 지역의 기록, 거점, host, 살아 있는 holder를 확인한다.
    2. 기존 소유국과 현재 소유국을 포함한 관련 국가 집합을 만든다.
    3. 관련 국가의 현재 위신을 임시 값으로 모두 읽는다.
    4. 모든 조계의 active 결과를 계산한다. 아직 modifier를 바꾸지 않는다.
    5. 과거 조계 합산 modifier와 계산용 임시 합계를 정리한다.
    6. 지역별 U, 상한, 사건 기록을 읽고 수입·비용·도시 효과를 계산한다.
    7. 국가별 위신·도시별 합산 modifier를 적용한다.
    8. host 차감과 holder 순수입을 국가별 순액으로 합산해 한 번 지급한다.
    9. 지역마다 active 조계가 있으면 월간 이벤트를 한 번 추첨한다.
   10. 표시 목록을 갱신하고 임시 계산값을 제거한다.
```

처리 중 반환으로 목록을 지울 때는 순회 대상의 임시 복사본 또는 제거 예정 목록을 사용한다. 목록을 직접 수정하며 순회해 다음 holder를 건너뛰지 않는다. 나라 하나가 모든 AI를 정복하거나 플레이어만 남아도 월간 처리 자체는 계속 실행되어야 한다.

월간 처리 밖의 강제 반환은 즉시 상시 효과를 정리한다. 이미 정산한 그 달 지급은 그대로이며 다음 정산에서 제외한다. UI 조회는 읽기 전용이다.

## 14. 전쟁 목표와 외교전

### 14.1. 획득 목표

정의 위치는 `common/war_goal_types/eafp_concessions_war_goals.txt`, ID는 `eafp_acquire_concession`으로 한다.

| 항목 | 값 또는 규칙 |
| --- | --- |
| `kind` | `custom` |
| `target_type` | `state` |
| `contestion_type` | `control_target_state` |
| `execution_priority` | 초안 10. 영토 이전 목표보다 뒤에서 최종 소유자를 검증 |
| `settings` | `require_target_be_part_of_war`, `requires_interest`, `validate_target_not_treaty_port`; 같은 주·같은 수혜국 중복 목표 검증은 시험 후 선택 |
| `ROOT` | 조계를 받을 국가 |
| `scope:target_country` | 조계를 내줄 현재 host |
| `scope:target_state` | 거점 province를 포함하는 host의 state |
| `maneuvers` / `infamy` | 초기 10 / 5. 별도 script value로 분리 |
| 효과 | 해당 region에서 ROOT의 권리 500bp 획득/확대, 영토 이전 없음 |

`possible`은 목표 선택 목록을 필터링하고 `valid`는 외교전 진행 중의 유효성을 확인한다. 공통 조건은 대상 26개 지역, 지정 거점 포함, 대상 state의 소유국 일치, holder와 host가 서로 다름, 열강 자격·해당 전략지역 이해관계, 조약항 아님, 잔여 500bp 이상이다. 위신이 낮은 국가는 획득해도 중단 상태가 될 수 있으므로 위신 비교를 획득 금지 조건으로 추가하지 않는다. UI에서 예상 중단을 보여 준다.

요구를 등록할 때의 열강 자격과 이해관계는 외교전 선택 조건이다. 목표 관철 시에는 국가 생존·정확한 현재 host·대상 조계/지역·상한처럼 결과 적용에 필요한 조건을 다시 확인한다. 전쟁 중 순위 하락만으로 이미 관철된 요구를 소급 취소하지 않는다. 같은 지역이 먼저 타국에 양도되어 host가 달라졌다면 새 소유국에 무작위 조계를 만들지 않고 미적용 사유를 알린다.

다음은 뼈대이며 helper 정의와 스코프 연결을 채워야 한다.

```paradox
eafp_acquire_concession = {
    icon = "gfx/interface/icons/war_goals/enforce_treaty_article.dds"
    kind = custom
    target_type = state
    contestion_type = control_target_state
    execution_priority = 10
    settings = {
        require_target_be_part_of_war
        requires_interest
        validate_target_not_treaty_port
    }
    possible = {
        # ROOT = 수혜국. target_state/target_country를 공통 검증에 연결.
        # 10절의 거점과 일치하는 state인지 확인.
    }
    valid = {
        # 진행 중 유효성. 다른 전쟁 목표와의 중복/충돌도 확인.
    }
    maneuvers = { value = 10 }
    infamy = { value = 5 }
    on_enforced = {
        # region/host/holder를 명시적으로 저장한 뒤
        # eafp_concession_grant_effect를 이곳에서 한 번 호출.
    }
    ai = { is_significant_demand = yes }
}
```

일반 `on_wargoal_enforced`나 항복 알림에서 같은 획득 효과를 다시 호출하지 않는다. 목표별 `on_enforced`와 전역 알림을 함께 사용하면 확대가 두 번 적용된다. 전쟁 목표의 열강 외 국가 대리 요구는 첫 버전에서 제외하고 `can_add_for_other_country`를 설정하지 않는다.

### 14.2. 반환 목표의 주 선택 문제와 해결

기본 `target_type = state`는 **적국 소유 state**를 순회한다. 반환 대상 조계가 있는 state는 요구국(host) 소유이므로 단순히 획득 목표의 효과만 뒤집으면 반환할 주를 선택할 수 없다.

첫 구현에서는 지역마다 country-target 반환 목표를 생성한다. 예: `eafp_return_concession_eastern_hubei`. 이 목표의 지역은 ID에 고정되고 `scope:target_country`가 조계 holder다. 선택 목록에는 “동부 후베이 조계 반환 — 영국”처럼 주와 상대국을 함께 표시한다. 26개 지역 목표는 하나의 생성 템플릿으로 관리한다.

| 항목 | 값 또는 규칙 |
| --- | --- |
| `kind` / `target_type` | `custom` / `country` |
| `contestion_type` | `control_own_capital` 초안. 조계를 보유한 외국 수도 점령을 필수로 요구하지 않는 방어적 목표 |
| `execution_priority` | 10 |
| `settings` | `require_target_be_part_of_war`. 영토 병합·종속화 관련 flags는 넣지 않음 |
| `ROOT` | 해당 지역 거점의 현재 host |
| `scope:target_country` | 반환할 조계를 가진 holder |
| `possible` / `valid` | ROOT가 지정 거점 소유, 상대국 기록 존재, 양국 생존·서로 다름. 작동 중단 조계도 허용 |
| `maneuvers` / `infamy` | 초안 10 / 0 |
| `on_enforced` | 지정 region과 상대국의 조계만 반환 helper 호출 |

반환 목표는 현재 존재하는 해당 국가의 권리를 대상으로 한다. 사건의 오래된 선택지를 검증하는 revision 조건을 전쟁 목표에 억지로 추가하지 않는다. 관철 시 이미 조계가 없다면 무동작으로 끝내며 대신 다른 조계를 제거하지 않는다. 반환 목표에 포함된 주가 평화 처리 중 다른 정부로 넘어갔다면 ROOT의 소유 조건을 재확인하고 미적용 사유를 알린다.

### 14.3. 외교전 등록과 관철 처리

- `common/diplomatic_plays/eafp_concessions_diplomatic_plays.txt`에 `dp_eafp_acquire_concession`과 지역별 `dp_eafp_return_concession_<region>`을 정의한다.
- `war_goal`은 각각 위 목표 ID를 가리킨다. `mirror_war_goal = yes`는 쓰지 않는다. 획득의 반대가 동일한 획득 목표가 아니기 때문이다.
- 플레이어는 렌즈/외교전 목표 목록 또는 조계 화면에서 국가와 주를 명시한다. 화면 버튼으로 시작할 때도 같은 엔진 외교전을 만들며 결과를 별도 버튼 효과로 지급하지 않는다.
- 무혈 요구 수락, 외교전 양보, 평화 조약에서의 목표 관철 모두 정확히 한 번만 적용되는지 각각 검증한다. `on_demand_accepted`는 외교전 객체가 없을 수 있으므로 무조건 같은 효과를 추가하지 않는다.
- 실제 시험에서 특정 수락 경로가 목표의 `on_enforced`를 호출하지 않을 때만 그 경로에 보완 처리를 넣는다. 이미 처리된 경로에 캐시 플래그를 덧붙여 이중 호출을 가리는 방식은 피한다.
- 일반 전쟁 승리, 목표가 빠진 별도 평화, 백지 평화에는 획득·반환 효과가 없다. 월간 사건으로 이미 반환된 권리가 백지 평화 때문에 복구되는 일도 없다.

## 15. 특약 획득 UI와 처리

### 15.1. 사용자 흐름

기존 `establish_concession_button`은 조계 목록/대상 선택 화면을 연다. 현재 플레이어에게 특약을 빚진 국가 목록 → 그 국가가 거점을 소유한 대상 주 → 획득 또는 확대할 조계 순서로 선택한다. 기존 `random_country`와 이벤트의 무작위 주 선택은 제거한다.

행마다 국가·주·기존 권리·획득 후 권리·잔여 상한·추정 월 순수입·특약 1개 소비·위신에 따른 예상 작동 여부를 보여 준다. 사용자가 “특약으로 획득/확대”를 실행하는 순간 최종 조건을 다시 검사한다. 설명만 띄우고 실제 특약이 남아 있는 구현은 실패다.

### 15.2. 실행 계약

```text
try_obligation_grant(actor, region):
    resolve current host and anchor state
    verify actor != host and both alive
    verify rank/interest/region/capacity and current ownership
    verify host owes an obligation to actor
    if any check fails: show reason, change nothing
    in one synchronous effect chain:
        increase actor extent by 500 and register membership
        increment actor-region revision
        host clears obligation owed to actor
        refresh effects/UI without paying cash or rolling events
```

특약 소비의 스코프 골격은 다음과 같다. `ROOT`의 의미가 GUI와 이벤트 사이에서 바뀔 수 있으므로 이름 있는 스코프를 쓴다.

```paradox
# concession_host = 특약 채무국, concession_holder = 특약 채권국
scope:concession_host = {
    if = {
        limit = { owes_obligation_to = scope:concession_holder }
        set_owes_obligation_to = {
            country = scope:concession_holder
            setting = no
        }
    }
}
```

위 코드는 소비 부분만 보여 준다. 실제 구현에서는 획득 가능한 모든 조건 검증을 먼저 끝내고 설치와 소비 사이에 선택 이벤트·날짜 지연을 두지 않는다. 엔진의 범용 트랜잭션/롤백 기능이 있다고 가정하지 않는다. 같은 틱 두 번 클릭하면 첫 실행이 특약을 소비하므로 두 번째는 검증에서 실패해야 한다.

실패 사유는 `no_obligation`, `wrong_obligation_direction`, `host_changed`, `no_capacity`, `invalid_anchor`, `rank_or_interest` 등 사용자에게 설명 가능한 현지화 문구로 구분한다. 실패 플래그를 영속 저장할 필요는 없으며 `IsValid`와 실행 직전 검사에서 도출한다.

## 16. 월간 이벤트 설계

### 16.1. 추첨과 스코프

이벤트는 기존 `concessions_in_china` 네임스페이스의 비어 있는 `.200`~`.299` 구간을 사용한다. 구현 전에 키 중복을 다시 검사한다. 기존 `.1`의 정산과 `.1001`~`.1006`의 자동 획득/반환은 그대로 살리지 않는다.

첫 밸런스는 지역당 월 5%로 사건을 시도하고, 아래 후보 중 조건을 충족하는 사건을 가중 추첨한다. 후보가 없으면 그달 사건이 없다. 보유국 수가 늘어도 5%를 국가마다 반복하지 않는다. 선택된 사건의 조건을 만족하는 작동 중 조계 하나를 골라 host 또는 holder에게 전달한다.

이벤트 컨텍스트에는 region, anchor state, host, holder, 해당 `revision`을 저장한다. 장기간 남아 있을 이벤트에서는 임시 스코프가 아니라 이벤트에 보존되는 `save_scope_as`/`save_scope_value_as` 패턴을 사용한다. 국가 전역에 “현재 대상 국가” 하나만 저장하면 서로 다른 사건이 덮어쓰므로 금지한다.

플레이어가 선택하기 전에 소유국·권리·revision·위신이 달라질 수 있다. 모든 선택지의 효과 시작에서 현재 대상과 작동 자격을 다시 확인한다. 이미 반환·재설치·확대되어 revision이 바뀌었거나 host가 바뀐 사건은 비용 없이 종료한다. 그 사건에서 다른 조계를 무작위로 찾아 대신 적용하지 않는다. 여러 달의 사건이 열려 있어도 같은 선택지의 일회성 효과가 두 번 실행되지 않게 한다.

### 16.2. 사건 초안

아래 관계 수치·기간·가중치는 구현 기본값이며 균형 조정 대상이다. `G`는 대상 조계의 이벤트 직전 기본 월 수입이다. 배상금은 payer 국고에서 빼고 receiver 국고에 같은 액수를 더한다.

| ID / 수신자 | 후보 조건·가중치 | 선택/결과 |
| --- | --- | --- |
| `.200` 용의자의 조계 도피 / holder | 작동 조계, 20 | 공동 조사: 관계 +5. 인도 거부: 관계 -10, 해당 조계 `disruption` 180일 |
| `.201` 관헌과 외국 경찰 충돌 / host | 작동 조계, 20 | 배상 수용: holder가 host에 `G` 지급, 관계 +5. 항의: 관계 -10, 수입 감소 180일. 무력 해결: 조건을 만족하면 host→holder 반환 전쟁 즉시 개시 |
| `.202` 중국인 대표 참여 요구 / holder | representation 없음, 20 | 허용: representation 365일, 관계 +10. 거부: 관계 -5, 수입 감소 180일 |
| `.203` 시정 시설 정비 / holder | works 없음, 15 | 정비: 즉시 £200 지출, works 365일 및 월 추가 운영비. 유보: 현 상태 유지 |
| `.204` 조계 시정기구 붕괴 / host 알림 | host와 holder 관계가 -50 이하, 작동 조계, 2 | 자동 강제 반환. 선택지에서 재승인받지 않고 사건 적용 시 해당 조계 기록을 제거한 뒤 알림만 표시 |
| `.205` 시위 발포와 군사 충돌 / host 알림 | 관계 -50 이하, 자동 전쟁 생성 조건 충족, 1 | host→holder 반환 목표를 가진 전쟁을 자동 시작. 알림 옵션은 효과를 다시 실행하지 않음 |
| `.206` 내전 피난민과 조계 / holder | host가 실제 내전 상태, 10 | 구호·시설 정비: £200 지출, 관계 +5, works 365일 및 월 추가 운영비. 통제 강화: 관계 -5, 수입 감소 180일 |
| `.207` 구역 확대 요구 / holder | 획득 가능 잔여량 있음, 10 | 특약이 있으면 15절 처리로 확대. 없으면 획득 외교전 시작 또는 철회. 무료 확대 없음 |

자동 전쟁·강제 반환은 희귀한 사건 후보이지만 기능을 비활성화하지 않는다. `.204`와 `.205`는 숨은 처리 효과에서 조건을 다시 검증하고 결과를 한 번 적용한 뒤 별도 알림을 보낸다. 사람이 알림을 닫는 시점에 전쟁/반환을 실행하는 구조는 “자동” 결과가 아니므로 사용하지 않는다.

단순 수입 감소·대표 참여·정비 결과는 지역별 기간제 변수의 유무로 계산한다. 효과가 같은 사건이 반복되면 강도를 더하지 않고 만료 기간을 갱신한다. 기간이 만료되면 다음 갱신에서 관련 modifier도 해제한다.

### 16.3. 자동 전쟁 처리

전쟁의 방향은 첫 버전에서 `initiator = host`, `target = holder`, 전쟁 목표는 `eafp_return_concession_<region>`으로 통일한다. 상대국을 단순히 굴욕 주거나 영토를 빼앗는 목표로 대체하지 않는다. 시위 사건 자체는 조계를 미리 반환하지 않으며 반환은 전쟁 목표 관철 시 발생한다. `.204`의 즉시 반환은 별도 결과다.

실행 직전에는 양국 생존·서로 다름, 거점 host와 사건 host 일치, 해당 조계와 revision 일치, 실제 위신 조건, 동일 양국 간 기존 전쟁/외교전 부재, 엔진이 허용하는 외교전 참가 조건을 확인한다. 휴전·동맹·종속 관계를 임의로 끊어 전쟁을 강제 생성하지 않는다. 엔진 조건상 전쟁을 만들 수 없으면 자동 전쟁 후보에서 제외하고, 선택 직전 달라졌다면 해당 선택은 비활성화/무동작 사유를 보여 준다. 기능을 수입 감소로 조용히 대체하지 않는다.

사용 가능한 API는 `create_diplomatic_play`와 외교전 스코프의 `set_war = yes`다. 생성 시 `war = yes`도 생성 문서에 있다. 첫 스모크 테스트에서 다음 둘 중 작동이 확인되는 한 경로만 선택한다.

1. 사건 host/holder 스코프에서 목표를 포함한 외교전을 `war = yes`로 생성.
2. 외교전을 생성하고 해당 initiator·target·정확한 전용 play type으로 새 객체를 찾은 뒤 `set_war = yes` 실행.

두 경로를 연달아 호출하지 않는다. `random_diplomatic_play`를 쓸 때는 생성 전 해당 양국 사이에 기존 외교전이 없다는 검사와 생성한 정확한 play type 조건이 필수다. 동명의 다른 전쟁이나 다른 지역의 반환 요구를 가져오지 않게 한다. “외교전 생성 성공”만으로 자동 전쟁 시험을 통과시키지 말고 실제 전쟁 상태와 해당 반환 목표를 확인한다.

## 17. 소유국 변경·반환·세이브 이관

### 17.1. 반환 공통 순서

```text
return(region, holder, expected_revision = optional):
    locate exactly this region-holder right
    if absent: return without other effects
    if event supplied revision and it differs: cancel stale event
    capture remaining works effect for the 180-day transition
    increment revision
    remove extent and all concession event records/active cache for this region
    remove holder from region membership list
    remove old host/holder/state/building aggregate modifiers and rebuild from remaining rights
    apply transition only for actual return, not prestige suspension
    update journals/UI; no cash payout and no new event roll
```

한 국가가 두 지역에 조계를 가진 경우 한 지역 반환으로 그 국가의 다른 조계 수입·위신까지 지우지 않는다. 같은 주의 다른 holder도 유지한다. 정비 전환 효과는 수입·위신·관할권을 남기지 않으며 조계 작동 판정에 영향을 주지 않는다.

### 17.2. 영토·내전 변화

`on_state_owner_change`는 존재하지만 호출 스코프를 실행 로그로 확인한 뒤 연결한다. 새 handler는 원소 복사가 아니라 영향받은 region의 거점 소유국 재조회와 합산 효과 갱신만 수행한다. 월간 재조회는 hook 누락 시에도 복구하는 기본 경로다.

| 상황 | 처리 |
| --- | --- |
| 전쟁 중 점령 | province/state `owner`가 그대로면 host 유지 |
| 내전으로 주 분할 | 거점 province가 포함된 state의 정부만 의무자. 양쪽에 복제하지 않음 |
| 통일·정식 영토 이전 | 현재 거점 owner로 변경, 옛 정부 효과 정리, 새 위신 비교 |
| 다른 정부가 거점 아닌 나머지 지역만 획득 | 조계 host 변경 없음 |
| 조계 보유국이 해당 거점 자체를 병합 | 외국 조계가 아니므로 자기 기록 제거 |
| holder의 태그/국가 스코프가 유지되는 정체 변경 | 기존 권리 유지 |
| holder 소멸 | 엔진이 확인 가능한 후계 관계를 제공할 때만 승계. 없으면 정리 |
| 국가 스코프 또는 지도 거점 판정 불가 | 해당 기록의 효과·정산·사건 보류, 디버그 사유 출력 |

### 17.3. 구 세이브 지원

저장소의 조계 파일은 현재 비활성 상태이므로 새 게임은 빈 권리 목록으로 시작한다. 역사적 조계를 무료로 배치하는 별도 시작 데이터는 이 구현 범위에 넣지 않는다.

구버전 활성 세이브 이관을 지원할 때만 다음을 일회성으로 수행한다. state의 `concession_owner_varlist`를 region 기준으로 합치고 같은 국가 중복은 한 번만 남긴다. 옛 데이터에는 extent가 없으므로 기본 500bp를 부여한다. 상한 초과 기록은 삭제하지 않고 `shrink_factor`로 제한한다. 거점과 무관한 분할 state에 복제된 목록을 각각 독립 조계로 만들지 않는다.

이관 후 옛 재정·건물 modifier, 계산용 저널, `concession_calc_holder`, 더 이상 사용하는 곳이 없는 옛 국가 소유 목록을 정리한다. `schema_version=1`을 기록하고 다음 로드에서 다시 권리를 지급하지 않는다. 이관은 월간 정산 호출이나 특약 소비를 발생시키지 않는다. 현재 코드의 `.disable`만 참고하는 경우에도 이 절의 이관 코드를 무조건 새로 만들 필요는 없다.

## 18. UI·AI·현지화

### 18.1. 표시와 행동

중국 측 저널은 자신이 거점을 소유하는 조계를, 외국 측 저널은 자신이 보유한 조계를 보여 준다. 비활성 조계도 목록에서 숨기지 않는다. 저널 완료는 작동 조계 수가 0일 때가 아니라 관련 **권리 기록**이 모두 없어졌을 때다.

각 행에는 주 이름, 현재 주 소유국, 조계 보유국, 권리 비중, 작동/위신으로 중단/소유권 확인 대기, 양국의 현재 위신, 추정 월 수입·유지비·순수입, 남은 사건 효과 기간을 표시한다. 작동 여부는 마지막 갱신 결과이고 외부 위신 변화는 다음 월간 갱신에 반영된다는 설명을 함께 표시한다. 과거 위신 값을 표시하려고 국가 변수로 중복 저장하지 않는다. 도심 레벨과 추정 세원 설명은 툴팁에 둔다. 운영 방침·공공조계·긴장도 게이지와 소·중·대 선택 UI는 만들지 않는다.

획득 행동은 “전쟁 목표로 요구”, “특약으로 획득/확대”이며 host에게는 해당 holder의 “반환 요구”를 표시한다. 각 행동은 선택된 row의 region/holder를 `GuiScope`로 전달하고 실행 시 다시 검증한다. UI에서 소유국·주 선택을 바꾼 뒤 이전 대상 스코프가 남지 않게 한다.

기존 `gui/eafp_concessions_in_china_gui.disable`은 types 정의만 있으므로 활성화할 때 실제 최상위 widget 인스턴스와 JE `widget` 연결을 함께 작성한다. `GetGlobalList('concession_candidate_states_gvarlist')`를 계속 쓸 경우 목록의 원소 타입은 **state**로 유지하고 현재 거점 state만 채운다. 권리 목록은 region에 있으므로 flag 하위 UI는 `state_region`으로 접근하도록 바꾼다. region 원소를 넣어 놓고 `Scope.GetState`를 호출하지 않는다.

### 18.2. AI 판단

AI의 최종 행동은 플레이어와 동일한 helper를 거친다. 특약 버튼의 기존 `ai_chance = { base = 0 }`를 그대로 두면 AI는 특약 경로를 사용하지 못하므로 명시적인 월간 AI 행동 평가를 한 곳에 연결한다. 기존 국가별 AI/버튼 실행 체계를 우선 사용하고 UI 버튼과 별도 AI handler 양쪽에서 동시에 실행하지 않는다.

초기 판단 기준은 다음과 같다.

- 특약 획득/확대: 획득 후 작동 가능하고 예상 순수입이 양수인 후보 중 우선순위를 정한다. AI는 낮은 위신으로 즉시 중단될 조계에 특약을 쓰지 않는다.
- 획득 전쟁: 예상 순수입·전략지역 가치에서 예상 전쟁 비용·관계 손실을 뺀 점수가 양수인 경우에만 고려한다. 이미 같은 요구를 진행 중이면 중복 시작하지 않는다.
- 반환 전쟁: host의 군사력과 상대국·동맹 전력을 비교한다. 위신 때문에 이미 중단된 조계는 낮은 우선순위로 두되 목표 자체를 막지 않는다.
- 월간 사건 선택: 배상액·작동 순수입·군사 전력·관계를 읽는다. 군사적으로 감당하기 어려우면 `.201`의 무력 해결보다 공동 조사/배상을 선호한다. 자동 결과 `.204/.205`는 AI 선택 여부와 무관하다.

새 “AI 긴장도”나 전략 가치를 누적하는 변수를 만들지 않는다. 수치는 판단 시 직접 계산하고, 여러 행동 후보를 한 번의 평가에서 골라 한 국가가 같은 회차에 같은 특약을 여러 번 쓰지 않게 한다.

### 18.3. 현지화 계약

기존 `localization/korean/eafp_china_l_korean.yml`, `localization/english/eafp_china_l_english.yml`, `localization/simp_chinese/eafp_china_l_simp_chinese.yml` 세 파일을 함께 갱신한다. 세 언어 모두 ID 누락 없이 작성하고 기존 `concept_concession_desc`의 TODO를 채운다. 사용자에게 영토가 할양됐다는 옛 설명은 “주 소유권은 유지되며 도시 일부의 조계권을 보유”하는 설명으로 바꾼다.

필요 키 묶음은 목표 이름/설명, 지역별 반환 목표 이름, 외교전 이름, 획득·확대·반환 버튼, 특약 소비 설명, 위신 동률·초과 상태, 실패 사유, 수입 계산 툴팁, 월간 사건 title/desc/flavor/options, 자동 전쟁/반환 알림, 정비 전환 modifier다. 이벤트의 모든 선택지는 실제 효과와 같은 국가·주·비용·전쟁 결과를 툴팁으로 보여 준다.

## 19. 파일별 작업 순서

다음은 **향후 구현 시** 편집할 파일이다. 이번 요청에서는 이 명세 문서만 수정한다.

| 파일/경로 | 작업 | 완료 조건 |
| --- | --- | --- |
| `tools/data/china_concessions_regions.json` | 10절의 26개 region/anchor/식별자 저장 | 기본 게임의 region 및 province와 모두 일치 |
| `tools/generate_china_concessions.py` | 정적 region 분기·반환 목표·외교전·현지화 반복 부분 생성 | 같은 입력으로 재생성하면 diff 없음 |
| `common/script_values/eafp_concessions_values.txt` | 단위·상한·수입·비용·사건 가중치 | 표의 숫자가 다른 파일에 중복 하드코딩되지 않음 |
| `common/scripted_triggers/eafp_concessions_triggers.txt` | 둘 이상 경로에서 쓰는 자격·대상 검증 | GUI와 목표가 같은 조건 사용 |
| `common/scripted_effects/eafp_concessions_effects.txt` | 공용 설치·반환·재계산 및 지역 템플릿 | 정산 없는 refresh와 실제 지급 분리 |
| `common/war_goal_types/eafp_concessions_war_goals.txt` | 획득 1개·지역별 반환 26개 목표 | 모든 수락/관철 경로에서 정확한 조계 한 번 처리 |
| `common/diplomatic_plays/eafp_concessions_diplomatic_plays.txt` | 대응 play 정의 | 목표 선택과 월간 자동 전쟁 모두 같은 정의 사용 |
| `common/on_actions/concessions_code_on_actions.txt` | 옛 `.disable`을 재작성해 글로벌 월간/소유국 변경 처리 | 옛 승리 자동 지급·복제 로직 없음 |
| `common/on_actions/00_code_on_actions_definition.txt` | 검증된 기존 hook에 연결 | 글로벌 월간 계산 1회, 다른 콘텐츠 호출 보존 |
| `events/eafp_chi_events/eafp_concessions_in_china_events.txt` | 기존 파일 재작성, `.200`대 사건과 알림 | 자동 결과와 클릭 결과의 중복 실행 없음 |
| `common/scripted_buttons/eafp_concessions_in_china_buttons.txt` | 기존 획득 버튼을 명시적 대상 선택 진입으로 수정 | 무작위 국가/주 없음, 옛 특약 반환 버튼 미노출 |
| `common/scripted_guis/concessions_in_china_sgui.txt` | 행별 행동·검증·툴팁 | 선택된 region/holder로만 실행 |
| `common/journal_entries/eafp_concessions_in_china.txt` | 기존 양측 JE와 widget 연결 | 중단된 권리도 표시, 기록 0일 때만 완료 |
| `gui/eafp_concessions_in_china_gui.gui` | 행, 국기, 상태, 행동, widget 인스턴스 | 실제 JE에서 UI 표시·클릭 확인 |
| `common/static_modifiers/eafp_chi_modifiers.txt` | 옛 조계 modifier를 새 합산 효과로 교체 | 기업 지분 변경·재정 이중 차감 없음 |
| 세 언어의 `eafp_china_l_*.yml` | 18.3절 키 | 누락·TODO·상태와 다른 설명 없음 |

구현 순서는 아래와 같다.

1. 데이터 매핑과 최소 권리 1개를 디버그로 생성해 저장·재로드·거점 소유국 판정 확인.
2. 특약 소비와 위신 판정부터 구현해 설치·중단·재개·반환의 공용 처리를 확인.
3. 획득 목표 1개, 동부 후베이 반환 목표 1개를 시험하고 성공 후 나머지 지역을 생성.
4. 월간 계산과 돈 보존식, 상시 modifier를 연결.
5. 단순 월간 사건 → 강제 반환 → 자동 전쟁 순으로 연결.
6. JE/GUI·현지화·AI를 연결하고 구 경로 중복 여부를 검사.
7. 게임 오류 로그, 테스트 표, 재로드·내전 시나리오를 통과한 후 활성화 파일만 정리.

게임 스크립트·GUI·현지화 파일은 저장소 스킬의 UTF-8 BOM/CRLF 규칙을 따른다. 생성 파일에도 같은 규칙을 적용한다. 명세 속 pseudocode를 Jomini 문법 파일로 복사해 오류를 해결하는 방식으로 구현하지 않는다.

## 20. 검증 시나리오와 완료 기준

### 20.1. 정적 검사

- `.txt`, `.gui`, `.yml`의 활성 정의만 대상으로 ID 중복·호출 대상 누락·현지화 누락을 확인한다. `.disable`의 옛 ID까지 중복 정의로 잘못 계산하지 않는다.
- 26개 region이 기본 게임에 있고, 대표 province가 해당 region의 provinces 목록에 실제로 포함되는지 확인한다.
- 생성된 반환 목표 26개가 서로 다른 region을 참조하고 각 play가 해당 목표를 가리키는지 확인한다.
- `china_concessions_on_monthly_pulse` 연결은 글로벌 hook 한 곳만 남긴다. `je_concession_calc`와 국가별 옛 pulse는 활성 참조가 없어야 한다.
- `set_owes_obligation_to`에서 성공한 획득의 채무국에 `setting = no`가 적용되는지 확인한다. 양측에 새로운 특약을 만드는 코드가 없어야 한다.
- GUI의 목록 원소 타입, JE widget 이름, 최상위 GUI 인스턴스, 실제 scripted GUI ID가 일치해야 한다.

### 20.2. 게임 실행 테스트

테스트는 작은 디버그 세이브에서 시작하며, 각 결과의 대상 국가·주·권리·국고·modifier와 `error.log`를 함께 확인한다. 테스트용 호출은 일반 플레이 UI에 노출하지 않는다.

| 번호 | 준비/행동 | 기대 결과 |
| --- | --- | --- |
| T01 | 26개 매핑을 순회 | 모두 거점 state와 현재 owner를 찾음. 만주·대만 후보 없음 |
| T02 | host 위신 100, holder 99/100/101 | 각각 중단/작동/작동. 순위가 같아도 실제 위신으로 판단 |
| T03 | 같은 지역 영국 90, 프랑스 110, host 100 | 영국만 중단. 프랑스 수입은 영국 몫을 흡수하지 않음 |
| T04 | host 위신 상승 후 다음 월 처리, 이후 하락 | 기록·extent 유지, 모든 상시 효과·지급·신규 사건 중단 후 재개 |
| T05 | 위신 bonus로 경계값 변화, holder 순회 순서 뒤집기 | 같은 판정 시작 스냅샷이면 같은 결과. 처리 중 재귀 갱신 없음 |
| T06 | host가 holder에게 특약 보유, 획득 실행 | 권리 +500bp, 기존 특약 한 번 소비, 반대 방향 특약 생성 없음 |
| T07 | 반대 방향/없는 특약, 상한 부족, 소유국 변경 | 실패 사유 표시, 권리·특약·국고 불변 |
| T08 | 특약 버튼 연속 클릭, 기존 조계 확대 | 첫 클릭만 소비·확대. 동일 region-holder 목록 원소는 하나 |
| T09 | 낮은 위신 holder가 특약으로 획득 | 특약 소비 및 권리는 존재하지만 효과는 중단 |
| T10 | 획득 요구 수락/양보/전쟁 후 관철 각각 | 지정 주에 한 번만 +500bp. 영토 소유권 불변 |
| T11 | 일반 전쟁 승리·백지 평화·해당 목표 제외 평화 | 조계 획득/반환 효과 없음 |
| T12 | host가 자기 땅의 영국 조계 반환 목표 선택 | 적국 state가 아니라 해당 지역 country-target 목표를 선택 가능 |
| T13 | 위신으로 중단된 조계 반환 목표 관철 | 기록도 제거. 이후 위신 회복으로 되살아나지 않음 |
| T14 | 같은 지역 2국, 한 국가 2지역, 한 조계만 반환 | 나머지 권리와 국가 합산 효과 유지 |
| T15 | U=10, 500bp 조계 두 곳 정산 | host -1000, holder 각각 +300, 운영비 합계 400 |
| T16 | 수입 감소·대표 참여·정비 효과 동시 적용 | 12절 산식과 일치, host 차감=순수입 합+비용 합 |
| T17 | 모든 조계 중단 또는 U=0 | 0으로 나누지 않음. 중단은 모두 0, U=0인 작동 조계는 기본 관리비만 부담 가능 |
| T18 | 세이브 로드·UI 열기·단순 refresh 반복 | 추가 현금 지급·이벤트 추첨·특약 소비 없음 |
| T19 | 월간 사건 강제 발생, 보유국 수 1→3 | 주당 추첨 횟수 한 번, 국가 수로 발생률이 세 배가 되지 않음 |
| T20 | `.204` 자동 강제 반환 | 알림 클릭 전 지정 조계 제거, 클릭 후 재실행 없음 |
| T21 | `.205` 자동 전쟁 | 실제 전쟁 상태, host→holder, 올바른 지역 반환 목표. 외교전 단계에만 머물지 않음 |
| T22 | 기존 전쟁/외교전 존재, 국가 소멸, 휴전 | 잘못된 중복 전쟁 없음. 해당 자동 전쟁 후보 제외/사유 확인 |
| T23 | 사건을 열어 둔 뒤 반환·재설치·확대·소유국 변경 | 옛 revision/host의 사건은 취소, 새 권리·다른 조계에 영향 없음 |
| T24 | 사건 기간 만료·중단 중 만료·반환 | modifier 및 기간제 기록이 남지 않음. 반환만 정비 전환 효과 생성 |
| T25 | 내전 분할 후 거점이 한쪽에만 존재 | 해당 정부만 부담. 두 정부에 조계 복제 없음 |
| T26 | 점령·통일·정식 영토 양도·holder 자기 병합 | 17.2절의 소유권 규칙 적용, 옛 정부 비용/효과 제거 |
| T27 | 모든 AI 제거, 플레이어 국가만 생존 | 글로벌 월간 처리 정상 작동 |
| T28 | 구 세이브 이관 후 두 번 재로드 | 목록 중복·추가 500bp·이중 현금 지급 없음 |
| T29 | 한국어·영어·중국어로 JE와 사건 확인 | 키 노출 없음, 위신·수입·대상·자동 결과 설명 일치 |
| T30 | AI 특약/전쟁/사건 판단 관찰 | 동일 공용 검증 사용, 플레이어 전용 숨은 이득/AI 무료 조계 없음 |

### 20.3. 먼저 확인해야 할 실행상 쟁점

| 쟁점 | 확인 방법 | 실패 시 처리 |
| --- | --- | --- |
| 주 지역 변수/국가 목록 저장 | 권리 생성 후 저장·재로드 | 11.1절의 지역별 전역 목록 대안 사용. 둘 다 운영하지 않음 |
| country-target 지역별 반환 목표의 UI 선택 | 동부 후베이 목표 한 개로 외교전 시작 | 지역 고정 play와 목표 연결을 수정. 적국 state 대상으로 바꾸지 않음 |
| `on_enforced`의 수락·양보·평화별 호출 | 각 경로에 디버그 로그를 붙여 호출 수 확인 | 빠진 경로만 보완하고 이중 호출 금지 |
| 자동 전쟁 호출 방향/목표 필드 | 두 국가 테스트에서 실제 initiator/target/goal 검사 | 문서와 사용례의 차이를 해소한 후 한 경로 채택 |
| 소유국 변경 hook의 스코프 | 영토 양도 때 로그 확인 | 확인 전에는 글로벌 월간 재조회 사용 |
| 서비스 modifier 스코프/효과 | 도심 건물 한 곳에만 시험 | 파서가 지원하는 도심 전용 효과로 수정하고 문서 수치 동기화 |
| 실제 도시 세수 조회 | 엔진 값과 예산 화면 대조 | 첫 버전 추정치 사용, 추정임을 표시 |

명세 작성 완료와 구현 완료를 구분한다. 구현 완료는 활성 코드·현지화·UI가 연결되고 위 테스트를 통과했을 때만 선언한다. 특히 자동 전쟁·강제 반환·특약 소비 중 하나가 빠져 있거나, 이벤트 효과를 설명만 하고 실행하지 않는 상태는 완료로 보지 않는다.
