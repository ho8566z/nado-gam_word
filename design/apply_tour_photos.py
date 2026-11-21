# -*- coding: utf-8 -*-
"""find_better_tour_photos.py 가 받은 후보 중 고른 사진을 프로젝트(static/img/tour)에 넣는다.

폭 640px 로 줄여 tour-번호.jpg 로 저장하고, 저작자·라이선스는 Commons API 로 조회해(조회만) credits.json 에 등록한다.
사용: python apply_tour_photos.py <후보 폴더 1> <후보 폴더 2>
"""
import json
import os
import sys
import time

from PIL import Image

import fetch_dest_photos as base

OUT = os.path.join(base.ROOT, "src", "main", "resources", "static", "img", "tour")

# (투어 번호, 후보 폴더 번호(1 또는 2), 후보 순번, 화면에 붙일 한글 이름)
PICKS = [
    (7, 1, 1, "바티칸 박물관 나선 계단"), (16, 1, 1, "삿포로 채소 라멘"), (25, 1, 2, "게티 센터"), (30, 1, 1, "스키 두바이"),
    (34, 1, 4, "모르타델라 샌드위치"), (35, 1, 1, "대이집트 박물관 대회랑"), (37, 1, 1, "무이젠버그 서핑"), (40, 1, 4, "청어 샌드위치"),
    (43, 1, 1, "미술사 박물관"), (46, 1, 2, "싱가포르 F1 야간 레이스"), (47, 1, 3, "마카오 그랑프리"), (48, 1, 3, "라오허 야시장 만두"),
    (51, 2, 4, "베트남식 홍합 요리"), (52, 1, 1, "발리 계단식 논"), (60, 1, 2, "멜버른 플랫화이트"), (62, 1, 3, "치킨 아도보"),
    (74, 1, 2, "카타르 국립박물관"), (77, 1, 3, "알 라흐마 수상 모스크"), (80, 1, 1, "헝가리 국립 오페라"), (86, 1, 3, "템플 바"),
    (93, 1, 1, "안토니누스 목욕장 유적"), (94, 1, 4, "라바디 비치"), (95, 2, 1, "연어 요리"), (106, 1, 3, "황금 가면"),
    (109, 1, 2, "서부 로브스터 어획"), (115, 1, 1, "순두부찌개"), (116, 1, 1, "정동진 일출"), (117, 1, 1, "오죽헌"),
    (122, 1, 2, "광안리 해변과 광안대교"), (124, 2, 4, "삼겹살 구이 한 상"), (131, 1, 1, "해상케이블카"), (133, 1, 1, "추어탕"),
    (134, 1, 3, "순천만 갈대밭"), (139, 1, 1, "더덕구이"),
]


def main(dirs):
    cpath = os.path.join(OUT, "credits.json")
    credits = json.load(open(cpath, encoding="utf-8"))
    metas = [json.load(open(os.path.join(d, "cands.json"), encoding="utf-8")) for d in dirs]
    for tid, which, idx, label in PICKS:
        c = metas[which - 1][str(tid)][idx - 1]
        src = os.path.join(dirs[which - 1], "%d_%d.jpg" % (tid, idx))
        im = Image.open(src).convert("RGB")
        if im.width > 640:
            im = im.resize((640, round(im.height * 640 / im.width)), Image.LANCZOS)
        im.save(os.path.join(OUT, "tour-%d.jpg" % tid), "JPEG", quality=80, optimize=True, progressive=True)
        cr = base.file_credit(c["file"])
        time.sleep(base.DELAY)
        cr.update({"subject": os.path.splitext(c["file"])[0], "label": label, "file": c["file"], "wiki": "commons"})
        credits["tour-%d" % tid] = cr
        print("OK", tid, label, "|", cr["license"], "|", cr["author"][:28])
    json.dump(credits, open(cpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1:])
