import os, sys
from base_porto import fila_inicial, Estado_Porto, Regras_Porto, Resultados_Ficheiro, construir_caminho, resultado_ficheiro
from algoritmo import custo_uniforme, algoritmo_greedy, pesquisa_largura, algoritmo_a_star

if __name__ == '__main__':
    if not fila_inicial:
        sys.exit(0)

    if os.path.exists(Resultados_Ficheiro):
        os.remove(Resultados_Ficheiro)
    print(f"[INFO] Ficheiro '{Resultados_Ficheiro}' limpo para nova comparação.")

    # Estado inicial (fila já ordenada em base_porto.py)
    estado_inicial = Estado_Porto(navios_em_espera=fila_inicial, disp_A=0.0, disp_B=0.0)
    # Usa janela_delta pequena e, se quiseres, limita nº de candidatos por expansão (ex.: 5)
    regras = Regras_Porto(estado_inicial, janela_delta=0.0, max_candidatos=None)

    print('\n' + '=' * 100)
    print('INÍCIO DA COMPARAÇÃO DOS ALGORITMOS')
    print('=' * 100)

    comparacao_final = {}

    # Greedy (para UB do UCS)
    nome = "algoritmo Greedy (UB para UCS)"
    print(f"\n[Execução] A correr {nome}...")
    c_g, cam_g, est_g, fin_g, t_g = algoritmo_greedy(regras)
    if fin_g is not None and regras.e_estado_final(fin_g):
        seq_g = construir_caminho(cam_g, fin_g, estado_inicial)
        print(f"[{nome}]: SUCESSO! Custo: {c_g:.2f}. Tempo: {t_g:.6f}s")
        resultado_ficheiro(nome, t_g, c_g, est_g, seq_g)
        ub = c_g  # upper bound para UCS
    else:
        print(f"[{nome}]: FALHOU. Tempo: {t_g:.6f}s. Estados: {est_g}")
        resultado_ficheiro(nome, t_g, None, est_g, [])
        ub = float('inf')
    comparacao_final[nome] = {"custo": c_g, "tempo": t_g}



    # A* com heurística melhorada
    nome = "A* (heurística melhorada: espera + carga relaxada)"
    print(f"\n[Execução] A correr {nome}...")
    c_a, cam_a, est_a, fin_a, t_a = algoritmo_a_star(regras)

    if fin_a is not None and regras.e_estado_final(fin_a):
        seq_a = construir_caminho(cam_a, fin_a, estado_inicial)
        print(f"[{nome}]: SUCESSO! Custo: {c_a:.2f}. Tempo: {t_a:.6f}s")
        resultado_ficheiro(nome, t_a, c_a, est_a, seq_a)
    else:
        print(f"[{nome}]: FALHOU. Tempo: {t_a:.6f}s. Estados: {est_a}")
        resultado_ficheiro(nome, t_a, None, est_a, [])
        
    comparacao_final[nome] = {"custo": c_a, "tempo": t_a}



    # UCS com poda por UB
    nome = "UCS Otimizado (branch-and-bound)"
    print(f"\n[Execução] A correr {nome}...")
    c_ucs, cam_ucs, est_ucs, fin_ucs, t_ucs = custo_uniforme(regras, ub=ub)
    if fin_ucs is not None and regras.e_estado_final(fin_ucs):
        seq_ucs = construir_caminho(cam_ucs, fin_ucs, estado_inicial)
        print(f"[{nome}]: SUCESSO! Custo: {c_ucs:.2f}. Tempo: {t_ucs:.6f}s")
        resultado_ficheiro(nome, t_ucs, c_ucs, est_ucs, seq_ucs)
    else:
        print(f"[{nome}]: FALHOU. Tempo: {t_ucs:.6f}s. Estados: {est_ucs}")
        resultado_ficheiro(nome, t_ucs, None, est_ucs, [])
    comparacao_final[nome] = {"custo": c_ucs, "tempo": t_ucs}


    print('\n' + '=' * 100)
    print("RESUMO FINAL DA COMPARAÇÃO DE ALGORITMOS")
    print('=' * 100)
    print(f"{'Algoritmo':<35} {'Custo Total (Espera)':<25} {'Tempo (s)':<15}")
    print('-' * 80)
    for nome, dados in comparacao_final.items():
        custo = f"{dados['custo']:.2f}" if dados['custo'] is not None else "FALHA"
        print(f"{nome:<35} {custo:<25} {dados['tempo']:.6f}")
    print('-' * 80)