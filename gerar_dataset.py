import pandas as pd
import random

def gerar_dataset_30_navios():
    
    filename = "dataset_navios_porto_100.xlsx" 
    num_navios = 100  # O limite que queremos testar
    
    
    portos_origem = ["Roterdão", "Xangai", "Singapura", "Los Angeles", "Hamburgo", "Santos", "Lisboa", "Sines"]
    
    cargas_grande_porte = ["Contentores", "Passageiros (Cruzeiro)", "Gás Natural", "Petróleo"]
    cargas_medio_porte = ["Pescado", "Carga Geral", "Veículos", "Cereais"]

    dados = []
    tempo_atual = 0.0

    print(f"A gerar '{filename}' com {num_navios} navios...")

    
    for i in range(1, num_navios + 1):
        id_navio = f"N{i:03d}"
        
        
        is_grande_porte = random.random() < 0.3 
        
        if is_grande_porte:
            
            tipo = "Tipo 2"
            zona = "A"
            tipo_carga = random.choice(cargas_grande_porte)
            duracao = round(random.uniform(6.0, 14.0), 2)
            prioridade = random.randint(3, 5)
            
        else:
            
            tipo = "Tipo 1"
            zona = "A, B"
            tipo_carga = random.choice(cargas_medio_porte)
            duracao = round(random.uniform(2.0, 8.0), 2)
            prioridade = random.randint(1, 4)

        # Hora de Chegada (Sequencial)
        tempo_atual += random.uniform(0.5, 2.5)
        hora_chegada = round(tempo_atual, 2)
        
        porto_origem = random.choice(portos_origem)

        dados.append({
            "ID_Navio": id_navio,
            "Tipo": tipo,
            "Zona_Permitida": zona,
            "Porto_Origem": porto_origem,
            "Tipo_Carga": tipo_carga,
            "Hora_Chegada": hora_chegada,
            "Duracao_Atracagem": duracao,
            "Prioridade": prioridade
        })

    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Ordenar colunas
    colunas_ordem = [
        "ID_Navio", "Tipo", "Zona_Permitida", "Porto_Origem", 
        "Tipo_Carga", "Hora_Chegada", "Duracao_Atracagem", "Prioridade"
    ]
    df = df[colunas_ordem]

    # Guardar Excel
    try:
        df.to_excel(filename, index=False)
        print(f"✅ Sucesso! Ficheiro '{filename}' criado com {num_navios} navios.")
        print(df.tail()) # Mostra os últimos para confirmar que vai até ao N030
    except ImportError:
        print("❌ ERRO: Instala as dependências: pip install pandas openpyxl")

if __name__ == "__main__":
    gerar_dataset_30_navios()