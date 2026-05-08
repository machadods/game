# C:\Users\wagner62215896\Documents\settings.py

WIDTH = 1280
HEIGHT = 600
FPS = 50
PLAYER_SIZE = 150, 150  # resolução do sprite (qualidade ao zoom in)
ENEMY_SIZE  = 150, 150

# Tamanho da nave em world units (colisão)
# Terra.visual_radius = 127wu. Nave = 10wu → nave = 10/127 = 7.9% do raio de Terra ✓
SHIP_WORLD_UNITS  = 10
ENEMY_WORLD_UNITS = 8

# Tamanho VISUAL em world units — desacoplado da física, só afeta o blit
# Ao zoom=1: nave = SHIP_VISUAL_UNITS*2 px de diâmetro
# SHIP_VISUAL_UNITS=35 → 70px ao zoom=1 (visível e proporcional ao combate)
SHIP_VISUAL_UNITS  = 50
ENEMY_VISUAL_UNITS = 34

# Sistema orbital
TIME_SCALE    = 300    # planetas praticamente imóveis
ORBITAL_SCALE = 40000  # 1 AU = 40 000 world units
PLANET_SIZE_BOOST = 8  # fator visual — mesma constante do iauniverse

# ── Fonte: iauniverse/universe/core/worldState.js ─────────────────────────────
# a_km  = semi-eixo real em km  →  AU = a_km / 149_600_000
# r_km  = raio real em km (iauniverse usa r em Mm: r_Mm * 1000 = r_km)
# color = hex exato do iauniverse (convertido para RGB)
# visual_r = r_km / 5  →  Earth≈1274 wu, Moon≈347 wu, Jupiter≈13900→cap 12000
# "parent" = orbita outro corpo (Moon → Terra)
ORBITAL_DATA = {
    # nome            a_km            AU       period   ecc     r_km    color (RGB do iauniverse)  parent
    "Mercurium":  {"a_km":  57_900_000, "period": 88,    "ecc": 0.205, "r_km":  2_440, "color": (170,170,170)},
    "Venus Nova": {"a_km": 108_200_000, "period": 225,   "ecc": 0.006, "r_km":  6_052, "color": (217,179,140)},
    "Terra":      {"a_km": 149_600_000, "period": 365,   "ecc": 0.0167,"r_km":  6_371, "color": ( 43,108,255)},
    "Moon":       {"a_km":     384_400, "period": 27.3,  "ecc": 0.055, "r_km":  1_737, "color": (180,180,190), "parent": "Terra"},
    "Marte":      {"a_km": 227_900_000, "period": 687,   "ecc": 0.093, "r_km":  3_390, "color": (255, 85, 51)},
    "Ceres":      {"a_km": 413_700_000, "period": 1680,  "ecc": 0.075, "r_km":    473, "color": (150,140,130)},
    "Jupiter":    {"a_km": 778_500_000, "period": 4333,  "ecc": 0.048, "r_km": 69_911, "color": (255,170,102)},
    "Saturno":    {"a_km":1_433_000_000,"period": 10759, "ecc": 0.056, "r_km": 58_232, "color": (255,200,120)},
    "Netuno":     {"a_km":4_495_000_000,"period": 60190, "ecc": 0.009, "r_km": 24_622, "color": ( 74,127,255)},

    # ── Urano — planeta + pai das suas luas ──────────────────────────────────
    "Urano":     {"a_km": 2_872_500_000, "period": 30_687, "ecc": 0.0457, "r_km": 25_362, "color": (147, 211, 207)},

    # ── Luas de Marte ─────────────────────────────────────────────────────────
    "Phobos":    {"a_km":      9_377, "period":   0.319, "ecc": 0.0151,  "r_km":    11, "color": (140, 110,  90), "parent": "Marte"},
    "Deimos":    {"a_km":     23_460, "period":   1.263, "ecc": 0.00027, "r_km":     6, "color": (130, 105,  85), "parent": "Marte"},

    # ── Luas de Saturno (novas — Titã já existe) ──────────────────────────────
    "Mimas":     {"a_km":    185_540, "period":   0.942, "ecc": 0.0196,  "r_km":   198, "color": (200, 195, 185), "parent": "Saturno"},
    "Encélado":  {"a_km":    238_020, "period":   1.370, "ecc": 0.0047,  "r_km":   252, "color": (240, 240, 235), "parent": "Saturno"},
    "Tétis":     {"a_km":    294_660, "period":   1.888, "ecc": 0.0001,  "r_km":   533, "color": (210, 205, 195), "parent": "Saturno"},
    "Dione":     {"a_km":    377_400, "period":   2.737, "ecc": 0.0022,  "r_km":   561, "color": (190, 180, 170), "parent": "Saturno"},
    "Reia":      {"a_km":    527_040, "period":   4.518, "ecc": 0.0010,  "r_km":   764, "color": (170, 160, 150), "parent": "Saturno"},
    "Hipérion":  {"a_km":  1_481_000, "period":  21.276, "ecc": 0.0232,  "r_km":   135, "color": (180, 145, 105), "parent": "Saturno"},
    "Jápeto":    {"a_km":  3_560_800, "period":  79.330, "ecc": 0.0283,  "r_km":   734, "color": ( 90,  80,  70), "parent": "Saturno"},
    "Febe":      {"a_km": 12_955_000, "period": 550.310, "ecc": 0.1635,  "r_km":   107, "color": ( 60,  55,  50), "parent": "Saturno"},

    # ── Luas de Urano ─────────────────────────────────────────────────────────
    "Miranda":   {"a_km":    129_390, "period":   1.413, "ecc": 0.0013,  "r_km":   235, "color": (155, 150, 145), "parent": "Urano"},
    "Ariel":     {"a_km":    191_020, "period":   2.520, "ecc": 0.0012,  "r_km":   579, "color": (180, 170, 160), "parent": "Urano"},
    "Umbriel":   {"a_km":    266_300, "period":   4.144, "ecc": 0.0039,  "r_km":   585, "color": ( 90,  85,  80), "parent": "Urano"},
    "Titânia":   {"a_km":    435_910, "period":   8.706, "ecc": 0.0011,  "r_km":   788, "color": (130, 120, 110), "parent": "Urano"},
    "Oberon":    {"a_km":    583_520, "period":  13.463, "ecc": 0.0014,  "r_km":   761, "color": (105,  95,  85), "parent": "Urano"},

    # ── Luas de Netuno ────────────────────────────────────────────────────────
    "Tritão":    {"a_km":    354_759, "period":   5.877, "ecc": 0.000016, "r_km": 1_353, "color": (200, 180, 160), "parent": "Netuno"},
    "Nereida":   {"a_km":  5_513_400, "period": 360.130, "ecc": 0.7507,  "r_km":   170, "color": (110, 105, 100), "parent": "Netuno"},

    # ── Lua de Plutão ─────────────────────────────────────────────────────────
    "Caronte":   {"a_km":     19_570, "period":   6.387, "ecc": 0.0022,  "r_km":   606, "color": (140, 125, 115), "parent": "Plutão"},

    # ── Planetas Anões (novos — Ceres já existe) ──────────────────────────────
    "Haumea":    {"a_km": 6_452_000_000, "period": 103_410, "ecc": 0.1944, "r_km":   780, "color": (200, 195, 185)},
    "Makemake":  {"a_km": 6_847_000_000, "period": 111_867, "ecc": 0.1587, "r_km":   715, "color": (180, 130,  90)},
    # Sedna real: 506 AU → ajustado 27.1 AU; apélio = 4050M×1.844 ≈ 7468M km ≈ 1996k wu ≤ 2M
    "Sedna":     {"a_km": 4_050_000_000, "period":  51_600, "ecc": 0.8439, "r_km":   498, "color": (190,  80,  70)},

    # ── Asteroides (Cinturão Principal) ───────────────────────────────────────
    "Vesta":     {"a_km":   353_360_000, "period":  1_325, "ecc": 0.0889, "r_km":   262, "color": (170, 145, 115)},
    "Pallas":    {"a_km":   414_710_000, "period":  1_686, "ecc": 0.2300, "r_km":   256, "color": (100,  95,  90)},
    "Juno":      {"a_km":   399_400_000, "period":  1_592, "ecc": 0.2557, "r_km":   117, "color": (160, 140, 105)},
    "Hygiea":    {"a_km":   469_700_000, "period":  2_034, "ecc": 0.1146, "r_km":   217, "color": ( 75,  70,  65)},
    "Psyche":    {"a_km":   437_100_000, "period":  1_823, "ecc": 0.1397, "r_km":   113, "color": (150, 130, 110)},
    "Eros":      {"a_km":   218_000_000, "period":    643, "ecc": 0.2226, "r_km":     8, "color": (155, 130, 105)},
    "Itokawa":   {"a_km":   198_000_000, "period":    556, "ecc": 0.2801, "r_km":     1, "color": (135, 115,  95)},

    # ── TNOs do Cinturão de Kuiper ────────────────────────────────────────────
    "Quaoar":    {"a_km": 6_535_000_000, "period": 105_120, "ecc": 0.0392, "r_km":   555, "color": (150, 105,  75)},
    "Orcus":     {"a_km": 5_891_000_000, "period":  90_625, "ecc": 0.2273, "r_km":   458, "color": (140, 130, 120)},

    # ── Cometas ───────────────────────────────────────────────────────────────
    # Halley: afélio = 2684M×1.967 ≈ 5280M km ≈ 1412k wu ✓
    "Halley":    {"a_km": 2_684_000_000, "period":  27_759, "ecc": 0.967, "r_km":    5, "color": ( 50,  45,  40)},
    # Hale-Bopp: real 186 AU → reduzido 23.4 AU; afélio ≈ 6985M km ≈ 1868k wu ✓
    "Hale-Bopp": {"a_km": 3_500_000_000, "period":  41_350, "ecc": 0.995, "r_km":   30, "color": ( 90,  85,  80)},
    "Encke":     {"a_km":   330_000_000, "period":   1_206, "ecc": 0.848, "r_km":    2, "color": ( 60,  55,  50)},

    # ── Enxames / Regiões ─────────────────────────────────────────────────────
    "Troianos L4":   {"a_km": 778_500_000,   "period":  4_333, "ecc": 0.048, "r_km": 0, "color": (140, 120, 100)},
    "Troianos L5":   {"a_km": 778_500_000,   "period":  4_333, "ecc": 0.048, "r_km": 0, "color": (130, 115,  95)},
    "Belt Principal": {"a_km": 374_000_000,  "period":  1_485, "ecc": 0.0,   "r_km": 0, "color": (120, 105,  90)},
    # Belt Kuiper: 45 AU → 1799k wu; afélio com ecc 0.05 = 1888k wu ✓
    "Belt Kuiper":   {"a_km": 6_730_000_000, "period": 110_409, "ecc": 0.05, "r_km": 0, "color": ( 90,  80, 100)},

    # ── Luas de Júpiter (Galileanas) ──────────────────────────────────────────
    # a_km = distância a Júpiter; wiring em main.py substitui semi_major_axis pelo
    # equivalente visual (parent.visual_radius * N) para que fiquem jogáveis.
    "Io":        {"a_km":   421_700, "period":  1.769, "ecc": 0.0040, "r_km": 1_822, "color": (220,140, 40), "parent": "Jupiter"},
    "Europa":    {"a_km":   670_900, "period":  3.551, "ecc": 0.0090, "r_km": 1_561, "color": (180,190,200), "parent": "Jupiter"},
    "Ganimedes": {"a_km": 1_070_400, "period":  7.155, "ecc": 0.0013, "r_km": 2_634, "color": (160,150,140), "parent": "Jupiter"},
    "Calisto":   {"a_km": 1_882_000, "period": 16.689, "ecc": 0.0074, "r_km": 2_410, "color": (100, 95, 90), "parent": "Jupiter"},

    # ── Lua de Saturno ───────────────────────────────────────────────────────
    "Titã":      {"a_km": 1_222_000, "period": 15.945, "ecc": 0.0288, "r_km": 2_575, "color": (200,160,100), "parent": "Saturno"},

    # ── Planetas Anões ───────────────────────────────────────────────────────
    # Plutão: 39.5 AU → ~1 579 000 wu (dentro do limite de 2 M)
    "Plutão":    {"a_km": 5_906_400_000, "period":  90_520, "ecc": 0.2488, "r_km": 1_188, "color": (180,130,100)},
    # Éris real ≈ 67.8 AU (> 2 M wu). Reduzido para 49.3 AU → ~1 973 000 wu ≤ 2 M.
    "Éris":      {"a_km": 7_375_930_000, "period": 203_500, "ecc": 0.4417, "r_km": 1_163, "color": (190,180,170)},
}

# Constante auxiliar — distância Terra→Sol em km (âncora de escala)
EARTH_ORBIT_KM = 149_600_000

# ── Sol — iauniverse/solarRenderer.js linha 11 ───────────────────────────────
# SUN_RADIUS = 696_340 km  →  world units = 696340 / EARTH_ORBIT_KM * ORBITAL_SCALE
# = 696340 / 149600000 * 20000 ≈ 93 wu  (minúsculo — boosted para visual)
# Usamos PLANET_SIZE_BOOST_2D implícito via visual: Terra=1274wu, Sol=109*Terra≈12000wu
SUN_COLOR_INNER = (255, 187,  51)   # #ffbb33 — iauniverse solarRenderer.js l.136
SUN_COLOR_OUTER = (255, 190,  80)   # rgba(255,190,80) — iauniverse l.133