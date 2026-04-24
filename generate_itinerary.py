from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import math

# Register fonts
pdfmetrics.registerFont(TTFont('Georgia', '/System/Library/Fonts/Supplemental/Georgia.ttf'))
pdfmetrics.registerFont(TTFont('Georgia-Bold', '/System/Library/Fonts/Supplemental/Georgia Bold.ttf'))
pdfmetrics.registerFont(TTFont('Georgia-Italic', '/System/Library/Fonts/Supplemental/Georgia Italic.ttf'))
pdfmetrics.registerFont(TTFont('Georgia-BoldItalic', '/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf'))

# Japan-themed palette
CRIMSON     = HexColor('#9B1B30')   # deep Japan red
SAKURA      = HexColor('#F2A7BB')   # sakura pink
SAKURA_PALE = HexColor('#FDF0F4')   # very pale pink bg
CREAM       = HexColor('#FDF6EC')   # warm cream
GOLD        = HexColor('#C9A84C')   # muted gold
INK         = HexColor('#1C1C2E')   # near-black ink
MIST        = HexColor('#8E9BAF')   # blue-grey mist
WHITE       = HexColor('#FFFFFF')
RULE        = HexColor('#D4A5B5')   # soft rule line

W, H = A4  # 595 x 842 pt

OUTPUT = '/Users/edwinchong/Documents/ClaudeCode/FirstTest/Osaka_Driving_2026.pdf'

# ── helpers ──────────────────────────────────────────────────────────────────

def draw_seigaiha(c, cx, cy, r=18, rows=4, cols=5, alpha=0.08):
    """Seigaiha (wave) pattern — overlapping arcs, very faint."""
    c.saveState()
    c.setFillColor(CRIMSON)
    c.setStrokeColor(CRIMSON)
    c.setFillAlpha(alpha)
    c.setStrokeAlpha(alpha * 1.5)
    c.setLineWidth(0.5)
    for row in range(rows):
        for col in range(cols):
            x = cx + col * r * 1.8 - (row % 2) * r * 0.9
            y = cy + row * r * 1.1
            p = c.beginPath()
            p.arc(x - r, y - r, x + r, y + r, 0, 180)
            p.close()
            c.drawPath(p, fill=1, stroke=1)
    c.restoreState()

def draw_sakura(c, cx, cy, size=14, alpha=0.55):
    """Five-petal sakura blossom."""
    c.saveState()
    c.setFillColor(SAKURA)
    c.setFillAlpha(alpha)
    c.setStrokeColor(CRIMSON)
    c.setStrokeAlpha(alpha * 0.6)
    c.setLineWidth(0.4)
    for i in range(5):
        angle = math.radians(i * 72 - 90)
        px = cx + math.cos(angle) * size * 0.55
        py = cy + math.sin(angle) * size * 0.55
        p = c.beginPath()
        p.ellipse(px - size * 0.28, py - size * 0.42,
                  px + size * 0.28, py + size * 0.42)
        c.rotate_around = angle
        # Draw rotated petal via transform
        c.saveState()
        c.transform(math.cos(angle), math.sin(angle),
                    -math.sin(angle), math.cos(angle), px, py)
        c.ellipse(-size * 0.28, -size * 0.42, size * 0.28, size * 0.42,
                  stroke=1, fill=1)
        c.restoreState()
    # centre
    c.setFillColor(GOLD)
    c.setFillAlpha(alpha)
    c.circle(cx, cy, size * 0.12, stroke=0, fill=1)
    c.restoreState()

def scatter_sakura(c, positions):
    for (x, y, sz, a) in positions:
        draw_sakura(c, x, y, sz, a)

def horizontal_rule(c, x, y, width, col=RULE, thick=0.6):
    c.saveState()
    c.setStrokeColor(col)
    c.setLineWidth(thick)
    c.line(x, y, x + width, y)
    c.restoreState()

def day_badge(c, x, y, number, col=CRIMSON):
    """Red circle badge with day number."""
    r = 13
    c.saveState()
    c.setFillColor(col)
    c.circle(x, y, r, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont('Georgia-Bold', 8)
    lbl = str(number)
    c.drawCentredString(x, y - 3, lbl)
    c.restoreState()

# ── data ─────────────────────────────────────────────────────────────────────

DAYS = [
    (1,  'Wednesday',  '20 May',  'Rinku Town',
     ['Arrive at Kansai Airport', 'Explore Rinku Premium Outlets'],
     'Odysis Suites Osaka Airport Hotel', 'Trip.com'),

    (2,  'Thursday',   '21 May',  'Uji',
     ['Byodoin Temple & Phoenix Hall', 'Uji tea houses & matcha', 'Ujigami Shrine'],
     'Lake Biwa Marriott Hotel', 'Bonvoy · Breakfast incl.'),

    (3,  'Friday',     '22 May',  'Omi-Hachiman',
     ['Hachiman-bori canal boat ride', 'Merchant townscape (Edo-era)', 'Chomeiji Temple on Mt. Kinugasa'],
     'Lake Biwa Marriott Hotel', 'Bonvoy · Breakfast incl.'),

    (4,  'Saturday',   '23 May',  'Lake Biwa',
     ['Scenic driveway along the lake shore', 'Shirahige Shrine floating torii', 'Mangetsuji Temple (Uki-mido)'],
     'Lake Biwa Marriott Hotel', 'Bonvoy · Breakfast incl.'),

    (5,  'Sunday',     '24 May',  'Kayabuki-no-Sato',
     ['Miyama thatched-roof village', 'Biwako Valley Ropeway', 'Countryside cycling & local craft stalls'],
     'Fairfield by Marriott Kyoto (Amanohashidate)', 'Bonvoy'),

    (6,  'Monday',     '25 May',  'Ine Bay & Amanohashidate',
     ['Ine Funaya fishing-house boat garages', 'Scenic boat tour of Ine Bay',
      'Amanohashidate sandbar viewpoint (Kasamatsu Park)'],
     'Fairfield by Marriott Kyoto (Amanohashidate)', 'Bonvoy'),

    (7,  'Tuesday',    '26 May',  'Marine World & Yumura Onsen',
     ['Kinosaki Marine World — dolphin & sea lion shows', 'Soak in Yumura Onsen hot springs',
      'Yukata stroll through onsen town'],
     'Asanoya, Yumura Onsen', 'Trip.com · Breakfast & Dinner incl.'),

    (8,  'Wednesday',  '27 May',  'Himeji',
     ['Himeji Castle — UNESCO World Heritage', 'Kokoen Garden', 'Samurai & folk museum'],
     'Smile Hotel Okayama', 'Trip.com · Breakfast incl.'),

    (9,  'Thursday',   '28 May',  'Okayama',
     ['Korakuen Garden (one of Japan\'s top 3)', 'Okayama Castle (Crow Castle)', 'Bizen pottery town'],
     'Smile Hotel Okayama', 'Trip.com · Breakfast incl.'),

    (10, 'Friday',     '29 May',  'Naoshima Art Island',
     ['Chichu Art Museum (Monet / Turrell / De Maria)', 'Yayoi Kusama\'s iconic Pumpkin sculpture',
      'Benesse House & waterfront art installations'],
     'Hotel Sunroute Tokushima', 'Trip.com'),

    (11, 'Saturday',   '30 May',  'Naruto & Kobe',
     ['Naruto whirlpools boat tour', 'Uzushio glass-floor walkway',
      'Nada sake brewery district, Kobe'],
     'Tanimachi-Kun Hotel Ebisucho 72, Osaka', 'Trip.com'),

    (12, 'Sunday',     '31 May',  'Osaka — Discovery Day',
     ['Dotonbori neon canal walk', 'Kuromon Ichiba market food crawl', 'Osaka Castle & Nishinomaru Garden'],
     'Tanimachi-Kun Hotel Ebisucho 72, Osaka', 'Trip.com'),

    (13, 'Monday',     '1 June',  'Osaka — City Day',
     ['Shinsekai & Tsutenkaku Tower', 'Den Den Town electronics district',
      'Namba Grand Kagetsu comedy theatre'],
     'Tanimachi-Kun Hotel Ebisucho 72, Osaka', 'Trip.com'),

    (14, 'Tuesday',    '2 June',  'Osaka — Farewell',
     ['Morning at leisure / last-minute shopping', 'Return rental car', 'Head to Kansai Airport'],
     '— Check out & fly home —', ''),
]

# ── cover page ────────────────────────────────────────────────────────────────

def cover(c):
    # Background
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Red accent strip on left
    c.setFillColor(CRIMSON)
    c.rect(0, 0, 18, H, fill=1, stroke=0)

    # Cream content area
    c.setFillColor(CREAM)
    c.rect(18, 60, W - 18, H - 120, fill=1, stroke=0)

    # Seigaiha watermark top-right
    draw_seigaiha(c, W - 80, H - 10, r=22, rows=5, cols=4, alpha=0.07)

    # Floating sakura
    blooms = [
        (W - 55, H - 55, 20, 0.5),
        (W - 95, H - 80, 14, 0.4),
        (W - 40, H - 100, 11, 0.3),
        (60, 110, 18, 0.45),
        (90,  80, 13, 0.35),
        (W - 70, 130, 15, 0.4),
    ]
    scatter_sakura(c, blooms)

    # Red circle motif (rising sun)
    c.saveState()
    c.setFillColor(CRIMSON)
    c.setFillAlpha(0.12)
    c.circle(W - 90, H - 90, 130, stroke=0, fill=1)
    c.restoreState()

    # Japanese vertical text strip (decorative kana)
    c.saveState()
    c.setFont('Georgia-Italic', 9)
    c.setFillColor(CRIMSON)
    c.setFillAlpha(0.55)
    kana = ['大', '阪', 'ド', 'ラ', 'イ', 'ブ']
    for i, ch in enumerate(kana):
        c.drawString(26, H - 130 - i * 22, ch)
    c.restoreState()

    # Title block
    title_y = H - 180
    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 38)
    c.drawString(50, title_y, 'Osaka Driving')

    c.setFillColor(GOLD)
    c.setFont('Georgia', 38)
    c.drawString(50, title_y - 48, '2026')

    # Thin gold rule
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(50, title_y - 62, 340, title_y - 62)

    # Sub-heading
    c.setFillColor(INK)
    c.setFont('Georgia-Italic', 14)
    c.drawString(50, title_y - 82, 'A 14-Day Road Journey Through the Heart of Japan')

    # Date block
    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 12)
    c.drawString(50, title_y - 115, '20 MAY  —  2 JUNE 2026')
    c.setFillColor(MIST)
    c.setFont('Georgia', 10)
    c.drawString(50, title_y - 132, 'Departing Singapore 19 May  ·  Returning 3 June')

    # Route overview box
    box_y = 180
    c.setStrokeColor(RULE)
    c.setLineWidth(0.8)
    c.setFillColor(SAKURA_PALE)
    c.roundRect(50, box_y, W - 100, 145, 6, fill=1, stroke=1)

    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 10)
    c.drawString(66, box_y + 118, 'ROUTE AT A GLANCE')
    horizontal_rule(c, 66, box_y + 112, W - 132, RULE, 0.5)

    route = [
        ('Kansai Region',   'Rinku Town · Uji · Omi-Hachiman'),
        ('Lake Biwa Area',  'Lake Biwa · Kayabuki-no-Sato · Ine Bay'),
        ('San\'in Coast',   'Amanohashidate · Yumura Onsen'),
        ('San\'yo & Shikoku', 'Himeji · Okayama · Naoshima · Naruto'),
        ('Return to Osaka', 'Kobe · Dotonbori · City Exploration'),
    ]
    c.setFont('Georgia', 9)
    for i, (region, spots) in enumerate(route):
        ry = box_y + 96 - i * 18
        c.setFillColor(CRIMSON)
        c.setFont('Georgia-Bold', 9)
        c.drawString(66, ry, region + ':')
        c.setFillColor(INK)
        c.setFont('Georgia', 9)
        c.drawString(185, ry, spots)

    # Footer
    c.setFillColor(MIST)
    c.setFont('Georgia-Italic', 8)
    c.drawCentredString(W / 2, 38, '✦  Itinerary prepared for personal travel  ✦')

    c.showPage()

# ── hotel overview page ───────────────────────────────────────────────────────

def hotels_overview(c):
    page_bg(c)

    y = H - 55
    section_title(c, 'Accommodation Overview', y)
    y -= 28

    horizontal_rule(c, 40, y, W - 80)
    y -= 18

    rows = [
        ('Night(s)', 'Date(s)', 'Hotel', 'Booking'),
        ('1',  '20 May',       'Odysis Suites Osaka Airport Hotel',          'Trip.com'),
        ('3',  '21–23 May',    'Lake Biwa Marriott Hotel',                   'Bonvoy · B'),
        ('2',  '24–25 May',    'Fairfield by Marriott Kyoto (Amanohashidate)','Bonvoy'),
        ('1',  '26 May',       'Asanoya, Yumura Onsen',                      'Trip.com · B+D'),
        ('2',  '27–28 May',    'Smile Hotel Okayama',                        'Trip.com · B'),
        ('1',  '29 May',       'Hotel Sunroute Tokushima',                   'Trip.com'),
        ('3',  '30 May–1 Jun', 'Tanimachi-Kun Hotel Ebisucho 72, Osaka',     'Trip.com'),
    ]

    col_x = [42, 82, 145, 430]
    col_w = [38, 60, 282, 115]

    for i, row in enumerate(rows):
        is_header = (i == 0)
        row_h = 22 if is_header else 26
        if is_header:
            c.setFillColor(CRIMSON)
            c.rect(42, y - row_h + 6, W - 84, row_h, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont('Georgia-Bold', 9)
        else:
            if i % 2 == 0:
                c.setFillColor(SAKURA_PALE)
                c.rect(42, y - row_h + 6, W - 84, row_h, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont('Georgia', 9.5)

        for j, cell in enumerate(row):
            c.drawString(col_x[j] + 4, y - 2, cell)

        y -= row_h

    y -= 10
    horizontal_rule(c, 40, y, W - 80)
    y -= 18

    c.setFillColor(MIST)
    c.setFont('Georgia-Italic', 8.5)
    c.drawString(42, y, 'B = Breakfast included    D = Dinner included    Bonvoy = Marriott Bonvoy member rate')

    # Sakura decoration
    scatter_sakura(c, [(W - 60, 90, 16, 0.4), (W - 95, 65, 11, 0.3), (W - 42, 60, 10, 0.3)])
    page_footer(c)
    c.showPage()

# ── shared page elements ──────────────────────────────────────────────────────

def page_bg(c):
    c.setFillColor(WHITE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # left accent
    c.setFillColor(CRIMSON)
    c.rect(0, 0, 6, H, fill=1, stroke=0)
    # faint seigaiha bottom-right
    draw_seigaiha(c, W - 20, 20, r=18, rows=3, cols=4, alpha=0.05)

def section_title(c, text, y):
    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 16)
    c.drawString(40, y, text)

def page_footer(c, txt='Osaka Driving 2026'):
    c.setFillColor(RULE)
    c.rect(0, 0, W, 22, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont('Georgia-Italic', 7.5)
    c.drawCentredString(W / 2, 7, txt + '  ·  Personal Travel Itinerary')

# ── day pages — 2 per physical page ──────────────────────────────────────────

def day_block(c, day_data, x, y, bw, bh):
    num, weekday, date, dest, activities, hotel, booking = day_data

    # Card background
    c.setFillColor(CREAM)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.roundRect(x, y, bw, bh, 8, fill=1, stroke=1)

    # Crimson header band
    c.setFillColor(CRIMSON)
    c.roundRect(x, y + bh - 38, bw, 38, 8, fill=1, stroke=0)
    # Patch bottom of header corners to be square
    c.rect(x, y + bh - 38, bw, 12, fill=1, stroke=0)

    # Day badge
    day_badge(c, x + 26, y + bh - 19, num, col=WHITE)
    c.setFillColor(CRIMSON)
    c.circle(x + 26, y + bh - 19, 13, stroke=0, fill=0)
    # Redo: white text on CREAM circle
    c.setFillColor(SAKURA_PALE)
    c.circle(x + 26, y + bh - 19, 13, stroke=0, fill=1)
    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 9)
    c.drawCentredString(x + 26, y + bh - 22, str(num))

    # Destination title
    c.setFillColor(WHITE)
    c.setFont('Georgia-Bold', 12)
    title = dest if len(dest) <= 28 else dest[:25] + '…'
    c.drawString(x + 46, y + bh - 17, title)

    # Weekday + date
    c.setFont('Georgia-Italic', 8)
    c.setFillColor(SAKURA)
    c.drawString(x + 46, y + bh - 30, weekday + '  ·  ' + date)

    # Divider
    horizontal_rule(c, x + 12, y + bh - 46, bw - 24, RULE, 0.5)

    # Activities
    c.setFillColor(INK)
    c.setFont('Georgia', 8.5)
    ay = y + bh - 62
    for act in activities[:4]:
        txt = act if len(act) <= 52 else act[:49] + '…'
        c.setFillColor(CRIMSON)
        c.circle(x + 20, ay + 3, 2.2, fill=1, stroke=0)
        c.setFillColor(INK)
        c.drawString(x + 28, ay, txt)
        ay -= 16

    # Hotel strip
    hstrip_y = y + 10
    c.setFillColor(SAKURA_PALE)
    c.rect(x + 1, hstrip_y, bw - 2, 30, fill=1, stroke=0)
    horizontal_rule(c, x + 12, hstrip_y + 30, bw - 24, RULE, 0.4)

    c.setFillColor(CRIMSON)
    c.setFont('Georgia-Bold', 7.5)
    c.drawString(x + 14, hstrip_y + 18, 'STAY')
    c.setFillColor(INK)
    c.setFont('Georgia', 8)
    hotel_text = hotel if len(hotel) <= 46 else hotel[:43] + '…'
    c.drawString(x + 40, hstrip_y + 18, hotel_text)
    if booking:
        c.setFillColor(MIST)
        c.setFont('Georgia-Italic', 7.5)
        c.drawString(x + 40, hstrip_y + 6, booking)

def days_page(c, pair):
    page_bg(c)

    margin_x = 32
    gap = 14
    bw = (W - 2 * margin_x - gap) / 2
    bh = (H - 80) * 0.92
    top_y = 45

    for i, d in enumerate(pair):
        bx = margin_x + i * (bw + gap)
        day_block(c, d, bx, top_y, bw, bh)
        # small sakura in corner
        scatter_sakura(c, [(bx + bw - 18, top_y + bh - 5, 10, 0.35)])

    page_footer(c)
    c.showPage()

# ── main ──────────────────────────────────────────────────────────────────────

def build():
    c = canvas.Canvas(OUTPUT, pagesize=A4)
    c.setTitle('Osaka Driving 2026 — Itinerary')
    c.setAuthor('Personal Travel Plan')

    cover(c)
    hotels_overview(c)

    # Pair days, 2 per page
    for i in range(0, len(DAYS), 2):
        pair = DAYS[i:i+2]
        days_page(c, pair)

    c.save()
    print(f'PDF saved to {OUTPUT}')

build()
