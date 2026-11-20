# -*- coding: utf-8 -*-
"""호텔·크루즈 더미 데이터. tour_data.emit 이 투어 생성 뒤에 호출한다. (11/20)

호텔: 해외 여행지 3곳 기준 3개씩, 이달의 기획·베스트셀러 6곳은 7개씩, 국내 도시 10곳은 3개씩 = 201개.
      (운항 불가 여행지는 만들지 않는다.) 이름·가격은 모두 가상이다.
크루즈: 항구와 가까운 해외 여행지 7곳에 1개씩.
"""
import hashlib

GRADE_BASE = {3: 80000, 4: 150000, 5: 280000}      # 1박 기준가(아시아·원화)
REGION_FACTOR = {"ASIA": 1.0, "EUROPE": 1.4, "NORTH_AMERICA": 1.5, "SOUTH_AMERICA": 1.1,
                 "MIDDLE_EAST": 1.2, "AFRICA": 1.1, "OCEANIA": 1.4, "DOMESTIC": 0.7}
SUFFIX = {3: ["시티 인", "스테이 호텔", "파크 호텔"], 4: ["플라자 호텔", "가든 호텔", "센트럴 호텔"], 5: ["그랜드 호텔", "로열 팰리스", "오션 리조트"]}
AREAS = ["시내 중심", "역 인근", "구시가지", "해변·항구", "쇼핑가", "공원 옆", "공항 인근"]
AMENITY = {3: ["무료 Wi-Fi", "24시간 프런트", "조식 옵션", "짐 보관"],
           4: ["무료 Wi-Fi", "피트니스", "레스토랑", "공항 셔틀", "조식 포함"],
           5: ["스파", "수영장", "컨시어지", "루프톱 바", "조식 포함", "객실 내 라운지"]}
GRADES_3 = [3, 4, 5]
GRADES_7 = [3, 3, 4, 4, 4, 5, 5]

# (여행지, 크루즈 이름, 배 이름, 출항 항구, 일정, 박수, 내측 객실가, 발코니 객실가, 하이라이트)
CRUISES = [
    ("바르셀로나", "서부 지중해 7박 크루즈", "나도감 메디호", "바르셀로나 항", "바르셀로나 → 마르세유 → 제노바 → 나폴리 → 팔마 → 바르셀로나", 7, 1290000, 1790000, "선상 파에야 쿠킹 클래스, 항구별 반일 시티 투어, 갑판 야외 영화"),
    ("로마", "이탈리아·그리스 8박 크루즈", "나도감 로마호", "치비타베키아 항(로마)", "로마 → 나폴리 → 카타니아 → 코르푸 → 산토리니 → 로마", 8, 1490000, 2090000, "산토리니 석양 감상, 선상 젤라토 바, 나폴리 피자 체험"),
    ("이스탄불", "에게해 7박 크루즈", "나도감 보스포러스호", "이스탄불 항", "이스탄불 → 쿠사다시 → 로도스 → 미코노스 → 아테네 → 이스탄불", 7, 1190000, 1690000, "에페소스 유적 반일 투어, 터키식 목욕 하맘 체험, 선상 터키 커피"),
    ("리스본", "대서양 섬 8박 크루즈", "나도감 테주호", "리스본 항", "리스본 → 카디스 → 말라가 → 퐁샬(마데이라) → 리스본", 8, 1390000, 1950000, "마데이라 와인 시음, 선상 파두 공연, 에그타르트 베이킹"),
    ("시드니", "남태평양 9박 크루즈", "나도감 오페라호", "시드니 서큘러키 항", "시드니 → 브리즈번 → 누메아 → 마레 섬 → 시드니", 9, 1790000, 2490000, "스노클링과 해변 휴식, 선상 선셋 요가, 오페라하우스 야경 출항"),
    ("밴쿠버", "알래스카 7박 크루즈", "나도감 글레이셔호", "밴쿠버 캐나다 플레이스 항", "밴쿠버 → 케치칸 → 주노 → 스캐그웨이 → 빅토리아 → 밴쿠버", 7, 1590000, 2290000, "빙하 감상 데크, 고래 관찰 투어, 알래스카 연어 요리"),
    ("호놀룰루", "하와이 제도 7박 크루즈", "나도감 알로하호", "호놀룰루 항", "호놀룰루 → 마우이 → 코나 → 힐로 → 카우아이 → 호놀룰루", 7, 1690000, 2390000, "훌라 댄스 레슨, 화산 국립공원 반일 투어, 선상 루아우 디너"),
]


def h(s):
    return int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16)


def hotels_for(place, region, count):
    """한 곳의 호텔 목록 [(이름, 등급, 지역, 소개, 편의시설, 1박 가격)]"""
    grades = GRADES_7 if count == 7 else GRADES_3
    used = {3: 0, 4: 0, 5: 0}
    out = []
    for i, g in enumerate(grades):
        key = f"{place}{g}{used[g]}"
        suffix = SUFFIX[g][(h(place + str(g)) + used[g]) % 3]
        used[g] += 1
        area = AREAS[h(key) % len(AREAS)]
        pool = AMENITY[g]
        start = h(key + "a") % len(pool)
        amen = ", ".join(pool[(start + k) % len(pool)] for k in range(3))
        price = round(GRADE_BASE[g] * REGION_FACTOR[region] / 10000) * 10000 + (h(key + "p") % 3) * 10000
        out.append((f"{place} {suffix}", g, area, f"{place} {area}에 있는 {g}성급 호텔. 여행 동선 중심에 있어 이동이 편하다.", amen, price))
    return out


def emit(w, q, dest_id, dest_region, city_id, featured, excluded):
    """dest_id: 여행지 이름→id, dest_region: 이름→권역, city_id: 국내 도시 이름→id. 만든 수를 돌려 준다."""
    stats = {"hotels": 0, "cruises": 0}
    sort = 0

    def add(dest, city, place, region, count):
        nonlocal sort
        for name, g, area, summary, amen, price in hotels_for(place, region, count):
            sort += 1
            w("INSERT INTO hotel (destination_id, city_id, name, grade, area, summary, amenities, price_per_night, status, sort_order) VALUES "
              f"({dest if dest else 'NULL'}, {city if city else 'NULL'}, {q(name)}, {g}, {q(area)}, {q(summary)}, {q(amen)}, {price}, 'ON_SALE', {sort});")
            stats["hotels"] += 1

    w("-- [N] 호텔: 해외 3개씩(이달의 기획·베스트셀러 6곳은 7개), 국내 도시 3개씩")
    for place, did in dest_id.items():
        if place in excluded:
            continue
        add(did, None, place, dest_region[place], 7 if place in featured else 3)
    for place, cid in city_id.items():
        add(None, cid, place, "DOMESTIC", 3)
    w("")

    w("-- [N] 크루즈 7곳(항구 도시)")
    for i, (place, title, ship, port, route, nights, inside, balcony, hl) in enumerate(CRUISES, start=1):
        w("INSERT INTO cruise (destination_id, title, ship_name, departure_port, itinerary, nights, price_inside, price_balcony, highlights, status, sort_order) VALUES "
          f"({dest_id[place]}, {q(title)}, {q(ship)}, {q(port)}, {q(route)}, {nights}, {inside}, {balcony}, {q(hl)}, 'ON_SALE', {i});")
        stats["cruises"] += 1
    w("")
    return stats
