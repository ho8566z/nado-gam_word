# -*- coding: utf-8 -*-
"""dest_captions.py 의 관광지·특산물 문구에 data.sql 의 도시 이름을 붙여 static/img/dest/info.json 을 만든다.
앱의 DestPhotos 가 이 파일(문구·이름 검색용)과 credits.json(받은 사진·출처)을 읽는다. data.sql 은 gen_data_sql.py 로 먼저 만들어 둔다.
사용: python gen_dest_info.py"""
import json, os, re

import dest_captions

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nado-gam'))
SQL = os.path.join(ROOT, 'src', 'main', 'resources', 'data.sql')
OUT = os.path.join(ROOT, 'src', 'main', 'resources', 'static', 'img', 'dest', 'info.json')


def names(table):
    text = open(SQL, encoding='utf-8').read()
    return [m.group(1) for m in re.finditer(r"INSERT INTO %s \([^)]*\) VALUES \('([^']*)'" % table, text)]


def main():
    out = {}
    for kind, table, caps in (('overseas', 'destination', dest_captions.OVERSEAS), ('domestic', 'domestic_city', dest_captions.DOMESTIC)):
        ko = names(table)
        assert len(ko) == len(caps), (kind, len(ko), len(caps))
        out[kind] = {str(i): {'name': ko[i - 1], 'landmark': caps[i][0], 'specialty': caps[i][1]} for i in range(1, len(ko) + 1)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('info.json', {k: len(v) for k, v in out.items()})


if __name__ == '__main__':
    main()
