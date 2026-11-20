# -*- coding: utf-8 -*-
"""신규 여행지 50곳의 인천발 항공편을 만들어 flight_dummy.csv 에 덧붙인다. (11/21)

실행: python gen_expand_flights.py  (이미 덧붙였으면 아무것도 하지 않는다)
도시당 3편: 직항 도시는 직항 2편 + 경유 1편, 경유 도시는 경유 3편. 항공사·편명·가격은 모두 가상이다.
시간·가격은 거리로 계산한다(파리 직항 14h20·89만원을 기준으로 맞춘 식). 도착 시각은 현지 표준시 기준이다.
"""
import csv
import hashlib
import math
import os

import expand_data as E
import gen_data_sql as G

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "flight_dummy.csv")

KOREAN_FSC = ["MG", "AQ"]
LCC_SHORT = ["BD", "HR", "NU", "BS", "LT", "MJ", "BO", "SB", "HX"]   # 5,500km 미만 직항 2번째 편에 쓴다
REGION_FSC = {
    "ASIA": ["SM", "EB", "SK", "DS", "AZ", "PL", "FM", "RR", "NS", "MA", "LC"],
    "MIDDLE_EAST": ["OA", "GF", "BN"],
    "EUROPE": ["GL", "RH", "TH", "AP", "TL", "BP", "LP"],
    "AFRICA": ["BN", "AT", "OA"],
    "NORTH_AMERICA": ["PC", "AT", "UW", "ML", "ZT"],
    "SOUTH_AMERICA": ["AT", "UW", "ZT"],
    "OCEANIA": ["SX", "RI", "PC"],
}
HUB_AIRLINE = {   # 경유 거점 → 그 거점을 쓰는 가상 항공사
    "IST": "BP", "FRA": "RH", "HEL": "LP", "DXB": "OA", "DOH": "GF", "ADD": "BN", "TPE": "FM", "SIN": "LC", "SEA": "PC",
    "HNL": "PC", "LAX": "UW", "JFK": "UW", "SFO": "PC", "ORD": "UW", "GRU": "AT", "MEX": "ZT", "CDG": "GL", "LHR": "TH",
    "AMS": "TL", "YYZ": "ML", "HKG": "DS", "PEK": "AZ", "PVG": "AZ", "BKK": "SM", "KUL": "MA", "SYD": "SX", "DEL": "EB",
}
DIRECT_SLOTS = ["09:30", "11:10", "13:40", "16:20", "19:30", "22:15"]
VIA_SLOTS = ["08:30", "13:10", "21:30", "23:40"]


def h(s):
    return int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16)


def fmt(m):
    return f"{m // 60}h{m % 60:02d}"


def leg(a, b):
    return round(G.km(a, b) / 650 * 60) + 40


def tz(code):
    return E.TZ_OFFSET[G.AP[code][7]]


def money(v):
    return int(round(v / 10000.0)) * 10000


def build():
    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))
    if any(r["id"] == "F155" for r in rows):
        print("이미 추가되어 있습니다:", len(rows), "편")
        return
    used_no = {r["flight_no"] for r in rows}
    region_of = {c[0]: c[3] for c in G.COUNTRIES}
    country_of = {d[0]: d[2] for d in G.DESTINATIONS}
    next_id = len(rows) + 1
    out = []

    def flight_no(code, key):
        n = 100 + h(key) % 900
        while code + str(n) in used_no:
            n += 1
        used_no.add(code + str(n))
        return code + str(n)

    def add(dest, apt, code, via, dep, total, e_price, p_price, b_price):
        nonlocal next_id
        arr_local = dep_min(dep) + total + round((tz(apt) - 9) * 60)
        day, mm = divmod(arr_local, 1440)
        out.append({
            "id": f"F{next_id:03d}", "tag": "", "dest": dest_name, "flight_no": flight_no(code, dest + dep + str(via)),
            "airline": G.AIRLINES[code][0], "type": "경유" if via else "직항", "origin": "ICN", "via": via or "",
            "arr_airport": apt, "dep": dep, "arr": f"{mm // 60:02d}:{mm % 60:02d}", "arr_day": day, "duration": fmt(total),
            "E": e_price, "P": p_price or "", "B": b_price or "", "F": "",
        })
        next_id += 1

    def dep_min(t):
        hh, mm = t.split(":")
        return int(hh) * 60 + int(mm)

    for d in E.DESTINATIONS_NEW:
        dest_name, apt = d[0], d[3]
        region = region_of[d[2]]
        dist = G.km("ICN", apt)
        direct_total = leg("ICN", apt)
        base = 120000 + dist * 85
        var = 0.93 + (h(dest_name) % 15) / 100.0
        e_dir = money(base * var)
        hubs = E.VIA[dest_name]
        picks = []   # (type, via 또는 None, 항공사 코드)
        if dest_name in E.DIRECT:
            picks.append(("D", None, KOREAN_FSC[h(dest_name) % 2]))
            if dist < 5500:
                picks.append(("D", None, LCC_SHORT[h(dest_name + "l") % len(LCC_SHORT)]))
            else:
                fsc = REGION_FSC[region]
                picks.append(("D", None, fsc[h(dest_name + "f") % len(fsc)]))
            picks.append(("V", hubs[0], HUB_AIRLINE[hubs[0]]))
        else:
            for hub in hubs[:3]:
                picks.append(("V", hub, HUB_AIRLINE[hub]))
        for n, (kind, via, code) in enumerate(picks):
            lcc = G.AIRLINES[code][2] == "LCC"
            if kind == "D":
                total = direct_total + (h(dest_name + str(n)) % 25) - 10
                dep = DIRECT_SLOTS[(h(dest_name) + n * 2) % len(DIRECT_SLOTS)]
                e = money(e_dir * (0.62 if lcc else (1.0 if n == 0 else 1.04)))
                p = None if lcc else money(e * 1.6)
                b = None if lcc else money(e * 3.2)
            else:
                layover = 100 + h(dest_name + via) % 90
                total = leg("ICN", via) + layover + leg(via, apt)
                total = max(total, direct_total + 150)   # 경유는 직항보다 반드시 오래 걸린다
                dep = VIA_SLOTS[(h(dest_name + via)) % len(VIA_SLOTS)]
                e = money(e_dir * 0.78)
                p = money(e * 1.6)
                b = money(e * 3.2)
            add(dest_name, apt, code, via, dep, total, e, p, b)

    cols = ["id", "tag", "dest", "flight_no", "airline", "type", "origin", "via", "arr_airport", "dep", "arr", "arr_day", "duration", "E", "P", "B", "F"]
    with open(CSV_PATH, "a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        for r in out:
            w.writerow(r)
    print("추가:", len(out), "편 (합계", len(rows) + len(out), "편)")


if __name__ == "__main__":
    build()
