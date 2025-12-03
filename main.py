import os
import sys


from base_porto import fila_inicial, Estado_Porto, Regras_Porto, Resultados_Ficheiro, construir_caminho, resultado_ficheiro
from algoritmo import custo_uniforme, algoritmo_greedy, pesquisa_largura

if __name__ == '__main__':
    if not fila_inicial:
        sys.exit(0)

    # 1. Limpa o ficheiro de resultados antes de começar
    if os.path.exists(Resultados_Ficheiro):
        os.remove(Resultados_Ficheiro)
        print(f"[INFO] Ficheiro '{Resultados_Ficheiro}' limpo para nova comparação.")


    estado_inicial = Estado_Porto(navios_em_espera=fila_inicial, disp_A=0.0, disp_B=0.0)
    regras = Regras_Porto(estado_inicial)

    print('\n' + '=' * 100)
    print('INÍCIO DA COMPARAÇÃO DOS ALGORITMOS')
    print('=' * 100)
    

    comparacao_final = {}# Dicionário para armazenar resultados finais
    
    #  2. TESTE CUSTO UNIFORME (UCS)
    nome_algoritmo = "UCS Otimizado"
    print(f"\n[Execução] A correr {nome_algoritmo}...")
    custo_ucs, caminho_ucs, estados_ucs, estado_final_ucs, tempo_ucs = custo_uniforme(regras)
    
    if estado_final_ucs is not None and regras.e_estado_final(estado_final_ucs):
        sequencia_ucs = construir_caminho(caminho_ucs, estado_final_ucs, estado_inicial)
        print(f"[{nome_algoritmo}]: SUCESSO! Custo: {custo_ucs:.2f}. Tempo: {tempo_ucs:.6f}s")
        resultado_ficheiro(nome_algoritmo, tempo_ucs, custo_ucs, estados_ucs, sequencia_ucs)
    else:
        print(f"[{nome_algoritmo}]: FALHOU. Tempo: {tempo_ucs:.6f}s. Estados: {estados_ucs}")
        resultado_ficheiro(nome_algoritmo, tempo_ucs, None, estados_ucs, [])
    
    comparacao_final[nome_algoritmo] = {"custo": custo_ucs, "tempo": tempo_ucs}
    
    
    #  TESTE PESQUISA EM LARGURA (BFS) 
    nome_algoritmo = "Pesquisa em Largura (BFS)"
    print(f"\n[Execução] A correr {nome_algoritmo}...")
    custo_bfs, caminho_bfs, estados_bfs, estado_final_bfs, tempo_bfs = pesquisa_largura(regras)
    
    if estado_final_bfs is not None and regras.e_estado_final(estado_final_bfs):
        sequencia_bfs = construir_caminho(caminho_bfs, estado_final_bfs, estado_inicial)
        print(f"[{nome_algoritmo}]: SUCESSO! Custo: {custo_bfs:.2f}. Tempo: {tempo_bfs:.6f}s")
        resultado_ficheiro(nome_algoritmo, tempo_bfs, custo_bfs, estados_bfs, sequencia_bfs)
    else:
        print(f"[{nome_algoritmo}]: FALHOU. Tempo: {tempo_bfs:.6f}s. Estados: {estados_bfs}")
        resultado_ficheiro(nome_algoritmo, tempo_bfs, None, estados_bfs, [])
    
    comparacao_final[nome_algoritmo] = {"custo": custo_bfs, "tempo": tempo_bfs}

    
    # TESTE algoritmo_greedy 
    nome_algoritmo = "algoritmo Greedy"
    print(f"\n[Execução] A correr {nome_algoritmo}...")
    custo_greedy, caminho_greedy, estados_greedy, estado_final_greedy, tempo_greedy = algoritmo_greedy(regras)
    
    if estado_final_greedy is not None and regras.e_estado_final(estado_final_greedy):
        sequencia_greedy = construir_caminho(caminho_greedy, estado_final_greedy, estado_inicial)
        print(f"[{nome_algoritmo}]: SUCESSO! Custo: {custo_greedy:.2f}. Tempo: {tempo_greedy:.6f}s")
        resultado_ficheiro(nome_algoritmo, tempo_greedy, custo_greedy, estados_greedy, sequencia_greedy)
    else:
        print(f"[{nome_algoritmo}]: FALHOU. Tempo: {tempo_greedy:.6f}s. Estados: {estados_greedy}")
        resultado_ficheiro(nome_algoritmo, tempo_greedy, None, estados_greedy, [])
    
    comparacao_final[nome_algoritmo] = {"custo": custo_greedy, "tempo": tempo_greedy}

    
  
    print('\n' + '=' * 100)
    print("RESUMO FINAL DA COMPARAÇÃO DE ALGORITMOS")
    print('=' * 100)
    print(f"{'Algoritmo':<30} | {'Custo Total (Espera)':<25} | {'Tempo (s)':<15}")
    print('-' * 70)
    
    for nome, dados in comparacao_final.items():
        custo = f"{dados['custo']:.2f}" if dados['custo'] is not None else "FALHA"
        print(f"{nome:<30} | {custo:<25} | {dados['tempo']:.6f}")
        
    print('-' * 70)