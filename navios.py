import pandas as pd

ficheiro= 'dataset_navios_porto.xlsx'

try:
    df = pd.read_excel(ficheiro)
    print("O ficheiro foi carregado com sucesso.")
    print(df.head()) #confirmação do carregamento


    fila_inicial=df.to_dict(orient='records') #criação do dicionário onde cada linha representa um registo
    
    print("\nFila Inicial de Espera:")
    print(f"Total de Navios: {len(fila_inicial)}")
    print(f"Primeiro Navio: {fila_inicial[0]}")

    print(fila_inicial)  # confirmação do conteúdo



except FileNotFoundError:
    print(f"Erro: Falha a encontrar o ficheiro '{ficheiro}'.")




