import pandas as pd
import heapq #fila prioritária
import datetime
import sys #erros
import itertools
import os
import time
import collections

ficheiro= 'dataset_navios_porto.xlsx'
Resultados_Ficheiro= 'resultados.txt'

try:
    df = pd.read_excel(ficheiro)
    print("O ficheiro foi carregado com sucesso.")
    print(df.head()) #confirmação do carregamento


    fila_inicial=df.to_dict(orient='records') #criação do dicionário onde cada linha representa um registo
    
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


def construir_caminho(caminho, estado_final, estado_inicial):
    if estado_final is None or caminho is None:
        return []

    caminho_reverso = []
    estado_atual = estado_final

    while  estado_atual is not None and estado_atual != estado_inicial:
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
        if estado_atual.tempo_livre_A != pai_estado.tempo_livre_A:
            zona_atracagem = 'A'

        elif estado_atual.tempo_livre_B != pai_estado.tempo_livre_B:
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



def resultado_ficheiro (nome_algoritmo, tempo_execucao, custo_total, estados_explorados, sequencia_atracagem):


    resultados_texto = []

    
    resultados_texto.append(f"ALGORITMO: {nome_algoritmo}")
    resultados_texto.append(f"Tempo de Execução: {tempo_execucao:.6f} segundos")
    resultados_texto.append(f"Estados Explorados: {estados_explorados}")
    resultados_texto.append(f"Custo Total (Soma Espera): {custo_total if custo_total is not None else 'N/A'}")
    resultados_texto.append('========================================================')
    resultados_texto.append('Sequência de Atracagem:')

    resultados_texto.append(f"{'#':<3} | {'Navio ID':<10} | {'Zona':<5} | {'Espera (C)':<10} | {'Custo Acumulado (g)':<20} | {'Disp A / Disp B'}")
    resultados_texto.append('-' * 100)

    custo_acumulado = 0.0
    for i, passo in enumerate(sequencia_atracagem or []):
        custo_acumulado += passo['Custo_Ação']

        linha = (f"{i+1:<3} | {passo['Navio_ID']:<10} | {passo['Zona']:<5} | {passo['Custo_Ação']:<10.2f} | "
                 f"{custo_acumulado:<20.2f} | {passo['Disp_A_Final']:.2f} / {passo['Disp_B_Final']:.2f}")
        resultados_texto.append(linha)


    try:
        
        with open(Resultados_Ficheiro, 'a', encoding='utf-8') as f: # 'a' (append) para adicionar o novo log ao fim do ficheiro
            f.write('\n'.join(resultados_texto) + '\n')
        print(f"\n[INFO] Resultados do {nome_algoritmo} registados em '{Resultados_Ficheiro}'.")
    except Exception as e:
        print(f"[ERRO] Falha ao escrever no ficheiro: {e}")