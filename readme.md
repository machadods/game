# Game Zero — Space Combat Sandbox

Jogo espacial single-player em Python + Pygame.
Pilote uma nave, explore 9 corpos celestes, enfrente 5 ondas de horda e domine o sistema solar.

---

## Como Rodar

**Requisitos:** Python 3.10+ e Pygame

```bash
pip install pygame
python main.py
```

---

## Mecânicas

| Mecânica | Descrição |
|----------|-----------|
| Universo aberto | 2 000 000 × 2 000 000 world units com câmera suave e zoom livre |
| Horda de 5 ondas | Cada planeta tem 130 inimigos em 5 ondas progressivas (normal → esquivador → patrol) |
| Economia de ouro | Colete moedas dropadas por inimigos para ativar habilidades e teleportes |
| Fogo rápido | Clique direito segurado com ≥ 10 ouro — rajada automática |
| Dano x2 | Com ≥ 100 ouro todos os tiros causam 2 de dano; consome 10 ouro a cada 100 disparos |
| Dobra Temporal | Teleporte para o planeta selecionado com intercept orbital (custo: 50 ouro, tecla F) |
| Mapa Estratégico | Visão zoom-out do sistema solar (tecla M) com seleção de destino |
| Radar circular | 10 000 wu de alcance — mostra planetas, inimigos, ouro e balas próximos em tempo real |
| Pouso (GROUND) | Após limpar a horda, pousa no planeta (tecla L) para conquistá-lo |
| Reconquista | Planetas conquistados são retomados pelos inimigos após 10 minutos sem defesa |
| Persistência SQLite | Save automático a cada 30 s + backup ao fechar |

---

## Sistema Solar

| Corpo | Tipo | Raio (km) | Dificuldade | Órbita |
|-------|------|-----------|-------------|--------|
| Mercurium | Lava | 2 440 | I | 57,9 M km do Sol |
| Venus Nova | Lava | 6 051 | III | 108,2 M km do Sol |
| Terra | Floresta | 6 371 | II | 149,6 M km do Sol |
| Moon | Gelo | 1 737 | I | satélite da Terra |
| Marte | Ferro Terrestre | 3 390 | II | 227,9 M km do Sol |
| Ceres | Gelo | 473 | I | 413,7 M km do Sol |
| Jupiter | Gigante Gasoso | 69 911 | IV | 778,5 M km do Sol |
| Saturno | Gigante Gasoso | 58 232 | IV | 1 433 M km do Sol |
| Netuno | Gelo | 24 622 | V | 4 495 M km do Sol |

> O **Sol** ocupa o centro do mapa. A **Zona Segura** (raio 18 000 wu) ao redor do Sol não gera hordas.

---

## Ondas de Horda

| Onda | Inimigos | Comportamento | HP |
|------|----------|---------------|----|
| 1 | 10 | Normal + strafing sinusoidal | 3 |
| 2 | 10 | Blindado (igual ao 1, mais HP) | 6 |
| 3 | 10 | Formação V (1 líder + 4 seguidores) | 9 |
| 4 | 50 | Esquivador — desvia de balas em tempo real | 12 |
| 5 | 50 | Patrol entre waypoints; foge apenas se player < 1 400 wu | 15 |

---

## Controles

| Ação | Controle |
|------|----------|
| Mover nave | WASD / Setas |
| Atirar (único) | Clique esquerdo |
| Fogo rápido | Clique direito (segurar) — precisa ≥ 10 ouro |
| Mapa estratégico | M |
| Selecionar planeta no mapa | Clique esquerdo |
| Dobra Temporal | F (orbital ou no mapa) |
| Pousar no planeta | L (na atmosfera, horda limpa) |
| Reset de zoom | Q |
| Sair | ESC |

---

## Estrutura de Arquivos

```
game/
├── main.py              # GameEngine, HUD, radar, loop principal
├── settings.py          # Constantes globais: tamanhos, escalas, dados orbitais
├── src/
│   ├── player.py        # Nave do jogador — movimento, sprites, colisão
│   ├── enemy.py         # IA inimiga — 5 tipos de comportamento + tiro preditivo
│   ├── bullet.py        # Projéteis do jogador e inimigos
│   ├── coin.py          # Moedas de ouro coletáveis (orbitam planetas)
│   ├── camera.py        # Câmera com zoom suave e world↔screen transform
│   ├── stars.py         # StarField parallax
│   ├── database.py      # SQLite — save/load de jogador e planetas
│   └── celestial/
│       └── planet.py    # Classe Planet, tipos, horda, órbita Kepleriana
└── assets/
    ├── up/down/left/right.png   # Sprites da nave (4 direções)
    └── enemy/                   # Sprites dos inimigos (4 direções)
```

---

## Roadmap

- [ ] Modo GROUND expandido — combate na superfície com terreno procedural
- [ ] Asteroides e cinturão de detritos entre Marte e Júpiter
- [ ] Luas adicionais (Io, Europa, Titã…)
- [ ] Construção de bases orbitais e robôs mineradores
- [ ] Sistema de facções e diplomacia
- [ ] Multiplayer LAN

---

**Autor:** Wagner Machado dos Santos  
**GitHub:** [github.com/machadods](https://github.com/machadods)
