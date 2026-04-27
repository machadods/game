import pygame
import random

class StarField:
    """Fundo espacial com estrelas em múltiplas camadas de paralaxe."""

    # Cada camada tem: fator de paralaxe, quantidade de estrelas, tamanho, brilho
    _LAYER_DEFS = [
        {"factor": 0.08, "mult": 3.0, "size": 1, "brightness": (80,  160)},
        {"factor": 0.25, "mult": 1.5, "size": 1, "brightness": (140, 210)},
        {"factor": 0.55, "mult": 0.8, "size": 2, "brightness": (190, 255)},
    ]

    def __init__(self, world_width=10000, world_height=10000, density=0.05):
        self.layers = []
        base_count = int(400 * density / 0.05)  # ~400 estrelas na densidade padrão

        for cfg in self._LAYER_DEFS:
            f = cfg["factor"]
            count = int(base_count * cfg["mult"])

            # Área visível no espaço de estrelas é mundo * fator + tela.
            # Geramos um pouco maior para nunca ter bordas vazias.
            rx = world_width  * f + 1200
            ry = world_height * f + 900

            stars = [
                (
                    random.uniform(-rx / 2, rx / 2),
                    random.uniform(-ry / 2, ry / 2),
                    cfg["size"],
                    random.randint(*cfg["brightness"]),
                )
                for _ in range(count)
            ]
            self.layers.append({"stars": stars, "factor": f})

    def draw(self, screen, camera_x, camera_y, width, height):
        """
        camera_x / camera_y = camera.camera.x / .y  (offset negativo do mundo)
        Estrelas com fator baixo se movem menos → parecem mais distantes.
        """
        for layer in self.layers:
            f = layer["factor"]
            # Offset reduzido pelo fator de paralaxe
            ox = camera_x * f
            oy = camera_y * f

            for (sx, sy, size, brightness) in layer["stars"]:
                screen_x = int(sx + ox)
                screen_y = int(sy + oy)

                if -size <= screen_x <= width + size and -size <= screen_y <= height + size:
                    color = (brightness, brightness, brightness)
                    if size <= 1:
                        screen.set_at((screen_x, screen_y), color)
                    else:
                        pygame.draw.circle(screen, color, (screen_x, screen_y), size)
