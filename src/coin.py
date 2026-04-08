import pygame # Importa a bilbioteca Pygame para usar as ferramentas de jogo

# Cria a classe Coin que herda de Sprite (ganha podere de objetos de jogo)
class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y): # função que nasce a moeda, recebendo sua posição.
        super().__init__() # Ativa as funções internas da classe Sprite do pygame
        self.image = pygame.Surface((32,32)) 
        self.image.fill((255,215,0)) 
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.size = 32 # Define o tamanho da moeda ( 32 pixels de largura e altura)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA) # Cria a superficie da imagem com suporte a transparencia(SRCALPHA)

        # Define as cores em formato RGB (Vermelho, Verde, Azul)
        OURO = (255, 215, 0) # Cor amarela brilhante
        OURO_ESCURO = (184, 134,11) # Cor para dar efeito de borda/sombra

        # Calcula o ponto central do quadrado de 32x32 para desenha o circulo nas bordas
        centro = (self.size // 2, self.size // 2)

        # Define o raio (metade do tamanho) para o circulo encostar nas bordas
        raio = self.size //2

        # Desenha o círculo maior (borda escura) na imagem da moeda
        pygame.draw.circle(self.image, OURO_ESCURO, centro, raio)

        #Desenha o círculo menor (centro claro) para dar efeito de relevo
        pygame.draw.circle(self.image, OURO,  centro, raio - 2)

        # Cria o "rect" (retângulo de colisão e posição) baseado na imagem criada
        self.rect = self.image.get_rect()

        # define onde o canto superior esquerdo da moeda ficará na tela
        self.rect.topleft = (x,y)