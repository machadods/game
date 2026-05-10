# Game Zero

Jogo espacial single-player desenvolvido em Python + Pygame.
Pilote uma nave no sistema solar, enfrente hordas inimigas, colete ouro e conquiste planetas.

---

## Como Rodar

**Requisitos:** Python 3.10+ e Pygame

```bash
pip install pygame
python main.py
```

---

## Controles

| Ação | Controle |
|---|---|
| Mover nave | WASD ou setas |
| Atirar | Clique esquerdo do mouse |
| Fogo rápido | Clique direito (segurado) — requer ≥ 10 ouro |
| Mapa estratégico | M |
| Selecionar planeta no mapa | Clique esquerdo |
| Dobra Temporal | F (orbital) ou ENTER (no mapa) |
| Reiniciar | R (tela de Game Over) |
| Sair | ESC |

---

## Mecânicas

### Mundo e Navegação
- Universo de **160 000 × 160 000 unidades de mundo** com câmera suave que segue o jogador
- **Zona Segura** na origem (raio 3 000 u) — nenhuma horda é ativada enquanto o jogador estiver dentro
- **Mapa Estratégico** (tecla M): visão zoom-out do sistema solar completo; clique em um planeta para selecioná-lo
- Janela **redimensionável e maximizável** com renderização em resolução nativa (sem borrão)

### Ouro
- Única moeda do jogo
- Fontes: moedas que orbitam cada planeta + **coin dropada por cada nave inimiga abatida**
- Quantidade de moedas por planeta é proporcional à dificuldade

### Combate
- **Tiro normal** (clique esquerdo): dispara um projétil na direção do cursor
- **Fogo rápido** (clique direito segurado): requer ≥ 10 ouro — dispara continuamente a cada 0,08 s

### Dobra Temporal
- Requer **50 ouro**
- Teletransporta a nave para o raio de ativação do planeta selecionado no mapa
- Ativada com **F** na tela orbital ou **ENTER** no mapa estratégico

### Hordas
- Ao entrar no raio de ativação de um planeta, a horda começa a spawnar
- Tamanho: `difficulty × 15` inimigos (mínimo 50)
- Ondas de **10 inimigos a cada 6 segundos**
- Inimigos têm separação entre si e atiram automaticamente ao entrar em alcance (1 200 u)

### Conquista
- Planeta **conquistado** quando toda a horda é eliminada e não restam inimigos vivos
- **Recompensa: +1 vida**
- Conquistas são salvas no banco de dados

---

## Sistema Solar

8 planetas com posições fixas inspiradas no Sistema Solar real.
O Sol é representado pela Zona Segura na origem do mapa.

| Planeta | Tipo | Dificuldade | Distância aprox. |
|---|---|---|---|
| Mercurium | Lava | I | 11 700 u |
| Venus Nova | Lava | III | 23 000 u |
| Gaia | Floresta | II | 29 400 u |
| Marte | Ferro Terrestre | II | 40 200 u |
| Ceres | Gelo | I | 50 100 u |
| Jupiter | Gigante Gasoso | IIII | 62 700 u |
| Saturno | Gigante Gasoso | IIII | 72 600 u |
| Netuno | Gelo | IIIII | 79 400 u |

---

## HUD

- **Vidas**: círculos vermelhos no canto superior esquerdo
- **Inimigos abatidos** / **Ouro atual** no canto superior direito
- **Status do fogo rápido**: mostra disponibilidade ou ativação
- **Radar circular** (canto inferior esquerdo): exibe planetas, inimigos, ouro e balas ao redor do jogador
- **Seta de waypoint**: aponta para o planeta selecionado quando fora de vista
- **Mensagens temporárias** no centro da tela para eventos importantes

---

## Estrutura de Arquivos

```
game/
├── main.py              # GameEngine, loop principal, HUD, radar, eventos
├── settings.py          # Resolução base, FPS, tamanhos de sprite
├── game_data.db         # Banco SQLite (gerado automaticamente)
└── src/
    ├── player.py        # Nave do jogador — movimento, sprites, colisão
    ├── enemy.py         # Inimigo — perseguição, separação, tiro automático
    ├── bullet.py        # Projéteis do jogador e inimigos
    ├── coin.py          # Moedas de ouro coletáveis
    ├── camera.py        # Câmera com suavização e resize dinâmico
    ├── stars.py         # Fundo com parallax em 3 camadas
    ├── database.py      # SQLite — save/load de jogador e planetas
    └── celestial/
        └── planet.py    # Classe Planet, tipos, sistema de horda, renderização
```

---

## Persistência

- **Auto-save** a cada 30 segundos durante o jogo
- **Backup** automático do banco ao fechar
- Login com nome de piloto: cria conta nova ou carrega dados existentes

---

## Roadmap

- [ ] Modo GROUND — combate na superfície do planeta
- [ ] Novos tipos de inimigo com comportamentos distintos
- [ ] Bases orbitais e robôs mineradores
- [ ] Multiplayer LAN
- [ ] Sistema de facções entre planetas

---

**Autor:** Wagner Machado dos Santos
