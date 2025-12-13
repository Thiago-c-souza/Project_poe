# MVP: ARPG Top-Down em Pygame CE

Este roteiro foca em entregar rapidamente um protótipo jogável e evoluir para um MVP com
loot e classes configuráveis.

## 1) Protótipo jogável (placeholder art)
- Movimento e colisão com bordas do mapa (já coberto pelo `PlayScene` inicial).
- Ataque básico: começar com hitbox frontal simples ou projétil reto; checar colisão com inimigos.
- Inimigos simples que andam em direção ao player e causam dano por contato.
- Vida, morte e reinício de cena.
- **Saída:** experiência curta (30s) onde o jogador pode se mover, atacar e morrer.

## 2) Estrutura de projeto
- `core/`: loop principal, cenas e input; `Game` centraliza ticking e delega para cenas.
- `scenes/`: PlayScene e futuras cenas (menu, pausa, tela de morte).
- `entities/`: Player, Enemy, Projectile; componentes de stats e inventário.
- `systems/`: combate, loot, skills, estatísticas, pathfinding simples.
- `data/`: tabelas de classes, inimigos e itens em JSON/YAML; carregar configs em runtime.
- `assets/`: sprites 32x32 ou 16x16, tileset compatível e SFX/UI.
- **Saída:** árvore limpa para evitar acoplamento excessivo.

## 3) Pipeline de assets
- Sprites 32x32 recomendados para leitura melhor em top-down.
- Tileset compatível (Tiled) e export para JSON/TSX + layers de colisão.
- Ferramentas: Aseprite/LibreSprite para sprites; Tiled para montagem de mapa.
- **Saída:** fluxo rápido para iterar no mapa e personagens.

## 4) Classes configuráveis
- Player base único + configs de classe em `data/classes.yml`.
- Cada classe define: stats iniciais, arma inicial e 1 skill exclusiva (cone, flecha perfurante, fireball).
- **Saída:** variedade sem duplicar código de player.

## 5) Feeling ARPG
- Loot dropável, itens no chão e coleta com tecla de ação.
- Raridade: normal/mágico/raro + mods simples (+vida, +dano, +atributo).
- Boss simples com padrão de ataque claro.
- UI mínima: barras de vida/mana, hotbar e indicador de loot.
- **Saída:** ciclo de recompensa viciante já perceptível no MVP.
