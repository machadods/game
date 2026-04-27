# GAME ZERO

Jogo espacial single-player (com arquitetura preparada para LAN multiplayer) desenvolvido em Python com Pygame.

---

## Visão Geral

O jogador pilota uma nave em um universo aberto 2D, explora planetas, combate hordas inimigas, coleta ouro e usa a **Dobra Temporal** para teletransporte rápido entre pontos do mapa.

### Fluxo de estados

```
LOGIN → MENU → ORBITAL ↔ STRATEGIC (mapa)
                   ↓
                GAMEOVER
```

---

## Mecânicas Implementadas

### Login e Persistência
- Tela de login com campo de texto — cria jogador novo ou carrega existente do banco SQLite
- Auto-save a cada 30 segundos durante o jogo
- Backup automático do banco ao fechar

### Mundo Aberto (ORBITAL)
- Universo de **160 000 × 160 000 unidades** com câmera seguindo o jogador
- Fundo com **parallax em 3 camadas** de estrelas
- **Zona Segura** na origem (raio 3 000 u) — hordas não são ativadas enquanto o jogador está dentro

### Sistema Solar Fixo

8 planetas com posições fixas inspiradas no Sistema Solar real. A Zona Segura (origem) representa o Sol.

| Planeta | Tipo | Distância aprox. | Dificuldade |
|---|---|---|---|
| Mercurium | lava_world | 11 700 u | I |
| Venus Nova | lava_world | 23 000 u | III |
| Gaia | forest | 29 400 u | II |
| Marte | terrestrial_iron | 40 200 u | II |
| Ceres | ice_world | 50 100 u | I |
| Jupiter | gas_giant | 62 700 u | IIII |
| Saturno | gas_giant | 72 600 u | IIII |
| Netuno | ice_world | 79 400 u | IIIII |

- Coordenadas fixas no banco — sem aleatoriedade
- Cada planeta tem raio visual proporcional ao tipo e raio de ativação de horda
- Se o banco estiver com planetas antigos (aleatórios), é automaticamente recriado

### Sistema de Horda
- Ao entrar no raio de ativação de um planeta, a horda começa a spawnar
- Mínimo de 50 inimigos por planeta (`difficulty × 15`, no mínimo 50)
- Ondas de 10 inimigos a cada 6 segundos
- Planeta **conquistado** quando toda a horda for eliminada — salvo no banco
- **Recompensa de conquista: +1 vida**

### Ouro (única moeda)
- Moedas de ouro orbitam cada planeta (quantidade proporcional à dificuldade)
- **Cada nave inimiga abatida solta 1 coin no lugar onde morreu**
- Coletadas por colisão com a nave
- Usadas para **Dobra Temporal** e **Tiro Rápido**

### Dobra Temporal
- Tecla **F** no modo ORBITAL (ou ENTER no mapa STRATEGIC)
- Requer **50 ouro**
- Teletransporta o jogador para o raio de ativação do planeta selecionado

### Combate
- **Tiro normal**: clique esquerdo do mouse — dispara na direção do cursor (azul-claro)
- **Tiro rápido**: botão **direito do mouse segurado** — requer **≥ 10 ouro** — dispara continuamente a cada 0,08 s (ciano)
- Inimigos atiram automaticamente quando o jogador entra em alcance (1 200 u)
- Inimigos com separação entre si (evitam aglomerar)

### Mapa Estratégico (STRATEGIC)
- Tecla **M** para abrir/fechar
- Visão zoom-out do mesmo mundo (fator `STRAT_SCALE = 0.004`)
- Clique em planeta para selecioná-lo — painel lateral exibe tipo, dificuldade, horda e se tem ouro
- **ENTER** no mapa: fecha e voa até o planeta selecionado (Dobra Temporal)

### HUD
- Vidas (círculos vermelhos)
- Nome do piloto
- Contador de inimigos eliminados
- Ouro atual (dourado se ≥ 50, escuro se insuficiente)
- Status do tiro rápido
- Radar circular com inimigos, ouro, balas e planetas
- Seta de waypoint para o planeta selecionado
- Mensagens temporárias no centro da tela

---

## Estrutura do Projeto

```
game/
├── main.py                  # Loop principal, GameEngine, eventos
├── settings.py              # Resolução (1200×800), FPS, tamanhos de sprite
├── readme.md
├── game_data.db             # Banco SQLite (gerado automaticamente)
└── src/
    ├── player.py            # Classe Player (nave do jogador)
    ├── enemy.py             # Classe Enemy (IA, separação, tiro automático)
    ├── bullet.py            # Classe Bullet (projéteis)
    ├── coin.py              # Classe Coin (ouro coletável)
    ├── camera.py            # Câmera com offset de mundo
    ├── stars.py             # StarField (parallax 3 camadas)
    ├── database.py          # GameDatabase (SQLite — players e planets)
    └── celestial/
        ├── __init__.py
        └── planet.py        # Classe Planet, sistema de horda, PLANET_TYPES
```

---

## Controles

| Ação | Controle |
|---|---|
| Mover nave | WASD ou setas |
| Atirar | Botão esquerdo do mouse |
| Tiro rápido | Botão direito do mouse (segurado, ≥ 10 ouro) |
| Abrir/fechar mapa | M |
| Selecionar planeta no mapa | Clique esquerdo |
| Dobra Temporal | F (orbital) / ENTER (mapa) |
| Sair | ESC |

---

## Como Rodar

**Requisitos:** Python 3.10+ e Pygame

```bash
pip install pygame
python main.py
```

---

## Banco de Dados (SQLite)

Arquivo `game_data.db` gerado automaticamente na primeira execução.

**Tabela `players`:** `id, username, color, ship_x, ship_y, health, kills, score, gold, created_at`

**Tabela `planets`:** `id, name, x, y, radius_km, planet_type, difficulty, minerals, owner_id, conquered`

Backups com timestamp são criados automaticamente ao fechar o jogo.

---

## Roadmap

- [ ] Multiplayer LAN (cliente/servidor)
- [ ] Modo GROUND (combate na superfície do planeta)
- [ ] Construção de base e robôs mineradores
- [ ] Terraformação
- [ ] Facções e diplomacia entre planetas
