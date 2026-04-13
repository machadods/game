#C:\Users\wagner62215896\Documents\main.py


import pygame
import random
from settings import WIDTH, HEIGHT, FPS
from src.player import Player
from src.coin import Coin
from src.camera import Camera


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TESTE")
clock = pygame.time.Clock()
running = True

# 1. INSTANCIA A CÂMERA
camera = Camera(WIDTH, HEIGHT)

#Grupo de jogadores
players = pygame.sprite.Group()

#Grupo de coins
coins =pygame.sprite.Group()

player = Player("player_1")
players.add(player)


for a in range(50):
    x_aleatorio = random.randint(-5000, 5000)
    y_aleatorio = random.randint(-5000, 5000)
    coin = Coin(x_aleatorio, y_aleatorio)
    coins.add(coin)

while running:
    delta = clock.tick(FPS)/1000

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                running = False


    # ATUALIZAÇÃO DE LÓGICA
    players.update(delta)
    coins.update()
    
    # 3. ATUALIZA A POSIÇÃO DA CÂMERA BASEADA NO PLAYER
    camera.update(player)

    colisao = pygame.sprite.spritecollide(player,coins,True)
    if colisao:
        print(f'Capturou a moeda')
        
    # DESENHO (A ordem importa!)
    screen.fill((45, 156, 200)) # Fundo

    for coin in coins:
        screen.blit(coin.image, camera.apply(coin))
    
    # Desenha o player
    screen.blit(player.image, camera.apply(player))
    
    # --- DESENHO DO RADAR (No final do bloco de desenho no main.py) ---
    radar_pos = (150, 150) # Posição do centro do radar na tela
    radar_raio = 100       # Tamanho do círculo do radar
    escala_radar = 0.05    # O quanto o radar "enxerga" longe (5% da distância real)

    # Desenha o fundo do radar (Círculo preto transparente)
    radar_surface = pygame.Surface((radar_raio*2, radar_raio*2), pygame.SRCALPHA)
    pygame.draw.circle(radar_surface, (0, 0, 0, 150), (radar_raio, radar_raio), radar_raio)
    screen.blit(radar_surface, (radar_pos[0] - radar_raio, radar_pos[1] - radar_raio))
    pygame.draw.circle(screen, (255, 255, 255), radar_pos, radar_raio, 2) # Borda

    for coin in coins:
        # Calcula a distância do minério em relação ao player
        rel_x = (coin.rect.centerx - player.rect.centerx) * escala_radar
        rel_y = (coin.rect.centery - player.rect.centery) * escala_radar

        # Verifica se o ponto está dentro do círculo do radar (Pitágoras)
        distancia = (rel_x**2 + rel_y**2)**0.5
        if distancia < radar_raio:
            ponto_x = int(radar_pos[0] + rel_x)
            ponto_y = int(radar_pos[1] + rel_y)
            # Desenha o minério como um pontinho amarelo no radar
            pygame.draw.circle(screen, (255, 215, 0), (ponto_x, ponto_y), 2)

    # Desenha um pontinho branco no centro do radar (Representa VOCÊ)
    pygame.draw.circle(screen, (255, 255, 255), radar_pos, 3)

    pygame.display.flip()

pygame.quit()