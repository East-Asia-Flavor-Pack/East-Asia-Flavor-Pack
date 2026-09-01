# 일본 바닐라 호환성 기준선

> **상태 변경(2026-09-01):** 이 문서는 0단계 조사 기준선으로만 보존한다. 현재 구현은 바닐라 호환 bridge를 사용하지 않고 EAFP 신게임 직접 소유 방식으로 전환되었다. 현행 구현 계약은 [`japan_stage3_bridge_report.md`](japan_stage3_bridge_report.md)를 따른다.

## 1. 기준

| 항목 | 값 |
|---|---|
| 조사일 | 2026-09-01 |
| 게임 버전 | Victoria 3 `1.13.11` |
| Steam 빌드 | `24799966` |
| 게임 데이터 | `D:/SteamLibrary/steamapps/common/Victoria 3/game` |
| 모드 | East Asia Flavor Pack `2.2.0` |
| DLC 전제 | 모든 공식 DLC 활성, `The Great Wave` 필수 |
| 세이브 지원 | 리뉴얼 적용 후 시작한 신게임만 지원, 이전 EAFP 세이브 migration 미지원 |

이 문서는 일본 리뉴얼 0단계의 바닐라 기준선이다. 아래 SHA-256이 달라지면 일본 호환 패치를 그대로 배포하지 않고 소유권·필드·이벤트 연결을 다시 대조한다.

## 2. 콘텐츠 소유권

| 영역 | 바닐라 정본 | EAFP 구현 경계 |
|---|---|---|
| 쇄국·개항 | `je_sakoku` | 옛 개항 사건은 선행·후속 풍미만 담당 |
| 덴포 위기 | `je_tenpo_crisis`, `tenpo_events` | `je_tenpo_famine`을 제거하고 사건만 바닐라 JE에 병합 |
| 메이지 유신 | `je_meiji_restoration`, `je_meiji_main/economy/army/diplomacy`, `meiji`, `ep2_meiji` | 네 메이지 JE는 바닐라 정의로 최신화하고 EAFP 사건 연결만 추가 |
| 보신전쟁 | `ep2_meiji` | EAFP JE는 전황·후속 사건만 담당하고 내전 생성·종전은 바닐라 소유 |
| 북방 | `je_taming_the_north` | 옛 `je_hokkaido`는 삭제하고 `hokkaido.2-6`은 바닐라 JE 진행 중에, `hokkaido.1`과 `je_karafuto`는 바닐라 JE 성공 뒤에만 이어지도록 연결 |
| 종교 | `je_shinbutsu_bunri`, `je_elevate_buddhism` | 옛 신토 체인은 사회 반응만 담당 |
| 재벌 | `je_zaibatsu`와 바닐라 공식 회사 | 옛 EAFP 재벌 JE·청원·사건은 제거하고 바닐라 체인만 사용 |
| 류큐 | `je_ryukyu_rivalry`, `ryukyu_rivalry` | 조선 개입과 옛 처분 사건만 별도 연결 |
| 이와쿠라 | `je_iwakura_mission`, `iwakura_mission` | 중복 JE를 만들지 않고 옛 외교 사건을 후속으로 연결 |
| 조선 식민화 | `je_colonize_korea` | 정한론은 정치적 선행·반발만 담당 |
| 다이묘 | 바닐라 magnate, `building_manor_house`, `daimyo_var`, `cached_daimyo_loyalty` | 지역 JE 없이 저택 보유자 충성도로 세금·정치 반응 계산 |
| 일본 인물 | `common/character_templates/country_jap.txt` | 동일 인물 EAFP 템플릿 제거 후 바닐라 정본 참조 |
| 일본 회사 | `company_mitsui`, `company_mitsubishi`, `company_mantetsu`, `company_sumitomo`, `company_yasuda` | 중복 회사 정의 금지, EAFP 고유 회사만 유지 |

## 3. 핵심 바닐라 JE 위치

| 키 | 원본 위치 |
|---|---|
| `je_meiji_restoration` | `common/journal_entries/00_meiji_restoration.txt:1` |
| `je_meiji_main` | `common/journal_entries/00_meiji_restoration.txt:640` |
| `je_meiji_economy` | `common/journal_entries/00_meiji_restoration.txt:744` |
| `je_meiji_army` | `common/journal_entries/00_meiji_restoration.txt:792` |
| `je_meiji_diplomacy` | `common/journal_entries/00_meiji_restoration.txt:851` |
| `je_ryukyu_rivalry` | `common/journal_entries/01_ryukyu_rivalry.txt:1` |
| `je_taming_the_north` | `common/journal_entries/07_hokkaido.txt:1` |
| `je_iwakura_mission` | `common/journal_entries/07_iwakura_mission.txt:1` |
| `je_shinbutsu_bunri` / `je_elevate_buddhism` | `common/journal_entries/07_japanese_religion.txt:1,155` |
| `je_colonize_korea` | `common/journal_entries/07_korea_colonization.txt:1` |
| `je_sakoku` | `common/journal_entries/07_sakoku.txt:1` |
| `je_tenpo_crisis` | `common/journal_entries/07_tenpo_crisis.txt:1` |
| `je_zaibatsu` | `common/journal_entries/07_zaibatsu.txt:1` |

## 4. 바닐라 파일 체크섬

| 상대 경로 | bytes | SHA-256 |
|---|---:|---|
| `common/journal_entries/00_meiji_restoration.txt` | 17136 | `aaaf94eb3c4acd16e2985381ef68f6cd1cf1ca8fa012002ad2305c24faa135d0` |
| `common/journal_entries/01_ryukyu_rivalry.txt` | 6102 | `acb43f7f590803e0bfd868b89b9af931be0a44da4ee8d8e35a29b68b8ce0c743` |
| `common/journal_entries/07_hokkaido.txt` | 8276 | `867af26f75e9e3b4f90c603ddbf0e7b357eb57fb6b92ac0f7989b7756436724d` |
| `common/journal_entries/07_iwakura_mission.txt` | 3075 | `15bad277059552d795fcc66843af4fc2d28b1baa33a789cf751ac778a2d93f4f` |
| `common/journal_entries/07_japanese_religion.txt` | 4180 | `7e4b96f4ea5134a1983de2fde8b16c60f3127fc40caf5acd038ea9a2c1a90234` |
| `common/journal_entries/07_korea_colonization.txt` | 5992 | `48f246262ac93d7d722608d8e31e3a81bd75d423c4b2c340e575142e287a3eb8` |
| `common/journal_entries/07_sakoku.txt` | 2211 | `142e4e23eec9d7667900a07a36016434dd53828492ad7ee829a84c7205b1f95e` |
| `common/journal_entries/07_tenpo_crisis.txt` | 2833 | `37e7bf5859dd585d512cfe0b39e7383765598b7e8b69d4d4bd48afbb76c90ac2` |
| `common/journal_entries/07_zaibatsu.txt` | 8793 | `cbcade9b9f356123356bc720d4bd2ade815cceae21076fdb01d705f630e1f94d` |
| `common/character_templates/country_jap.txt` | 68852 | `a727ba61139ffd2ed58419cced1ab0c8d52147cafc6f1eb4f6347922c249c864` |
| `common/company_types/00_companies_ep2.txt` | 25850 | `d36e4b2ff7d3094764f33f66e908bfbe029487b6eb4960b198d35d86cb0184c6` |
| `common/company_types/00_companies_japan.txt` | 5133 | `f626e624c2ae3ec808d8e550b108b85a7f3af51659f57ed9a316cce96b02904e` |
| `common/script_values/ep2_japan_values.txt` | 7439 | `fbe8069966e67a2b73a9bb7672a219092b19cea0aba3c857813deade510cca9e` |
| `common/scripted_effects/00_victoria_ep2_scripted_effects.txt` | 68775 | `5eb6dca67e7647b4d09dbeb1c22e0ab2b68cee66c04a7476375c581f074191dc` |
| `events/japan_events/ep2_tenpo_events.txt` | 20456 | `84d87db2c927a7f97b79325b38b2650bd35d8c52e33c574f3ab18d7770b76003` |
| `events/japan_events/ep2_meiji_restoration.txt` | 43873 | `358d0b9d3b8b356f102e14caf469f873087f2ee657768a5ef6aa64f4101084bb` |
| `events/japan_events/ryukyu_rivalry_events.txt` | 13725 | `03f59c6e72f243183246c144426502c4620f02dbe9bf400fd61964daef9560b0` |
| `events/japan_events/ep2_iwakura_events.txt` | 21366 | `d4f381ba27a95f16355ae8e68e759b4afa170f2b846064f762038c0e7c166d93` |
| `events/japan_events/ep2_zaibatsu_events.txt` | 4489 | `1fcb83e0315490e4a01d8357d20ef3234bde8a24f6bda4e80b20f14e7168515e` |
| `events/meiji_restoration.txt` | 30495 | `5e010ebc08631a2c18921792a768d9510cb3b117be961fb0f762597c537144b0` |

## 5. EAFP 활성 충돌 기준선과 P0 결과

| 파일 | 충돌 | 0단계 판정 | 2단계 결과 |
|---|---|---|---|
| `common/country_definitions/eafp_countries.txt` | `REPLACE:JAP` | 국가 정의 전체 교체 제거 또는 최소 초기화 effect로 전환 | 일본 블록 제거, 바닐라 정본 사용 |
| `common/flag_definitions/eafp_jap_flag_definitions.txt` | `REPLACE:JAP` | 바닐라 국기 분기 복구 | 일본 블록 제거, 바닐라 정본 사용 |
| `common/cultures/00_cultures_jap.txt` | `REPLACE:japanese` | 현행 바닐라 필드를 보존하는 생성형 패치 또는 교체 제거 | 바닐라 비인명 필드 + 안정적 이름 합집합으로 재생성 |
| `localization/english/replace/jap_replace_l_english.yml` 및 두 언어 대응 파일 | 바닐라 메이지 문자열 직접 교체 | 옛 문구 이관 후 직접 덮어쓰기 제거 | canonical 메이지·국가명 키 제거 |
| `common/journal_entries/eafp_01_ryukyu_rivalry.txt` | 바닐라 `je_ryukyu_rivalry` 재정의 | 조선 개입 사이드카로 분리 | `je_eafp_ryukyu_intervention`으로 분리 |
| `common/journal_entries/eafp_japan.txt` | 바닐라 `je_zaibatsu` 재정의 | 옛 재벌 체인 완전 삭제 | 옛 JE 4개·이벤트·전용 자산 제거, 바닐라 정본만 유지 |
| `common/company_types/eafp_companies_japan.txt` | 일본 공식 회사 재정의·중복 | 바닐라 정본 복구 | 공식 회사 4개 제거, EAFP 고유 회사 2개만 유지 |
| `common/history/military_formations/06_military_formations_asia.txt` | 바닐라 동경로 전체 복사 | EAFP 추가분만 별도 파일로 분리 | 원본 경로 제거, 조선 추가분을 EAFP 파일로 분리 |
| `common/history/countries/jap - japan.txt` | 바닐라 동경로 전체 복사 | 바닐라 국가 history 복구 | 원본 경로 제거, EAFP 추가 effect를 legacy 파일로 분리 |
| `events/meiji_restoration.txt` | 바닐라 동경로 전체 복사·namespace 충돌 | 옛 이벤트 namespacing | EAFP legacy 경로와 `eafp_jap_meiji_legacy`로 분리 |

## 6. 갱신 규칙

1. 바닐라 패치 후 위 20개 파일의 SHA-256을 다시 계산한다.
2. 하나라도 달라지면 해당 파일의 JE·이벤트·변수·인물·회사 필드를 semantic diff한다.
3. 바닐라 소유 키를 EAFP가 재정의하는 예외는 기준 버전, 원본 체크섬, 변경 필드와 회귀 시험을 기록해야 한다.
4. 모든 공식 DLC 활성 환경만 검증한다.
