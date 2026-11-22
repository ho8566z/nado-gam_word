# -*- coding: utf-8 -*-
"""여행지 카드용 대표 관광지 사진을 Wikipedia/Wikimedia Commons 에서 내려받는다.

- 도시마다 대표 관광지 문서(LANDMARKS)의 대표 이미지를 쓰고, 이미지가 없으면 도시 문서의 이미지로 대신한다.
- 실제로 내려받은 사진만 저장하고, 못 받은 도시는 결과에서 빠진다(카드는 기존 그라데이션 유지).
- 사진 파일: nado-gam/src/main/resources/static/img/dest/{overseas|domestic}-{번호}.jpg
- 출처·저작자·라이선스: nado-gam/src/main/resources/static/img/dest/credits.json (화면의 사진 출처 표기에 쓴다)
- Wikimedia 정책에 따라 식별 가능한 User-Agent 를 쓰고 요청 사이에 간격을 둔다. 이미 받은 파일은 건너뛰므로 다시 실행해도 된다.
사용: python fetch_dest_photos.py
"""
import json, os, re, sys, time, urllib.parse, urllib.request, urllib.error

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nado-gam'))
OUT = os.path.join(ROOT, 'src', 'main', 'resources', 'static', 'img', 'dest')
UA = 'nado-gam-student-project/1.0 (educational portfolio project; low-rate photo fetch)'  # 개인 연락처는 넣지 않는다
THUMB = 960  # Wikimedia 표준 썸네일 폭
DELAY = 1.5  # 요청 사이 간격(초). 한도에 걸리지 않도록 느리게 받는다

# 해외 여행지 번호(sort_order) -> (영어 도시 문서, 대표 관광지 영어 문서)
OVERSEAS = {
    1: ('Paris', 'Eiffel Tower'), 2: ('London', 'Tower Bridge'), 3: ('Berlin', 'Brandenburg Gate'),
    4: ('Madrid', 'Royal Palace of Madrid'), 5: ('Rome', 'Colosseum'), 6: ('Barcelona', 'Sagrada Família'),
    7: ('Seoul', 'Gyeongbokgung'), 8: ('Busan', 'Gamcheon Culture Village'), 9: ('Tokyo', 'Tokyo Tower'),
    10: ('Osaka', 'Osaka Castle'), 11: ('Fukuoka', 'Fukuoka Tower'), 12: ('Sapporo', 'Sapporo Clock Tower'),
    13: ('Beijing', 'Forbidden City'), 14: ('Bangkok', 'Wat Arun'), 15: ('Vladivostok', 'Zolotoy Bridge'),
    16: ('New York City', 'Statue of Liberty'), 17: ('Washington, D.C.', 'Lincoln Memorial'),
    18: ('Los Angeles', 'Hollywood Sign'), 19: ('Hong Kong', 'Victoria Harbour'),
    20: ('Shanghai', 'Oriental Pearl Tower'), 21: ('Dubai', 'Burj Khalifa'), 22: ('Chicago', 'Cloud Gate'),
    23: ('Sydney', 'Sydney Opera House'), 24: ('Vancouver', 'Stanley Park'), 25: ('São Paulo', 'Avenida Paulista'),
    26: ('Cairo', 'Great Pyramid of Giza'), 27: ('Cape Town', 'Table Mountain'), 28: ('Milan', 'Milan Cathedral'),
    29: ('Amsterdam', 'Canals of Amsterdam'), 30: ('Istanbul', 'Hagia Sophia'), 31: ('Prague', 'Charles Bridge'),
    32: ('Vienna', 'Schönbrunn Palace'), 33: ('Lisbon', 'Belém Tower'), 34: ('Edinburgh', 'Edinburgh Castle'),
    35: ('Singapore', 'Marina Bay Sands'), 36: ('Macau', "Ruins of St. Paul's"), 37: ('Taipei', 'Taipei 101'),
    38: ('Da Nang', 'Dragon Bridge (Da Nang)'), 39: ('Nha Trang', 'Po Nagar'), 40: ('Phú Quốc', 'Phú Quốc'),
    41: ('Bali', 'Tanah Lot'), 42: ('Hanoi', 'Hoàn Kiếm Lake'),
    43: ('Ho Chi Minh City', 'Saigon Notre-Dame Basilica'), 44: ('Kuala Lumpur', 'Petronas Towers'),
    45: ('San Francisco', 'Golden Gate Bridge'), 46: ('Toronto', 'CN Tower'), 47: ('Honolulu', 'Diamond Head, Hawaii'),
    48: ('Mexico City', 'Palacio de Bellas Artes'), 49: ('Melbourne', 'Flinders Street railway station'),
    50: ('Guam', 'Two Lovers Point'), 51: ('Manila', 'Intramuros'), 52: ('New Delhi', 'India Gate'),
    53: ('Mumbai', 'Gateway of India'), 54: ('Bangalore', 'Vidhana Soudha'), 55: ('Colombo', 'Gangaramaya Temple'),
    56: ('Kathmandu', 'Boudhanath'), 57: ('Ulaanbaatar', 'Gandantegchinlen Monastery'),
    58: ('Almaty', 'Ascension Cathedral, Almaty'), 59: ('Tashkent', 'Hazrati Imam Complex'),
    60: ('Jakarta', 'National Monument (Indonesia)'), 61: ('Guangzhou', 'Canton Tower'),
    62: ('Chengdu', 'Chengdu Research Base of Giant Panda Breeding'), 63: ('Doha', 'Museum of Islamic Art, Doha'),
    64: ('Riyadh', 'Kingdom Centre'), 65: ('Tel Aviv', 'Jaffa'), 66: ('Jeddah', "King Fahd's Fountain"),
    67: ('Frankfurt', 'Römerberg'), 68: ('Zürich', 'Grossmünster'), 69: ('Budapest', 'Hungarian Parliament Building'),
    70: ('Warsaw', 'Royal Castle, Warsaw'), 71: ('Copenhagen', 'Nyhavn'), 72: ('Stockholm', 'Gamla stan'),
    73: ('Oslo', 'Oslo Opera House'), 74: ('Helsinki', 'Helsinki Cathedral'), 75: ('Dublin', "Ha'penny Bridge"),
    76: ('Athens', 'Parthenon'), 77: ('Nairobi', 'Nairobi National Park'), 78: ('Johannesburg', 'Soweto'),
    79: ('Casablanca', 'Hassan II Mosque'), 80: ('Addis Ababa', 'Holy Trinity Cathedral, Addis Ababa'),
    81: ('Dar es Salaam', 'Dar es Salaam'), 82: ('Tunis', 'Medina of Tunis'), 83: ('Accra', 'Independence Square, Accra'),
    84: ('Seattle', 'Space Needle'), 85: ('Dallas', 'Reunion Tower'), 86: ('Miami', 'South Beach'),
    87: ('Denver', 'Red Rocks Park and Amphitheatre'), 88: ('Montreal', 'Notre-Dame Basilica (Montreal)'),
    89: ('Cancún', 'Chichen Itza'), 90: ('Panama City', 'Miraflores Locks'),
    91: ('Rio de Janeiro', 'Christ the Redeemer (statue)'), 92: ('Buenos Aires', 'Obelisk of Buenos Aires'),
    93: ('Santiago', 'San Cristóbal Hill'), 94: ('Lima', 'Plaza Mayor, Lima'), 95: ('Bogotá', 'Monserrate'),
    96: ('Quito', 'Basílica del Voto Nacional'), 97: ('Brisbane', 'South Bank Parklands'),
    98: ('Perth', 'Kings Park, Perth'), 99: ('Auckland', 'Sky Tower (Auckland)'),
    100: ('Nadi', 'Sri Siva Subramaniya Swami Temple, Nadi'),
}
# 국내 도시 번호(sort_order) -> (한국어 도시 문서, 대표 관광지 한국어 문서)
DOMESTIC = {
    1: ('경주시', '불국사'), 2: ('강릉시', '경포대'), 3: ('속초시', '설악산'), 4: ('부산광역시', '광안대교'),
    5: ('제주시', '성산 일출봉'), 6: ('전주시', '전주 한옥마을'), 7: ('여수시', '오동도'),
    8: ('순천시', '순천만'), 9: ('통영시', '동피랑 벽화마을'), 10: ('단양군', '도담삼봉'),
}


def get(url, binary=False, tries=4):
    """한도(429)에 걸리면 Retry-After 를 지키며 기다린다. 끝내 안 되면 예외를 낸다(호출 쪽에서 그 항목만 건너뜀)."""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            return data if binary else json.loads(data.decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 503) and i < tries - 1:
                wait = e.headers.get('Retry-After')
                time.sleep(min(int(wait), 120) if wait and wait.isdigit() else 30 * (i + 1))
                continue
            raise
    return None


def shrink(path, width=800):
    """저장소 용량을 줄이려고 가로 800px·품질 80 으로 다시 저장한다(Pillow 가 있을 때만)."""
    try:
        from PIL import Image
    except ImportError:
        return
    im = Image.open(path).convert('RGB')
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(path, 'JPEG', quality=80, optimize=True, progressive=True)


def page_image(lang, title):
    """문서 대표 이미지의 (썸네일 URL, Commons 파일명). 없으면 None."""
    url = 'https://%s.wikipedia.org/w/api.php?action=query&format=json&redirects=1&prop=pageimages&piprop=thumbnail|name&pithumbsize=%d&titles=%s' % (
        lang, THUMB, urllib.parse.quote(title))
    data = get(url)
    if not data:
        return None
    for p in data.get('query', {}).get('pages', {}).values():
        th = p.get('thumbnail')
        if th and p.get('pageimage'):
            return th['source'], p['pageimage'], p.get('title', title)
    return None


def file_credit(name):
    """Commons 파일의 저작자·라이선스·원본 페이지."""
    url = ('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=extmetadata|url'
           '&titles=File:%s' % urllib.parse.quote(name))
    data = get(url) or {}
    for p in data.get('query', {}).get('pages', {}).values():
        info = (p.get('imageinfo') or [{}])[0]
        meta = info.get('extmetadata', {})
        strip = lambda v: re.sub(r'<[^>]+>', '', v or '').strip()
        return {
            'author': strip(meta.get('Artist', {}).get('value'))[:120] or 'Unknown',
            'license': strip(meta.get('LicenseShortName', {}).get('value')) or 'See source',
            'source': info.get('descriptionurl') or 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(name),
        }
    return {'author': 'Unknown', 'license': 'See source', 'source': 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(name)}


def fetch_all(kind, table, lang):
    credits_path = os.path.join(OUT, 'credits.json')
    credits = json.load(open(credits_path, encoding='utf-8')) if os.path.exists(credits_path) else {}
    for num, (city, landmark) in table.items():
        key = '%s-%d' % (kind, num)
        dest = os.path.join(OUT, key + '.jpg')
        if os.path.exists(dest) and key in credits:
            continue
        found = None
        try:
            for title in (landmark, city):
                found = page_image(lang, title)
                time.sleep(DELAY)
                if found:
                    found = found + (title,)
                    break
        except Exception as e:  # noqa  한도 등으로 실패하면 이 항목만 건너뛰고 다음 실행에서 다시 시도
            print('LOOKUP FAIL', key, e); continue
        if not found:
            print('NO IMAGE', key, city, '/', landmark); continue
        thumb, fname, page_title, used = found
        try:
            blob = get(thumb, binary=True)
        except Exception as e:  # noqa
            print('DOWNLOAD FAIL', key, e); continue
        time.sleep(DELAY)
        if not blob or len(blob) < 5000:
            print('EMPTY', key); continue
        open(dest, 'wb').write(blob)
        shrink(dest)
        try:
            c = file_credit(fname)
        except Exception as e:  # noqa
            print('CREDIT FAIL', key, e); os.remove(dest); continue
        time.sleep(DELAY)
        c.update({'subject': used, 'file': fname, 'wiki': lang})
        credits[key] = c
        json.dump(credits, open(credits_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
        print('OK', key, used, '|', c['license'])


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fetch_all('overseas', OVERSEAS, 'en')
    fetch_all('domestic', DOMESTIC, 'ko')
    print('files', len([f for f in os.listdir(OUT) if f.endswith('.jpg')]))
