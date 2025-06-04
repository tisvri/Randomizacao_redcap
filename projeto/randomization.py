import math
import random
import pandas as pd

# ==========================================
# 1) CONFIGURAÇÕES INICIAIS
# ==========================================
random.seed(42)

# 1.1) Número total de participantes no estudo
total_participantes = 100

# 1.2) DEFINIR OS CENTROS (Estrato 1)
#     Aqui listamos todos os IDs de centro (por exemplo, 5 centros: 1,2,3,4,5).
estrato_centros = [1, 2, 3, 4, 5]

# Verifica se o total de participantes é divisível pelo número de centros
numero_centros = len(estrato_centros)
assert total_participantes % numero_centros == 0, (
    f"O total de participantes ({total_participantes}) deve ser divisível "
    f"pelo número de centros ({numero_centros})."
)

# Participantes por centro
participantes_por_centro = total_participantes // numero_centros
# 100 / 5 = 20 participantes por centro

# 1.3) DEFINIR O ESTRATO 2: GÊNERO
estrato_genero = ['Masculino', 'Feminino']

# Em cada centro, queremos exatamente 50% Masculino e 50% Feminino
assert participantes_por_centro % 2 == 0, (
    f"Participantes por centro ({participantes_por_centro}) deve ser par "
    "para distribuir 50% Masculino e 50% Feminino."
)
participantes_por_genero_por_centro = participantes_por_centro // 2
# 20 / 2 = 10 por gênero em cada centro

# 1.4) PARÂMETROS DE RANDOMIZAÇÃO EM BLOCOS
#      Para blocos 1:1, o tamanho do bloco precisa ser par e deve dividir
#      exatamente 'participantes_por_genero_por_centro'.
#
#      Aqui escolhemos bloco de 10, porque 10 divisível por 10:
#      -> 10 participantes (por gênero × centro) → 1 bloco de 10
#      -> 5 Tratamento + 5 Placebo dentro desse bloco
tamanho_bloco = 10  
assert participantes_por_genero_por_centro % tamanho_bloco == 0, (
    f"O número de participantes por gênero em cada centro "
    f"({participantes_por_genero_por_centro}) deve ser divisível "
    f"pelo tamanho do bloco ({tamanho_bloco})."
)

# ==========================================
# 2) FUNÇÃO DE RANDOMIZAÇÃO EM BLOCOS
# ==========================================
def criar_blocos_randomizacao(tamanho_amostral: int, tamanho_bloco: int) -> list:
    """
    Gera uma lista de alocações em blocos de tamanho 'tamanho_bloco'
    para um determinado estrato (por exemplo, 10 participantes Masculino-centr0).
    A proporção dentro de cada bloco será sempre 1:1 (Tratamento vs Placebo).

    Retorna uma lista de strings de comprimento 'tamanho_amostral',
    contendo “Tratamento” ou “Placebo” embaralhados em blocos.
    """
    assert tamanho_amostral % tamanho_bloco == 0, (
        f"{tamanho_amostral} não é divisível por {tamanho_bloco}."
    )
    alocacao = []
    numero_blocos = tamanho_amostral // tamanho_bloco
    for _ in range(numero_blocos):
        # Dentro de cada bloco de tamanho_even, metade Tratamento e metade Placebo
        bloco = ['Tratamento'] * (tamanho_bloco // 2) + ['Placebo'] * (tamanho_bloco // 2)
        random.shuffle(bloco)
        alocacao.extend(bloco)
    return alocacao


# ==========================================
# 3) MONTAR REGISTROS (Centro → Gênero → Alocação)
# ==========================================
# Cada dicionário conterá: { 'Centro': int, 'Gênero': str, 'Alocação': str }
registros = []

for centro in estrato_centros:
    # 3.1) Gerar as alocações para os 10 participantes masculinos deste centro
    aloc_masculino = criar_blocos_randomizacao(
        participantes_por_genero_por_centro,
        tamanho_bloco
    )
    # 3.2) Gerar as alocações para os 10 participantes femininos deste centro
    aloc_feminino = criar_blocos_randomizacao(
        participantes_por_genero_por_centro,
        tamanho_bloco
    )

    # 3.3) Preencher registros Masculino neste centro
    for estudo in aloc_masculino:
        registros.append({
            'Centro': centro,
            'Gênero': 'Masculino',
            'Alocação': estudo
        })

    # 3.4) Preencher registros Feminino neste centro
    for estudo in aloc_feminino:
        registros.append({
            'Centro': centro,
            'Gênero': 'Feminino',
            'Alocação': estudo
        })


# ==========================================
# 4) CALCULAR QTD. DE AMPOLAS NECESSÁRIAS POR (Centro × Braço)
#    Aplicamos +50% de buffer e arredondamos para cima (math.ceil).
# ==========================================
# Primeiro, convertemos 'registros' em DataFrame para facilitar contagens
df_registros = pd.DataFrame(registros)

# Vamos criar um dicionário que guardará, para cada tupla (centro, braço),
# quantas ampolas precisamos gerar.
ampoules_needed = {}  # chave = (centro, 'Tratamento' ou 'Placebo'), valor = quantidade_int

for centro in estrato_centros:
    for braco in ['Tratamento', 'Placebo']:
        # Contar quantos participantes masculinos neste (centro, braco)
        qtd_masc = df_registros[
            (df_registros['Centro'] == centro) &
            (df_registros['Gênero'] == 'Masculino') &
            (df_registros['Alocação'] == braco)
        ].shape[0]

        # Contar quantos participantes femininos neste (centro, braco)
        qtd_fem = df_registros[
            (df_registros['Centro'] == centro) &
            (df_registros['Gênero'] == 'Feminino') &
            (df_registros['Alocação'] == braco)
        ].shape[0]

        # Cada homem precisa de 2 ampolas, cada mulher de 1
        necessidade_base = qtd_masc * 2 + qtd_fem * 1

        # Aplicar +50% de buffer
        necessidade_com_buffer = math.ceil(necessidade_base * 1.5)

        ampoules_needed[(centro, braco)] = necessidade_com_buffer

# ==========================================
# 5) GERAR OS CÓDIGOS DE ETIQUETA PARA CADA (Centro, Braço)
# ==========================================
def gerar_etiquetas_ampolas(centro: int, braco: str, quantidade: int) -> list:
    """
    Para um dado centro e braço, gera N etiquetas no formato:
       'centro_{centro}_{B}{XXX}'
    onde:
       B = primeira letra do braço (T ou P)
       XXX = número sequencial com zero-padding (001, 002, ... até quantidade)
    Embaralha antes de retornar para garantir aleatoriedade de distribuição.
    """
    prefixo = f"centro_{centro}_{braco[0].upper()}"
    etiquetas = [f"{prefixo}{i:03d}" for i in range(1, quantidade + 1)]
    random.shuffle(etiquetas)
    return etiquetas

# Montamos um dicionário de pools de etiquetas:
#   key = (centro, braco), value = lista embaralhada de etiquetas desse pool
etiquetas_pools = {}

for (centro, braco), qtd in ampoules_needed.items():
    etiquetas_pools[(centro, braco)] = gerar_etiquetas_ampolas(centro, braco, qtd)


# ==========================================
# 6) ATRIBUIR ETIQUETAS A CADA PARTICIPANTE
#    - Homens retiram 2 ampolas do pool (centro, braço)
#    - Mulheres retiram 1 ampola e a segunda coluna fica vazia
# ==========================================
# Vamos percorrer 'df_registros' em ordem e “pop()” etiquetas do pool correto
lista_amp1 = []
lista_amp2 = []

for idx, row in df_registros.iterrows():
    centro = row['Centro']
    braco = row['Alocação']       # 'Tratamento' ou 'Placebo'
    genero = row['Gênero']        # 'Masculino' ou 'Feminino'
    pool_key = (centro, braco)

    if genero == 'Masculino':
        # Homens levam duas ampolas
        etiqueta1 = etiquetas_pools[pool_key].pop()
        etiqueta2 = etiquetas_pools[pool_key].pop()
        lista_amp1.append(etiqueta1)
        lista_amp2.append(etiqueta2)
    else:
        # Mulheres levam uma ampola; a segunda coluna fica vazia
        etiqueta1 = etiquetas_pools[pool_key].pop()
        lista_amp1.append(etiqueta1)
        lista_amp2.append('')

# Adiciona as colunas ao DataFrame
df_registros['Etiqueta_Ampola_1'] = lista_amp1
df_registros['Etiqueta_Ampola_2'] = lista_amp2


# ==========================================
# 7) INSERIR 'randomization_id' E ORDENAR COLUNAS
# ==========================================
df_registros.insert(
    loc=0,
    column='randomization_id',
    value=range(1, len(df_registros) + 1)
)

# Reordena colunas para exibir: randomization_id, Centro, Gênero, Alocação, Amp1, Amp2
colunas_ordenadas = [
    'randomization_id',
    'Centro',
    'Gênero',
    'Alocação',
    'Etiqueta_Ampola_1',
    'Etiqueta_Ampola_2'
]
df_registros = df_registros[colunas_ordenadas]


# ==========================================
# 8) EXPORTAR PARA CSV
# ==========================================
output_file = 'randomization_table_com_centros.csv'
df_registros.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"Tabela gerada com sucesso: '{output_file}' → {len(df_registros)} linhas.")
