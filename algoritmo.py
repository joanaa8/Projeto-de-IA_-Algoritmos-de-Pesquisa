
import time, heapq, itertools, collections
from base_porto import Regras_Porto, Estado_Porto

# --- A* com heurística admissível (espera bruta) ---
def heuristica_espera(estado: Estado_Porto) -> float:
    tA, tB = estado.tempo_livre_A, estado.tempo_livre_B
    exclusivos_A, exclusivos_B, flexiveis = [], [], []
    for n in estado.navios_em_espera:
        chg = float(n['Hora_Chegada']); dur = float(n['Duracao_Atracagem'])
        if n['Tipo'] == 'Tipo 2': exclusivos_A.append((chg, dur))       # exclusivo A
        else:                      flexiveis.append(chg)                 # Tipo 1 (A/B)
        # (Se existirem exclusivos B no teu dataset, separa-os em exclusivos_B)

    exclusivos_A.sort(key=lambda x: x[0])
    lb = 0.0
    for chg, dur in exclusivos_A:
        start = max(tA, chg)
        lb += max(0.0, tA - chg)
        tA = start + dur

    m = min(tA, tB)
    for chg in flexiveis:
        if m > chg:
            lb += (m - chg)
    return lb

def algoritmo_a_star(regras: Regras_Porto):
    start = time.time()
    cnt = itertools.count()
    openh = []
    best_g = {}
    caminho = {}
    e0 = regras.estado_inicial

    f0 = heuristica_espera(e0)
    heapq.heappush(openh, (f0, next(cnt), e0))
    best_g[e0] = 0.0
    caminho[e0] = (None, 0.0, None)
    explorados = 0

    while openh:
        f_atual, _, e = heapq.heappop(openh)
        g_atual = best_g.get(e)
        if g_atual is None:  # entrada obsoleta
            continue
        h_atual = heuristica_espera(e)
        if f_atual > g_atual + h_atual + 1e-12:  # obsoleta
            continue

        explorados += 1
        if regras.e_estado_final(e):
            return g_atual, caminho, explorados, e, time.time()-start

        for e2, c, acao in regras.simular_sucessores(e):
            ng = g_atual + c
            if ng < best_g.get(e2, float('inf')):
                best_g[e2] = ng
                caminho[e2] = (e, c, acao)
                nf = ng + heuristica_espera(e2)
                heapq.heappush(openh, (nf, next(cnt), e2))

    return None, None, explorados, None, time.time()-start


# --- UCS com branch-and-bound (UB retirado do Greedy) ---
def custo_uniforme(regras: Regras_Porto, ub: float = float('inf')):
    """UCS: ótimo; poda ramos com custo >= ub (upper bound opcional)."""
    start = time.time()
    contador = itertools.count()
    openh = []
    best = {}       # melhor g(n) por estado
    caminho = {}
    e0 = regras.estado_inicial

    heapq.heappush(openh, (0.0, next(contador), e0))
    best[e0] = 0.0
    caminho[e0] = (None, 0.0, None)
    explorados = 0

    while openh:
        g_atual, _, e = heapq.heappop(openh)
        if g_atual > best.get(e, float('inf')):
            continue
        explorados += 1
        if regras.e_estado_final(e):
            return g_atual, caminho, explorados, e, time.time()-start

        for e2, c, acao in regras.simular_sucessores(e):
            ng = g_atual + c
            if ng >= ub:
                continue  # poda
            if ng < best.get(e2, float('inf')):
                best[e2] = ng
                caminho[e2] = (e, c, acao)
                heapq.heappush(openh, (ng, next(contador), e2))

    return None, None, explorados, None, time.time()-start


# --- Greedy com política de não bloquear A ---
def algoritmo_greedy(regras: Regras_Porto):
    start = time.time()
    e = regras.estado_inicial
    caminho = {e: (None, 0.0, None)}
    g_total = 0.0
    explorados = 0

    while not regras.e_estado_final(e):
        explorados += 1
        sucs = list(regras.simular_sucessores(e))
        if not sucs:
            break

        # Preferência: se há ação na A para Exclusivo_A (Tipo 2), filtra outras de A (Tipo 1)
        a_excl = [s for s in sucs if s[2].get('Zona')=='A' and s[2].get('Exclusivo_A')]
        if a_excl:
            sucs = [s for s in sucs if not (s[2].get('Zona')=='A' and not s[2].get('Exclusivo_A'))] or sucs

        # Guloso: custo -> chegada -> duração
        sucs.sort(key=lambda s: (s[1], s[2]['Hora_Chegada'], s[2]['Duracao']))
        e2, c, acao = sucs[0]
        g_total += c
        caminho[e2] = (e, c, acao)
        e = e2

    return g_total, caminho, explorados, e, time.time()-start


# --- BFS (referência estrutural) ---
def pesquisa_largura(regras: Regras_Porto):
    start = time.time()
    fila = collections.deque([regras.estado_inicial])
    caminho = {regras.estado_inicial: (None, 0.0, None)}
    visitados = {regras.estado_inicial}
    explorados = 0

    while fila:
        e = fila.popleft()
        explorados += 1
        if regras.e_estado_final(e):
            # acumula custo percorrendo caminho
            custo_total = 0.0
            temp = e
            while caminho.get(temp) and caminho[temp][0] is not None:
                _, c, _ = caminho[temp]
                custo_total += c
                temp = caminho[temp][0]
            return custo_total, caminho, explorados, e, time.time()-start

        for e2, c, acao in regras.simular_sucessores(e):
            if e2 not in visitados:
                visitados.add(e2)
                caminho[e2] = (e, c, acao)
                fila.append(e2)

    return None, None, explorados, None, time.time()-start
