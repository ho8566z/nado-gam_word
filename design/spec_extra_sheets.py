# -*- coding: utf-8 -*-
"""명세서 엑셀의 추가 시트: 트러블슈팅 · ERD · 와이어프레임(화면 구성). gen_spec_xlsx.py 가 불러 쓴다.

- ERD 그림은 schema.sql 을 읽어 Pillow 로 그린다(erd.png, design/ 아래 생성).
- 와이어프레임은 ppt_output/captures 의 실제 화면 캡처에 화면 ID·구성 설명을 붙인 시트다.
"""
import os
import re

from openpyxl.drawing.image import Image as XImage
from openpyxl.utils import get_column_letter as L
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CAPS = os.path.normpath(os.path.join(HERE, "..", "ppt_output", "captures"))
ERD_PNG = os.path.join(HERE, "erd.png")
FONT_R = r"C:\Windows\Fonts\malgun.ttf"
FONT_B = r"C:\Windows\Fonts\malgunbd.ttf"

# ---------------------------------------------------------------------
# 트러블슈팅 (구분, 증상, 원인, 해결, 재발 방지·확인, 상태)
# ---------------------------------------------------------------------
TROUBLE = [
    ("화면(Thymeleaf)", "카드 조각(fragment)에 사진 정보를 넘기면 오류가 나고 사진 카드가 뜨지 않음",
     "조각 인자 안에서 @빈(@destPhotos) 호출이 금지돼 있음(\"@bean forbidden in fragment args\")",
     "조각이 id·이름만 받고 조각 안에서 DestPhotos 를 조회하도록 바꿈(fragments/spot.html 의 byId·byName)",
     "여행지·투어·국내 카드 템플릿 모두 같은 조각 사용, DestPhotosTest 5개", "해결"),
    ("화면(Thymeleaf)", "th:with 로 만든 값을 같은 태그의 th:if 에서 쓰면 값이 비어 보임",
     "th:if 가 th:with 보다 먼저 평가됨",
     "th:block 으로 감싸 th:with 를 바깥에, th:if 를 안쪽에 둠",
     "해당 패턴은 th:block 으로 통일", "해결"),
    ("개발 환경", "CSS 를 고쳤는데 화면에 반영되지 않음",
     "개발 서버가 build/resources 에 복사된 CSS 를 읽음(원본 수정만으로는 갱신 안 됨)",
     "CSS 수정 후 서버 재시작(또는 processResources 실행)",
     "화면 점검 때마다 재시작 후 확인", "해결"),
    ("디자인", "성공 알림이 오류처럼 빨갛게 보여 결과를 헷갈림",
     "라이트 테마 포인트(주황빨강 #ff5a36)를 알림 색에도 그대로 썼음",
     "성공·판매 중·완료는 초록(--ok #2b8a3e), 오류는 --hot 으로 분리 (커밋 d4d7546)",
     "ThemeTest 로 변수 값 확인, 화면 캡처로 눈 확인", "해결"),
    ("테스트", "라이트 테마 적용 후 ThemeTest 일부 실패",
     "테스트가 이전 다크 테마의 색 값을 기대하고 있었음",
     "새 변수 값(--accent, --bg 등)을 기대하도록 테스트를 갱신",
     "전체 테스트 149개 통과", "해결"),
    ("외부 데이터", "여행지 사진을 받던 중 Wikimedia 가 HTTP 429(요청 과다)로 거부",
     "짧은 간격 요청이 한도에 걸림",
     "요청 간격 1.5초, Retry-After 를 지켜 재시도, 실패 항목만 건너뜀. 한도를 우회하는 방법은 쓰지 않음",
     "fetch_dest_photos.py 는 받은 파일을 건너뛰어 다시 실행 가능. 댈러스 1곳은 못 받아 그라데이션 카드로 대체", "일부 미해결(대체 표시)"),
    ("외부 데이터", "무료 사진을 비공식 검색 주소로 받아오는 방식은 허용되지 않음",
     "Unsplash 공식 API 가 아닌 내부 주소 호출은 정책에 어긋남",
     "Wikipedia·Wikimedia Commons 공개 API 로 변경(사용자 선택), 요청 헤더에는 개인 연락처를 넣지 않음",
     "사진 출처·저작자·라이선스를 /photo-credits 에 표기", "해결"),
    ("데이터", "사진이 없는 도시에서 카드가 빈 배경으로 보일 위험",
     "사진은 파일 기반이라 일부 도시는 없을 수 있음",
     "DestPhotos 가 사진이 없으면 빈 값을 돌려주고 기존 그라데이션 카드를 그대로 보여 줌",
     "DestPhotosTest 의 '사진 없음' 케이스", "해결"),
    ("결제", "동시에 결제하면 남은 좌석보다 많이 팔릴 수 있음",
     "좌석 수를 읽은 뒤 따로 빼면 그 사이에 다른 결제가 끼어듦",
     "UPDATE ... WHERE seats_left >= :인원 조건부 한 번 차감, 0건이면 예외로 전체 롤백. 단가는 서버가 DB 값으로 다시 계산",
     "SeatDeductionTest, CartFlightTest", "해결(설계)"),
    ("명세서", "명세서의 회원 상태값·투어 테마 코드가 실제 코드와 달랐음",
     "구현 전에 쓴 문서를 그대로 둠",
     "코드를 열어 값을 확인한 뒤 spec_additions.py 의 행을 고쳐 엑셀을 다시 생성",
     "테이블 시트는 schema.sql 에서 자동 생성해 DDL 과 항상 일치", "해결"),
]

# ---------------------------------------------------------------------
# ERD
# ---------------------------------------------------------------------
GROUPS = [
    ("관리자·사용자", "DDEAFE", ["admin_account", "admin_audit_log", "popup_event", "member", "support_inquiry",
                         "cart_item", "reservation", "reservation_item"]),
    ("마스터·항공", "DCFCE7", ["country", "airport", "destination", "airline", "flight", "flight_segment",
                          "flight_fare", "flight_sales_stat", "monthly_plan", "monthly_plan_flight"]),
    ("국내·상품", "FEF3C7", ["domestic_city", "domestic_transport", "hotel", "cruise", "tour", "tour_option", "tour_day"]),
]


def parse_relations(sql):
    info = {}
    for m in re.finditer(r"CREATE TABLE (\w+) \((.*?)\n\);", sql, re.S):
        name, body = m.group(1), m.group(2)
        pk = re.search(r"PRIMARY KEY \((.*?)\)", body)
        fks = re.findall(r"FOREIGN KEY \((\w+)\) REFERENCES (\w+) \((\w+)\)", body)
        info[name] = {"pk": [c.strip() for c in pk.group(1).split(",")] if pk else [], "fks": fks}
    return info


def draw_erd(sql):
    info = parse_relations(sql)
    fr, fb = ImageFont.truetype(FONT_R, 15), ImageFont.truetype(FONT_B, 17)
    bw, pad, lh = 270, 12, 21
    colx = [40, 480, 920]
    pos, size, bottoms = {}, {}, []
    for ci, (gname, color, names) in enumerate(GROUPS):
        y = 90
        for n in names:
            d = info[n]
            h = pad + 26 + lh * (len(d["pk"]) + len(d["fks"])) + pad
            pos[n] = (colx[ci], y)
            size[n] = (bw, h)
            y += h + 28
        bottoms.append(y)
    W, Ht = 1260, max(bottoms) + 30
    img = Image.new("RGB", (W, Ht), "white")
    dr = ImageDraw.Draw(img)
    dr.text((40, 24), "나도 감 ERD — 테이블 %d개, 선은 FK(자식 → 부모)" % len(info), font=ImageFont.truetype(FONT_B, 22), fill="#111827")
    for ci, (gname, color, names) in enumerate(GROUPS):
        dr.text((colx[ci], 60), gname, font=fb, fill="#374151")
    palette = ["#ef4444", "#2563eb", "#16a34a", "#d97706", "#9333ea", "#0891b2", "#db2777", "#65a30d"]
    k = 0
    for n, d in info.items():
        for col, parent, pcol in d["fks"]:
            cx, cy = pos[n]
            px, py = pos[parent]
            color = palette[k % len(palette)]
            if cx == px:  # 같은 열: 오른쪽 바깥으로 빼서 연결(선마다 간격을 달리해 구분)
                a = (cx + bw, cy + 14)
                b = (px + bw, py + 14)
                mid = cx + bw + 10 + (k % 9) * 7
                dr.line([a, (mid, a[1]), (mid, b[1]), b], fill=color, width=2)
                dr.polygon([(b[0], b[1]), (b[0] + 8, b[1] - 4), (b[0] + 8, b[1] + 4)], fill=color)
            else:
                a = (cx + bw if px > cx else cx, cy + 14)
                b = (px if px > cx else px + bw, py + 14)
                dr.line([a, b], fill=color, width=2)
                dr.ellipse([b[0] - 4, b[1] - 4, b[0] + 4, b[1] + 4], fill=color)
            dr.ellipse([a[0] - 3, a[1] - 3, a[0] + 3, a[1] + 3], fill=color)
            k += 1
    for ci, (gname, color, names) in enumerate(GROUPS):
        for n in names:
            x, y = pos[n]
            w, h = size[n]
            dr.rectangle([x, y, x + w, y + h], fill="white", outline="#6b7280", width=2)
            dr.rectangle([x, y, x + w, y + 26], fill="#" + color, outline="#6b7280", width=2)
            dr.text((x + pad, y + 3), n, font=fb, fill="#111827")
            yy = y + 30
            for c in info[n]["pk"]:
                dr.text((x + pad, yy), "PK  " + c, font=fr, fill="#1d4ed8")
                yy += lh
            for col, parent, pcol in info[n]["fks"]:
                dr.text((x + pad, yy), "FK  %s → %s" % (col, parent), font=fr, fill="#b91c1c")
                yy += lh
    img.save(ERD_PNG)
    return info, img.size


# ---------------------------------------------------------------------
# 와이어프레임: (화면 ID, 화면 이름, 주소, 캡처 파일, 화면 구성(위→아래))
# ---------------------------------------------------------------------
WIRES = [
    ("SCR-U-001", "메인 — 지구본", "GET /", "cap01_home-globe.jpg",
     "상단 메뉴(홈·이달의 특별전·베스트셀러·투어·해외·국내·계정·고객문의) → 왼쪽 큰 제목과 안내 문구 / 오른쪽 도는 지구본(경로 선·도시 이름표)"),
    ("SCR-U-001", "메인 — 기획전·베스트셀러", "GET /", "cap02_home-carousel.jpg",
     "이달의 기획전 캐로셀(포스터 카드 3장, 이전·다음·점) → 베스트셀러 캐로셀. 카드 클릭 시 상세로 이동"),
    ("SCR-U-002", "해외 여행 — 여행지 선택", "GET /travel", "cap03_travel-list.jpg",
     "단계 표시(1 여행지) → 권역 탭 → 여행지 카드 격자(대표 관광지 사진·명소·특산 한 줄·최저가·항공편 수)"),
    ("SCR-U-003", "해외 여행 — 출발지·항공편", "GET /travel/{destinationId}", "cap04_travel-detail.jpg",
     "여행지 머리글(사진·출처) → 출발지 선택 → 직항·경유 항공편 목록(정렬·필터)"),
    ("SCR-U-004", "항공편 상세", "GET /travel/flights/{flightId}", "cap05_flight-detail.jpg",
     "항공편 요약 → 구간·환승 대기 → 좌석등급별 요금 → 장바구니 담기"),
    ("SCR-U-009", "투어 상세", "GET /tour/{tourId}", "cap06_tour-detail.jpg",
     "투어 머리글 → 옵션 선택 → 일자별 일정 → 인원·가격 → 장바구니 담기"),
    ("SCR-U-011", "호텔·크루즈", "GET /stay", "cap07_hotels.jpg",
     "호텔·크루즈 탭 → 상품 카드 목록(등급·가격·위치)"),
    ("SCR-U-010", "국내여행", "GET /domestic", "cap08_domestic.jpg",
     "국내 도시 카드(사진·명소·특산) → 도시별 이동편·호텔·투어"),
    ("SCR-U-012", "장바구니", "GET /cart", "cap09_cart-items.jpg",
     "담은 상품 목록(수량·삭제) → 합계 → 결제 영역"),
    ("SCR-U-012", "모의 결제", "POST /cart/pay", "cap10_cart-pay.jpg",
     "결제 요약 → 모의 결제 → 성공 알림(초록)"),
    ("SCR-U-013", "내 예약·QR", "GET /reservations/{id}", "cap11_reservation-qr.jpg",
     "예약 번호·상태 → 체크인 QR → 예약 상품 목록"),
    ("SCR-U-013", "내 예약 목록", "GET /reservations", "cap12_reservation-items.jpg",
     "예약 카드 목록(상태 칩: 예약 완료 파랑 / 체크인 완료 초록)"),
    ("SCR-U-017", "모바일(390px)", "공통", "cap13_mobile.jpg",
     "상단 메뉴가 하단 탭 바로 바뀌고 카드는 한 줄로 쌓임"),
    ("SCR-A-001", "관리자 — 대시보드", "GET /admin", "cap14_admin-dashboard.jpg",
     "관리자 로그인 후 통계 카드(회원·예약·상품) → 최근 작업 이력"),
    ("SCR-A-003", "관리자 — 투어 관리", "GET /admin/tours", "cap15_admin-tours.jpg",
     "상품 목록 표 → 등록·수정·삭제 폼"),
    ("SCR-A-004", "관리자 — 체크인", "GET /admin/checkin", "cap16_admin-checkin.jpg",
     "예약 번호·QR 값 입력 → 체크인 처리 결과"),
]


def add_sheets(wb, schema_sql, style, title, GRAY, LIGHT, CENTER, WRAP, fit_width, table_sheet):
    table_sheet(wb, "트러블슈팅", "트러블슈팅 기록", ["구분", "증상", "원인", "해결", "재발 방지·확인", "상태"],
                TROUBLE, [16, 46, 40, 56, 40, 14], group_cols=0)
    # ERD
    info, (iw, ih) = draw_erd(schema_sql)
    ws = wb.create_sheet("ERD")
    title(ws, "ERD (엔티티 관계도)", 6)
    ws.merge_cells("A2:F2")
    style(ws.cell(2, 1, "schema.sql 에서 자동 생성. PK 는 파랑, FK 는 빨강 글자. 관리자 계정(admin_account)과 사용자 계정(member)은 분리돼 있다."), fill=LIGHT)
    img = XImage(ERD_PNG)
    scale = 1150 / iw
    img.width, img.height = int(iw * scale), int(ih * scale)
    ws.add_image(img, "A4")
    start = 4 + int(ih * scale / 20) + 2
    for i, h in enumerate(["자식 테이블", "자식 컬럼", "부모 테이블", "부모 컬럼"], start=1):
        style(ws.cell(start, i, h), bold=True, fill=GRAY, align=CENTER)
    r = start + 1
    for n, d in info.items():
        for col, parent, pcol in d["fks"]:
            for i, v in enumerate([n, col, parent, pcol], start=1):
                style(ws.cell(r, i, v))
            r += 1
    for i, w in enumerate([26, 22, 26, 22, 30, 30], start=1):
        ws.column_dimensions[L(i)].width = w
    fit_width(ws)
    # 와이어프레임
    ws = wb.create_sheet("와이어프레임")
    title(ws, "와이어프레임(화면 구성 + 실제 화면 캡처)", 5)
    for i, h in enumerate(["화면 ID", "화면 이름", "주소", "화면 구성(위→아래)", "화면 캡처"], start=1):
        style(ws.cell(2, i, h), bold=True, fill=GRAY, align=CENTER)
    for r, (sid, name, url, fn, desc) in enumerate(WIRES, start=3):
        for i, v in enumerate([sid, name, url, desc], start=1):
            style(ws.cell(r, i, v))
        style(ws.cell(r, 5))
        im = XImage(os.path.join(CAPS, fn))
        im.width, im.height = 476, 240
        ws.add_image(im, "E%d" % r)
        ws.row_dimensions[r].height = 186
    for i, w in enumerate([13, 24, 28, 60, 66], start=1):
        ws.column_dimensions[L(i)].width = w
    ws.freeze_panes = "A3"
    fit_width(ws)
    return len(TROUBLE), len(WIRES), sum(len(d["fks"]) for d in info.values())
