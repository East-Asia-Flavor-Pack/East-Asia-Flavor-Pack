# 일본 콘텐츠 리뉴얼 4단계 구현 보고서

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
| `je_tenpo_crisis` | 바닐라 3개 버튼·목표·12년 timeout·공식 결과에 구호소 버튼과 `tenpo_famine.1-6/.99`를 병합 |
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
