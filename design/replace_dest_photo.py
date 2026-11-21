# -*- coding: utf-8 -*-
"""여행지 카드 사진 한 장을 사용자가 지정한 Commons 파일로 바꾼다(저작자·라이선스는 Commons API 로 조회).
사용: python replace_dest_photo.py overseas-19 Hong_Kong_Harbour_Night_2019-06-11.jpg "Victoria Harbour"
fetch_dest_photos.py 와 같은 규칙(일반 User-Agent, 요청 간격)을 쓴다."""
import json
import os
import sys
import time
import urllib.parse

import fetch_dest_photos as base


def main(key, fname, subject):
    url = ('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url'
           '&iiurlwidth=%d&titles=File:%s' % (base.THUMB, urllib.parse.quote(fname)))
    data = base.get(url) or {}
    time.sleep(base.DELAY)
    thumb = None
    for p in data.get('query', {}).get('pages', {}).values():
        info = (p.get('imageinfo') or [{}])[0]
        thumb = info.get('thumburl') or info.get('url')
    assert thumb, 'thumb url not found'
    blob = base.get(thumb, binary=True)
    time.sleep(base.DELAY)
    assert blob and len(blob) > 5000, 'download failed'
    dest = os.path.join(base.OUT, key + '.jpg')
    open(dest, 'wb').write(blob)
    base.shrink(dest, 800)
    credit = base.file_credit(fname)
    credit.update({'subject': subject, 'file': fname, 'wiki': 'commons'})
    cpath = os.path.join(base.OUT, 'credits.json')
    credits = json.load(open(cpath, encoding='utf-8'))
    credits[key] = credit
    json.dump(credits, open(cpath, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
    print('OK', key, credit['license'], credit['author'])


if __name__ == '__main__':
    main(*sys.argv[1:4])
