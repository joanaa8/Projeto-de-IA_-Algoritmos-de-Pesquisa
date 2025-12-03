# Projeto-de-IA_-Algoritmos-de-Pesquisa
Este projeto implementa um sistema baseado em algoritmos de pesquisa para otimizar a sequência de atracagem de navios no Atlantic InteliHarbour, com o objetivo de minimizar o tempo total de espera e evitar bloqueios operacionais.

Algoritmos Implementados:

🔹 UCS — Uniform Cost Search
Garante solução ótima (menor tempo total de espera).
Expande sempre o estado com menor custo acumulado.
Ideal para problemas com custos positivos.
É o algoritmo principal do sistema.

🔹 Greedy Search
Escolhe sempre a ação imediata de menor custo.
Muito rápido.
Não garante solução ótima.
Útil como baseline.

🔹 BFS — Pesquisa em Largura
Não considera custos.
Baseado apenas em profundidade.
Útil para comparação, mas não adequado ao problema.

Ficheiros principais neste diretório:
- `main.py` — script principal que corre os algoritmos e grava resultados.  
- `base_porto.py` — modelação do estado do porto e a geração de sucessores.  
- `algoritmo.py` — implementação dos algoritmos (UCS, Greedy, BFS).  
- `dataset_navios_porto.xlsx` — (entrada) lista de navios (pode ser gerado sinteticamente).


Notas úteis:  
- Ver `guia_boaspraticas.md` para configurar o ambiente e boas práticas.  
- Ver `ideias.md` para a modelação, algoritmos sugeridos e plano de experimentos.
