# -*- coding: utf-8 -*-
"""투어 테마 사진을 더 나은 것으로 바꾸기 위한 후보를 Wikimedia Commons 에서 찾아 임시 폴더에 받는다.

- Commons 검색 API 로 투어마다 검색어로 후보 파일(가로 1000px 이상 사진, 로고·지도·그림 제외)을 찾고, 960px 썸네일을 받는다.
- 요청 간격을 두고, 429 가 나오면 즉시 멈춘다(우회하지 않는다). 이미 받은 후보는 건너뛴다.
- 사진을 고른 뒤에는 apply_tour_photos.py 로 프로젝트에 넣는다.
사용: python find_better_tour_photos.py <출력 폴더>
"""
import json
import os
import sys
import time
import urllib.parse

import fetch_dest_photos as base

BAD = ("logo", "map", "diagram", "icon", "flag", "coat of arms", "locator", "svg", "drawing", "illustration", "sketch", "poster", "banner", "screenshot")

# 투어 번호 -> 검색어 목록(앞에서부터 후보를 모은다)
QUERIES = {
    7: ["Vatican Museums spiral staircase", "Sistine Chapel interior"],
    16: ["Sapporo miso ramen bowl", "Hokkaido ramen"],
    25: ["Getty Center Los Angeles exterior", "Getty Center architecture"],
    30: ["Ski Dubai slope", "Dubai desert safari dunes"],
    34: ["Mortadella sandwich Sao Paulo", "Pao com mortadela"],
    35: ["Grand Egyptian Museum atrium", "Egyptian Museum Cairo building"],
    37: ["Surfers Muizenberg beach Cape Town", "Cape Town surfing"],
    40: ["Haring herring onions Amsterdam", "Raw herring sandwich"],
    43: ["Kunsthistorisches Museum Vienna facade", "Belvedere Palace Vienna"],
    46: ["Singapore Grand Prix night race Marina Bay", "Marina Bay Street Circuit race"],
    47: ["Macau Grand Prix race cars", "Guia Circuit Macau race"],
    48: ["Shilin Night Market food stalls", "Taipei night market street food"],
    51: ["Phu Quoc seafood grilled night market", "Phu Quoc beach sunset"],
    52: ["Tegallalang rice terrace Ubud", "Bali rice terraces"],
    60: ["Queen Victoria Market stalls Melbourne", "Melbourne flat white coffee"],
    62: ["Chicken adobo Filipino dish", "Pork adobo plate"],
    74: ["National Museum of Qatar building", "Museum of Islamic Art Doha"],
    77: ["Jeddah Corniche Red Sea", "King Fahd Fountain Jeddah"],
    80: ["Hungarian State Opera House facade", "Hungarian Parliament Budapest night"],
    86: ["Temple Bar Dublin pub street", "Dublin Temple Bar nightlife"],
    93: ["Carthage Antonine Baths ruins", "Sidi Bou Said Tunisia"],
    94: ["Labadi Beach Accra", "Accra beach Ghana"],
    95: ["Pike Place Market Seattle", "Seattle coffee shop espresso"],
    106: ["Museo del Oro Bogota gold", "Gold Museum Bogota Muisca raft"],
    109: ["Rock lobster dish plated", "Western rock lobster Australia"],
    115: ["Sundubu jjigae soft tofu stew", "Soondubu"],
    116: ["Jeongdongjin sunrise", "Jeongdongjin beach train"],
    117: ["Ojukheon Gangneung house", "Ojukheon"],
    120: ["Abai village Sokcho ferry", "Sokcho Gaetbae"],
    122: ["Gwangalli Beach Gwangandaegyo bridge night", "Gwangalli beach Busan"],
    124: ["Jeju black pork grilled", "Heukdwaeji-gui"],
    131: ["Yeosu Maritime Cable Car", "Yeosu cable car sea"],
    133: ["Jjangttungeo-tang mudskipper soup", "Chueotang Korean soup"],
    134: ["Suncheon Bay reed field", "Suncheonman wetland"],
    139: ["Deodeok-gui grilled deodeok", "Deodeok roots Korean cuisine"],
}


def search(q, n=8):
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch=%s&gsrnamespace=6&gsrlimit=%d"
           "&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=960") % (urllib.parse.quote(q + " filetype:bitmap"), n)
    d = base.get(url) or {}
    out = []
    for p in sorted((d.get("query") or {}).get("pages", {}).values(), key=lambda x: x.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]
        title = p["title"][5:]
        if not ii or ii.get("mime") != "image/jpeg" or ii.get("width", 0) < 1000:
            continue
        if any(b in title.lower() for b in BAD):
            continue
        out.append({"file": title, "thumb": ii["thumburl"], "page": ii.get("descriptionurl"), "w": ii["width"], "h": ii["height"],
                    "license": ((ii.get("extmetadata") or {}).get("LicenseShortName") or {}).get("value", "")})
    return out


def main(out):
    os.makedirs(out, exist_ok=True)
    meta_path = os.path.join(out, "cands.json")
    meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else {}
    for tid, qs in QUERIES.items():
        if str(tid) in meta and len(meta[str(tid)]) >= 3:
            continue
        cands = []
        for q in qs:
            for c in search(q):
                if all(c["file"] != x["file"] for x in cands):
                    cands.append(c)
            time.sleep(base.DELAY)
        cands = cands[:4]
        for i, c in enumerate(cands):
            path = os.path.join(out, "%d_%d.jpg" % (tid, i + 1))
            if not os.path.exists(path):
                try:
                    blob = base.get(c["thumb"], binary=True, tries=1)
                except Exception as e:  # noqa
                    print("STOP(제한 또는 오류)", tid, str(e)[:60])
                    json.dump(meta, open(meta_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                    return
                time.sleep(base.DELAY)
                if blob:
                    open(path, "wb").write(blob)
            c["local"] = path
        meta[str(tid)] = cands
        json.dump(meta, open(meta_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("OK", tid, len(cands), [c["file"][:30] for c in cands])
    print("done")


if __name__ == "__main__":
    main(sys.argv[1])
