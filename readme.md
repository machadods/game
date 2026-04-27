# Game Zero — Space Combat Sandbox

Jogo espacial single-player desenvolvido em Python com Pygame.
Pilote uma nave, explore 8 planetas, enfrente hordas e use a Dobra Temporal.

---

## Como Rodar Localmente

**Requisitos:** Python 3.10+ e Pygame

```bash
pip install pygame
python main.py
```

---

## Mecânicas

- **Universo aberto** — 160.000 × 160.000 unidades com câmera suave
- **8 planetas** com hordas de até 50+ inimigos cada
- **Economia de ouro** — colete moedas, ative fogo rápido, pague teleportes
- **Dobra Temporal** — teleporte instantâneo por 50 gold (tecla F)
- **Mapa Estratégico** — visão zoom-out (tecla M) com painel de planeta
- **Radar circular** — rastreia inimigos, gold, balas e planetas
- **Persistência SQLite** — save automático a cada 30s + backup ao fechar

## Planetas

| Planeta | Tipo | Dificuldade |
|---------|------|-------------|
| Mercurium | Lava | I |
| Venus Nova | Lava | III |
| Gaia | Floresta | II |
| Marte | Terrestre | II |
| Ceres | Gelo | I |
| Jupiter | Gigante gasoso | IV |
| Saturno | Gigante gasoso | IV |
| Netuno | Gelo | V |

## Controles

| Ação | Controle |
|------|----------|
| Mover nave | WASD / Setas |
| Atirar | Clique esquerdo |
| Fogo rápido | Clique direito (segurar, ≥10 gold) |
| Mapa estratégico | M |
| Dobra Temporal | F (orbital) / ENTER (mapa) |
| Sair | ESC |

---

## Estrutura

```
game/
├── main.py              # Loop principal e GameEngine
├── settings.py          # Resolução, FPS, tamanhos
├── src/
│   ├── player.py        # Nave do jogador
│   ├── enemy.py         # IA inimiga com separação (flocking)
│   ├── bullet.py        # Projéteis
│   ├── coin.py          # Ouro coletável
│   ├── camera.py        # Câmera com easing suave
│   ├── stars.py         # StarField parallax 3 camadas
│   ├── database.py      # SQLite — save/load de jogador e planetas
│   └── celestial/
│       └── planet.py    # Planetas, hordas e tipos
└── assets/
    ├── up/down/left/right.png   # Sprites da nave
    └── enemy/                   # Sprites dos inimigos
```

---

## Roadmap

- [ ] Multiplayer LAN (arquitetura preparada no código)
- [ ] Modo GROUND: combate na superfície dos planetas
- [ ] Construção de bases e robôs mineradores
- [ ] Terraformação e sistema de facções

---

**Autor:** Wagner Machado dos Santos  
**GitHub:** [github.com/machadods](https://github.com/machadods)
