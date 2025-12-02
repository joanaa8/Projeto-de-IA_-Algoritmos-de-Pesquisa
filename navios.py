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


class Estado_Porto:#aqui surge a definição do Estado
    def __init__(self, navios_em_espera, disp_A, disp_B):
        self.navios_em_espera = tuple(navios_em_espera)  
        self.tempo_livre_A = disp_A  
        self.tempo_livre_B = disp_B     

    def _criar_id (self):
        navios_ids = tuple(sorted([n['ID_Navio'] for n in self.navios_em_espera]))
        return (navios_ids, self.tempo_livre_A, self.tempo_livre_B)

    def __hash__(self):
        return hash(self._criar_id())

    def __eq__(self, other):
        if not isinstance(other, Estado_Porto):
            return NotImplemented
        return self._criar_id() == other._criar_id()




class Regras_Porto: #definir as regras e restrições que o porto apresenta
    def __init__(self, estado_inicial):
        self.estado_inicial = estado_inicial

    def e_estado_final(self, estado):
        return len(estado.navios_em_espera) == 0  # Estado final quando não há navios na fila

    def simular_sucessores(self, estado_atual):
        sucessores = []
        navios_fila = estado_atual.navios_em_espera

        for i, navio in enumerate(navios_fila):

            zona_possivel = []

            if navio['Tipo'] == 'Tipo 2': #aplicar restrição
                zona_possivel.append(('A', estado_atual.tempo_livre_A))
           
           else: 
                zona_possivel.append(('A', estado_atual.tempo_livre_A))
                zona_possivel.append(('B', estado_atual.tempo_livre_B))
            
            for zona_nome, tempo_livre_zona in zona_possivel:
                tempo_inicio_atracagem = max(navio['Hora_Chegada'], tempo_livre_zona) #restringir a capacidade
                custo_da_acao = tempo_inicio_atracagem - navio['Hora_Chegada'] #cálculo do tempo de espera


                novo_tempo_livre_zona = tempo_inicio_atracagem + navio['Duracao_Atracagem'] #perceber quando é que a zona ficará livre novamente

            
                nova_fila_espera = navios_fila[:i] + navios_fila[i+1:]#utilização dos principios da programação imperativa e utilizar a incrementação para remover o navio que foi atracado
                
                
                nova_disp_A = novo_tempo_livre_zona if zona_nome == 'A' else estado_atual.tempo_livre_A # Atualizar a disponibilidade quando A usada
                nova_disp_B = novo_tempo_livre_zona if zona_nome == 'B' else estado_atual.tempo_livre_B

                
                
                estado_sucessor = Estado_Porto( #programação orientada a objetos
                    navios_em_espera=nova_fila_espera,
                    disp_A=nova_disp_A,
                    disp_B=nova_disp_B,
                
                )

                sucessores.append((estado_sucessor, custo_da_acao))


        return sucessores


