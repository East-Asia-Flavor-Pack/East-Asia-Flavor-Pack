# 2026-11-07 오류 수정 적용 기록

기준: `587a62ca`, [분석 계획](error_fix_plan_2026-11-07_1844.md)의 A2·A3·A5·B1~B5.
상태: 소스 수정과 정적 검증 완료. 게임을 재시작한 런타임 검증은 미실행.

## 적용 내용

| 항목 | 수정 결과 |
|---|---|
| A2 일본 초기화 | 지역 충성도의 지주 IG 접근을 선택적 스코프로 변경했다. 국가 history 후 기존 GLOBAL 갱신 경로가 남아 있으므로 IG가 없을 때 건너뛴 보정은 그 경로에서 계산한다. 이에나리 양위 사건은 군주 존재를 명시적으로 확인하고 군주 스코프에 안전하게 접근한다. |
| A3 무효 참조 | 폐번치현 완료 조건은 기존 `japan_daimyo_abolished` 전역 변수로 직접 검사한다. 조선 군주 사망 설명 분기에서 없는 `building_gaudi_gyeong` 참조 2개를 제거했고, 완성된 경복궁의 기존 판정은 유지한다. 동학 선동가 이념에서 비활성 종교 `rel:donghak`의 국교 판정을 제거하고 기존 종교 자유 법률 조건을 유지한다. |
| A5 진행 막대 | `double_sided_bad`를 1.15의 명시적 빨강/금색 텍스처·glow·marker 필드로 변경했다. 기존 진행 계산과 양쪽 설명을 유지한다. |
| B1 저널 | 112개에 `activation_description`을 추가했다. 자동 등록 36개는 기존 `possible`의 조건을 그대로 표시한다. 나머지 76개는 사용자 요청에 따라 툴팁 없이 `activation_description = { always = yes }`를 사용한다. 앞서 추가한 전용 현지화 파일 3개는 다른 참조가 없음을 확인하고 제거했다. 실제 등록 조건이나 실행 경로는 변경하지 않는다. |
| B1 목표 문구 | 누락된 선교·유학생 파견·이화원 목표 문구를 추가했다. 더 이상 쓰이지 않는 구형 `_goal` 키 13종을 세 언어에서 제거했다. 현재 참조 중인 4종은 `_objective_tt`로 이름을 바꾸고 스크립트와 현지화 참조를 함께 갱신하여 implicit goal 경고를 피했다. |
| B2 현지화 구문 | 원본 로그가 지목한 EAFP 키·삽입문 132개 조합을 기준으로 세 언어의 데이터 표현식 내부 인용을 수정했다. 총 388회 키/삽입문 수정이며, 같은 줄에 여러 치환이 포함될 수 있다. `ijo_information`의 과다 닫는 괄호 2곳도 세 언어에서 수정했다. 제외된 바닐라 파일의 인용 경고는 손대지 않았다. |
| B3 누락 현지화 | 확장 GUI, 간도 버튼·툴팁, 신문화 진행도, 저널 제목·설명·목표, 특성 슬롯과 디버그 사건에 35개 키를 언어별로 추가했다. 무조건 활성화 설명의 툴팁을 제거한 뒤 언어별 신규 키는 35개다. |
| B3 해시 충돌 | 모드의 `japan_invasion.5.t`를 `japan_invasion.5.eafp_title`로 세 언어에서 변경했다. 현재 활성 사건에는 이전 제목 키의 호출이 없음을 확인했다. 바닐라 인명 키는 유지한다. |
| B4 DNA | 8개 얼굴의 기존 모든 gene 데이터를 보존하면서 `gene_asian_east = { "asian_east" 0 "asian_east" 0 }`를 추가했다. 1.15 바닐라 DNA의 이행 방식 및 morph 곡선에서 확인한 중립 값으로 추가 변형을 주지 않도록 했다. |
| B5 몽골 | 국가 history와 중국 통치 JE 종료의 두 등록 경로에 이미 활성화된 복국 JE가 있는지 검사한다. 기존 시작 변수와 경로는 유지하며 새 변수나 helper는 추가하지 않는다. |

새 scripted effect·scripted trigger·이벤트 훅·게임 상태 변수는 추가하지 않았다. 기존 함수 본문과 호출 위치를 수정했다. 게임 텍스트는 UTF-8 BOM·CRLF를 유지했다.

## 제외 항목

사용자 지정에 따라 A1(장군부 history), A4(정당·외교 행동 INJECT), A6(도자기 명품 한도), C1(이벤트 중복), CMF·바닐라/로드 환경은 수정하지 않았다. 해당 오류가 새 로그에도 남을 수 있다.

B5에 필요한 `common/history/countries/mgl - china.txt`의 JE 등록 검사만 수정했다. 주·POP·건물·부대 history와 소유권은 변경하지 않았다. 몽골 종속관계의 시작 순서 자체를 재설계한 것은 아니므로 신규 게임에서 JE의 유지 여부를 확인해야 한다.

## 검증

다음 검사가 통과했다.

```powershell
python -B tools/validate_115_log_fixes.py --game "D:/SteamLibrary/steamapps/common/Victoria 3/game" --log "$env:USERPROFILE/Documents/Paradox Interactive/Victoria 3/logs/error.log"
python -B tools/validate_115_p0.py --game "D:/SteamLibrary/steamapps/common/Victoria 3/game"
python -B tools/validate_115_p2.py --game "D:/SteamLibrary/steamapps/common/Victoria 3/game"
python -B tools/validate_formosa_expedition.py
python -B tools/validate_boshin_international_journal.py
git diff --check
```

새 검사기는 112개 활성화 설명, 36개 기존 조건의 동일성, 세 언어의 132개 오류 조합·괄호·새 키, DNA와 막대 에셋, 초기화·저널 중복 방지 및 무효 참조 제거를 확인한다. 대만 원정 검사는 표시되지 않는 구형 `_goal` 키가 있어야 한다던 요구를 제거하고, 해당 JE가 구형 목표 카운터를 사용하지 않으며 중복 키도 없음을 검사하도록 갱신했다.

별도로 확인한 보존 사항:

- 새 현지화 키 35개가 각 언어에서 한 번씩만 정의된다.
- DNA 8개의 기존 데이터는 추가 gene을 제외하면 토큰 단위로 동일하다.
- JE 파일 36개 중 실제 게임 조건을 고친 메이지 유신·중국 통치 2개를 제외한 34개는 표시 필드 및 툴팁 키 변경 외에 게임 데이터가 동일하다.
- 제외한 경로와 `.disable` 파일은 변경하지 않았다.

P1 전체 검사와 과거 직위/폐번치현/지역 콘텐츠 검사의 기존 실패를 이번 작업으로 해결했다고 집계하지 않는다.

## 남은 실행 확인

새 게임을 시작해 초기 IG·군주 접근 오류와 몽골 JE 중복 오류가 사라지는지 확인한다. 조건이 있는 저널의 활성화 설명, 신문화 진행도, 막부 개혁 막대의 양쪽 색/마커와 DNA 8개를 화면에서 확인한다. 한국어·영어·간체 중국어 각각에서 누락 키·인용 오류를 확인한다. 한 달 경과 및 저장·재로드 후에도 같은 결과인지 점검한다.

원본 error.log는 이전 실행의 기록이며 수정 후 실행 결과가 아니다. 이번 검사기는 해당 로그를 회귀 대상 목록으로 사용했고, 로그를 지우거나 덮어쓰지 않았다.
