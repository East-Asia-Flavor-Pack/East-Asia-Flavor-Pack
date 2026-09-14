import urllib.request
import re
import json

domains = ["徳島藩", "高知藩", "伊予松山藩", "高松藩", "宇和島藩"]
for d in domains:
    url = "https://ja.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&titles=" + urllib.parse.quote(d) + "&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode("utf-8"))
    for p in data["query"]["pages"].values():
        txt = p.get("extract", "")[:400].replace("\n", " ")
        m = re.findall(r"(\d+[\.\d]*\s*万[^\s、。]*石|\d+石)", txt)
        print(f"{d}: {m[:5]}")
        print(f"  {txt[:150]}")
