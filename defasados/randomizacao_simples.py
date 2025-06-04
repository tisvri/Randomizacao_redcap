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

if __name__ == "__main__":
    # 1. Definições iniciais
    grupos = ["Controle", "Tratamento"]
    # Razão 1:1 → rácio = [1, 1], bloco de tamanho 2
    racio = [1, 1]
    tamanho_bloco = sum(racio)  # = 2
    n_total = 120
    seed = 42

    # 2. Gera randomização simples (não estratificada)
    df_random = criar_lista_randomizacao_simples(n_total, grupos, racio, tamanho_bloco, seed)
    print("Randomização Simples (sem estratos):")
    print(df_random.head(10))
    
    # Salvar em CSV, se desejar
    df_random.to_csv("randomizacao_simples.csv", index=False)