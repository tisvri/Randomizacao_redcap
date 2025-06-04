import random
import itertools
import pandas as pd

def gerar_blocos_permutados(grupos, racio, tamanho_bloco, seed=None):
    """
    Retorna uma lista “embaralhada” de blocos, onde cada bloco é uma tupla de grupos.
    - grupos: lista de strings, ex.: ["A", "B", "C"]
    - racio: lista de inteiros, ex.: [2, 1, 1] (significa 2 de "A", 1 de "B", 1 de "C")
    - tamanho_bloco: inteiro, ex.: sum(racio)
    - seed: valor inteiro para random.seed (opcional)
    """
    if seed is not None:
        random.seed(seed)
    # Montar o bloco base, ex.: ["A","A","B","C"]
    bloco_base = []
    for g, qty in zip(grupos, racio):
        bloco_base.extend([g] * qty)
    # Gerar todas as permutações únicas do bloco_base
    permutacoes = set(itertools.permutations(bloco_base, tamanho_bloco))
    permutacoes = list(permutacoes)
    random.shuffle(permutacoes)
    return permutacoes

def criar_lista_randomizacao_simples(n_total, grupos, racio, tamanho_bloco, seed=None):
    """
    Gera a lista completa de randomização sem estratificação.
    Retorna um DataFrame pandas com colunas: ['ID_Participante', 'Grupo_Alocado'].
    """
    if seed is not None:
        random.seed(seed)
    blocos = gerar_blocos_permutados(grupos, racio, tamanho_bloco, seed)
    
    # Quantos blocos serão necessários para atingir n_total
    n_blocos = (n_total + tamanho_bloco - 1) // tamanho_bloco  # arredonda pra cima
    lista_total = []
    
    bloco_idx = 0
    for i in range(n_blocos):
        # Seleciona um bloco permutado
        bloco = blocos[bloco_idx % len(blocos)]
        bloco_idx += 1
        for grupo in bloco:
            lista_total.append(grupo)
    # Trunca para n_total exato
    lista_total = lista_total[:n_total]
    
    # Monta DataFrame
    df = pd.DataFrame({
        'ID_Participante': list(range(1, n_total + 1)),
        'Grupo_Alocado': lista_total
    })
    return df

def criar_lista_stratificada(n_total, grupos, racio, tamanho_bloco, seed, estratos, proporcoes_estrato):
    """
    Gera lista randomizada estratificada.
    - estratos: lista de dicionários, ex.: [
          {'nome': 'Sexo_M', 'prop': 0.5},
          {'nome': 'Sexo_F', 'prop': 0.5},
      ]
    - proporcoes_estrato: dicionário de proporções para combinações, ex.:
      {
        'Sexo_M_Idade_<=60': 0.25,
        'Sexo_M_Idade_>60': 0.25,
        'Sexo_F_Idade_<=60': 0.25,
        'Sexo_F_Idade_>60': 0.25
      }
    (Nesse exemplo, 4 estratos igualmente ponderados)
    """
    if seed is not None:
        random.seed(seed)
    df_final = []
    participante_global = 1
    
    # Exemplo de chaves: "Sexo_M_Idade_<=60" etc.
    for chave_estrato, prop in proporcoes_estrato.items():
        n_estrato = int(round(prop * n_total))
        # Gera randomização dentro desse estrato
        df_estrato = criar_lista_randomizacao_simples(
            n_estrato, grupos, racio, tamanho_bloco, seed
        )
        # Adiciona uma coluna de estrato e ajusta IDs participantes
        df_estrato.insert(0, 'Estrato', chave_estrato)
        df_estrato['ID_Participante_Global'] = list(range(participante_global, participante_global + n_estrato))
        participante_global += n_estrato
        df_final.append(df_estrato)
    
    # Concatena todos os DataFrames por estrato
    df_concat = pd.concat(df_final, ignore_index=True)
    # Reordena colunas (opcional)
    df_concat = df_concat[['ID_Participante_Global', 'Estrato', 'ID_Participante', 'Grupo_Alocado']]
    return df_concat

if __name__ == "__main__":
    # 1. Definições iniciais
    grupos = ["Controle", "Tratamento"]
    # Razão 1:1 → rácio = [12, 1], bloco de tamanho 2
    racio = [2,2]  # Exemplo: 2 de "Controle", 2 de "Tratamento"
    # Tamanho do bloco é a soma dos rácio
    tamanho_bloco = sum(racio)  # = 2
    n_total = 100
    seed = 42
    proporcoes_estrato = {
        'Masculino': 0.5,
        'Feminino': 0.5
    }
    # Mantém mesmos grupos e rácio de alocação.
    df_strat = criar_lista_stratificada(
        n_total, grupos, racio, tamanho_bloco, seed, estratos=None, proporcoes_estrato=proporcoes_estrato
    )
    print("\nRandomização Estratificada (exemplo):")
    print(df_strat.head(10))
    # Salvar em CSV, se desejar
    df_strat.to_csv("randomizacao_estratificada.csv", index=False)
    print("\nTotal de participantes:", len(df_strat))
    print("Estratos únicos:", df_strat['Estrato'].unique())
    print("Grupos alocados únicos:", df_strat['Grupo_Alocado'].unique())
    print("Exemplo de IDs participantes:", df_strat['ID_Participante_Global'].head(10).tolist())
    print("Proporção de cada estrato:" , df_strat['Estrato'].value_counts(normalize=True).to_dict())
    print("Proporção de cada grupo alocado:", df_strat['Grupo_Alocado'].value_counts(normalize=True).to_dict())
    print("Proporção de cada estrato por grupo alocado:" , df_strat.groupby(['Estrato', 'Grupo_Alocado']).size().unstack(fill_value=0).to_dict())
    # print("Tabela de randomização estratificada:" , df_strat.pivot_table(index='Estrato', columns='Grupo_Alocado', aggfunc='size', fill_value=0).to_dict())
    # print("Tabela de randomização estratificada (com margens):", df_strat.pivot_table(index='Estrato', columns='Grupo_Alocado', aggfunc='size', fill_value=0, margins=True).to_dict())