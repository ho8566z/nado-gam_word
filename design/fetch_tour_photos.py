# -*- coding: utf-8 -*-
"""투어 카드 오른쪽 절반에 넣을 테마 사진(음식·스포츠 경기장·예술/휴식 명소)을 Wikipedia/Wikimedia Commons 에서 내려받는다.

- 주제는 tour_theme_subjects.py. 후보 문서를 앞에서부터 시도해 대표 이미지가 있는 첫 문서를 쓴다.
- 여행지 전경 사진과 같은 파일이면 건너뛰고 다음 후보를 쓴다(왼쪽과 오른쪽이 같은 그림이 되지 않게).
- 사진: nado-gam/src/main/resources/static/img/tour/tour-{투어번호}.jpg, 출처: 같은 폴더의 credits.json
- fetch_dest_photos.py 와 같은 규칙(식별 가능한 일반 User-Agent, 요청 간격, 429 는 Retry-After 를 지키고 우회하지 않음)을 쓴다.
  이미 받은 파일은 건너뛰므로 다시 실행하면 못 받은 것만 이어받는다.
사용: python fetch_tour_photos.py
"""
import json
import os
import time

import fetch_dest_photos as base
from tour_theme_subjects import SUBJECTS

OUT = os.path.join(base.ROOT, "src", "main", "resources", "static", "img", "tour")
DEST_CREDITS = os.path.join(base.OUT, "credits.json")


def main():
    os.makedirs(OUT, exist_ok=True)
    cpath = os.path.join(OUT, "credits.json")
    credits = json.load(open(cpath, encoding="utf-8")) if os.path.exists(cpath) else {}
    dest_files = {v.get("file") for v in json.load(open(DEST_CREDITS, encoding="utf-8")).values()}
    for tid, (lang, titles, label) in sorted(SUBJECTS.items()):
        key = "tour-%d" % tid
        dest = os.path.join(OUT, key + ".jpg")
        if os.path.exists(dest) and key in credits:
            continue
        found = None
        try:
            for title in titles:
                r = base.page_image(lang, title)
                time.sleep(base.DELAY)
                if r and r[1] not in dest_files:
                    found = r + (title,)
                    break
        except Exception as e:  # noqa  한도 등으로 실패하면 이 항목만 건너뛰고 다음 실행에서 다시 시도
            print("LOOKUP FAIL", key, e)
            continue
        if not found:
            print("NO IMAGE", key, titles)
            continue
        thumb, fname, page_title, used = found
        try:
            blob = base.get(thumb, binary=True)
        except Exception as e:  # noqa
            print("DOWNLOAD FAIL", key, e)
            continue
        time.sleep(base.DELAY)
        if not blob or len(blob) < 5000:
            print("EMPTY", key)
            continue
        open(dest, "wb").write(blob)
        base.shrink(dest, 640)
        try:
            c = base.file_credit(fname)
        except Exception as e:  # noqa
            print("CREDIT FAIL", key, e)
            os.remove(dest)
            continue
        time.sleep(base.DELAY)
        c.update({"subject": used, "label": label, "file": fname, "wiki": lang})
        credits[key] = c
        json.dump(credits, open(cpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
        print("OK", key, used, "|", c["license"])
    print("files", len([f for f in os.listdir(OUT) if f.endswith(".jpg")]), "/", len(SUBJECTS))


if __name__ == "__main__":
    main()
