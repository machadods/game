import pygame
import random
import math
from dataclasses import dataclass
from typing import Dict

# 1 unidade de mundo = 1 px na tela orbital
# No mapa estratégico, tudo é reduzido por esse fator
STRAT_SCALE = 0.004

PLANET_COLORS = {
    'ice_world':           (150, 200, 220),
    'terrestrial_iron':    (160, 100,  70),
    'terrestrial_silicon': (190, 170,  90),
    'lava_world':          (210,  70,  30),
    'gas_giant':           (220, 180,  90),
    'forest':              ( 70, 160,  80),
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
    owner_id:    int = None
    health:      int = 100

    def __post_init__(self):
        self.color = PLANET_COLORS.get(self.planet_type, (120, 120, 120))

        # Raio visual no orbital — escala 1:20 000
        self.visual_radius = max(200, min(1500, int(self.radius_km / 20)))

        # Raio visual no mapa estratégico (círculo pequeno)
        self.strat_radius = max(10, min(50, int(self.radius_km / 500)))

        # Distância para ativar a horda defensora
        self.activation_range = self.visual_radius + 2500

        # Horda
        self.horde_total         = max(50, self.difficulty * 15)
        self.horde_wave_size     = 10
        self.horde_wave_interval = 6.0
        self.reset_horde()

    # ── Horda ─────────────────────────────────────────────────────────────────
    def reset_horde(self):
        self.horde_spawned  = 0
        self.horde_timer    = self.horde_wave_interval  # primeira onda imediata
        self.conquered      = False

    def update_horde(self, dt, enemies, bullets_group, EnemyClass):
        if self.horde_spawned >= self.horde_total:
            return
        self.horde_timer += dt
        if self.horde_timer < self.horde_wave_interval:
            return
        self.horde_timer = 0
        wave = min(self.horde_wave_size, self.horde_total - self.horde_spawned)
        for _ in range(wave):
            angle   = random.uniform(0, 2 * math.pi)
            spawn_x = self.x + math.cos(angle) * (self.visual_radius + 80)
            spawn_y = self.y + math.sin(angle) * (self.visual_radius + 80)
            enemies.add(EnemyClass(spawn_x, spawn_y, bullets_group))
        self.horde_spawned += wave
        print(f"[HORDA] {self.name}: {self.horde_spawned}/{self.horde_total}")

    @property
    def horde_done(self):
        return self.horde_spawned >= self.horde_total

    # ── Posicionamento estratégico (relativo ao player) ───────────────────────
    def screen_pos_strategic(self, screen_w, screen_h, ref_x=0.0, ref_y=0.0):
        """Posição em pixels no mapa estratégico, centrado no ponto ref (player)."""
        sx = int((self.x - ref_x) * STRAT_SCALE + screen_w / 2)
        sy = int((self.y - ref_y) * STRAT_SCALE + screen_h / 2)
        return sx, sy

    # ── Desenho: mapa estratégico ─────────────────────────────────────────────
    def draw_strategic(self, screen, screen_w, screen_h,
                       ref_x=0.0, ref_y=0.0, is_selected=False):
        sx, sy = self.screen_pos_strategic(screen_w, screen_h, ref_x, ref_y)

        # Fora da tela → skip
        if sx < -60 or sx > screen_w + 60 or sy < -60 or sy > screen_h + 60:
            return

        # Anel de seleção
        if is_selected:
            pygame.draw.circle(screen, (255, 255, 80), (sx, sy), self.strat_radius + 10, 2)

        # Conquista: cor dourada
        draw_color = (255, 215, 0) if self.conquered else self.color
        pygame.draw.circle(screen, draw_color, (sx, sy), self.strat_radius)
        pygame.draw.circle(screen, (255, 255, 255), (sx, sy), self.strat_radius, 1)

        # Pontos de dificuldade
        for i in range(self.difficulty):
            dot_x = sx - (self.difficulty * 4) + i * 8 + 4
            pygame.draw.circle(screen, (255, 80, 80), (dot_x, sy - self.strat_radius - 7), 3)

        # Nome e dono
        font  = pygame.font.Font(None, 17)
        label = self.name if not self.conquered else f"{self.name} [CONQUISTADO]"
        txt   = font.render(label, True, (200, 200, 200))
        screen.blit(txt, (sx - txt.get_width() // 2, sy + self.strat_radius + 3))

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
        """Planeta gigante no fundo do combate orbital."""
        sr = self.visual_radius
        sx = int(self.x + camera.camera.x)
        sy = int(self.y + camera.camera.y)

        sw, sh = screen.get_width(), screen.get_height()
        if sx + sr < -300 or sx - sr > sw + 300:
            return
        if sy + sr < -300 or sy - sr > sh + 300:
            return

        # Atmosfera (camadas)
        atmo = tuple(min(255, c + 50) for c in self.color)
        for g in range(4):
            pygame.draw.circle(screen, tuple(max(0, c - g * 18) for c in atmo),
                               (sx, sy), sr + 40 - g * 9, 13 - g * 3)

        # Corpo
        pygame.draw.circle(screen, self.color, (sx, sy), sr)

        # Detalhes de superfície
        dark = tuple(max(0, c - 70) for c in self.color)
        if self.planet_type == 'gas_giant':
            for i in range(7):
                oy = -sr + i * (sr * 2 // 7)
                hw = int((sr ** 2 - oy ** 2) ** 0.5) if abs(oy) < sr else 0
                if hw > 0 and i % 2 == 0:
                    pygame.draw.line(screen, dark, (sx - hw, sy + oy), (sx + hw, sy + oy), 4)
        else:
            for ci in range(self.difficulty + 3):
                a  = ci * 0.9 + 0.3
                cr = max(8, sr // 10)
                cx_ = sx + int(math.cos(a) * sr * 0.45)
                cy_ = sy + int(math.sin(a) * sr * 0.45)
                pygame.draw.circle(screen, dark, (cx_, cy_), cr, 3)

        # Conquista: brilho dourado na borda
        border_color = (255, 215, 0) if self.conquered else (255, 255, 255)
        pygame.draw.circle(screen, border_color, (sx, sy), sr, 3)

        # Label acima (só se visível)
        label_y = sy - sr - 28
        if 0 < label_y < sh:
            font = pygame.font.Font(None, 20)
            status = "CONQUISTADO" if self.conquered else f"Horda {self.horde_spawned}/{self.horde_total}"
            txt = font.render(f"{self.name}  |  {status}", True, (220, 220, 220))
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
        'radius_km':    6500,
        'minerals':     {'platinum': 80, 'rare_earth': 50, 'gold': 30},
        'difficulty':   5,
        'base_enemies': 30,
    },
    'gas_giant': {
        'radius_km':    70000,
        'minerals':     {'helium3': 200, 'hydrogen': 300},
        'difficulty':   4,
        'base_enemies': 25,
    },
    'forest': {
        'radius_km':    4000,
        'minerals':     {'organic': 100, 'silicon': 40},
        'difficulty':   2,
        'base_enemies': 10,
    },
    
}
