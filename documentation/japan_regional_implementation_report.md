# 일본 막번체제 주별 통치 구현 보고

작성일: 2026-09-06  
상태: 코드 반영·정적 검증·엔진 DB 검사 완료. DB 전체에는 기존 오류가 남으며, 신게임 플레이·화면 검증은 미완료.

## 반영한 최종 결정

기존 `je_bakuhantaisei` 하나가 도호쿠·간토·호쿠신에쓰·도카이·교토·간사이·주고쿠·시코쿠·규슈의 충성도(L)와 독립성(I)을 관리한다. 별도 주별 JE를 만들지 않았다. 고료 저장값·계산·버튼·비용·UI는 추가하지 않았으며 활성 지역 경로에 고료 식별자가 없는 것을 검사했다.

L/I 원본은 JAP의 지역 접미사별 국가 변수다. 주 L은 다이묘 인물 평균과 독립적이다. 바닐라 `country_calculate_and_cache_daimyo_loyalties_per_state`를 호출하면 원본 바닐라 처리를 거친 뒤, 관리 중인 실제 주의 `cached_daimyo_loyalty`를 EAFP L로 덮어쓴다. 다이묘가 없어도 관리 주의 캐시는 유지한다. 실제 인물 충성도는 주 L 변경으로 자동 변경하지 않는다.

## 주요 파일과 실행 흐름

| 파일 | 역할 |
|---|---|
| [지역 effects](../common/scripted_effects/eafp_japan_regional_effects.txt) | 최초 초기화, 캐시 덮어쓰기, 월간 L/I 변경, 파생 효과, 소유권 상실·종료 정리, 사건용 L/I 변경 인터페이스 |
| [지역 script values](../common/script_values/eafp_japan_regional_values.txt) | 0~100 주 L 접근자, 주별 월간 변화, 세금 낭비 |
| [지역 triggers](../common/scripted_triggers/eafp_japan_regional_triggers.txt) | JAP·막부법·전국 JE·종료 표식의 관리 조건 |
| [기존 일본 effects](../common/scripted_effects/eafp_japan_effects.txt) | 바닐라 캐시 함수 override, 교토 임무 인계, 상실한 주 지역 기준 임무 비용 제거 |
| [전국 JE](../common/journal_entries/eafp_japan.txt) | 초기화·월간 처리·완료/무효화 정리 연결, 지역 패널 widget 등록 |
| [지역 on_actions](../common/on_actions/eafp_japan_regional_on_actions.txt) | 주 생성·소유권 변경·history 완료 후 정합성 갱신, 등록만 남아 있던 직위자 사망 해임 정의 복구 |
| [전국 권위 막대](../common/scripted_progress_bars/eafp_bakuhantaisei_progress_bars.txt) | 바닐라 0~1 접근자 대신 EAFP 0~100 L을 읽고 교토 기여 포함 |
| [저널 widget](../gui/journal_entry_widgets/eafp_je_bakuhantaisei.gui) | 기존 인사 UI 유지, 9주 × 충성도/독립성 숫자·막대·월간 변화·원인 설명 |
| [지역 효과 이관표](japan_regional_effect_migration.md) | 사건별 기존 결과와 새 L/I 결과 대조 |
| [정적 검증 도구](../tools/validate_japan_regional_content.py) | 9주 범위, 단일 월간 실행 주체, 캐시 계약, 종료 연결, 구조·인코딩·3개 언어 UI 키 검사 |

국가 history의 기존 전국 JE 추가 경로를 활용하여 JE `immediate`에서 초기화한다. history가 모두 끝난 `on_game_started`에서도 누적 없이 정합성을 보정한다. 초기 주 데이터가 존재하면 다시 초기화하지 않는다.

월간에는 모든 유효 주의 갱신 전 값으로 L/I 변화량을 계산하여 저장한다. 이후 두 값을 변경하고 캐시·지역 효과·UI 예상치를 갱신한다. 기존 주간 캐시 호출은 정합성만 보정하며 한 달치 진행을 추가하지 않는다. UI를 열거나 특정 주를 선택해야 계산이 돌아가는 구조가 아니다.

관리 대상에서 벗어난 실제 주는 EAFP 캐시 표식과 지역 효과를 제거한다. JAP 소유 주라면 바닐라와 같은 인물 기반 캐시 계산으로 인계하며, 대상 인물이 없거나 다른 소유자라면 캐시 기본 동작을 사용한다. 소유권 상실 때 국가 L/I는 휴면 보존하고 재획득하면 다시 캐시에 전달한다. 체제가 끝날 때는 종료 표식을 먼저 설정하여 정리 중 재덮어쓰기를 막은 뒤 국가 데이터를 제거한다.

## 사건·임무·밸런스

- `eafp_japan` 사건 19개의 효과 호출 62개를 `.disable`과 순서·값으로 대조했다. 주 충성도 29개와 독립성 33개로 분리하고 독립성의 원래 부호를 복원했다.
- 임무 선택 사건 `.11/.12`에 있던 인물 충성도 즉시 보너스 32개를 제거했다. 영지 감독은 월간 I −0.5만, 충성심 재확인은 월간 L +0.5만 직접 변경한다. 교토 선택지를 추가하고 기존 임무를 정리한 뒤 새 임무를 배치한다. 같은 지역·같은 종류의 임무 담당자가 있으면 기존 담당자를 복귀시킨 뒤 교체하여 중복 배치를 막는다. `.disable`의 주별 `tt`(배치)·`tt2`(복귀) 표시를 9주 선택지 모두에 연결했다. 사건 시작 시 기존 담당자를 저장하고, 선택 시 소유국·임무·대상 주를 재확인한다.
- 임무 해제는 현재 JAP 주 객체가 아니라 저장된 임무 대상의 `state_region`으로 지역 비용을 찾는다. 다른 국가로 넘어간 실제 주에 남은 임무도 귀환시킨다.
- 보신전쟁 전후 처리 `.10`의 현행 선택지 a/b/c/e를 유지하면서 9주에 원본의 비례 L/I 결과를 적용했다. 고료 결과는 제외했다. 세부 계수는 이관표에 기록했다. 비례 효과 63곳은 `save_scope_value_as`로 변화량을 먼저 평가한 뒤 단일 `scope:` 인자로 전달한다. 계산식 블록을 scripted effect 인자로 넘기던 오류를 수정했고, 효과 적용 전 변화량을 툴팁에도 사용한다.
- 추가 세금 낭비는 `0.25 × I/100`이다. 독립성의 비재정 효과는 I=100 기준 징병소 최대 단계 −5, 정치력 −10%, 인구 행정비용 −10%를 초기 계수로 정했다. 기존보다 작은 계수이며 실제 재정·징병 결과와 장기 밸런스는 게임에서 검증해야 한다.
- 지주 승인도는 유효 주의 `3 × (L−50)/50 × (1−I/100)` 평균으로 전국 단일 modifier에 반영한다. 주 modifier는 중첩하지 않고 갱신하며, 정리 경로의 보완책으로 14일 유효기간을 둔다.
- 한·영·중 지역 패널·효과 설명을 추가했다. 바닐라 다이묘 정치운동 영향 툴팁 2종도 지역 캐시를 기준으로 설명하도록 각 언어의 `replace/` 파일에 반영했다.

## 검증한 범위

실행 명령:

```text
python tools/validate_japan_regional_content.py
```

결과: 9개 지역, 월간 호출 한 곳, 종료 연결 두 곳, 캐시 덮어쓰기 연결, 관련 스크립트/GUI 10개 구조·BOM·CRLF, UI 키 23개의 3개 언어 정의가 통과했다. 새 지역 effect/trigger의 활성 정의 참조도 별도로 확인했다. 보신전쟁 비례 호출 63곳의 값 저장·전달·정리 개수와 계산식 블록 인자 금지 검사도 통과했다. 원본 `.disable`은 수정하지 않았다. 기존 사용자 변경을 포함한 전체 Git diff를 이번 변경의 결과로 간주하지 않았으며, 이 작업 직전 파일 사본과 대조했다.

로컬 바닐라의 `00_victoria_ep2_scripted_effects.txt`, `ep2_japan_values.txt`, `00_code_on_actions.txt` 및 생성된 modifier/effect 문서로 캐시 단위·기본 동작·주 스코프 on_action·modifier type을 확인했다. 정적 검사 도구는 게임 인터프리터가 아니므로 엔진의 모든 스코프 판정이나 GUI 렌더링을 보증하지 않는다.

## 미완료 검증

Victoria 3 1.13.11 실행 파일을 `-debug_mode`와 별도 임시 `-userdir`로 시작하고, 해당 프로필에는 EAFP만 활성화·전체 DLC 활성 설정을 작성했다. 사용자 플레이세트나 기존 저장 파일을 변경하지 않았다.

실행 프로세스는 생성되어 셰이더 캐시를 작성했지만, 게임 창 및 `error.log`/`game.log`/`debug.log`가 생성되기 전 단계에 머물렀다. 출력은 비어 있는 `pdxsdk.log`뿐이어서 모드 DB 로드 통과로 간주하지 않았다. 이 작업에서 시작한 프로세스만 PID와 시작 시각을 확인하여 종료했다. 초기화 지연의 원인은 확정하지 않았다.

후속 재실행에서는 기존 셰이더 캐시를 임시 프로필에 복사하고 `victoria3_win_console.exe`로 실행했다. 2026-09-06 18:20:07 시작한 프로세스가 DB 검사까지 진행했으며, 체크섬 출력에서 새 지역 파일을 읽은 사실을 확인했다. `database_conflicts.log`는 0바이트였고, 당시 `error.log`에서 새 지역 파일·보신전쟁 파일·지역 저널 GUI의 직접 오류는 발견하지 않았다. 단, 에도성 건물/생산방식 등 기존 콘텐츠의 오류가 남아 있으므로 모드 전체 DB가 정상이라는 뜻은 아니다.

실제 창 핸들은 생성되었지만 computer-use의 창 및 앱 목록에는 게임이 나오지 않아 신게임 선택·패널 확인을 진행하지 못했다. 자동화로 접근 가능한 창을 확보했다고 간주하지 않았고, 이번에 시작한 게임과 콘솔 래퍼만 PID·시작 시각을 확인하여 종료했다. 사용자의 원래 프로필·저장 파일은 수정하지 않았다.

이번 검사 원본은 [DB 오류 로그](../scratch/japan_regional_runtime_qa/database_error.log), [DB 충돌 로그](../scratch/japan_regional_runtime_qa/database_conflicts.log), [지역 파일 로드 체크섬](../scratch/japan_regional_runtime_qa/regional_load_checksums.log)에 보존했다. `scratch/`의 로컬 검증 산출물이며 배포용 모드 파일이 아니다.

따라서 다음은 **아직 실행으로 검증하지 않았다**: 1836 JAP 실제 초기값과 패널 배치, 효과 툴팁, 다이묘 0명/사망 후 캐시, 월간 진행, 주 양도·재획득·분할, 체제 종료 인계, 저장·불러오기, 30일·1년·AI 5년 진행, 메이지 정치운동 반응과 비일본 회귀. 기존 런타임 보고서의 통과 기록으로 이를 대체하지 않는다.

[최신 계획](japan_regional_bakuhantaisei_restoration_plan.md)의 게임 내 수용 기준에 따라 후속 실행 검증이 필요하다. 코드는 반영했지만 이 검증까지 완료한 상태로 보고하지 않는다.

## 2026-09-07 임무 효과의 주 modifier 이관

영지 감독은 실제 주에 `modifier_oversee_daimyo_domains`(독립성 월간 −0.5), 충성심 재확인은 `modifier_reaffirm_daimyos_loyalty`(충성도 월간 +0.5)를 붙인다. 국가 modifier는 기존 권위 비용 및 임무 활성 상태를 유지한다. 지역 갱신은 주 modifier를 먼저 반영한 뒤 월간 변화량을 계산한다. 임무별 고정 기여분은 제거했으며, 효과와 툴팁은 기존 주 변화요인 합계에서 한 번만 읽는다. 임무 귀환 시 저장된 실제 주의 해당 modifier를 제거하고, 주 상실·체제 종료 시에도 정리한다. 주 modifier는 주간 갱신 및 14일 만료를 사용한다. 기존 월간 효과량은 유지하며, 국가 권위 비용의 노중수좌 배율을 새로 월간 효과에 적용하지 않는다.

## 2026-09-07 세키가하라의 유산 복원

옛 `common/history/countries/jap - japan.disable`의 규슈 배율 0.4·주고쿠 배율 0.2와 `EAFP_japan_modifiers.disable`의 `legacy_of_sekigahara_modifier` 정의를 복원했다. 기본 충성도 월간 보정 −1에 따라 규슈 −0.4, 주고쿠 −0.2가 주 변화요인 합계에 반영된다. 관리 중인 JAP 주에만 중복 없이 적용하며, 기존 저널 완료·무효화의 `eafp_japan_end_regions` → 지역 해제 경로에서 존재 여부 확인 후 제거한다. 주 소유권 상실 시에도 같은 해제 경로로 정리한다. `.disable`과 기존 한·영·중 명칭은 유지했다. 정적 검사를 통과했으며 실제 게임 진행 검증은 미완료다.
