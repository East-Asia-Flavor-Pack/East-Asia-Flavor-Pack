# 일본 콘텐츠 2단계 P0 충돌 제거 보고서

## 1. 판정

2단계의 목표였던 바닐라 일본 정본 복구를 완료했다. Victoria 3 1.13.11과 모든 공식 DLC를 기준으로 EAFP만 활성화한 초기 로드에서 다음 P0 충돌은 모두 0건이다.

- `je_ryukyu_rivalry`, `je_zaibatsu`, `company_sumitomo` duplicated key
- EAFP의 `REPLACE:JAP`, `REPLACE:je_meiji_*`, `REPLACE:je_terakoya`
- EAFP `events/meiji_restoration.txt`와 아시아 군사 편제·일본 국가 history의 바닐라 동일 경로 가림
- `je_terakoya` 정의·시작 호출·전용 수정치 참조
- 옛 조선 함대의 `Combat units are not applicable for fleets` 오류
- 이번 단계에서 생성·이동한 파일의 UTF-8 BOM 경고

P0는 바닐라 정본 소유권 충돌을 제거하는 단계이므로, 전면 복원된 옛 일본 콘텐츠의 구형 이념·지역·JE group·건물·localization 오류는 후속 단계 backlog로 유지한다. 따라서 이 보고서의 완료 판정은 모드 전체 오류 0건을 뜻하지 않는다.

## 2. 실행 환경

| 항목 | 값 |
|---|---|
| 최종 실행 시각 | 2026-09-01 01:51 KST |
| 실행 파일 | `victoria3_win_console.exe -debug_mode` |
| 게임 버전 | Victoria 3 `1.13.11`, Git revision `15aa89ae42` |
| 활성 모드 | EAFP만 활성화 |
| DLC | 모든 공식 DLC 활성화 (`disabledDLC = []`) |
| 런처 설정 | 실행 전 백업, 검증 종료 후 원래 EAFP + Workshop `3385002128` 설정으로 복원 |
| 데이터베이스 초기화 | 이벤트·JE·history PostValidate와 localization 초기화 완료 후 로그 보존 |

## 3. 충돌 소유권 이관표

| 충돌 자산 | 바닐라 정본 | EAFP P0 결과 |
|---|---|---|
| 메이지 핵심 JE | `je_meiji_restoration`, `je_meiji_main/economy/army/diplomacy` | 모든 `REPLACE:` 정의 제거. 옛 진행형 JE 하나만 `je_eafp_jap_legacy_meiji_restoration`으로 분리 |
| 메이지 이벤트 | `events/meiji_restoration.txt`, `meiji.1-14` | 옛 13개 이벤트를 `events/eafp_jap_events/eafp_meiji_restoration_legacy.txt`, `eafp_jap_meiji_legacy.1-13`으로 이동 |
| 데라코야 | 바닐라 1.13.11에는 해당 JE 없음 | `je_terakoya`, history 시작 호출, 두 전용 수정치 참조를 제거하고 대체 JE를 만들지 않음 |
| 일본 국가 | 바닐라 `JAP` | `REPLACE:JAP` 국가 블록 제거 |
| 일본 국기 | 바닐라 `JAP` flag definition | `REPLACE:JAP` 국기 블록 제거. EAFP 국기 자산 파일은 삭제하지 않음 |
| 일본 문화 | 바닐라 `japanese` 비인명 필드 | 유일한 허용 예외 `REPLACE:japanese`를 생성기로 재구성하고 네 이름 배열만 합집합 처리 |
| 류큐 경쟁 | 바닐라 `je_ryukyu_rivalry` | 조선 버튼과 결과만 `je_eafp_ryukyu_intervention` sidecar로 분리 |
| 재벌 | 바닐라 `je_zaibatsu` | 옛 재벌 JE·청원 JE 3개·이벤트 4개와 전용 trigger·modifier·localization을 제거 |
| 일본 공식 회사 | 바닐라 `company_mitsui`, `company_mitsubishi`, `company_mantetsu`, `company_sumitomo` | EAFP 정의·`REPLACE:` 제거. `company_zohiko`, `company_daiichi_kokuritsu_bank`만 EAFP 고유 회사로 유지 |
| 아시아 군사 편제 | 바닐라 `06_military_formations_asia.txt` | 동일 경로 파일 제거. 조선 추가분만 `eafp_korea_military_formations.txt`로 분리 |
| 일본 국가 history | 바닐라 `jap - japan.txt` | 동일 경로 파일 제거. EAFP 추가 effect만 `eafp_japan_legacy.txt`로 분리 |

## 4. 주요 구현 내용

### 4.1 메이지와 데라코야

- 바닐라 메이지 JE 5개의 EAFP 정의를 제거했다.
- 옛 `je_meiji_restoration`은 바닐라 결과 변수·영토 effect를 직접 쓰지 않는 비활성 legacy companion으로 바꿨다.
- 옛 메이지 이벤트 13개는 바닐라 파일과 별도 경로·namespace로 이동했다.
- `replace/jap_replace` 3개 언어 파일에서 `dyn_c_japan_shogunate`, `je_meiji_main`, `meiji.*` 직접 덮어쓰기를 제거했다.
- legacy JE의 제목·설명·목표는 `je_eafp_jap_legacy_meiji_restoration*` 키로 분리했다.
- `je_terakoya`와 `modifier_jap_terakoya`, `modifier_legacy_of_terakoya`는 활성 정의·참조에서 제거했다.

### 4.2 류큐와 재벌

- 류큐 sidecar는 조선만 관여하도록 `should_be_involved`를 제한했다.
- sidecar 버튼은 바닐라 류큐 진행 막대에 제한된 진행도만 전달하며 일본·청의 공식 승패 effect를 소유하지 않는다.
- 조선의 독립적인 100 진행도 결과와 대만 개척 연결만 EAFP sidecar가 처리한다.
- 옛 재벌 JE와 청원 JE 3개를 활성 journal 파일에서 제거했다.
- 활성 `eafp_zaibatsu_events.txt`, `zaibatsu_events.1-4` 호출, 고아 `.101` localization을 제거했다.
- 전용 `is_zaibatsu_company` trigger와 `zaibatsu_cooperation_modifier`를 제거했으며, 원본 `.disable`은 회귀 대조본으로 보존했다.

### 4.3 문화 생성 패치

[`tools/generate_japanese_culture_patch.py`](../tools/generate_japanese_culture_patch.py)가 다음 규칙으로 일본 문화 파일을 생성한다.

- 바닐라 기준 파일: `common/cultures/00_cultures.txt`
- 바닐라 SHA-256: `30c8a1085257fb130634d3e5cc187d2eef7717a07db5fa7b390846dd319e5baa`
- 모든 비인명 필드와 일본 외교조약 인장 texture는 바닐라 원문을 사용한다.
- 이름 수량: 남성 이름 852, 여성 이름 125, 귀족 성씨 921, 일반 성씨 946
- 바닐라 이름 누락 0, 기존 EAFP 이름 누락 0, 대소문자 정규화 중복 0
- 생성 파일은 Victoria 3 요구 형식인 UTF-8 BOM으로 저장한다.

### 4.4 history 분리

- 바닐라 아시아 편제와 일본 국가 history의 동일 경로 가림을 제거했다.
- 조선 함대는 구형 `combat_unit_type_frigate` 대신 `ship_type:ship_type_frigate`를 사용한다.
- 일본 history의 바닐라 법률·기술·공식 JE 시작부는 바닐라 파일에 맡겼다.
- EAFP 옛 지역 JE·덴포 기근 JE·사건 예약·초기 변수는 후속 단계 이관을 위해 별도 legacy history에 남겼다.

## 5. 정적 검증 결과

| 검사 | 결과 |
|---|---:|
| `REPLACE:JAP` | 0 |
| `REPLACE:je_meiji_*`, `REPLACE:je_terakoya` | 0 |
| 활성 `je_terakoya` 및 전용 수정치 참조 | 0 |
| EAFP `je_ryukyu_rivalry`, `je_zaibatsu`, 일본 공식 회사 정의 | 0 |
| EAFP 옛 재벌 JE 4개·`zaibatsu_events`·전용 지원 자산 참조 | 0 |
| `namespace = meiji` | 0 |
| `eafp_jap_meiji_legacy.*` 이벤트 정의 | 13 |
| `je_eafp_ryukyu_intervention` 정의 | 1 |
| `je_eafp_jap_legacy_zaibatsu` 정의 | 0 |
| `REPLACE:japanese` | 1 |
| P0 수정 스크립트 중괄호 불균형 | 0 |
| 원본 `.disable` manifest SHA-256 불일치 | 0 / 53 |
| `git diff --check` 공백 오류 | 0 |

## 6. 초기 로드 전후 비교

| 항목 | 1단계 기준선 | P0 최종 |
|---|---:|---:|
| `Duplicated key je_ryukyu_rivalry` | 1 | 0 |
| `Duplicated key je_zaibatsu` | 1 | 0 |
| `Duplicated key company_sumitomo` | 1 | 0 |
| `je_terakoya` 오류·참조 | 존재 | 0 |
| 구형 조선 함대 combat unit 오류 | 존재 | 0 |
| P0 생성·이동 파일 BOM 경고 | 해당 없음 | 0 |
| `database_conflicts.log` | 0 bytes | 0 bytes |

최종 `game.log`에서 바닐라 `events/meiji_restoration.txt`가 14개 이벤트를, EAFP legacy 파일이 별도로 13개 이벤트를 로드한 것을 확인했다.

## 7. 후속 단계 backlog

최종 `error.log`는 966줄이며 timestamp가 있는 메시지는 882개다. 다음은 P0 소유권 충돌과 별개의 전면 복원 잔여 오류다.

| 잔여군 | 최종 로그 관측 | 처리 단계 |
|---|---:|---|
| 옛 막부 파벌 이념 ID | 56 | 3·4단계 adapter |
| `region_japan` | 14 | 3·4단계 현행 strategic region 이관 |
| `je_group_bakuhantaisei` | 8 | 4단계 지역 JE 제거 |
| `japan_historical_names_l_korean.yml` 자체 중복 | 177 | 8단계 localization 정리 |
| 다른 옛 일본 이벤트의 `has_port` | 6 | 5~8단계 사건 현행화 |
| 일본·조선 옛 building history | 2 | 각 국가 후속 현행화 |

`common/history/characters/jap - japan.txt`는 바닐라와 같은 상대 경로로 남아 있는 유일한 일본 파일이다. 중복 인물 정본화가 8단계 범위이므로 P0에서 임의 병합하지 않고 승인된 임시 예외로 기록한다. 8단계에서는 바닐라 인물 history를 복구하고 EAFP 고유 인물만 별도 파일로 분리해야 한다.

## 8. 보존 로그

| 파일 | bytes | SHA-256 |
|---|---:|---|
| `japan_p0_error.log` | 132180 | `5c3a3e93e1e22dd00c18ddc8e874460eea06309f2551ea08acf1a5ee16e9dbca` |
| `japan_p0_debug.log` | 333391 | `c997722d977f9f92328cc3e6585761902db8565bc420c39a76ed3b9ba79d74fa` |
| `japan_p0_game.log` | 110255 | `6a69fc2c8255706e276f1c38a0fc2047b622aacf5fffa54a1f7ead4b17c24ecf` |
| `japan_p0_database_conflicts.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

이번 최종 실행에서는 `debug.log`가 회전되지 않았으므로 단일 파일만 보존했다.
