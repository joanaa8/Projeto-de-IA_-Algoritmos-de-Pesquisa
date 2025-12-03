import time
import heapq
import itertools
import collections
# Importa as classes base e regras do modelo
from base_porto import Regras_Porto, Estado_Porto

def custo_uniforme(regras):
    start_time = time.time()  #
    contador = itertools.count()
    fila_prioritaria = []
    melhor_custo = {} 
    caminho = {} 

    estado_inicial = regras.estado_inicial
    heapq.heappush(fila_prioritaria, (0.0, next(contador), estado_inicial))

    melhor_custo[estado_inicial] = 0.0
    caminho[estado_inicial] = None

    estados_explorados = 0

    while fila_prioritaria:

        custo_atual, _, estado_atual = heapq.heappop(fila_prioritaria)

        
        if custo_atual > melhor_custo.get(estado_atual, float('inf')):
            continue

        estados_explorados += 1
        
        if estados_explorados % 10000 == 0:
             print(f"Status UCS: {estados_explorados} estados explorados. Custo atual: {custo_atual:.2f}")
        
        if regras.e_estado_final(estado_atual):
            tempo_execucao = time.time() - start_time 
            return custo_atual, caminho, estados_explorados, estado_atual, tempo_execucao

        for estado_sucessor, custo_acao in regras.simular_sucessores(estado_atual):
            novo_custo = custo_atual + custo_acao
            
            # ID pré-calculado para o lookup
            if novo_custo < melhor_custo.get(estado_sucessor, float('inf')):
                melhor_custo[estado_sucessor] = novo_custo
                caminho[estado_sucessor] = (estado_atual, custo_acao)
                heapq.heappush(fila_prioritaria, (novo_custo, next(contador), estado_sucessor))

   
    tempo_execucao = time.time() - start_time  
    return None, None, estados_explorados, None, tempo_execucao


def algoritmo_greedy(regras):
    start_time = time.time()  
    estado_atual = regras.estado_inicial
    caminho = {estado_atual: None} 
    custo_total = 0.0
    estados_explorados = 0
    
    while not regras.e_estado_final(estado_atual):
        estados_explorados += 1

        sucessores_e_custos = regras.simular_sucessores(estado_atual)
        
        if not sucessores_e_custos:
            
            break

        # O algoritmo_greedy só explora a melhor opção imediata.
        melhor_sucessor, melhor_custo_acao = min(
            sucessores_e_custos, 
            key=lambda item: item[1] # item[1] é o custo_acao (tempo de espera)
        )
        
        
        custo_total += melhor_custo_acao
        caminho[melhor_sucessor] = (estado_atual, melhor_custo_acao)
        estado_atual = melhor_sucessor

    tempo_execucao = time.time() - start_time     
    return custo_total, caminho, estados_explorados, estado_atual, tempo_execucao

def pesquisa_largura(regras):
    inicio_tempo = time.time()
    
    fila = collections.deque([regras.estado_inicial]) # FILA normal (FIFO)
    caminho = {regras.estado_inicial: None} # Guarda o predecessor e o custo da ação
    visitados = {regras.estado_inicial} # Set para evitar re-exploração e loops
    
    estados_explorados = 0
    
    while fila:
        estado_atual = fila.popleft() # Pega o nó menos profundo
        estados_explorados += 1

        if regras.e_estado_final(estado_atual):
            tempo_decorrido = time.time() - inicio_tempo
            
            # BFS não acumula custo, tem de ser calculado a partir do caminho
            custo_total = 0.0
            temp_estado = estado_atual
            while caminho.get(temp_estado) is not None:
                _, custo_acao = caminho[temp_estado]
                custo_total += custo_acao
                # Para avançar, precisamos do estado pai.
                temp_estado = caminho[temp_estado][0]
            
            return custo_total, caminho, estados_explorados, estado_atual, tempo_decorrido

        for estado_sucessor, custo_acao in regras.simular_sucessores(estado_atual):
            
            if estado_sucessor not in visitados:
                visitados.add(estado_sucessor)
                caminho[estado_sucessor] = (estado_atual, custo_acao) # Guarda o estado pai E o custo da ação
                fila.append(estado_sucessor)
                
    tempo_decorrido = time.time() - inicio_tempo
    return None, None, estados_explorados, None, tempo_decorrido
