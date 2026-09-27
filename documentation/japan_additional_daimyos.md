# 추가 다이묘 10개 번: 역사 인물과 승계 구현

1836년 재임 번주 10명과 이후 역사 인물 22명, 총 32개 character_template을 추가했다. 시작 인물만 국가 역사에서 생성하며, 나머지는 해당 번의 승계가 발생할 때 생성한다. 기존 10개 번과 합쳐 20개 번을 개별 식별한다.

## 번 배치와 신분

| 번 | 가문 | 게임 주 | 분류 | 1836년 번주 |
|---|---|---|---|---|
| 구마모토 | 호소카와 | KYUSHU | 도자마 | 나리모리 |
| 사가 | 나베시마 | KYUSHU | 도자마 | 나오마사 |
| 후쿠오카 | 구로다 | KYUSHU | 도자마 | 나가히로 |
| 오카야마 | 이케다 | CHUGOKU | 도자마 | 나리토시 |
| 히로시마 | 아사노 | CHUGOKU | 도자마 | 나리타카 |
| 돗토리 | 이케다 | CHUGOKU | 도자마 | 나리미치 |
| 후쿠이 | 마쓰다이라 | HOKUSHINETSU | 신판 | 나리사와 |
| 쓰 | 도도 | TOKAI | 도자마 | 다카유키 |
| 구보타 | 사타케 | TOHOKU | 도자마 | 요시히로 |
| 토사 | 야마우치 | SHIKOKU | 도자마 | 도요스케 |

주 배치는 게임의 큰 주 구획에 대응시킨 것이다. 바닐라 `dynamic_state_and_hub_names_l_english.yml`의 쓰 거점은 `STATE_TOKAI`, 후쿠이 거점은 `STATE_HOKUSHINETSU`에 속한다. 돗토리 이케다가는 도쿠가와가와 가까운 대우를 받았지만 도자마로 분류했다. 쓰번 도도가는 도자마이면서 준후다이 대우를 받은 사례로, 이 구현은 출신 구분인 도자마를 사용한다. 준후다이 지위를 별도 후다이 변화요인과 중복 적용하지 않는다. 이 특수성은 [국립국회도서관의 도도가 연구 서지](https://ndlsearch.ndl.go.jp/books/R000000004-I8799055)에서도 확인할 수 있다.

## 인물 목록과 조사 자료

출생일은 양력으로 맞췄다. 재임 연도는 조사용 자료이며 게임에서 강제 퇴임시키는 날짜가 아니다. 1869년 이후의 표기는 지번사 재임을 포함한다. 호소카와 모리히사와 도도 다카키요는 에도시대 번주가 아니라 이후 지번사인 가문 계승자이므로 이를 별도로 표시했다.

| 번 | 인물 (전기) | 출생일 | 재임 |
|---|---|---|---|
| 구마모토 | [호소카와 나리모리 / 細川斉護](https://ja.wikipedia.org/wiki/細川斉護) | 1804.10.19 | 1826–1860 |
| 구마모토 | [호소카와 요시쿠니 / 細川韶邦](https://ja.wikipedia.org/wiki/細川韶邦) | 1835.7.23 | 1860–1870 |
| 구마모토 | [호소카와 모리히사 / 細川護久](https://ja.wikipedia.org/wiki/細川護久) | 1839.4.14 | 1870–1871 (知藩事) |
| 사가 | [나베시마 나오마사 / 鍋島直正](https://ja.wikipedia.org/wiki/鍋島直正) | 1815.1.16 | 1830–1861 |
| 사가 | [나베시마 나오히로 / 鍋島直大](https://ja.wikipedia.org/wiki/鍋島直大) | 1846.10.17 | 1861–1871 |
| 후쿠오카 | [쿠로다 나가히로 / 黒田長溥](https://ja.wikipedia.org/wiki/黒田長溥) | 1811.4.23 | 1834–1869 |
| 후쿠오카 | [쿠로다 나가토모 / 黒田長知](https://ja.wikipedia.org/wiki/黒田長知) | 1839.2.2 | 1869–1871 |
| 오카야마 | [이케다 나리토시 / 池田斉敏](https://ja.wikipedia.org/wiki/池田斉敏) | 1811.5.29 | 1829–1842 |
| 오카야마 | [이케다 요시마사 / 池田慶政](https://ja.wikipedia.org/wiki/池田慶政) | 1823.8.10 | 1842–1863 |
| 오카야마 | [이케다 모치마사 / 池田茂政](https://ja.wikipedia.org/wiki/池田茂政) | 1839.11.16 | 1863–1868 |
| 오카야마 | [이케다 아키마사 / 池田章政](https://ja.wikipedia.org/wiki/池田章政) | 1836.6.16 | 1868–1871 |
| 히로시마 | [아사노 나리타카 / 浅野斉粛](https://ja.wikipedia.org/wiki/浅野斉粛) | 1817.11.7 | 1830–1858 |
| 히로시마 | [아사노 요시테루 / 浅野慶熾](https://ja.wikipedia.org/wiki/浅野慶熾) | 1836.12.19 | 1858 |
| 히로시마 | [아사노 나가미치 / 浅野長訓](https://ja.wikipedia.org/wiki/浅野長訓) | 1812.9.4 | 1858–1869 |
| 히로시마 | [아사노 나가코토 / 浅野長勲](https://ja.wikipedia.org/wiki/浅野長勲) | 1842.8.28 | 1869–1871 |
| 돗토리 | [이케다 나리미치 / 池田斉訓](https://ja.wikipedia.org/wiki/池田斉訓) | 1820.9.2 | 1830–1841 |
| 돗토리 | [이케다 요시유키 / 池田慶行](https://ja.wikipedia.org/wiki/池田慶行) | 1832.5.24 | 1841–1848 |
| 돗토리 | [이케다 요시타카 / 池田慶栄](https://ja.wikipedia.org/wiki/池田慶栄) | 1834.5.1 | 1848–1850 |
| 돗토리 | [이케다 요시노리 / 池田慶徳](https://ja.wikipedia.org/wiki/池田慶徳) | 1837.8.13 | 1850–1871 |
| 후쿠이 | [마츠다이라 나리사와 / 松平斉善](https://ja.wikipedia.org/wiki/松平斉善) | 1820.10.30 | 1835–1838 |
| 후쿠이 | [마츠다이라 요시나가 / 松平慶永](https://ja.wikipedia.org/wiki/松平慶永) | 1828.10.10 | 1838–1858 |
| 후쿠이 | [마츠다이라 모치아키 / 松平茂昭](https://ja.wikipedia.org/wiki/松平茂昭) | 1836.9.17 | 1858–1871 |
| 쓰 | [도도 다카유키 / 藤堂高猷](https://ja.wikipedia.org/wiki/藤堂高猷) | 1813.3.11 | 1825–1871 |
| 쓰 | [도도 다카키요 / 藤堂高潔](https://ja.wikipedia.org/wiki/藤堂高潔) | 1837.10.19 | 1871 (知藩事) |
| 구보타 | [사타케 요시히로 / 佐竹義厚](https://ja.wikipedia.org/wiki/佐竹義厚) | 1812.8.23 | 1815–1846 |
| 구보타 | [사타케 요시치카 / 佐竹義睦](https://ja.wikipedia.org/wiki/佐竹義睦) | 1839.7.2 | 1846–1857 |
| 구보타 | [사타케 요시타카 / 佐竹義堯](https://ja.wikipedia.org/wiki/佐竹義堯) | 1825.9.9 | 1857–1871 |
| 토사 | [야마우치 도요스케 / 山内豊資](https://ja.wikipedia.org/wiki/山内豊資) | 1794.11.9 | 1809–1843 |
| 토사 | [야마우치 도요테루 / 山内豊熈](https://ja.wikipedia.org/wiki/山内豊熈) | 1815.4.8 | 1843–1848 |
| 토사 | [야마우치 도요아쓰 / 山内豊惇](https://ja.wikipedia.org/wiki/山内豊惇) | 1824.7.2 | 1848 |
| 토사 | [야마우치 도요시게 / 山内豊信](https://ja.wikipedia.org/wiki/山内豊信) | 1827.11.27 | 1848–1859 |
| 토사 | [야마우치 도요노리 / 山内豊範](https://ja.wikipedia.org/wiki/山内豊範) | 1846.5.10 | 1859–1871 |

연속된 번주 목록과 행적 확인에는 다음 박물관·지역 자료를 함께 사용했다. 개별 출생일은 위 인물별 전기와 대조했다.

- 구마모토: [문화유산 온라인의 호소카와가 묘소 자료](https://online.bunka.go.jp/heritages/detail/162588).
- 사가: [나베시마 보효회 나오마사 소개](https://www.nabeshima.or.jp/main/40.html), [아시아역사자료센터 나오히로 인물사전](https://www.jacar.go.jp/dictionary/02_item.html?id=00001038).
- 후쿠오카: [구로다가 역대 당주](https://toukoukai-kuroda.com/master/), [후쿠오카시박물관 나가히로 자료](https://museum.city.fukuoka.jp/archives/leaflet/479/index02.html).
- 오카야마: [오카야마성 역대 성주](https://okayama-castle.jp/learn-castlelords/), [하야시바라미술관 막말 이케다가 전시](https://www.hayashibara-museumofart.jp/data/199/exhibition_tpl/).
- 히로시마: [히로시마성 역대 성주](https://hiroshimacastle.jp/history/lord-of-castle), [국립국회도서관 아사노 나가코토](https://www.ndl.go.jp/portrait/datas/524).
- 돗토리: [돗토리현 이케다 요시노리](https://www.pref.tottori.lg.jp/82541.htm), [돗토리시역사박물관 요시유키 자료](https://www.tbz.or.jp/yamabikokan/yamabiko/10348/).
- 후쿠이: [후쿠이현 문서관 마쓰다이라가 자료](https://www.library-archives.pref.fukui.lg.jp/bunsho/category/usage/22268.html).
- 쓰: [도도 다카유키 인물사전](https://kotobank.jp/word/藤堂高猷-19061). 사전의 음력 생일과 게임에서 사용하는 양력 생일을 구분했다.
- 구보타: [사타케 요시히로](https://en.wikipedia.org/wiki/Satake_Yoshihiro), [요시치카](https://en.wikipedia.org/wiki/Satake_Yoshichika), [요시타카](https://en.wikipedia.org/wiki/Satake_Yoshitaka) 전기에서 출생일과 계승 순서를 확인했다.
- 토사: [고치성역사박물관 야마우치가 번주 소개](https://www.kochi-johaku.jp/column/3819/), [국립국회도서관 야마우치 도요시게](https://www.ndl.go.jp/portrait/datas/206).

## 이념·이해집단·특성

이름·생일·계승 순서는 역사 자료에 근거한다. 게임의 이념, 이해집단, trait 배정은 그 행적을 게임 규칙에 대응시킨 해석이며 역사 자료의 직접 분류가 아니다.

- 나베시마 나오마사·구로다 나가히로는 기술 도입과 번정 쇄신을 반영해 막부개혁가와 산업가를 배정했다.
- 마쓰다이라 요시나가·야마우치 도요시게 등 막부 틀 안의 현실적 개혁을 지향한 인물에는 `ideology_bakufu_reformer`를 사용했다.
- 미토가 출신 이케다 모치마사·요시노리는 미토학으로 배정했다.
- 이후 근대화·유신에 참여한 후계자 일부는 개혁가로 배정했다. 행적이 불분명한 단기·어린 번주는 중도파를 중심으로 설정했다.
- 특성은 혁신적·꼼꼼함·신중함·정치적 수완 등을 1~2개 부여했다. 생성일에 만 16세 미만이면 바닐라 방식의 `trait_child` 조건도 적용한다.
- 이 인물들은 실제 번주이므로 귀족·다이묘·magnate·politician으로 생성한다. 막부 관직만 가진 인물의 역할 설정에는 영향을 주지 않는다.

정확한 인물별 게임 설정과 원전 URL은 `tools/data/japan_additional_daimyos.json`에 보관했다.

## 승계와 이벤트 연결

1. 모든 번주에게 `daimyo_var = s:STATE_...`와 `daimyo_han_var = flag:...`를 함께 부여한다. 주별 GUI는 전자로 묶고, 번 이름과 후계자는 후자로 구별한다.
2. 바닐라 `on_character_death` → `JAP_character_generate_new_daimyo` 경로에 새 번 10개를 추가했다. 바닐라의 쇼군 취임·도쿠가와가 입양에서 호출하는 승계도 같은 분기를 사용한다. 별도의 중복 사망 on_action은 만들지 않는다.
3. 번마다 `eafp_daimyo_chain_id_<han>`를 주 지역에 저장한다. 규슈의 구마모토·사가·후쿠오카가 각자 다른 순번을 가지며, 기존 사쓰마의 순번과도 공유하지 않는다. 역사 인물 등록은 순번을 앞으로만 진행시킨다.
4. 다음 역사 인물이 이미 사용된 템플릿이면 건너뛴다. 매 반복마다 순번을 증가시키며 한 번의 호출에서 최대 해당 번 후계자 수만큼 반복한다.
5. 아직 태어나지 않은 후계자는 생성하지 않고 같은 가문의 무작위 번주를 생성한다. 이때 역사 승계 순번을 소비하지 않아 다음 승계 때 다시 확인한다. 역사 인물 목록이 끝나면 같은 가문·번·주·신분을 가진 무작위 후임을 생성한다.
6. 현재 국가가 해당 주를 소유하는 경우에만 새 번주를 생성한다. 폐번 전역 변수가 설정된 뒤에는 새 생성 경로가 작동하지 않는다.
7. 내전 후 공석 복구는 주 전체의 다이묘 존재가 아니라 해당 번 flag를 가진 살아 있는 인물의 존재를 확인한다. 같은 주의 다른 번주가 복구를 막지 않는다.
8. 기존 `daimyos_list`와 주별 목록은 모든 해당 인물을 순회하므로 신규 번주도 초상화·충성도 표시, 일반 다이묘 상호작용·이벤트 및 내전 소유국 이전 대상이 된다. 기존 지역 충성도·독립성은 주 단위 값을 계속 사용한다.
9. 조슈·히코네·마쓰마에 같은 특정 번의 전용 사건은 해당 번 flag를 판정한다. 예를 들어 히로시마 번주가 같은 주에 있다는 이유로 조슈 전용 사건의 대상이 되지 않는다.

역사상 퇴임 연도나 사망 연도에 강제로 교체하는 새 일정은 추가하지 않았다. 바닐라처럼 게임 중 사망·해임 등 승계 계기가 발생할 때 순서대로 이어지므로 실제 교체 연도는 달라질 수 있다.

## 파일과 검증

- `common/character_templates/eafp_japan_additional_daimyo_templates.txt`: 32개 역사 인물.
- `common/scripted_effects/eafp_japan_additional_daimyo_effects.txt`: 등록·번별 역사 승계·무작위 후임.
- `common/history/characters/jap - japan.txt`: 시작 번주 10명.
- `common/scripted_effects/eafp_japan_daimyo_effects.txt`: 승계 및 공석 복구 연결.
- `common/customizable_localization/eafp_japan_daimyo_custom_loc.txt`: 번 flag별 이름.
- `localization/{korean,english,simp_chinese}/eafp_japan_additional_daimyos_l_<language>.yml`: 번 이름 및 새 인명.

동일 로마자·동일 한자는 기존 인명 키를 사용한다. 동일 로마자에 다른 한자이면 빈 숫자 접미사 키를 사용한다. 새 키는 한국어·영어·중국어 간체에 모두 정의한다.

재생성 및 검사:

```powershell
python -B tools/generate_japan_additional_daimyos.py --game 'D:/SteamLibrary/steamapps/common/Victoria 3/game'
python -B tools/validate_japan_daimyo_identity.py --game 'D:/SteamLibrary/steamapps/common/Victoria 3/game'
python -B tools/validate_japan_additional_daimyos.py --game 'D:/SteamLibrary/steamapps/common/Victoria 3/game'
```

검사는 40개 기존 역사 템플릿의 번 식별, 20개 번 분기, 새 역사 인물 32명과 무작위 후임 10개, 참조·현지화·구조 및 추출된 승계 표의 64개 조건 사례를 확인한다. 게임 엔진에서의 실행·화면 검증은 별도로 필요하다.

새 게임을 기준으로 한 변경이며, 이미 진행 중인 세이브에 시작 번주나 번 식별자를 소급 부여하는 이관은 포함하지 않는다.
