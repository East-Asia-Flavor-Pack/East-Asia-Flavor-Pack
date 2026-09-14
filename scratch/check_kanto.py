import urllib.request
import re
import json

kanto_domains = [
    ("水戸藩", "徳川"),
    ("川越藩", "松平/酒井"),
    ("古河藩", "土井"),
    ("前橋藩", "酒井/松平"),
    ("宇都宮藩", "本多/奥平"),
    ("小田原藩", "大久保/稲葉"),
    ("佐倉藩", "堀田/土井"),
    ("高崎藩", "松平/大河内"),
    ("館林藩", "徳川綱吉/秋元"),
    ("大多喜藩", "本多"),
    ("結城藩", "結城/水野"),
    ("岩槻藩", "阿部/大岡")
]

for name, clan in kanto_domains:
    url = "https://ja.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&titles=" + urllib.parse.quote(name) + "&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode("utf-8"))
        for p in data["query"]["pages"].values():
            txt = p.get("extract", "")[:600].replace("\n", " ")
            m = re.findall(r"(\d+[\.\d]*\s*万[^\s、。]*石|\d+石)", txt)
            print(f"{name} ({clan}): {m[:5]}")
            # print first 150 chars
            print(f"   {txt[:150]}")
    except Exception as e:
        print(f"Error {name}: {e}")
