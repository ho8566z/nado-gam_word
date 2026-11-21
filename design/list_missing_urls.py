# -*- coding: utf-8 -*-
"""아직 받지 못한 투어 사진의 문서·파일 주소를 조회만 해서 출력한다(이미지는 받지 않는다). 사용: python list_missing_urls.py"""
import json
import os
import time
import urllib.parse

import fetch_dest_photos as base
from tour_theme_subjects import SUBJECTS

TOUR_DIR = os.path.join(base.ROOT, "src", "main", "resources", "static", "img", "tour")
dest_files = {v.get("file") for v in json.load(open(os.path.join(base.OUT, "credits.json"), encoding="utf-8")).values()}

missing = [t for t in sorted(SUBJECTS) if not os.path.exists(os.path.join(TOUR_DIR, "tour-%d.jpg" % t))]
print("못 받은 투어:", missing)
for tid in missing:
    lang, titles, label = SUBJECTS[tid]
    found = None
    for title in titles:
        r = base.page_image(lang, title)
        time.sleep(base.DELAY)
        if r and r[1] not in dest_files:
            found = (title, r)
            break
    if not found:
        print(tid, label, "-> 후보에서 이미지를 찾지 못함", titles)
        continue
    title, (thumb, fname, ptitle) = found
    article = "https://%s.wikipedia.org/wiki/%s" % (lang, urllib.parse.quote(ptitle.replace(" ", "_")))
    filepage = "https://commons.wikimedia.org/wiki/File:" + urllib.parse.quote(fname)
    print("TOUR %d | %s | 문서: %s" % (tid, label, ptitle))
    print("  문서   :", article)
    print("  파일   :", filepage)
    print("  사진   :", thumb)
