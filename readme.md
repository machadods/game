# Game Zero

`Game Zero` é um shooter espacial single-player em Python + Pygame.
Você pilota uma nave em um sistema solar expandido, enfrenta hordas inimigas, coleta ouro e conquista planetas para ganhar vidas e desbloquear novas invasões.

---

## Como Rodar

### Requisitos
- Python 3.10+
- Pygame

### Comandos
```bash
pip install pygame
python main.py
```

---

## Controles

| Ação | Tecla / Mouse |
|---|---|
| Mover nave | WASD ou ←↑↓→ |
| Atirar | Clique esquerdo |
| Fogo rápido | Clique direito segurado (requer ≥ 10 ouro) |
| Mapa estratégico | M |
| Selecionar planeta no mapa | Clique esquerdo |
| Dobra Temporal | F no modo orbital |
| Reiniciar após Game Over | R |
| Sair | ESC |

---

## Visão Geral do Jogo

### Mundo e navegação
- Universo amplo com sistema solar jogável.
- Câmera suave segue o jogador e a janela é redimensionável.
- O Sol fica no centro do mapa e funciona como a zona segura do jogo.
- Na tela estratégica, você vê todo o sistema e pode escolher qual planeta atacar.

### Ouro e recursos
- Ouro é a moeda principal do jogo.
- Coleta-se moedas orbitando planetas e eliminando inimigos.
- Ouro permite usar habilidades especiais, como tiro rápido e Dobra Temporal.

### Combate
- Clique esquerdo para atirar em direção ao cursor.
- Clique direito segurado ativa fogo rápido quando há ouro suficiente.
- Acumular ouro suficiente melhora o dano de tiros.

### Dobra Temporal
- Custa **50 ouro**.
- Teleporta o jogador para a borda de ativação do planeta selecionado.
- O destino é calculado com intercept orbital baseado na posição futura do planeta.

### Hordas e conquista
- Quando o jogador entra na área de ativação de um planeta, a horda começa a aparecer.
- Cada planeta possui dificuldade definida.
- O planeta é conquistado quando todos os inimigos da horda são eliminados.
- Conquistar um planeta recompensa o jogador com vidas e pode ativar invasões de outros planetas.

### Invasões e dinâmica
- Planetas conquistados podem provocar invasões de outros planetas não conquistados.
- As invasões são enviadas em ondas e criam pressão constante no mapa.

---

## Sistema Solar Atualizado

O jogo contém um sistema solar expandido, com planetas principais, luas, asteroides, cometas e regiões especiais.
O Sol é representado como a zona segura central.

### Exemplos de corpos celestes
- Mercurium, Venus Nova, Terra, Marte, Ceres, Jupiter, Saturno, Netuno
- Lua, Io, Europa, Ganimedes, Calisto, Titã, Tritão e outros satélites
- Plutão, Éris, asteroides do cinturão principal, cometas e cinturão de Kuiper

---

## HUD e interface

- Vidas aparecem no canto superior esquerdo.
- Inimigos abatidos e ouro atual aparecem no canto superior direito.
- Indicadores de status de tiro rápido e dano extra são exibidos no HUD.
- Waypoint aponta para o planeta selecionado quando ele está fora de vista.
- Mensagens temporárias aparecem no centro da tela.

---

## Estrutura do Projeto

```
game/
├── main.py              # Entrada principal, loop do jogo, lógica e interface
├── settings.py          # Configurações de tela, escala e tamanhos de sprites
├── game_data.db         # Banco SQLite gerado automaticamente
├── readme.md            # Documentação do projeto
└── src/
    ├── player.py        # Classe do jogador: movimento, sprites e limites
    ├── enemy.py         # Classe de inimigos: IA, formação e invasões
    ├── bullet.py        # Projéteis de jogador e inimigos
    ├── coin.py          # Moedas de ouro e órbita de recursos
    ├── camera.py        # Câmera com zoom e conversão de coordenadas
    ├── stars.py         # Fundo de estrelas com parallax
    ├── database.py      # SQLite para salvar jogadores e planetas
    └── celestial/
        └── planet.py    # Classe Planet, tipos, sistema de horda e renderização
```

---

## Persistência

- O jogo salva progresso no banco de dados (`game_data.db`).
- O banco possui backups automáticos.
- Login com nome de piloto cria conta nova ou carrega dados existentes.

---

## Observações

- A pasta `assets/player/` era um teste e foi removida, pois o jogo usa sprites diretamente em `assets/`.
- O arquivo `zombie.py` era apenas um experimento e também foi removido.

---

## Roadmap

- [ ] Modo GROUND — combate na superfície do planeta
- [ ] Novos tipos de inimigo com comportamentos distintos
- [ ] Bases orbitais e robôs mineradores
- [ ] Multiplayer LAN
- [ ] Sistema de facções entre planetas

---

**Autor:** Wagner Machado dos Santos
