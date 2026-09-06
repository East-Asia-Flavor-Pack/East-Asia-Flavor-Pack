# 일본 콘텐츠 리뉴얼 4단계 구현 보고서

> 2026-09-06 후속 변경: 지역 충성도·독립성 관리는 `je_bakuhantaisei` 하나에 통합했다. 주 충성도는 독자 저장값이며, 관리 주의 `cached_daimyo_loyalty`를 이 값으로 덮어쓴다. 별도 지역 JE와 고료 기능은 사용하지 않는다. 아래의 지역 삭제·인물 평균/대표자 캐시·고료 관련 과거 서술은 결정 이력으로 보존한다. 현재 구현과 검증 범위는 [주별 통치 구현 보고](japan_regional_implementation_report.md), 효과별 변경은 [이관표](japan_regional_effect_migration.md)를 참조한다.

구현일: 2026-09-02

대상 환경: Victoria 3 1.13.11, 모든 일본 관련 DLC 활성, 신게임 전용

세이브 migration: 구현하지 않음

## 1. 구현 결과

- 바닐라 전문을 기준으로 `je_meiji_restoration`, `je_meiji_main`, `je_meiji_economy`, `je_meiji_army`, `je_meiji_diplomacy`, `je_taming_the_north`, `je_tenpo_crisis`를 `REPLACE:`했다.
- 각 블록에서 `EAFP DELTA BEGIN/END` 구간을 제거하고 공백·주석을 정규화하면 Victoria 3 1.13.11 바닐라 블록과 일치한다.
- EAFP 추가 사건은 공식 사건과 결과를 유지한 뒤 단발성 guard를 거쳐 호출한다.
- 런타임 bridge trigger/effect와 바닐라 JE 상태를 복제하는 변수는 만들지 않았다.

## 2. 저널 처리

| 대상 | 처리 |
|---|---|
| 메이지 5개 JE와 유신 JE | 바닐라 버튼, widget, 변수, 공식 사건, 완료·실패·무효화 결과를 유지하고 EAFP legacy 사건과 추적 flag만 추가 |
| `je_taming_the_north` | 바닐라 5개 버튼·3개 카운터·아이누 우호도·공식 사건을 유지하고 `hokkaido.1-6`, `je_karafuto`를 진행·성공 후속으로 연결 |
| `je_tenpo_crisis` | 바닐라 3개 버튼·목표·12년 timeout·공식 결과와 구호 실적 누적·결말 보상, `tenpo_famine.3-6`, `.99`를 유지. 기근 시작 안내 `.1`은 정의·호출·3개 언어 전용 현지화를 삭제하고 `.3`은 JE 개시 2개월 뒤 직접 예약. 구호소 관리 버튼 4개·구호소 modifier·니도메 `.2`는 후속 요청으로 삭제 |
| `je_bakufu_kaikaku/kaikoku/guntai/naibu/zaisei` | 현행 메이지 main·diplomacy·army·restoration·economy 조건에 대응하도록 완료·무효화·timeout을 갱신 |
| 7개 지역 막번 JE | 정의·history·on_action·사건·진행 막대·GUI·현지화 참조 삭제 |
| 8개 정책·청원 JE | 정의와 전용 버튼·GUI·trigger localization 삭제. 기존 성공·실패 사건은 청원 사건의 직접 후속으로 보존 |
| 독립 `je_tenpo_famine` | 삭제하고 바닐라 `je_tenpo_crisis`에 흡수 |
| `je_terakoya`, 옛 재벌 JE·사건, 옛 `je_hokkaido` | 활성 정의·참조가 없는 상태를 유지 |

## 3. 막번 충성도와 세금

지역 loyalty·independency·goryo 진행 바 대신 주 저택을 소유한 magnate의 실제 `loyalty`를 사용한다.

1. `je_meiji_restoration_update_daimyos`로 다이묘 소유 관계를 갱신한다.
2. `country_calculate_and_cache_daimyo_loyalties_per_state`로 각 주의 `cached_daimyo_loyalty`를 계산한다.
3. 복수 후보가 있으면 `prominence`가 가장 높은 인물을 선택한다.
4. 기존 사건의 loyalty 변화는 `add_eafp_japan_daimyo_loyalty`로 해당 인물에게 직접 적용한다.
5. 기존 autonomy 증가는 충성도 감소, autonomy 감소는 충성도 증가로 역변환한다.
6. 세금 누수는 매주 다음 식으로 다시 계산한다.

```text
세금 보존율 = 0.75 + 0.25 × clamp(loyalty, 0, 100) / 100
세금 누수율 = 0.25 × (1 - clamp(loyalty, 0, 100) / 100)
```

충성도 판정은 40 미만 불충, 40~65 중립, 65 초과 충성으로 scripted trigger를 제공한다.

## 4. 덴포 파벌 대응

| 바닐라 결과 | EAFP 파벌 |
|---|---|
| `tenpo_outcome_reformer_var` | 히토츠바시파·개혁파 |
| `tenpo_outcome_hardliner_var` | 난키파·보수파 |
| `tenpo_outcome_balanced_var` 또는 timeout | 양 파벌 균형 처리 |

`eafp_jap_tenpo_faction_result_applied`가 보상의 중복 적용을 막는다.

## 5. 4단계에서 추가·보존한 변수

| 변수 | 범위 | 목적 |
|---|---|---|
| `eafp_japan_daimyo_loyalty_adjustment` | character | legacy 사건이 저택 소유 다이묘에게 누적한 충성도 조정값 |
| `eafp_jap_bakufu_reform_timed_out` | country | 막부 개혁 main JE의 12년 timeout 기록 |
| `eafp_jap_restoration_finished`, `eafp_jap_restoration_failed` | country | 공식 유신 종료 결과 추적 |
| `eafp_jap_meiji_legacy_1_fired`, `eafp_jap_meiji_legacy_2_fired`, `eafp_jap_meiji_legacy_3_fired`, `eafp_jap_meiji_legacy_13_fired` | country | 유신·메이지·북방 legacy 후속 사건의 단발성 보장 |
| `eafp_jap_meiji_main_finished` | country | 메이지 main 완료 추적 |
| `eafp_jap_meiji_economy_finished` | country | 메이지 경제 완료 추적 |
| `eafp_jap_meiji_army_finished` | country | 메이지 군사 완료 추적 |
| `eafp_jap_meiji_diplomacy_finished` | country | 메이지 외교 완료 추적 |
| `eafp_jap_taming_north_completed`, `eafp_jap_taming_north_failed` | country | 북방 JE 성공·실패와 `je_karafuto` 접근 통제 |
| `eafp_jap_hokkaido_castle_chain_started`, `eafp_jap_hokkaido_1_fired` | country | 옛 홋카이도 사건 단발성 보장 |
| `eafp_jap_karafuto_started`, `eafp_jap_karafuto_event_resolved`, `eafp_jap_karafuto_closed` | country | `je_taming_the_north` 성공 뒤 가라후토 후속 JE의 개시·사건·종료 추적 |
| `eafp_jap_tenpo_famine_started` | country | 바닐라 덴포 JE에서 legacy 기근 트랙을 한 번만 초기화 |
| `eafp_jap_tenpo_oshio_followup_scheduled` | country | 공식 오시오 사건 뒤 EAFP 후속 중복 방지 |
| `eafp_jap_tenpo_famine_conclusion_scheduled` | country | 성공·timeout의 기근 정리 사건 중복 방지 |
| `eafp_jap_tenpo_faction_result_applied` | country | 바닐라 덴포 결과의 EAFP 파벌 보상 중복 방지 |
| `eafp_jap_currency_reform_commissioned/resolved` | country | 새 화폐 사건 체인 접수·종료 |
| `eafp_jap_water_reform_commissioned/resolved` | country | 중농치수 사건 체인 접수·종료 |
| `eafp_jap_domain_reform_commissioned/resolved` | country | 상지령 사건 체인 접수·종료 |
| `eafp_jap_purge_reform_commissioned/resolved` | country | 강기숙정 사건 체인 접수·종료 |

기존 `sukuigoya_for_tenpo`, `sukuigoya_for_tenpo_accumulation`, 바닐라 `ainu_friendship_var`, `cached_daimyo_loyalty`, `tenpo_outcome_*_var`는 새 변수가 아니라 보존·재사용한 상태다.

## 6. 인물 정본화

바닐라와 중복되는 EAFP 인물 템플릿 69개를 제거했다. history, on_action, event의 모든 활성 참조를 바닐라 정본 ID로 바꿨다. 전체 대응표는 [japan_legacy_character_identity_map.md](japan_legacy_character_identity_map.md)에 기록했다.

## 7. 정적 검증

- 변경된 활성 `.txt` 25개: 문자열·주석을 제외한 중괄호 균형 정상.
- `REPLACE:` 7개: EAFP delta 제거 후 바닐라 1.13.11 블록과 정규화 기준 일치.
- 세 언어 주 현지화: 중복 키 0개, 홀수 따옴표 0개, UTF-8 BOM 유지.
- 활성 `common/events/localization`에서 다음 참조 0개:
  - 7개 `je_bakuhantaisei_*`
  - 8개 `je_bakufu_seisaku_*`
  - `je_tenpo_famine`, `je_terakoya`, 옛 `je_hokkaido`
  - `goryo`, 지역 `independency`, `reduce_nidome*`
  - 옛 재벌 JE·사건
  - 제거한 EAFP 중복 인물 ID 69개
- 실제 게임 신게임·장기 관전 검증은 아직 실행하지 않았다.

## 8. 선택 P0 후속 구현

4단계 최초 구현 뒤 실제 엔진 로그에서 확인된 state key, 막부 데이터베이스, 존황양이 운동, `NIP`, 구식 문법, 다이묘 충성도 effect 문제 중 사용자가 선택한 1, 3, 4, 5, 6, 7번을 후속 수정했다.

구현 내역, 새 키, 변수 변화와 3차 로딩 검증 결과는 [japan_stage4_selected_p0_implementation_report.md](japan_stage4_selected_p0_implementation_report.md)에 기록했다.

## 9. 구호소 관리 버튼·니도메 삭제

- `install_sukuigoya_button`, `reduce_sukuigoya_button`, `expand_sukuigoya_button`, `close_sukuigoya_button`의 정의와 덴포 JE 연결, 영어·한국어·중국어 표시 문구를 삭제했다. 해당 4개 정의만 들어 있던 `common/scripted_buttons/eafp_tenpo_famine_buttons.txt`도 삭제했다.
- `tenpo_famine.2`(니도메) 이벤트 및 `.1`에서의 1개월 후 예약 호출을 삭제했다. `.1`에서 `.3`으로 이어지는 2개월 후 대이주 사건은 유지한다.
- 니도메 전용 `rice_export_ban_state_modifier`, `rice_export_ban_reduced_state_modifier`의 정의·결말 정리 코드·3개 언어 현지화도 함께 제거했다.
- 구호소의 자동 초기화, 월간 누적, 기근 종료 시 구호 보상은 유지했다. 바닐라 덴포 버튼 3개와 공식 결과, 나머지 EAFP 기근 사건도 유지했다.
- `.disable` 원본은 변경하지 않았으며 새 변수·migration·bridge 코드는 추가하지 않았다. 삭제한 콘텐츠는 Git 및 `.disable` 대조본에서 복구할 수 있다.
- 검증: 삭제한 버튼·이벤트·전용 수정치의 활성 참조 0건, 덴포 JE의 바닐라 버튼 3개 및 `.1`→`.3` 예약 유지, 수정한 게임 텍스트 6개의 UTF-8 BOM·CRLF 및 `.txt` 중괄호 개수 검사 통과, `git diff --check` 오류 없음. 이번 삭제 변경 후 실제 게임은 다시 실행하지 않았다.

## 10. 이국선타불령 증보·구호소 수정치 제거·시작 저널

### 10.1 이국선타불령

- 기존 국가 modifier를 삭제하고 `common/amendments/eafp_amendments_japan.txt`에 `amendment_eafp_ikokusen_uchiharairei`를 추가했다.
- 한국어 기준 ‘쇄국’은 `law_sakoku`이며 ‘고립주의’는 `law_isolationism`이다. 따라서 `allowed_laws`는 `law_sakoku`만 허용하고 이념 선호를 위한 `parent`만 상위법 `law_isolationism`을 사용한다.
- 기존 8개 효과 중 현행 엔진에서 유효하지 않은 `country_max_declared_interests_add = -5`를 제외한 7개를 같은 수치로 증보의 `modifier`에 옮겼다.
- 도입·폐지 버튼, 청원 선정 조건과 `eafp_japan.2301/.2306`의 수락 결과는 현행 무역법 scope의 증보를 직접 조회·추가·제거한다. 폐지는 해당 증보 type만 대상으로 하며 다른 증보는 건드리지 않는다. 쇄국을 떠났거나 이미 요청 상태가 바뀌었을 때는 수락 선택지가 유효하지 않다.
- 시작 시 지주 IG를 sponsor로 부착하며, 영어·한국어·중국어의 증보명·설명 및 버튼 설명을 갱신했다.

### 10.2 구호소 modifier 제거

- `modifier_sukuigoya_for_tenpo` 정의, 덴포 JE 시작 적용, `.99`의 제거 코드 및 3개 언어 표시 키를 삭제했다. 기존 버튼 삭제에 이어 구호소의 상시 보너스도 남지 않는다.
- 이번 요청은 ‘구호소’ modifier 제거이므로 기존 `sukuigoya_for_tenpo`, `sukuigoya_for_tenpo_accumulation`의 실적 계산과 별개인 `nomin_kyusai_modifier` 결말 보상은 유지했다.

### 10.3 신게임 시작 저널

- 후속 요청으로 초기화 위치를 `common/history/countries/jap - japan.txt` 마지막으로 옮겼다. 일본의 시작 법률·EAFP 초기값 설정 뒤 증보와 `je_bakuhantaisei`를 추가한다. 저널은 막부법 보유와 미등록을 확인하므로 중복 생성하지 않는다. 이전 전역 history 단계와 실행 시점이 달라졌으며, 이관 후 실제 신게임 초기 상태는 재검증이 필요하다.
- 저널의 기존 `immediate`가 다이묘 관계·충성도 캐시·세금 계산을 수행하고, 기존 기본 고정 표시 설정도 유지한다.
- 하루 뒤 `eafp_japan.1`은 안내 팝업으로만 유지했다. 그 이벤트에서 중복 초기화와 저널 추가를 제거해 저널 표시가 하루 진행에 의존하지 않도록 했다.
- 새 영구 변수, bridge trigger/effect 또는 세이브 migration은 추가하지 않았다. `.disable` 대조본은 변경하지 않았다.

### 10.4 검증

- 수정·추가한 게임 텍스트 12개: UTF-8 BOM + CRLF 및 `.txt` 중괄호 개수 검사 통과.
- 활성 스크립트·현지화의 `ikokusen_uchiharairei_modifier`, `modifier_sukuigoya_for_tenpo` 참조 0건. 신규 증보 정의 1개, 제목·설명은 3개 언어에 각각 1개씩 존재한다.
- EAFP 단독·전체 DLC·`-debug_mode`로 데이터베이스와 메인 메뉴를 로드했다. 신규 증보·초기화 파일·수정 버튼·청원 이벤트를 가리키는 오류는 0건이다. 로그는 `scratch/japan_sakoku_amendment_qa/after_error.log`, `after_game.log`, `after_debug.log`에 보존했다.
- 기존 다른 static modifier·인물·GUI 등 오류는 남아 있다. 일본 신게임 선택 직후 저널 표시 및 실제 증보 도입·폐지 클릭은 직접 검증하지 않았다.
- 검증 전 로그를 `before_*`로 보존했다. 실행 종료 후 원래 플레이셋을 백업과 동일한 SHA-256으로 복원했다.

## 11. 바닐라 일본 국가 history 전문 병합

### 11.1 파일 구성과 표시

- 바닐라 1.13.11의 `common/history/countries/jap - japan.txt` 전문을 모드의 같은 경로에 복사하고, 기존 활성 `eafp_japan_legacy.txt`에 남아 있던 EAFP 효과를 병합했다.
- 파일 상단에 바닐라 원본 SHA-256과 한글 주석 표시 규칙을 적었다. `# 수정: …` / `# 수정 끝` 1개 구간은 군부 이념·IG 명칭·유교 국교 변경이며, `# 추가: …` / `# 추가 끝` 6개 구간은 부패 수정치·시작 안내 사건·기근 및 다이묘 수정치·역사 사건 예약·파벌 초기값·시작 증보 및 막번 저널이다. 주석 한글화에서는 실행 코드를 변경하지 않았고, 그 뒤 별도 요청으로 전역 초기화 구간을 추가 이관했다.
- 바닐라의 기술, 세율, 시작 법률, 경찰 제도, 지주 집권 설정, DLC 시작 저널·사건·기근 효과는 삭제하지 않았다. 현재 EAFP 변경 효과는 그 원문 뒤에 명시적으로 적용한다.
- 중복 실행을 막기 위해 활성 분리 파일 `eafp_japan_legacy.txt`를 제거했다. 그 내용은 병합 파일에 모두 보존되어 있으며 Git에서도 복구할 수 있다.
- `common/history/global/eafp_japan_start.txt`의 증보 부착·막번체제 저널 등록 본문을 국가 파일 마지막으로 이관하고 전역 파일은 제거했다. 기존 법률·중복 방지 조건과 `PREV.ig:ig_landowners` 후원자 scope를 유지한다. 하루 뒤 안내 사건에는 초기화를 추가하지 않는다.

### 11.2 옛 원본 대조와 제외 사항

`.disable` 원본도 대조했지만 앞선 리뉴얼에서 폐기한 초기화를 다시 넣지 않았다. 옛 고립주의·무학교·변경 식민화 및 제도 설정으로 현행 쇄국·테라코야·에도 사회제도를 되돌리지 않는다. 삭제한 지역 막번 JE, 테라코야 JE, 독립 기근·홋카이도 JE와 전용 수정치도 복원하지 않는다. 옛 이국선타불령 modifier 대신 직전 구현의 쇄국 증보를 유지한다.

### 11.3 검증

- 표시된 7개 EAFP 구간 제거 후 주석·공백을 정규화하면 설치된 바닐라 일본 country history 전체와 일치한다.
- 기존 6개 구간의 예약 사건 ID·지연시간과 변수 초기값은 보존했다. 새 마지막 구간은 이관 직전 전역 초기화 파일의 일본 국가 scope 본문과 주석·공백 정규화 기준으로 일치한다.
- `.disable` 원본은 그대로 보존했고, 전역 초기화 파일은 국가 파일로 내용 이관 후 제거했다.
- UTF-8 BOM·CRLF, 중괄호 개수 및 `git diff --check` 검사 통과. 새 변수·bridge·migration 코드 없음.
- 국가 파일 병합 및 전역 초기화 이관 뒤 실제 게임은 재실행하지 않았다. 직전 증보 작업의 로딩 로그를 이번 변경의 검증 결과로 재사용하지 않는다. 신게임의 증보 부착·막번 저널 표시와 저널 `immediate`의 다이묘·충성도·세금 초기값을 확인해야 한다.
