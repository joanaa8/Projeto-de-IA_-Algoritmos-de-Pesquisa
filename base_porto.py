
import pandas as pd
import sys, os
from typing import Dict, Any, Iterable, List

ficheiro = 'dataset_navios_porto_100.xlsx'
Resultados_Ficheiro = 'resultadosdata100.txt'

# Carrega dataset e normaliza tipos
try:
    df = pd.read_excel(ficheiro, engine='openpyxl')
    fila_inicial: List[Dict[str, Any]] = df.to_dict(orient='records')
    for r in fila_inicial:
        r['ID_Navio'] = str(r.get('ID_Navio', '')).strip()
        r['Tipo'] = str(r.get('Tipo', '')).strip()
        try: r['Hora_Chegada'] = float(r.get('Hora_Chegada', 0.0))
        except: r['Hora_Chegada'] = 0.0
        try: r['Duracao_Atracagem'] = float(r.get('Duracao_Atracagem', 0.0))
        except: r['Duracao_Atracagem'] = 0.0
    # Ordena APENAS uma vez por (Hora_Chegada, ID_Navio)
    fila_inicial = sorted(fila_inicial, key=lambda n: (float(n['Hora_Chegada']), str(n['ID_Navio'])))
    print("O ficheiro foi carregado com sucesso.")
except Exception as e:
    print(f"Erro ao ler o ficheiro: {e}")
    sys.exit(1)


class Estado_Porto:
 
    __slots__ = ('navios_em_espera', 'tempo_livre_A', 'tempo_livre_B',
                 '_ids_tuple', '_id', '_hash')

    def __init__(self, navios_em_espera, disp_A: float, disp_B: float, ids_tuple=None):
        
       
        navios_ordenados = tuple(sorted(
            navios_em_espera,
            key=lambda n: (float(n['Hora_Chegada']), str(n['ID_Navio']))
        ))
        self.navios_em_espera = navios_ordenados

        
        self.tempo_livre_A = round(float(disp_A), 6)# Garantir consistência numérica
        self.tempo_livre_B = round(float(disp_B), 6)

        # Cache dos IDs da fila para hashing rápido
        if ids_tuple is None:
            self._ids_tuple = tuple(n['ID_Navio'] for n in navios_ordenados)
        else:
            self._ids_tuple = ids_tuple

        
        self._id = (self._ids_tuple, self.tempo_livre_A, self.tempo_livre_B)# Identificador único do estado (tupla imutável)

        
        self._hash = hash(self._id)# Pre-hash, muito mais rápido

    def __eq__(self, other):
        return isinstance(other, Estado_Porto) and self._id == other._id

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return f"Estado_Porto({len(self.navios_em_espera)} navios, A={self.tempo_livre_A}, B={self.tempo_livre_B})"



class Regras_Porto:

    def __init__(self, estado_inicial, janela_delta=0.0, max_candidatos=None):
        self.estado_inicial = estado_inicial
        self.janela_delta = float(janela_delta)
        self.max_candidatos = max_candidatos

    def e_estado_final(self, estado):
        return len(estado.navios_em_espera) == 0

    # Tipos elegíveis para zonas
    def _zonas_elegiveis(self, navio):
        return ['A'] if navio['Tipo'] == 'Tipo 2' else ['A', 'B']

   
    def simular_sucessores(self, estado):
        fila = list(estado.navios_em_espera)
        if not fila:
            return []

        sucessores = []

     
        limite_lookahead = 1 # olhamos para os 3 primeiros e tentamos alocar qualquer um deles
        #troca para 2 para 25
        #troca para 1 para 30
       
        for i in range(min(len(fila), limite_lookahead)): # para cada um dos primeiros 3 navios na fila
            navio = fila[i]

            chegada = float(navio['Hora_Chegada'])
            dur = float(navio['Duracao_Atracagem'])
            zonas = self._zonas_elegiveis(navio)

            for zona in zonas:
                if zona == 'A':
                    inicio = max(chegada, estado.tempo_livre_A)
                    novo_tA = inicio + dur
                    novo_tB = estado.tempo_livre_B
                else:
                    inicio = max(chegada, estado.tempo_livre_B)
                    novo_tA = estado.tempo_livre_A
                    novo_tB = inicio + dur

                espera = max(0.0, inicio - chegada)

                nova_fila = fila[:i] + fila[i+1:]# remove o navio que estamos a processar (i) e mantem os outros.
                
                novo_ids = estado._ids_tuple[:i] + estado._ids_tuple[i+1:] #atualiza ids

                novo_estado = Estado_Porto(nova_fila, novo_tA, novo_tB, ids_tuple=novo_ids)

                acao = { 
                    'Navio_ID': navio['ID_Navio'],
                    'Zona': zona,
                    'Inicio': inicio,
                    'Duracao': dur,
                    'Espera': espera,
                    'Hora_Chegada': chegada,
                    'Tipo': navio['Tipo'],
                    'Exclusivo_A': navio['Tipo'] == 'Tipo 2'
                }

                sucessores.append((novo_estado, espera, acao))

        return sucessores



def construir_caminho(caminho, estado_final, estado_inicial):
    if estado_final is None or caminho is None:
        return []
    sequencia = []
    e = estado_final
    while e is not None and e != estado_inicial:
        entrada = caminho.get(e)
        if entrada is None:
            break
        pai, custo_acao, acao = entrada
        passo = {
            'Navio_ID': acao.get('Navio_ID'),
            'Zona': acao.get('Zona'),
            'Inicio': acao.get('Inicio'),
            'Duracao': acao.get('Duracao'),
            'Espera': custo_acao,
            'Disp_A_Final': e.tempo_livre_A,
            'Disp_B_Final': e.tempo_livre_B
        }
        sequencia.append(passo)
        e = pai
    return list(reversed(sequencia))


def resultado_ficheiro (nome_algoritmo, tempo_execucao, custo_total, estados_explorados, sequencia_atracagem):
    resultados = []
    resultados.append(f"ALGORITMO: {nome_algoritmo}")
    resultados.append(f"Tempo de Execução: {tempo_execucao:.6f} segundos")
    resultados.append(f"Estados Explorados: {estados_explorados}")
    resultados.append(f"Custo Total (Soma Espera): {custo_total if custo_total is not None else 'N/A'}")
    resultados.append('========================================================')
    resultados.append('Sequência de Atracagem:')
    resultados.append(f"{'#':<3} {'Navio ID':<10} {'Zona':<5} {'Espera (C)':<10} {'Disp A / Disp B'}")
    resultados.append('-'*100)
    for i, p in enumerate(sequencia_atracagem or []):
        linha = (f"{i+1:<3} {p['Navio_ID']:<10} {p['Zona']:<5} "
                 f"{float(p['Espera']):<10.2f} "
                 f"{p['Disp_A_Final']:.2f} / {p['Disp_B_Final']:.2f}")
        resultados.append(linha)
    with open(Resultados_Ficheiro, 'a', encoding='utf-8') as f:
        f.write('\n'.join(resultados) + '\n')
    print(f"\n[INFO] Resultados do {nome_algoritmo} registados em '{Resultados_Ficheiro}'.")
    print('\n')