# -*- coding: utf-8 -*-
"""사용자가 직접 받은 투어 사진을 프로젝트에 넣는다: 폭 640px 로 줄여 tour-번호.jpg 로 저장하고,
저작자·라이선스는 Commons API 로 조회해(조회만, 이미지는 받지 않음) credits.json 에 등록한다.
사용: python import_tour_photos.py <사진이 있는 폴더>
"""
import json
import os
import sys
import time

from PIL import Image

import fetch_dest_photos as base
from tour_theme_subjects import SUBJECTS

OUT = os.path.join(base.ROOT, "src", "main", "resources", "static", "img", "tour")

# 받은 파일 이름 -> (투어 번호, Commons 원본 파일명, 위키 언어, 사용한 문서 제목)
FILES = {
    "Mortadella_tagliata.jpg": (34, "Mortadella_tagliata.jpg", "en", "Mortadella"),
    "Reef_snorkeler.jpg": (50, "Reef_snorkeler.jpg", "en", "Snorkeling"),
    "Tango_dancers_in_Montevideo.png": (103, "Tango_dancers_in_Montevideo.png", "en", "Tango"),
    "Korean_cuisine-Ojingeo_sundae-01.jpg": (118, "Korean_cuisine-Ojingeo_sundae-01.jpg", "ko", "오징어순대"),
    "Dinosaur_Ridge_of_Seoraksan.jpg": (119, "Dinosaur_Ridge_of_Seoraksan.jpg", "en", "Seoraksan"),
    "Dolsan_Bridge1.jfif": (132, "Dolsan_Bridge1.JPG", "en", "Yeosu"),
    "View_of_Suncheon.jpg": (134, "View_of_Suncheon.jpg", "en", "Suncheon"),
    "Panorama_of_International_Garden_Exposition_Suncheon_Bay_Korea_2013.jpg": (135, "Panorama_of_International_Garden_Exposition_Suncheon_Bay_Korea_2013.jpg", "ko", "순천만국가정원"),
    "청풍호_구담봉.jpg": (140, "청풍호_구담봉.jpg", "ko", "구담봉"),
    "Panoramic_view_of_Danyang-eup.jpg": (141, "Panoramic_view_of_Danyang-eup.jpg", "en", "Danyang County"),
}


def main(folder):
    cpath = os.path.join(OUT, "credits.json")
    credits = json.load(open(cpath, encoding="utf-8"))
    for local, (tid, fname, lang, used) in FILES.items():
        src = os.path.join(folder, local)
        if not os.path.exists(src):
            print("없음:", local)
            continue
        im = Image.open(src).convert("RGB")
        if im.width > 640:
            im = im.resize((640, round(im.height * 640 / im.width)), Image.LANCZOS)
        dest = os.path.join(OUT, "tour-%d.jpg" % tid)
        im.save(dest, "JPEG", quality=80, optimize=True, progressive=True)
        c = base.file_credit(fname)
        time.sleep(base.DELAY)
        c.update({"subject": used, "label": SUBJECTS[tid][2], "file": fname, "wiki": lang})
        credits["tour-%d" % tid] = c
        print("OK tour-%d" % tid, fname, "|", c["license"], "|", c["author"][:30], "|", os.path.getsize(dest) // 1024, "KB")
    json.dump(credits, open(cpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1])
