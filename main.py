"""
GAME ZERO
=========
Mundo único — ORBITAL é o espaço real, STRATEGIC é zoom-out do mesmo mundo.

Fluxo:  LOGIN → MENU → ORBITAL ↔ STRATEGIC
Estados extras: GROUND (futuro), GAMEOVER
"""

import pygame
import random
import math
import json
import ctypes
from enum import Enum
from settings import WIDTH, HEIGHT, FPS, TIME_SCALE, SUN_COLOR_INNER, SUN_COLOR_OUTER, SHIP_WORLD_UNITS, ENEMY_WORLD_UNITS, SHIP_VISUAL_UNITS, ENEMY_VISUAL_UNITS

# Diz ao Windows para não escalar o processo — pygame recebe pixels reais da tela pq assim a gente controla o zoom manualmente (câmera) e evita problemas de DPI em telas 4K agora que o universo é expandido para órbitas maiores. Se falhar, o jogo ainda roda, mas pode ter problemas de escala em telas de alta DPI.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
from src.player import Player
from src.coin import Coin
from src.camera import Camera, ZOOM_START
from src.enemy import Enemy
from src.bullet import Bullet
from src.stars import StarField
from src.database import GameDatabase
from src.celestial.planet import Planet, PLANET_TYPES, STRAT_SCALE

# ── Constantes de gameplay ────────────────────────────────────────────────────
UNIVERSE_LIMIT_X  = 2_000_000  # world units (expandido para órbitas maiores)
UNIVERSE_LIMIT_Y  = 2_000_000
SAFE_ZONE_RADIUS  = 18_000    # world units ao redor do Sol — sem horda (fora da superfície solar)
DOBRA_GOLD_COST   = 50
ATMOSPHERE_RATIO  = 1.18      # atmosfera = 1.18x visual_radius do planeta

# Sistema solar fixo — posições em unidades de mundo, inspiradas no Sistema Solar real.
# A Zona Segura (origem) representa o Sol.
SOLAR_SYSTEM = [
    {
        'name': 'Mercurium',
        'planet_type': 'lava_world',
        'x':  11000, 'y':  -4000,   # ~11 700 u
        'difficulty': 1,
    },
    {
        'name': 'Venus Nova',
        'planet_type': 'lava_world',
        'x': -19000, 'y':  13000,   # ~23 000 u
        'difficulty': 3,
    },
    {
        'name': 'Terra',
        'planet_type': 'forest',
        'x':  28000, 'y':   9000,   # ~29 400 u
        'difficulty': 2,
    },
        {
        'name': 'Moon',
        'planet_type': 'ice_world',   # 1800 km — ~1/3 de Terra (real: 1737 km)
        'x':  28100, 'y':   9000,
        'difficulty': 1,
    },
    {
        'name': 'Marte',
        'planet_type': 'terrestrial_iron',
        'x': -36000, 'y': -18000,   # ~40 200 u
        'difficulty': 2,
    },
    {
        'name': 'Ceres',
        'planet_type': 'ice_world',
        'x': 38000, 'y': -19000,   # ~50 100 u
        'difficulty': 1,
    },
    {
        'name': 'Jupiter',
        'planet_type': 'gas_giant',
        'x': -54000, 'y':  32000,   # ~62 700 u
        'difficulty': 4,
    },
    {
        'name': 'Saturno',
        'planet_type': 'gas_giant',
        'x':  58000, 'y': -44000,   # ~72 600 u
        'difficulty': 4,
    },
    {
        'name': 'Netuno',
        'planet_type': 'ice_world',
        'x': -60000, 'y': -52000,   # ~79 400 u
        'difficulty': 5,
    },

    # ── Luas de Júpiter — posições iniciais perto de Júpiter ─────────────────
    # O wiring abaixo sobrescreve x,y com a órbita real ao redor de Júpiter.
    {
        'name': 'Io',
        'planet_type': 'lava_world',
        'x': -54000, 'y': 40000,
        'difficulty': 3,
    },
    {
        'name': 'Europa',
        'planet_type': 'ice_world',
        'x': -41200, 'y': 32000,
        'difficulty': 3,
    },
    {
        'name': 'Ganimedes',
        'planet_type': 'ice_world',
        'x': -54000, 'y': 12000,
        'difficulty': 4,
    },
    {
        'name': 'Calisto',
        'planet_type': 'terrestrial_silicon',
        'x': -84000, 'y': 32000,
        'difficulty': 4,
    },

    # ── Lua de Saturno ────────────────────────────────────────────────────────
    {
        'name': 'Titã',
        'planet_type': 'lava_world',
        'x': 58000, 'y': -26000,
        'difficulty': 4,
    },

    # ── Planetas Anões ────────────────────────────────────────────────────────
    {
        'name': 'Plutão',
        'planet_type': 'ice_world',
        'x': 145000, 'y': -120000,
        'difficulty': 5,
    },
    {
        'name': 'Éris',
        'planet_type': 'ice_world',
        'x': -160000, 'y': 135000,
        'difficulty': 5,
    },

    # ── Urano ──────────────────────────────────────────────────────────────────
    {
        'name': 'Urano',
        'planet_type': 'gas_giant',
        'x': -70000, 'y': 55000,
        'difficulty': 4,
    },

    # ── Luas de Marte (x,y = 0: wiring posiciona) ────────────────────────────
    {'name': 'Phobos',  'planet_type': 'terrestrial_iron',     'x': 0, 'y': 0, 'difficulty': 1},
    {'name': 'Deimos',  'planet_type': 'terrestrial_iron',     'x': 0, 'y': 0, 'difficulty': 1},

    # ── Luas de Saturno ───────────────────────────────────────────────────────
    {'name': 'Mimas',    'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 2},
    {'name': 'Encélado', 'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 2},
    {'name': 'Tétis',    'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 3},
    {'name': 'Dione',    'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 3},
    {'name': 'Reia',     'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 3},
    {'name': 'Hipérion', 'planet_type': 'terrestrial_silicon', 'x': 0, 'y': 0, 'difficulty': 3},
    {'name': 'Jápeto',   'planet_type': 'terrestrial_silicon', 'x': 0, 'y': 0, 'difficulty': 4},
    {'name': 'Febe',     'planet_type': 'terrestrial_silicon', 'x': 0, 'y': 0, 'difficulty': 4},

    # ── Luas de Urano ─────────────────────────────────────────────────────────
    {'name': 'Miranda',  'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 3},
    {'name': 'Ariel',    'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 4},
    {'name': 'Umbriel',  'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 4},
    {'name': 'Titânia',  'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 4},
    {'name': 'Oberon',   'planet_type': 'terrestrial_silicon', 'x': 0, 'y': 0, 'difficulty': 4},

    # ── Luas de Netuno ────────────────────────────────────────────────────────
    {'name': 'Tritão',   'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 5},
    {'name': 'Nereida',  'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 4},

    # ── Lua de Plutão ─────────────────────────────────────────────────────────
    {'name': 'Caronte',  'planet_type': 'ice_world',           'x': 0, 'y': 0, 'difficulty': 5},

    # ── Novos planetas anões ──────────────────────────────────────────────────
    {'name': 'Haumea',   'planet_type': 'ice_world',   'x': -155000, 'y':  120000, 'difficulty': 5},
    {'name': 'Makemake', 'planet_type': 'ice_world',   'x':  165000, 'y': -110000, 'difficulty': 5},
    {'name': 'Sedna',    'planet_type': 'ice_world',   'x':   90000, 'y': -170000, 'difficulty': 5},

    # ── Asteroides (Cinturão Principal) ───────────────────────────────────────
    {'name': 'Vesta',    'planet_type': 'terrestrial_iron',    'x':  22000, 'y':  16000, 'difficulty': 2},
    {'name': 'Pallas',   'planet_type': 'terrestrial_silicon', 'x':  28000, 'y': -19000, 'difficulty': 2},
    {'name': 'Juno',     'planet_type': 'terrestrial_silicon', 'x':  35000, 'y':   9000, 'difficulty': 2},
    {'name': 'Hygiea',   'planet_type': 'terrestrial_silicon', 'x':  41000, 'y': -28000, 'difficulty': 3},
    {'name': 'Psyche',   'planet_type': 'terrestrial_iron',    'x':  37000, 'y':  31000, 'difficulty': 3},
    {'name': 'Eros',     'planet_type': 'terrestrial_iron',    'x':  12000, 'y':   7000, 'difficulty': 1},
    {'name': 'Itokawa',  'planet_type': 'terrestrial_silicon', 'x':  10500, 'y':  -5500, 'difficulty': 1},

    # ── TNOs do Cinturão de Kuiper ────────────────────────────────────────────
    {'name': 'Quaoar',   'planet_type': 'ice_world', 'x':  170000, 'y':   85000, 'difficulty': 5},
    {'name': 'Orcus',    'planet_type': 'ice_world', 'x':  130000, 'y': -145000, 'difficulty': 5},

    # ── Cometas ───────────────────────────────────────────────────────────────
    {'name': 'Halley',    'planet_type': 'comet', 'x':  -85000, 'y':  95000, 'difficulty': 3},
    {'name': 'Hale-Bopp', 'planet_type': 'comet', 'x': -180000, 'y': -90000, 'difficulty': 4},
    {'name': 'Encke',     'planet_type': 'comet', 'x':   30000, 'y':  38000, 'difficulty': 2},

    # ── Enxames / Regiões ─────────────────────────────────────────────────────
    {'name': 'Troianos L4',    'planet_type': 'meteoroid_swarm', 'x':  60000, 'y':  20000, 'difficulty': 4},
    {'name': 'Troianos L5',    'planet_type': 'meteoroid_swarm', 'x':  20000, 'y':  60000, 'difficulty': 4},
    {'name': 'Belt Principal', 'planet_type': 'meteoroid_swarm', 'x':  32000, 'y':      0, 'difficulty': 3},
    {'name': 'Belt Kuiper',    'planet_type': 'meteoroid_swarm', 'x': 175000, 'y':      0, 'difficulty': 5},
]

# ── Estados ───────────────────────────────────────────────────────────────────
class GameState(Enum):
    LOGIN     = 0   # tela de login (estado inicial)
    MENU      = 1   # tela inicial pós-login
    ORBITAL   = 2   # pilotagem no mundo aberto
    STRATEGIC = 3   # mapa zoom-out (pausa)
    GROUND    = 4   # futuro
    GAMEOVER  = 5

# ── Pygame ────────────────────────────────────────────────────────────────────
pygame.init()
screen  = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("GAME ZERO")
clock   = pygame.time.Clock()
running = True

font_large  = pygame.font.SysFont("Arial", 74)
font_medium = pygame.font.SysFont("Arial", 36)
font_small  = pygame.font.SysFont("Arial", 24)

# ── Câmera e fundo ────────────────────────────────────────────────────────────
camera     = Camera(WIDTH, HEIGHT)
star_field = StarField(world_width=160000, world_height=160000, density=0.05)

# ── Grupos de sprites ─────────────────────────────────────────────────────────
players = pygame.sprite.Group()
coins   = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# ── Estado do jogo ────────────────────────────────────────────────────────────
player            = None
score_enemies     = 0
invincible_timer  = 0.0
auto_save_timer   = 0.0
game_initialized  = False
rapid_fire_timer  = 0.0
spawn_protection  = 0.0   # segundos de imunidade no spawn (sem horda)
strat_zoom        = 1.0   # zoom do mapa estratégico (scroll no modo M)
STRAT_SCALE_BASE  = 0.003 # escala base — mesma que STRAT_SCALE em planet.py
landed_planet     = None  # planeta em que o player está pousado (estado GROUND)
landed_angle      = 0.0   # ângulo de abordagem ao pousar (para decolar de volta)

RAPID_FIRE_INTERVAL = 0.08
RAPID_FIRE_MIN_GOLD = 10
POWER_SHOT_GOLD_MIN = 100   # ouro mínimo para dano x2
POWER_SHOT_DRAIN    = 10    # ouro consumido a cada POWER_DRAIN_SHOTS disparos
POWER_DRAIN_SHOTS   = 100

# ── Jogador / Login ───────────────────────────────────────────────────────────
player_db_id      = None
player_username   = ""
player_gold       = 0          # ouro acumulado (moeda da Dobra Temporal)
player_name_input = ""         # campo de texto na tela de login
bullet_shot_counter = 0        # contagem de disparos para consumo de ouro

# ── Planetas e navegação ──────────────────────────────────────────────────────
planets         = []
selected_planet = None
current_planet  = None

# ── UI temporária (mensagens na tela) ─────────────────────────────────────────
ui_message       = ""
ui_message_timer = 0.0
ui_message_color = (255, 220, 60)

_ASTEROID_NAMES = {
    'Vesta', 'Pallas', 'Juno', 'Hygiea', 'Psyche', 'Eros', 'Itokawa',
}

def show_message(text, duration=3.0, color=(255, 220, 60)):
    global ui_message, ui_message_timer, ui_message_color
    ui_message       = text
    ui_message_timer = duration
    ui_message_color = color

# ── Database ──────────────────────────────────────────────────────────────────
db = GameDatabase('game_data.db')

# ── Geração / carregamento de planetas ───────────────────────────────────────
def _seed_planets():
    """Popula o banco com o sistema solar fixo, apagando dados antigos."""
    db.conn.execute("DELETE FROM planets")
    db.conn.commit()
    for entry in SOLAR_SYSTEM:
        pdata = PLANET_TYPES[entry['planet_type']]
        db.create_planet(
            name=entry['name'],
            x=entry['x'],
            y=entry['y'],
            radius_km=pdata['radius_km'],
            planet_type=entry['planet_type'],
            difficulty=entry['difficulty'],
            minerals=pdata['minerals'],
        )
    print(f"[DB] Sistema solar semeado: {len(SOLAR_SYSTEM)} planetas")


planets_db     = db.get_all_planets()
expected_names = {e['name'] for e in SOLAR_SYSTEM}
existing_names = {row['name'] for row in planets_db}

# Re-semeia se nomes ou tamanhos de planeta mudaram
_need_reseed = not planets_db or expected_names != existing_names
if not _need_reseed and planets_db:
    _moon_row  = next((r for r in planets_db if r['name'] == 'Moon'),  None)
    _terra_row = next((r for r in planets_db if r['name'] == 'Terra'), None)
    from src.celestial.planet import PLANET_TYPES as _PT
    if (_moon_row  and _moon_row['radius_km']  != _PT['ice_world']['radius_km'] or
            _terra_row and _terra_row['radius_km'] != _PT['forest']['radius_km']):
        _need_reseed = True
if _need_reseed:
    _seed_planets()
    planets_db = db.get_all_planets()

for row in planets_db:
    minerals = json.loads(row['minerals']) if isinstance(row['minerals'], str) else {}
    p = Planet(id=row['id'], name=row['name'],
               x=row['x'], y=row['y'],
               radius_km=row['radius_km'],
               planet_type=row['planet_type'],
               difficulty=row['difficulty'],
               minerals=minerals)
    # Carrega status de conquista salvo no banco
    if row['conquered']:
        p.conquered = True
    planets.append(p)

print(f"[DB] {len(planets)} planetas carregados")

# Asteroides nomeados não são conquistáveis (cenário)
for _p in planets:
    if _p.name in _ASTEROID_NAMES:
        _p.is_conquerable = False

# ── Wiring de satélites — Moon orbita Terra ───────────────────────────────────
_terra = next((p for p in planets if p.name == 'Terra'), None)
_moon  = next((p for p in planets if p.name == 'Moon'),  None)
if _terra and _moon:
    _moon.parent_body     = _terra
    _moon.period_days     = 27.3
    _moon.eccentricity    = 0.055
    # Moon a 30x diâmetro de Terra (real: 30x) → proporcional e real
    _moon.semi_major_axis = _terra.visual_radius * 6
    _r = _moon.semi_major_axis * (1 - _moon.eccentricity**2) / \
         (1 + _moon.eccentricity * math.cos(_moon.angle))
    _moon.x = _terra.x + _r * math.cos(_moon.angle)
    _moon.y = _terra.y + _r * math.sin(_moon.angle)
    print(f"[ORBIT] Moon → Terra | r=384 400 km (real) | Terra visual_r={_terra.visual_radius} km")

# ── Wiring de satélites — Luas de Júpiter ────────────────────────────────────
# semi_major_axis é substituído por parent.visual_radius * N para escala jogável.
# Proporções relativas mantidas: Io < Europa < Ganimedes < Calisto.
_jupiter = next((p for p in planets if p.name == 'Jupiter'), None)
for _moon_name, _mult in [('Io', 2.0), ('Europa', 3.2), ('Ganimedes', 5.0), ('Calisto', 7.5)]:
    _m = next((p for p in planets if p.name == _moon_name), None)
    if _jupiter and _m:
        _m.parent_body     = _jupiter
        _m.semi_major_axis = _jupiter.visual_radius * _mult
        _r = _m.semi_major_axis * (1 - _m.eccentricity ** 2) / \
             (1 + _m.eccentricity * math.cos(_m.angle))
        _m.x = _jupiter.x + _r * math.cos(_m.angle)
        _m.y = _jupiter.y + _r * math.sin(_m.angle)
        print(f"[ORBIT] {_moon_name} → Jupiter | orbit_r={int(_m.semi_major_axis)} wu ({_mult}x)")

# ── Wiring de satélites — Titã orbita Saturno ────────────────────────────────
_saturno = next((p for p in planets if p.name == 'Saturno'), None)
_tita    = next((p for p in planets if p.name == 'Titã'),    None)
if _saturno and _tita:
    _tita.parent_body     = _saturno
    _tita.semi_major_axis = _saturno.visual_radius * 4.5
    _r = _tita.semi_major_axis * (1 - _tita.eccentricity ** 2) / \
         (1 + _tita.eccentricity * math.cos(_tita.angle))
    _tita.x = _saturno.x + _r * math.cos(_tita.angle)
    _tita.y = _saturno.y + _r * math.sin(_tita.angle)
    print(f"[ORBIT] Titã → Saturno | orbit_r={int(_tita.semi_major_axis)} wu (4.5x)")


def _wire(planets_list, child_name, parent_name, mult):
    """Fia um satélite ao planeta-pai com semi_major_axis = parent.visual_radius * mult."""
    parent = next((p for p in planets_list if p.name == parent_name), None)
    child  = next((p for p in planets_list if p.name == child_name),  None)
    if parent and child:
        child.parent_body     = parent
        child.semi_major_axis = parent.visual_radius * mult
        r = child.semi_major_axis * (1 - child.eccentricity ** 2) / \
            (1 + child.eccentricity * math.cos(child.angle))
        child.x = parent.x + r * math.cos(child.angle)
        child.y = parent.y + r * math.sin(child.angle)
        print(f"[ORBIT] {child_name} → {parent_name} | r={int(child.semi_major_axis)} wu ({mult}x)")


# ── Luas de Marte — Fobos < Deimos ────────────────────────────────────────────
# Marte.visual_radius ≈ 678 wu
_wire(planets, 'Phobos',  'Marte', 2.5)   # ~1 695 wu
_wire(planets, 'Deimos',  'Marte', 4.5)   # ~3 051 wu

# ── Luas de Saturno — ordem real preservada, Titã (4.5x) já está wired ────────
# Saturno.visual_radius ≈ 4 000 wu (capped)
_wire(planets, 'Mimas',    'Saturno', 1.2)   #  ~4 800 wu
_wire(planets, 'Encélado', 'Saturno', 1.6)   #  ~6 400 wu
_wire(planets, 'Tétis',    'Saturno', 2.0)   #  ~8 000 wu
_wire(planets, 'Dione',    'Saturno', 2.6)   # ~10 400 wu
_wire(planets, 'Reia',     'Saturno', 3.5)   # ~14 000 wu
# Titã já wired a 4.5x = ~18 000 wu
_wire(planets, 'Hipérion', 'Saturno', 5.5)   # ~22 000 wu
_wire(planets, 'Jápeto',   'Saturno', 7.5)   # ~30 000 wu
_wire(planets, 'Febe',     'Saturno', 10.0)  # ~40 000 wu

# ── Luas de Urano ─────────────────────────────────────────────────────────────
# Urano.visual_radius ≈ 4 000 wu (capped)
_wire(planets, 'Miranda',  'Urano', 1.5)   #  ~6 000 wu
_wire(planets, 'Ariel',    'Urano', 2.2)   #  ~8 800 wu
_wire(planets, 'Umbriel',  'Urano', 3.0)   # ~12 000 wu
_wire(planets, 'Titânia',  'Urano', 4.5)   # ~18 000 wu
_wire(planets, 'Oberon',   'Urano', 6.0)   # ~24 000 wu

# ── Luas de Netuno ────────────────────────────────────────────────────────────
# Netuno.visual_radius ≈ 4 000 wu (capped)
_wire(planets, 'Tritão',   'Netuno', 3.5)   # ~14 000 wu
_wire(planets, 'Nereida',  'Netuno', 10.0)  # ~40 000 wu  (órbita altamente excêntrica)

# ── Lua de Plutão ─────────────────────────────────────────────────────────────
# Plutão.visual_radius ≈ 237 wu
_wire(planets, 'Caronte',  'Plutão', 8.0)   # ~1 896 wu

# ── Inicialização do mundo ────────────────────────────────────────────────────
def initialize_game():
    global player, score_enemies, invincible_timer
    global game_initialized, current_planet, spawn_protection

    current_planet  = None
    player = Player("player_1")
    players.empty(); players.add(player)

    score_enemies    = 0
    invincible_timer = 0.0
    game_initialized = True
    spawn_protection = 8.0   # 8 s sem horda após spawn

    coins.empty(); enemies.empty(); bullets.empty()

    # Reset das hordas
    for p in planets:
        p.reset_horde()

    # Nasce próximo à Terra
    terra = next((p for p in planets if p.name == 'Terra'), None)
    if terra:
        spawn_ang  = random.uniform(0, 2 * math.pi)
        spawn_dist = terra.visual_radius * 2.5   # spawn fora da activation_range
        spawn_x    = terra.x + math.cos(spawn_ang) * spawn_dist
        spawn_y    = terra.y + math.sin(spawn_ang) * spawn_dist
    else:
        spawn_x, spawn_y = 5000, 0

    player.world_pos   = pygame.math.Vector2(spawn_x, spawn_y)
    player.rect.center = (int(spawn_x), int(spawn_y))

    # Minérios orbitam o planeta — entre 1.5x e 3x o visual_radius
    for p in planets:
        mineral_count = p.difficulty * 20
        for _ in range(mineral_count):
            angle  = random.uniform(0, 2 * math.pi)
            radius = random.uniform(p.visual_radius * 1.2, p.visual_radius * 2.0)
            coins.add(Coin(
                p.x + math.cos(angle) * radius,
                p.y + math.sin(angle) * radius,
                planet=p, angle=angle, radius=radius,
            ))

    show_message("Missão iniciada! Aproxime-se de um planeta para engajar a horda.",
                 5.0, (80, 220, 80))

# ── Dobra Temporal ────────────────────────────────────────────────────────────
def calcular_intercept(planet, player_world_pos, velocidade_dobra=500000):
    """Calcula onde o planeta estará quando a nave chegar (intercept orbital)."""
    dist = math.hypot(planet.x - player_world_pos.x, planet.y - player_world_pos.y)
    if dist < 1:
        dist = 1
    tempo_viagem_s = dist / velocidade_dobra
    dias_jogo = (tempo_viagem_s * TIME_SCALE) / 86400
    futuro_angle = planet.angle + (2 * math.pi / planet.period_days) * dias_jogo
    if planet.semi_major_axis <= 0:
        return planet.x, planet.y
    r = planet.semi_major_axis * (1 - planet.eccentricity ** 2) / \
        (1 + planet.eccentricity * math.cos(futuro_angle))
    return r * math.cos(futuro_angle), r * math.sin(futuro_angle)


def do_dobra_temporal() -> bool:
    """Teletransporta o player para o intercept orbital do planeta selecionado.
    Retorna True se o teleporte foi realizado, False caso contrário."""
    global player_gold

    if not selected_planet:
        show_message("Selecione um planeta no mapa (M) antes da Dobra.", color=(255, 100, 100))
        return False
    if player_gold < DOBRA_GOLD_COST:
        show_message(f"Dobra requer {DOBRA_GOLD_COST} ouro. Voce tem {player_gold}.",
                     color=(255, 100, 100))
        return False

    player_gold -= DOBRA_GOLD_COST

    # Destino: onde o planeta ESTARÁ quando a nave chegar (intercept orbital)
    dest_x, dest_y = calcular_intercept(selected_planet, player.world_pos)
    angle = random.uniform(0, 2 * math.pi)
    dist  = selected_planet.activation_range - 100
    px    = dest_x + math.cos(angle) * dist
    py    = dest_y + math.sin(angle) * dist

    player.world_pos   = pygame.math.Vector2(px, py)
    player.rect.center = (int(px), int(py))

    show_message(f"Dobra Temporal: {selected_planet.name}! (-{DOBRA_GOLD_COST} ouro)",
                 4.0, (100, 200, 255))
    print(f"[DOBRA] Intercept: {selected_planet.name}  |  Ouro restante: {player_gold}")
    return True

# ── Helpers ───────────────────────────────────────────────────────────────────
def clamp_radar(dx, dy, max_r):
    d = math.hypot(dx, dy)
    if d > max_r:
        s = max_r / d
        return dx * s, dy * s
    return dx, dy


def _send_next_invasion_wave(target_planet):
    """Envia 10 tropas do primeiro planeta da fila de invasão do alvo."""
    if not target_planet.invasion_queue:
        return
    source = target_planet.invasion_queue.pop(0)
    target_planet.invasion_active_count = 10

    spawn_r = source.visual_radius + max(200, int(source.visual_radius * 0.2))
    for _ in range(10):
        a  = random.uniform(0, 2 * math.pi)
        ex = source.x + math.cos(a) * spawn_r
        ey = source.y + math.sin(a) * spawn_r
        e = Enemy(ex, ey, bullets, wave=1)
        e.invasion_target   = target_planet
        e.invasion_conquest = target_planet   # tag permanente — persiste após chegada
        enemies.add(e)

    restantes = len(target_planet.invasion_queue)
    show_message(
        f"Invasão de {source.name} → {target_planet.name}!"
        + (f"  ({restantes} na fila)" if restantes else "  (última onda!)"),
        4.0, (255, 120, 40)
    )


def trigger_invasions(conquered_planet):
    """Monta a fila de invasão e envia a primeira onda.
    Cada onda de 10 só parte quando a anterior for completamente eliminada."""
    fontes = [p for p in planets
              if p is not conquered_planet and p.is_conquerable and not p.conquered]
    if not fontes:
        return

    # Ordena do mais próximo ao mais distante do planeta conquistado
    fontes.sort(key=lambda p: math.hypot(p.x - conquered_planet.x,
                                          p.y - conquered_planet.y))
    conquered_planet.invasion_queue        = fontes
    conquered_planet.invasion_active_count = 0
    _send_next_invasion_wave(conquered_planet)

    show_message(
        f"{len(fontes)} planeta(s) preparam invasão de {conquered_planet.name}!",
        6.0, (255, 100, 30)
    )


SOL_WORLD_RADIUS = 12_000   # world units — ~9x Terra (real: 109x), proporcional ao sistema

def draw_safe_zone():
    """Desenha o Sol na origem — posição e escala respeitam o zoom da câmera."""
    sx, sy = camera.world_to_screen(0, 0)

    sol_r  = max(3, int(SOL_WORLD_RADIUS * camera.zoom))
    safe_r = max(2, int(SAFE_ZONE_RADIUS * camera.zoom))
    aura_r = int(sol_r * 1.6)

    # Cull: não desenha se o Sol inteiro estiver fora da tela
    if (sx + aura_r < -200 or sx - aura_r > WIDTH  + 200 or
            sy + aura_r < -200 or sy - aura_r > HEIGHT + 200):
        return

    # Camadas de aura (corona)
    for r_mult, color in [
        (1.6, (35, 20, 0)),
        (1.4, (60, 35, 0)),
        (1.2, (100, 60, 5)),
        (1.1, (160, 100, 10)),
    ]:
        pygame.draw.circle(screen, color, (sx, sy), int(sol_r * r_mult))

    # Corpo do Sol — cores exatas do iauniverse solarRenderer.js
    pygame.draw.circle(screen, SUN_COLOR_OUTER, (sx, sy), sol_r)
    pygame.draw.circle(screen, SUN_COLOR_INNER, (sx, sy), int(sol_r * 0.75))
    pygame.draw.circle(screen, (255, 240, 180), (sx, sy), int(sol_r * 0.45))
    pygame.draw.circle(screen, (255, 255, 240), (sx, sy), int(sol_r * 0.20))

    # Zona segura — borda tênue verde
    pygame.draw.circle(screen, (40, 70, 40), (sx, sy), safe_r, 1)

    # Label quando a tela ainda mostra o centro do Sol
    label_y = sy - aura_r - 14
    if 0 < label_y < HEIGHT:
        font = pygame.font.Font(None, 20)
        txt  = font.render("SOL", True, (255, 220, 80))
        screen.blit(txt, (sx - txt.get_width() // 2, label_y))


def _hud_panel(surface, x, y, w, h, alpha=195):
    """Desenha painel HUD sci-fi com borda cyan e linha de destaque no topo."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 6, 18, alpha))
    pygame.draw.rect(s, (0, 155, 195, 210), (0, 0, w, h), 1, border_radius=4)
    pygame.draw.line(s, (0, 210, 250, 130), (2, 1), (w - 2, 1), 1)
    surface.blit(s, (x, y))


def _draw_heart(surface, cx, cy, size, color):
    """Coração vetorial via curva paramétrica — não depende de fonte emoji."""
    scale = size / 17.0
    pts = []
    for i in range(48):
        t = math.pi * 2 * i / 48
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t)
              - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((int(cx + x * scale), int(cy + y * scale)))
    if len(pts) >= 3:
        pygame.draw.polygon(surface, color, pts)


def draw_hud():
    W, H = screen.get_width(), screen.get_height()
    fnt_m = pygame.font.Font(None, 20)
    fnt_s = pygame.font.Font(None, 17)
    fnt_t = pygame.font.Font(None, 14)

    # ── Vidas (top-left) ──────────────────────────────────────────────────────
    _hud_panel(screen, 8, 8, 170, 58)
    screen.blit(fnt_t.render("VIDAS", True, (0, 200, 240)), (16, 11))
    for i in range(3):
        alive = i < player.lives
        hcx   = 34 + i * 46
        hcy   = 40
        col   = (220, 30, 30) if alive else (50, 14, 14)
        _draw_heart(screen, hcx, hcy, 24, col)

    # ── Stats (top-right) ─────────────────────────────────────────────────────
    bullet_damage = 2 if player_gold >= 100 else 1

    # Altura dinâmica: cresce se tiver planeta ativo e/ou indicador de dano
    panel_h = 112
    if current_planet and current_planet.is_conquerable:
        panel_h += 22
    if bullet_damage > 1:
        panel_h += 18

    panel_w = 300
    px = W - panel_w - 8
    py = 8
    _hud_panel(screen, px, py, panel_w, panel_h)

    row = py + 10

    # Inimigos
    screen.blit(fnt_m.render(f"INIMIGOS: {score_enemies}", True, (255, 65, 65)),
                (px + 10, row))
    row += 22

    # Ouro + badge de dano
    ouro_cor = (255, 215, 0) if player_gold >= DOBRA_GOLD_COST else (150, 105, 0)
    gold_txt = f"OURO: {player_gold}"
    screen.blit(fnt_m.render(gold_txt, True, ouro_cor), (px + 10, row))
    if bullet_damage > 1:
        badge = fnt_t.render(f"DANOx{bullet_damage}", True, (255, 80, 0))
        bx = px + 10 + fnt_m.size(gold_txt)[0] + 8
        pygame.draw.rect(screen, (80, 30, 0), (bx - 2, row, badge.get_width() + 4, 16), border_radius=3)
        screen.blit(badge, (bx, row + 1))
        row += 22
        shots_left = 100 - bullet_shot_counter
        sc_col = (200, 190, 80) if shots_left > 30 else (255, 130, 40)
        screen.blit(fnt_s.render(f"  -{10} ouro em {shots_left} tiros", True, sc_col), (px + 10, row))
    row += 22

    # Tiro rápido
    if player_gold >= RAPID_FIRE_MIN_GOLD:
        rf_ativo = pygame.mouse.get_pressed()[2]
        rf_col   = (0, 255, 220) if rf_ativo else (0, 200, 170)
        rf_txt   = "[MB2] TIRO RAPIDO ativo!" if rf_ativo else "[MB2] TIRO RAPIDO pronto"
    else:
        rf_col = (80, 80, 105)
        rf_txt = f"[MB2] precisa {RAPID_FIRE_MIN_GOLD} ouro"
    screen.blit(fnt_m.render(rf_txt, True, rf_col), (px + 10, row))
    row += 22

    # Planeta ativo (só para conquistáveis)
    if current_planet and current_planet.is_conquerable:
        alive = len(enemies)
        sp, tot = current_planet.horde_spawned, current_planet.horde_total
        if current_planet.conquered:
            def_cor = (80, 255, 80) if current_planet.defenders > 60 else \
                      (255, 200, 50) if current_planet.defenders > 20 else (255, 60, 60)
            screen.blit(fnt_m.render(
                f"{current_planet.name}: DEFENDENDO — {current_planet.defenders} def.", True, def_cor),
                (px + 10, row))
            msg = font_medium.render("CONQUISTADO! — M: mapa", True, (80, 255, 80))
            screen.blit(msg, msg.get_rect(center=(W // 2, H - 55)))
        else:
            cor = (80, 255, 80) if current_planet.horde_done else (255, 165, 45)
            screen.blit(fnt_m.render(f"{current_planet.name}: {alive} ({sp}/{tot})", True, cor),
                        (px + 10, row))
        row += 22

    # Hints (dobra + mapa)
    hint_row = py + panel_h - 19
    dobra_cor = (75, 190, 255) if player_gold >= DOBRA_GOLD_COST else (45, 70, 90)
    screen.blit(fnt_s.render(f"[F] Dobra {DOBRA_GOLD_COST}o   [M] Mapa   [Q] Zoom",
                             True, dobra_cor), (px + 10, hint_row))

    # ── Nome do piloto (bottom-left) ──────────────────────────────────────────
    pilot_w = max(100, len(player_username) * 11 + 24)
    _hud_panel(screen, 8, H - 38, pilot_w, 28, alpha=165)
    screen.blit(font_small.render(player_username, True, (60, 230, 60)), (14, H - 35))

    # ── Waypoint do planeta selecionado ───────────────────────────────────────
    if selected_planet and player:
        rel  = pygame.math.Vector2(selected_planet.x - player.world_pos.x,
                                   selected_planet.y - player.world_pos.y)
        dist = rel.length()
        if dist > selected_planet.visual_radius + 100:
            ang  = math.atan2(rel.y, rel.x)
            ar_x = W // 2 + int(math.cos(ang) * 145)
            ar_y = H // 2 + int(math.sin(ang) * 145)
            pygame.draw.circle(screen, selected_planet.color, (ar_x, ar_y), 9)
            pygame.draw.circle(screen, (255, 255, 255), (ar_x, ar_y), 9, 2)
            ft  = pygame.font.Font(None, 19)
            dtx = ft.render(f"{selected_planet.name}  {int(dist)}u", True, selected_planet.color)
            screen.blit(dtx, (ar_x - dtx.get_width() // 2, ar_y - 18))

    # ── Defensores baixos — aviso pulsante ────────────────────────────────────
    warn_y = H // 2 - 160
    for p in planets:
        if p.conquered and p.is_conquerable and 0 < p.defenders <= 60:
            if (pygame.time.get_ticks() // 400) % 2 == 0:
                msg = font_small.render(
                    f"PERIGO: {p.name} — {p.defenders} defensores!", True, (255, 75, 45))
                screen.blit(msg, msg.get_rect(center=(W // 2, warn_y)))
            warn_y -= 28

    # ── Mensagem temporária central ───────────────────────────────────────────
    if ui_message_timer > 0:
        msg_surf = font_medium.render(ui_message, True, ui_message_color)
        screen.blit(msg_surf, msg_surf.get_rect(center=(W // 2, H // 2 - 120)))


def draw_radar():
    rr = 115
    mg = 20
    cx = rr + mg
    cy = HEIGHT - rr - mg

    # Escala próxima: vê Terra+Lua+inimigos próximos (~10k wu)
    RADAR_RANGE = 10000
    esc = (rr - 12) / RADAR_RANGE

    # Fundo escuro translúcido
    bg = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(bg, (0, 4, 14, 215), (rr, rr), rr)
    screen.blit(bg, (cx - rr, cy - rr))

    # Crosshair suave
    pygame.draw.line(screen, (0, 55, 35), (cx - rr + 14, cy), (cx + rr - 14, cy), 1)
    pygame.draw.line(screen, (0, 55, 35), (cx, cy - rr + 14), (cx, cy + rr - 14), 1)

    # Anéis de referência (33 % e 66 %)
    for frac in (0.33, 0.66):
        pygame.draw.circle(screen, (0, 65, 40), (cx, cy), int(rr * frac), 1)

    # Borda com glow duplo
    pygame.draw.circle(screen, (0, 80, 50),  (cx, cy), rr, 3)
    pygame.draw.circle(screen, (0, 190, 115), (cx, cy), rr, 1)
    pygame.draw.circle(screen, (0, 240, 150), (cx, cy), rr - 1, 1)

    # Ponto do jogador
    pygame.draw.circle(screen, (0, 255, 110), (cx, cy), 4)
    pygame.draw.circle(screen, (220, 255, 220), (cx, cy), 4, 1)

    # Sol — sempre clampado à borda
    sol_rel = pygame.math.Vector2(-player.world_pos.x, -player.world_pos.y)
    sdx, sdy = clamp_radar(sol_rel.x * esc, sol_rel.y * esc, rr - 7)
    sp_x, sp_y = int(cx + sdx), int(cy + sdy)
    pygame.draw.circle(screen, (255, 130, 0), (sp_x, sp_y), 7)
    pygame.draw.circle(screen, (255, 220, 60), (sp_x, sp_y), 4)

    # Planetas — ponto + nome curto
    font_r = pygame.font.Font(None, 13)
    for p in planets:
        rel = pygame.math.Vector2(p.x - player.world_pos.x, p.y - player.world_pos.y)
        dx, dy = clamp_radar(rel.x * esc, rel.y * esc, rr - 9)
        col = (255, 215, 0) if p.conquered else p.color
        px_, py_ = int(cx + dx), int(cy + dy)
        pygame.draw.circle(screen, col, (px_, py_), 6)
        pygame.draw.circle(screen, (180, 180, 180), (px_, py_), 6, 1)
        lbl = font_r.render(p.name[:4], True, col)
        screen.blit(lbl, (px_ - lbl.get_width() // 2, py_ - 14))

    # Inimigos — pulsam em vermelho
    pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.006)
    e_r   = max(3, int(3 + pulse * 1.5))
    e_col = (int(210 + 45 * pulse), int(25 + 25 * pulse), 30)
    for e in enemies:
        rel = e.world_pos - player.world_pos
        dx, dy = clamp_radar(rel.x * esc, rel.y * esc, rr - 5)
        pygame.draw.circle(screen, e_col, (int(cx + dx), int(cy + dy)), e_r)

    # Moedas/ouro (40 mais próximos)
    nearby_coins = sorted(coins, key=lambda c: (c.world_pos - player.world_pos).length_squared())[:40]
    for c in nearby_coins:
        rel = c.world_pos - player.world_pos
        dx, dy = clamp_radar(rel.x * esc, rel.y * esc, rr - 5)
        pygame.draw.circle(screen, (255, 215, 30), (int(cx + dx), int(cy + dy)), 2)

    # Tiros inimigos
    for b in list(bullets)[:20]:
        if getattr(b, "owner", None) == "enemy":
            rel = b.world_pos - player.world_pos
            dx, dy = clamp_radar(rel.x * esc, rel.y * esc, rr - 5)
            pygame.draw.circle(screen, (255, 55, 35), (int(cx + dx), int(cy + dy)), 2)

    # Label de escala + pontos cardeais
    ft = pygame.font.Font(None, 13)
    screen.blit(ft.render(f"{RADAR_RANGE // 1000}k u", True, (0, 160, 90)), (cx - rr + 5, cy - rr + 5))

    fc = pygame.font.Font(None, 12)
    co = rr - 6
    for label, ang_deg in (("N", 270), ("E", 0), ("S", 90), ("W", 180)):
        lx = cx + int(math.cos(math.radians(ang_deg)) * co)
        ly = cy + int(math.sin(math.radians(ang_deg)) * co)
        lt = fc.render(label, True, (0, 130, 75))
        screen.blit(lt, (lx - lt.get_width() // 2, ly - lt.get_height() // 2))

# ── GameEngine ────────────────────────────────────────────────────────────────
class GameEngine:
    def __init__(self):
        self.state          = GameState.LOGIN
        self.previous_state = None

    def transition_to(self, new_state: GameState):
        self.previous_state = self.state
        self.state          = new_state
        print(f"[STATE] {new_state.name}")

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt):
        global ui_message_timer
        if ui_message_timer > 0:
            ui_message_timer -= dt
        if self.state == GameState.ORBITAL:
            self._update_orbital(dt)

    def _update_orbital(self, dt):
        global score_enemies, invincible_timer
        global auto_save_timer, current_planet, player_gold, rapid_fire_timer
        global spawn_protection, bullet_shot_counter

        # Atualiza órbitas: planetas primeiro, satélites depois (dependem do pai)
        for planet in planets:
            if planet.parent_body is None:
                planet.update_orbit(dt)
        for planet in planets:
            if planet.parent_body is not None:
                planet.update_orbit(dt)

        # Reconquista por defensores esgotados
        for planet in planets:
            if planet.conquered and planet.is_conquerable and planet.defenders <= 0:
                planet.conquered  = False
                planet.defenders  = 0
                planet.reset_horde()
                show_message(
                    f"PERDIDO: {planet.name} foi reconquistado! Defensores eliminados.",
                    6.0, (255, 50, 50))

        players.update(dt)

        # ── Colisão com o Sol — nave rebate e toma dano ───────────────────────
        sol_dist = player.world_pos.length()
        if sol_dist < SOL_WORLD_RADIUS and sol_dist > 0.1:
            push_sol = player.world_pos.normalize()
            player.world_pos   = push_sol * (SOL_WORLD_RADIUS + 2)
            player.rect.center = (int(player.world_pos.x), int(player.world_pos.y))
            if invincible_timer <= 0:
                player.lives    -= 1
                invincible_timer = 2.0
                show_message("CALOR SOLAR! Afaste-se do Sol!", 2.0, (255, 100, 0))

        # ── Colisão orbital — apenas corpos conquistáveis são sólidos ─────────
        for p in planets:
            if not p.is_conquerable:
                continue
            d = p.check_distance(player.world_pos.x, player.world_pos.y)
            if d < p.visual_radius:
                # Rebate na superfície planetária — parede de colisão real
                if d > 0.1:
                    push = (player.world_pos - pygame.math.Vector2(p.x, p.y)).normalize()
                    player.world_pos = pygame.math.Vector2(p.x, p.y) + push * (p.visual_radius + 2)
                    player.rect.center = (int(player.world_pos.x), int(player.world_pos.y))
                horde_alive = sum(1 for e in enemies if e.invasion_conquest is None)
                if not p.horde_done or horde_alive > 0:
                    show_message(
                        f"Derrote todos os inimigos de {p.name} para pousar!",
                        0.5, (255, 80, 60))

        # ── Zona de atmosfera — hint de pouso (só conquistáveis) ─────────────
        for p in planets:
            if not p.is_conquerable:
                continue
            d = p.check_distance(player.world_pos.x, player.world_pos.y)
            if d < p.visual_radius * ATMOSPHERE_RATIO and d >= p.visual_radius:
                _horde_alive = sum(1 for e in enemies if e.invasion_conquest is None)
                can_land = p.conquered or (p.horde_done and _horde_alive == 0)
                if can_land:
                    show_message(f"Atmosfera de {p.name}  —  L: POUSAR", 0.15, (100, 220, 255))
                else:
                    show_message(f"Limpe a horda de {p.name} para pousar!", 0.15, (255, 160, 50))

        coins.update()
        enemies.update(player, dt, enemies)
        bullets.update(dt)

        # ── Chegada de tropas invasoras ───────────────────────────────────────
        # Ao chegar: reduz defensores; o contador da onda só muda quando o inimigo morre
        for e in list(enemies):
            if e._arrived_at is not None:
                target        = e._arrived_at
                e._arrived_at = None
                if target.conquered and target.is_conquerable and target.defenders > 0:
                    target.defenders -= 1

        if invincible_timer > 0:
            invincible_timer -= dt
        if spawn_protection > 0:
            spawn_protection -= dt

        # ── Sem horda: perto do Sol OU em proteção de spawn ──────────────────
        player_in_safe_zone = (
            player.world_pos.length() <= SAFE_ZONE_RADIUS or spawn_protection > 0
        )

        # ── Planeta conquistável mais próximo ─────────────────────────────────
        nearest, nearest_dist = None, float('inf')
        for p in planets:
            if not p.is_conquerable:
                continue
            d = p.check_distance(player.world_pos.x, player.world_pos.y)
            if d < nearest_dist:
                nearest_dist = d
                nearest      = p

        if nearest and nearest_dist <= nearest.activation_range and not player_in_safe_zone:
            current_planet = nearest
            current_planet.update_horde(dt, enemies, bullets, Enemy)
        else:
            current_planet = None

        # ── Colisões ─────────────────────────────────────────────────────────
        bullet_damage = 2 if player_gold >= POWER_SHOT_GOLD_MIN else 1
        for bullet in list(bullets):
            if getattr(bullet, "owner", None) == "player":
                hit = pygame.sprite.spritecollideany(
                    bullet, enemies, pygame.sprite.collide_circle)
                if hit:
                    bullet.kill()
                    hit.lives -= bullet_damage
                    if hit.lives <= 0:
                        # Se era invasor, decrementa e libera próxima onda se necessário
                        if hit.invasion_conquest is not None:
                            tgt = hit.invasion_conquest
                            tgt.invasion_active_count = max(0, tgt.invasion_active_count - 1)
                            if tgt.invasion_active_count <= 0 and tgt.conquered:
                                _send_next_invasion_wave(tgt)
                        drop_pos = pygame.math.Vector2(hit.world_pos)
                        hit.kill()
                        score_enemies += 1
                        coins.add(Coin(drop_pos.x, drop_pos.y))

        if invincible_timer <= 0:
            hits = [b for b in bullets
                    if getattr(b, "owner", None) == "enemy"
                    and pygame.sprite.collide_circle(player, b)]
            for b in hits:
                b.kill()
            if hits:
                player.lives -= 1
                invincible_timer = 1.0

        if player.lives <= 0:
            self.transition_to(GameState.GAMEOVER)

        # ── Coleta de ouro ────────────────────────────────────────────────────
        collected = pygame.sprite.spritecollide(player, coins, True)
        if collected:
            gained = len(collected)
            player_gold += gained
            show_message(f"+{gained} ouro!  Total: {player_gold}", 1.5, (255, 215, 0))

        # ── Tiro rápido (botão direito do mouse) ──────────────────────────────
        rapid_fire_timer -= dt
        if pygame.mouse.get_pressed()[2] and player_gold >= RAPID_FIRE_MIN_GOLD:
            if rapid_fire_timer <= 0:
                mx, my = pygame.mouse.get_pos()
                dx = mx - WIDTH  // 2
                dy = my - HEIGHT // 2
                d  = math.hypot(dx, dy)
                if d > 0:
                    direction = pygame.math.Vector2(dx / d, dy / d)
                    spawn_pos = player.world_pos + direction * 30
                    b = Bullet(spawn_pos, direction, (0, 200, 255))
                    b.owner = "player"
                    bullets.add(b)
                    bullet_shot_counter += 1
                    if bullet_shot_counter >= POWER_DRAIN_SHOTS:
                        bullet_shot_counter = 0
                        if player_gold >= POWER_SHOT_GOLD_MIN:
                            player_gold = max(0, player_gold - POWER_SHOT_DRAIN)
                rapid_fire_timer = RAPID_FIRE_INTERVAL

        camera.update(player)

        # Auto-save 30 s
        auto_save_timer += dt
        if auto_save_timer >= 30:
            db.save_player(player_db_id, player_username,
                           player.world_pos.x, player.world_pos.y,
                           player.lives, score_enemies, 0, player_gold)
            auto_save_timer = 0

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, screen):
        if   self.state == GameState.LOGIN:     self._draw_login(screen)
        elif self.state == GameState.MENU:      self._draw_menu(screen)
        elif self.state == GameState.ORBITAL:   self._draw_orbital(screen)
        elif self.state == GameState.STRATEGIC: self._draw_strategic(screen)
        elif self.state == GameState.GROUND:    self._draw_ground(screen)
        elif self.state == GameState.GAMEOVER:  self._draw_gameover(screen)

    def _draw_login(self, screen):
        screen.fill((5, 5, 15))
        star_field.draw(screen, 0, 0, WIDTH, HEIGHT)

        fl = pygame.font.Font(None, 80)
        fm = pygame.font.Font(None, 36)
        fs = pygame.font.Font(None, 28)

        title = fl.render("GAME ZERO", True, (80, 220, 80))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150)))

        label = fm.render("Digite seu nome de piloto:", True, (200, 200, 200))
        screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))

        # Caixa de input
        bw, bh = 420, 54
        bx = WIDTH // 2 - bw // 2
        by = HEIGHT // 2 - 10
        pygame.draw.rect(screen, (25, 25, 55), (bx, by, bw, bh), border_radius=8)
        pygame.draw.rect(screen, (80, 120, 220), (bx, by, bw, bh), 2, border_radius=8)

        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        inp    = fs.render(player_name_input + cursor, True, (255, 255, 255))
        screen.blit(inp, (bx + 16, by + 13))

        hint = fs.render("ENTER para entrar", True, (100, 180, 100))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 82)))

    def _draw_menu(self, screen):
        screen.fill((5, 5, 15))
        star_field.draw(screen, 0, 0, WIDTH, HEIGHT)

        fl = pygame.font.Font(None, 80)
        fm = pygame.font.Font(None, 36)
        fs = pygame.font.Font(None, 26)

        title = fl.render("GAME ZERO", True, (80, 220, 80))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110)))

        welcome = fm.render(f"Bem-vindo, {player_username}!", True, (180, 255, 180))
        screen.blit(welcome, welcome.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

        ouro = fm.render(f"Ouro disponivel: {player_gold}", True, (255, 215, 0))
        screen.blit(ouro, ouro.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

        start = fm.render("SPACE: iniciar missao", True, (220, 220, 80))
        screen.blit(start, start.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))

        tips = [
            "WASD/setas: mover  |  Mouse: atirar  |  M: mapa estrategico",
            f"F: Dobra Temporal (custa {DOBRA_GOLD_COST} ouro de lava_world)",
        ]
        for i, t in enumerate(tips):
            s = fs.render(t, True, (100, 130, 100))
            screen.blit(s, s.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 138 + i * 26)))

    def _draw_orbital(self, screen):
        screen.fill((5, 5, 15))
        star_field.draw(screen, camera.camera.x, camera.camera.y, WIDTH, HEIGHT)

        draw_safe_zone()

        # Halo de atmosfera — anel translúcido em torno de cada planeta visível
        for p in planets:
            atm_r = int(p.visual_radius * ATMOSPHERE_RATIO * camera.zoom)
            if atm_r < 3:
                continue
            px_, py_ = camera.world_to_screen(p.x, p.y)
            if px_ + atm_r < -60 or px_ - atm_r > WIDTH + 60 or \
               py_ + atm_r < -60 or py_ - atm_r > HEIGHT + 60:
                continue
            s = pygame.Surface((atm_r * 2 + 10, atm_r * 2 + 10), pygame.SRCALPHA)
            cx, cy = atm_r + 5, atm_r + 5
            for off, alpha in ((0, 40), (3, 22), (7, 10)):
                pygame.draw.circle(s, (*p.color, alpha), (cx, cy), max(1, atm_r - off), 3)
            screen.blit(s, (px_ - atm_r - 5, py_ - atm_r - 5))

        for p in planets:
            p.draw_orbital(screen, camera)

        # Moedas
        for coin in coins:
            screen.blit(camera.scale_img(coin.image), camera.apply(coin))

        # Inimigos — tamanho visual desacoplado da física
        for enemy in enemies:
            ep = max(3, min(150, round(ENEMY_VISUAL_UNITS * 2 * camera.zoom)))
            ei = pygame.transform.scale(enemy.image, (ep, ep))
            ex, ey = camera.world_to_screen(enemy.rect.centerx, enemy.rect.centery)
            er = ei.get_rect(); er.center = (ex, ey)
            screen.blit(ei, er)

        # Nave — visual desacoplado da física; colisão usa SHIP_WORLD_UNITS
        sp = max(4, min(150, round(SHIP_VISUAL_UNITS * 2 * camera.zoom)))
        si = pygame.transform.scale(player.image, (sp, sp))
        px_, py_ = camera.world_to_screen(player.rect.centerx, player.rect.centery)
        pr = si.get_rect(); pr.center = (px_, py_)
        screen.blit(si, pr)

        # Balas
        for bullet in bullets:
            screen.blit(camera.scale_img(bullet.image), camera.apply(bullet))

        draw_hud()
        # Indicador de zoom + hint da tecla Q
        zl    = camera.zoom_label()
        zfont = pygame.font.Font(None, 18)
        hint  = "  Q: voltar" if camera.zoom_target < ZOOM_START * 0.8 else ""
        ztxt  = zfont.render(f"ZOOM {zl}  scroll:±{hint}", True,
                              (80, 200, 80) if hint else (80, 140, 80))
        screen.blit(ztxt, (WIDTH - ztxt.get_width() - 10, HEIGHT - 20))
        draw_radar()

    def _draw_strategic(self, screen):
        screen.fill((5, 5, 15))
        star_field.draw(screen, 0, 0, WIDTH, HEIGHT)

        ref_x = player.world_pos.x if player else 0.0
        ref_y = player.world_pos.y if player else 0.0
        sc    = STRAT_SCALE_BASE * strat_zoom   # escala com zoom

        # Posição do Sol na tela (usando a escala com zoom)
        sun_sx = int((0 - ref_x) * sc + WIDTH  // 2)
        sun_sy = int((0 - ref_y) * sc + HEIGHT // 2)

        # Elipses orbitais (escaladas com zoom)
        for p in planets:
            if p.semi_major_axis <= 0 or p.parent_body is not None:
                continue
            orb_r = int(p.semi_major_axis * sc)
            if orb_r < 2:
                continue
            if (sun_sx + orb_r < -10 or sun_sx - orb_r > WIDTH  + 10 or
                    sun_sy + orb_r < -10 or sun_sy - orb_r > HEIGHT + 10):
                continue
            pygame.draw.circle(screen, (30, 35, 55), (sun_sx, sun_sy), orb_r, 1)

        # Sol
        sol_strat_r = max(5, int(SOL_WORLD_RADIUS * sc))
        if (-sol_strat_r * 2 < sun_sx < WIDTH + sol_strat_r * 2 and
                -sol_strat_r * 2 < sun_sy < HEIGHT + sol_strat_r * 2):
            pygame.draw.circle(screen, (60, 40, 0),     (sun_sx, sun_sy), int(sol_strat_r * 1.5))
            pygame.draw.circle(screen, (150, 100, 0),   (sun_sx, sun_sy), int(sol_strat_r * 1.2))
            pygame.draw.circle(screen, (255, 200, 30),  (sun_sx, sun_sy), sol_strat_r)
            pygame.draw.circle(screen, (255, 240, 140), (sun_sx, sun_sy), max(2, sol_strat_r // 2))
            ft   = pygame.font.Font(None, 15)
            stxt = ft.render("Sol", True, (255, 220, 50))
            screen.blit(stxt, (sun_sx - stxt.get_width() // 2, sun_sy + sol_strat_r + 3))

        # Linha de rota
        if selected_planet:
            sx, sy = selected_planet.screen_pos_strategic(WIDTH, HEIGHT, ref_x, ref_y, scale=sc)
            pygame.draw.line(screen, (60, 80, 180), (WIDTH // 2, HEIGHT // 2), (sx, sy), 1)

        # Planetas (passando scale para posicionamento e raio corretos)
        for p in planets:
            p.draw_strategic(screen, WIDTH, HEIGHT, ref_x, ref_y,
                             is_selected=(p is selected_planet), scale=sc)

        # Hint zoom
        ft2 = pygame.font.Font(None, 15)
        zt  = ft2.render(f"MAPA ZOOM {strat_zoom:.1f}x  scroll:±", True, (60, 120, 60))
        screen.blit(zt, (14, 14))

        # Player (sempre no centro — o mapa gira em torno dele)
        pygame.draw.circle(screen, (80, 255, 80), (WIDTH // 2, HEIGHT // 2), 7)
        pygame.draw.circle(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 7, 2)
        lbl = pygame.font.Font(None, 17).render(player_username, True, (80, 255, 80))
        screen.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, HEIGHT // 2 - 19))

        # Painel lateral
        if selected_planet:
            selected_planet.draw_strategic_info(screen, WIDTH, HEIGHT)

        # Ouro no mapa
        ouro_cor = (255, 215, 0) if player_gold >= DOBRA_GOLD_COST else (130, 100, 0)
        screen.blit(font_small.render(f"Ouro: {player_gold}", True, ouro_cor),
                    (14, HEIGHT - 50))

        font = pygame.font.Font(None, 21)
        hints = [
            "CLIQUE: selecionar planeta",
            "M / ESC: voltar a pilotar",
            f"F: Dobra Temporal (custa {DOBRA_GOLD_COST} ouro)",
        ]
        for i, h in enumerate(hints):
            screen.blit(font.render(h, True, (100, 160, 100)), (14, 14 + i * 21))

    def _draw_ground(self, screen):
        p = landed_planet

        # Paletas por tipo de planeta
        SKY = {
            'forest':              ((2,8,30),   (10,40,100),  (40,90,180)),
            'lava_world':          ((15,2,2),   (60,10,5),    (140,30,5)),
            'gas_giant':           ((20,12,5),  (80,50,15),   (160,110,30)),
            'ice_world':           ((3,10,25),  (20,60,110),  (80,150,210)),
            'terrestrial_iron':    ((18,8,3),   (65,30,10),   (120,60,25)),
            'terrestrial_silicon': ((12,12,4),  (50,45,15),   (100,90,35)),
        }
        TERRAIN = {
            'forest':              (15,65,15),
            'lava_world':          (45,5,3),
            'gas_giant':           (100,70,20),
            'ice_world':           (180,210,230),
            'terrestrial_iron':    (80,35,15),
            'terrestrial_silicon': (70,65,25),
        }
        ptype  = (p.planet_type if p else 'forest')
        deep, mid, high = SKY.get(ptype, ((2,8,30),(10,40,100),(40,90,180)))
        tc     = TERRAIN.get(ptype, (30,60,30))
        pcolor = p.color if p else (43,108,255)

        terrain_y = int(HEIGHT * 0.70)

        # Gradiente de céu
        for y in range(terrain_y):
            t = y / terrain_y
            if t < 0.5:
                t2 = t * 2
                r = int(deep[0] + (mid[0]-deep[0]) * t2)
                g = int(deep[1] + (mid[1]-deep[1]) * t2)
                b = int(deep[2] + (mid[2]-deep[2]) * t2)
            else:
                t2 = (t-0.5) * 2
                r = int(mid[0] + (high[0]-mid[0]) * t2)
                g = int(mid[1] + (high[1]-mid[1]) * t2)
                b = int(mid[2] + (high[2]-mid[2]) * t2)
            pygame.draw.line(screen, (r,g,b), (0,y), (WIDTH,y))

        # Estrelas no céu
        rng = random.Random((p.id if p else 0) * 7919)
        for _ in range(90):
            sx_ = rng.randint(0, WIDTH)
            sy_ = rng.randint(0, int(terrain_y * 0.55))
            bri = rng.randint(140, 255)
            pygame.draw.circle(screen, (bri,bri,bri), (sx_,sy_), 1)

        # Planeta no horizonte (parcial, mostra curvatura)
        pygame.draw.circle(screen, pcolor,
                           (WIDTH // 2, terrain_y + int(HEIGHT * 0.8)),
                           int(HEIGHT * 0.75), 0)
        pygame.draw.circle(screen, tuple(min(255,c+40) for c in pcolor),
                           (WIDTH // 2, terrain_y + int(HEIGHT * 0.8)),
                           int(HEIGHT * 0.75), 3)

        # Terreno irregular (polygon)
        seed_v = (p.id if p else 1)
        pts = [(0, HEIGHT), (0, terrain_y)]
        for x in range(0, WIDTH+1, 30):
            y_off = int(math.sin(x * 0.025 + seed_v) * 14
                        + math.sin(x * 0.07 + seed_v*2) * 6)
            pts.append((x, terrain_y + y_off))
        pts.append((WIDTH, HEIGHT))
        pygame.draw.polygon(screen, tc, pts)
        # Linha de superfície brilhante
        surf_pts = pts[2:-1]
        if len(surf_pts) > 1:
            pygame.draw.lines(screen, tuple(min(255,c+50) for c in tc), False, surf_pts, 2)

        # Nave pousada no centro
        ship_s = 80
        si = pygame.transform.scale(player.image, (ship_s, ship_s))
        screen.blit(si, (WIDTH//2 - ship_s//2, terrain_y - ship_s - 2))

        # Poeira de pouso
        for i in range(-2, 3):
            dx = i * 18
            dw = 36 - abs(i)*5
            pygame.draw.ellipse(screen, tuple(min(255,c+70) for c in tc),
                                (WIDTH//2 + dx - dw//2, terrain_y - 10, dw, 9))

        # Título
        pname = p.name if p else "Planeta"
        title_s = font_large.render(f"POUSADO: {pname}", True, (255,255,200))
        screen.blit(title_s, title_s.get_rect(center=(WIDTH//2, 55)))

        # Status
        if p and p.conquered:
            st_txt  = "CONQUISTADO"
            st_cor  = (80,255,80)
        else:
            st_txt  = "Território inimigo"
            st_cor  = (255,120,50)
        st_s = font_medium.render(st_txt, True, st_cor)
        screen.blit(st_s, st_s.get_rect(center=(WIDTH//2, 118)))

        # Instrução
        inst = font_small.render("SPACE / ESC / L : decolar e voltar à órbita", True, (200,200,220))
        screen.blit(inst, inst.get_rect(center=(WIDTH//2, HEIGHT - 30)))

    def _draw_gameover(self, screen):
        screen.fill((0, 0, 0))
        go = font_large.render("GAME OVER", True, (255, 0, 0))
        screen.blit(go, go.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
        st = font_medium.render(f"Ouro perdido: {player_gold}", True, (200, 150, 0))
        screen.blit(st, st.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        rs = font_medium.render("R: reiniciar  |  ESC: sair", True, (200, 200, 200))
        screen.blit(rs, rs.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))


game_engine = GameEngine()

# ── Game Loop ─────────────────────────────────────────────────────────────────
while running:
    dt = clock.tick(FPS) / 1000

    # Resolução real da janela a cada frame (muda ao redimensionar/maximizar)
    WIDTH, HEIGHT = screen.get_size()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.WINDOWRESIZED:
            camera.resize(event.x, event.y)

        # ── Scroll do mouse (MOUSEWHEEL nativo) ──────────────────────────────────
        elif event.type == pygame.MOUSEWHEEL:
            if game_engine.state == GameState.ORBITAL:
                camera.zoom_step(event.y)
            elif game_engine.state == GameState.STRATEGIC:
                factor = 1.15 if event.y > 0 else (1.0 / 1.15)
                strat_zoom = max(0.05, min(8.0, strat_zoom * factor))

        elif event.type == pygame.KEYDOWN:

            # ── LOGIN ─────────────────────────────────────────────────────────
            if game_engine.state == GameState.LOGIN:
                if event.key == pygame.K_BACKSPACE:
                    player_name_input = player_name_input[:-1]
                elif event.key == pygame.K_RETURN and player_name_input.strip():
                    username = player_name_input.strip()[:20]
                    existing = db.get_player_by_username(username)
                    if existing:
                        player_db_id    = existing['id']
                        player_gold     = existing.get('gold', 0)
                        player_username = username
                        print(f"[LOGIN] Bem-vindo de volta, {username}! Ouro: {player_gold}")
                    else:
                        player_db_id    = db.create_player(username, '#00FF00')
                        player_gold     = 0
                        player_username = username
                        print(f"[LOGIN] Novo piloto: {username}")
                    game_engine.transition_to(GameState.MENU)
                elif event.unicode.isprintable() and len(player_name_input) < 20:
                    player_name_input += event.unicode

            # ── MENU ──────────────────────────────────────────────────────────
            elif game_engine.state == GameState.MENU:
                if event.key == pygame.K_SPACE:
                    initialize_game()
                    game_engine.transition_to(GameState.ORBITAL)

            # ── ORBITAL ───────────────────────────────────────────────────────
            elif game_engine.state == GameState.ORBITAL:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    strat_zoom = 1.0   # reset zoom ao abrir mapa
                    game_engine.transition_to(GameState.STRATEGIC)
                elif event.key == pygame.K_f:
                    do_dobra_temporal()
                elif event.key == pygame.K_q:
                    # Q — snap zoom de volta ao padrão
                    camera.zoom_target = ZOOM_START
                elif event.key == pygame.K_l:
                    # L — pousar no planeta mais próximo (se na atmosfera e horda limpa)
                    for p in planets:
                        d = p.check_distance(player.world_pos.x, player.world_pos.y)
                        if d < p.visual_radius * ATMOSPHERE_RATIO:
                            _hl = sum(1 for e in enemies if e.invasion_conquest is None)
                            can_land = p.conquered or (p.horde_done and _hl == 0)
                            if can_land:
                                landed_planet = p
                                landed_angle  = math.atan2(
                                    player.world_pos.y - p.y,
                                    player.world_pos.x - p.x,
                                )
                                if not p.conquered:
                                    p.conquered  = True
                                    p.defenders  = 200   # horda aliada (5 ondas × 40)
                                    db.set_planet_conquered(p.id, player_db_id)
                                    player.lives += 1
                                    trigger_invasions(p)
                                game_engine.transition_to(GameState.GROUND)
                            break
                elif event.key == pygame.K_r:
                    pass  # R só funciona no GAMEOVER

            # ── STRATEGIC ─────────────────────────────────────────────────────
            elif game_engine.state == GameState.STRATEGIC:
                if event.key in (pygame.K_m, pygame.K_ESCAPE):
                    game_engine.transition_to(GameState.ORBITAL)
                elif event.key == pygame.K_f:
                    # Dobra a partir do mapa: teletransporta E fecha o mapa
                    if do_dobra_temporal():
                        game_engine.transition_to(GameState.ORBITAL)

            # ── GROUND ────────────────────────────────────────────────────────
            elif game_engine.state == GameState.GROUND:
                if event.key in (pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_l):
                    # Decola: posiciona nave fora da atmosfera no ângulo de chegada
                    if landed_planet:
                        r = landed_planet.visual_radius * 1.28
                        player.world_pos = pygame.math.Vector2(
                            landed_planet.x + math.cos(landed_angle) * r,
                            landed_planet.y + math.sin(landed_angle) * r,
                        )
                        player.rect.center = (int(player.world_pos.x), int(player.world_pos.y))
                    game_engine.transition_to(GameState.ORBITAL)

            # ── GAMEOVER ──────────────────────────────────────────────────────
            elif game_engine.state == GameState.GAMEOVER:
                if event.key == pygame.K_r:
                    initialize_game()
                    game_engine.transition_to(GameState.ORBITAL)
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # ── Mouse: clique + scroll fallback ──────────────────────────────────────
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # ── Scroll fallback (botões 4/5) para pygame sem MOUSEWHEEL ─────────
            if event.button in (4, 5):
                direction_scroll = 1 if event.button == 4 else -1
                if game_engine.state == GameState.ORBITAL:
                    camera.zoom_step(direction_scroll)
                elif game_engine.state == GameState.STRATEGIC:
                    factor = 1.15 if direction_scroll > 0 else (1.0 / 1.15)
                    strat_zoom = max(0.05, min(8.0, strat_zoom * factor))

            # ── Clique esquerdo ──────────────────────────────────────────────────
            elif event.button == 1:
                if game_engine.state == GameState.STRATEGIC:
                    ref_x  = player.world_pos.x if player else 0.0
                    ref_y  = player.world_pos.y if player else 0.0
                    sc     = STRAT_SCALE_BASE * strat_zoom   # escala atual do mapa
                    hit_r  = max(12, int(20 * strat_zoom))   # raio de clique escalado
                    selected_planet = None
                    for p in planets:
                        sx, sy = p.screen_pos_strategic(WIDTH, HEIGHT, ref_x, ref_y, scale=sc)
                        if math.hypot(mx - sx, my - sy) <= p.strat_radius * strat_zoom + hit_r:
                            selected_planet = p
                            print(f"[MAP] Selecionado: {p.name}")
                            break

                elif game_engine.state == GameState.ORBITAL and player:
                    # Direção zoom-aware: screen → world via camera
                    wx, wy    = camera.screen_to_world(mx, my)
                    direction = pygame.math.Vector2(wx - player.world_pos.x,
                                                    wy - player.world_pos.y)
                    if direction.length() > 0:
                        direction = direction.normalize()
                    else:
                        direction = pygame.math.Vector2(0, -1)
                    b       = Bullet(player.world_pos + direction * 20, direction, (0, 255, 0))
                    b.owner = "player"
                    bullets.add(b)
                    bullet_shot_counter += 1
                    if bullet_shot_counter >= POWER_DRAIN_SHOTS:
                        bullet_shot_counter = 0
                        if player_gold >= POWER_SHOT_GOLD_MIN:
                            player_gold = max(0, player_gold - POWER_SHOT_DRAIN)

    game_engine.update(dt)
    game_engine.draw(screen)
    pygame.display.flip()

# ── Cleanup ───────────────────────────────────────────────────────────────────
if player is not None and player_db_id is not None:
    db.save_player(player_db_id, player_username,
                   player.world_pos.x, player.world_pos.y,
                   player.lives, score_enemies, 0, player_gold)
    print(f"[SAVE] {player_username} salvo. Ouro: {player_gold}")

db.backup()
db.close()
pygame.quit()
