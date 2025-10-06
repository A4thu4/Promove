import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

DATA_CONCLUSAO = 3654 # 10 anos [7306 - 20 anos] (em dias)
MIN_DATE = datetime(2000, 1, 1).date()
MAX_DATE = datetime(2050, 12, 31).date()
NIVEIS = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S']


val_states = {
    "data_inicial": None, "data_fim": None, "nivel_atual": None, "pts_ultima_evolucao": None, "carreira": [], "resultados_carreira": [],
    "obrigatorios": [], "afastamentos": [], "aperfeicoamentos": [], "titulacoes": [],
    "resp_mensais": [], 
    "comissao_lista": [], "func_c_lista": [], "func_d_lista": [], 
    "agente_lista": [], "conselho_lista": [], "prioritaria_lista": [], 
    "resp_unicas":[], 
    "artigos_lista": [], "livros_lista": [], "pesquisas_lista": [], 
    "registros_lista": [], "cursos_lista": [],
    "calculo_executado": False
}

# ---- TITULAÇÕES ---- #

dados_tit = {
    'Nenhuma': None,
    'Graduação': 6,
    'Especialização': 8,
    'Mestrado': 24,
    'Doutorado': 48
}

# ---- RESPONSABILIDADES UNICAS ---- #

dados_artigo = {
    'Nenhum': 0,
    'NÃO Indexado': 0.5,
    'Indexado': 4
}

dados_livro = {
    'Nenhum': 0,
    'Organizador': 1,
    'Capitulo': 4,
    'Livro Completo': 6
}

dados_pesquisas = {
    'Nennhum': 0,
    'Estadual': 1,
    'Regional': 3,
    'Nacional': 3,
    'Internacional': 4
}

dados_registros = {
    'Nenhum': 0,
    'Patente': 8,
    'Cultivar':8
}

dados_cursos = {
    'Nenhum': 0,
    'Estágio Pós-Doutoral no Orgão (6 meses)': 6,   
    'Pós-Doutorado (6 a 12 meses)': 8,   
    'Pós-Doutorado (13 a 24 meses)': 12,  
    'Pós-Doutorado (25 a 48 meses)': 24,
    'Pós-Doutorado (maior que 48 meses)': 48  
}

# ---- RESPONSABILIDADES MENSAIS ---- #

dados_cargos = {
    'Nenhum': 0,
    "DAS-1": 1.000, "DAS-2": 1.000,
    "DAS-3": 0.889, "DAS-4": 0.889,
    "DAS-5": 0.800, "DAS-6": 0.800, "DAS-7": 0.800, "DAID-1A": 0.800, "AEG": 0.800,
    "DAI-1": 0.667, "DAID-1": 0.667, "DAID-1B": 0.667, "DAID-2": 0.667, "AE-1": 0.667, "AE-2": 0.667,
    "DAI-2": 0.500, "DAI-3": 0.500, "DAID-4": 0.500, "DAID-5": 0.500, "DAID-6": 0.500, "DAID-7": 0.500,
    "DAID-8": 0.500, "DAID-9": 0.500, "DAID-10": 0.500, "DAID-11": 0.500, "DAID-12": 0.500,
    "DAID-13": 0.500, "DAID-14": 0.500
}

dados_func_c = {
    'Nenhum': 0,
    "até R$ 750,00": 0.333, 
    " 751,00 - 1.200,00": 0.364, 
    " 1.201,00 - 1.650,00": 0.400, 
    " 1.651,00 - 2.250,00": 0.444,  
    "acima de 2.250,00": 0.500
}

dados_unicos = {
    'Nenhum': 0,
    'Houve': 0.333
}

dados_agente = {
    'Nenhum': 0,
    "I": 0.333, 
    "II": 0.364, 
    "III": 0.400, 
    "IV": 0.444,  
    "V": 0.500
}
