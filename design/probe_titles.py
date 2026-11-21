# -*- coding: utf-8 -*-
"""후보 문서 제목에 대표 이미지가 있는지 확인한다(이미지는 받지 않고 조회만 한다). 사용: python probe_titles.py"""
import json
import os
import time

import fetch_dest_photos as base

DEST_CREDITS = os.path.join(base.OUT, "credits.json")
dest_files = {v.get("file") for v in json.load(open(DEST_CREDITS, encoding="utf-8")).values()}

CANDIDATES = {
    118: [("ko", ["오징어순대", "아바이순대", "순대", "속초시"]), ("en", ["Sundae (food)", "Sokcho"])],
    119: [("ko", ["설악산 케이블카", "권금성", "설악산국립공원"]), ("en", ["Seoraksan", "Sokcho"])],
    132: [("ko", ["여수 이순신광장", "이순신광장", "여수 해양공원", "여수시"]), ("en", ["Yeosu", "Odongdo"])],
    134: [("ko", ["순천만 스카이큐브", "스카이큐브", "순천만", "순천시"]), ("en", ["Suncheon Bay", "Suncheon"])],
    135: [("ko", ["순천만국가정원", "순천만 국가정원", "선암사"]), ("en", ["Suncheon Bay National Garden", "Seonamsa"])],
    140: [("ko", ["구담봉", "옥순봉", "충주호", "단양군"]), ("en", ["Chungju Lake", "Danyang County"])],
    141: [("ko", ["단양팔경", "사인암", "단양 도담삼봉", "단양군"]), ("en", ["Danyang County", "Dodamsambong"])],
}

for tid, groups in CANDIDATES.items():
    for lang, titles in groups:
        for t in titles:
            try:
                r = base.page_image(lang, t)
            except Exception as e:  # noqa
                print(tid, lang, t, "ERR", str(e)[:40])
                time.sleep(base.DELAY)
                continue
            time.sleep(base.DELAY)
            if r:
                print(tid, lang, t, "->", r[1], "(도시 사진과 같음)" if r[1] in dest_files else "OK")
            else:
                print(tid, lang, t, "-> 이미지 없음")
