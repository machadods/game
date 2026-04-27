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
from settings import WIDTH, HEIGHT, FPS

# Diz ao Windows para não escalar o processo — pygame recebe pixels reais da tela
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
from src.player import Player
from src.coin import Coin
from src.camera import Camera
from src.enemy import Enemy
from src.bullet import Bullet
from src.stars import StarField
from src.database import GameDatabase
from src.celestial.planet import Planet, PLANET_TYPES, STRAT_SCALE

# ── Constantes de gameplay ────────────────────────────────────────────────────
UNIVERSE_LIMIT_X  = 80000
UNIVERSE_LIMIT_Y  = 80000
SAFE_ZONE_RADIUS  = 3000
DOBRA_GOLD_COST   = 50

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
        'planet_type': 'forest',
        'x':  28100, 'y':   9000,   # ~29 400 u
        'difficulty': 2,
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
player           = None
score_enemies    = 0
invincible_timer = 0.0
auto_save_timer  = 0.0
game_initialized = False
rapid_fire_timer = 0.0

RAPID_FIRE_INTERVAL = 0.08
RAPID_FIRE_MIN_GOLD = 10

# ── Jogador / Login ───────────────────────────────────────────────────────────
player_db_id     = None
player_username  = ""
player_gold      = 0          # ouro acumulado (moeda da Dobra Temporal)
player_name_input = ""        # campo de texto na tela de login

# ── Planetas e navegação ──────────────────────────────────────────────────────
planets         = []
selected_planet = None
current_planet  = None

# ── UI temporária (mensagens na tela) ─────────────────────────────────────────
ui_message       = ""
ui_message_timer = 0.0
ui_message_color = (255, 220, 60)

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


planets_db = db.get_all_planets()
expected_names = {e['name'] for e in SOLAR_SYSTEM}
existing_names = {row['name'] for row in planets_db}
if not planets_db or expected_names != existing_names:
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

# ── Inicialização do mundo ────────────────────────────────────────────────────
def initialize_game():
    global player, score_enemies, invincible_timer
    global game_initialized, current_planet

    current_planet  = None
    player = Player("player_1")
    players.empty(); players.add(player)

    score_enemies    = 0
    invincible_timer = 0.0
    game_initialized = True

    coins.empty(); enemies.empty(); bullets.empty()

    # Player nasce na zona segura (origem)
    player.world_pos   = pygame.math.Vector2(0, 0)
    player.rect.center = (0, 0)

    # Reset das hordas
    for p in planets:
        p.reset_horde()

    # Ouro em anel ao redor de cada planeta — quantidade proporcional à dificuldade
    for p in planets:
        mineral_count = p.difficulty * 20
        for _ in range(mineral_count):
            angle = random.uniform(0, 2 * math.pi)
            dist  = random.uniform(p.visual_radius + 300, p.visual_radius + 2200)
            coins.add(Coin(
                p.x + math.cos(angle) * dist,
                p.y + math.sin(angle) * dist,
            ))

    show_message("Bem-vindo, piloto! Navegue para os planetas ou use Dobra Temporal (F).",
                 5.0, (80, 220, 80))

# ── Dobra Temporal ────────────────────────────────────────────────────────────
def do_dobra_temporal() -> bool:
    """Teletransporta o player para o raio de ativação do planeta selecionado.
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

    # Spawn a uma distância que já ativa a horda
    angle  = random.uniform(0, 2 * math.pi)
    dist   = selected_planet.activation_range - 100   # dentro do raio de ativação
    px     = selected_planet.x + math.cos(angle) * dist
    py     = selected_planet.y + math.sin(angle) * dist

    player.world_pos   = pygame.math.Vector2(px, py)
    player.rect.center = (int(px), int(py))

    show_message(f"Dobra Temporal: {selected_planet.name}! (-{DOBRA_GOLD_COST} ouro)",
                 4.0, (100, 200, 255))
    print(f"[DOBRA] Destino: {selected_planet.name}  |  Ouro restante: {player_gold}")
    return True

# ── Helpers ───────────────────────────────────────────────────────────────────
def clamp_radar(dx, dy, max_r):
    d = math.hypot(dx, dy)
    if d > max_r:
        s = max_r / d
        return dx * s, dy * s
    return dx, dy


def draw_safe_zone():
    """Círculo verde indicando a zona segura (origem do mundo)."""
    sx = int(0 + camera.camera.x)
    sy = int(0 + camera.camera.y)
    sr = SAFE_ZONE_RADIUS

    if (sx + sr < -100 or sx - sr > WIDTH + 100 or
            sy + sr < -100 or sy - sr > HEIGHT + 100):
        return

    # Borda
    pygame.draw.circle(screen, (40, 140, 70), (sx, sy), sr, 2)
    # Beacon central
    pygame.draw.circle(screen, (50, 200, 80), (sx, sy), 22)
    pygame.draw.circle(screen, (255, 255, 255), (sx, sy), 22, 2)
    font = pygame.font.Font(None, 20)
    txt  = font.render("ZONA SEGURA", True, (50, 220, 80))
    screen.blit(txt, (sx - txt.get_width() // 2, sy - 38))


def draw_hud():
    # Vidas
    for i in range(player.lives):
        pygame.draw.circle(screen, (255, 0, 0), (50 + i * 40, 50), 15)

    # Nome do piloto
    screen.blit(font_small.render(player_username, True, (100, 220, 100)), (10, HEIGHT - 48))

    # Scores
    screen.blit(font_small.render(f"Inimigos: {score_enemies}", True, (255, 100, 100)), (WIDTH - 260, 30))

    # Ouro
    ouro_cor = (255, 215, 0) if player_gold >= DOBRA_GOLD_COST else (160, 130, 0)
    screen.blit(font_small.render(f"Ouro: {player_gold}", True, ouro_cor), (WIDTH - 260, 60))

    # Tiro rápido
    if player_gold >= RAPID_FIRE_MIN_GOLD:
        rf_cor = (0, 230, 255)
        rf_txt = "Bot.Dir: TIRO RAPIDO" if pygame.mouse.get_pressed()[2] else f"Bot.Dir: pronto (>={RAPID_FIRE_MIN_GOLD} ouro)"
    else:
        rf_cor = (100, 100, 120)
        rf_txt = f"Bot.Dir: precisa {RAPID_FIRE_MIN_GOLD} ouro"
    screen.blit(font_small.render(rf_txt, True, rf_cor), (WIDTH - 260, 90))

    # Planeta ativo (horda)
    if current_planet:
        alive = len(enemies)
        sp, tot = current_planet.horde_spawned, current_planet.horde_total
        cor = (80, 255, 80) if current_planet.horde_done else (255, 200, 80)
        screen.blit(font_small.render(
            f"{current_planet.name}: {alive} vivos ({sp}/{tot})", True, cor),
            (WIDTH - 400, 120))
        if current_planet.conquered:
            msg = font_medium.render("PLANETA CONQUISTADO! — M: mapa", True, (80, 255, 80))
            screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT - 55)))

    # Waypoint do planeta selecionado
    if selected_planet and player:
        rel  = pygame.math.Vector2(selected_planet.x - player.world_pos.x,
                                   selected_planet.y - player.world_pos.y)
        dist = rel.length()
        if dist > selected_planet.visual_radius + 100:
            ang  = math.atan2(rel.y, rel.x)
            ar_x = WIDTH  // 2 + int(math.cos(ang) * 145)
            ar_y = HEIGHT // 2 + int(math.sin(ang) * 145)
            pygame.draw.circle(screen, selected_planet.color, (ar_x, ar_y), 9)
            pygame.draw.circle(screen, (255, 255, 255), (ar_x, ar_y), 9, 2)
            ft  = pygame.font.Font(None, 19)
            dtx = ft.render(f"{selected_planet.name}  {int(dist)}u", True, selected_planet.color)
            screen.blit(dtx, (ar_x - dtx.get_width() // 2, ar_y - 18))

    # Hint Dobra Temporal
    dobra_cor = (100, 200, 255) if player_gold >= DOBRA_GOLD_COST else (80, 80, 100)
    screen.blit(pygame.font.Font(None, 20).render(
        f"F: Dobra Temporal (custa {DOBRA_GOLD_COST} ouro)", True, dobra_cor),
        (10, HEIGHT - 22))

    # Mensagem temporária central
    if ui_message_timer > 0:
        msg_surf = font_medium.render(ui_message, True, ui_message_color)
        screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))


def draw_radar():
    rr = 100; esc = 0.007; mg = 20
    cx = rr + mg; cy = HEIGHT - rr - mg

    surf = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
    pygame.draw.circle(surf, (0, 0, 0, 150), (rr, rr), rr)
    screen.blit(surf, (cx - rr, cy - rr))
    pygame.draw.circle(screen, (255, 255, 255), (cx, cy), rr, 2)
    pygame.draw.circle(screen, (0, 255, 0),     (cx, cy), 4)

    for e in enemies:
        rel = e.world_pos - player.world_pos
        dx, dy = clamp_radar(rel.x * esc, rel.y * esc, rr - 5)
        pygame.draw.circle(screen, (255, 0, 0), (int(cx + dx), int(cy + dy)), 3)

    for c in coins:
        rel = c.world_pos - player.world_pos
        dx, dy = clamp_radar(rel.x * esc, rel.y * esc, rr - 5)
        pygame.draw.circle(screen, (255, 255, 0), (int(cx + dx), int(cy + dy)), 2)

    for b in bullets:
        rel = b.world_pos - player.world_pos
        dx, dy = clamp_radar(rel.x * esc, rel.y * esc, rr - 5)
        cor = (0, 255, 0) if getattr(b, "owner", "") == "player" else (255, 0, 0)
        pygame.draw.circle(screen, cor, (int(cx + dx), int(cy + dy)), 2)

    for p in planets:
        rel = pygame.math.Vector2(p.x - player.world_pos.x, p.y - player.world_pos.y)
        dx, dy = clamp_radar(rel.x * esc, rel.y * esc, rr - 5)
        col = (255, 215, 0) if p.conquered else p.color
        pygame.draw.circle(screen, col, (int(cx + dx), int(cy + dy)), 5)

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

        players.update(dt)
        coins.update()
        enemies.update(player, dt, enemies)
        bullets.update(dt)

        if invincible_timer > 0:
            invincible_timer -= dt

        # ── Zona segura: bloqueia ativação de horda ──────────────────────────
        player_in_safe_zone = (player.world_pos.length() <= SAFE_ZONE_RADIUS)

        # ── Planeta mais próximo ──────────────────────────────────────────────
        nearest, nearest_dist = None, float('inf')
        for p in planets:
            d = p.check_distance(player.world_pos.x, player.world_pos.y)
            if d < nearest_dist:
                nearest_dist = d
                nearest      = p

        if nearest and nearest_dist <= nearest.activation_range and not player_in_safe_zone:
            current_planet = nearest
            current_planet.update_horde(dt, enemies, bullets, Enemy)
            if (current_planet.horde_done
                    and len(enemies) == 0
                    and not current_planet.conquered):
                current_planet.conquered = True
                db.set_planet_conquered(current_planet.id, player_db_id)
                player.lives += 1
                show_message(
                    f"{current_planet.name} CONQUISTADO! +1 vida  ({player.lives} vidas)",
                    5.0, (80, 255, 80))
        else:
            current_planet = None

        # ── Colisões ─────────────────────────────────────────────────────────
        for bullet in list(bullets):
            if getattr(bullet, "owner", None) == "player":
                hit = pygame.sprite.spritecollideany(
                    bullet, enemies, pygame.sprite.collide_circle)
                if hit:
                    bullet.kill()
                    hit.lives -= 1
                    if hit.lives <= 0:
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

        for p in planets:
            p.draw_orbital(screen, camera)

        for coin in coins:
            screen.blit(coin.image, camera.apply(coin))
        for enemy in enemies:
            screen.blit(enemy.image, camera.apply(enemy))
        screen.blit(player.image, camera.apply(player))
        for bullet in bullets:
            screen.blit(bullet.image, camera.apply(bullet))

        draw_hud()
        draw_radar()

    def _draw_strategic(self, screen):
        screen.fill((5, 5, 15))
        star_field.draw(screen, 0, 0, WIDTH, HEIGHT)

        ref_x = player.world_pos.x if player else 0.0
        ref_y = player.world_pos.y if player else 0.0

        # Zona segura no mapa (círculo pequeno no centro)
        sz_r = max(4, int(SAFE_ZONE_RADIUS * STRAT_SCALE))
        pygame.draw.circle(screen, (40, 140, 70), (WIDTH // 2, HEIGHT // 2), sz_r, 1)

        # Linha de rota
        if selected_planet:
            sx, sy = selected_planet.screen_pos_strategic(WIDTH, HEIGHT, ref_x, ref_y)
            pygame.draw.line(screen, (60, 60, 150), (WIDTH // 2, HEIGHT // 2), (sx, sy), 1)

        # Planetas
        for p in planets:
            p.draw_strategic(screen, WIDTH, HEIGHT, ref_x, ref_y,
                             is_selected=(p is selected_planet))

        # Player (centro)
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
        screen.fill((10, 20, 10))
        msg = font_medium.render("GROUND — em desenvolvimento", True, (200, 200, 100))
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

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
                    game_engine.transition_to(GameState.STRATEGIC)
                elif event.key == pygame.K_f:
                    do_dobra_temporal()
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

            # ── GAMEOVER ──────────────────────────────────────────────────────
            elif game_engine.state == GameState.GAMEOVER:
                if event.key == pygame.K_r:
                    initialize_game()
                    game_engine.transition_to(GameState.ORBITAL)
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # ── Clique esquerdo ───────────────────────────────────────────────────
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if game_engine.state == GameState.STRATEGIC:
                ref_x = player.world_pos.x if player else 0.0
                ref_y = player.world_pos.y if player else 0.0
                selected_planet = None
                for p in planets:
                    sx, sy = p.screen_pos_strategic(WIDTH, HEIGHT, ref_x, ref_y)
                    if math.hypot(mx - sx, my - sy) <= p.strat_radius + 16:
                        selected_planet = p
                        print(f"[MAP] Selecionado: {p.name}")
                        break

            elif game_engine.state == GameState.ORBITAL and player:
                world_mouse = pygame.math.Vector2(mx, my) - pygame.math.Vector2(camera.camera.topleft)
                direction   = world_mouse - player.world_pos
                if direction.length() > 0:
                    direction = direction.normalize()
                else:
                    direction = pygame.math.Vector2(0, -1)
                b       = Bullet(player.world_pos + direction * 20, direction, (0, 255, 0))
                b.owner = "player"
                bullets.add(b)

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
