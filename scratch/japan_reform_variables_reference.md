# 공무합체·공의여론·천황 승리의 변수 설정과 참조

현재 파일 기준으로 정리했습니다. 여기서 “어디서 trigger되는지”는 **어디서 값을 설정하고, 어떤 조건에서 읽는지**로 나누었습니다. 코드는 수정하지 않았습니다.

대부분은 `set_variable = 변수명`으로 존재 여부만 기록하는 표식입니다. `restoration_timer_var`처럼 숫자를 저장하는 변수, 인물에 붙는 변수, 사건에만 전달되는 값은 별도로 구분했습니다.

**1. 세 결말을 확정하는 공통 변수**

| 변수 | 설정·제거 위치 | 참조 위치와 역할 |
|---|---|---|
| `kobu_gattai` | 막부 개혁 `on_complete`에서 설정. `on_fail`에서 제거 | `eafp_japan_kobu_gattai_completed`가 공무합체 확정 여부를 판단. 네 후속 개혁 일지의 시작·유지에도 사용 |
| `kogi_yoron` | 막부 개혁 `on_fail`에서 설정. `on_complete`에서 제거 | `eafp_japan_kogi_yoron_completed`가 공의여론 확정 여부를 판단 |
| `bakufu_kaikaku_complete_var` | 막부 개혁의 `on_complete`와 `on_fail`에서 설정 | **막부 주도 정치 개혁의 성공 표식.** 두 성공 분기의 재진입을 막고, 막번체제 저널의 완료에도 사용 |
| `japan_restoration_complete` | 공무합체·공의여론에서 설정. 명예로운 유신의 `on_complete`와 군주제 상실에 따른 `on_invalid`에서도 설정 | **유신 정국이 끝났다는 표식.** 이것만으로 성공 여부나 승자를 구분할 수 없음 |
| `japan_emperor_restored` | 공의여론의 `on_fail`, 천황 승리의 유신 `on_complete`에서 설정 | 천황 복권을 기록. **공의여론에서도 설정되므로 천황 단독 승리 전용 표식이 아님** |

실제 기록은 [막부 개혁의 완료·실패 효과](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_japan.txt:250), [유신의 천황 승리 효과](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_00_meiji_restoration.txt:131)에 있습니다. 기록된 결과를 읽는 것은 [결말 확인 트리거](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_triggers/eafp_japan_reform_triggers.txt:37)입니다.

각 결말이 변수에 가하는 변경은 다음과 같습니다. `—`는 해당 콜백에서 변경하지 않는다는 뜻입니다.

| 변수 | 공무합체 | 공의여론 | 천황 승리 |
|---|---|---|---|
| `kobu_gattai` | 설정 | 제거 | — |
| `kogi_yoron` | 제거 | 설정 | — |
| `bakufu_kaikaku_complete_var` | 설정 | 설정 | — |
| `japan_restoration_complete` | 설정 | 설정 | 설정 |
| `japan_emperor_restored` | — | 설정 | 설정 |

따라서 천황 승리 후 막부 개혁의 무효화 판정에서는 **`japan_restoration_complete`와 `japan_emperor_restored`가 있고, `bakufu_kaikaku_complete_var`는 없는 조합**도 확인합니다.

**2. 공무합체의 준비·탄원·유임 변수**

진행은 `혼인 성립 → 혼인 과제 완료 → 탄원 → 유임 응답 → 막부 개혁 complete`입니다.

| 변수·저장 범위 | 설정되는 곳 | 읽히는 곳과 역할 |
|---|---|---|
| `japan_imperial_marriage` · 인물 | `ep2_meiji.3.a`에서 쇼군에게 설정 | 혼인 저널이 현재 통치자의 혼인 상태를 검사. 혼인 실패·시간 초과·무효화 때 정리 효과가 제거 |
| `japan_break_treaty_var` · 혼인 저널 | 혼인 저널 `immediate`에서 파기 대상 조약이 잡히면 설정 | 혼인 완료 판정에서 조약 파기 조건을 적용할지 결정 |
| `japan_completed_imperial_marriage` · 국가 | `je_meiji_imperial_marriage.on_complete` | `eafp_japan_kobu_gattai_petition_ready`가 검사하는 **혼인 과제 달성 표식**. 혼인 성립 자체와 구분 |
| `je_meiji_restoration_proclaim_imperial_restoration_var` · 국가 | 황실 복원 탄원 버튼의 `effect` | 버튼 재사용을 막고 선택 완료 상태를 표시. 공무합체·공의여론 최종 조건 모두에서 탄원 실행 증거로 검사 |
| `eafp_japan_petition_kobu_ready` · 사건 범위 값 | 탄원 클릭 당시 공무합체 준비 조건이 참이면 `1` 저장 | `ep2_meiji.5`가 존재 여부를 읽어 `.52` 유임 사건으로 연결. 국가에 남기는 결말 변수가 아님 |
| `japan_renewed_bakufu` · 국가 | `ep2_meiji.52.a` 유임 응답 선택지 | `eafp_japan_kobu_gattai_conditions`가 검사하는 **실제 유임 승인 표식** |

공무합체 준비 판정은 혼인 완료 표식 외에도 **정통성 75 이상, 막부법 유지, 공통 안정 조건**을 요구합니다. 최종 판정에서는 준비 조건을 다시 확인하고 탄원 실행·유임 표식을 추가로 검사합니다.

근거: [혼인 성립 효과](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/events/000_eafp_japan_overrides.txt:251), [혼인 과제 조건·완료](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_00_meiji_restoration.txt:275), [공무합체 판정](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_triggers/eafp_japan_reform_triggers.txt:100), [탄원 버튼](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_buttons/eafp_japan_buttons.txt:69), [유임 승인](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/events/000_eafp_japan_overrides.txt:1830).

**3. 공의여론의 준비·탄원·합의 변수**

진행은 `공의여론 준비 조건 → 탄원 → 정치적 합의 응답 → 막부 개혁 fail`입니다. 여기서 `fail`은 공의여론이라는 대체 성공입니다.

| 변수·저장 범위 | 설정되는 곳 | 읽히는 곳과 역할 |
|---|---|---|
| `house_tokugawa` · 인물 | 도쿠가와 인물의 템플릿·생성 효과 | 준비 조건에서 **다이묘 이해집단 지도자가 도쿠가와인지** 검사. 결말을 선택하는 표식이 아니라 가문 식별자 |
| `house_yamato` · 인물 | 바닐라 황실 인물 템플릿·황실 인물 생성 효과 | 준비 조건에서 **현재 통치자가 황실 인물인지** 검사 |
| `eafp_japan_petition_kogi_ready` · 사건 범위 값 | 탄원 시 공무합체 준비 조건이 거짓이고 공의여론 준비 조건이 참이면 `1` 저장 | `ep2_meiji.5`에서 읽어 `.7` 정치적 합의 사건으로 연결 |
| `japan_taikunate_var` · 국가 | `ep2_meiji.7.a` 선택지 | `eafp_japan_kogi_yoron_conditions`가 **정치적 합의를 수락했는지** 검사 |
| `former_shogun_var` · 인물 | 바닐라 `country_restore_japanese_emperor` 등의 효과가 전직 쇼군에게 설정 | `.7`과 `.9`에서 전직 쇼군·대군을 찾는 데 사용. `.9.b`의 도쿠가와 인물 보상 대상에서도 구분자로 사용 |

여기에 앞 표의 **탄원 실행 표식**도 필요합니다. 준비 조건은 정통성 75 이상, 선거권, 다이묘 이해집단의 정부 참여, 도쿠가와 지도자, 황실 통치자와 공통 안정 조건입니다.

`house_yamato`와 `japan_emperor_restored`는 다릅니다. 전자는 **통치자의 신분**, 후자는 **국가의 정치적 결과 기록**입니다. 현재 구조에서는 황실 인물이 이미 통치해야 공의여론 탄원을 준비할 수 있고, 공의여론이 확정되면 국가에 `japan_emperor_restored`가 기록됩니다.

근거: [공의여론 준비·완료 판정](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_triggers/eafp_japan_reform_triggers.txt:120), [탄원 사건 분기](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/events/000_eafp_japan_overrides.txt:3792), [합의 수락](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/events/000_eafp_japan_overrides.txt:3939), [도쿠가와 템플릿](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/character_templates/eafp_japan_daimyo_templates.txt:17), [바닐라 황실 템플릿](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/character_templates/country_jap.txt:23), [전직 쇼군 표식 설정](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/scripted_effects/00_victoria_ep2_scripted_effects.txt:1).

**4. 천황 승리의 조건 변수**

천황 승리는 탄원 표식 없이도, 명예로운 유신 저널의 `complete` 조건으로 발생합니다.

| 변수·저장 범위 | 설정·변경되는 곳 | 읽히는 곳과 역할 |
|---|---|---|
| `restoration_timer_var` · 국가 숫자 | 유신 저널 `immediate`에서 `0`. 월간 조건 충족 시 `+1`, 불충족 시 `0`으로 초기화 | `eafp_japan_imperial_victory`가 `>= 6`을 검사. **조건을 유지한 월간 누적 횟수** |
| `house_tokugawa` · 인물 | 도쿠가와 인물 생성 시 설정 | 월간 타이머와 천황 승리 판정에서 다이묘 지도자에게 이 표식이 **없어야 함** |
| `emperor_var` · 국가의 인물 참조 | `je_meiji_restoration_update_japanese_emperor`가 황실 인물을 찾아 갱신. 유신 시작·주간 처리에서 호출 | 천황 위젯과 `meiji.1`의 초상화·인물 참조에 사용. **승리 여부를 저장하는 변수가 아님** |

타이머는 **천황 특성의 통치자, 막부법 없음, 진행 중인 내전 없음, 다이묘 지도자가 도쿠가와가 아님**을 만족하면 증가합니다. 천황 승리 트리거도 이 상태와 타이머 6 이상을 함께 확인합니다. 공무합체·공의여론과 달리 **정통성 75 조건은 없습니다.**

승리하면 유신 `on_complete`가 `meiji.1`을 호출하고 `japan_emperor_restored`, `japan_restoration_complete`를 설정합니다. 막부 개혁은 이를 받아 `invalid`로 종료합니다.

근거: [타이머 초기화·월간 계산](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_00_meiji_restoration.txt:76), [천황 승리 트리거](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_triggers/eafp_japan_reform_triggers.txt:2), [천황 인물 참조 갱신](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/scripted_effects/00_sgui_effects.txt:2).

**5. 결말 후 후속 일지와 정리에 사용하는 변수**

| 변수 | 설정·참조 위치 | 역할 |
|---|---|---|
| `kaikaku_start` | `eafp_japan_start_kobu_reforms`에서 부재를 검사한 뒤 설정 | 공무합체의 네 후속 개혁 일지 중복 생성 방지 |
| `bakufu_kaikaku_kaikoku_complete_var` | 개국 일지 `on_complete` | 개국 개혁 완료 기록 |
| `bakufu_kaikaku_guntai_complete_var` | 군제 일지 `on_complete` | 군제 개혁 완료 기록 |
| `bakufu_kaikaku_naibu_complete_var` | 내정 일지 `on_complete` | 내정 개혁 완료 기록 |
| `bakufu_kaikaku_zaisei_complete_var` | 재정 일지 `on_complete` | 재정 개혁 완료 기록 |
| `eafp_japan_kobu_reforms_rewarded` | 네 완료 표식 확인 후 `eafp_japan_check_kobu_reforms_complete`에서 설정 | `.2999` 종합 보상 중복 지급 방지 |
| `meiji_var` | 바닐라 `je_meiji_main` 시작 시 `0`, 근대화 과제 완료 시 증가. `meiji.1`도 초기화 | 공의여론·천황 승리 이후 바닐라 근대화 진행도 |
| `completed_je_meiji_economy`, `completed_je_meiji_army`, `completed_je_meiji_diplomacy` | 각 바닐라 후속 일지 완료 시 설정. 일부는 결말 사건에서 이미 조건을 만족하면 바로 기록 | 바닐라 근대화 분야별 완료 판정. 외교 분야는 DLC 조건에 따라 적용 |
| `hitotsubashiha_influence_var_monthly_add`, `nankiha_influence_var_monthly_add` | 파벌 주간 계산에서 산출, 월간 계산에서 사용. 개혁 종료 정리에서 제거 | 파벌 영향력의 월간 증감값. 결말 선택 표식은 아님 |
| `modifier_multiplier` · 지역 변수 | `eafp_japan_end_reform_factions` 실행 중 계산 | 종료 후 남기는 다이묘 호감도 보정의 크기·부호 계산 |
| `eafp_japan_negotiation_protected` · 인물 | `.51`에서 협상 대상 다이묘에게 설정. 사건 종료 또는 개혁 정리에서 제거 | 협상 중 임시 불멸 상태를 해제할 인물을 식별 |

근거: [후속 개혁 생성·보상·종료 정리](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_effects/eafp_japan_reform_effects.txt:2), [후속 개혁 완료 기록](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_japan.txt:608), [바닐라 근대화 저널](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/journal_entries/00_meiji_restoration.txt:649).

**현재 코드에서 확인된 주의점도 있습니다.**

- **공의여론 탄원 조건이 충돌합니다.** 현재 버튼의 `possible`은 다시 `law_bakufu`를 필수로 요구합니다. 반면 공의여론 준비는 선거권과 황실 통치자를 요구하므로, 일반적인 선거권 법률 경로에서는 준비를 마친 뒤 버튼을 사용할 수 없습니다. [현재 버튼 조건](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_buttons/eafp_japan_buttons.txt:44)
- 현재 탄원 `effect`에는 과거의 `japan_renewed_bakufu`·`japan_taikunate_var`를 지우는 처리가 없습니다. **이미 해당 표식이 남아 있는 상태에서는**, 탄원 실행 표식이 추가되는 것만으로 새 응답 전에 완료 조건이 참이 될 여지가 있습니다. [현재 탄원 효과](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_buttons/eafp_japan_buttons.txt:69)
