# -*- coding: utf-8 -*-
"""나도 감 발표 PPT 생성 스크립트 (python-pptx). 구성안: 00_PPT_구성안.md, 캡처: captures/
사용: python build_ppt.py [sample|all]   → sample 은 디자인 확인용 5장, all 은 36장 전체
크기는 White Eyes 샘플과 같은 20 x 11.25 in(16:9). 색은 사이트 색(#ff5a36 주 / #2f3dff 보조).
숫자(요구·기능·API 개수, 테스트 수, ERD)는 명세서 스크립트·schema.sql·테스트 결과에서 읽어 와서 쓴다.
"""
import glob
import os
import sys
import xml.etree.ElementTree as ET

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = os.path.join(HERE, "captures")
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "nado_gam"))
sys.path.insert(0, os.path.join(HERE, "..", "design"))
TOTAL = 36

# ---- 색·글꼴 ---------------------------------------------------------------
INK = RGBColor(0x1B, 0x22, 0x36)
MUTED = RGBColor(0x5B, 0x66, 0x7F)
ORANGE = RGBColor(0xFF, 0x5A, 0x36)
ORANGE_INK = RGBColor(0xD9, 0x3A, 0x17)
BLUE = RGBColor(0x2F, 0x3D, 0xFF)
CARD = RGBColor(0xFF, 0xFF, 0xFF)       # 카드(흰색 + 테두리)
BG = RGBColor(0xE9, 0xE1, 0xD2)         # 페이지 배경(카드와 뚜렷이 구분되는 모래색)
DECO = RGBColor(0xE0, 0xD6, 0xC2)       # 배경 장식 원
CARD_LINE = RGBColor(0xD2, 0xC7, 0xB1)
INNER = RGBColor(0xF4, 0xEF, 0xE4)      # 카드 안쪽 요소
ZEBRA = RGBColor(0xF4, 0xEF, 0xE4)
LINE = RGBColor(0xE4, 0xDD, 0xD2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x1B, 0x22, 0x36)
GREEN = RGBColor(0x2B, 0x8A, 0x3E)
SLATE = RGBColor(0x5B, 0x66, 0x7F)
FAINT = RGBColor(0x8C, 0x85, 0x77)
FONT = "맑은 고딕"
MONO = "Consolas"

W, H = 20.0, 11.25
MX = 1.3   # 좌우 여백
SCALE = 1.2   # 20in 폭 슬라이드에서 읽기 쉽도록 모든 글자 크기에 곱한다(54pt 이상 큰 글자는 그대로)


def sz(v):
    return v if v >= 54 else round(v * SCALE * 2) / 2


# ---- 도형·글자 도우미 --------------------------------------------------------
def new_prs():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    return prs


def blank(prs, bg=BG, deco=True):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = bg
    if deco and bg == BG:                     # 모서리에 걸친 큰 원: 배경에 깊이를 준다
        rect(s, W - 4.6, -3.4, 8.0, 8.0, fill=DECO, shape=MSO_SHAPE.OVAL, noline=True)
        rect(s, -3.4, H - 4.2, 7.4, 7.4, fill=DECO, shape=MSO_SHAPE.OVAL, noline=True)
    return s


def rect(s, x, y, w, h, fill=CARD, line=None, radius=0.0, shape=None, lw=1.0, noline=False):
    shp = s.shapes.add_shape(shape or (MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE),
                             Inches(x), Inches(y), Inches(w), Inches(h))
    if radius and shp.adjustments:
        shp.adjustments[0] = min(radius / min(w, h), 0.5)
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None and fill == CARD and not noline:
        line = CARD_LINE
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    st = shp._element.find(qn("p:style"))   # 기본 스타일(그림자·테두리 참조)을 제거해 평평하게 그린다
    if st is not None:
        shp._element.remove(st)
    return shp


def text(s, x, y, w, h, content, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.15, font=FONT):
    """content: 문자열 또는 문단 목록. 항목이 (문자열, {size, bold, color, align}) 이면 문단별 서식을 바꾼다."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    items = content if isinstance(content, list) else [content]
    flat = []
    for it in items:                       # 줄바꿈 문자는 문단으로 나눠 정렬이 같이 적용되게 한다
        opts = {}
        if isinstance(it, tuple):
            it, opts = it
        for part in it.split(chr(10)):
            flat.append((part, opts))
    for i, (it, opts) in enumerate(flat):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = opts.get("align", align)
        p.line_spacing = spacing
        r = p.add_run()
        r.text = it
        f = r.font
        f.name = opts.get("font", font)
        f.size = Pt(sz(opts.get("size", size)))
        f.bold = opts.get("bold", bold)
        f.color.rgb = opts.get("color", color)
    return tb


def pic(s, name, x, y, w=None, h=None, border=True):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    p = s.shapes.add_picture(os.path.join(CAP, name), Inches(x), Inches(y), **kw)
    if border:
        p.line.color.rgb = LINE
        p.line.width = Pt(1.25)
    return p


def line(s, x1, y1, x2, y2, color=LINE, width=1.5, arrow=False, dash=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    if dash:
        d = ln.makeelement(qn("a:prstDash"), {"val": "dash"})
        ln.append(d)
    if arrow:
        t = ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"})
        ln.append(t)
    st = c._element.find(qn("p:style"))
    if st is not None:
        c._element.remove(st)
    return c


def header(s, label, title, sub=None):
    text(s, 0, 0.62, W, 0.4, label, size=15, bold=True, color=ORANGE_INK, align=PP_ALIGN.CENTER)
    text(s, 0, 1.0, W, 0.9, title, size=38, bold=True, color=INK, align=PP_ALIGN.CENTER)
    if sub:
        text(s, 0, 1.95, W, 0.45, sub, size=17, color=MUTED, align=PP_ALIGN.CENTER)


def footer(s, n, dark=False, strip=True):
    if strip and not dark:                    # 왼쪽 색 띠: PART 1 주황 · PART 2 파랑 · PART 3 남색
        rect(s, 0, 0, 0.3, H, fill=ORANGE if n <= 9 else (BLUE if n <= 24 else DARK), noline=True)
    c = FAINT if not dark else RGBColor(0x9A, 0xA3, 0xBA)
    text(s, MX, 10.55, 8, 0.4, "나도 감 · nado_gam", size=12, color=c)
    text(s, W - MX - 3, 10.55, 3, 0.4, "%d / %d" % (n, TOTAL), size=12, color=c, align=PP_ALIGN.RIGHT)


def pill(s, x, y, w, h, label, fill=ORANGE, color=WHITE, size=14):
    rect(s, x, y, w, h, fill=fill, radius=h / 2)
    text(s, x, y, w, h, label, size=size, bold=True, color=color, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def card(s, x, y, w, h, title, body, accent=ORANGE, tsize=20, bsize=15, num=None, fill=CARD, line_c=None, body_color=MUTED):
    rect(s, x, y, w, h, fill=fill, line=line_c, radius=0.16)
    rect(s, x, y + 0.28, 0.09, h - 0.56, fill=accent)
    tx = x + 0.4
    if num:
        pill(s, tx, y + 0.28, 0.58, 0.58, num, fill=accent, size=16)
        tx += 0.8
    text(s, tx, y + 0.25, w - (tx - x) - 0.25, 0.7, title, size=tsize, bold=True, color=INK, spacing=1.1)
    text(s, x + 0.4, y + (1.05 if num else 0.95), w - 0.65, h - 1.15, body, size=bsize, color=body_color, spacing=1.3)


def bullets(s, x, y, w, h, lines, size=17, color=INK, gap=1.4, dot=ORANGE_INK):
    text(s, x, y, w, h, [("•  " + t, {}) for t in lines], size=size, color=color, spacing=gap)


def code_block(s, x, y, w, h, lines, size=12.5, title=None):
    rect(s, x, y, w, h, fill=DARK, radius=0.15)
    if title:
        text(s, x + 0.35, y + 0.2, w - 0.7, 0.4, title, size=12, bold=True, color=RGBColor(0xFF, 0x9A, 0x7A), font=FONT)
    text(s, x + 0.35, y + (0.65 if title else 0.3), w - 0.7, h - 0.9, lines, size=size, color=RGBColor(0xE8, 0xEA, 0xF2), font=MONO, spacing=1.18)


def table(s, x, y, widths, rows, row_h=0.62, size=15, head_fill=DARK, zebra=True, first_bold=True, aligns=None):
    n, m = len(rows), len(widths)
    gt = s.shapes.add_table(n, m, Inches(x), Inches(y), Inches(sum(widths)), Inches(row_h * n))
    tbl = gt.table
    tblPr = tbl._tbl.tblPr
    tblPr.set("firstRow", "0")
    tblPr.set("bandRow", "0")
    for j, w in enumerate(widths):
        tbl.columns[j].width = Inches(w)
    for i, r in enumerate(rows):
        tbl.rows[i].height = Inches(row_h)
        for j, val in enumerate(r):
            c = tbl.cell(i, j)
            c.fill.solid()
            if i == 0 and head_fill is not None:
                c.fill.fore_color.rgb = head_fill
            else:
                c.fill.fore_color.rgb = ZEBRA if (zebra and i % 2 == 0) else WHITE
            c.margin_left = c.margin_right = Inches(0.15)
            c.margin_top = c.margin_bottom = Inches(0.05)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            if aligns:
                p.alignment = aligns[j]
            run = p.add_run()
            run.text = str(val)
            f = run.font
            f.name = FONT
            f.size = Pt(sz(size))
            if i == 0 and head_fill is not None:
                f.bold = True
                f.color.rgb = WHITE
            else:
                f.bold = bool(first_bold and j == 0)
                f.color.rgb = INK
    return gt


# ---- 자료 읽기 -------------------------------------------------------------------
def load_spec():
    import gen_spec_xlsx as G
    return G


def test_counts():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "build", "test-results", "test", "*.xml"))):
        r = ET.parse(f).getroot()
        out.append((r.get("name").split(".")[-1].replace("Test", ""), int(r.get("tests")), int(r.get("failures"))))
    return out


def prepare_assets():
    """표지용 지구본: 메인 화면 캡처에서 지구본만 잘라 어두운 배경을 투명하게 만든다(둥근 마스크)."""
    from PIL import Image, ImageDraw, ImageFilter
    dst = os.path.join(CAP, "cover_globe.png")
    src = os.path.join(CAP, "cap01_home-globe.jpg")
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return
    cx, cy, r, S = 706, 493, 192, 4        # 캡처에서 잰 지구본 중심·반지름
    im = Image.open(src).convert("RGB")
    big = im.crop((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10))
    big = big.resize((big.width * S // 2, big.height * S // 2), Image.LANCZOS)
    w, h = big.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).ellipse((w / 2 - (r - 1) * S / 2, h / 2 - (r - 1) * S / 2, w / 2 + (r - 1) * S / 2, h / 2 + (r - 1) * S / 2), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(big, (0, 0), mask)
    out.save(dst)


# ============================ PART 1 · 기획 ==========================================
def slide_cover(prs, n=1):
    s = blank(prs, BG)
    rect(s, 0, 0, 0.5, H, fill=ORANGE)
    rect(s, 11.6, 1.8, 8.2, 8.2, fill=RGBColor(0xFF, 0xD9, 0xCC), shape=MSO_SHAPE.OVAL, noline=True)   # 지구본 뒤 은은한 원(글자보다 먼저 그린다)
    pill(s, 1.6, 2.2, 3.6, 0.55, "PERSONAL PROJECT · 4TH", fill=DARK, size=14)
    text(s, 1.5, 3.1, 9, 2.2, "나도 감", size=120, bold=True, color=INK)
    text(s, 1.6, 5.5, 9.8, 0.9, "nado_gam — 지구본으로 떠나는 여행사 웹 서비스", size=25, bold=True, color=ORANGE_INK)
    text(s, 1.6, 6.5, 9.2, 1.2, "가고 싶은 여행지를 고르면 항공편·투어·호텔·크루즈를 한 번에 담고, 비행 경로는 3D 지구본으로 보여 줍니다.",
         size=18, color=MUTED, spacing=1.3)
    text(s, 1.6, 9.2, 8, 0.5, "발표자 이윤호", size=20, bold=True, color=INK)
    text(s, 1.6, 9.75, 8, 0.5, "2026년 11월 25일 · 프로젝트 발표", size=16, color=MUTED)
    pic(s, "cover_globe.png", 12.25, 2.45, w=6.9, border=False)
    return s


def slide_index(prs, n=2):
    s = blank(prs)
    text(s, 0, 0.62, W, 0.4, "INDEX", size=15, bold=True, color=ORANGE_INK, align=PP_ALIGN.CENTER)
    text(s, 0, 1.0, W, 0.9, "나도 감 목차", size=38, bold=True, align=PP_ALIGN.CENTER)
    parts = [
        ("PART 1 · PLAN", "기획", ORANGE, ["프로젝트 소개", "주제 선정 배경", "목표", "벤치마킹", "차별점", "활용 방안·기대 효과"]),
        ("PART 2 · DESIGN", "시연 및 설계", BLUE, ["핵심 사용자 시나리오", "시연 (캡처)", "서비스 구성도·메뉴 구성", "ERD·명세서·API", "WBS·유스케이스", "워크플로우·패키지 구조"]),
        ("PART 3 · DELIVER", "구현 및 평가", DARK, ["개발 환경·Git 전략", "핵심 구현 3가지", "테스트·검증", "트러블슈팅", "성과·한계·향후 확장", "질의응답"]),
    ]
    cw, gap = 5.5, 0.55
    x0 = (W - (cw * 3 + gap * 2)) / 2
    k = 1
    for i, (tag, name, col, items) in enumerate(parts):
        x = x0 + i * (cw + gap)
        rect(s, x, 2.7, cw, 1.5, fill=col, radius=0.18)
        text(s, x + 0.4, 2.95, cw - 0.8, 0.4, tag, size=14, bold=True, color=WHITE)
        text(s, x + 0.4, 3.35, cw - 0.8, 0.7, name, size=28, bold=True, color=WHITE)
        rect(s, x, 4.4, cw, 5.3, fill=CARD, radius=0.18)
        for j, it in enumerate(items):
            y = 4.75 + j * 0.84
            text(s, x + 0.45, y, 0.8, 0.5, "%02d" % k, size=20, bold=True, color=col if col != DARK else MUTED)
            text(s, x + 1.35, y, cw - 1.7, 0.5, it, size=20, color=INK)
            if j < len(items) - 1:
                rect(s, x + 0.45, y + 0.66, cw - 0.9, 0.012, fill=LINE)
            k += 1
    footer(s, n)
    return s


def slide_part(prs, n, no, part, title, items, col=ORANGE):
    s = blank(prs, BG)
    rect(s, 0, 0, 0.5, H, fill=col)
    text(s, 1.8, 2.2, 6, 3.4, no, size=230, bold=True, color=col)
    text(s, 9.2, 3.1, 9, 0.5, part, size=18, bold=True, color=ORANGE_INK if col == ORANGE else col)
    text(s, 9.2, 3.6, 9.5, 1.3, title, size=58, bold=True, color=INK)
    rect(s, 9.25, 5.25, 1.6, 0.07, fill=col)
    text(s, 9.2, 5.6, 9.5, 3.5, ["·  " + t for t in items], size=22, color=MUTED, spacing=1.55)
    footer(s, n, strip=False)
    return s


def slide_intro(prs, n):
    s = blank(prs)
    header(s, "PROJECT · OVERVIEW", "프로젝트 소개", "나도 갈래! — 가고 싶은 곳을 고르면 예약까지 한 흐름으로 이어지는 여행사 웹 서비스")
    rect(s, MX, 2.8, 7.2, 6.4, fill=CARD, radius=0.2)
    text(s, MX + 0.5, 3.1, 6.2, 0.5, "CONCEPT", size=14, bold=True, color=ORANGE_INK)
    text(s, MX + 0.5, 3.55, 6.3, 1.4, "'나도 감'은\n‘나도 갈래!’라는 뜻", size=30, bold=True)
    rows = [("지구본", "비행 경로를 3D 지구본으로 보여 줘요"), ("한 흐름", "여행지 → 항공편·투어·호텔 → 결제 → QR"),
            ("운영까지", "관리자가 상품·노출·문의·체크인 관리")]
    for i, (k, v) in enumerate(rows):
        y = 5.35 + i * 1.2
        pill(s, MX + 0.5, y, 1.7, 0.5, k, fill=ORANGE, size=14)
        text(s, MX + 2.4, y - 0.04, 4.5, 0.9, v, size=17, color=INK, spacing=1.25)
    stats = [("100", "곳", "해외 여행지"), ("304", "편", "항공편"), ("141", "개", "투어"),
             ("351", "개", "호텔"), ("7", "곳", "크루즈"), ("149", "개", "자동 테스트")]
    sx, sy, cw, ch, gx, gy = 9.0, 2.8, 3.03, 2.0, 0.3, 0.4
    for i, (num, unit, label) in enumerate(stats):
        x = sx + (i % 3) * (cw + gx)
        y = sy + (i // 3) * (ch + gy)
        col = ORANGE if i % 2 == 0 else BLUE
        rect(s, x, y, cw, ch, fill=WHITE, line=LINE, radius=0.16)
        rect(s, x, y + 0.3, 0.09, ch - 0.6, fill=col)
        text(s, x + 0.35, y + 0.2, cw - 0.5, 1.1, [(num, {"size": 48, "bold": True, "color": col})], size=48)
        text(s, x + 0.35 + len(num) * 0.43 + 0.1, y + 0.62, 1.0, 0.5, unit, size=20, bold=True, color=MUTED)
        text(s, x + 0.35, y + 1.35, cw - 0.5, 0.5, label, size=17, color=INK)
    rect(s, 9.0, 7.75, 3.03 * 3 + 0.6, 1.45, fill=CARD, radius=0.16)
    info = [("개발 기간", "2026.11.19 ~ 11.25"), ("개발 인원", "1인 (이윤호)"), ("핵심 스택", "Spring Boot 4 · Thymeleaf · H2/MySQL")]
    for i, (k, v) in enumerate(info):
        x = 9.35 + i * 3.2
        text(s, x, 8.0, 3.0, 0.4, k, size=13, bold=True, color=ORANGE_INK)
        text(s, x, 8.45, 3.0, 0.7, v, size=15, bold=True, color=INK, spacing=1.2)
    footer(s, n)
    return s


def note_box(s, x, y, w, h, msg):
    """발표자가 직접 채울 부분 표시(발표 전에 지우거나 고친다)."""
    rect(s, x, y, w, h, fill=RGBColor(0xFF, 0xF3, 0xCD), line=RGBColor(0xE8, 0xB9, 0x30), radius=0.12)
    text(s, x + 0.2, y, w - 0.4, h, "✎ 직접 입력 · " + msg, size=14, color=RGBColor(0x7A, 0x5B, 0x00), anchor=MSO_ANCHOR.MIDDLE)


def slide_background(prs, n):
    s = blank(prs)
    header(s, "BACKGROUND", "주제 선정 배경과 필요성", "여행을 준비할 때 겪는 불편을 한 흐름으로 줄이고 싶었습니다")
    probs = [("상품이 따로따로", "항공권, 현지 투어, 숙소를 각각 다른 화면에서 찾고 비교해야 합니다."),
             ("노선이 한눈에 안 보임", "노선이 글자와 표로만 나와서 어느 도시에서 어느 도시로 가는지 감이 안 옵니다."),
             ("고른 뒤가 끊김", "고른 상품을 한 번에 담아 결제하고, 현장에서 바로 보여 줄 방법이 필요합니다.")]
    cw = 5.3
    for i, (t, b) in enumerate(probs):
        x = MX + i * (cw + 0.45)
        card(s, x, 2.8, cw, 3.1, t, b, accent=[ORANGE, BLUE, ORANGE][i], num=str(i + 1), tsize=21, bsize=16)
    line(s, W / 2, 6.05, W / 2, 6.75, color=ORANGE, width=4, arrow=True)
    rect(s, MX, 6.9, W - 2 * MX, 2.0, fill=DARK, radius=0.2)
    text(s, MX + 0.6, 7.1, 6, 0.5, "그래서 나도 감", size=16, bold=True, color=RGBColor(0xFF, 0x9A, 0x7A))
    text(s, MX + 0.6, 7.6, W - 2 * MX - 1.2, 1.2,
         "지구본으로 노선을 보여 주고, 여행지를 고르면 항공편·투어·호텔·크루즈를 한 곳에서 담아 모의 결제하고 QR로 예약을 확인합니다.",
         size=22, bold=True, color=WHITE, spacing=1.3)
    note_box(s, MX, 9.3, W - 2 * MX, 0.7, "이 주제를 고른 개인적인 계기를 한 줄로 적어 주세요 (발표 전에 이 상자는 지웁니다).")
    footer(s, n)
    return s


def slide_goals(prs, n):
    s = blank(prs)
    header(s, "GOALS", "나도 감이 얻고자 하는 목표", "목표 4가지와 달성한 결과")
    goals = [("지구본으로 보는 노선", "비행 경로를 글자가 아니라 3D 지구본으로 보여 주기", "도시 100곳 · 경로 60개 · 자유 회전"),
             ("여행지 먼저, 출발지는 뒤에", "여행지를 고르면 그곳으로 가는 출발지·항공편만 보여 주기", "100곳 · 항공편 304편 · 직항/경유·정렬"),
             ("예약까지 한 흐름", "담기 → 모의 결제 → 좌석 차감 → QR 예약 확인", "장바구니 · 결제 · 좌석 차감 · 체크인"),
             ("운영 기능까지", "관리자가 상품·노출·문의·팝업·체크인을 관리하기", "상품 CRUD · 노출 중지 · 문의 답변")]
    cw, ch = 8.5, 3.15
    for i, (t, b, r) in enumerate(goals):
        x = MX + (i % 2) * (cw + 0.4)
        y = 2.8 + (i // 2) * (ch + 0.35)
        card(s, x, y, cw, ch, t, b, accent=[ORANGE, BLUE][i % 2], num="%02d" % (i + 1), tsize=22, bsize=17)
        pill(s, x + 0.4, y + ch - 0.85, cw - 0.8, 0.55, "달성 · " + r, fill=INNER, color=INK, size=14)
    footer(s, n)
    return s


def slide_benchmark(prs, n):
    s = blank(prs)
    header(s, "BENCHMARK", "유사 서비스 조사", "하나투어·모두투어·트립닷컴·놀유니버스(NOL)를 브라우저로 직접 확인했습니다")
    rows = [["조사 대상", "확인한 것", "나도 감의 선택"],
            ["하나투어", "Next.js 기반 웹", "화면은 서버 렌더링(Thymeleaf)으로 단순하게"],
            ["모두투어", "Next.js 기반 웹", "항공·투어·호텔·크루즈를 한 사이트에 모음"],
            ["트립닷컴", "React 기반 웹", "여행지 → 출발지 → 항공편의 단계 흐름"],
            ["놀유니버스(NOL)", "채용 공고에서 Java·Kotlin·Spring Boot 백엔드 확인", "백엔드는 Java 17 + Spring Boot 로 맞춤"]]
    table(s, MX, 2.8, [3.6, 6.4, 7.4], rows, row_h=1.0, size=17)
    note_box(s, MX, 8.2, W - 2 * MX, 0.8, "사이트별로 직접 본 기능(예: 검색 방식, 상품 구성)이 있으면 '확인한 것'에 추가해 주세요.")
    text(s, MX, 9.2, W - 2 * MX, 0.6, "※ 기술 스택은 브라우저로 직접 확인한 내용이며, 위 사이트의 이름·로고·상품은 사용하지 않았습니다(모든 상품은 가상 데이터).",
         size=13, color=MUTED)
    footer(s, n)
    return s


def slide_difference(prs, n):
    s = blank(prs)
    header(s, "DIFFERENCE", "유사 서비스와의 차별점", "나도 감만의 다섯 가지")
    items = [("지구본 노선", "가운데에서 도는 지구본과 비행 경로 시각화, 항공편에 마우스를 올리면 경로가 강조"),
             ("여행지 먼저", "여행지를 고르면 그 여행지로 가는 출발지만 보여 주는 흐름"),
             ("직항 · 경유", "직항/경유 필터와 가격·시간·출발 정렬"),
             ("사진 카드", "이달의 특별전·베스트셀러 포스터와 대표 관광지 사진, 명소·특산 한 줄"),
             ("예약 흐름", "장바구니 → 모의 결제 → 좌석 차감 → QR 예약 확인·체크인")]
    cw, gap = 3.2, 0.34
    x0 = (W - (cw * 5 + gap * 4)) / 2
    for i, (t, b) in enumerate(items):
        x = x0 + i * (cw + gap)
        col = ORANGE if i % 2 == 0 else BLUE
        rect(s, x, 2.8, cw, 6.4, fill=CARD, radius=0.18)
        rect(s, x + 0.35, 3.15, 0.8, 0.09, fill=col)
        text(s, x + 0.3, 3.35, 1.5, 0.5, "%02d" % (i + 1), size=20, bold=True, color=col)
        text(s, x + 0.3, 4.1, cw - 0.55, 1.4, t, size=24, bold=True, color=INK, spacing=1.15)
        text(s, x + 0.3, 5.5, cw - 0.55, 3.6, b, size=16, color=MUTED, spacing=1.4)
    footer(s, n)
    return s


def slide_effect(prs, n):
    s = blank(prs)
    header(s, "UTILIZATION · EXPECTED EFFECT", "활용 방안 · 기대 효과", "이 서비스를 어떻게 쓰고, 어떤 효과를 기대하는지")
    cols = [("활용 방안", ORANGE, ["여행사 상품 소개·예약 흐름을 시연하는 포트폴리오", "가상 데이터라 개인정보 걱정 없이 체험 가능", "관리자 화면으로 운영 업무까지 시연"]),
            ("기대 효과", BLUE, ["항공·투어·호텔을 한 화면 흐름에서 비교·선택", "휴대폰에서 QR로 예약을 바로 확인(모바일 탑승권)", "운영자는 상품 노출·문의·체크인을 한 곳에서 관리"]),
            ("확장성 (2단계)", DARK, ["날짜별 재고와 동시 예약 제어(낙관적 락)", "실제 결제 연동(테스트 모드), 후기·찜", "'나도 감' 동행 모집, Redis 캐시, Docker·CI 배포"])]
    cw = 5.5
    for i, (t, col, items) in enumerate(cols):
        x = MX + i * (cw + 0.45)
        rect(s, x, 2.8, cw, 1.1, fill=col, radius=0.16)
        text(s, x + 0.4, 2.8, cw - 0.8, 1.1, t, size=24, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
        rect(s, x, 4.1, cw, 5.1, fill=CARD, radius=0.16)
        for j, it in enumerate(items):
            y = 4.45 + j * 1.5
            pill(s, x + 0.4, y + 0.05, 0.5, 0.5, str(j + 1), fill=col, size=14)
            text(s, x + 1.1, y, cw - 1.4, 1.4, it, size=17, color=INK, spacing=1.3)
    footer(s, n)
    return s


# ============================ PART 2 · 시연·설계 =====================================
def flow_chips(s, x, y, labels, color, cw=2.15, ch=0.95, gap=0.35, size=15, row_w=None):
    for i, lab in enumerate(labels):
        xx = x + i * (cw + gap)
        rect(s, xx, y, cw, ch, fill=WHITE, line=color, radius=0.14, lw=2)
        text(s, xx + 0.05, y, cw - 0.1, ch, lab, size=size, bold=True, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.1)
        if i < len(labels) - 1:
            line(s, xx + cw + 0.02, y + ch / 2, xx + cw + gap - 0.02, y + ch / 2, color=color, width=2.5, arrow=True)


def slide_scenario(prs, n):
    s = blank(prs)
    header(s, "CORE SCENARIO", "핵심 사용자 시나리오", "사용자는 고르고 담아 결제하고, 관리자는 상품과 예약을 운영합니다")
    pill(s, MX, 2.75, 5.2, 0.62, "A. 사용자 · 여행을 고르고 예약한다", fill=ORANGE, size=17)
    flow_chips(s, MX, 3.6, ["지구본·\n특별전 보기", "여행지\n선택", "출발지·\n항공편 선택", "투어·호텔·\n크루즈 보기"], ORANGE, cw=3.7, ch=1.1, gap=0.45, size=17)
    flow_chips(s, MX, 5.05, ["장바구니\n담기", "모의 결제", "예약 확인\n(QR)", "문의하기"], ORANGE, cw=3.7, ch=1.1, gap=0.45, size=17)
    pill(s, MX, 6.75, 5.6, 0.62, "B. 관리자 · 상품과 예약을 운영한다", fill=BLUE, size=17)
    flow_chips(s, MX, 7.6, ["로그인\n(/admin)", "상품 등록·\n수정·삭제", "노출 중지·\n재개", "팝업·문의\n답변", "QR 체크인"], BLUE, cw=3.05, ch=1.1, gap=0.5, size=17)
    text(s, MX, 9.2, W - 2 * MX, 0.6, "비회원은 둘러보기만 가능하고, 장바구니·결제·내 예약·문의는 로그인이 필요합니다. 관리자와 사용자는 계정 테이블이 분리되어 있습니다.",
         size=15, color=MUTED)
    footer(s, n)
    return s


def slide_demo_flow(prs, n):
    s = blank(prs)
    header(s, "PROJECT DEMO", "시연 흐름", "화면 캡처로 3묶음을 따라가며 시연합니다")
    cols = [("① 메인 · 해외 여행", ORANGE, "cap03_travel-list.jpg", ["메인 지구본 · 특별전", "해외 여행지 100곳 카드", "여행지 → 출발지 → 항공편", "지구본에 경로 강조"]),
            ("② 투어 · 장바구니 · 결제", BLUE, "cap09_cart-items.jpg", ["투어 기간 옵션 · 호텔", "항공권·투어·호텔 담기", "서버가 가격 재계산", "모의 결제 · 좌석 차감"]),
            ("③ 예약 · QR · 관리자", ORANGE, "cap11_reservation-qr.jpg", ["예약 번호 · 모바일 QR", "관리자 체크인", "상품 관리 · 노출 관리", "390px 모바일 화면"])]
    cw = 5.5
    for i, (t, col, img, items) in enumerate(cols):
        x = MX + i * (cw + 0.45)
        rect(s, x, 2.8, cw, 6.6, fill=CARD, radius=0.18)
        pill(s, x + 0.35, 3.05, cw - 0.7, 0.62, t, fill=col, size=16)
        pic(s, img, x + 0.35, 3.9, w=cw - 0.7)
        bullets(s, x + 0.4, 3.9 + (cw - 0.7) * 718 / 1428 + 0.25, cw - 0.7, 2.4, items, size=16, gap=1.35)
    text(s, MX, 9.65, W - 2 * MX, 0.6,
         "시연 계정: 사용자 user · 관리자 admin (시연용 더미 계정)   ※ 지구본은 인터넷(CDN)이 필요해 캡처 화면으로 시연합니다.",
         size=14, color=MUTED)
    footer(s, n)
    return s


def demo_slide(prs, n, no, title, sub, steps, imgs):
    """시연 슬라이드 공통: 왼쪽 단계 설명 4개 + 오른쪽 캡처 2x2."""
    s = blank(prs)
    header(s, "PROJECT DEMO · %d/3" % no, title, sub)
    for i, (ttl, desc) in enumerate(steps):
        y = 2.9 + i * 1.95
        pill(s, MX, y, 0.6, 0.6, str(i + 1), fill=ORANGE if i % 2 == 0 else BLUE, size=18)
        text(s, MX + 0.85, y - 0.05, 4.2, 0.5, ttl, size=20, bold=True)
        text(s, MX + 0.85, y + 0.5, 4.5, 1.3, desc, size=13, color=MUTED, spacing=1.25)
    iw = 5.7
    ih = iw * 718 / 1428
    gx0, gy0 = 6.95, 2.85
    for i, name in enumerate(imgs):
        x = gx0 + (i % 2) * (iw + 0.35)
        y = gy0 + (i // 2) * (ih + 0.75)
        pic(s, name, x, y, w=iw)
        pill(s, x + 0.15, y + 0.15, 0.5, 0.5, str(i + 1), fill=ORANGE if i % 2 == 0 else BLUE, size=15)
        text(s, x, y + ih + 0.08, iw, 0.45, steps[i][0], size=14, bold=True, color=MUTED)
    footer(s, n)
    return s


def slide_demo1(prs, n):
    return demo_slide(prs, n, 1, "시연 ① 메인 · 해외 여행", "지구본에서 시작해 여행지를 고르고 항공편을 선택합니다 (캡처 화면)",
                      [("메인 지구본", "도시 100곳 사이의 비행 경로가 흐르고,\n끌어서 어느 방향으로든 돌릴 수 있어요."),
                       ("이달의 특별전", "특가 항공편을 대표 관광지 사진 카드로\n보여 주는 캐로셀이에요."),
                       ("해외 여행지 100곳", "카드마다 명소·특산을 붙였고\n권역 탭과 검색으로 찾아요."),
                       ("여행지 → 항공편", "출발지·직항/경유를 고르고, 항공편에\n마우스를 올리면 지구본에 경로가 강조돼요.")],
                      ["cap01_home-globe.jpg", "cap02_home-carousel.jpg", "cap03_travel-list.jpg", "cap04_travel-detail.jpg"])


def slide_demo2(prs, n):
    return demo_slide(prs, n, 2, "시연 ② 투어 · 장바구니 · 결제", "투어와 호텔을 고르고 장바구니에 담아 모의 결제합니다 (캡처 화면)",
                      [("투어 상세", "투어마다 기간 옵션(박수)별 일정과\n1인 가격을 보여 줘요."),
                       ("호텔", "1박 가격과 선택한 박수의\n전체 가격을 함께 보여 줘요."),
                       ("장바구니", "항공권·투어·호텔을 한 번에 담고\n가격은 서버가 다시 계산해요."),
                       ("결제 수단 선택", "카드번호는 받지 않고 결제 완료로\n안내한 뒤 예약만 만들어요.")],
                      ["cap06_tour-detail.jpg", "cap07_hotels.jpg", "cap09_cart-items.jpg", "cap10_cart-pay.jpg"])


def slide_demo3(prs, n):
    return demo_slide(prs, n, 3, "시연 ③ 예약 · QR · 관리자 · 모바일", "결제 뒤 예약과 QR을 확인하고, 관리자가 체크인합니다 (캡처 화면)",
                      [("예약 · QR", "결제 완료 안내와 예약 번호, 모바일 탑승권\nQR이 나와요."),
                       ("관리자 체크인", "예약 번호나 QR 토큰으로 조회해\n체크인 처리해요."),
                       ("관리자 상품 관리", "투어·호텔·항공편·특별전을 등록·수정·\n삭제하고 삭제 탭에서 복구해요."),
                       ("모바일 화면", "390px 폭에서도 하단 탭 바로\n같은 흐름을 쓸 수 있어요.")],
                      ["cap11_reservation-qr.jpg", "cap16_admin-checkin.jpg", "cap15_admin-tours.jpg", "cap13_mobile.jpg"])


def box(s, x, y, w, h, title, sub=None, fill=CARD, tcolor=INK, line_c=None, tsize=16, ssize=12.5, bold=True):
    rect(s, x, y, w, h, fill=fill, line=line_c, radius=0.14)
    if sub:
        text(s, x + 0.1, y + 0.1, w - 0.2, 0.5, title, size=tsize, bold=bold, color=tcolor, align=PP_ALIGN.CENTER)
        text(s, x + 0.12, y + 0.6, w - 0.24, h - 0.65, sub, size=ssize, color=tcolor if fill in (DARK, ORANGE, BLUE) else MUTED, align=PP_ALIGN.CENTER, spacing=1.2)
    else:
        text(s, x + 0.1, y, w - 0.2, h, title, size=tsize, bold=bold, color=tcolor, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.1)


def slide_architecture(prs, n):
    s = blank(prs)
    header(s, "SERVICE ARCHITECTURE", "서비스 구성도", "Spring Boot 앱 하나가 사용자 웹과 관리자 웹을 모두 처리합니다")
    # 왼쪽: 브라우저
    box(s, MX, 3.2, 3.0, 1.5, "사용자 브라우저", "지구본·카드·장바구니\n(휴대폰 포함)", fill=CARD, line_c=LINE)
    box(s, MX, 5.1, 3.0, 1.5, "관리자 브라우저", "/admin/** 운영 화면", fill=CARD, line_c=LINE)
    # 가운데: 앱
    ax, ay, aw, ah = 5.2, 2.7, 8.6, 5.65
    rect(s, ax, ay, aw, ah, fill=WHITE, line=ORANGE, radius=0.2, lw=2.5)
    text(s, ax + 0.4, ay + 0.15, aw - 0.8, 0.5, "Spring Boot 앱 (Java 17 · 1개)", size=18, bold=True, color=ORANGE_INK)
    box(s, ax + 0.35, ay + 0.85, aw - 0.7, 1.1, "Spring Security 필터 체인 2개", "사용자 경로 · /admin/** 관리자 경로 (BCrypt)", fill=DARK, tcolor=WHITE, tsize=15, ssize=12.5)
    box(s, ax + 0.35, ay + 2.15, 2.55, 1.3, "Controller", "도메인 패키지 17개\n(travel·tour·cart …)", fill=CARD, tsize=15)
    box(s, ax + 3.0, ay + 2.15, 2.55, 1.3, "Service", "결제·좌석 차감\n서버 가격 재계산", fill=CARD, tsize=15)
    box(s, ax + 5.65, ay + 2.15, 2.55, 1.3, "Repository", "읽기 JdbcClient\n쓰기 JPA", fill=CARD, tsize=15)
    box(s, ax + 0.35, ay + 3.65, aw - 0.7, 0.75, "Thymeleaf 템플릿 + CSS/JS (지구본·캐로셀·팝업)", fill=CARD, tsize=15)
    box(s, ax + 0.35, ay + 4.55, aw - 0.7, 0.75, "ZXing: 예약·팝업·모바일 접속 QR을 서버에서 SVG로 생성", fill=CARD, tsize=14, bold=False)
    # 오른쪽: DB
    box(s, 15.2, 3.2, 3.5, 2.0, "DB", "로컬 H2(MySQL 모드)\n운영 MySQL 8\n테이블 25개", fill=BLUE, tcolor=WHITE, tsize=18, ssize=14)
    box(s, 15.2, 5.6, 3.5, 2.0, "정적 파일", "css · js · 이미지\n대표 관광지 사진 109장\n(출처는 credits.json)", fill=CARD, line_c=LINE, tsize=16, ssize=13)
    # 하단: 외부
    box(s, 5.2, 8.7, 4.1, 1.3, "외부 CDN (jsDelivr)", "globe.gl · 지구 텍스처", fill=CARD, line_c=LINE, tsize=15)
    box(s, 9.7, 8.7, 4.1, 1.3, "Wikimedia Commons", "사진은 미리 내려받아 저장\n(저작자·라이선스 표기)", fill=CARD, line_c=LINE, tsize=15, ssize=12)
    # 화살표
    line(s, MX + 3.0, 3.95, ax, 3.95, color=ORANGE, width=3, arrow=True)
    line(s, MX + 3.0, 5.85, ax, 5.85, color=BLUE, width=3, arrow=True)
    line(s, ax + aw, 4.2, 15.2, 4.2, color=BLUE, width=3, arrow=True)
    line(s, ax + aw, 6.6, 15.2, 6.6, color=LINE, width=3, arrow=True)
    line(s, 7.25, 8.35, 7.25, 8.7, color=FAINT, width=2, arrow=True, dash=True)
    footer(s, n)
    return s


def slide_menu(prs, n):
    s = blank(prs)
    header(s, "MENU STRUCTURE", "메뉴 · 화면 구성", "상단 메뉴 8개, 휴대폰에서는 하단 탭 바")
    menus = [("홈", ["지구본", "특별전·베스트셀러", "이벤트 팝업"]),
             ("이달의 특별전", ["목록", "상세(특가)"]),
             ("베스트셀러", ["순위", "상세"]),
             ("투어", ["목록(테마·검색)", "상세(기간 옵션)"]),
             ("해외여행", ["여행지 선택", "출발지·항공편", "상세 · 호텔 · 크루즈"]),
             ("국내여행", ["도시 10곳", "이동편·숙소·투어"]),
             ("계정", ["내 정보·수정", "장바구니", "내 예약·QR"]),
             ("고객문의", ["문의 등록", "내 문의·답변"])]
    cw, gap = 1.95, 0.22
    x0 = (W - (cw * 8 + gap * 7)) / 2
    for i, (m, subs) in enumerate(menus):
        x = x0 + i * (cw + gap)
        col = ORANGE if i % 2 == 0 else BLUE
        rect(s, x, 2.75, cw, 0.9, fill=col, radius=0.14)
        text(s, x, 2.75, cw, 0.9, m, size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        for j, t in enumerate(subs):
            y = 3.9 + j * 0.95
            rect(s, x, y, cw, 0.8, fill=CARD, radius=0.12)
            text(s, x + 0.05, y, cw - 0.1, 0.8, t, size=13, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.1)
    pill(s, MX, 7.15, 3.8, 0.6, "관리자 (/admin)  ·  별도 로그인", fill=DARK, size=15)
    adm = ["대시보드", "회원 관리", "상품 노출", "특별전", "투어", "호텔", "항공편", "팝업", "체크인", "고객문의"]
    cw2, gap2 = 1.62, 0.1
    x0b = MX
    for i, a in enumerate(adm):
        x = x0b + i * (cw2 + gap2)
        rect(s, x, 7.95, cw2, 0.85, fill=WHITE, line=DARK, radius=0.12, lw=1.5)
        text(s, x, 7.95, cw2, 0.85, a, size=14, bold=True, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, MX, 9.2, W - 2 * MX, 0.8, "하단 탭 바(760px 이하): 홈 · 여행 · 국내 · 특별전 · 투어 · 문의 · 내 정보 (7칸)   |   화면 기능 명세서 104행으로 정리했습니다.",
         size=15, color=MUTED)
    footer(s, n)
    return s


ERD_SHORT = {
    "admin_account": "관리자 계정", "admin_audit_log": "관리자 작업 이력", "popup_event": "이벤트 팝업", "support_inquiry": "고객문의·답변",
    "member": "사용자 계정", "country": "국가·권역", "airport": "공항·좌표", "destination": "여행지 100곳", "airline": "가상 항공사",
    "domestic_city": "국내 도시 10곳", "flight": "항공편", "flight_segment": "비행 구간", "flight_fare": "좌석 등급별 요금",
    "flight_sales_stat": "판매 집계", "monthly_plan": "이달의 특별전", "monthly_plan_flight": "특별전 특가", "domestic_transport": "국내 이동편",
    "hotel": "호텔", "cruise": "크루즈", "tour": "투어", "tour_option": "기간 옵션", "tour_day": "일별 일정", "cart_item": "장바구니",
    "reservation": "예약 · QR 토큰", "reservation_item": "예약 상품 줄",
}
ERD_GRID = [
    ["admin_account", "admin_audit_log", "popup_event", "support_inquiry", "member"],
    ["country", "airport", "destination", "airline", "domestic_city"],
    ["flight", "flight_segment", "flight_fare", "flight_sales_stat", "monthly_plan"],
    ["monthly_plan_flight", "domestic_transport", "hotel", "cruise", "tour"],
    ["tour_option", "tour_day", "cart_item", "reservation", "reservation_item"],
]
ERD_AREA = {"admin_account": "A", "admin_audit_log": "A", "popup_event": "A",
            "member": "U", "support_inquiry": "U", "cart_item": "U", "reservation": "U", "reservation_item": "U"}


def slide_erd(prs, n):
    G = load_spec()
    tables = G.parse_schema(open(G.SCHEMA, encoding="utf-8").read())
    ncols = {t[0]: len(t[1]) for t in tables}
    fks = []
    for name, cols, _ in tables:
        for c in cols:
            if c["fk"]:
                fks.append((name, c["fk"].split(".")[0]))
    s = blank(prs)
    header(s, "DATABASE · TABLE STRUCTURE", "ERD", "테이블 %d개 · 컬럼 %d개 — 관리자[A] · 사용자[U] · 운영 마스터[M] 영역으로 나눴습니다" % (len(tables), sum(ncols.values())))
    x0, y0, bw, bh, gx, gy = 1.0, 2.7, 3.2, 1.0, 0.5, 0.42
    pos = {}
    for r, row in enumerate(ERD_GRID):
        for c, t in enumerate(row):
            pos[t] = (x0 + c * (bw + gx), y0 + r * (bh + gy))
    for child, parent in set(fks):     # 관계선을 먼저 그리고 상자를 그 위에 얹는다
        if child in pos and parent in pos and child != parent:
            cx, cy = pos[child]
            px, py = pos[parent]
            line(s, cx + bw / 2, cy + bh / 2, px + bw / 2, py + bh / 2, color=RGBColor(0xC9, 0xC2, 0xB5), width=1.25)
    colors = {"A": ORANGE, "U": BLUE, "M": SLATE}
    for t, (x, y) in pos.items():
        col = colors[ERD_AREA.get(t, "M")]
        rect(s, x, y, bw, bh, fill=WHITE, line=col, radius=0.1, lw=1.75)
        rect(s, x, y, bw, 0.12, fill=col)
        text(s, x + 0.12, y + 0.17, bw - 0.24, 0.45, t, size=14, bold=True, color=INK, font=MONO)
        text(s, x + 0.12, y + 0.6, bw - 0.24, 0.4, "%s · %d개 컬럼" % (ERD_SHORT.get(t, ""), ncols.get(t, 0)), size=12, color=MUTED)
    ly = 9.95
    for i, (lab, col) in enumerate([("[A] 관리자 영역", ORANGE), ("[U] 사용자 영역", BLUE), ("[M] 운영 마스터", SLATE)]):
        rect(s, 1.0 + i * 3.4, ly + 0.08, 0.35, 0.22, fill=col, radius=0.05)
        text(s, 1.5 + i * 3.4, ly, 2.8, 0.4, lab, size=13, color=INK)
    line(s, 11.4, ly + 0.2, 12.2, ly + 0.2, color=RGBColor(0xC9, 0xC2, 0xB5), width=1.5)
    text(s, 12.3, ly, 6.6, 0.4, "외래키 관계(FK, %d개)  ·  schema.sql 기준" % len(set(fks)), size=13, color=INK)
    footer(s, n)
    return s


def slide_spec_summary(prs, n):
    G = load_spec()
    s = blank(prs)
    header(s, "SPECIFICATIONS", "명세서 요약", "엑셀 명세서 10개 시트로 요구사항부터 테이블까지 정리했습니다")
    tables = G.parse_schema(open(G.SCHEMA, encoding="utf-8").read())
    nums = [("요구사항", len(G.REQ), "건"), ("기능", len(G.FNC), "개"), ("화면 행", len(G.SCREENS), "행"), ("API", len(G.API), "개"), ("테이블", len(tables), "개")]
    cw = 3.2
    for i, (lab, v, u) in enumerate(nums):
        x = MX + i * (cw + 0.35)
        col = ORANGE if i % 2 == 0 else BLUE
        rect(s, x, 2.8, cw, 2.1, fill=CARD, radius=0.16)
        rect(s, x, 3.1, 0.09, 1.5, fill=col)
        text(s, x + 0.35, 3.0, cw - 0.5, 1.1, [(str(v), {"size": 54, "bold": True, "color": col})], size=54)
        text(s, x + 0.35 + len(str(v)) * 0.5 + 0.12, 3.5, 1.0, 0.5, u, size=20, bold=True, color=MUTED)
        text(s, x + 0.35, 4.2, cw - 0.5, 0.5, lab, size=18, color=INK)
    # 구분별 요구 개수
    cnt = {}
    for r in G.REQ:
        cnt[r[0]] = cnt.get(r[0], 0) + 1
    text(s, MX, 5.3, 12, 0.5, "요구사항 구분별 개수 (상위 12개 구분)", size=18, bold=True)
    mx = max(cnt.values())
    items = sorted(cnt.items(), key=lambda kv: -kv[1])[:12]
    for i, (k, v) in enumerate(items):
        col = i % 2
        row = i // 2
        x = MX + col * 8.8
        y = 5.85 + row * 0.6
        text(s, x, y, 2.4, 0.5, k, size=14, color=INK)
        rect(s, x + 2.5, y + 0.07, 4.6 * v / mx, 0.3, fill=ORANGE if col == 0 else BLUE, radius=0.08)
        text(s, x + 2.5 + 4.6 * v / mx + 0.12, y, 0.8, 0.5, str(v), size=14, bold=True, color=INK)
    footer(s, n)
    return s


def slide_api(prs, n):
    G = load_spec()
    s = blank(prs)
    header(s, "API SPECIFICATION", "API 개요", "폼 기반 화면이라 응답은 HTML 또는 302 이동이고, 지구본용 경로만 JSON입니다 (총 %d개)" % len(G.API))
    groups = {}
    for r in G.API:
        g = groups.setdefault(r[0], {"n": 0, "uri": r[3], "auth": r[6]})
        g["n"] += 1
    rows = [["구분", "개수", "대표 URI", "권한"]]
    for k, g in groups.items():
        uri = g["uri"]
        rows.append([k, str(g["n"]), uri if len(uri) < 34 else uri[:32] + "…", g["auth"]])
    half = (len(rows) - 1 + 1) // 2
    left = [rows[0]] + rows[1:1 + half]
    right = [rows[0]] + rows[1 + half:]
    aligns = [PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.LEFT, PP_ALIGN.CENTER]
    table(s, MX, 2.8, [2.2, 0.9, 4.3, 1.3], left, row_h=0.66, size=13, aligns=aligns)
    table(s, MX + 8.85, 2.8, [2.2, 0.9, 4.3, 1.3], right, row_h=0.66, size=13, aligns=aligns)
    text(s, MX, 9.6, W - 2 * MX, 0.6, "※ 컨트롤러의 매핑을 기준으로 다시 작성했고, 모든 라우트가 시트에 들어 있는지 스크립트로 대조했습니다.", size=14, color=MUTED)
    footer(s, n)
    return s


def slide_wbs(prs, n):
    s = blank(prs)
    header(s, "WBS", "수행 절차 · 일정", "2026.11.19 ~ 11.25 (11/20 추가 요구사항으로 마감을 11/22에서 11/25로 연장)")
    days = ["19(목)", "20(금)", "21(토)", "22(일)", "23(월)", "24(화)", "25(수)"]
    lx, lw, dx, dw = MX, 7.6, MX + 7.8, 1.35
    rect(s, lx - 0.15, 2.6, lw + 0.5 + dw * 7, 7.45, fill=CARD, radius=0.16)
    rect(s, lx, 2.75, lw + 0.2 + dw * 7, 0.7, fill=DARK, radius=0.1)
    text(s, lx + 0.2, 2.75, lw, 0.7, "작업", size=15, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    for i, d in enumerate(days):
        text(s, dx + i * dw, 2.75, dw, 0.7, d, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rows = [("1.0  프로젝트 명세서 (요구·기능·화면·API·테이블)", 0, 2, ORANGE, "완료"),
            ("2.0  설계 (기능정의서·DB·더미데이터)", 0, 1, ORANGE, "완료"),
            ("3.1~3.4  골격·메인·특별전·해외 여행", 0, 0, BLUE, "완료"),
            ("3.5~3.18  계정·관리자·팝업·문의·투어·국내·호텔·결제·QR", 1, 1, BLUE, "완료"),
            ("3.19~3.24  지구본 개선·100곳 확장·관리자 CRUD·좌석 차감", 1, 1, BLUE, "완료"),
            ("3.25~3.27  라이트 테마·사진 카드·성공 색", 2, 2, BLUE, "완료"),
            ("4.0  화면·서버 점검 (장바구니~체크인, 390px)", 1, 2, ORANGE, "완료"),
            ("5.0  README·명세서(완료) · 발표 PPT", 2, 6, SLATE, "진행 중")]
    rh = 0.78
    for r, (lab, a, b, col, st) in enumerate(rows):
        y = 3.6 + r * rh
        if r % 2 == 0:
            rect(s, lx, y, lw + 0.2 + dw * 7, rh, fill=ZEBRA, noline=True)
        text(s, lx + 0.2, y, lw - 0.3, rh, lab, size=14, color=INK, anchor=MSO_ANCHOR.MIDDLE, bold=(r in (0, 1, 6, 7)))
        rect(s, dx + a * dw + 0.08, y + 0.17, (b - a + 1) * dw - 0.16, rh - 0.34, fill=col, radius=0.1)
        text(s, dx + a * dw + 0.08, y + 0.1, (b - a + 1) * dw - 0.16, rh - 0.2, st, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, MX, 10.0, W - 2 * MX, 0.5, "※ 11/19~11/21 막대는 실제 수행 기록이고, 11/22~11/25는 계획(PPT·최종 점검·시연 리허설)입니다.", size=13, color=MUTED)
    footer(s, n)
    return s


def actor(s, x, y, label, col):
    rect(s, x + 0.4, y, 0.7, 0.7, fill=col, shape=MSO_SHAPE.OVAL)
    rect(s, x + 0.2, y + 0.75, 1.1, 0.85, fill=col, radius=0.3)
    text(s, x - 0.6, y + 1.7, 2.7, 0.5, label, size=17, bold=True, color=INK, align=PP_ALIGN.CENTER)


def slide_usecase(prs, n):
    s = blank(prs)
    header(s, "USE CASE", "유스케이스", "액터 3종(비회원 · 사용자 · 관리자)이 쓰는 기능")
    rows = [("비회원", MUTED, ["지구본 보기", "여행지·항공편 조회", "투어·국내여행 조회", "호텔·크루즈 조회", "특별전·베스트셀러", "사진 출처 보기"]),
            ("사용자", ORANGE, ["회원가입·로그인", "장바구니 담기", "모의 결제", "내 예약·QR", "고객문의 등록", "계정 관리·탈퇴"]),
            ("관리자", BLUE, ["회원 이용 정지", "상품 등록·수정·삭제", "상품 노출 중지", "팝업 관리", "문의 답변", "예약 체크인"])]
    rect(s, 3.4, 2.65, 15.3, 7.45, fill=CARD, line=CARD_LINE, radius=0.15, lw=2)
    text(s, 3.6, 2.7, 6, 0.4, "나도 감 시스템", size=13, bold=True, color=MUTED)
    for r, (name, col, cases) in enumerate(rows):
        y = 3.1 + r * 2.35
        actor(s, 1.2, y + 0.1, name, col)
        line(s, 2.6, y + 0.9, 3.9, y + 0.9, color=col, width=2.5)
        for i, c in enumerate(cases):
            ox = 3.9 + (i % 3) * 4.9
            oy = y + (i // 3) * 1.05
            rect(s, ox, oy, 4.55, 0.9, fill=WHITE, line=col, shape=MSO_SHAPE.OVAL, lw=2)
            text(s, ox, oy, 4.55, 0.9, c, size=16, bold=True, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    footer(s, n)
    return s


def slide_workflow(prs, n):
    s = blank(prs)
    header(s, "WORKFLOW", "단위업무 워크플로우", "담기에서 체크인까지 — 가격은 서버가, 좌석은 조건부 UPDATE로 처리합니다")
    steps = [("장바구니 담기", "투어·호텔·크루즈·\n항공권·이동편\n날짜·인원 검증"), ("가격 재계산", "클라이언트 값이\n아니라 DB 값으로\n단가를 다시 계산"),
             ("결제 요청", "결제 수단만 선택\n(카드번호 미수집)"), ("좌석 차감", "같은 항공편·등급을\n합쳐 조건부 UPDATE\nseats_left ≥ 인원"),
             ("예약 저장", "예약 번호·QR 토큰\n발급, 예약 줄 저장\n장바구니 비움"), ("QR 확인", "/r/{토큰}\n로그인 없이\n예약 내용 확인"),
             ("체크인", "관리자가 예약 번호·\nQR로 조회해\n체크인 처리")]
    cw, gap = 2.1, 0.45
    x0 = (W - (cw * 7 + gap * 6)) / 2
    for i, (t, b) in enumerate(steps):
        x = x0 + i * (cw + gap)
        col = ORANGE if i < 5 else BLUE
        rect(s, x, 3.0, cw, 4.6, fill=CARD, radius=0.16)
        pill(s, x + 0.55, 3.25, 1.0, 0.55, "%02d" % (i + 1), fill=col, size=15)
        text(s, x + 0.1, 4.05, cw - 0.2, 0.7, t, size=18, bold=True, color=INK, align=PP_ALIGN.CENTER, spacing=1.1)
        text(s, x + 0.12, 4.95, cw - 0.24, 2.5, b, size=13.5, color=MUTED, align=PP_ALIGN.CENTER, spacing=1.35)
        if i < 6:
            line(s, x + cw + 0.03, 5.3, x + cw + gap - 0.03, 5.3, color=col, width=3, arrow=True)
    rect(s, MX, 8.2, W - 2 * MX, 1.6, fill=RGBColor(0xFD, 0xEC, 0xEA), line=ORANGE_INK, radius=0.14, lw=1.5)
    text(s, MX + 0.5, 8.35, 4, 0.5, "예외 처리", size=15, bold=True, color=ORANGE_INK)
    text(s, MX + 0.5, 8.85, W - 2 * MX - 1, 0.9,
         "좌석이 하나라도 부족하거나 판매가 중지되면 결제 전체를 거절하고 트랜잭션을 되돌립니다(이미 줄인 좌석도 원래대로). "
         "노출이 중지된 상품·운항하지 않는 요일·잔여 좌석 초과는 담는 단계에서 거절합니다.", size=15, color=INK, spacing=1.35)
    footer(s, n)
    return s


PKGS = [("home", "메인 대시보드"), ("travel", "해외 여행·항공편"), ("special", "이달의 특별전"), ("bestseller", "베스트셀러"),
        ("tour", "투어"), ("domestic", "국내여행"), ("stay", "호텔·크루즈"), ("cart", "장바구니·결제·예약"),
        ("qr", "QR 생성"), ("support", "고객문의"), ("popup", "이벤트 팝업"), ("auth", "가입·로그인"),
        ("account", "내 계정"), ("admin", "관리자 화면"), ("globe", "지구본 경로 API"), ("config", "보안 설정"), ("common", "공통 변환·사진")]


def slide_packages(prs, n):
    s = blank(prs)
    header(s, "CLASS · PACKAGE STRUCTURE", "패키지 구조", "기능(도메인) 단위로 나누고, 읽기와 쓰기 방식을 분리했습니다")
    cw, ch, gx, gy = 2.7, 1.35, 0.22, 0.28
    x0 = (W - (cw * 6 + gx * 5)) / 2
    for i, (p, d) in enumerate(PKGS):
        x = x0 + (i % 6) * (cw + gx)
        y = 2.75 + (i // 6) * (ch + gy)
        col = ORANGE if (i // 6 + i % 6) % 2 == 0 else BLUE
        rect(s, x, y, cw, ch, fill=CARD, radius=0.14)
        rect(s, x, y, cw, 0.1, fill=col)
        text(s, x + 0.2, y + 0.22, cw - 0.4, 0.5, p, size=17, bold=True, color=INK, font=MONO)
        text(s, x + 0.2, y + 0.78, cw - 0.4, 0.5, d, size=14, color=MUTED)
    # 읽기/쓰기 분리 설명
    y = 8.0
    card(s, MX, y, 8.5, 1.9, "읽기: JdbcClient + record", "화면용 조회는 SQL을 직접 쓰고 record 로 받습니다. 정렬·필터 값은 화이트리스트로 검증합니다.", accent=ORANGE, tsize=19, bsize=15)
    card(s, MX + 8.9, y, 8.5, 1.9, "쓰기: Spring Data JPA", "계정·예약·문의처럼 저장이 중요한 쓰기는 JPA 엔티티와 트랜잭션으로 처리합니다.", accent=BLUE, tsize=19, bsize=15)
    footer(s, n)
    return s


# ============================ PART 3 · 구현·평가 =====================================
def slide_env(prs, n):
    s = blank(prs)
    header(s, "DEVELOPMENT ENVIRONMENT", "개발 환경", "Java 17과 Spring Boot를 중심으로, 로컬은 H2로 바로 실행합니다")
    rows = [["구분", "사용 기술"],
            ["언어·런타임", "Java 17"],
            ["백엔드", "Spring Boot 4.1.2 · Spring Security(BCrypt) · Spring Data JPA · Spring JDBC(JdbcClient)"],
            ["화면", "Thymeleaf(서버 렌더링) · HTML/CSS/JavaScript · globe.gl(지구본)"],
            ["DB", "로컬 H2(MySQL 호환 모드) · 운영 MySQL 8 (mysql 프로필, 접속 정보는 환경변수)"],
            ["빌드·테스트", "Gradle 9.8.2 · JUnit 5 / Spring Boot Test (149개)"],
            ["라이브러리", "ZXing 3.5.3(QR) · Lombok"],
            ["도구", "IntelliJ · VS Code · Chrome(화면 확인) · Git · GitHub"]]
    table(s, MX, 2.8, [3.6, 13.8], rows, row_h=0.88, size=17)
    footer(s, n)
    return s


def slide_git(prs, n):
    s = blank(prs)
    header(s, "GIT STRATEGY", "Git 브랜치 전략과 커밋 규칙", "main에서 직접 개발하지 않고, 기능마다 feature 브랜치를 만들어 dev로 합칩니다")
    # 왼쪽: 브랜치 흐름
    box(s, MX, 2.9, 3.3, 1.2, "main", "안정 버전 (최종 병합)", fill=DARK, tcolor=WHITE, tsize=20, ssize=13)
    box(s, MX, 4.7, 3.3, 1.2, "dev", "통합 브랜치", fill=BLUE, tcolor=WHITE, tsize=20, ssize=13)
    box(s, MX, 6.5, 3.3, 1.2, "feature/*", "기능별 개발", fill=ORANGE, tcolor=WHITE, tsize=20, ssize=13)
    line(s, MX + 1.65, 6.5, MX + 1.65, 5.9, color=ORANGE, width=3, arrow=True)
    line(s, MX + 1.65, 4.7, MX + 1.65, 4.1, color=BLUE, width=3, arrow=True, dash=True)
    text(s, MX, 7.9, 3.4, 0.9, "feature → dev: 빠른 병합(fast-forward)\ndev → main: 최종 점검 후", size=12.5, color=MUTED, spacing=1.3)
    # 가운데: 실제 브랜치
    text(s, 5.2, 2.9, 7, 0.5, "실제 feature 브랜치 (앞 브랜치 위에 쌓음)", size=16, bold=True)
    names = ["project-setup", "travel", "login", "popup", "support", "tour", "domestic", "hotel", "cart", "qr", "admin",
             "destinations-100", "admin-crud", "light-theme-photos", "dest-photos", "readme", "status-colors"]
    cx, cy = 5.2, 3.5
    for i, nm in enumerate(names):
        x = cx + (i % 3) * 2.75
        y = cy + (i // 3) * 0.95
        rect(s, x, y, 2.6, 0.7, fill=CARD, radius=0.35)
        text(s, x, y, 2.6, 0.7, nm, size=12, color=INK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, font=MONO)
    # 오른쪽: 커밋 컨벤션
    rect(s, 14.0, 2.9, 4.7, 6.7, fill=CARD, radius=0.18)
    text(s, 14.3, 3.1, 4.2, 0.5, "커밋 컨벤션", size=18, bold=True, color=ORANGE_INK)
    text(s, 14.3, 3.7, 4.2, 0.9, "타입(범위): 제목", size=22, bold=True, color=INK, font=MONO)
    text(s, 14.3, 4.5, 4.2, 4.9,
         ["feat · fix · refactor · style", "docs · test · chore", "",
          "예)", "feat(photos): 여행지 사진·문구를 읽는 DestPhotos 추가", "fix(layout): 3열 카드가 넘치던 문제 수정", "style(theme): 성공 표시를 초록으로 바꿔 오류와 구분",
          "", "한 커밋에는 한 가지 변경, 제목은 50자 안쪽 한국어"], size=13.5, color=INK, spacing=1.35)
    footer(s, n)
    return s


def slide_core1(prs, n):
    s = blank(prs)
    header(s, "CORE DESIGN · CODE ①", "핵심 구현 ① 지구본", "기본 컨트롤을 끄고 회전을 직접 계산해, 어느 방향으로 돌려도 끊김 없이 돕니다")
    card(s, MX, 2.8, 6.6, 2.0, "경로: 선 + 불빛 겹치기", "같은 좌표로 주황 선과 그 위를 흐르는 불빛을 함께 그려 경로가 살아 있는 것처럼 보입니다.", accent=ORANGE, tsize=19, bsize=14.5)
    card(s, MX, 5.0, 6.6, 2.2, "회전: 직접 계산", "놓은 방향 그대로 관성을 주고(최대 1200도/초) 3초에 걸쳐 평소 속도(15도/초)로 돌아옵니다.", accent=BLUE, tsize=19, bsize=14.5)
    card(s, MX, 7.4, 6.6, 2.0, "경로 데이터: JSON API", "GET /api/globe/routes 가 도시 100곳 중 무작위 경로 60개를 내려줍니다.", accent=ORANGE, tsize=19, bsize=14.5)
    code_block(s, 8.3, 2.8, 10.4, 6.6, [
        "// home-globe.js",
        "var CRUISE    = 15 * RAD;     // 평소 회전 속도(15도/초)",
        "var FLICK_MAX = 1200 * RAD;   // 던질 때 최대 속도",
        "",
        "var controls = globe.controls();",
        "controls.enabled = false;     // 기본 회전은 끄고 직접 처리",
        "",
        "globe.pathsData(lines)        // 선 + 불빛을 같은 좌표로",
        "  .pathColor(function (d) {",
        "    if (d.light) return ['rgba(255,214,140,0)', 'rgba(255,252,240,1)'];",
        "    if (d.glow)  return ['rgba(255,90,54,0)', 'rgba(255,140,100,.7)'];",
        "    return 'rgba(255, 90, 54, 0.5)';   // 주황 선",
        "  })",
        "  .pathDashAnimateTime(function (d) {",
        "    return 3200 + d.total * 2400;      // 불빛이 흐르는 시간",
        "  });",
    ], size=13, title="src/main/resources/static/js/home-globe.js (발췌)")
    footer(s, n)
    return s


def slide_core2(prs, n):
    s = blank(prs)
    header(s, "CORE DESIGN · CODE ②", "핵심 구현 ② 결제와 좌석 차감", "마지막 남은 좌석을 두 사람이 동시에 사도 좌석이 음수가 되지 않게 했습니다")
    card(s, MX, 2.8, 6.6, 2.0, "서버가 가격을 계산", "장바구니와 결제의 단가는 클라이언트 값이 아니라 DB 값으로 다시 계산해 저장합니다.", accent=ORANGE, tsize=19, bsize=14.5)
    card(s, MX, 5.0, 6.6, 2.2, "조건부 UPDATE", "seats_left >= 인원 조건으로 한 번에 차감하고, 판매 중인 항공편만 대상으로 합니다.", accent=BLUE, tsize=19, bsize=14.5)
    card(s, MX, 7.4, 6.6, 2.0, "하나라도 부족하면 전체 취소", "예외로 트랜잭션을 되돌려 이미 줄인 좌석도 원래대로 돌아갑니다.", accent=ORANGE, tsize=19, bsize=14.5)
    code_block(s, 8.3, 2.8, 10.4, 6.6, [
        "// CartService.reserveFlightSeats (발췌)",
        "int n = jdbc.sql(\"\"\"",
        "    UPDATE flight_fare",
        "       SET seats_left = seats_left - :n, version = version + 1",
        "     WHERE flight_id = :flight AND cabin_class = :cabin",
        "       AND seats_left >= :n          -- 부족하면 0건",
        "       AND EXISTS (SELECT 1 FROM flight f",
        "                    WHERE f.flight_id = flight_fare.flight_id",
        "                      AND f.status = 'ON_SALE')",
        "    \"\"\").param(\"n\", need).param(\"flight\", flightId)",
        "      .param(\"cabin\", cabin).update();",
        "",
        "if (n == 0) {                        // 좌석 부족·판매 중지",
        "    throw new IllegalArgumentException(title + \" 남은 좌석이 부족해요.\");",
        "}                                    // → 트랜잭션 전체 롤백",
    ], size=13, title="src/main/java/com/nadogam/cart/CartService.java (발췌)")
    footer(s, n)
    return s


def slide_core3(prs, n):
    s = blank(prs)
    header(s, "CORE DESIGN · CODE ③", "핵심 구현 ③ 여행지 사진 카드", "DB와 쿼리를 건드리지 않고, 파일만 읽어 카드에 사진과 문구를 붙였습니다")
    card(s, MX, 2.8, 6.6, 2.0, "파일 기반 DestPhotos", "info.json(명소·특산)과 credits.json(받은 사진·출처)을 읽는 빈 하나가 전부 처리합니다.", accent=ORANGE, tsize=19, bsize=14.5)
    card(s, MX, 5.0, 6.6, 2.2, "사진이 없으면 그라데이션", "style() 이 빈 문자열을 돌려주면 기존 그라데이션 카드가 그대로 보입니다(댈러스).", accent=BLUE, tsize=19, bsize=14.5)
    card(s, MX, 7.4, 6.6, 2.0, "출처는 반드시 표기", "저작자·라이선스를 상세 머리글과 /photo-credits 화면에 보여 줍니다(CC BY-SA 등).", accent=ORANGE, tsize=19, bsize=14.5)
    code_block(s, 8.3, 2.8, 10.4, 6.6, [
        "// DestPhotos.java (발췌) — 템플릿에서 @destPhotos 로 부름",
        "public String style(String kind, long id) {",
        "    return credits.containsKey(key(kind, id))",
        "        ? \";--photo:url(/img/dest/\" + key(kind, id) + \".jpg)\"",
        "        : \"\";                    // 사진이 없으면 아무것도 붙이지 않는다",
        "}",
        "",
        "/* CSS: 사진 레이어를 그라데이션 위에 얹는다 */",
        ".dest-card {",
        "  background: var(--photo, linear-gradient(transparent, transparent))",
        "              center / cover no-repeat,",
        "              linear-gradient(135deg, var(--c1), var(--c2));",
        "}",
        "",
        "<!-- Thymeleaf -->",
        "th:style=\"|--c1:${d.from()};--c2:${d.to()}",
        "   ${@destPhotos.style('overseas', d.destinationId())}|\"",
    ], size=12.5, title="DestPhotos.java · travel.css · travel/index.html (발췌)")
    footer(s, n)
    return s


def slide_tests(prs, n):
    s = blank(prs)
    tests = test_counts()
    total = sum(t[1] for t in tests)
    fails = sum(t[2] for t in tests)
    header(s, "VERIFICATION", "테스트 · 검증 결과", "자동 테스트 %d개 통과(실패 %d) + 브라우저로 핵심 흐름을 직접 점검했습니다" % (total, fails))
    rect(s, MX, 2.8, 4.6, 3.1, fill=DARK, radius=0.2)
    text(s, MX, 3.0, 4.6, 1.7, str(total), size=96, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    text(s, MX, 4.9, 4.6, 0.6, "테스트 통과 · 실패 %d" % fails, size=18, bold=True, color=RGBColor(0xFF, 0x9A, 0x7A), align=PP_ALIGN.CENTER)
    mx = max(t[1] for t in tests)
    cols = 2
    per = (len(tests) + cols - 1) // cols
    for i, (name, cnt, _f) in enumerate(sorted(tests, key=lambda t: -t[1])):
        c, r = i // per, i % per
        x = 6.3 + c * 6.8
        y = 2.75 + r * 0.43
        text(s, x, y, 2.5, 0.4, name, size=11.5, color=INK, font=MONO)
        rect(s, x + 2.55, y + 0.08, 3.0 * cnt / mx, 0.24, fill=ORANGE if c == 0 else BLUE, radius=0.05)
        text(s, x + 2.65 + 3.0 * cnt / mx, y, 0.6, 0.4, str(cnt), size=11.5, bold=True, color=INK)
    text(s, MX, 6.75, 8, 0.5, "화면 점검 (11/21, 브라우저)", size=18, bold=True)
    checks = [("담기 → 결제 → 예약", "금액 일치\n(1,780,000 + 1,580,000×2 = 4,940,000)"), ("좌석 차감", "일반석 잔여 좌석\n58석 → 56석"),
              ("QR · 체크인", "QR 확인 화면과\n관리자 체크인 처리 정상"), ("모바일 390px", "장바구니·예약·문의·호텔\n화면 정상")]
    cw = 4.0
    for i, (t, b) in enumerate(checks):
        x = MX + i * (cw + 0.4)
        card(s, x, 7.4, cw, 2.9, t, b, accent=ORANGE if i % 2 == 0 else BLUE, tsize=16, bsize=13)
    footer(s, n)
    return s


def slide_trouble(prs, n):
    s = blank(prs)
    header(s, "TROUBLESHOOTING", "트러블슈팅", "막힌 문제와 해결 — 대표 5가지")
    rows = [["문제", "원인", "해결"],
            ["지구본이 멈춘 느낌", "놓으면 0에서 다시 가속하고 던진 속도가 1.6초에 급감", "기본 컨트롤을 끄고 직전 회전을 이어 가며 시간 기반으로 감속"],
            ["Thymeleaf에서 @빈 호출 오류", "fragment 호출 인자에서는 빈 접근이 막히고, th:if가 th:with보다 먼저 평가됨", "번호·이름만 넘기고 조각 안에서 조회, th:block으로 감쌈"],
            ["성공 안내가 오류처럼 보임", "포인트 색(#ff5a36)이 붉은 계열이라 성공·판매 중과 오류·중지가 비슷함", "성공용 초록(--ok)을 추가하고 화면으로 의미가 섞이지 않는지 확인"],
            ["국내여행 화면 500 오류", "JdbcClient 레코드 매핑에서 컬럼 별칭이 필드명과 달랐음", "SELECT에 AS 별칭을 붙여 필드명과 맞춤"],
            ["CSS를 고쳐도 화면이 그대로", "개발 서버가 시작 시점의 CSS 사본과 브라우저 캐시를 사용", "정적 파일 캐시를 끄고 서버를 다시 시작"]]
    table(s, MX, 2.75, [4.2, 6.7, 6.5], rows, row_h=1.12, size=13)
    text(s, MX, 9.75, W - 2 * MX, 0.5, "이 밖에 Wikimedia 요청 한도(429)에 걸려 요청 간격을 늘리고 Retry-After를 지키도록 고쳤습니다.", size=14, color=MUTED)
    footer(s, n)
    return s


def slide_result(prs, n):
    s = blank(prs)
    header(s, "RESULT · ACHIEVEMENT", "성과 · 목표 달성도", "목표로 세운 4가지를 모두 구현했고, 기능 구현 27개 항목을 완료했습니다")
    rows = [["목표", "결과", "달성"],
            ["지구본으로 보는 노선", "도시 100곳 · 경로 60개 · 끊김 없는 자유 회전", "완료"],
            ["여행지 먼저 → 출발지 → 항공편", "여행지 100곳 · 항공편 304편 · 직항/경유·정렬", "완료"],
            ["예약까지 한 흐름", "장바구니 · 모의 결제 · 좌석 차감 · QR · 체크인", "완료"],
            ["운영 기능", "상품 CRUD · 노출 관리 · 팝업 · 문의 답변 · 체크인", "완료"],
            ["품질", "자동 테스트 149개 통과 · 화면 점검 완료", "완료"]]
    table(s, MX, 2.75, [5.6, 9.2, 2.6], rows, row_h=0.8, size=15,
          aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.CENTER])
    stats = [("27", "기능 구현 항목(3.1~3.27)"), ("78", "요구사항"), ("43", "기능"), ("52", "API"), ("25", "테이블")]
    cw = 3.2
    for i, (v, l) in enumerate(stats):
        x = MX + i * (cw + 0.35)
        rect(s, x, 8.1, cw, 1.8, fill=CARD, radius=0.16)
        text(s, x, 8.2, cw, 1.0, v, size=44, bold=True, color=ORANGE if i % 2 == 0 else BLUE, align=PP_ALIGN.CENTER)
        text(s, x, 9.2, cw, 0.5, l, size=14, color=INK, align=PP_ALIGN.CENTER)
    footer(s, n)
    return s


def slide_next(prs, n):
    s = blank(prs)
    header(s, "LIMITATIONS & NEXT", "한계 · 개선 계획 · 향후 확장", "지금의 한계를 알고, 2단계에서 보완할 계획입니다")
    rect(s, MX, 2.8, 8.4, 6.9, fill=CARD, radius=0.18)
    text(s, MX + 0.5, 3.0, 7, 0.5, "현재의 한계", size=22, bold=True, color=ORANGE_INK)
    bullets(s, MX + 0.5, 3.7, 7.5, 6.0, ["결제는 모의 처리(카드 정보 미수집)", "항공권 재고가 날짜별이 아니라 항공편 단위", "댈러스 사진이 없어 그라데이션 카드", "지구본은 인터넷(CDN)이 필요", "실제 휴대폰 QR 스캔·MySQL 실행은 미확인"], size=19, gap=1.75)
    rect(s, MX + 8.9, 2.8, 8.5, 6.9, fill=CARD, radius=0.18)
    text(s, MX + 9.4, 3.0, 7, 0.5, "2단계 계획", size=22, bold=True, color=BLUE)
    roadmap = [("01", "날짜별 재고 + 낙관적 락, 100명 동시 예약 테스트"), ("02", "실제 결제 연동(테스트 모드), 성능 개선(Redis·k6)"),
               ("03", "'나도 감' 동행 모집"), ("04", "후기·찜, FAQ·공지"), ("05", "Docker · GitHub Actions · 배포")]
    for i, (no, t) in enumerate(roadmap):
        y = 3.75 + i * 1.18
        pill(s, MX + 9.4, y, 0.7, 0.55, no, fill=BLUE, size=14)
        text(s, MX + 10.3, y - 0.03, 6.8, 1.0, t, size=18, color=INK, spacing=1.25)
    footer(s, n)
    return s


def slide_qna(prs, n):
    s = blank(prs, BG)
    rect(s, 0, 0, 0.5, H, fill=ORANGE)
    text(s, 1.6, 3.2, 9, 3, "Q & A", size=130, bold=True, color=INK)
    text(s, 1.7, 6.6, 9, 0.8, "질의응답", size=34, bold=True, color=ORANGE_INK)
    text(s, 1.7, 7.5, 9, 0.6, "궁금한 점을 편하게 물어봐 주세요", size=18, color=MUTED)
    pic(s, "mascot.png", 11.0, 2.9, w=7.4, border=False)
    footer(s, n, strip=False)
    return s


def slide_thanks(prs, n):
    s = blank(prs, DARK)
    rect(s, 0, 0, 0.5, H, fill=ORANGE)
    text(s, 1.6, 3.4, 12, 2, "THANK YOU", size=96, bold=True, color=WHITE)
    text(s, 1.7, 5.6, 12, 0.9, "감사합니다", size=40, bold=True, color=RGBColor(0xFF, 0x9A, 0x7A))
    text(s, 1.7, 7.0, 12, 0.6, "나도 감 (nado_gam) — 4차 개인 프로젝트", size=20, color=RGBColor(0xC9, 0xCE, 0xDD))
    text(s, 1.7, 7.7, 12, 0.6, "발표자 이윤호 · 2026년 11월 25일", size=18, color=RGBColor(0x9A, 0xA3, 0xBA))
    text(s, 1.7, 8.6, 14, 0.6, "github.com/ho8566z/nado_gam  ·  github.com/ho8566z/nado_gam_word", size=15, color=RGBColor(0x9A, 0xA3, 0xBA))
    footer(s, n, dark=True)
    return s


SLIDES = [
    slide_cover,                                                                              # 1
    slide_index,                                                                              # 2
    lambda p, n: slide_part(p, n, "01", "PART 1 · PLAN", "프로젝트 기획", ["프로젝트 소개", "주제 선정 배경 · 목표", "벤치마킹 · 차별점", "활용 방안 · 기대 효과"]),   # 3
    slide_intro, slide_background, slide_goals, slide_benchmark, slide_difference, slide_effect,   # 4-9
    lambda p, n: slide_part(p, n, "02", "PART 2 · DESIGN", "시연 및 설계", ["시나리오 · 시연(캡처)", "서비스 구성도 · 메뉴 구성", "ERD · 명세서 · API", "WBS · 유스케이스 · 워크플로우", "패키지 구조"], BLUE),   # 10
    slide_scenario, slide_demo_flow, slide_demo1, slide_demo2, slide_demo3,                   # 11-15
    slide_architecture, slide_menu, slide_erd, slide_spec_summary, slide_api,                 # 16-20
    slide_wbs, slide_usecase, slide_workflow, slide_packages,                                 # 21-24
    lambda p, n: slide_part(p, n, "03", "PART 3 · DELIVER", "구현 및 평가", ["개발 환경 · Git 전략", "핵심 구현 3가지", "테스트 · 트러블슈팅", "성과 · 한계 · 향후 확장"], INK),   # 25
    slide_env, slide_git, slide_core1, slide_core2, slide_core3,                              # 26-30
    slide_tests, slide_trouble, slide_result, slide_next,                                     # 31-34
    slide_qna, slide_thanks,                                                                  # 35-36
]


def main(mode="all"):
    prepare_assets()
    prs = new_prs()
    todo = SLIDES if mode == "all" else SLIDES[:3] + [SLIDES[3]] + [SLIDES[13]]
    for fn in todo:
        n = len(prs.slides) + 1
        if mode != "all":
            n = {0: 1, 1: 2, 2: 3, 3: 4, 4: 13}[len(prs.slides)]
        fn(prs, n)
    out = os.path.join(HERE, "나도감_발표_샘플5장.pptx" if mode == "sample" else "나도감_발표.pptx")
    prs.save(out)
    print("저장:", out, "슬라이드", len(prs.slides))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
