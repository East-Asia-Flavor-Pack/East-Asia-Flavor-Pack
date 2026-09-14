import urllib.request
import re
import json

# Let's inspect major han in each region
regions = {
    "TOHOKU": ["仙台藩", "会津藩", "秋田藩", "盛岡藩", "米沢藩", "弘前藩", "庄内藩"],
    "KANTO": ["水戸藩", "宇都宮藩", "川越藩", "佐倉藩", "小田原藩", "古河藩", "前橋藩", "高崎藩", "忍藩"],
    "HOKUSHINETSU": ["加賀藩", "越前府中藩", "福井藩", "越後長岡藩", "高田藩", "富山藩", "松代藩", "新発田藩"],
    "TOKAI": ["尾張藩", "駿府藩", "浜松藩", "岡崎藩", "吉田藩", "西尾藩", "田原藩", "津藩"],
    "KYOTO": ["彦根藩", "膳所藩", "淀藩", "亀岡藩", "丹波亀山藩", "福知山藩", "宮津藩"],
    "KANSAI": ["紀州藩", "姫路藩", "大和郡山藩", "明石藩", "尼崎藩", "岸和田藩", "赤穂藩", "篠山藩"],
    "CHUGOKU": ["広島藩", "長州藩", "鳥取藩", "岡山藩", "松江藩", "津山藩"],
    "SHIKOKU": ["徳島藩", "高知藩", "高松藩", "伊予松山藩", "宇和島藩", "丸亀藩", "大洲藩"],
    "KYUSHU": ["薩摩藩", "熊本藩", "福岡藩", "佐賀藩", "小倉藩", "久留米藩", "中津藩", "延岡藩", "飫肥藩"]
}

for r, hans in regions.items():
    print(f"=== {r} ===")
    for h in hans:
        url = 'https://ja.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&titles=' + urllib.parse.quote(h) + '&format=json'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode('utf-8'))
        for p in data['query']['pages'].values():
            txt = p.get('extract', '')[:300].replace('\n', ' ')
            # find kokudaka like XX万石
            m = re.findall(r'(\d+[\.\d]*\s*万[^\s、。]*石|\d+石)', txt)
            print(f"  {h}: {m[:3]} | {txt[:100]}")
