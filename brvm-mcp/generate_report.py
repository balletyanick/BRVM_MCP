"""
Rapport d'analyse BRVM — Perspectives fin 2026
Source : MCP brvm-server | Date : 9 mai 2026
"""

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUTPUT = r"c:\Users\Yanick\Desktop\BRVM\Analyse_BRVM_Perspectives_2026.docx"

# ── DONNÉES (MCP brvm-server — 9 mai 2026) ───────────────────────────────────
STOCKS = [
    {"ticker": "PRSC",  "cours": 3695,  "var_jour": "0,00%",  "rsi": 16.57, "beta": 0.97,  "var_1m": -26.03, "var_1y": 71.86,  "vol_xof": 3388315,   "val_mrd": 37.8},
    {"ticker": "SVOC",  "cours": 2395,  "var_jour": "0,00%",  "rsi": 20.70, "beta": 0.00,  "var_1m":   0.00, "var_1y":  0.00,  "vol_xof": 0,          "val_mrd": 2.0},
    {"ticker": "BNBC",  "cours": 1300,  "var_jour": "-2,62%", "rsi": 24.32, "beta": 1.22,  "var_1m": -20.06, "var_1y": 27.50,  "vol_xof": 11506300,   "val_mrd": 8.6},
    {"ticker": "SAFC",  "cours": 3500,  "var_jour": "0,00%",  "rsi": 27.57, "beta": 3.84,  "var_1m": -50.04, "var_1y": 451.18, "vol_xof": 10314500,   "val_mrd": 28.4},
    {"ticker": "ORGT",  "cours": 2550,  "var_jour": "-7,44%", "rsi": 27.92, "beta": 0.45,  "var_1m": -30.14, "var_1y": 59.38,  "vol_xof": 39417900,   "val_mrd": 177.0},
    {"ticker": "CFAC",  "cours": 1380,  "var_jour": "-1,43%", "rsi": 35.65, "beta": 2.38,  "var_1m": -15.60, "var_1y": 130.00, "vol_xof": 3255420,    "val_mrd": 250.3},
    {"ticker": "SEMC",  "cours": 1525,  "var_jour": "0,00%",  "rsi": 35.72, "beta": 1.92,  "var_1m": -20.57, "var_1y": 117.86, "vol_xof": 6830475,    "val_mrd": 38.4},
    {"ticker": "UNXC",  "cours": 1805,  "var_jour": "-0,55%", "rsi": 36.60, "beta": 2.37,  "var_1m":  -8.84, "var_1y": 237.38, "vol_xof": 13634970,   "val_mrd": 37.5},
    {"ticker": "ABJC",  "cours": 2975,  "var_jour": "-1,49%", "rsi": 38.37, "beta": 1.06,  "var_1m": -13.01, "var_1y": 82.52,  "vol_xof": 5628700,    "val_mrd": 32.5},
    {"ticker": "SHEC",  "cours": 1940,  "var_jour": "+2,37%", "rsi": 39.14, "beta": 1.30,  "var_1m": -11.42, "var_1y": 110.87, "vol_xof": 7597040,    "val_mrd": 122.2},
    {"ticker": "NTLC",  "cours": 11650, "var_jour": "-0,43%", "rsi": 39.78, "beta": 1.01,  "var_1m":  -5.28, "var_1y": 16.73,  "vol_xof": 10333550,   "val_mrd": 257.1},
    {"ticker": "CABC",  "cours": 3400,  "var_jour": "0,00%",  "rsi": 40.59, "beta": 0.29,  "var_1m": -17.45, "var_1y": 163.16, "vol_xof": 0,          "val_mrd": 20.1},
    {"ticker": "SOGC",  "cours": 7390,  "var_jour": "-0,14%", "rsi": 40.64, "beta": 0.81,  "var_1m":  -6.15, "var_1y": 15.37,  "vol_xof": 0,          "val_mrd": 159.6},
    {"ticker": "TTLS",  "cours": 2950,  "var_jour": "-1,67%", "rsi": 41.13, "beta": 0.16,  "var_1m": -12.46, "var_1y": 20.41,  "vol_xof": 6251050,    "val_mrd": 96.1},
    {"ticker": "BOABF", "cours": 5430,  "var_jour": "+0,56%", "rsi": 43.67, "beta": 0.51,  "var_1m":  -3.89, "var_1y": 67.08,  "vol_xof": 6695190,    "val_mrd": 238.9},
    {"ticker": "BICB",  "cours": 5225,  "var_jour": "+2,05%", "rsi": 43.83, "beta": 0.00,  "var_1m":   3.72, "var_1y": -0.93,  "vol_xof": 19990850,   "val_mrd": 301.8},
    {"ticker": "FTSC",  "cours": 2210,  "var_jour": "+0,45%", "rsi": 45.48, "beta": 0.81,  "var_1m":  -2.60, "var_1y": -30.39, "vol_xof": 1858610,    "val_mrd": 31.2},
    {"ticker": "STAC",  "cours": 2705,  "var_jour": "-4,92%", "rsi": 46.17, "beta": 3.34,  "var_1m": -25.38, "var_1y": 350.83, "vol_xof": 7311615,    "val_mrd": 36.4},
    {"ticker": "TTLC",  "cours": 2750,  "var_jour": "+1,10%", "rsi": 46.53, "beta": -0.09, "var_1m":   3.77, "var_1y":  5.77,  "vol_xof": 13565750,   "val_mrd": 173.1},
    {"ticker": "SPHC",  "cours": 7050,  "var_jour": "-0,70%", "rsi": 46.97, "beta": 1.04,  "var_1m":   0.07, "var_1y": 28.65,  "vol_xof": 3680100,    "val_mrd": 180.2},
    {"ticker": "UNLC",  "cours": 56000, "var_jour": "-5,08%", "rsi": 47.21, "beta": 3.09,  "var_1m": -13.85, "var_1y": 422.88, "vol_xof": 784000,     "val_mrd": 514.3},
    {"ticker": "BOAC",  "cours": 8700,  "var_jour": "+0,58%", "rsi": 47.84, "beta": 0.36,  "var_1m":   3.63, "var_1y": 42.74,  "vol_xof": 73906500,   "val_mrd": 348.0},
    {"ticker": "ORAC",  "cours": 15000, "var_jour": "+0,67%", "rsi": 48.32, "beta": 0.70,  "var_1m":  -1.32, "var_1y":  0.00,  "vol_xof": 4950000,    "val_mrd": 2259.8},
    {"ticker": "NSBC",  "cours": 14100, "var_jour": "+0,71%", "rsi": 48.40, "beta": 1.09,  "var_1m":  -1.36, "var_1y": 66.86,  "vol_xof": 11435100,   "val_mrd": 348.8},
    {"ticker": "SDSC",  "cours": 1745,  "var_jour": "-3,06%", "rsi": 48.70, "beta": 1.40,  "var_1m": -10.79, "var_1y": 20.21,  "vol_xof": 191035620,  "val_mrd": 95.0},
    {"ticker": "SGBC",  "cours": 33895, "var_jour": "+0,28%", "rsi": 48.80, "beta": 1.59,  "var_1m":  -0.31, "var_1y": 55.16,  "vol_xof": 38708090,   "val_mrd": 1054.5},
    {"ticker": "SLBC",  "cours": 38000, "var_jour": "+1,33%", "rsi": 48.82, "beta": 2.34,  "var_1m":   0.00, "var_1y": 162.07, "vol_xof": 4104000,    "val_mrd": 625.5},
    {"ticker": "PALC",  "cours": 7800,  "var_jour": "-1,27%", "rsi": 48.94, "beta": 0.94,  "var_1m":  -5.00, "var_1y": 21.62,  "vol_xof": 10904400,   "val_mrd": 120.6},
    {"ticker": "ONTBF", "cours": 2760,  "var_jour": "-0,54%", "rsi": 49.02, "beta": 0.27,  "var_1m":  -5.26, "var_1y": 11.11,  "vol_xof": 1716720,    "val_mrd": 187.7},
    {"ticker": "ETIT",  "cours": 30,    "var_jour": "0,00%",  "rsi": 49.60, "beta": 1.81,  "var_1m": -11.76, "var_1y": 87.50,  "vol_xof": 15377670,   "val_mrd": 542.5},
    {"ticker": "SMBC",  "cours": 12000, "var_jour": "+0,84%", "rsi": 52.32, "beta": 1.57,  "var_1m":   0.84, "var_1y": 50.00,  "vol_xof": 15816000,   "val_mrd": 93.5},
    {"ticker": "ECOC",  "cours": 16800, "var_jour": "+3,07%", "rsi": 52.90, "beta": 0.53,  "var_1m":   2.75, "var_1y": 69.70,  "vol_xof": 13524000,   "val_mrd": 924.9},
    {"ticker": "SIVC",  "cours": 2800,  "var_jour": "-1,75%", "rsi": 53.62, "beta": 0.16,  "var_1m":  -4.60, "var_1y": 418.52, "vol_xof": 5667200,    "val_mrd": 24.5},
    {"ticker": "STBC",  "cours": 21300, "var_jour": "+1,43%", "rsi": 54.57, "beta": 1.06,  "var_1m":  -0.47, "var_1y": 124.09, "vol_xof": 56956200,   "val_mrd": 382.4},
    {"ticker": "BOAM",  "cours": 4700,  "var_jour": "+0,21%", "rsi": 54.90, "beta": 0.03,  "var_1m":   2.29, "var_1y": 84.31,  "vol_xof": 14819100,   "val_mrd": 129.0},
    {"ticker": "LNBB",  "cours": 3800,  "var_jour": "-3,68%", "rsi": 55.90, "beta": -0.02, "var_1m":  -1.79, "var_1y": -19.73, "vol_xof": 21979200,   "val_mrd": 76.0},
    {"ticker": "SNTS",  "cours": 28900, "var_jour": "0,00%",  "rsi": 56.36, "beta": 0.75,  "var_1m":  -0.34, "var_1y":  9.06,  "vol_xof": 0,          "val_mrd": 2890.0},
    {"ticker": "SIBC",  "cours": 7100,  "var_jour": "-0,70%", "rsi": 56.40, "beta": 0.65,  "var_1m":   1.50, "var_1y": 51.06,  "vol_xof": 27278200,   "val_mrd": 710.0},
    {"ticker": "BICC",  "cours": 25650, "var_jour": "+1,79%", "rsi": 58.32, "beta": 1.02,  "var_1m":   8.66, "var_1y": 61.32,  "vol_xof": 26522100,   "val_mrd": 427.5},
    {"ticker": "SICC",  "cours": 4290,  "var_jour": "-0,23%", "rsi": 58.61, "beta": 0.55,  "var_1m":  13.94, "var_1y": 38.39,  "vol_xof": 429000,     "val_mrd": 2.6},
    {"ticker": "CIEC",  "cours": 3320,  "var_jour": "-0,75%", "rsi": 58.65, "beta": 1.17,  "var_1m":  -0.90, "var_1y": 44.98,  "vol_xof": 14853680,   "val_mrd": 185.9},
    {"ticker": "BOAN",  "cours": 3485,  "var_jour": "-0,43%", "rsi": 61.51, "beta": 0.49,  "var_1m":  24.02, "var_1y": 35.34,  "vol_xof": 33225990,   "val_mrd": 72.5},
    {"ticker": "NEIC",  "cours": 1745,  "var_jour": "0,00%",  "rsi": 63.18, "beta": 1.00,  "var_1m":  26.45, "var_1y": 200.86, "vol_xof": 10353085,   "val_mrd": 22.3},
    {"ticker": "CBIBF", "cours": 16800, "var_jour": "+1,20%", "rsi": 63.72, "beta": 0.68,  "var_1m":  12.00, "var_1y": 71.43,  "vol_xof": 15724800,   "val_mrd": 537.6},
    {"ticker": "SDCC",  "cours": 9095,  "var_jour": "+2,19%", "rsi": 69.09, "beta": 1.15,  "var_1m":  21.27, "var_1y": 48.37,  "vol_xof": 5147770,    "val_mrd": 81.9},
    {"ticker": "SCRC",  "cours": 2405,  "var_jour": "+7,37%", "rsi": 74.41, "beta": 1.28,  "var_1m":  26.58, "var_1y": 142.93, "vol_xof": 28568995,   "val_mrd": 47.1},
    {"ticker": "BOAS",  "cours": 7395,  "var_jour": "+1,79%", "rsi": 76.60, "beta": 0.72,  "var_1m":   8.82, "var_1y": 76.19,  "vol_xof": 29846220,   "val_mrd": 266.2},
    {"ticker": "BOAB",  "cours": 9345,  "var_jour": "+0,48%", "rsi": 83.32, "beta": 0.14,  "var_1m":  22.96, "var_1y": 95.71,  "vol_xof": 58714635,   "val_mrd": 379.0},
]

MARKET = {
    "date": "9 mai 2026",
    "hausse": 20, "baisse": 20, "stable": 8,
    "rsi_moyen": 48.49,
    "top5_hausse": [("SCRC", "+7,37%", 2405), ("ECOC", "+3,07%", 16800),
                    ("SHEC", "+2,37%", 1940), ("SDCC", "+2,19%", 9095), ("BICB", "+2,05%", 5225)],
    "top5_baisse": [("ORGT", "-7,44%", 2550), ("UNLC", "-5,08%", 56000),
                    ("STAC", "-4,92%", 2705), ("LNBB", "-3,68%", 3800), ("SDSC", "-3,06%", 1745)],
}


# ── HELPERS ──────────────────────────────────────────────────────────────────

def cell_bg(cell, color_hex):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color_hex.lstrip("#"))
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    tcPr.append(shd)


def rgb(hex_str):
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def add_cell(cell, text, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT,
             font_size=9, color=None, bg=None, italic=False):
    if bg:
        cell_bg(cell, bg)
    p = cell.paragraphs[0]
    p.alignment = align
    run = p.add_run(str(text))
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(font_size)
    if color:
        run.font.color.rgb = rgb(color)


def signal_info(rsi, vol_xof):
    illiq = (vol_xof or 0) < 1_500_000
    if rsi < 30:
        sig, col = "ACHAT FORT", "1E7E1E"
    elif rsi < 40:
        sig, col = "ACHAT", "28A745"
    elif rsi < 50:
        sig, col = "NEUTRE", "5A6268"
    elif rsi < 60:
        sig, col = "NEUTRE +", "2980B9"
    elif rsi < 70:
        sig, col = "PRUDENCE", "E67E22"
    else:
        sig, col = "VENTE", "C0392B"
    if illiq:
        sig += " *"
    return sig, col


def analyse_technique(s):
    rsi, v1m, v1y, beta = s["rsi"], s["var_1m"], s["var_1y"], s["beta"]
    lines = []

    if rsi < 25:
        lines.append(f"RSI en zone de survente extreme ({rsi:.1f}) — correction violente, rebond technique probable mais incertitude elevee.")
    elif rsi < 35:
        lines.append(f"RSI en survente ({rsi:.1f}) — la pression baissiere s'epuise, signal de retournement possible.")
    elif rsi < 45:
        lines.append(f"RSI ({rsi:.1f}) — zone neutre baissiere, momentum negatif modere.")
    elif rsi < 55:
        lines.append(f"RSI neutre ({rsi:.1f}) — equilibre acheteurs/vendeurs, pas de direction claire.")
    elif rsi < 65:
        lines.append(f"RSI ({rsi:.1f}) — momentum haussier modere, acheteurs aux commandes.")
    elif rsi < 75:
        lines.append(f"RSI eleve ({rsi:.1f}) — zone de surchauffe, prise de benefices a surveiller.")
    else:
        lines.append(f"RSI tres eleve ({rsi:.1f}) — titre surach ete, risque de correction technique imminent.")

    if v1m < -40:
        lines.append(f"Forte correction de {v1m:.1f}% sur 1 mois — mouvement excessif, rebond possible.")
    elif v1m < -20:
        lines.append(f"Correction significative de {v1m:.1f}% sur 1 mois.")
    elif v1m < -10:
        lines.append(f"Repli de {v1m:.1f}% sur 1 mois — consolidation en cours.")
    elif v1m < 0:
        lines.append(f"Legere baisse de {v1m:.1f}% sur 1 mois.")
    elif v1m < 10:
        lines.append(f"Legere hausse de +{v1m:.1f}% sur 1 mois — momentum positif naissant.")
    elif v1m < 25:
        lines.append(f"Bonne performance de +{v1m:.1f}% sur 1 mois.")
    else:
        lines.append(f"Forte progression de +{v1m:.1f}% sur 1 mois — momentum puissant.")

    if v1y < -20:
        lines.append(f"Tendance annuelle negative ({v1y:.1f}%) — titre en declin structurel.")
    elif v1y < 0:
        lines.append(f"Legere baisse annuelle ({v1y:.1f}%) — pression vendeuse persistante sur l'annee.")
    elif v1y < 30:
        lines.append(f"Performance annuelle modeste (+{v1y:.1f}%).")
    elif v1y < 80:
        lines.append(f"Bonne performance annuelle (+{v1y:.1f}%) — tendance haussiere etablie.")
    elif v1y < 200:
        lines.append(f"Tres forte performance annuelle (+{v1y:.1f}%) — titre en forte expansion.")
    else:
        lines.append(f"Performance annuelle exceptionnelle (+{v1y:.1f}%) — mouvement hors-norme.")

    if beta == 0:
        lines.append("Beta non disponible.")
    elif abs(beta) < 0.2:
        lines.append(f"Beta ({beta:.2f}) — titre quasi-independant du marche BRVM, mouvement propre.")
    elif abs(beta) < 0.7:
        lines.append(f"Beta faible ({beta:.2f}) — profil defensif, peu sensible aux mouvements du marche.")
    elif abs(beta) < 1.3:
        lines.append(f"Beta proche du marche ({beta:.2f}) — volatilite standard.")
    elif abs(beta) < 2.0:
        lines.append(f"Beta eleve ({beta:.2f}) — titre plus volatil que le marche BRVM.")
    else:
        lines.append(f"Beta tres eleve ({beta:.2f}) — titre tres speculatif, mouvements amplifies des 2 cotes.")

    return lines


def perspectives(s):
    rsi, v1m, v1y, cours = s["rsi"], s["var_1m"], s["var_1y"], s["cours"]

    if rsi < 35 and v1y > 40:
        bp, mp, bp2 = 1.40, 1.18, 0.82
        bt = "Rebond vers les sommets anterieurs si la tendance annuelle se confirme."
        mt = "Reprise progressive apres la correction — consolidation saine."
        bt2 = "Poursuite de la baisse si le support cle ne tient pas."
    elif rsi < 35 and v1y <= 0:
        bp, mp, bp2 = 1.20, 0.97, 0.75
        bt = "Rebond technique possible, potentiel limite sans catalyseur."
        mt = "Stabilisation autour des niveaux actuels."
        bt2 = "Continuation de la tendance baissiere annuelle."
    elif rsi > 75:
        bp, mp, bp2 = 1.12, 0.87, 0.70
        bt = "Poursuite exceptionnelle du momentum (scenario rare)."
        mt = "Correction puis stabilisation — retour a la moyenne."
        bt2 = "Correction forte attendue apres epuisement du momentum."
    elif rsi > 65:
        bp, mp, bp2 = 1.18, 0.92, 0.78
        bt = "Poursuite si catalyseur fondamental se maintient."
        mt = "Legere correction puis consolidation dans une fourchette haute."
        bt2 = "Correction vers les supports — retour a RSI neutre."
    elif v1y > 200:
        bp, mp, bp2 = 1.30, 1.08, 0.72
        bt = "Continuation du mouvement exceptionnel si fondamentaux solides."
        mt = "Consolidation apres un mouvement historique."
        bt2 = "Prise de benefices massive — retour partiel vers la base."
    elif v1y < -15:
        bp, mp, bp2 = 1.18, 0.98, 0.80
        bt = "Retournement haussier avec catalyseur (resultats, contrat)."
        mt = "Stabilisation sans reprise significative."
        bt2 = "Poursuite du declin annuel — nouveau point bas."
    else:
        bp, mp, bp2 = 1.22, 1.08, 0.88
        bt = "Progression dans la continuite de la tendance haussiere."
        mt = "Progression moderee et reguliere d'ici fin 2026."
        bt2 = "Correction vers les supports si marche BRVM se retourne."

    def rnd(p):
        return int(cours * p / 5) * 5

    return [
        ("HAUSSIER", f"{rnd(bp):,} XOF", bt, "D5F5E3"),
        ("BASE",     f"{rnd(mp):,} XOF", mt, "EBF5FB"),
        ("BAISSIER", f"{rnd(bp2):,} XOF", bt2, "FADBD8"),
    ]


# ── DOCUMENT ─────────────────────────────────────────────────────────────────

def build():
    doc = Document()

    # Page setup A4
    sec = doc.sections[0]
    sec.page_width  = Cm(21)
    sec.page_height = Cm(29.7)
    sec.left_margin = sec.right_margin = Cm(1.8)
    sec.top_margin  = sec.bottom_margin = Cm(1.8)

    # ── PAGE DE TITRE ─────────────────────────────────────────────────────────
    for _ in range(4):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ANALYSE DU MARCHE BRVM")
    r.bold = True
    r.font.size = Pt(28)
    r.font.color.rgb = rgb("1A5276")

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("Perspectives & Recommandations — Fin 2026")
    r2.font.size = Pt(16)
    r2.font.color.rgb = rgb("2C3E50")
    r2.italic = True

    doc.add_paragraph()

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.add_run(f"Date d'analyse : {MARKET['date']}").font.size = Pt(11)

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p4.add_run("Source : MCP brvm-server  |  github.com/Fredysessie/brvm-data-public")
    r4.font.size = Pt(9)
    r4.italic = True
    r4.font.color.rgb = rgb("7F8C8D")

    doc.add_paragraph()
    p5 = doc.add_paragraph()
    p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r5 = p5.add_run("* Titre peu liquide (volume < 1,5 M XOF/jour) — signal a confirmer")
    r5.font.size = Pt(9)
    r5.font.color.rgb = rgb("E74C3C")

    doc.add_page_break()

    # ── VUE D'ENSEMBLE DU MARCHE ──────────────────────────────────────────────
    h1 = doc.add_heading("1. Vue d'ensemble du marche BRVM", level=1)

    # 4 KPI boxes
    tbl = doc.add_table(rows=1, cols=4)
    tbl.style = "Table Grid"
    kpis = [
        ("20", "Titres en hausse", "1E8449"),
        ("20", "Titres en baisse", "C0392B"),
        ("8",  "Titres stables",  "7F8C8D"),
        ("48.49", "RSI moyen marche", "1A5276"),
    ]
    for i, (val, label, col) in enumerate(kpis):
        c = tbl.rows[0].cells[i]
        cell_bg(c, col)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(f"{val}\n{label}")
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = rgb("FFFFFF")

    doc.add_paragraph()

    # Top movers side by side
    def movers_table(title, data, up=True):
        doc.add_paragraph().add_run(title).bold = True
        t = doc.add_table(rows=1, cols=3)
        t.style = "Table Grid"
        hdr_col = "1E8449" if up else "C0392B"
        for i, h in enumerate(["Ticker", "Variation", "Cours (XOF)"]):
            cell_bg(t.rows[0].cells[i], hdr_col)
            add_cell(t.rows[0].cells[i], h, bold=True, color="FFFFFF",
                     align=WD_ALIGN_PARAGRAPH.CENTER)
        for ticker, var, cours in data:
            row = t.add_row()
            row.cells[0].paragraphs[0].add_run(ticker).bold = True
            bg = "D5F5E3" if up else "FADBD8"
            text_col = "1E8449" if up else "C0392B"
            cell_bg(row.cells[1], bg)
            add_cell(row.cells[1], var, color=text_col, align=WD_ALIGN_PARAGRAPH.CENTER)
            add_cell(row.cells[2], f"{cours:,}", align=WD_ALIGN_PARAGRAPH.RIGHT)

    movers_table("Top 5 Hausses du jour", MARKET["top5_hausse"], up=True)
    doc.add_paragraph()
    movers_table("Top 5 Baisses du jour", MARKET["top5_baisse"], up=False)

    doc.add_page_break()

    # ── TABLEAU RECAPITULATIF ─────────────────────────────────────────────────
    doc.add_heading("2. Tableau recapitulatif — 48 actions BRVM", level=1)

    cols = ["Ticker", "Cours (XOF)", "Var. Jour", "RSI", "Var. 1M", "Var. 1 An", "Cap. Mrd XOF", "SIGNAL"]
    ts = doc.add_table(rows=1, cols=len(cols))
    ts.style = "Table Grid"
    for i, h in enumerate(cols):
        cell_bg(ts.rows[0].cells[i], "1A5276")
        add_cell(ts.rows[0].cells[i], h, bold=True, color="FFFFFF",
                 align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8)

    for s in sorted(STOCKS, key=lambda x: x["ticker"]):
        sig, sig_col = signal_info(s["rsi"], s["vol_xof"])
        row = ts.add_row()
        cs = row.cells

        add_cell(cs[0], s["ticker"], bold=True, font_size=9)
        add_cell(cs[1], f"{s['cours']:,}", align=WD_ALIGN_PARAGRAPH.RIGHT, font_size=9)

        vj = s["var_jour"]
        vj_col = "1E8449" if "+" in vj else ("C0392B" if "-" in vj else "5A6268")
        add_cell(cs[2], vj, color=vj_col, align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9)

        add_cell(cs[3], f"{s['rsi']:.1f}", align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9)

        v1m_col = "1E8449" if s["var_1m"] >= 0 else "C0392B"
        add_cell(cs[4], f"{s['var_1m']:+.1f}%", color=v1m_col,
                 align=WD_ALIGN_PARAGRAPH.RIGHT, font_size=9)

        v1y_col = "1E8449" if s["var_1y"] >= 0 else "C0392B"
        add_cell(cs[5], f"{s['var_1y']:+.1f}%", color=v1y_col,
                 align=WD_ALIGN_PARAGRAPH.RIGHT, font_size=9)

        add_cell(cs[6], f"{s['val_mrd']:.1f}", align=WD_ALIGN_PARAGRAPH.RIGHT, font_size=9)

        cell_bg(cs[7], sig_col)
        add_cell(cs[7], sig, bold=True, color="FFFFFF",
                 align=WD_ALIGN_PARAGRAPH.CENTER, font_size=8)

    doc.add_page_break()

    # ── ANALYSES INDIVIDUELLES ────────────────────────────────────────────────
    doc.add_heading("3. Analyses individuelles", level=1)

    for idx, s in enumerate(sorted(STOCKS, key=lambda x: x["rsi"])):
        ticker = s["ticker"]
        sig, sig_col = signal_info(s["rsi"], s["vol_xof"])

        # En-tete ticker
        hdr = doc.add_table(rows=1, cols=2)
        hdr.style = "Table Grid"
        cell_bg(hdr.rows[0].cells[0], "1A5276")
        cell_bg(hdr.rows[0].cells[1], sig_col)
        add_cell(hdr.rows[0].cells[0], f"  {ticker}", bold=True, color="FFFFFF",
                 font_size=13, align=WD_ALIGN_PARAGRAPH.LEFT)
        add_cell(hdr.rows[0].cells[1], sig, bold=True, color="FFFFFF",
                 font_size=11, align=WD_ALIGN_PARAGRAPH.RIGHT)

        # Donnees cles
        dt = doc.add_table(rows=2, cols=5)
        dt.style = "Table Grid"
        vol_str = f"{s['vol_xof']:,.0f} XOF" if s["vol_xof"] else "N/D"
        row1 = [("Cours", f"{s['cours']:,} XOF"), ("Var. Jour", s["var_jour"]),
                ("RSI", f"{s['rsi']:.2f}"), ("Beta 1 an", f"{s['beta']:.2f}"),
                ("Cap.", f"{s['val_mrd']:.1f} Mrd")]
        row2 = [("Var. 1 Mois", f"{s['var_1m']:+.2f}%"), ("Var. 1 An", f"{s['var_1y']:+.2f}%"),
                ("Volume XOF", vol_str), ("Signal", sig), ("", "")]

        for i, (label, val) in enumerate(row1):
            cell_bg(dt.rows[0].cells[i], "D6EAF8")
            dt.rows[0].cells[i].paragraphs[0].add_run(f"{label}: {val}").font.size = Pt(8)
        for i, (label, val) in enumerate(row2):
            cell_bg(dt.rows[1].cells[i], "EBF5FB")
            dt.rows[1].cells[i].paragraphs[0].add_run(f"{label}: {val}" if label else "").font.size = Pt(8)

        # Analyse technique
        doc.add_paragraph()
        p_at = doc.add_paragraph()
        p_at.add_run("Analyse technique").bold = True

        for line in analyse_technique(s):
            bp = doc.add_paragraph(style="List Bullet")
            bp.add_run(line).font.size = Pt(9)

        # Perspectives
        doc.add_paragraph()
        p_pv = doc.add_paragraph()
        p_pv.add_run("Perspectives fin 2026").bold = True

        pt = doc.add_table(rows=3, cols=3)
        pt.style = "Table Grid"
        cell_bg(pt.rows[0].cells[0], "1A5276")
        cell_bg(pt.rows[0].cells[1], "1A5276")
        cell_bg(pt.rows[0].cells[2], "1A5276")
        for i, h in enumerate(["Scenario", "Objectif prix", "Conditions"]):
            add_cell(pt.rows[0].cells[i], h, bold=True, color="FFFFFF",
                     font_size=8, align=WD_ALIGN_PARAGRAPH.CENTER)

        for row_idx, (label, price, cond, bg) in enumerate(perspectives(s)):
            row = pt.add_row()
            cell_bg(row.cells[0], bg)
            cell_bg(row.cells[1], bg)
            cell_bg(row.cells[2], bg)
            add_cell(row.cells[0], label, bold=True, font_size=8, align=WD_ALIGN_PARAGRAPH.CENTER)
            add_cell(row.cells[1], price, bold=True, font_size=8, align=WD_ALIGN_PARAGRAPH.CENTER)
            add_cell(row.cells[2], cond, font_size=8)

        doc.add_paragraph()

        if idx < len(STOCKS) - 1:
            if (idx + 1) % 2 == 0:
                doc.add_page_break()
            else:
                doc.add_paragraph("─" * 90)

    doc.add_page_break()

    # ── CLASSEMENT DES OPPORTUNITES ───────────────────────────────────────────
    doc.add_heading("4. Classement des opportunites", level=1)

    doc.add_heading("Opportunites d'achat (RSI < 40, var. 1 an > 0, liquides)", level=2)
    buys = sorted(
        [s for s in STOCKS if s["rsi"] < 40 and s["var_1y"] > 0 and (s["vol_xof"] or 0) > 2_000_000],
        key=lambda x: x["rsi"]
    )
    bt = doc.add_table(rows=1, cols=5)
    bt.style = "Table Grid"
    for i, h in enumerate(["Ticker", "Cours", "RSI", "Var. 1M", "Var. 1 An"]):
        cell_bg(bt.rows[0].cells[i], "1E8449")
        add_cell(bt.rows[0].cells[i], h, bold=True, color="FFFFFF",
                 align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9)
    for s in buys:
        row = bt.add_row()
        cell_bg(row.cells[0], "D5F5E3")
        row.cells[0].paragraphs[0].add_run(s["ticker"]).bold = True
        row.cells[1].paragraphs[0].add_run(f"{s['cours']:,} XOF").font.size = Pt(9)
        row.cells[2].paragraphs[0].add_run(f"{s['rsi']:.1f}").font.size = Pt(9)
        add_cell(row.cells[3], f"{s['var_1m']:+.1f}%",
                 color="C0392B" if s["var_1m"] < 0 else "1E8449", font_size=9)
        add_cell(row.cells[4], f"{s['var_1y']:+.1f}%", color="1E8449", font_size=9)

    doc.add_paragraph()
    doc.add_heading("Titres surachetes — Prudence (RSI > 65)", level=2)
    sells = sorted([s for s in STOCKS if s["rsi"] > 65], key=lambda x: -x["rsi"])
    st2 = doc.add_table(rows=1, cols=5)
    st2.style = "Table Grid"
    for i, h in enumerate(["Ticker", "Cours", "RSI", "Var. 1M", "Var. 1 An"]):
        cell_bg(st2.rows[0].cells[i], "C0392B")
        add_cell(st2.rows[0].cells[i], h, bold=True, color="FFFFFF",
                 align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9)
    for s in sells:
        row = st2.add_row()
        cell_bg(row.cells[0], "FADBD8")
        row.cells[0].paragraphs[0].add_run(s["ticker"]).bold = True
        row.cells[1].paragraphs[0].add_run(f"{s['cours']:,} XOF").font.size = Pt(9)
        add_cell(row.cells[2], f"{s['rsi']:.1f}", color="C0392B",
                 align=WD_ALIGN_PARAGRAPH.CENTER, font_size=9)
        add_cell(row.cells[3], f"{s['var_1m']:+.1f}%", color="1E8449", font_size=9)
        add_cell(row.cells[4], f"{s['var_1y']:+.1f}%", color="1E8449", font_size=9)

    doc.add_paragraph()

    # Note de bas de page
    note = doc.add_paragraph()
    note.add_run(
        "AVERTISSEMENT : Ce rapport est genere automatiquement a partir de donnees de marche "
        "publiques. Il ne constitue pas un conseil en investissement. Tout investissement comporte "
        "des risques, y compris la perte du capital investi. La BRVM est un marche emergent avec "
        "une liquidite limitee sur de nombreux titres."
    ).italic = True
    note.runs[0].font.size = Pt(8)
    note.runs[0].font.color.rgb = rgb("7F8C8D")

    doc.save(OUTPUT)
    print(f"Rapport sauvegarde : {OUTPUT}")
    print(f"Taille : {__import__('os').path.getsize(OUTPUT) // 1024} Ko")


if __name__ == "__main__":
    build()
