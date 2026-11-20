# -*- coding: utf-8 -*-
"""국내 도시와 투어(해외·국내) 더미 데이터를 만든다. gen_data_sql.py 의 main() 이 호출한다. (11/20)

모든 투어 이름·브랜드·가격·일정은 가상이다. design/research/*.json 은 도시별 특산물·관광상품을 웹에서 조사한 메모(Haiku)이고,
여기서는 참고만 하며 문장을 그대로 쓰지 않는다. 규칙은 03_더미데이터설계서.md 8절을 따른다.
"""
import glob
import hashlib
import json
import os

import domestic_data
import hotel_data

HERE = os.path.dirname(os.path.abspath(__file__))

FOOD, SPORTS, ART = "FOOD_DRINK", "SPORTS_ACTIVITY", "ART_REST"
THEMES = [FOOD, SPORTS, ART]
THEME_KEY = {FOOD: "food", SPORTS: "sports", ART: "art"}
THEME_NAME = {FOOD: "미식·주류", SPORTS: "스포츠·액티비티", ART: "예술·휴식"}

# 세 테마를 모두 만드는 해외 여행지(이달의 기획 3곳 + 베스트셀러 3곳)
FEATURED = ["로마", "삿포로", "케이프타운", "도쿄", "로스앤젤레스", "홍콩"]
# 운항 불가라 투어를 만들지 않는 여행지
EXCLUDED = ["블라디보스토크"]
# 나머지 해외 여행지는 조사 결과의 best 테마 1개를 쓰되, 도시의 대표 특산물·관광상품에 더 맞는 쪽으로 바꾼 곳
BEST_OVERRIDE = {
    "바르셀로나": SPORTS,   # 축구 경기 관람
    "마드리드": SPORTS,     # 축구 경기 관람
    "런던": SPORTS,         # 프리미어리그 관람
    "뉴욕": SPORTS,         # 프로 농구·야구 관람
    "베를린": FOOD,         # 맥주·소시지
    "프라하": FOOD,         # 체코 맥주
    "이스탄불": FOOD,       # 튀르키예 음식
    "암스테르담": FOOD,     # 치즈·맥주
    "리스본": FOOD,         # 에그타르트·포트와인
    "에든버러": FOOD,       # 위스키 증류소
}

# (이름, 지역, 위도, 경도, 소개, 포스터 색 시작, 끝)
DOMESTIC = [
    ("경주", "경북", 35.8562, 129.2247, "천년 신라의 수도, 도시 전체가 야외 박물관", "#c0842b", "#7a3b12"),
    ("강릉", "강원", 37.7519, 128.8761, "동해 바다와 커피 거리, 초당 두부의 도시", "#1c7ed6", "#0b3d66"),
    ("속초", "강원", 38.2070, 128.5918, "설악산과 동해가 만나는 항구 도시", "#2f9e44", "#0b5a3a"),
    ("부산", "경남", 35.1796, 129.0756, "해운대와 광안대교, 자갈치 시장의 바다 도시", "#ff6b6b", "#7d2a4d"),
    ("제주", "제주", 33.4996, 126.5312, "한라산과 바다, 돌담과 귤밭의 섬", "#20c997", "#0b6e4f"),
    ("전주", "전북", 35.8242, 127.1480, "한옥마을과 비빔밥, 막걸리 골목의 맛의 도시", "#e67700", "#8a3b00"),
    ("여수", "전남", 34.7604, 127.6622, "밤바다와 케이블카, 돌산 갓김치의 남해 항구", "#4c6ef5", "#1b2a6b"),
    ("순천", "전남", 34.9506, 127.4872, "순천만 습지와 국가정원이 있는 생태 도시", "#82c91e", "#2b6a1c"),
    ("통영", "경남", 34.8544, 128.4331, "한려수도와 충무김밥, 예술가의 항구", "#15aabf", "#0b4f6c"),
    ("단양", "충북", 36.9845, 128.3655, "남한강과 도담삼봉, 패러글라이딩의 고장", "#7950f2", "#3b2a8a"),
]

# 콜라보 브랜드(모두 가상): 테마별 풀
BRANDS = {
    FOOD: ["푸른보리 양조장", "금빛밀 베이커리", "달빛 와이너리", "은하수 제면소", "바람결 증류소", "햇살 올리브농장",
           "구름 치즈공방", "소금꽃 식초공방", "참나무 위스키", "별빛 초콜릿공방", "새벽 커피로스터스", "한입 소스상회"],
    SPORTS: ["바람개비 아웃도어", "파도소리 서프클럽", "거코 스포츠", "구름 러닝크루", "산들 트레킹", "물결 카약스쿨"],
    ART: ["고요숲 스파", "수채 아틀리에", "달무리 공연장", "온기 온천마을", "유리잔 공방", "느린걸음 티하우스"],
}

# 지역별 하루 현지 상품가(항공권·호텔 제외, 가이드·차량·입장료·체험비·식사)
REGION_NIGHT = {"ASIA": 70000, "EUROPE": 100000, "NORTH_AMERICA": 110000, "SOUTH_AMERICA": 105000,
                "MIDDLE_EAST": 95000, "AFRICA": 100000, "OCEANIA": 100000}
THEME_MULT = {FOOD: 1.0, SPORTS: 1.15, ART: 1.05}

SHORT_NIGHTS = [2, 3, 6]      # 인천 기준 비행 6시간 이하
LONG_NIGHTS = [6, 9, 13]      # 6시간 초과
DOMESTIC_NIGHTS = [1, 2, 3]


def h(s):
    return int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16)


def load_research():
    """(해외 도시 조사, 국내 도시 조사). 해외 '부산'과 국내 '부산'이 겹치므로 research_E.json 의 홍콩 외 도시는 국내로 나눈다."""
    overseas, domestic = {}, {}
    for f in sorted(glob.glob(os.path.join(HERE, "research", "research_*.json"))):
        for c in json.load(open(f, encoding="utf-8")):
            if f.endswith("research_E.json") and c["city"] != "홍콩":
                domestic[c["city"]] = c
            else:
                overseas[c["city"]] = c
    return overseas, domestic


def fit(s, n):
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


# ---------------------------------------------------------------- 일정 만들기
def mid_days(theme, city, items, brand):
    """테마별 중간 일차 후보. 상품마다 순서대로 쓰고, 긴 기간은 뒤에 더 붙는다."""
    a, b, c = (items + items)[:3] if len(items) < 3 else items[:3]
    if theme == FOOD:
        return [
            (f"{a['name']} 탐방", f"{a['note']}. 현지 가이드와 함께 대표 맛집과 시장을 돌며 점심과 간식을 맛봅니다."),
            (f"{brand} 견학과 시음", f"{brand}(가상)의 공방을 둘러보고 시음 코스를 즐깁니다. {b['name']}과 어울리는 한 잔을 곁들입니다."),
            (f"{c['name']} 체험", f"{c['note']}. 직접 맛보고 고르는 시간을 가진 뒤 저녁은 현지 식당에서 합니다."),
            ("쿠킹 클래스", f"현지 셰프에게 {city}의 대표 요리를 배우고 직접 만든 요리로 저녁을 먹습니다."),
            ("근교 산지 미식 여행", f"{city} 근교의 산지로 이동해 제철 재료와 지역 음식을 맛보고 농장·공방을 방문합니다."),
            (f"{b['name']} 깊이 보기", f"{b['note']}. 전문 가이드의 설명과 함께 두 번째 코스를 즐깁니다."),
            ("시장 쇼핑과 자유 시간", "현지 시장과 상점가에서 기념품과 식재료를 둘러보고 자유 시간을 보냅니다."),
            ("로컬 맛집 릴레이", "가이드가 고른 현지 단골 식당 세 곳을 이어서 맛보는 미식 산책입니다."),
            ("디저트·카페 투어", f"{city}의 유명 디저트와 카페를 돌며 여유로운 오후를 보냅니다."),
            ("현지 가정식 초대", "현지 가정집 식탁에서 가정식을 함께 먹으며 이야기를 나눕니다."),
            ("자유 일정", "하루는 자유롭게 보냅니다. 가이드가 추천 맛집 지도를 드립니다."),
            ("야시장·야경 산책", "저녁 시장과 야경 명소를 걸으며 길거리 음식을 맛봅니다."),
        ]
    if theme == SPORTS:
        return [
            (f"{a['name']}", f"{a['note']}. 현지 가이드와 함께 경기장·현장 분위기를 즐깁니다."),
            (f"{b['name']} 체험", f"{b['note']}. 초보자도 따라 할 수 있도록 강사가 안내합니다."),
            (f"{c['name']}", f"{c['note']}. 장비 대여와 안전 교육이 포함됩니다."),
            ("근교 트레킹·야외 활동", f"{city} 근교의 자연으로 이동해 가볍게 걷고 풍경을 즐기는 액티비티를 합니다."),
            ("경기장·스포츠 문화 투어", "경기장 내부와 박물관을 둘러보며 현지 스포츠 문화를 배웁니다."),
            ("체험 레슨", "현지 코치에게 짧은 레슨을 받고 미니 게임으로 마무리합니다."),
            ("자유 일정과 휴식", "활동 사이 하루는 자유롭게 쉬며 근육을 풀 시간을 가집니다."),
            (f"{a['name']} 심화 코스", "가이드와 함께 한 단계 높은 코스에 도전합니다."),
            ("강변·해변 러닝과 요가", "아침 러닝이나 요가로 몸을 깨운 뒤 도시를 가볍게 둘러봅니다."),
            ("현지 팀 팬 모임", "현지 팬들과 함께 응원 문화를 체험하고 기념품을 고릅니다."),
            ("물가 액티비티", "수상·해안 액티비티를 즐기고 온천이나 스파로 피로를 풉니다."),
            ("로컬 스포츠 클래스", "현지에서 사랑받는 전통 스포츠를 배우는 체험 수업입니다."),
        ]
    return [
        (f"{a['name']}", f"{a['note']}. 전문 도슨트의 설명과 함께 천천히 감상합니다."),
        (f"{b['name']}", f"{b['note']}. 여유롭게 둘러본 뒤 근처 카페에서 쉬어 갑니다."),
        (f"{c['name']}", f"{c['note']}. 공연이나 전시 일정에 맞춰 관람 시간을 조정합니다."),
        ("공연·전시 관람", f"{city}에서 열리는 공연 또는 전시 중 일정에 맞는 한 편을 관람합니다."),
        ("스파·휴식의 날", "스파나 온천, 마사지 등 느린 휴식으로 여행의 피로를 풉니다."),
        ("근교 소도시 산책", f"{city} 근교의 작은 마을을 산책하며 갤러리와 공방을 둘러봅니다."),
        ("전통 체험 클래스", "현지 공예 또는 전통 문화 체험 수업에 참여해 작품을 만듭니다."),
        ("자유 일정", "하루는 자유롭게 보냅니다. 가이드가 추천 산책로와 전시 정보를 드립니다."),
        ("정원·공원 힐링 산책", "도심 공원과 정원을 걸으며 사색하는 시간을 가집니다."),
        ("야경과 재즈·클래식의 밤", "저녁에는 야경 명소를 보고 가벼운 공연을 즐깁니다."),
        ("미술관 한 곳 더", f"{a['name']} 외에 가이드가 고른 작은 미술관을 한 곳 더 방문합니다."),
        ("티타임과 독서의 오후", "현지 찻집에서 천천히 차를 마시며 하루를 정리합니다."),
    ]


def build_days(theme, city, items, brand, nights, depart_label, domestic):
    total = nights + 1
    mids = mid_days(theme, city, items, brand)
    days = []
    start = "서울" if domestic else "인천"
    first_act = mids[0]
    if nights == 1:
        days.append((f"{city} 도착과 대표 체험", f"{start}에서 출발해 {city}에 도착합니다. 가이드와 만나 {first_act[1]}"))
    else:
        days.append((f"{city} 도착", f"{start}에서 출발해 {city}에 도착합니다{'' if domestic else '(항공권 별도)'}. 숙소에 짐을 풀고 가이드 미팅과 환영 안내, 가벼운 저녁 식사를 합니다."))
        for i in range(nights - 1):
            days.append(mids[i % len(mids)] if i < len(mids) else (f"{mids[i % len(mids)][0]} (심화)", mids[i % len(mids)][1]))
    days.append((f"체크아웃과 출발", f"조식 후 체크아웃하고 {depart_label}으로 이동합니다. 아쉬운 마음으로 여행을 마무리합니다."))
    assert len(days) == total, (city, theme, nights, len(days), total)
    return days


# ---------------------------------------------------------------- 포함·불포함·가격
def includes_text(theme):
    base = ["현지 한국어 가이드 동행", "일정표에 있는 현지 이동 차량", "일정표의 입장료·체험비"]
    extra = {FOOD: ["일정에 표시된 식사와 시음"], SPORTS: ["경기 관람 티켓 또는 액티비티 이용권·장비 대여"], ART: ["미술관·공연 입장권 또는 스파 이용권"]}[theme]
    return "\n".join(base + extra)


def excludes_text(domestic):
    lines = ["호텔 숙박(호텔 메뉴에서 별도 선택)", "개인 경비와 쇼핑", "여행자 보험", "선택 관광과 가이드 팁"]
    lines.insert(0, "서울 출발 이동편(국내여행 메뉴에서 별도 선택)" if domestic else "국제선 항공권(해외 여행 메뉴에서 별도 선택)")
    return "\n".join(lines)


def price(place, theme, nights, region, domestic):
    var = 0.92 + (h(place) % 17) / 100.0
    if domestic:
        base = 50000 + 50000 * nights
    else:
        base = 150000 + REGION_NIGHT[region] * nights
    return int(round(base * THEME_MULT[theme] * var / 10000.0)) * 10000


# ---------------------------------------------------------------- SQL 생성
def emit(w, q, dest_id, dest_region, min_icn_minutes):
    """w: 줄 추가 함수, q: SQL 문자열 이스케이프. dest_id: 여행지 이름→id. dest_region: 이름→권역. min_icn_minutes: 이름→인천발 최단 분."""
    research_overseas, research_domestic = load_research()
    stats ={"overseas": 0, "domestic": 0, "options": 0, "days": 0}

    w("-- [M] 국내 여행지 10곳 (경주·강릉·속초·부산·제주·전주·여수·순천·통영·단양)")
    city_id = {}
    for i, (name, prov, lat, lng, summary, c1, c2) in enumerate(DOMESTIC, start=1):
        city_id[name] = i
        w("INSERT INTO domestic_city (name_ko, province, latitude, longitude, summary, poster_color_from, poster_color_to, status, sort_order) VALUES "
          f"({q(name)}, {q(prov)}, {lat}, {lng}, {q(summary)}, {q(c1)}, {q(c2)}, 'AVAILABLE', {i});")
    w("")
    stats["transports"] = domestic_data.emit_transport(w, q, city_id)

    state = {"tour": 0, "option": 0, "sort": 0}

    def add_tour(scope, place, theme, region, nights_list, domestic, dest, city):
        r = (research_domestic if domestic else research_overseas)[place]
        items = r[THEME_KEY[theme]]
        assert len(items) >= 2, (place, theme)
        first, second = items[0], items[1]
        brand_pool = BRANDS[theme]
        use_brand = theme == FOOD or h(place + theme) % 2 == 0
        brand = brand_pool[h(place + theme) % len(brand_pool)] if use_brand else None
        # 일정 문구에 쓸 브랜드는 음식 투어만 필수
        day_brand = brand or BRANDS[FOOD][h(place) % len(BRANDS[FOOD])]
        title = fit(f"{place} {THEME_NAME[theme]} 투어: {first['name']} · {second['name']}", 100)
        subtitle = fit(f"{first['note']}. {second['note']}.", 200)
        highlights = "\n".join(f"{it['name']} — {it['note']}" for it in items[:3])
        state["tour"] += 1
        state["sort"] += 1
        tour_id = state["tour"]
        dest_sql = dest_id[dest] if dest else "NULL"
        city_sql = city_id[city] if city else "NULL"
        w("INSERT INTO tour (scope, destination_id, city_id, theme, title, subtitle, collab_brand, highlights, includes, excludes, source_note, status, sort_order) VALUES "
          f"({q(scope)}, {dest_sql}, {city_sql}, {q(theme)}, {q(title)}, {q(subtitle)}, {q(brand)}, {q(fit(highlights, 500))}, "
          f"{q(includes_text(theme))}, {q(excludes_text(domestic))}, {q(fit('웹 조사 참고: ' + ', '.join(i['name'] for i in items[:3]) + ' (상품·브랜드는 가상)', 200))}, 'ON_SALE', {state['sort']});")
        depart = "역·터미널" if domestic else "공항"
        for nights in nights_list:
            state["option"] += 1
            opt_id = state["option"]
            p = price(place, theme, nights, region, domestic)
            w("INSERT INTO tour_option (tour_id, nights, days, price_per_person, min_people, max_people) VALUES "
              f"({tour_id}, {nights}, {nights + 1}, {p}, {2 if not domestic else 2}, {20 if not domestic else 30});")
            for no, (dt, dd) in enumerate(build_days(theme, place, items, day_brand, nights, depart, domestic), start=1):
                w("INSERT INTO tour_day (option_id, day_no, title, description) VALUES "
                  f"({opt_id}, {no}, {q(fit(dt, 100))}, {q(fit(dd, 500))});")
                stats["days"] += 1
            stats["options"] += 1
        stats["domestic" if domestic else "overseas"] += 1

    w("-- [M] 해외 투어: 이달의 기획 3곳·베스트셀러 3곳은 3테마 전부, 나머지는 도시를 대표하는 1테마 (블라디보스토크 제외)")
    for place, region in dest_region.items():
        if place in EXCLUDED:
            continue
        minutes = min_icn_minutes.get(place)
        short = minutes is None or minutes <= 360   # 서울·부산은 인천 출발 항공편이 없어 단거리 기준을 쓴다
        nights_list = SHORT_NIGHTS if short else LONG_NIGHTS
        if place in FEATURED:
            themes = THEMES
        else:
            themes = [BEST_OVERRIDE.get(place, research_overseas[place]["best"])]
        for theme in themes:
            add_tour("OVERSEAS", place, theme, region, nights_list, False, place, None)
    w("")
    w("-- [M] 국내 투어: 10개 도시 × 3테마 (1박2일·2박3일·3박4일)")
    for name, *_ in DOMESTIC:
        for theme in THEMES:
            add_tour("DOMESTIC", name, theme, None, DOMESTIC_NIGHTS, True, None, name)
    w("")
    stats.update(hotel_data.emit(w, q, dest_id, dest_region, city_id, FEATURED, EXCLUDED))
    return stats
