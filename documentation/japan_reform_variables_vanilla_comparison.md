# 막부 개혁 변수: 바닐라와의 설정·조건 읽음 비교

바닐라 원본과 현재 모드를 대조했습니다. 가장 큰 변화는 **노선 선택용 변수를 결말 확정용으로 바꾼 것**, 그리고 **탄원과 응답 수락을 완료 조건으로 추가한 것**입니다.

아래의 “설정”은 별도 숫자가 표시되지 않은 경우 `set_variable = 변수명`, “읽음”은 주로 `has_variable`에 의한 존재 여부 검사입니다.

**1. 결말을 기록하는 변수**

| 변수 | 바닐라의 설정·조건 읽음 | 현재 모드의 설정·조건 읽음 | 차이 |
|---|---|---|---|
| `kobu_gattai` | **설정:** 전략 선택 사건 `.2`에서 공무합체 선택 시 설정. 전략 버튼으로 변경 가능. **읽음:** 혼인·탄원 행동, `.5`의 유임 분기, 유신 JE의 막부 승리 분기 등에 사용 | **설정:** 막부 개혁 `on_complete`에서 설정하고 공의여론 `on_fail`에서는 제거. **읽음:** 공무합체 확정 확인과 후속 개혁 시작·유지에 사용 | **앞으로 추진할 노선 → 이미 성립한 결말**로 의미 변경 |
| `kogi_yoron` | **설정:** `.2`의 공의여론 선택, 전략 전환 버튼, 혼인 실패·만료, 일부 정권 반환 사건에서 설정. **읽음:** 유신 JE의 공의여론 승리 조건과 결말 사건 선택에 사용 | **설정:** 막부 개혁 `on_fail`에서 설정하고 공무합체 `on_complete`에서는 제거. **읽음:** 공의여론 확정 확인에 사용 | 사전 선택·강제 전환 표식을 없애고 **최종 결과 표식**으로 사용 |
| `bakufu_kaikaku_complete_var` | 없음 | **설정:** 막부 개혁의 공무합체·공의여론 양쪽 성공에서 설정. **읽음:** 공통 준비 조건에서는 부재를 요구하고, 성공 확인에서는 존재를 요구. 막번체제 완료에도 사용 | EAFP의 **막부 주도 개혁 성공 표식** |
| `japan_restoration_complete` | **설정:** 유신 JE의 천황 승리 `on_complete`, 막부 승리 `on_fail`, 군주제 상실 `on_invalid`. **읽음:** 유신 재등장 방지 및 이후 콘텐츠 조건 | 천황 승리·군주제 상실은 동일. 공무합체·공의여론에서는 **막부 개혁 JE가 먼저 설정**. 개혁 준비·결말 확인·무효화 조건에서도 추가로 읽음 | 의미는 동일한 **유신 정국 종료**. 막부 승리 때 기록 주체가 이동 |
| `japan_emperor_restored` | **설정:** 천황 승리, 또는 유신 `on_fail`의 공의여론 분기. **읽음:** 천황 복권 이후 콘텐츠 조건 | 천황 승리는 동일. 공의여론은 막부 개혁 `on_fail`에서 설정. 공의여론 확정·막부 개혁 무효화에도 사용 | 의미는 유지. **바닐라에서도 공의여론과 천황 승리 양쪽에서 설정됨** |

바닐라에서는 유신 JE가 `kobu_gattai`·`kogi_yoron`을 보고 **선택한 노선의 국가 조건을 검사**합니다. 현재 모드의 유신 JE는 두 노선의 실질 조건을 직접 평가하지 않고, **막부 개혁에서 이미 확정한 결과 변수 조합을 확인하여 종료**합니다.

근거: [바닐라 유신 승리 판정](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/journal_entries/00_meiji_restoration.txt:239), [바닐라 전략 전환](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/scripted_buttons/07_meiji_buttons.txt:169), [현재 결과 기록](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_japan.txt:250), [현재 결과 확인](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_triggers/eafp_japan_reform_triggers.txt:37).

**2. 공무합체의 혼인·유임 변수**

| 변수 | 바닐라의 설정·조건 읽음 | 현재 모드의 설정·조건 읽음 | 차이 |
|---|---|---|---|
| `japan_imperial_marriage` · 인물 | `.3.a`에서 쇼군에게 설정. 혼인 JE의 실패 조건에서 현재 통치자에게 있는지 검사. 실패·만료 때 현재 통치자에게서 제거 | 설정은 동일. 혼인 JE의 **완료 조건에서도 존재를 명시적으로 요구**. 실패·만료·무효화 때 해당 표식을 가진 국가 내 인물들을 찾아 제거 | 완료 판정 강화, 통치자가 바뀌었을 때의 정리 범위 확대 |
| `japan_break_treaty_var` · 혼인 JE | 시작 시 파기 대상 조약이 있으면 설정. 완료 조건에서 조약 파기 검사를 적용할지 결정 | 같은 위치에서 설정하고 같은 방식으로 읽음 | 이 변수 자체의 동작은 유지 |
| `japan_completed_imperial_marriage` · 국가 | 혼인 JE 완료 시 설정. 공무합체를 선택한 상태에서 유신 승리 조건이 검사. 탄원 가능 조건의 한 경로는 `kobu_gattai`와 이 표식을 함께 요구 | 혼인 JE 완료 시 설정하는 것은 동일. 공무합체 준비 조건이 **노선 선택 표식 없이** 검사. 현재 탄원 버튼도 혼인 성과만으로 해당 가능 조건을 충족할 수 있음 | 성과 표식은 유지하되, 사전 공무합체 선택 의존 제거 |
| `japan_renewed_bakufu` · 국가 | `.52.a` 유임 응답에서 설정. 유신 JE가 공무합체 승리 조건으로 읽음 | 설정 사건·선택지는 동일. 막부 개혁의 공무합체 완료 조건에서 읽음 | 설정 의미는 유지하고 읽는 JE 이동. 현재는 탄원 실행 표식도 함께 요구 |

특히 **유임 사건에 도달하는 조건**이 달라졌습니다.

- 바닐라 `.5`: `kobu_gattai`가 있고 **정통성 50 초과**이면 `.52`.
- 현재 모드: 탄원 시 **공무합체 준비 조건 전체와 정통성 75 이상**을 충족했다는 사건 범위 값을 확인하면 `.52`.

정통성 **75 이상이라는 최종 승리 기준 자체는 바닐라에도 있었습니다.** 모드에서는 그것을 탄원 응답 분기를 결정하는 시점에도 적용합니다.

근거: [바닐라 혼인 JE](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/journal_entries/00_meiji_restoration.txt:496), [현재 혼인 JE](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/journal_entries/eafp_00_meiji_restoration.txt:275), [바닐라 유임 분기](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/japan_events/ep2_meiji_restoration.txt:529), [현재 준비·완료 조건](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_triggers/eafp_japan_reform_triggers.txt:100).

**3. 탄원 실행과 공의여론 합의 변수**

| 변수 | 바닐라의 설정·조건 읽음 | 현재 모드의 설정·조건 읽음 | 차이 |
|---|---|---|---|
| `je_meiji_restoration_proclaim_imperial_restoration_var` · 국가 | 탄원 버튼 `effect`에서 설정. 버튼의 재사용 금지와 `selected` 상태에서 읽음 | 같은 방식으로 설정·사용. 추가로 **공무합체와 공의여론의 최종 완료 조건 모두에서 읽음** | 단순 사용 기록에 **결말의 필수 조건** 역할 추가 |
| `eafp_japan_petition_kobu_ready` · 사건 범위 | 없음 | 클릭 당시 공무합체 준비 조건이 참이면 `1` 저장. `.5`가 `exists = scope:…`로 읽어 `.52` 호출 | 현재 국가 상태를 나중에 다시 분기하는 대신, **클릭 당시 자격을 전달** |
| `eafp_japan_petition_kogi_ready` · 사건 범위 | 없음 | 공무합체 준비 조건이 거짓이고 공의여론 준비 조건이 참이면 `1` 저장. `.5`가 존재 여부를 읽어 `.7` 호출 | 공의여론 자격 전달. `else_if`이므로 양쪽 충족 시 공무합체 우선 |
| `japan_taikunate_var` · 국가 | **`.7.immediate`에서 설정.** `amendment_taikunate.possible`이 읽어 대군제 수정안의 사용을 허용. 수정안 `on_deactivate`에서 제거. **유신의 공의여론 승리 조건은 이 변수를 요구하지 않음** | **`.7.a` 선택지에서 설정.** 기존 수정안 사용 조건 외에, 막부 개혁의 공의여론 완료 조건도 이 변수를 요구 | 사건이 열릴 때 설정하던 것을 **응답 선택 시점**으로 늦추고, **합의 수락 증거**로도 사용 |

두 `eafp_japan_petition_*` 값은 국가의 영구적인 결과 변수가 아닙니다. `save_scope_value_as`로 사건 체인에 전달되며, 현재 분기 코드는 숫자 `1`과 비교하기보다 **값이 존재하는지** 검사합니다.

`japan_taikunate_var`에는 주의할 차이가 있습니다. 모드에서 합의 수락 표식으로 재사용했지만, 바닐라 수정안의 제거 효과는 남아 있습니다. 따라서 **공의여론 저널이 끝나기 전에 대군제 수정안이 비활성화되면 이 변수가 제거되어 완료 조건이 다시 미충족될 수 있습니다.** 이미 결말이 확정된 뒤에는 별도의 `kogi_yoron` 결과 조합을 읽으므로 같은 의미의 문제는 아닙니다.

근거: [바닐라 탄원 버튼](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/scripted_buttons/07_meiji_buttons.txt:54), [현재 탄원 기록·전달](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_buttons/eafp_japan_buttons.txt:64), [바닐라 대군제 사건](C:/Users/user/Documents/GitHub/Vic3-vanilla/events/japan_events/ep2_meiji_restoration.txt:849), [현재 합의 수락](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/events/000_eafp_japan_overrides.txt:3939), [대군제 수정안의 변수 검사·제거](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/amendments/00_amendments_ep2_04.txt:14).

**4. 천황 승리·인물 식별 변수**

| 변수 | 바닐라의 설정·조건 읽음 | 현재 모드와의 차이 |
|---|---|---|
| `restoration_timer_var` · 국가 숫자 | 유신 시작 시 `0`. 천황 통치·막부법 없음·내전 없음·다이묘 지도자가 도쿠가와가 아닌 상태에서 매월 `+1`, 아니면 `0`. 유신 완료 조건은 `>= 6` 요구 | **값 설정과 계산 조건 유지.** 완료 판정을 `eafp_japan_imperial_victory`로 분리하고, 막부 개혁의 준비 배제·무효화에서도 재사용 |
| `house_tokugawa` · 인물 | 도쿠가와 인물 템플릿·생성 효과에서 설정. 공의여론은 다이묘 지도자에게 존재해야 하고, 천황 승리는 없어야 함 | 가문 식별 의미 유지. EAFP 추가 인물에도 설정. 공의여론 검사가 **탄원 준비 단계로 이동** |
| `house_yamato` · 인물 | 황실 인물 템플릿·생성 효과에서 설정. 공의여론 완료 조건이 현재 통치자에게 존재하는지 검사 | 설정 의미 유지. 같은 검사를 **탄원 준비 조건부터 적용** |
| `former_shogun_var` · 인물 | 천황 복원 효과 등이 전직 쇼군에게 설정. `.7`·`.9`에서 대군을 찾고, 수정안 효과와 인물 보상 대상을 구분 | 본래 역할 유지. 현재 `.5`에도 막부법이 없을 때 전직 쇼군을 찾는 참조가 추가됨 |
| `emperor_var` · 국가의 인물 참조 | 천황 갱신 효과가 황실 인물을 찾아 저장. 유신 시작·주간 처리에서 갱신. 위젯과 `meiji.1`에서 사용. 군주제 상실 시 제거 | 관련 설정·참조 방식 유지. 결말 성공 표식으로 바꾸지 않음 |

천황 승리의 경우는 **조건의 내용보다, 그 조건을 여러 저널에서 공유하도록 옮긴 차이**가 중심입니다. 정통성 75는 바닐라와 모드 모두 천황 승리의 필수 조건이 아닙니다.

근거: [바닐라 타이머·천황 승리](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/journal_entries/00_meiji_restoration.txt:75), [현재 공용 천황 승리 트리거](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_triggers/eafp_japan_reform_triggers.txt:2), [바닐라 전직 쇼군 설정](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/scripted_effects/00_victoria_ep2_scripted_effects.txt:1), [천황 참조 갱신](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/scripted_effects/00_sgui_effects.txt:2).

**5. 후속 개혁·종료 정리 변수**

| 변수 | 바닐라 | 현재 모드 |
|---|---|---|
| `kaikaku_start` | 없음 | 공무합체 성공 후 후속 개혁 생성 효과에서 부재 확인 → 설정. 중복 시작 방지 |
| `bakufu_kaikaku_kaikoku_complete_var` | 없음 | 개국 일지 완료 시 설정. 재생성 방지·종합 완료 검사 |
| `bakufu_kaikaku_guntai_complete_var` | 없음 | 군제 일지 완료 시 설정. 재생성 방지·종합 완료 검사 |
| `bakufu_kaikaku_naibu_complete_var` | 없음 | 내정 일지 완료 시 설정. 재생성 방지·종합 완료 검사 |
| `bakufu_kaikaku_zaisei_complete_var` | 없음 | 재정 일지 완료 시 설정. 재생성 방지·종합 완료 검사 |
| `eafp_japan_kobu_reforms_rewarded` | 없음 | 네 분야 완료와 자신의 부재를 확인한 뒤 설정. `.2999` 보상 중복 방지 |
| `meiji_var` | 바닐라 근대화 주 일지 시작 시 `0`, 분야별 완료 시 증가. 주 일지 진행도에서 읽음 | 기존 처리 유지. 공의여론은 `.9`, 천황 승리는 `meiji.1`을 통해 같은 바닐라 근대화 체계로 연결 |
| `completed_je_meiji_economy` | 경제 과제 완료 또는 결말 사건의 경제 조건 선충족 처리에서 설정. 근대화 완료 판정에서 읽음 | 해당 바닐라 처리 유지 |
| `completed_je_meiji_army` | 군제 과제 완료 시 설정. 근대화 완료 판정에서 읽음 | 해당 바닐라 처리 유지 |
| `completed_je_meiji_diplomacy` | 외교 과제 완료 또는 선충족 처리에서 설정. DLC 조건에 따라 사용 | 해당 바닐라 처리 유지 |
| `hitotsubashiha_influence_var_monthly_add` | 해당 EAFP 파벌 변수 없음 | 파벌 주간 계산에서 설정·가산, 월간 영향력 계산에서 읽음. 개혁 종료 시 제거 |
| `nankiha_influence_var_monthly_add` | 해당 EAFP 파벌 변수 없음 | 위와 같은 난키파용 처리 |
| `modifier_multiplier` · 지역 변수 | **해당 막부 개혁 종료 계산은 없음.** 일반적인 이름이므로 다른 바닐라 코드의 동명 변수와 구분 필요 | 종료 정리 실행 중 계산하여 다이묘 호감도 보정의 부호·크기를 결정 |
| `eafp_japan_negotiation_protected` · 인물 | 이 표식은 없음. `.51`은 대상 다이묘에게 직접 임시 불멸을 켰다가 선택지에서 해제 | 임시 불멸 설정과 함께 표식을 추가. 사건 선택지뿐 아니라 **개혁 종료 정리에서도 표식을 찾아 해제** 가능 |

근거: [EAFP 후속 개혁·정리 효과](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/common/scripted_effects/eafp_japan_reform_effects.txt:2), [바닐라 근대화 변수](C:/Users/user/Documents/GitHub/Vic3-vanilla/common/journal_entries/00_meiji_restoration.txt:649), [현재 협상 대상 보호](C:/Users/user/Documents/GitHub/East-Asia-Flavor-Pack/events/000_eafp_japan_overrides.txt:3843).

현재 비교에서 특히 중요한 호환성 지점은 두 가지입니다. **`kobu_gattai`·`kogi_yoron`은 같은 이름으로 설정 시점과 의미가 바뀌었고**, **`japan_taikunate_var`는 기존 수정안 생명주기에 종속된 변수에 새로운 완료 조건 역할을 더했습니다.** 반면 천황 승리 타이머와 가문·천황 인물 식별 변수는 본래 의미를 유지하고 있습니다.
