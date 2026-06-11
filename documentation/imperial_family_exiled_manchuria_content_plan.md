# `imperial_family_exiled` 만주 콘텐츠 구상

## 전제

청나라 붕괴 이벤트에서 플레이어가 `만주로 몽진한다`를 선택하면 `c:MCH`에 `imperial_family_exiled` 변수가 붙는다. 이 루트의 핵심은 일반적인 봉천/만주 군벌이 아니라, 중원을 잃은 황실이 발상지로 돌아와 생존과 복벽을 동시에 도모하는 `망명 조정`이다.

기존 흐름상 `MCH`는 이미 만주 군사 본부 또는 만주 군벌 태그로 쓰이고, 중국 분열 체계에서는 `warlord_state` 또는 `eafp_is_chinese_fragment` 조건에 자연스럽게 편입될 수 있다. 따라서 신규 콘텐츠는 다음 세 가지를 분명히 나누는 방향이 좋다.

- 평시 만주: `je_home_of_the_manchus`
- 중국 분열 후 일반 만주 군벌: `warlord_state`
- 황실 몽진 만주: `imperial_family_exiled`

## 핵심 플레이 판타지

`imperial_family_exiled` 만주는 강한 국가가 아니라, 상징 자본만 강한 국가다. 플레이어는 황제라는 명분, 만주라는 성지, 팔기라는 낡은 군사 전통, 한인 관료와 이주민의 현실적 행정력, 러시아와 일본의 압력을 동시에 다뤄야 한다.

추천 테마는 다음과 같다.

- 황실 보호: 황제와 종실을 보존하고 망명 조정을 안정화한다.
- 발상지 재건: 봉천, 길림, 흑룡강을 `대청의 근거지`로 재편한다.
- 팔기 재편: 낡은 기인 봉급 공동체를 근대적 군사 또는 귀족 신분으로 바꾼다.
- 한인 협치: 만주로 유입된 한인 관료, 지주, 상인과 타협한다.
- 외세 후견: 러시아, 일본, 영국, 프랑스 중 누구에게 인정과 원조를 받을지 고른다.
- 복벽 또는 생존: 중원 수복, 입헌 망명 왕조, 만주 국가화, 황실 퇴위 중 하나로 귀결한다.

## 새 저널: `je_manchu_exile_court`

### 표시 조건

- `ROOT = c:MCH`
- `has_variable = imperial_family_exiled`
- `is_country_alive = yes`
- `NOT = { has_global_variable = eafp_manchu_exile_resolved }`

### 권장 그룹

- 단기적으로는 `je_group_qing` 재사용
- 장기적으로는 중국 분열 전용 그룹이 필요하면 `je_group_chinese_interregnum` 또는 `je_group_manchuria` 추가

### 저널 목표

망명 조정을 안정화하고, 대청의 장래를 결정한다.

완료 조건 예시:

- `exile_court_legitimacy >= 80`
- `manchurian_stability >= 70`
- `is_subject = no`
- 수도가 만주 지역에 있음
- 황제가 생존 중

실패 조건 예시:

- 황제가 사망하거나 폐위됨
- `manchurian_stability <= 0`
- `MCH`가 합병됨
- 공화정 법률 채택
- `ROC` 또는 다른 중국 중앙정부에게 항복 결정 사용

### 추적 변수

- `exile_court_legitimacy`: 망명 조정의 정통성. 황실 의례, 외교 승인, 복벽 선전으로 증가.
- `manchurian_stability`: 만주 내부 안정. 한인 협치, 치안, 식량, 이주민 관리로 증가.
- `restoration_momentum`: 중원 수복 여론. 군사 성공, 중국 내 보수파 접촉, 외세 승인으로 증가.
- `foreign_dependency`: 외세 의존도. 원조와 차관을 받을수록 증가하며, 엔딩 분기에서 위험 요소가 됨.

## 저널 진행 단계

### 1단계: 봉천에 조정을 세우다

초기 이벤트로 망명 조정의 소재를 정한다.

- 봉천 궁전 재개장: 정통성 증가, 비용 증가, 귀족/지주 세력 강화.
- 길림 임시 조정: 안정 증가, 정통성은 낮음, 관료제 강화.
- 하얼빈 외교 피난처: 외세 접촉 증가, `foreign_dependency` 증가.

효과 예시:

- `add_modifier = exile_court_in_mukden`
- `set_capital = STATE_SOUTHERN_MANCHURIA` 또는 현재 소유 만주 주 중 하나
- `exile_court_legitimacy +10`
- `manchurian_stability -5`

### 2단계: 황실 재산과 옥새

자금과 상징물 회수 이벤트.

- 옥새를 되찾았다: 정통성 대폭 증가, 복벽 명분 강화.
- 내탕금을 풀어 군대를 먹인다: 재정 획득, 황실 권위 감소.
- 보물을 담보로 차관을 얻는다: 즉시 자금, `foreign_dependency` 증가.

이 이벤트는 기존 몽진 이벤트 직후 1개월 안에 발생시키기 좋다.

### 3단계: 팔기 재편

기존 `je_manchus_and_han`의 팔기/기인 관련 감각을 망명 만주에 맞게 축소 재활용한다.

선택지:

- 팔기 특권 복구: 만주 귀족과 지주 강화, 병력 동원 보너스, 한인 급진파 증가.
- 신식 금려군 창설: 군부와 지식인 강화, 군사 기술 또는 훈련율 보너스.
- 기인 봉급 삭감: 재정 개선, 만주 지지도 하락.
- 기인 개척단 편성: 북만주 이주, 농업/벌목/광산 개발 보너스.

추천 결과:

- 팔기 복구 루트는 복벽에 유리하지만 안정에 불리.
- 신식 군대 루트는 생존형 만주 국가에 유리.
- 봉급 삭감 루트는 단기 반란 위험이 있으나 장기 산업화에 유리.

### 4단계: 한인 관료와 이주민

만주는 이미 한인 인구와 상업망 없이는 운영하기 어렵다. 망명 황실의 현실 정치가 드러나는 핵심 이벤트 묶음이다.

선택지:

- 한인 관료 유임: 관료제와 세수 개선, 만주 보수파 불만.
- 만주인 우선 등용: 정통성 증가, 행정력 부족과 세금 낭비 증가.
- 협치 내각 구성: 양쪽 지지도 소폭 증가, 급진적 복벽파 불만.

연계 효과:

- `ig_landowners`를 황실파로 유지할지, `ig_intelligentsia`와 타협할지 결정.
- `law_cultural_exclusion` 유지 또는 완화 선택을 저널 보너스와 연결.
- 한인 장군을 등용하면 `restoration_momentum`은 증가하지만 황실 경계심도 증가.

### 5단계: 공화국의 퇴위 요구

`ROC` 또는 현재 중국 중앙정부가 살아 있으면 발생한다.

공화국 측 제안:

- 황실 우대 조건으로 퇴위: 저널 실패, 대신 안정과 자금 획득.
- 만주 자치 인정 대가로 황제 칭호 포기: 만주 생존 루트.
- 거부하고 복벽을 선언: `restoration_momentum` 증가, 공화국과 관계 악화 또는 외교전 개방.

구현상 `global_var:chinese_central_government`가 있으면 그 국가를 대상으로 잡는 것이 좋다.

### 6단계: 외세의 승인

망명 조정은 혼자 오래 버티기 어렵다. 외교 결정 또는 이벤트 체인으로 구현한다.

후견 후보:

- 러시아: 동청철도, 북만주, 외만주 문제와 연결. 군사 원조와 차관은 강하지만 종속 위험이 큼.
- 일본: 남만주 철도와 군사고문. 복벽 군대에는 유리하나 괴뢰화 위험이 큼.
- 영국/프랑스: 공화국 견제용 제한 승인. 원조는 약하지만 의존도 상승이 낮음.
- 몽골: 황제의 초원 명분. 기병 또는 정통성 보너스.

결정 예시:

- `decision_seek_russian_protection_for_exile_court`
- `decision_invite_japanese_military_advisers`
- `decision_request_recognition_of_the_qing_court`

위험:

- `foreign_dependency >= 80`이면 최종 분기에서 외세 보호국 또는 괴뢰국 루트 발생.
- 러시아/일본이 만주에 이해관계 또는 외교적 관심을 가질 때 승인 확률 증가.

### 7단계: 만주의 질서

망명 조정이 오면 치안과 난민 문제가 커진다.

이벤트 소재:

- 북양군 잔당 유입: 병력 또는 급진파 중 선택.
- 혁명파 암살단: 황실 보호 강화 또는 정치 개혁 약속.
- 조선 국경 밀무역: 세수, 무기, 외교 마찰.
- 러시아 철도 경비대와 충돌: 주권 또는 안정 중 선택.
- 장백산 의례: 만주/몽골/조선 접경의 상징 행위로 정통성 증가.

### 8단계: 복벽 선포

조건 예시:

- `restoration_momentum >= 60`
- `exile_court_legitimacy >= 60`
- `is_subject = no`
- 중국 중앙정부와 휴전 또는 전쟁 가능 상태
- 최소 1개 외세가 우호적이거나 군사력이 충분함

효과:

- `MCH`가 중국 중앙정부 명분을 주장할 수 있음.
- `eafp_claim_chinese_central_government_button`과 연계하거나 별도 버튼 추가.
- 국가명 변경: `대청 망명조정`, `봉천 대청국`, `대청 복벽정부`.

대안:

- 복벽 포기 후 `만주 제국` 또는 `만주 왕국`으로 전환.
- 황실 입헌화 후 만주 독립 생존 루트.
- 공화국과 타협해 `만주 자치정부`로 전환.

## 이벤트 묶음 초안

### `imperial_exile.1` 봉천의 빈 궁전

발동: `imperial_family_exiled` 획득 후 7일.

내용: 황실이 봉천에 도착했으나 궁전은 비어 있고, 관료와 군대는 준비되어 있지 않다.

선택지:

- `선조의 궁궐을 다시 열어라`: 정통성 증가, 지출 증가.
- `먼저 군영과 창고를 장악하라`: 안정 증가, 군부 강화.
- `외국 공사관과 접촉하라`: 자금 또는 관계 보너스, 외세 의존 증가.

### `imperial_exile.2` 사라진 옥새

발동: 1단계 후.

선택지:

- `궁중 환관을 추궁하라`: 정통성 회복 가능, 급진파 증가.
- `가짜라도 만들어야 한다`: 단기 정통성, 폭로 시 큰 손실.
- `옥새보다 군대가 먼저다`: 정통성 감소, 군사 보너스.

### `imperial_exile.3` 팔기의 마지막 명부

발동: 팔기 재편 단계.

선택지:

- `명부를 복원하라`: 만주 지지, 귀족 강화.
- `쓸 수 있는 자만 남겨라`: 병력 품질, 만주 급진파.
- `팔기는 이제 의장대다`: 권위와 의례 보너스, 군사 보너스 없음.

### `imperial_exile.4` 한인 총독들의 충성 서약

발동: 안정이 낮거나 관료제 부족 시.

선택지:

- `그들의 직책을 인정한다`: 세수/관료제 증가, 만주 보수파 불만.
- `황실 감찰관을 붙인다`: 균형형.
- `모두 갈아치워라`: 정통성 증가, 행정 붕괴 위험.

### `imperial_exile.5` 공화국의 밀사

발동: 중국 중앙정부 존재.

선택지:

- `우대 조건을 논의한다`: 퇴위/타협 루트 개방.
- `만주는 황실의 발상지다`: 독립 생존 루트.
- `중원은 반드시 돌아올 것이다`: 복벽 루트, 전쟁 위험.

### `imperial_exile.6` 동청철도의 청구서

발동: 러시아가 존재하고 만주에 관심 또는 관계가 있을 때.

선택지:

- `철도권을 보장한다`: 자금/관계, 외세 의존 증가.
- `공동 경비대를 둔다`: 안정, 주권 손실.
- `주권을 침해할 수 없다`: 정통성, 외교 악화.

### `imperial_exile.7` 남만주의 군사고문

발동: 일본이 존재하고 관계가 일정 이상일 때.

선택지:

- `고문단을 받아들인다`: 군사 보너스, 외세 의존 증가.
- `무기만 구매한다`: 비용, 의존도 낮음.
- `일본군은 들일 수 없다`: 정통성, 군사 기회 상실.

### `imperial_exile.8` 장백산 제례

발동: 정통성 중간 이상, 안정 중간 이상.

선택지:

- `대청은 다시 천명에 답할 것이다`: 복벽 추진.
- `만주의 백성을 먼저 돌보겠다`: 안정과 생존 루트.
- `제례를 조용히 치른다`: 급진파 감소.

### `imperial_exile.9` 복벽의 조서

발동: 복벽 조건 충족.

선택지:

- `대청의 이름으로 중원을 회복하라`: 중앙정부 주장, 전쟁/외교전.
- `입헌군주국으로 돌아가겠다`: 지식인/산업가 타협, 보수 불만.
- `만주를 지키는 것이 곧 황실을 지키는 것이다`: 만주 국가 엔딩.

### `imperial_exile.10` 황실의 퇴위 조서

발동: 실패 조건 또는 타협 선택.

선택지:

- `황실 우대 조건을 받아들인다`: 저널 종료, 공화국과 관계 개선.
- `황제는 상징으로 남는다`: 입헌 만주 루트.
- `끝까지 버틴다`: 안정 하락, 복벽파 강화.

## 결정 초안

### `decision_restore_the_mukden_palace`

조건:

- `has_variable = imperial_family_exiled`
- `owns_entire_state_region = STATE_SOUTHERN_MANCHURIA`
- 충분한 금 보유고 또는 수입

효과:

- `exile_court_legitimacy +10`
- 수도 주에 위신/권위/귀족 정치력 보너스
- 일정 기간 정부 지출 증가

### `decision_reorganize_the_banners_in_manchuria`

조건:

- 팔기 재편 이벤트 이후
- 군대 또는 지주 세력 불만이 일정 이상

효과:

- 선택한 팔기 정책에 따라 군사, 권위, 안정 보너스
- 기존 `chi_banner_armies_*` 감각과 연결 가능

### `decision_seek_foreign_recognition_of_qing_exile`

조건:

- 독립국
- 악명 과다 아님
- 특정 열강과 관계 양호

효과:

- 승인국과 관계 증가
- 정통성 증가
- `foreign_dependency` 증가

### `decision_proclaim_qing_restoration_from_manchuria`

조건:

- 복벽 조건 충족
- `restoration_momentum >= 60`
- `exile_court_legitimacy >= 60`

효과:

- 중국 중앙정부 주장
- 주변 중국 파편국에 외교 압박 또는 복종 요구
- 국가명/국기/정부명 변경 가능

## 엔딩 분기

### 대청 복벽정부

조건:

- 복벽 조서 선택
- 중국 중앙정부 주장 성공 또는 일정 규모의 중국 본토 확보

결과:

- `MCH`가 새 중국 중앙정부가 되거나 `CHI` 복원.
- `imperial_family_exiled` 제거.
- `eafp_chinese_interregnum`과 강하게 연계.

### 만주 입헌군주국

조건:

- 복벽 포기
- 안정과 정통성이 높고, 지식인 또는 산업가와 타협

결과:

- 황제는 만주의 군주로 남음.
- 한인 협치와 외교 생존에 보너스.
- 중국 재통일 야망은 약화.

### 외세 보호하의 황실

조건:

- `foreign_dependency >= 80`
- 러시아 또는 일본과 강한 관계/의존

결과:

- 보호국 또는 종속국화 이벤트.
- 군사/경제 보너스와 주권 손실.
- 장기적으로 독립 회복 저널 가능.

### 황실 퇴위와 만주 공화화

조건:

- 안정 실패, 공화국과 타협, 또는 공화정 법률 채택

결과:

- `imperial_family_exiled` 제거.
- 황실 관련 정통성 시스템 종료.
- 일반 `MCH` 군벌/공화국 플레이로 전환.

## 구현 메모

### 권장 파일

- `common/journal_entries/eafp_manchu_exile_court.txt`
- `events/eafp_chi_events/eafp_manchu_exile_court_events.txt`
- `common/decisions/eafp_manchu_exile_court_decisions.txt`
- `common/static_modifiers/eafp_manchu_exile_court_modifiers.txt`
- `common/scripted_triggers/eafp_manchu_exile_court_triggers.txt`
- `common/scripted_effects/eafp_manchu_exile_court_effects.txt`
- `localization/korean/eafp_manchu_exile_court_l_korean.yml`
- `localization/english/eafp_manchu_exile_court_l_english.yml`
- `localization/simp_chinese/eafp_manchu_exile_court_l_simp_chinese.yml`

### 기존 코드와 연결할 지점

- `events/warlord_china_events.txt`
  - 몽진 선택지에서 `set_variable = imperial_family_exiled` 직후 `trigger_event = { id = imperial_exile.1 days = 7 }` 추가.
  - 필요하면 `add_journal_entry = { type = je_manchu_exile_court }`를 `c:MCH` 스코프에서 직접 추가.

- `common/scripted_triggers/eafp_chinese_interregnum_triggers.txt`
  - `imperial_family_exiled` 만주가 중국 파편국으로 확실히 잡히는지 확인.
  - 이미 `country_has_primary_culture = cu:manchu`가 있으므로 대체로 문제는 적음.

- `common/dynamic_country_names/eafp_china.txt`
  - `MCH`에 `imperial_family_exiled` 조건의 동적 국명 추가 가능.
  - 예: `dyn_c_qing_exile_court`, `dyn_c_qing_restoration_government`, `dyn_c_manchurian_empire`.

- `common/static_modifiers/eafp_chi_modifiers.txt`
  - 기존 만주/한 관련 모디파이어가 있으므로 팔기, 기인, 만주 지지도 쪽은 재활용 가능.
  - 망명 조정 전용 모디파이어는 별도 파일로 분리하는 편이 추적하기 쉽다.

### 주의할 점

- 몽진 직후 `c:ROC = { annex = c:CHI }`가 실행되므로, `MCH`가 종속국 상태로 남는지 확인해야 한다. 망명 조정 콘텐츠는 독립국일 때 가장 자연스럽지만, 의도적으로 공화국의 명목상 자치령으로 남기는 루트도 가능하다.
- `MCH`가 기존 군사 본부 subject type을 유지하면 외교 결정과 중앙정부 주장 버튼이 막힐 수 있다. 몽진 순간 `break_subject` 또는 별도 독립 처리 여부를 먼저 설계해야 한다.
- `je_manchus_and_han`은 `china_shatters` 시 무효화되므로, 망명 만주 전용 시스템은 해당 저널에 의존하지 않는 편이 좋다.
- 황제 캐릭터가 `MCH`로 이동한 뒤 다른 캐릭터가 80% 확률로 사망하므로, 황실 조정 이벤트에서 필요한 인물은 새로 생성하거나 생존 보장 변수를 부여해야 한다.

## 우선 구현 추천 순서

1. 몽진 직후 `je_manchu_exile_court`와 `imperial_exile.1`만 추가한다.
2. 저널 변수 3개만 도입한다: `exile_court_legitimacy`, `manchurian_stability`, `foreign_dependency`.
3. 초기 이벤트 4개를 만든다: 봉천 조정, 옥새, 팔기 명부, 한인 관료.
4. 러시아/일본 외교 이벤트를 붙인다.
5. 복벽, 만주 입헌군주국, 황실 퇴위의 3개 엔딩을 만든다.
6. 마지막으로 동적 국명과 로컬라이징을 다듬는다.

## 한 줄 요약

`imperial_family_exiled` 만주는 "중국을 잃었지만 황제를 가진 만주"다. 이 루트는 정통성은 높고 국력은 약한 상태에서, 황실을 복벽의 깃발로 삼을지, 만주 국가의 상징으로 낮출지, 외세의 후견물로 팔아넘길지를 선택하게 만들면 가장 맛이 산다.
