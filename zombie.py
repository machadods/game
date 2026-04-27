import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Emoji Zombie")

font = pygame.font.SysFont("Segoe UI Emoji", 32)

# Player
player_x = WIDTH // 2
player_y = HEIGHT // 2
speed = 4
gold = 0

# Listas
zombies = []
bullets = []

# Classes
class Zombie:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 50
        self.speed = 1

    def update(self):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)

        if dist > 0:
            self.x += (dx/dist) * self.speed
            self.y += (dy/dist) * self.speed

    def draw(self):
        text = font.render("🧟", True, (0,255,0))
        screen.blit(text, (self.x, self.y))


class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.speed = 6
        dist = math.hypot(dx, dy)
        self.dx = dx/dist
        self.dy = dy/dist

    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self):
        text = font.render("🔴", True, (255,0,0))
        screen.blit(text, (self.x, self.y))


def spawn_zombie():
    side = random.choice(["top","bottom","left","right"])
    if side == "top":
        return Zombie(random.randint(0, WIDTH), -50)
    if side == "bottom":
        return Zombie(random.randint(0, WIDTH), HEIGHT+50)
    if side == "left":
        return Zombie(-50, random.randint(0, HEIGHT))
    if side == "right":
        return Zombie(WIDTH+50, random.randint(0, HEIGHT))


clock = pygame.time.Clock()
running = True

spawn_timer = 0

while running:
    screen.fill((10,10,20))

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            bullets.append(Bullet(player_x, player_y, mx-player_x, my-player_y))

    # Movimento
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: player_y -= speed
    if keys[pygame.K_s]: player_y += speed
    if keys[pygame.K_a]: player_x -= speed
    if keys[pygame.K_d]: player_x += speed

    # Spawn zumbi
    spawn_timer += 1
    if spawn_timer > 60:
        zombies.append(spawn_zombie())
        spawn_timer = 0

    # Update zumbis
    for z in zombies:
        z.update()

    # Update tiros
    for b in bullets:
        b.update()

    # Colisão
    for z in zombies[:]:
        for b in bullets[:]:
            if abs(z.x - b.x) < 20 and abs(z.y - b.y) < 20:
                z.hp -= 25
                bullets.remove(b)
                if z.hp <= 0:
                    zombies.remove(z)
                    gold += 1

    # Draw player
    player_text = font.render("🚀", True, (255,255,255))
    screen.blit(player_text, (player_x, player_y))

    # Draw zumbis
    for z in zombies:
        z.draw()

    # Draw tiros
    for b in bullets:
        b.draw()

    # UI
    ui = font.render(f"💰 {gold}", True, (255,255,0))
    screen.blit(ui, (10,10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()