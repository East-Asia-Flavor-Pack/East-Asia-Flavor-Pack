# 다이묘의 주 위치와 번 식별자 분리

## 변수 계약

```text
set_variable = { name = daimyo_var value = s:STATE_KYOTO }
set_variable = { name = daimyo_han_var value = flag:hikone }
```

- `daimyo_var`: 영지가 속한 주 지역 스코프. 주별 GUI 목록, 충성도 캐시, 주 변화요인, 소유 국가 판정에 사용한다.
- `daimyo_han_var`: 번 식별용 flag. 번 이름, 특정 번주 선택, 번별 후임 생성에 사용한다.
- `has_variable = daimyo_var`: 기존의 다이묘 신분 판정이므로 유지한다.
- 다이묘 지위를 해제하는 `character_clear_daimyo_status`는 두 변수를 모두 제거한다.

## 부여 경로

기존 10개 번의 역사 인물 템플릿 40개와 무작위 후임 생성 경로 10개에 번 식별자를 추가했다. 이이 나오아키는 기존 EAFP 템플릿에 추가하고, 나머지는 바닐라 템플릿을 REPLACE한다. 막부 직위만 가진 인물에게 다이묘 신분을 새로 부여하지 않는다.

| 번 | flag | 기본 주 |
|---|---|---|
| 사쓰마 | satsuma | KYUSHU |
| 미토 | mito | KANTO |
| 조슈 | choshu | CHUGOKU |
| 도쿠시마 | tokushima | SHIKOKU |
| 기슈 | kishu | KANSAI |
| 오와리 | owari | TOKAI |
| 히코네 | hikone | KYOTO |
| 가가 | kaga | HOKUSHINETSU |
| 센다이 | sendai | TOHOKU |
| 마쓰마에 | matsumae | HOKKAIDO |

## 번 기준으로 변경한 사용처

- `japan_domain_by_character`: 인물의 번 이름. EAFP 초상화 위 번 이름도 이 정의를 사용한다.
- `JAP_character_generate_new_daimyo`: 사망·쇼군 취임 등으로 공석이 된 번의 후임 생성 경로 선택.
- `JAP_state_generate_new_daimyo`, `japan_replace_missing_daimyo`: 내전 후 복구 시 해당 번의 생존 번주 유무 확인. 같은 주에 다른 번주가 있어도 복구를 막지 않는다.
- 대로 등용의 기존 이이 가문 후보 선택: 교토 소재 여부 대신 히코네번 여부 확인.
- `ep2_meiji.52`, `ep2_meiji_pulse.3`: 조슈 번주 선택.
- 나마무기 사건의 번주 선택: 내륙의 히코네번만 제외한다. 교토 주의 다른 번까지 제외하지 않는다.
- `ezo_republic.2`: 마쓰마에 번주의 자동 망명 대상 판정.
- `evaluate_matsumae_curse`: 바닐라 월간 on_action이 선택한 에조치 인물의 소유 국가에서 마쓰마에 번주를 다시 선택한다. 같은 주의 다른 번주가 사망 확률 판정을 대신 소모하지 않는다. 기존 역사 인물·연도·확률 조건은 유지한다.

## 주 기준으로 유지한 사용처

- 주별 다이묘 목록과 충성도 캐시, 주 변화요인·급진파·충성파 효과.
- 지진 피해 지역, 나마무기 사건의 실제 영지·피해 주 선택, 신선조가 활동하는 교토의 지역 대상.
- 내전에서 영지 소유 국가에 따른 인물 이전, 사망 시 소유 영지 존재 확인.
- 월간 on_action의 에조치·간사이 진입 조건. 실제 마쓰마에 대상은 새 효과에서 번으로 선택하고, 기슈의 조기 사망 대상은 기존 역사 인물 템플릿으로 한정되어 있다.
- 일반 다이묘 여부를 확인하는 상호작용·정치 운동·의복·정당 GUI 조건.
- `japan_domain_by_state`: 특정 인물의 소속이 아닌 주의 대표 번을 표시하는 바닐라 문구.

## 번을 추가할 때

1. 해당 인물의 생성 경로마다 주 지역과 새 번 flag를 모두 설정한다.
2. `japan_domain_by_character`에 flag와 `domain_번이름` 현지화의 대응을 추가한다.
3. 번별 후임 생성 효과와 `JAP_character_generate_new_daimyo`의 flag 분기를 추가한다. 역사 승계 순번을 사용한다면 다른 번과 공유하지 않는 변수를 사용한다. 기존 10개 번의 바닐라 승계 순번은 각 생성 효과에 고정된 서로 다른 주 지역에 저장되어 있다.
4. `JAP_state_generate_new_daimyo`에 해당 주·번의 공석 확인과 생성 분기를 추가한다. 같은 주에 분기를 여러 개 두어도 번주 존재 확인은 flag별로 이루어진다.

후속 구현으로 구마모토·사가·후쿠오카·오카야마·히로시마·돗토리·후쿠이·쓰·구보타·토사 10개 번을 추가하여 총 20개 번을 지원한다. 신규 역사 인물 32명과 번별 승계 순번은 `japan_additional_daimyos.md`에 정리했다. 기존 세이브에 번 식별자를 추정하여 넣는 이관 코드는 포함하지 않는다. 시작 인물 추가는 새 게임부터 적용된다.

## 검증

`python -B tools/validate_japan_daimyo_identity.py --game "D:/SteamLibrary/steamapps/common/Victoria 3/game"`

역사 템플릿 누락, 생성 경로, 번 이름·승계 분기, 같은 주에 다른 번을 지정한 경우의 이름·분기 분리, 주별 목록 유지, 공석 복구, 지위 해제, 중복 REPLACE, 파일 구조를 정적으로 검사한다. 게임 엔진 실행 검증을 대체하지 않는다.
