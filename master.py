### ---------- PARA USO DA GGDP ---------- ###

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import openpyxl as px

MIN_DATE = datetime(2024, 1, 1)
MAX_DATE = datetime(2050, 12, 31)
DATA_CONCLUSAO = 7306 # aprox. 20 anos em dias 

st.set_page_config(page_title="GGDP", layout="wide")

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- COLETA DOS DADOS ---------- ###

carreira = [[0 for _ in range(10)] for _ in range(DATA_CONCLUSAO)]
# arquivo = st.file_uploader("Arquivo", type=["xlsx","xls"])

# if arquivo is not None:
#     arq = px.load_workbook(arquivo) #a brir arquivo 
#     aba = arq.active # pega a aba ativa
#     data = aba.values # pega valores das celulas
#     cols = next(data) # primeira coluna 
#     ind = [i for i, col in enumerate(cols) if col is not None and str(col).strip() != ''] # criar uma lista com os indices das colunas que tem nome valido
#     filtro_cols = [cols[i] for i in ind] # pega o nome das colunas validas
#     data = list(data) # converte em uma lista
#     filtro_data = [[row[i] for i in ind] for row in data] # filtar as linhas validas

#     df = pd.DataFrame(data=filtro_data, columns=filtro_cols).drop_duplicates()
#     st.dataframe(df)

### ---------- NÃO CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- PONTOS PADRÕES ---------- ###

if "obrigatorios" not in st.session_state:
    st.session_state.obrigatorios = []  # Lista de (mes, faltas)

st.subheader("Obrigatorios")

col = st.columns([2, 2, 2])
with col[0]:
    data_inicial = st.date_input("Data do Enquadramento ou Ultima Evolução", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE)
with col[1]:
    pts_remanescentes = st.number_input("Pontos Remanescentes da Última Evolução", min_value=0.000)
with col[2]:
    if st.button("Adicionar", key="obg"):
        if pts_remanescentes > 0:
            st.session_state.obrigatorios.append((data_inicial, pts_remanescentes))

# Mostrar afastamentos cadastrados
if st.session_state.obrigatorios:
    st.write("**Pontos Vindos da Última Evolução:**")
    cols = st.columns(6)
    for i, (data, pts) in enumerate(st.session_state.obrigatorios):
        col = cols[i % 6]  # escolhe a coluna certa
        with col:
            st.write(f"{pts} ponto(s) ")
            if st.button(f"Remover", key=f"remover_obg{i}"):
                st.session_state.obrigatorios.pop(i)
                st.rerun() 

if "afastamentos" not in st.session_state:
    st.session_state.afastamentos = []  # Lista de (mes, faltas)

st.subheader("Afastamentos")

# Entrada de um novo afastamento
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    mes_novo = st.date_input("Mês", format="DD/MM/YYYY", value=data_inicial, min_value=MIN_DATE, max_value=MAX_DATE, key="mes_afast", help="SERÁ CONTADO SERÁ SOMENTE O MÊS")
with col2:
    faltas_novo = st.number_input("Faltas", min_value=0, step=1, key="qntd_afast")
with col3:
    if st.button("Adicionar", key="afast"):
        if faltas_novo > 0:
            st.session_state.afastamentos.append((mes_novo, faltas_novo))

# Mostrar afastamentos cadastrados
if st.session_state.afastamentos:
    st.write("**Afastamentos cadastrados:**")
    cols = st.columns(6)
    for i, (mes, faltas) in enumerate(st.session_state.afastamentos):
        col = cols[i % 6]  # escolhe a coluna certa
        with col:
            st.write(f"{mes.strftime('%m/%Y')} → {faltas} falta(s) |")
            if st.button(f"Remover", key=f"remover_afast{i}"):
                st.session_state.afastamentos.pop(i)
                st.rerun()    

#datas em meses#
carreira = [
    [data_inicial + timedelta(days=i)] + [0] * 9
    for i in range(DATA_CONCLUSAO)
]

#pontos_base#
for i in range(len(carreira)):
    data_atual = carreira[i][0]

    # procura se existe afastamento nesse mês
    faltas_mes = next((faltas for mes, faltas in st.session_state.afastamentos
                       if data_atual.month == mes.month and data_atual.year == mes.year), 0)

    desconto = 0.0067 * faltas_mes
    desconto_des = 0.05 * faltas_mes

    # Pega o primeiro dia do próximo mês
    if data_atual.month == 12:
        prox_mes = datetime(data_atual.year + 1, 1, 1)
    else:
        prox_mes = datetime(data_atual.year, data_atual.month + 1, 1)

    ultimo_dia_mes = prox_mes - timedelta(days=1)

    if (data_atual.year == ultimo_dia_mes.year and
    data_atual.month == ultimo_dia_mes.month and
    data_atual.day == ultimo_dia_mes.day):
        
        carreira[i][1] = 0.2
        carreira[i][3] = 1.5
        carreira[i][2] = max(min(0.2 - desconto, 0.2), 0)
        carreira[i][4] = max(min(1.5 - desconto_des, 1.5), 0)
        
    else:
        carreira[i][1] = carreira[i][2] = carreira[i][3] = carreira[i][4] = 0

### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- APERFEIÇOAMENTO ---------- ###

if "aperfeicoamentos" not in st.session_state:
    st.session_state.aperfeicoamentos = []
    
st.subheader("Aperfeiçoamento")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    data_conclusao = st.date_input("Data de Conclusão", format="DD/MM/YYYY", value=data_inicial, min_value=MIN_DATE, max_value=MAX_DATE, key="mes_aperf")
with col2:
    horas_curso = st.number_input("Horas do Curso", min_value=0, step=1, key="hrs_aperf")
with col3:
    if st.button("Adicionar", key="aperf"):
        if data_conclusao:
            st.session_state.aperfeicoamentos.append((data_conclusao, horas_curso))

# Mostrar aperfeiçoamentos cadastrados
if st.session_state.aperfeicoamentos:
    st.write("**Aperfeiçoamentos cadastrados:**")
    cols = st.columns(6)
    for j, (data, horas) in enumerate(st.session_state.aperfeicoamentos):
        col = cols[j % 6]  # escolhe a coluna certa
        with col:
            st.write(f"{data.strftime('%d/%m/%Y')} → {horas} hora(s) |")
            if st.button(f"Remover", key=f"remover_aperf{j}"):
                st.session_state.aperfeicoamentos.pop(j)
                st.rerun()    

total_horas = 0  

# Percorre todos os aperfeiçoamentos cadastrados
for data_conclusao, horas_curso in st.session_state.aperfeicoamentos:
    # Quanto desse curso ainda pode ser aproveitado
    horas_restantes = max(0, 100 - total_horas)
    horas_aproveitadas = min(horas_curso, horas_restantes)

    # Atualiza acumulado de horas
    total_horas += horas_aproveitadas

    # Só calcula pontos se ainda tiver horas aproveitáveis
    if horas_aproveitadas > 0:
        pontos = horas_aproveitadas * 0.09

        # Encontra a linha na matriz carreira e insere os pontos
        for idx, linha in enumerate(carreira):
            data_linha = linha[0]
            if (data_linha.year == data_conclusao.year and 
                data_linha.month == data_conclusao.month and 
                data_linha.day == data_conclusao.day):
                carreira[idx][5] += pontos
                break

### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- TITULAÇÕES ---------- ###

# Valores fixos para cada titulação
valores_tit = {
    'Graduação': 6,   # Graduação
    'Especialização': 12,   # Especialização
    'Mestrado': 24,  # Mestrado
    'Doutorado': 48    # Doutorado
}

# Dicionário para armazenar as datas preenchidas pelo usuário
data_titulos = {}

if "titulacoes" not in st.session_state:
    st.session_state.titulacoes = []
    
st.subheader("Titulações")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    data_conclusao_tit = st.date_input("Data de Conclusão", format="DD/MM/YYYY", value=data_inicial, min_value=MIN_DATE, max_value=MAX_DATE, key="mes_tit")
with col2:
    tipo_tit = st.selectbox("Tipo", list(valores_tit.keys()))
    
with col3:
    if st.button("Adicionar", key="tit"):
        if data_conclusao_tit:
            st.session_state.titulacoes.append((data_conclusao_tit, tipo_tit))

# Mostrar aperfeiçoamentos cadastrados
if st.session_state.titulacoes:
    st.write("**Titulações cadastradas:**")
    cols = st.columns(6)
    for idx, (data, tipo) in enumerate(st.session_state.titulacoes):
        col = cols[idx % 6]
        with col:
            st.write(f"{data.strftime('%d/%m/%Y')} → {tipo} |")
            if st.button("Remover", key=f"remover_tit{idx}"):
                st.session_state.titulacoes.pop(idx)
                st.rerun()  


total_pontos_tit = 0
LIMITE_TIT = 144

for data_concl, tipo in st.session_state.titulacoes:
    pontos_titulo = valores_tit.get(tipo, 0)
    pontos_restantes = max(0, LIMITE_TIT - total_pontos_tit)
    pontos_aproveitados = min(pontos_titulo, pontos_restantes)
    total_pontos_tit += pontos_aproveitados

    if pontos_aproveitados > 0:
        for i, linha in enumerate(carreira):
            d = linha[0]
            if d.year == data_concl.year and d.month == data_concl.month and d.day == data_concl.day:
                carreira[i][6] += pontos_aproveitados
                break

### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- RESPONSABILIDADES ÚNICAS ---------- ###

if "resp_unicas" not in st.session_state:
    st.session_state.resp_unicas = []

st.subheader("Responsabilidades Únicas")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    data_resp_unic = st.date_input("Data de Conclusão", format="DD/MM/YYYY", value=data_inicial, min_value=MIN_DATE, max_value=MAX_DATE, key="m_resp_unic")
with col2:
    pontos_resp_unic = st.number_input("Pontos Responsabilidades", min_value=0, key="pts_ru")
with col3:
    if st.button("Adicionar", key="resp_uni"):
        if data_resp_unic and pontos_resp_unic > 0:
            st.session_state.resp_unicas.append((data_resp_unic, pontos_resp_unic))

# Mostrar responsabilidades cadastradas em 6 colunas
if st.session_state.resp_unicas:
    st.write("**Responsabilidades Únicas cadastradas:**")
    cols = st.columns(6)
    for idx, (data, pontos_u) in enumerate(st.session_state.resp_unicas):
        col = cols[idx % 6]
        with col:
            st.write(f"{data.strftime('%d/%m/%Y')} → {pontos_u} ponto(s)")
            if st.button("Remover", key=f"remover_ru{idx}"):
                st.session_state.resp_unicas.pop(idx)
                st.rerun()

# Processa pontos por data e aplica na carreira
resp_dict = {}
for data, pontos in st.session_state.resp_unicas:
    if data in resp_dict:
        resp_dict[data] += pontos
    else:
        resp_dict[data] = pontos

pontos_acumulados_resp = 0
LIMITE_RESP = 144

for data_resp, pontos in resp_dict.items():
    # Ajusta para não ultrapassar limite
    if pontos_acumulados_resp + pontos > LIMITE_RESP:
        pontos = max(0, LIMITE_RESP - pontos)
    if pontos <= 0:
        continue

    # Aplica na matriz carreira
    for i, linha in enumerate(carreira):
        d = linha[0]
        if d.year == data_resp.year and d.month == data_resp.month and d.day == data_resp.day:
            carreira[i][7] = pontos
            pontos_acumulados_resp += pontos
            break

### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- RESPONSABILIDADES MENSAIS ---------- ###

if "resp_mensais" not in st.session_state:
    st.session_state.resp_mensais = []
    
st.subheader("Responsabilidades Mensais")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    data_resp_mensal = st.date_input("Data de Início", format="DD/MM/YYYY", value=data_inicial, min_value=MIN_DATE, max_value=MAX_DATE, key="m_resp_mes")
with col2:
    pontos_resp_mensal = st.number_input("Pontos de Responsabilidade p/Mês", min_value=0.0000, key="pts_rm")
with col3:
    qntd_meses_resp_m = st.number_input("Quantidade de Meses", min_value=0, key="qntd_rm")
with col4:
    if st.button("Adicionar", key="resp_mes"):
        if data_resp_mensal and pontos_resp_mensal > 0 and qntd_meses_resp_m > 0:
            st.session_state.resp_mensais.append((data_resp_mensal, pontos_resp_mensal, qntd_meses_resp_m))

# Mostrar aperfeiçoamentos cadastrados
if st.session_state.resp_mensais:
    st.write("**Responsabilidades Mensais cadastradas:**")
    cols = st.columns(6)
    for idx3, (data, pontos_m, qntd_m) in enumerate(st.session_state.resp_mensais):
        col = cols[idx3 % 6]  # escolhe a coluna certa
        with col:
            st.write(f"{data.strftime('%d/%m/%Y')} → {pontos_m:.3f} ponto(s) → Durante {qntd_m} mês(es)")
            if st.button(f"Remover", key=f"remover_rm{idx3}"):
                st.session_state.resp_mensais.pop(idx3)
                st.rerun()    

# Exemplo de dados do usuário
responsabilidades_mensais = [
    {
        'data_inicio': data_resp_mensal,
        'meses': qntd_meses_resp_m,
        'pontos_mensais': pontos_resp_mensal
    }
]

for resp in responsabilidades_mensais:
    inicio = resp['data_inicio']
    meses = resp['meses']
    pontos = resp['pontos_mensais']
    
    for i in range(len(carreira)):
        d = carreira[i][0]
        
        # Verifica se d é último dia do mês
        prox_dia = d + timedelta(days=1)
        if prox_dia.day != 1:
            continue  # Não é último dia, pula
        
        # Verifica se d está dentro do período da responsabilidade
        delta_ano = d.year - inicio.year
        delta_mes = d.month - inicio.month
        total_meses = delta_ano * 12 + delta_mes
        
        if 0 <= total_meses < meses:
            carreira[i][8] = pontos

### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- ACUMULADO ---------- ###

for i in range(DATA_CONCLUSAO):
    if i == 0 and pts_remanescentes > 0:
        carreira[i][9] = carreira[i-1][9] + carreira[i][2] + carreira[i][4] + (carreira[i][5]/24) + carreira[i][6] + carreira[i][7] + carreira[i][8] + pts_remanescentes 
    else:
        carreira[i][9] = carreira[i-1][9] + carreira[i][2] + carreira[i][4] + (carreira[i][5]/24) + carreira[i][6] + carreira[i][7] + carreira[i][8] 
### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- DATAFRAME DE CONTROLE ---------- ###

# Criar DataFrame com as colunas
df_carreira = pd.DataFrame(carreira, columns=[
    "Data",
    "Pontos Base (0.2)",
    "Pontos Base Descontado",
    "Desempenho",
    "Desempenho Descontado",
    "Aperfeiçoamento",
    "Titulação",
    "Resp. Únicas",
    "Resp. Mensais",
    "Total Acumulado" 
])

# Arredondar para 4 casas decimais
df_carreira = df_carreira.round(4)

# Selecionar meses para exibição (primeiros 12 + um por ano após)
meses_exibir = list(range(DATA_CONCLUSAO))
df_exibir = df_carreira.iloc[meses_exibir]

# Configurar formatação de exibição
pd.options.display.float_format = '{:.4f}'.format

# Mostrar tabela com colunas selecionadas
st.dataframe(
    df_exibir[[
        "Data",
        "Pontos Base (0.2)",
        "Pontos Base Descontado",
        "Desempenho",
        "Desempenho Descontado",
        "Aperfeiçoamento",
        "Titulação",
        "Resp. Únicas",
        "Resp. Mensais",
        "Total Acumulado" 
    ]],
    height=600,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Data": st.column_config.DateColumn(format="DD/MM/YYYY"),
        "Pontos Base (0.2)": st.column_config.NumberColumn(format="%.4f"),
        "Pontos Base Descontado": st.column_config.NumberColumn(format="%.4f"),
        "Desempenho": st.column_config.NumberColumn(format="%.4f"),
        "Desempenho Descontado": st.column_config.NumberColumn(format="%.4f"),
        "Aperfeiçoamento": st.column_config.NumberColumn(format="%.4f"),
        "Titulação": st.column_config.NumberColumn(format="%.4f"),
        "Resp. Únicas":st.column_config.NumberColumn(format="%.4f"),
        "Resp. Mensais": st.column_config.NumberColumn(format="%.4f"),
        "Total Acumulado": st.column_config.NumberColumn(format="%.4f")
    }
)

### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- CÁLCULO DE TEMPO ---------- ###

resultado_niveis = []

# Dados iniciais
data_inicio = carreira[0][0]  # primeira data 
evolucao = None
meses_ate_evolucao = None
pts_resto = None

for i in range(DATA_CONCLUSAO):
    data_atual = carreira[i][0]
    pontos = carreira[i][9]

    meses_passados = (data_atual.year - data_inicio.year) * 12 + (data_atual.month - data_inicio.month)

    # Regra do mínimo de meses
    if meses_passados < 12:
        continue

    if 12 <= meses_passados < 18:
        if pontos >= 96:
            evolucao = data_atual
            meses_ate_evolucao = meses_passados
            break

    if meses_passados >= 18:
        if pontos >= 96 or pontos >= 48:
            evolucao = data_atual
            meses_ate_evolucao = meses_passados
            break

pts_evo = pontos
pts_resto = pts_evo - 48

if evolucao:
    resultado_niveis.append({
        "Data da Próxima Evolução": evolucao.strftime("%d/%m/%Y"),
        "Meses Gastos para Evolução": meses_ate_evolucao,
        "Pontos Remanescentes": pts_resto
    })

df_resultados = pd.DataFrame(resultado_niveis)
st.dataframe(df_resultados, hide_index=True, height=700)

### ---------- CONCLUIDO ---------- ###