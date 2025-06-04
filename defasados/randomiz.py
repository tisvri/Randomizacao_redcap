import random
import pandas as pd
import csv

# ==========================================
# Configurações iniciais
# ==========================================
# Semente para reprodutibilidade (opcional)
random.seed(123)

# Total de participantes no estudo
total_participants = 200

# Verifica se o total é par e divisible por 2 (para estratificação 50%/50%)
assert total_participants % 2 == 0, f"Total de participantes ({total_participants}) não é par."

# Número de participantes por gênero (50% Masculino, 50% Feminino)
participants_per_gender = total_participants // 2  # = 100

# Tamanho do bloco para randomização em blocos
block_size = 4

# Verifica se cada estrato é divisível pelo tamanho do bloco
assert participants_per_gender % block_size == 0, (
    f"Participantes por gênero ({participants_per_gender}) não são divisíveis por block_size ({block_size})."
)


# ==========================================
# Função de Randomização em Blocos
# ==========================================
def generate_block_randomization(num_participants: int, block_size: int) -> list:
    """
    Gera uma lista de alocações em blocos de tamanho 'block_size' 
    para num_participants, com proporção 1:1 entre Tratamento e Placebo.
    
    Retorna uma lista de strings: ['Tratamento' ou 'Placebo'] de comprimento num_participants.
    """
    assert num_participants % block_size == 0, (
        f"{num_participants} não é divisível por {block_size}."
    )
    
    assignments = []
    num_blocks = num_participants // block_size
    for _ in range(num_blocks):
        # Monta um bloco com metade Tratamento e metade Placebo
        block = ['Tratamento'] * (block_size // 2) + ['Placebo'] * (block_size // 2)
        random.shuffle(block)            # Embaralha as posições dentro do bloco
        assignments.extend(block)        # Adiciona o bloco embaralhado à lista final
    
    return assignments


# ==========================================
# 1) Gera alocações por estrato de gênero
# ==========================================
# Para 100 participantes masculinos:
male_assignments = generate_block_randomization(participants_per_gender, block_size)

# Para 100 participantes femininos:
female_assignments = generate_block_randomization(participants_per_gender, block_size)


# ==========================================
# 2) Monta lista de registros sem ampoulas
# ==========================================
# Cada registro conterá: gender, study_group.
records = []

# Primeiro preenche os registros masculinos
for group in male_assignments:
    records.append({
        'gender': 'Masculino',
        'study_group': group
    })

# Em seguida, preenche os registros femininos
for group in female_assignments:
    records.append({
        'gender': 'Feminino',
        'study_group': group
    })


# ==========================================
# 3) Conta quantas ampolas serão necessárias
# ==========================================
# Para o grupo "Tratamento":
# - Homens: 2 ampolas por participante
# - Mulheres: 1 ampola por participante
male_treatment_count = sum(1 for r in records if r['gender'] == 'Masculino' and r['study_group'] == 'Tratamento')
female_treatment_count = sum(1 for r in records if r['gender'] == 'Feminino'  and r['study_group'] == 'Tratamento')

total_treatment_ampoules = male_treatment_count * 2 + female_treatment_count * 1

# Para o grupo "Placebo":
male_placebo_count = sum(1 for r in records if r['gender'] == 'Masculino' and r['study_group'] == 'Placebo')
female_placebo_count = sum(1 for r in records if r['gender'] == 'Feminino'  and r['study_group'] == 'Placebo')

total_placebo_ampoules = male_placebo_count * 2 + female_placebo_count * 1

# ==========================================
# 4) Gera e embaralha listas de códigos de ampolas
# ==========================================
# Função auxiliar para criar códigos com prefixo e zero-padding
def generate_ampoule_codes(prefix: str, quantity: int) -> list:
    """
    Gera uma lista de códigos de ampola do tipo '{prefix}-{NNN}', 
    onde NNN vai de 001 até quantity.
    """
    codes = [f"{prefix}-{i:03d}" for i in range(1, quantity + 1)]
    random.shuffle(codes)
    return codes

# Gera lista embaralhada de ampolas de Tratamento: prefixo "T-"
treatment_ampoules = generate_ampoule_codes('T', total_treatment_ampoules)

# Gera lista embaralhada de ampolas de Placebo: prefixo "P-"
placebo_ampoules = generate_ampoule_codes('P', total_placebo_ampoules)


# ==========================================
# 5) Atribui ampolas a cada participante
# ==========================================
for r in records:
    group = r['study_group']
    gender = r['gender']
    
    if group == 'Tratamento':
        # Remove da lista treatment_ampoules conforme gênero
        if gender == 'Masculino':
            # Homens recebem duas ampolas
            r['ampoule_number_1'] = treatment_ampoules.pop()
            r['ampoule_number_2'] = treatment_ampoules.pop()
        else:
            # Mulheres recebem uma ampola; segunda coluna vazia
            r['ampoule_number_1'] = treatment_ampoules.pop()
            r['ampoule_number_2'] = ''
    else:  # Placebo
        if gender == 'Masculino':
            r['ampoule_number_1'] = placebo_ampoules.pop()
            r['ampoule_number_2'] = placebo_ampoules.pop()
        else:
            r['ampoule_number_1'] = placebo_ampoules.pop()
            r['ampoule_number_2'] = ''


# ==========================================
# 6) Atribui randomization_id e monta DataFrame
# ==========================================
# randomization_id sequencial de 1 a 200
for idx, r in enumerate(records, start=1):
    r['randomization_id'] = idx

# Reordena colunas para coincidir com saída desejada
ordered_columns = ['randomization_id', 'gender', 'study_group', 'ampoule_number_1', 'ampoule_number_2']

# Cria DataFrame
df = pd.DataFrame(records)[ordered_columns]

# ==========================================
# 7) Exporta para CSV
# ==========================================
output_filename = 'randomization_table_2.csv'
df.to_csv(output_filename, index=False, encoding='utf-8-sig')

print(f"Tabela de randomização gerada em '{output_filename}' com {len(df)} registros.")
