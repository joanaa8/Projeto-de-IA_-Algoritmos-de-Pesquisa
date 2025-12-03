import pandas as pd
import heapq # fila prioritária (usado pelo UCS)
import datetime
import sys # erros
import itertools
import os
import time

ficheiro= 'dataset_navios_porto.xlsx'
Resultados_Ficheiro= 'resultados_ucs_otimizado.txt' # Nome do ficheiro atualizado

try:
    df = pd.read_excel(ficheiro)
    print("O ficheiro foi carregado com sucesso.")
    print(df.head()) # confirmação do carregamento


    fila_inicial=df.to_dict(orient='records') # criação do dicionário onde cada linha representa um registo
    
    for r in fila_inicial:
        try:
            r['Hora_Chegada'] = float(r.get('Hora_Chegada', 0.0))
        except Exception:
            r['Hora_Chegada'] = 0.0

        try:
            r['Duracao_Atracagem'] = float(r.get('Duracao_Atracagem', 0.0))
        except Exception:
            r['Duracao_Atracagem'] = 0.0

        r['ID_Navio'] = str(r.get('ID_Navio'))

    print('\nFila Inicial de Espera:')
    print(f"Total de Navios: {len(fila_inicial)}")

    if fila_inicial:
        print(f"Primeiro Navio: {fila_inicial[0]}")

except FileNotFoundError:
    print(f"Erro: Falha a encontrar o ficheiro '{ficheiro}'.")
    sys.exit(1)
except Exception as e:
    print(f"Erro ao ler o ficheiro: {e}")
    sys.exit(1)


class Estado_Porto: # aqui surge a definição do Estado
    def __init__(self, navios_em_espera, disp_A, disp_B):
        try:
           
            navios_ordenados = sorted(navios_em_espera, key=lambda n: n['ID_Navio'])
        except Exception:
            navios_ordenados = sorted(navios_em_espera)

        self.navios_em_espera = tuple(navios_ordenados)
        self.tempo_livre_A = disp_A
        self.tempo_livre_B = disp_B

        try:
            navios_ids = tuple(n['ID_Navio'] for n in navios_ordenados)
        except Exception:
            navios_ids = tuple(str(n) for n in navios_ordenados)

  
        self._id = (navios_ids, round(self.tempo_livre_A, 3), round(self.tempo_livre_B, 3))
        self._hash = hash(self._id)

    def _criar_id(self):
        return self._id

  
    def __eq__(self, other):
        if not isinstance(other, Estado_Porto):
            return False
        if self._hash != other._hash:
             return False
        return self._id == other._id

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return f"Estado_Porto(navios={len(self.navios_em_espera)}, A={self.tempo_livre_A}, B={self.tempo_livre_B})"


class Regras_Porto: #definir as regras e restrições que o porto apresenta
    def __init__(self, estado_inicial):
        self.estado_inicial = estado_inicial

    def e_estado_final(self, estado):
        return len(estado.navios_em_espera) == 0 

 
    def simular_sucessores(self, estado_atual):
        sucessores = []
        navios_fila = list(estado_atual.navios_em_espera)

        if not navios_fila:
            return sucessores
            
        navio_a_atracar = min(navios_fila, key=lambda n: n['Hora_Chegada'])
        

        try:
            index_do_navio = navios_fila.index(navio_a_atracar)
        except ValueError:
    
            return sucessores
        
   
        navio = navio_a_atracar
        i = index_do_navio 

        zonas_possiveis = []

        # Tipo 2 só pode ir para A
        if navio['Tipo'] == 'Tipo 2':
            zonas_possiveis = [('A', estado_atual.tempo_livre_A)]
        # Tipo 1 pode ir para A ou B
        elif navio['Tipo'] == 'Tipo 1':
            zonas_possiveis = [
                ('A', estado_atual.tempo_livre_A),
                ('B', estado_atual.tempo_livre_B)
            ]
      
        
        for zona, tempo_livre in zonas_possiveis:

            hora_chegada = float(navio.get('Hora_Chegada', 0.0))
            duracao = float(navio.get('Duracao_Atracagem', 0.0))

         
            tempo_inicio = max(hora_chegada, tempo_livre)

            custo_acao = tempo_inicio - hora_chegada


            novo_tempo_livre = tempo_inicio + duracao
            

            nova_fila = navios_fila[:i] + navios_fila[i+1:]

            nova_disp_A = novo_tempo_livre if zona == 'A' else estado_atual.tempo_livre_A
            nova_disp_B = novo_tempo_livre if zona == 'B' else estado_atual.tempo_livre_B
            
            estado_sucessor = Estado_Porto(
                navios_em_espera=nova_fila,
                disp_A=nova_disp_A,
                disp_B=nova_disp_B
            )

            sucessores.append((estado_sucessor, custo_acao))

        return sucessores


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


def construir_caminho(caminho, estado_final, estado_inicial):
    if estado_final is None or caminho is None:
        return []

    caminho_reverso = []
    estado_atual = estado_final

    while estado_atual is not None and estado_atual != estado_inicial:
        resultado = caminho.get(estado_atual)

        if resultado is None:
            break
                
        pai_estado, custo_acao = resultado
                
       
        navios_pai_ids = set(n['ID_Navio'] for n in pai_estado.navios_em_espera)
        navios_atual_ids = set(n['ID_Navio'] for n in estado_atual.navios_em_espera)

        navio_removido = list(navios_pai_ids - navios_atual_ids)
        if not navio_removido:
            estado_atual = pai_estado
            continue
                
        id_navio_atracado = list(navio_removido)[0]

      
        zona_atracagem = 'Indefinida'
      
        if estado_atual.tempo_livre_A > pai_estado.tempo_livre_A + 1e-3: 
            zona_atracagem = 'A'
        elif estado_atual.tempo_livre_B > pai_estado.tempo_livre_B + 1e-3: 
            zona_atracagem = 'B'
        else:
            zona_atracagem = 'Erro: Zona Indefinida'
            
        passo= {
            'Navio_ID': id_navio_atracado,
            'Custo_Ação': custo_acao,
            'Zona': zona_atracagem,
            'Disp_A_Final': estado_atual.tempo_livre_A,
            'Disp_B_Final': estado_atual.tempo_livre_B
        }
        caminho_reverso.append(passo)
            
        estado_atual = pai_estado

    return list(reversed(caminho_reverso))



def resultado_ficheiro (nome_ficheiro, custo_total, estados_explorados, sequencia_atracagem, tempo_execucao): 

  
    resultados_texto = []


   
    resultados_texto.append("CUSTO UNIFORME OTIMIZADO (Restrição: Processar o Navio de Chegada Mais Cedo)")
    resultados_texto.append(f"Tempo de Execução: {tempo_execucao:.4f} segundos") 
    resultados_texto.append(f"Estados Explorados: {estados_explorados}")
    resultados_texto.append(f"Custo Total Mínimo (Espera Acumulada): {custo_total if custo_total is not None else 'N/A'}")
    resultados_texto.append('-' * 60)
    resultados_texto.append('Sequência de Atracagem:')


    resultados_texto.append(f"{'#':<3} | {'Navio ID':<10} | {'Zona':<5} | {'Espera (C)':<10} | {'Custo Acumulado (g)':<20} | {'Disp A / Disp B'}")
    resultados_texto.append('-' * 100)

    custo_acumulado = 0.0
    for i, passo in enumerate(sequencia_atracagem or []):
        custo_acumulado += passo['Custo_Ação']

        
        linha = (f"{i+1:<3} | {passo['Navio_ID']:<10} | {passo['Zona']:<5} | {passo['Custo_Ação']:<10.2f} | "
                 f"{custo_acumulado:<20.2f} | {passo['Disp_A_Final']:.2f} / {passo['Disp_B_Final']:.2f}")
        resultados_texto.append(linha)


    resultados_texto.append('\n')

    try:
        with open(nome_ficheiro, 'a', encoding='utf-8') as f:
            f.write('\n'.join(resultados_texto) + '\n\n')
        print(f"\n[INFO] Resultados registados em '{nome_ficheiro}'.")
    except Exception as e:
        print(f"[ERRO] Falha ao escrever no ficheiro: {e}")

    

# Main
if __name__ == '__main__':
    if not fila_inicial:
        print('Fila inicial vazia. Nada a fazer.')
        sys.exit(0)


    estado_inicial = Estado_Porto(navios_em_espera=fila_inicial, disp_A=0.0, disp_B=0.0)
    regras = Regras_Porto(estado_inicial)


    print('\n' + '=' * 100)
    print('Início da Pesquisa de Custo Uniforme Otimizada')
    print('=' * 100)


    
    custo_total, caminho, estados_explorados, estado_final, tempo_execucao = custo_uniforme(regras)

    if estado_final is None:
        print('\nNão foi encontrada solução.')
        
        resultado_ficheiro(Resultados_Ficheiro, None, estados_explorados, [], tempo_execucao)
        sys.exit(0)


    print(f"\nSolução encontrada com custo total = {custo_total:.2f}")
    print(f"Estados explorados: {estados_explorados}")
    print(f"Tempo de execução: {tempo_execucao:.4f} segundos") # Imprime na consola

    sequencia = construir_caminho(caminho, estado_final, estado_inicial)


    print('\nSequência de Atracagem:')
    print(f"{'#':<3} | {'Navio ID':<10} | {'Zona':<5} | {'Espera (C)':<10} | {'Custo Acumulado (g)':<20} | {'Disp A / Disp B'}")
    print('-' * 100)
    acum = 0.0
    for i, passo in enumerate(sequencia):
        acum += passo['Custo_Ação']
        print((f"{i+1:<3} | {passo['Navio_ID']:<10} | {passo['Zona']:<5} | {passo['Custo_Ação']:<10.2f} | "
               f"{acum:<20.2f} | {passo['Disp_A_Final']:.2f} / {passo['Disp_B_Final']:.2f}"))


    
    resultado_ficheiro(Resultados_Ficheiro, custo_total, estados_explorados, sequencia, tempo_execucao)