import pygame
import random
import math
import os
from settings import ENEMY_SIZE
from src.bullet import Bullet

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# V-formation: 4 offsets para seguidores (espaço local x=dir, y=sentido ao player)
V_OFFSETS = [
    (-80, -50),   # asa esquerda frontal
    ( 80, -50),   # asa direita frontal
    (-50,  45),   # asa esquerda traseira
    ( 50,  45),   # asa direita traseira
]

# Raios de órbita para as 3 camadas da onda 5 (multiplicador de visual_radius)
RING_RADII = [2.0, 2.6, 3.2]
# Direção de órbita por anel (alterna para efeito visual)
RING_DIRS  = [1, -1, 1]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, bullets_group, wave=1,
                 formation_leader=None, formation_index=0,
                 planet_center=None, planet_radius=0):
        super().__init__()

        self.wave             = wave
        self.formation_leader = formation_leader
        self.formation_index  = formation_index
        self.planet_center    = planet_center
        self.planet_radius    = planet_radius
        self.bullets_group    = bullets_group

        # HP: onda 1=1, onda 2=2, ondas 3/4/5=4
        self.lives     = {1: 1, 2: 2}.get(wave, 4)
        self.max_lives = self.lives

        # Velocidade por onda
        self.speed = {1: 200, 2: 170, 3: 215, 4: 240, 5: 180}.get(wave, 200)

        # Tiro
        self.shoot_cooldown  = random.uniform(0, 1.5)
        self.shoot_delay     = {1: 1.0, 2: 1.1, 3: 0.95, 4: 0.8, 5: 0.30}.get(wave, 1.0)
        self.shoot_range     = 1400

        # Mira preditiva — rastreia posição anterior do player
        self._last_player_pos = None

        # Esquiva (wave 4 e 5)
        self.dodge_vel      = pygame.math.Vector2(0, 0)
        self.dodge_timer    = 0.0
        self.dodge_cooldown = 0.0

        # Onda 5 — raio de confinamento reduzido + patrol
        self.flee_max_radius = planet_radius * 2.2 if wave == 5 else 0.0
        self.patrol_target   = None
        self.patrol_cd       = 0.0

        # Modo invasão — viaja de um planeta origem até o planeta alvo
        self.invasion_target  = None   # Planet a alcançar; None = comportamento normal
        self._arrived_at      = None   # Setado ao chegar; processado em main.py
        self.invasion_conquest = None  # Tag permanente: planeta que este inimigo ataca

        # Sprites
        self.sprites = {}
        for img in ['assets/enemy/up.png', 'assets/enemy/down.png',
                    'assets/enemy/left.png', 'assets/enemy/right.png']:
            path = os.path.join(BASE_DIR, img)
            try:
                loaded = pygame.image.load(path).convert_alpha()
                spr    = pygame.transform.scale(loaded, ENEMY_SIZE)
            except Exception:
                spr = pygame.Surface(ENEMY_SIZE, pygame.SRCALPHA)
                spr.fill((180, 60, 60, 255))
            self.sprites[img] = spr

        up   = self.sprites['assets/enemy/up.png']
        down = self.sprites['assets/enemy/down.png']
        self.sprites['assets/enemy/up_left.png']    = pygame.transform.rotate(up,    45)
        self.sprites['assets/enemy/up_right.png']   = pygame.transform.rotate(up,   -45)
        self.sprites['assets/enemy/down_left.png']  = pygame.transform.rotate(down, -45)
        self.sprites['assets/enemy/down_right.png'] = pygame.transform.rotate(down,  45)

        self.base_image = self.sprites['assets/enemy/up.png']
        self.image      = self.base_image
        self.rect       = self.image.get_rect()
        self.radius     = self.rect.width // 4

        self.world_pos   = pygame.math.Vector2(x, y)
        self.rect.center = (int(x), int(y))

    # ── Update principal ───────────────────────────────────────────────────────
    def update(self, player, delta, enemies):
        # Tropa invasora em trânsito — viaja até o alvo, atira se player aparecer
        if self.invasion_target is not None:
            self._update_invasion_travel(delta)
            self._update_shoot(player, delta)
            return

        if self.wave == 5:
            self._update_flee(player, delta)
            self._try_dodge()                 # foge E desvia de balas
        elif self.wave == 3 and self.formation_leader is not None:
            self._update_formation_follower(player, delta, enemies)
        elif self.wave == 4:
            self._update_dodger(player, delta, enemies)
        else:
            self._update_normal(player, delta, enemies)
        self._update_shoot(player, delta)

    # ── Invasão: viagem direta ao planeta alvo ────────────────────────────────
    def _update_invasion_travel(self, delta):
        """Move em linha reta rumo ao planeta conquiistado. Sem dobra — viagem real."""
        tx = self.invasion_target.x
        ty = self.invasion_target.y
        to_target = pygame.math.Vector2(tx - self.world_pos.x, ty - self.world_pos.y)
        dist = to_target.length()

        # Chegou dentro do raio de ativação do alvo
        if dist <= self.invasion_target.activation_range:
            self._arrived_at     = self.invasion_target
            self.invasion_target = None
            return

        move = to_target.normalize()
        self.world_pos += move * 260 * delta   # velocidade fixa de viagem
        self.rect.center = (int(self.world_pos.x), int(self.world_pos.y))
        self._rotate(move)

    # ── Movimento normal com strafing sinusoidal ───────────────────────────────
    def _update_normal(self, player, delta, enemies):
        d = player.world_pos - self.world_pos
        if d.length() == 0:
            return
        d_norm = d.normalize()

        # Strafing — cada inimigo tem fase única, cria movimento em S
        t    = pygame.time.get_ticks() * 0.0015 + id(self) * 0.0004
        perp = pygame.math.Vector2(-d_norm.y, d_norm.x)
        approach = d_norm + perp * math.sin(t) * 0.5

        sep   = self._separation(enemies)
        final = approach + sep * 1.5
        if final.length() > 0:
            final = final.normalize()

        self.world_pos += final * self.speed * delta
        self.rect.center = (int(self.world_pos.x), int(self.world_pos.y))
        self._rotate(final)

    # ── Formação V — seguidor mantém offset em relação ao líder ───────────────
    def _update_formation_follower(self, player, delta, enemies):
        if not self.formation_leader.alive():
            self._update_normal(player, delta, enemies)
            return

        ldr  = self.formation_leader
        to_p = player.world_pos - ldr.world_pos
        fwd  = to_p.normalize() if to_p.length() > 0 else pygame.math.Vector2(0, -1)
        rgt  = pygame.math.Vector2(fwd.y, -fwd.x)

        ox, oy = V_OFFSETS[self.formation_index]
        target = ldr.world_pos + rgt * ox - fwd * oy

        diff = target - self.world_pos
        if diff.length() > 4:
            move = diff.normalize() * self.speed * 1.8 * delta
            if move.length() > diff.length():
                move = diff
            self.world_pos += move

        self.rect.center = (int(self.world_pos.x), int(self.world_pos.y))
        dp = player.world_pos - self.world_pos
        if dp.length() > 0:
            self._rotate(dp.normalize())

    # ── Esquivador — desvia de balas + strafing ────────────────────────────────
    def _update_dodger(self, player, delta, enemies):
        self.dodge_timer    = max(0.0, self.dodge_timer    - delta)
        self.dodge_cooldown = max(0.0, self.dodge_cooldown - delta)

        if self.dodge_timer > 0:
            self.world_pos += self.dodge_vel * delta
        else:
            if self.dodge_cooldown <= 0:
                self._try_dodge()
            # Movimento com strafing agressivo
            d = player.world_pos - self.world_pos
            if d.length() == 0:
                return
            d_norm = d.normalize()
            t    = pygame.time.get_ticks() * 0.002 + id(self) * 0.0005
            perp = pygame.math.Vector2(-d_norm.y, d_norm.x)
            approach = d_norm + perp * math.sin(t) * 0.7   # strafing mais agressivo
            sep      = self._separation(enemies)
            final    = approach + sep * 1.5
            if final.length() > 0:
                final = final.normalize()
            self.world_pos += final * self.speed * delta

        self.rect.center = (int(self.world_pos.x), int(self.world_pos.y))
        dp = player.world_pos - self.world_pos
        if dp.length() > 0:
            self._rotate(dp.normalize())

    def _try_dodge(self):
        """Detecta bala incoming e desvia perpendicular."""
        for b in self.bullets_group:
            if getattr(b, 'owner', None) != 'player':
                continue
            to_self = self.world_pos - b.world_pos
            dist    = to_self.length()
            if dist > 700 or dist == 0:
                continue
            dot = to_self.normalize().dot(b.direction)
            if dot > 0.60:
                perp = pygame.math.Vector2(-b.direction.y, b.direction.x)
                if random.random() < 0.5:
                    perp = -perp
                spd = 500 if self.wave >= 4 else 420
                self.dodge_vel      = perp * spd
                self.dodge_timer    = 0.28
                self.dodge_cooldown = 0.5 if self.wave >= 4 else 0.8
                break

    # ── Onda 5 — patrol + fuga quando player se aproxima ─────────────────────
    def _update_flee(self, player, delta):
        """Patrulha waypoints ao redor do planeta; foge apenas quando player está próximo."""
        self.patrol_cd = max(0.0, self.patrol_cd - delta)

        dist_to_player = (player.world_pos - self.world_pos).length()
        flee_threshold = 1400  # foge só se player estiver nessa distância

        if dist_to_player < flee_threshold:
            # Fuga direta do player
            away = self.world_pos - player.world_pos
            move_dir = away.normalize() if away.length() > 0 else \
                pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        else:
            # Patrol: move em direção ao waypoint atual
            if self.patrol_target is None or self.patrol_cd <= 0:
                self._pick_patrol_target()
            to_target = self.patrol_target - self.world_pos
            if to_target.length() < 120:
                self._pick_patrol_target()
                to_target = self.patrol_target - self.world_pos
            move_dir = to_target.normalize() if to_target.length() > 0 else \
                pygame.math.Vector2(0, -1)

        # Confinamento ao raio do planeta
        if self.planet_center is not None and self.flee_max_radius > 0:
            to_center = pygame.math.Vector2(
                self.planet_center.x - self.world_pos.x,
                self.planet_center.y - self.world_pos.y,
            )
            if to_center.length() > self.flee_max_radius:
                pull = to_center.normalize() * 3.5
                combined = move_dir + pull
                move_dir = combined.normalize() if combined.length() > 0 else move_dir
                self.patrol_target = None   # força novo waypoint dentro do raio

        self.world_pos += move_dir * self.speed * delta
        self.rect.center = (int(self.world_pos.x), int(self.world_pos.y))
        if move_dir.length() > 0:
            self._rotate(move_dir)

    def _pick_patrol_target(self):
        """Escolhe um waypoint aleatório dentro do raio de confinamento."""
        if self.planet_center is not None and self.flee_max_radius > 0:
            angle = random.uniform(0, 2 * math.pi)
            min_r = max(self.planet_radius * 1.1, 200)
            max_r = self.flee_max_radius * 0.88
            dist  = random.uniform(min_r, max(min_r + 50, max_r))
            self.patrol_target = pygame.math.Vector2(
                self.planet_center.x + math.cos(angle) * dist,
                self.planet_center.y + math.sin(angle) * dist,
            )
        else:
            angle = random.uniform(0, 2 * math.pi)
            dist  = random.uniform(300, 700)
            self.patrol_target = self.world_pos + pygame.math.Vector2(
                math.cos(angle) * dist, math.sin(angle) * dist
            )
        self.patrol_cd = random.uniform(4.0, 9.0)

    # ── Tiro com mira preditiva ────────────────────────────────────────────────
    def _update_shoot(self, player, delta):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= delta

        # Atualiza rastreio de velocidade do player
        if self._last_player_pos is None:
            self._last_player_pos = pygame.math.Vector2(player.world_pos)

        player_vel = pygame.math.Vector2(0, 0)
        if delta > 0:
            player_vel = (player.world_pos - self._last_player_pos) / delta
        self._last_player_pos = pygame.math.Vector2(player.world_pos)

        if self.shoot_cooldown > 0:
            return
        # Onda 5 sempre atira (mesmo fugindo)

        dist = (player.world_pos - self.world_pos).length()
        if dist > self.shoot_range:
            return

        # Mira preditiva: calcula onde o player estará quando a bala chegar
        travel_time = dist / 400.0   # velocidade da bala = 400
        predicted   = player.world_pos + player_vel * travel_time * 0.8
        aim_vec     = predicted - self.world_pos

        if aim_vec.length() == 0:
            return
        direction = aim_vec.normalize()

        # Onda 5 dispara mais rápido e em cor diferente
        color = (255, 180, 0) if self.wave == 5 else (255, 0, 0)
        b = Bullet(self.world_pos + direction * 30, direction, color)
        b.owner = "enemy"
        self.bullets_group.add(b)
        self.shoot_cooldown = self.shoot_delay

    # ── Utilitários ───────────────────────────────────────────────────────────
    def _separation(self, enemies):
        sep = pygame.math.Vector2(0, 0)
        for other in enemies:
            if other is self:
                continue
            d = self.world_pos.distance_to(other.world_pos)
            if 0 < d < 80:
                sep += (self.world_pos - other.world_pos).normalize() * (80 - d) / 80
        return sep

    def _rotate(self, direction):
        angle      = direction.angle_to(pygame.math.Vector2(0, -1))
        self.image = pygame.transform.rotate(self.base_image, angle)
        self.rect  = self.image.get_rect(center=self.rect.center)
