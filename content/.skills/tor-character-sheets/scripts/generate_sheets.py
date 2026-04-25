#!/usr/bin/env python3
"""Generate TOR 2e character sheets — 4 pages per hero, Czech only, with stories."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

# Register fonts
pdfmetrics.registerFont(TTFont('DV', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DVI', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'))
pdfmetrics.registerFont(TTFont('DVC', '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf'))
pdfmetrics.registerFont(TTFont('DVCB', '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DVCI', '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Oblique.ttf'))

W, H = A4
M = 12*mm  # margin
CW = W - 2*M  # content width

# Colors
DARK = colors.HexColor('#2C1810')
MID = colors.HexColor('#8B4513')
ACCENT = colors.HexColor('#B22222')
GRID = colors.HexColor('#D4C4B0')
LIGHT = colors.HexColor('#FFF8F0')
HDR_BG = colors.HexColor('#3C2415')
SECTION_BG = colors.HexColor('#F5EDE3')


class Sheet:
    def __init__(self, c):
        self.c = c

    def box(self, x, y, w, h, title=None):
        c = self.c
        c.setFillColor(LIGHT)
        c.roundRect(x, y, w, h, 2*mm, fill=1, stroke=0)
        c.setStrokeColor(GRID)
        c.setLineWidth(0.5)
        c.roundRect(x, y, w, h, 2*mm, fill=0, stroke=1)
        if title:
            th = 7*mm
            c.setFillColor(HDR_BG)
            c.roundRect(x, y+h-th, w, th, 2*mm, fill=1, stroke=0)
            c.rect(x, y+h-th, w, 3*mm, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont('DVCB', 7.5)
            c.drawString(x+3*mm, y+h-th+2*mm, title)
        return y + h  # return top

    def txt(self, x, y, s, font='DVC', size=7, col=DARK):
        self.c.setFont(font, size)
        self.c.setFillColor(col)
        self.c.drawString(x, y, s)

    def txtr(self, x, y, s, font='DVC', size=7, col=DARK):
        self.c.setFont(font, size)
        self.c.setFillColor(col)
        self.c.drawRightString(x, y, s)

    def txtc(self, x, y, s, font='DVC', size=7, col=DARK):
        self.c.setFont(font, size)
        self.c.setFillColor(col)
        self.c.drawCentredString(x, y, s)

    def hline(self, x1, y, x2, col=GRID, w=0.3):
        self.c.setStrokeColor(col)
        self.c.setLineWidth(w)
        self.c.line(x1, y, x2, y)

    def dots(self, x, y, rating, max_dots=6, r=1.3*mm, gap=3.2*mm):
        """Draw rating dots — filled for rating, empty for rest."""
        for i in range(max_dots):
            cx = x + i * gap
            if i < rating:
                self.c.setFillColor(ACCENT)
                self.c.circle(cx, y, r, fill=1, stroke=0)
            else:
                self.c.setStrokeColor(GRID)
                self.c.setLineWidth(0.4)
                self.c.setFillColor(colors.white)
                self.c.circle(cx, y, r, fill=1, stroke=1)

    def skill_row(self, x, y, w, name, rating, favoured=False):
        """Draw one skill row — Czech name + dots, no English."""
        self.hline(x, y, x+w)
        star = "★ " if favoured else "   "
        self.txt(x+1*mm, y+1.2*mm, f"{star}{name}", 'DVC', 7)
        # dots on the right side with proper spacing
        dot_x = x + w - 22*mm
        self.dots(dot_x, y+2.2*mm, rating)

    def header(self, hero):
        """Draw page header."""
        c = self.c
        hh = 20*mm
        c.setFillColor(HDR_BG)
        c.rect(0, H-hh, W, hh, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont('DVB', 18)
        c.drawString(M, H-13*mm, hero['name'])
        c.setFont('DVI', 8)
        c.setFillColor(colors.HexColor('#D4C4B0'))
        info = f"{hero['culture']}  •  {hero['calling']}  •  Věk: {hero['age']}  •  Stezka Stínu: {hero['shadow']}"
        c.drawString(M, H-18*mm, info)
        self.txtr(W-M, H-10*mm, f"Hráč: {hero['player']}", 'DVCB', 9, colors.white)
        return H - hh - 3*mm

    def page_num(self, n):
        self.txtc(W/2, 5*mm, f"— {n} —", 'DVC', 6, MID)


def draw_page1(s, hero, pn):
    """Attributes, skills, combat."""
    y = s.header(hero)

    # ATTRIBUTES
    attr_h = 37*mm
    attr_w = 62*mm
    s.box(M, y-attr_h, attr_w, attr_h, "VLASTNOSTI")
    ay = y - attr_h + 2*mm
    col_w = attr_w / 3
    for i, (name, val, tn) in enumerate(hero['attrs']):
        cx = M + i*col_w + col_w/2
        s.txtc(cx, ay+17*mm, name, 'DVCB', 8, DARK)
        s.c.setFont('DVB', 22)
        s.c.setFillColor(ACCENT)
        s.c.drawCentredString(cx, ay+5*mm, str(val))
        s.txtc(cx, ay+1*mm, f"CČ {tn}", 'DVC', 7, MID)

    # DERIVED
    der_x = M + attr_w + 3*mm
    der_w = CW - attr_w - 3*mm
    s.box(der_x, y-attr_h, der_w, attr_h, "ODVOZENÉ HODNOTY")
    dy = y - attr_h + 2*mm
    derived = hero['derived']
    rh = 4.5*mm
    for i, (label, val) in enumerate(derived):
        ry = dy + (len(derived)-1-i)*rh
        s.txt(der_x+2*mm, ry+1*mm, label, 'DVC', 7)
        s.txtr(der_x+der_w-3*mm, ry+1*mm, str(val), 'DVB', 9, ACCENT)
        if i < len(derived)-1:
            s.hline(der_x+2*mm, ry, der_x+der_w-2*mm)

    y -= attr_h + 3*mm

    # SKILLS — 3 columns
    skill_h = 84*mm
    s.box(M, y-skill_h, CW, skill_h, "DOVEDNOSTI")
    sy = y - 11*mm
    scw = CW / 3
    for gi, (group_name, skills) in enumerate(hero['skill_groups']):
        col_x = M + gi * scw
        s.txt(col_x+2*mm, sy+1*mm, group_name, 'DVCB', 7, ACCENT)
        for si, (name, rating, fav) in enumerate(skills):
            row_y = sy - (si+1)*4.2*mm
            s.skill_row(col_x+1*mm, row_y, scw-2*mm, name, rating, fav)

    y -= skill_h + 3*mm

    # COMBAT + WEAPONS side by side
    combat_h = 32*mm
    combat_w = 50*mm
    s.box(M, y-combat_h, combat_w, combat_h, "BOJOVÉ ZDATNOSTI")
    cy = y - combat_h + 2*mm
    for i, (name, rating) in enumerate(hero['combat']):
        ry = cy + (len(hero['combat'])-1-i)*6*mm
        s.txt(M+3*mm, ry+2*mm, name, 'DVC', 7)
        s.dots(M+35*mm, ry+3*mm, rating, max_dots=4)

    weap_x = M + combat_w + 3*mm
    weap_w = CW - combat_w - 3*mm
    s.box(weap_x, y-combat_h, weap_w, combat_h, "ZBRANĚ & ZBROJ")
    wy = y - combat_h + 2*mm
    for i, line in enumerate(hero['weapons']):
        ry = wy + (len(hero['weapons'])-1-i)*5*mm
        s.txt(weap_x+2*mm, ry+1.5*mm, line, 'DVC', 6.5)

    y -= combat_h + 3*mm

    # EQUIPMENT + KEYWORDS side by side
    equip_h = 32*mm
    half = CW/2 - 1*mm

    s.box(M, y-equip_h, half, equip_h, "UŽITEČNÉ PŘEDMĚTY")
    ey = y - equip_h + 2*mm
    for i, line in enumerate(hero['items']):
        s.txt(M+3*mm, ey+(len(hero['items'])-1-i)*4.5*mm+1*mm, line, 'DVC', 6.5)

    kx = M + half + 2*mm
    s.box(kx, y-equip_h, half, equip_h, "KLÍČOVÁ SLOVA & PŘEDMĚTY")
    ky = y - equip_h + 2*mm
    for i, line in enumerate(hero['keywords']):
        s.txt(kx+2*mm, ky+(len(hero['keywords'])-1-i)*4.5*mm+1*mm, line, 'DVC', 6)

    y -= equip_h + 3*mm

    # RELATIONSHIPS
    remaining = y - M - 2*mm
    if remaining > 8*mm:
        s.box(M, M, CW, remaining, "VZTAHY & POZNÁMKY")
        ny = y - 10*mm
        for i, line in enumerate(hero['notes']):
            if ny - i*4.5*mm < M+2*mm:
                break
            s.txt(M+3*mm, ny-i*4.5*mm, line, 'DVC', 6.5)

    s.page_num(pn)


def draw_page2(s, hero, pn):
    """XP spending + virtues reference."""
    y = s.header(hero)

    # XP EARNED
    box_h = 30*mm
    s.box(M, y-box_h, CW, box_h, "BODY ZKUŠENOSTÍ — ZÍSKÁNO")
    ey = y - 12*mm
    for i, line in enumerate(hero['xp_earned']):
        s.txt(M+3*mm, ey-i*4.5*mm, line, 'DVC', 7)

    y -= box_h + 3*mm

    # COST TABLES side by side
    table_h = 42*mm
    half = CW/2 - 1*mm

    s.box(M, y-table_h, half, table_h, "CENY DOVEDNOSTÍ (Dovednostní body)")
    ty = y - 13*mm
    sp_rows = [
        ("Z — na ●", "1 bod"),
        ("Z ● na ●●", "2 body"),
        ("Z ●● na ●●●", "3 body"),
        ("Z ●●● na ●●●●", "5 bodů"),
    ]
    for i, (desc, cost) in enumerate(sp_rows):
        ry = ty - i*5.5*mm
        s.txt(M+3*mm, ry, desc, 'DVC', 7)
        s.txtr(M+half-3*mm, ry, cost, 'DVB', 7, ACCENT)
        s.hline(M+2*mm, ry-1.5*mm, M+half-2*mm)
    s.txt(M+3*mm, ty-4*5.5*mm-1*mm, "Max 1 stupeň za dovednost za fázi!", 'DVCB', 6.5, ACCENT)

    ap_x = M + half + 2*mm
    s.box(ap_x, y-table_h, half, table_h, "CENY ZDATNOSTÍ / UDATNOST / MOUDROST (Dobrodruž. body)")
    ty2 = y - 13*mm
    ap_rows = [
        ("Boj. zdatnost — → ●", "2 body"),
        ("Boj. zdatnost ● → ●●", "4 body"),
        ("Boj. zdatnost ●● → ●●●", "6 bodů"),
        ("Nový stupeň UDATNOSTI", "→ Odměna"),
        ("Nový stupeň MOUDROSTI", "→ Ctnost"),
    ]
    for i, (desc, cost) in enumerate(ap_rows):
        ry = ty2 - i*5*mm
        s.txt(ap_x+3*mm, ry, desc, 'DVC', 6.5)
        s.txtr(ap_x+half-3*mm, ry, cost, 'DVB', 6.5, ACCENT)
        s.hline(ap_x+2*mm, ry-1.5*mm, ap_x+half-2*mm)
    s.txt(ap_x+3*mm, ty2-5*5*mm, "Buď Udatnost NEBO Moudrost za fázi!", 'DVCB', 6.5, ACCENT)

    y -= table_h + 3*mm

    # RECOMMENDATIONS
    rec_h = 34*mm
    s.box(M, y-rec_h, CW, rec_h, f"DOPORUČENÍ — {hero['name']}")
    ry = y - 13*mm
    s.txt(M+3*mm, ry, f"Celkem dovednostních bodů: {hero['total_sp']}  |  Celkem dobrodružných bodů: {hero['total_ap']}", 'DVB', 8, ACCENT)
    ry -= 6*mm
    s.txt(M+3*mm, ry, "Doporučené utracení dovednostních bodů:", 'DVCB', 7)
    for i, rec in enumerate(hero['sp_recs']):
        s.txt(M+6*mm, ry-(i+1)*4.5*mm, f"• {rec}", 'DVC', 7)
    rx = M + CW/2
    s.txt(rx, ry, "Doporučené utracení dobrodružných bodů:", 'DVCB', 7)
    for i, rec in enumerate(hero['ap_recs']):
        s.txt(rx+3*mm, ry-(i+1)*4.5*mm, f"• {rec}", 'DVC', 7)

    y -= rec_h + 3*mm

    # HOBBIT VIRTUES
    remaining = y - M
    if remaining > 10*mm:
        s.box(M, M, CW, remaining, "HOBITÍ CTNOSTI (dostupné při Moudrost 2)")
        vy = y - 11*mm
        virtues = [
            ("Houževnatý jako kořen stromu", "Lepší hody na Zranění, dvojnásobná SÍLA při odpočinku"),
            ("Malý človíček", "+2 Odrážení proti větším tvorům, snazší střelecký postoj"),
            ("Přesná muška", "Příznivé útoky na dálku, hozené kameny probodávají"),
            ("Tři dělají společnost", "+1 Sounáležitost, druhý cíl Sounáležitosti"),
            ("Umění zmizet", "Hod na Nenápadnost → zmizíš"),
            ("V nouzi hrdinou", "Inspirace, dokud jsi zraněný/sklíčený/vyčerpaný"),
        ]
        for i, (cz, desc) in enumerate(virtues):
            if vy-i*5*mm < M+2*mm:
                break
            s.txt(M+3*mm, vy-i*5*mm, f"• {cz}", 'DVCB', 7)
            s.txt(M+55*mm, vy-i*5*mm, desc, 'DVCI', 6, MID)

    s.page_num(pn)


def draw_story_pages(s, hero, pn_start):
    """Pages 3-4: Character story, wrapped text."""
    # Page 3
    y = s.header(hero)
    y -= 2*mm

    s.box(M, M, CW, y-M, "PŘÍBĚH POSTAVY")
    ty = y - 11*mm
    line_h = 4.2*mm

    story_lines = []
    for para in hero['story']:
        if para == '':
            story_lines.append('')
        else:
            wrapped = simpleSplit(para, 'DVC', 7.5, CW-8*mm)
            story_lines.extend(wrapped)
            story_lines.append('')  # paragraph break

    page_lines_drawn = 0
    i = 0
    while i < len(story_lines) and ty > M + 3*mm:
        line = story_lines[i]
        if line == '':
            ty -= 2*mm
        else:
            s.txt(M+3*mm, ty, line, 'DVC', 7.5)
            ty -= line_h
        i += 1
        page_lines_drawn += 1

    s.page_num(pn_start)

    # Page 4 — overflow if needed
    if i < len(story_lines):
        s.c.showPage()
        y = s.header(hero)
        y -= 2*mm
        s.box(M, M, CW, y-M, "PŘÍBĚH POSTAVY (pokračování)")
        ty = y - 11*mm

        while i < len(story_lines) and ty > M + 3*mm:
            line = story_lines[i]
            if line == '':
                ty -= 2*mm
            else:
                s.txt(M+3*mm, ty, line, 'DVC', 7.5)
                ty -= line_h
            i += 1

        s.page_num(pn_start + 1)
    else:
        # If story fits on one page, make page 4 a notes/blank page
        s.c.showPage()
        y = s.header(hero)
        y -= 2*mm
        s.box(M, M, CW, y-M, "POZNÁMKY")
        # Draw some lined paper effect
        ty = y - 12*mm
        while ty > M + 5*mm:
            s.hline(M+3*mm, ty, M+CW-3*mm, colors.HexColor('#E8DDD0'), 0.3)
            ty -= 7*mm
        s.page_num(pn_start + 1)


# ===================== HERO DATA =====================

sedrik = {
    'name': 'Sedrik Dobromysl',
    'player': 'Sedrik (7)',
    'culture': 'Hobbit z Hůrecka',
    'calling': 'Posel',
    'age': '14–15',
    'shadow': 'Cestovní horečka',
    'attrs': [
        ('SÍLA', 3, 17),
        ('SRDCE', 6, 14),
        ('DŮVTIP', 5, 15),
    ],
    'derived': [
        ('Výdrž', '23'),
        ('Naděje', '16'),
        ('Odrážení', '15'),
        ('Udatnost / Moudrost', '1 / 1'),
        ('Stín', '2'),
        ('Zátěž', '0'),
    ],
    'skill_groups': [
        ('SÍLA  CČ 17', [
            ('Působivost', 0, False),
            ('Mrštnost', 1, False),
            ('Ostražitost', 1, False),
            ('Lov', 1, False),
            ('Hudba', 2, False),
            ('Řemesla', 0, False),
        ]),
        ('SRDCE  CČ 14', [
            ('Povzbuzování', 2, True),
            ('Cestování', 1, False),
            ('Vhled', 2, True),
            ('Léčení', 1, False),
            ('Dvornost', 2, False),
            ('Válečnictví', 0, False),
        ]),
        ('DŮVTIP  CČ 15', [
            ('Přesvědčování', 2, False),
            ('Nenápadnost', 1, False),
            ('Všímavost', 1, False),
            ('Průzkum', 0, False),
            ('Hádanky', 1, False),
            ('Učenost', 2, False),
        ]),
    ],
    'combat': [
        ('Rvačka', 1),
        ('Meče', 0),
        ('Luky', 0),
    ],
    'weapons': [
        'Krátký nůž — Poškoz. 2, Nebezp. 14, Zátěž 0',
        'Hůlka (obušek) — Poškoz. 3, Nebezp. 12, Zátěž 0',
        'Prak — Poškoz. 1, střelná, Zátěž 0',
        'Zbroj: žádná',
    ],
    'items': [
        'Píšťalka na ptáky → HUDBA +1k',
        'Kniha příběhů → UČENOST +1k',
    ],
    'keywords': [
        '„Hodní chlapci" — +1k DVORNOST s hobity z Kraje',
        'Stará mapa (Ep 1) — záhadné značky',
        'Ametystový přívěsek (Ep 2, pokud získán)',
    ],
    'notes': [
        'Cíl Sounáležitosti: Geralt Rychlonožka',
        'Požehnání: Hobití smysl — hody na MOUDROST příznivé, +1k proti Chamtivosti',
        'Osobité rysy: Zvídavý, Upřímný',
        'Role: hlas družiny, vyjednávání, znalosti, morálka, empatie',
        'Patron: Gilraen',
    ],
    'xp_earned': [
        'Ep 1 — Tajemství statku Pytlíků (~1 sezení): 3 dovednostních + 3 dobrodružných bodů',
        'Ep 2 — Duch z Jehličné (~2 sezení): 6 dovednostních + 6 dobrodružných bodů',
        'CELKEM: 9 dovednostních bodů + 9 dobrodružných bodů',
    ],
    'total_sp': 9, 'total_ap': 9,
    'sp_recs': [
        'Povzbuzování 2→3 (3 body)',
        'Dvornost 2→3 (3 body)',
        'Hudba 2→3 (3 body)',
    ],
    'ap_recs': [
        'Moudrost 1→2 (~8 bodů) → ctnost',
        'Zbude 1 bod na příště',
    ],
    'story': [
        'Sedrik vyrostl v zadním pokoji otcova bylinkářského krámku na okraji Hůrky, obklopený svazky sušeného kostivalu a příběhy. Jeho otec obchodoval s bylinkami po celém Hůrecku — až ke Gwynethině chatě u Chrastového lesa — a malý Sedrik chodil s ním, víc poslouchal než nosil. Brzy se naučil dvě věci: že rostliny mají jména a účely, a že lidé vám řeknou cokoli, pokud umíte naslouchat.',

        'Když záhada na statku Pytlíků ze Sáčkova vtáhla jeho a Geralta do prvního skutečného dobrodružství (Ep 1), Sedrik zjistil, že má dar — ne pro boj nebo šplhání, ale pro řeč. Byl to on, kdo pokládal správné otázky. V Duchu z Jehličné (Ep 2) to byl on, kdo dokázal promluvit k Mňoukalovi se soucitem místo násilí, a kdo utěšil truchlícího Mudrocha Pelíška.',

        'Je mu čtrnáct, je malý i na hobita, a statečnější, než sám tuší.',

        'Jeho otec by nejraději viděl, kdyby převzal bylinkářský krám. Ale Sedrik nemůže — ne po tom, co viděl v Jehličné, ne po tom, co slyšel v hlase Mňoukala. Na světě je víc bolesti, než se vejde do jednoho hobitího krámku, a Sedrik ví, že ji dokáže zmírnit. Neví jak. Ale ví, že musí.',

        'Jeho kniha příběhů — opotřebovaný svazek pohádek a legend, který dostal od otce — je pro něj víc než užitečný předmět. Je to připomínka, že příběhy mají smysl. Že hrdinové v nich nejsou jen postavy, ale lidé, kteří se rozhodli udělat správnou věc. Jako on.',

        'S Geraltem se spřátelil tak, jak to umějí jen děti — okamžitě a úplně. Geralt je ten odvážný, ten, kdo se první podívá přes zeď. Sedrik je ten, kdo ví, co říct lidem na druhé straně.',
    ],
}

geralt = {
    'name': 'Geralt Rychlonožka',
    'player': 'Geralt (10)',
    'culture': 'Hobbit z Hůrecka',
    'calling': 'Hledač pokladů',
    'age': '14–15',
    'shadow': 'Dračí nemoc',
    'attrs': [
        ('SÍLA', 3, 17),
        ('SRDCE', 5, 15),
        ('DŮVTIP', 6, 14),
    ],
    'derived': [
        ('Výdrž', '23'),
        ('Naděje', '15'),
        ('Odrážení', '16'),
        ('Udatnost / Moudrost', '1 / 1'),
        ('Stín', '2'),
        ('Zátěž', '0'),
    ],
    'skill_groups': [
        ('SÍLA  CČ 17', [
            ('Působivost', 0, False),
            ('Mrštnost', 2, True),
            ('Ostražitost', 1, False),
            ('Lov', 2, False),
            ('Hudba', 0, False),
            ('Řemesla', 0, False),
        ]),
        ('SRDCE  CČ 15', [
            ('Povzbuzování', 0, False),
            ('Cestování', 2, False),
            ('Vhled', 1, False),
            ('Léčení', 0, False),
            ('Dvornost', 1, False),
            ('Válečnictví', 1, False),
        ]),
        ('DŮVTIP  CČ 14', [
            ('Přesvědčování', 0, False),
            ('Nenápadnost', 2, False),
            ('Všímavost', 2, True),
            ('Průzkum', 2, False),
            ('Hádanky', 1, False),
            ('Učenost', 1, False),
        ]),
    ],
    'combat': [
        ('Rvačka', 1),
        ('Meče', 0),
        ('Luky', 0),
    ],
    'weapons': [
        'Krátký nůž — Poškoz. 2, Nebezp. 14, Zátěž 0',
        'Hůl — Poškoz. 3, Nebezp. 12, Zátěž 0',
        'Prak — Poškoz. 1, střelná, Zátěž 0',
        'Zbroj: žádná',
    ],
    'items': [
        'Lano (15 yardů) → MRŠTNOST +1k',
        'Lucerna → VŠÍMAVOST +1k',
    ],
    'keywords': [
        '„Hodní chlapci" — +1k DVORNOST s hobity z Kraje',
        'Stará mapa (Ep 1) — nese ji; záhadné značky',
        'Medové koláčky (Ep 2, 0–3 zbývají)',
    ],
    'notes': [
        'Cíl Sounáležitosti: Sedrik Dobromysl',
        'Požehnání: Hobití smysl — hody na MOUDROST příznivé, +1k proti Chamtivosti',
        'Osobité rysy: Odvážný, Rychlý',
        'Role: průzkumník, stopař, šplhač, hledání skrytých věcí',
        'Patron: Gilraen — „Jaro přijde, ať jsme připraveni nebo ne."',
    ],
    'xp_earned': [
        'Ep 1 — Tajemství statku Pytlíků (~1 sezení): 3 dovednostních + 3 dobrodružných bodů',
        'Ep 2 — Duch z Jehličné (~2 sezení): 6 dovednostních + 6 dobrodružných bodů',
        'CELKEM: 9 dovednostních bodů + 9 dobrodružných bodů',
    ],
    'total_sp': 9, 'total_ap': 9,
    'sp_recs': [
        'Všímavost 2→3 (3 body)',
        'Průzkum 2→3 (3 body)',
        'Nenápadnost 2→3 (3 body)',
    ],
    'ap_recs': [
        'Moudrost 1→2 (~8 bodů) → ctnost',
        'Zbude 1 bod na příště',
    ],
    'story': [
        'Geralt je syn obchodníka s koňmi, který jezdí po cestách mezi Hůrkou a Krajem. Tam, kde Sedrik zdědil slova, Geralt zdědil pohyb — šplhá po zdech, proplétá se živými ploty a dokáže najít ztracenou minci v kupce sena. Jeho otec chtěl, aby se učil řemeslu, ale Geralt trávil víc času prozkoumáváním polí jižně od Hůrky než péčí o poníky.',

        'Se Sedrikem se spřátelil tak, jak to umějí jen děti — okamžitě a úplně. Geralt je ten odvážný, ten, kdo se podívá přes zeď jako první, kdo brodil Velkým Rašeliništěm s lucernou, zatímco Sedrik navigoval podle zvuku.',

        'Na statku Pytlíků ze Sáčkova (Ep 1) to byl on, kdo našel stopy. V Duchu z Jehličné (Ep 2) vytáhl lidi z bahna a navigoval cestami přes bažinu, které by spolkly méně hbitého hobita.',

        'Nese Starou mapu — *jeho* mapu, jak o ní přemýšlí. Záhadné značky na ní ukazují kamsi na sever, a Geralt chce zjistit, co znamenají.',

        'Neplánuje, neváhá, prostě jde. Svět se děje a Geralt chce být u toho. To je Geraltova životní filosofie.',

        'Mapa je jeho poklad i jeho past. Čím víc se o ní dozvídá, tím víc ji považuje za *svou*. Dračí nemoc — stezka Stínu Hledače pokladů — by z mapy mohla udělat posedlost. *Jeho* mapa, *jeho* objev, *jeho* poklad na konci cesty.',

        'Ale zatím je mu čtrnáct a svět je velký a zajímavý a Geralt chce vidět, co je za dalším kopcem.',
    ],
}

borek = {
    'name': 'Borek Hbitoprstý',
    'player': 'Timur (13)',
    'culture': 'Hobbit z Hůrecka',
    'calling': 'Ochránce',
    'age': '19',
    'shadow': 'Stezka zoufalství',
    'attrs': [
        ('SÍLA', 6, 14),
        ('SRDCE', 3, 17),
        ('DŮVTIP', 5, 15),
    ],
    'derived': [
        ('Výdrž', '26'),
        ('Naděje', '13'),
        ('Odrážení', '15'),
        ('Udatnost / Moudrost', '1 / 1'),
        ('Stín', '0'),
        ('Zátěž', '3'),
    ],
    'skill_groups': [
        ('SÍLA  CČ 14', [
            ('Působivost', 1, False),
            ('Mrštnost', 2, True),
            ('Ostražitost', 2, True),
            ('Lov', 2, False),
            ('Hudba', 0, False),
            ('Řemesla', 3, False),
        ]),
        ('SRDCE  CČ 17', [
            ('Povzbuzování', 0, False),
            ('Cestování', 1, False),
            ('Vhled', 1, False),
            ('Léčení', 2, False),
            ('Dvornost', 1, False),
            ('Válečnictví', 1, False),
        ]),
        ('DŮVTIP  CČ 15', [
            ('Přesvědčování', 0, False),
            ('Nenápadnost', 2, False),
            ('Všímavost', 2, False),
            ('Průzkum', 2, False),
            ('Hádanky', 1, False),
            ('Učenost', 1, False),
        ]),
    ],
    'combat': [
        ('Rvačka', 1),
    ],
    'weapons': [
        'Prak — Poškoz. 1, střelná, Zátěž 0',
        'Pastýřská hůl — Poškoz. 3, Nebezp. 12, Zátěž 0',
        'Krátký nůž — Poškoz. 2, Nebezp. 14, Zátěž 0',
        'Kožená košile — Ochrana 1k, Zátěž 3',
    ],
    'items': [
        'Sada nástrojů → ŘEMESLA +1k',
        'Bylinkářská brašna → LÉČENÍ +1k',
    ],
    'keywords': [
        'Šedá šála Hraničáře (Iorethova)',
        'Dutý kámen — zpráva v Tengwaru',
        'Vstupuje v Ep 3 §8',
    ],
    'notes': [
        'Cíl Sounáležitosti: (zvolí po Ep 3)',
        'Požehnání: Hobití smysl — hody na MOUDROST příznivé, +1k proti Chamtivosti',
        'Osobité rysy: Důmyslný, Vytrvalý',
        'Role: hlídač, řemeslník, léčitel, fyzická síla, praktické řešení',
        'Patron: Gilraen',
        'Stará Meg: tajná spojenkyně Hraničářů, Borek jí pomáhá od 14 let',
    ],
    'xp_earned': [
        'Ep 3 — Hádankářova mapa (~1 sezení, vstupuje v §8): 3 dovednostních + 3 dobrodružných bodů',
        'CELKEM: 3 dovednostní body + 3 dobrodružné body',
        '(Borek je nový — první fáze společenstva bude po Ep 3)',
    ],
    'total_sp': 3, 'total_ap': 3,
    'sp_recs': [
        'Léčení 2→3 (3 body) — lékař družiny',
        'Nebo: Ostražitost 2→3 (3 body)',
    ],
    'ap_recs': [
        'Šetřit na Moudrost 2',
        'Nebo: Rvačka 1→2 (4 body, ještě nemá dost)',
    ],
    'story': [
        'Borek je syn Donnamíra Hbitoprstého, koláře z Kopečné ulice v Hůrce. Jeho matka Kopretina potichu skrývá spáleniny na stropě kuchyně. Borek zdědil otcovy šikovné prsty, ale ne jeho trpělivost — místo oprav vozů vynalézá věci. Protizávažovou past na krtky. Větruvzdornou lucernu. Šňůrkový mlýnek na koření. Některé fungují krásně. Některé vybuchnou. Většina obojí.',

        'Od čtrnácti let ho otec posílá pomáhat Staré Meg do Staddle — „pomoz staré paní, platí uzeným." Meg provozuje stáj a zásobovací stanici na východním okraji Staddle, poslední budovu, než cesta stoupá ke Komárovým mokřinám.',

        'Co nikdo nahlas neříká, je to, že Meg už desítky let tajně slouží Hraničářům. Dutý zprávonosný kámen u brány. Šedoplášťníci, kteří přicházejí v noci a mizí před úsvitem. Borek to všechno vidí — řezné rány v jejich kůži, bláto z míst, kam žádný obchodník nejezdí.',

        'Jednou v noci, když mu bylo patnáct, se Borek podíval z okna Megina seníku a uviděl muže v kápi, jak stojí na kopci a pozoruje tmu, zatímco celá vesnice spala. Hraničář tam stál celou noc. Ráno byl pryč, žádné stopy ve sněhu. Od té noci chtěl Borek být jako oni. Ne Hraničář — ví, že je hobit. Ale někdo, kdo hlídá, opravuje, drží věci pohromadě.',

        'Tři dny před Ep 3 našel Borek v dutém kameni zprávu psanou Tengwarem, které plně nerozuměl. Poznal jedno slovo, které ho Meg naučila: *gor* — nebezpečí. Tři ovce zmizely z obecních pastvin ve Staddle — žádné kosti, žádní vlci.',

        'To ho přivedlo k padlému milníku na Zelené cestě, kde tříprsté stopy rozbily kámen. Tam potkal dva mladé hobity na cestě — jeden rychle mluvil o značkách na mapě, druhý prohlížel živé ploty lucernou.',

        '„Jste malí na to, abyste tady chodili potmě," řekl Borek. Než došli ke Gwynethině chatě, nesl Borek Sedrikův batoh.',

        'Nosí šedou šálu, příliš dlouhou na hobita, dvakrát omotanou kolem krku, na okrajích roztřepenou. Patří Iorethovi — jednomu ze dvou pohřešovaných Hraničářů, které má družina najít.',

        'Pro Timura: „Sedrik mluví. Geralt prozkoumává. Ty držíš všechno pohromadě. Jsi nejstarší, nejsilnější, ten, kdo opraví, co se rozbije — včetně svých přátel."',
    ],
}


# ===================== GENERATE =====================

out = "/sessions/nifty-peaceful-wright/Character_Sheets_All_Heroes.pdf"
c = canvas.Canvas(out, pagesize=A4)
s = Sheet(c)

pn = 1
for hero in [sedrik, geralt, borek]:
    draw_page1(s, hero, pn)
    c.showPage()
    pn += 1

    draw_page2(s, hero, pn)
    c.showPage()
    pn += 1

    draw_story_pages(s, hero, pn)
    c.showPage()
    pn += 2

c.save()
print(f"PDF saved: {out}")
print(f"Total pages: {pn-1}")
