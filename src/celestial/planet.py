import pygame
import random
import math
from dataclasses import dataclass
from typing import Dict
from settings import ORBITAL_DATA, ORBITAL_SCALE, TIME_SCALE, EARTH_ORBIT_KM

# 1 unidade de mundo = 1 px na tela orbital
# No mapa estratégico, tudo é reduzido por esse fator
STRAT_SCALE = 0.003   # mapa estratégico: cobre até Saturno (~190k units)

# Cores de fallback por tipo (iauniverse define cor por planeta individualmente
# via ORBITAL_DATA; estas são usadas apenas se o planeta não tiver entrada lá)
PLANET_COLORS = {
    'ice_world':           (150, 200, 220),
    'terrestrial_iron':    (160, 100,  70),
    'terrestrial_silicon': (190, 170,  90),
    'lava_world':          (210,  70,  30),
    'gas_giant':           (255, 170, 102),
    'forest':              ( 43, 108, 255),
    'comet':               ( 80,  80,  70),   # núcleo escuro, gelo sujo
    'meteoroid_swarm':     (110, 100,  90),   # nuvem de fragmentos rochosos
}


@dataclass
class Planet:
    id:          int
    name:        str
    x:           float   # posição no mundo compartilhado (orbital e estratégico)
    y:           float
    radius_km:   float
    planet_type: str
    difficulty:  int
    minerals:    Dict
    owner_id:          int   = None
    health:            int   = 100
    angle:             float = 0.0
    semi_major_axis:   float = 0.0
    eccentricity:      float = 0.0
    period_days:       float = 365.0
    parent_name:       str   = None   # nome do planeta pai (satélites)

    def __post_init__(self):
        self.color = PLANET_COLORS.get(self.planet_type, (120, 120, 120))

        # visual_radius: radius_km/10 → Terra=637wu, Moon=174wu
        # Planeta nunca cabe na tela ao zoom padrão — superfície = horizonte curvo
        self.visual_radius    = max(100, min(4000, int(self.radius_km / 5)))
        self.strat_radius     = max(3,  min(14,  int(self.radius_km / 5000)))
        self.activation_range = max(1200, int(self.visual_radius * 4))

        # Horda: 5 ondas — 1-3 com 10 inimigos, 4-5 com 50 inimigos cada = 130 total
        self.horde_total         = 130
        self.horde_wave_size     = 10
        self.horde_wave_interval = 6.0   # ondas 1-3: 6s; ondas 4-5: 3s (dinâmico)
        self.reset_horde()

        # Reconquista — após conquista, inimigos retomam se player não defender
        self.reconquest_timer = 0.0    # contagem regressiva ativa quando > 0
        self.reconquest_delay = 600.0  # 10 minutos para reconquista

        # ── Órbita Kepleriana — dados do iauniverse (worldState.js) ─────────────
        self.parent_body = None   # preenchido em main.py para satélites
        data = ORBITAL_DATA.get(self.name)
        if data:
            # Converte a_km → world units usando a mesma âncora do iauniverse
            self.semi_major_axis = data["a_km"] / EARTH_ORBIT_KM * ORBITAL_SCALE
            self.eccentricity    = data["ecc"]
            self.period_days     = data["period"]
            self.parent_name     = data.get("parent", None)
            # Sobrescreve raio e cor com dados reais do iauniverse
            self.radius_km       = data["r_km"]
            self.color           = data["color"]
            self.visual_radius    = max(100, min(4000, int(self.radius_km / 5)))
            self.strat_radius     = max(3,  min(14,  int(self.radius_km / 5000)))
            self.activation_range = max(1200, int(self.visual_radius * 4))
        # Corpos cenário: sem horda, sem conquista
        self.is_conquerable        = self.planet_type not in ('comet', 'meteoroid_swarm')
        self.defenders             = 0    # aliados; decresce quando invasores chegam
        self.invasion_queue        = []   # planetas-fonte aguardando sua vez
        self.invasion_active_count = 0    # unidades da onda atual ainda vivas

        self.angle = random.uniform(0, 2 * math.pi)
        # Sync inicial x,y — satélites corrigidos em main.py após wiring do parent
        if self.semi_major_axis > 0 and self.parent_name is None:
            r = self.semi_major_axis * (1 - self.eccentricity ** 2) / \
                (1 + self.eccentricity * math.cos(self.angle))
            self.x = r * math.cos(self.angle)
            self.y = r * math.sin(self.angle)

    # ── Órbita ────────────────────────────────────────────────────────────────
    def update_orbit(self, dt: float):
        if self.period_days <= 0 or self.semi_major_axis <= 0:
            return
        omega = (2 * math.pi) / (self.period_days * 86400)
        self.angle += omega * dt * TIME_SCALE
        self.angle %= (2 * math.pi)
        r = self.semi_major_axis * (1 - self.eccentricity ** 2) / \
            (1 + self.eccentricity * math.cos(self.angle))
        if self.parent_body is not None:
            # Satélite: orbita ao redor do planeta pai
            self.x = self.parent_body.x + r * math.cos(self.angle)
            self.y = self.parent_body.y + r * math.sin(self.angle)
        else:
            # Planeta: orbita ao redor do Sol (0,0)
            self.x = r * math.cos(self.angle)
            self.y = r * math.sin(self.angle)

    # ── Horda ─────────────────────────────────────────────────────────────────
    def reset_horde(self):
        self.horde_spawned  = 0
        self.horde_timer    = self.horde_wave_interval
        self.conquered      = False

    def update_reconquest(self, dt) -> bool:
        """Retorna True se o planeta foi reconquistado pelos inimigos."""
        if not self.conquered or self.reconquest_timer <= 0:
            return False
        self.reconquest_timer -= dt
        if self.reconquest_timer <= 0:
            self.reconquest_timer = 0.0
            self.conquered        = False
            self.reset_horde()
            return True
        return False

    @staticmethod
    def _wave_idx(spawned):
        """Retorna o índice da onda (1-5) baseado em quantos já foram spawnados."""
        if spawned < 10:  return 1
        if spawned < 20:  return 2
        if spawned < 30:  return 3
        if spawned < 80:  return 4
        return 5

    def update_horde(self, dt, enemies, bullets_group, EnemyClass):
        if not self.is_conquerable:
            return
        if self.horde_spawned >= self.horde_total:
            return

        # Ondas 4-5 spwnam mais rápido (3s) para criar pressão crescente
        interval = 3.0 if self.horde_spawned >= 30 else self.horde_wave_interval

        self.horde_timer += dt
        if self.horde_timer < interval:
            return
        self.horde_timer = 0

        count    = min(self.horde_wave_size, self.horde_total - self.horde_spawned)
        wave_idx = self._wave_idx(self.horde_spawned)
        # Spawn seguro: pelo menos 20% além da superfície
        spawn_r  = self.visual_radius + max(150, int(self.visual_radius * 0.25))

        if wave_idx == 3:
            # Formação V: grupos de 5 (1 líder + 4 seguidores)
            groups = count // 5
            for _ in range(groups):
                ga = random.uniform(0, 2 * math.pi)
                gx = self.x + math.cos(ga) * spawn_r
                gy = self.y + math.sin(ga) * spawn_r
                leader = EnemyClass(gx, gy, bullets_group, wave=3,
                                    formation_leader=None, formation_index=-1)
                enemies.add(leader)
                for fi in range(4):
                    enemies.add(EnemyClass(
                        gx + random.uniform(-25, 25),
                        gy + random.uniform(-25, 25),
                        bullets_group, wave=3,
                        formation_leader=leader, formation_index=fi))
            for _ in range(count % 5):
                a = random.uniform(0, 2 * math.pi)
                enemies.add(EnemyClass(
                    self.x + math.cos(a) * spawn_r,
                    self.y + math.sin(a) * spawn_r,
                    bullets_group, wave=3))

        elif wave_idx == 5:
            # Defensores orbitais em anéis — formation_index define qual anel (0,1,2)
            base_offset = self.horde_spawned - 80
            for i in range(count):
                ring = min((base_offset + i) // 17, 2)
                a    = random.uniform(0, 2 * math.pi)
                enemies.add(EnemyClass(
                    self.x + math.cos(a) * spawn_r,
                    self.y + math.sin(a) * spawn_r,
                    bullets_group, wave=5,
                    formation_index=ring,
                    planet_center=self, planet_radius=self.visual_radius))

        else:
            # Ondas 1 (normal), 2 (blindada), 4 (esquivadora)
            for _ in range(count):
                a = random.uniform(0, 2 * math.pi)
                enemies.add(EnemyClass(
                    self.x + math.cos(a) * spawn_r,
                    self.y + math.sin(a) * spawn_r,
                    bullets_group, wave=wave_idx))

        self.horde_spawned += count
        print(f"[ONDA {wave_idx}] {self.name}: {self.horde_spawned}/{self.horde_total}")

    @property
    def horde_done(self):
        if not self.is_conquerable:
            return True
        return self.horde_spawned >= self.horde_total

    # ── Posicionamento estratégico (relativo ao player) ───────────────────────
    def screen_pos_strategic(self, screen_w, screen_h, ref_x=0.0, ref_y=0.0, scale=None):
        """Posição em pixels no mapa estratégico, centrado no ponto ref (player)."""
        s  = STRAT_SCALE if scale is None else scale
        sx = int((self.x - ref_x) * s + screen_w / 2)
        sy = int((self.y - ref_y) * s + screen_h / 2)
        return sx, sy

    # ── Desenho: mapa estratégico ─────────────────────────────────────────────
    def draw_strategic(self, screen, screen_w, screen_h,
                       ref_x=0.0, ref_y=0.0, is_selected=False, scale=None):
        sx, sy = self.screen_pos_strategic(screen_w, screen_h, ref_x, ref_y, scale=scale)

        # Calcula zoom relativo para escalar o raio visual
        s    = STRAT_SCALE if scale is None else scale
        zoom = s / STRAT_SCALE
        sr   = max(3, int(self.strat_radius * zoom))

        # Fora da tela → skip
        if sx < -sr - 10 or sx > screen_w + sr + 10:
            return
        if sy < -sr - 10 or sy > screen_h + sr + 10:
            return

        # Anel de seleção
        if is_selected:
            pygame.draw.circle(screen, (255, 255, 80), (sx, sy), sr + max(4, int(10 * zoom)), 2)

        # Conquista: cor dourada
        draw_color = (255, 215, 0) if self.conquered else self.color
        pygame.draw.circle(screen, draw_color, (sx, sy), sr)
        pygame.draw.circle(screen, (255, 255, 255), (sx, sy), sr, 1)

        # Nome — só mostra quando o planeta é grande o suficiente
        if sr >= 4:
            font  = pygame.font.Font(None, max(12, int(17 * zoom)))
            label = self.name if not self.conquered else f"{self.name} ✓"
            txt   = font.render(label, True, (220, 220, 220))
            lx = max(2, min(screen_w - txt.get_width() - 2, sx - txt.get_width() // 2))
            ly = sy + sr + 3
            if -4 < ly < screen_h + 10:
                bg = pygame.Surface((txt.get_width() + 4, txt.get_height() + 2), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 150))
                screen.blit(bg, (lx - 2, ly - 1))
                screen.blit(txt, (lx, ly))

    def draw_strategic_info(self, screen, screen_w, screen_h):
        """Painel lateral com detalhes do planeta selecionado."""
        px, py = screen_w - 290, 60
        lh     = 22
        ft     = pygame.font.Font(None, 24)
        fs     = pygame.font.Font(None, 19)

        # Fundo do painel
        panel_h = 40 + 9 * lh
        pygame.draw.rect(screen, (15, 15, 35),
                         (px - 10, py - 10, 285, panel_h), border_radius=8)
        pygame.draw.rect(screen, (70, 70, 110),
                         (px - 10, py - 10, 285, panel_h), 1, border_radius=8)

        def line(text, color=(180, 180, 200)):
            nonlocal py
            screen.blit(fs.render(text, True, color), (px, py))
            py += lh

        screen.blit(ft.render(self.name, True, self.color), (px, py)); py += lh + 4
        line(f"Tipo:        {self.planet_type}")
        line(f"Raio:        {self.radius_km:,.0f} km")
        line(f"Dificuldade: {'I' * self.difficulty}", (255, 100, 100))
        line(f"Horda:       {self.horde_total} inimigos", (255, 180, 80))
        has_gold = 'gold' in self.minerals or 'platinum' in self.minerals
        gold_txt = "Ouro: SIM" if has_gold else "Ouro: nao"
        gold_cor = (255, 215, 0) if has_gold else (120, 120, 120)
        line(gold_txt, gold_cor)
        if self.conquered:
            line("-- CONQUISTADO --", (80, 255, 80))
        line("ENTER: fechar mapa / voar ate la", (100, 200, 100))

    # ── Desenho: combate orbital ───────────────────────────────────────────────
    def draw_orbital(self, screen, camera):
        """Planeta no modo orbital — tamanho e posição respeitam o zoom."""
        sr = max(2, int(self.visual_radius * camera.zoom))
        sx, sy = camera.world_to_screen(self.x, self.y)

        sw, sh = screen.get_width(), screen.get_height()
        margin = sr + 400
        if sx + sr < -margin or sx - sr > sw + margin:
            return
        if sy + sr < -margin or sy - sr > sh + margin:
            return

        # Atmosfera — proporcional ao raio do planeta na tela (evita anel gigante)
        if sr >= 4:
            atmo = tuple(min(255, c + 40) for c in self.color)
            for g in range(3):
                # anel fino: +12%, +8%, +4% do raio do planeta
                r_atmo = sr + max(1, int(sr * (0.12 - g * 0.04)))
                w_atmo = max(1, int(sr * (0.06 - g * 0.015)))
                alpha  = tuple(max(0, c - g * 25) for c in atmo)
                pygame.draw.circle(screen, alpha, (sx, sy), r_atmo, w_atmo)

        # Corpo
        pygame.draw.circle(screen, self.color, (sx, sy), sr)

        # Detalhes de superfície (só quando visível em tamanho razoável)
        dark = tuple(max(0, c - 70) for c in self.color)
        if sr >= 8:
            if self.planet_type == 'gas_giant':
                for i in range(7):
                    oy = -sr + i * (sr * 2 // 7)
                    hw = int((sr ** 2 - oy ** 2) ** 0.5) if abs(oy) < sr else 0
                    if hw > 0 and i % 2 == 0:
                        pygame.draw.line(screen, dark, (sx - hw, sy + oy), (sx + hw, sy + oy),
                                         max(1, int(4 * camera.zoom)))
            else:
                for ci in range(self.difficulty + 3):
                    a   = ci * 0.9 + 0.3
                    cr  = max(2, sr // 10)
                    cx_ = sx + int(math.cos(a) * sr * 0.45)
                    cy_ = sy + int(math.sin(a) * sr * 0.45)
                    pygame.draw.circle(screen, dark, (cx_, cy_), cr, max(1, cr // 3))

        # Conquista: brilho dourado na borda
        border_color = (255, 215, 0) if self.conquered else (255, 255, 255)
        pygame.draw.circle(screen, border_color, (sx, sy), sr, max(1, min(3, int(2 * camera.zoom))))

        # Label — só aparece quando o planeta é grande o suficiente na tela
        if sr >= 6:
            label_y = sy - sr - 28
            if -40 < label_y < sh + 10:
                font = pygame.font.Font(None, max(12, int(20 * camera.zoom)))
                if self.is_conquerable:
                    status = "CONQUISTADO" if self.conquered else f"Horda {self.horde_spawned}/{self.horde_total}"
                    txt = font.render(f"{self.name}  |  {status}", True, (220, 220, 220))
                else:
                    txt = font.render(self.name, True, (150, 150, 130))
                screen.blit(txt, (sx - txt.get_width() // 2, label_y))

    # ── Utilitários ───────────────────────────────────────────────────────────
    def check_distance(self, x, y):
        return math.hypot(self.x - x, self.y - y)

    def get_mineral_value(self):
        return sum(self.minerals.values())


# ── Tipos de planeta ──────────────────────────────────────────────────────────
PLANET_TYPES = {
    'ice_world': {
        'radius_km':    1800,
        'minerals':     {'water_ice': 150, 'helium3': 40},
        'difficulty':   1,
        'base_enemies': 8,
    },
    'terrestrial_iron': {
        'radius_km':    5500,
        'minerals':     {'iron': 120, 'nickel': 50, 'platinum': 10},
        'difficulty':   2,
        'base_enemies': 12,
    },
    'terrestrial_silicon': {
        'radius_km':    6000,
        'minerals':     {'silicon': 100, 'rare_earth': 30},
        'difficulty':   3,
        'base_enemies': 18,
    },
    'lava_world': {
        'radius_km':    6051,    # Venus-like (real: 6051 km)
        'minerals':     {'platinum': 80, 'rare_earth': 50, 'gold': 30},
        'difficulty':   5,
        'base_enemies': 30,
    },
    'gas_giant': {
        'radius_km':    69911,   # Jupiter-like (real: 69 911 km)
        'minerals':     {'helium3': 200, 'hydrogen': 300},
        'difficulty':   4,
        'base_enemies': 25,
    },
    'forest': {
        'radius_km':    6371,
        'minerals':     {'organic': 100, 'silicon': 40},
        'difficulty':   2,
        'base_enemies': 10,
    },
    'comet': {
        'radius_km':    5,
        'minerals':     {'water_ice': 80, 'dust': 20},
        'difficulty':   3,
        'base_enemies': 15,
    },
    'meteoroid_swarm': {
        'radius_km':    100,
        'minerals':     {'iron': 50, 'silicon': 35},
        'difficulty':   3,
        'base_enemies': 20,
    },
}
