import pygame

ZOOM_MIN    = 0.003   # sistema solar completo visível
ZOOM_MAX    = 50.0    # combate ultra-close (superfície do planeta)
ZOOM_START  = 1.0     # padrão: zoom 1:1
ZOOM_SMOOTH = 0.10

class Camera:
    def __init__(self, width, height):
        self.width   = width
        self.height  = height
        self.zoom        = ZOOM_START
        self.zoom_target = ZOOM_START
        self._cx = 0.0
        self._cy = 0.0
        self.camera = pygame.Rect(0, 0, width, height)

    # ── Transforms ────────────────────────────────────────────────────────────
    def world_to_screen(self, wx, wy):
        """Converte posição world → pixel de tela (respeitando zoom)."""
        sx = int((wx - self._cx) * self.zoom + self.width  * 0.5)
        sy = int((wy - self._cy) * self.zoom + self.height * 0.5)
        return sx, sy

    def screen_to_world(self, sx, sy):
        """Converte pixel de tela → posição world."""
        wx = (sx - self.width  * 0.5) / self.zoom + self._cx
        wy = (sy - self.height * 0.5) / self.zoom + self._cy
        return wx, wy

    def apply(self, entity):
        """Retorna o rect de destino (posição) para blit — zoom-aware."""
        sx, sy = self.world_to_screen(entity.rect.centerx, entity.rect.centery)
        r = entity.image.get_rect()
        r.center = (sx, sy)
        return r

    def scale_img(self, img):
        """Escala uma surface pelo zoom atual. Retorna a mesma se zoom ≈ 1."""
        if abs(self.zoom - 1.0) < 0.02:
            return img
        w = max(2, round(img.get_width()  * self.zoom))
        h = max(2, round(img.get_height() * self.zoom))
        return pygame.transform.scale(img, (w, h))

    # ── Zoom ──────────────────────────────────────────────────────────────────
    def zoom_step(self, direction):
        factor = 1.25 if direction > 0 else (1.0 / 1.25)
        self.zoom_target = max(ZOOM_MIN, min(ZOOM_MAX, self.zoom_target * factor))

    def zoom_label(self):
        if self.zoom >= 1.0:
            return f"x{self.zoom:.1f}"
        wu = int(1.0 / self.zoom)
        return f"1:{wu}"

    # ── Update ────────────────────────────────────────────────────────────────
    def resize(self, width, height):
        self.width  = width
        self.height = height

    def update(self, target):
        self._cx = float(target.rect.centerx)
        self._cy = float(target.rect.centery)
        # Interpolação suave do zoom
        self.zoom += (self.zoom_target - self.zoom) * ZOOM_SMOOTH
        # Atualiza rect legado para star_field.draw (sem zoom — paralaxe flat)
        self.camera.x = int(-self._cx + self.width  * 0.5)
        self.camera.y = int(-self._cy + self.height * 0.5)
