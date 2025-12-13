# ARPG Top-Down Prototype (Pygame)

Este repositório prepara um protótipo estilo ARPG top-down em Python usando Pygame CE.
O objetivo inicial é um MVP com 1 mapa, 3 classes configuráveis, 1 habilidade exclusiva
por classe mais ataque básico, inimigos simples e loot básico.

## Estrutura proposta
- `core/`: loop do jogo, gerenciamento de cenas, input e câmera.
- `scenes/`: telas jogáveis e menus; começa com uma cena de jogo simples.
- `entities/`: player, inimigos, projéteis e componentes de estatísticas.
- `systems/`: combate, loot, inventário, habilidades e cálculos de atributos.
- `data/`: configs em JSON/YAML para classes, inimigos, itens e habilidades.
- `assets/`: sprites, tilesets, fontes e efeitos sonoros.

## Como rodar
1. Instale dependências (Pygame Community Edition é recomendada):
   ```bash
   pip install pygame-ce
   ```
2. Execute o protótipo:
   ```bash
   python main.py
   ```

A cena atual é um playground simples para validar movimento, colisão com bordas e desenho
básico. Use as setas ou WASD para mover. Feche a janela para sair.

## Próximos passos sugeridos
- Adicionar colisão com tiles do mapa e paredes definidas em arquivos `data/` (ex.: Tiled).
- Implementar inimigos que perseguem o jogador, causando dano por contato.
- Criar o fluxo de vida/morte e reinício da cena.
- Acrescentar ataque básico (hitbox ou projétil) e habilidades exclusivas de cada classe.
- Integrar loot básico com raridade simples (normal/mágico/raro).
- Conectar UI mínima (vida/mana e hotbar) e um boss simples para fechar o MVP.
