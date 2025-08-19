import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import openpyxl as px

MIN_DATE = datetime(2000, 1, 1)
MAX_DATE = datetime(2050, 12, 31)
DATA_CONCLUSAO = 7306 # aprox. 20 anos em dias 

st.set_page_config(page_title="GGDP", layout="wide")

tabs = st.tabs(['**Cálculo Individual**', '**Cálculo Múltiplo**', '**Resultados**'])

st.markdown(
    """
<style>
div[data-testid="stDialog"] div[role="dialog"]:has(.big-dialog) {
    width: 90vw;
    height: 90vh;
    overflow: auto;  /* adiciona barra de rolagem quando necessário */
}
</style>
""",
    unsafe_allow_html=True,
)

@st.dialog("Calcular Pontuações de Responsabilidades")
def calculo_responsabilidades():
    pts_responsabilidade_unic = 0.0
    pts_responsabilidade_mensais = 0.0

    st.html("<span class='big-dialog'></span>")
    sub_tabs = st.tabs(["**Responsabilidades Únicas**", "**Responsabilidades Mensais**","**Resultados**"])
    cols = st.columns(2)

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- RESPONSABILIDADES MENSAIS ---------- ###
    
    with sub_tabs[1]:
        
        ### ---------- CARGO DE COMISSÃO ---------- ###    
        qntd_meses_comissao = 0
        pontuacao_cargos = {
            "DAS-1": 1.000, "DAS-2": 1.000,
            "DAS-3": 0.889, "DAS-4": 0.889,
            "DAS-5": 0.800, "DAS-6": 0.800, "DAS-7": 0.800, "DAID-1A": 0.800, "AEG": 0.800,
            "DAI-1": 0.667, "DAID-1": 0.667, "DAID-1B": 0.667, "DAID-2": 0.667, "AE-1": 0.667, "AE-2": 0.667,
            "DAI-2": 0.500, "DAI-3": 0.500, "DAID-4": 0.500, "DAID-5": 0.500, "DAID-6": 0.500, "DAID-7": 0.500,
            "DAID-8": 0.500, "DAID-9": 0.500, "DAID-10": 0.500, "DAID-11": 0.500, "DAID-12": 0.500,
            "DAID-13": 0.500, "DAID-14": 0.500
        }

        if "comissao_lista" not in st.session_state:
            st.session_state.comissao_lista = []

        if st.checkbox("Exercício em Cargo de Comissão", value=False):   
            cols = st.columns([1, 1, 1, 1])
            with cols[0]:
                cargo_comissao = st.selectbox("Cargo de Comissão", ["Nenhum"] + list(pontuacao_cargos.keys()))
            with cols[1]:
                data_inicio_comissao = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_comissao")
            with cols[2]:
                data_fim_comissao = st.date_input("Data de Encerramento", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_comissao")
            with cols[3]:
                if st.button("Adicionar", key="comissao"):
                    if data_fim_comissao < data_inicio_comissao:
                        st.error("A data de fim não pode ser anterior à data de início.")
                    elif cargo_comissao != 'Nenhum' and data_inicio_comissao and data_fim_comissao and data_fim_comissao >= data_inicio_comissao:
                        delta_ano = data_fim_comissao.year - data_inicio_comissao.year
                        delta_mes = data_fim_comissao.month - data_inicio_comissao.month
                        qntd_meses_comissao = delta_ano * 12 + delta_mes
                        st.session_state.comissao_lista.append((cargo_comissao, qntd_meses_comissao))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")

            # Mostrar comissões cadastradas
            if st.session_state.comissao_lista:
                st.write("**Comissão(es) Cadastradas:**")
                cols = st.columns(4)
                for idx, (cargo, meses) in enumerate(st.session_state.comissao_lista):
                    pts = pontuacao_cargos.get(cargo,0)
                    col = cols[idx % 4]
                    with col:
                        st.write(f"{cargo} [{pts} ponto(s)] → Durante {meses} mês(es)")
                        if st.button("Remover", key=f"remover_comissao{idx}"):
                            st.session_state.comissao_lista = [
                                item for i, item in enumerate(st.session_state.comissao_lista) if i != idx
                            ]

        pts_comissao_total =  sum(
            pontuacao_cargos[cargo] * meses
            for cargo, meses in st.session_state.comissao_lista
        )
        pts_comissao = sum(pontuacao_cargos[cargo] for cargo, meses in st.session_state.comissao_lista)
        
        ### ---------- FUNÇÃO COMISSIONADA ---------- ###  

        pontuacao_func_c = {
            "até R$ 750,00": 0.333, 
            " 751,00 - 1.200,00": 0.364, 
            " 1.201,00 - 1.650,00": 0.400, 
            " 1.651,00 - 2.250,00": 0.444,  
            "acima de 2.250,00": 0.500
        }

        if "func_c_lista" not in st.session_state:
            st.session_state.func_c_lista = []

        if st.checkbox("Exercício de Função Comissionada ou Gratificada", value=False):   
            cols = st.columns([1, 1, 1, 1])
            with cols[0]:
                func_c = st.selectbox("Função", ["Nenhum"] + list(pontuacao_func_c.keys()))
            with cols[1]:
                data_inicio_func_c = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_func_c")
            with cols[2]:
                data_fim_func_c = st.date_input("Data de Fim", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_func_c")
            with cols[3]:
                if st.button("Adicionar", key="func_c"):
                    if data_fim_func_c < data_inicio_func_c:
                        st.error("A data de fim não pode ser anterior à data de início.")
                    elif func_c != 'Nenhum' and data_inicio_func_c and data_fim_func_c and data_fim_func_c >= data_inicio_func_c:
                        delta_ano = data_fim_func_c.year - data_inicio_func_c.year
                        delta_mes = data_fim_func_c.month - data_inicio_func_c.month
                        qntd_meses_func_c = delta_ano * 12 + delta_mes
                        st.session_state.func_c_lista.append((func_c, qntd_meses_func_c))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")

            # Mostrar funções comissionadas cadastradas
            if st.session_state.func_c_lista:
                st.write("**Função(es) Comissionadas Cadastradas:**")
                cols = st.columns(4)
                for idx2, (func, meses) in enumerate(st.session_state.func_c_lista):
                    col = cols[idx2 % 4]
                    with col:
                        st.write(f"{func} → Durante {meses} mês(es)")
                        if st.button("Remover", key=f"remover_func_c{idx2}"):
                            st.session_state.func_c_lista = [
                                item for i, item in enumerate(st.session_state.func_c_lista) if i != idx2
                            ]

        pts_func_c_total =  sum(
            pontuacao_func_c[func] * meses
            for func, meses in st.session_state.func_c_lista
        )

        pts_func_c = sum(pontuacao_func_c[cargo] for cargo, meses in st.session_state.func_c_lista)

        ### ---------- FUNÇÃO DESIGNADA ---------- ###  

        if "func_d_lista" not in st.session_state:
            st.session_state.func_d_lista = []
        if "pts_func_d" not in st.session_state:
            st.session_state.pts_func_d = 0

        if st.checkbox("Exercício de Função Designada", value=False): 
            cols = st.columns([1, 1, 1])
            with cols[0]:
                data_inicio_func_d = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_func_d")
            with cols[1]:
                data_fim_func_d = st.date_input("Data de Fim", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_func_d")
            with cols[2]:
                if st.button("Adicionar", key="func_d"):
                    if data_fim_func_d < data_inicio_func_d:
                        st.error("A data de fim não pode ser anterior à data de início.")
                    elif data_inicio_func_d and data_fim_func_d and data_fim_func_d >= data_inicio_func_d:
                        delta_ano = data_fim_func_d.year - data_inicio_func_d.year
                        delta_mes = data_fim_func_d.month - data_inicio_func_d.month
                        qntd_meses_func_d = delta_ano * 12 + delta_mes
                        st.session_state.func_d_lista.append((qntd_meses_func_d))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")
            if data_fim_func_d > data_inicio_func_d:
                st.session_state.pts_func_d = 0.333  

            # Mostrar funções comissionadas cadastradas
            if st.session_state.func_d_lista:
                st.write("**Função(es) Comissionadas Cadastradas:**")
                cols = st.columns(4)
                for idx3, meses in enumerate(st.session_state.func_d_lista):
                    col = cols[idx3 % 4]
                    with col:
                        st.write(f" 1 Função → Durante {meses} mês(es)")
                        if st.button("Remover", key=f"remover_func_d{idx3}"):
                            st.session_state.func_d_lista = [
                                item for i, item in enumerate(st.session_state.func_d_lista) if i != idx3
                            ]

        pts_func_d = st.session_state.pts_func_d if 'pts_func_d' in st.session_state else 0
        
        pts_func_d_total = sum(
            0.333 * meses
            for meses in st.session_state.func_d_lista
        )

        ### ---------- ATUAÇÃO COMO AGENTE ---------- ###  

        pontuacao_agente = {
            "I": 0.333, 
            "II": 0.364, 
            "III": 0.400, 
            "IV": 0.444,  
            "V": 0.500
        }

        if "agente_lista" not in st.session_state:
            st.session_state.agente_lista = []

        if st.checkbox("Atuação como Agente de Contratação, Gestor/Fiscal de Contratos/Convênios", value=False):   
            cols = st.columns([1, 1, 1, 1])
            with cols[0]:
                agente = st.selectbox("Atuação", ["Nenhum"] + list(pontuacao_agente.keys()))
            with cols[1]:
                data_inicio_agente = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_agente")
            with cols[2]:
                data_fim_agente = st.date_input("Data de Fim", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_agente")
            with cols[3]:
                if st.button("Adicionar", key="agente"):
                    if data_fim_agente < data_inicio_agente:
                        st.error("A data de fim não pode ser anterior à data de início.")
                    elif agente != 'Nenhum' and data_inicio_agente and data_fim_agente and data_fim_agente >= data_inicio_agente:
                        delta_ano = data_fim_agente.year - data_inicio_agente.year
                        delta_mes = data_fim_agente.month - data_inicio_agente.month
                        qntd_meses_agente = delta_ano * 12 + delta_mes
                        st.session_state.agente_lista.append((agente, qntd_meses_agente))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")

            # Mostrar atuações como agente cadastradas
            if st.session_state.agente_lista:
                st.write("**Atuação(es) Cadastradas:**")
                cols = st.columns(4)
                for idx4, (at, meses) in enumerate(st.session_state.agente_lista):
                    col = cols[idx4 % 4]
                    with col:
                        st.write(f"Atuação {at} → Durante {meses} mês(es)")
                        if st.button("Remover", key=f"remover_agente{idx4}"):
                            st.session_state.agente_lista = [
                                item for i, item in enumerate(st.session_state.agente_lista) if i != idx4
                            ]

        pts_agente_total =  sum(
            pontuacao_agente[at] * meses
            for at, meses in st.session_state.agente_lista
        )

        pts_agente = sum(pontuacao_agente[cargo] for cargo, meses in st.session_state.agente_lista)

        ### ---------- ATUAÇÃO EM CONSELHO ---------- ###  

        if "conselho_lista" not in st.session_state:
            st.session_state.conselho_lista = []
        if "pts_conselho" not in st.session_state:
            st.session_state.pts_conselho = 0

        if st.checkbox("Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho", value=False):   
            cols = st.columns([1, 1, 1])
            with cols[0]:
                data_inicio_conselho = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_conselho")
            with cols[1]:
                data_fim_conselho = st.date_input("Data de Fim", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_conselho")
            with cols[2]:
                if st.button("Adicionar", key="conselho"):
                    if data_fim_conselho < data_inicio_conselho:
                        st.error("A data de fim não pode ser anterior à data de início.")
                    elif data_inicio_conselho and data_fim_conselho and data_fim_conselho >= data_inicio_conselho:
                        delta_ano = data_fim_conselho.year - data_inicio_conselho.year
                        delta_mes = data_fim_conselho.month - data_inicio_conselho.month
                        qntd_meses_conselho = delta_ano * 12 + delta_mes
                        st.session_state.conselho_lista.append(( qntd_meses_conselho))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")
            if data_fim_conselho > data_inicio_conselho:
                st.session_state.pts_conselho = 0.333
        
            # Mostrar atuações em conselho cadastradas
            if st.session_state.conselho_lista:
                st.write("**Atuação(es) Cadastrada(s):**")
                cols = st.columns(4)
                for idx5, meses in enumerate(st.session_state.conselho_lista):
                    col = cols[idx5 % 4]
                    with col:
                        st.write(f" 1 Atuação → Durante {meses} mês(es)")
                        if st.button("Remover", key=f"remover_conselho{idx5}"):
                            st.session_state.conselho_lista = [
                                item for i, item in enumerate(st.session_state.conselho_lista) if i != idx5
                            ]
        
        pts_conselho = st.session_state.pts_conselho if 'pts_conselho' in st.session_state else 0

        pts_conselho_total = sum(
            0.333 * meses
            for meses in st.session_state.conselho_lista
        )

    ### ---------- ATUAÇÃO PRIORITÁRIA ---------- ###  

        if "prioritaria_lista" not in st.session_state:
            st.session_state.prioritaria_lista = []
        if "pts_prioritaria" not in st.session_state:
            st.session_state.pts_prioritaria = 0

        if st.checkbox("Exercício de Atuação Prioritária", value=False):   
            cols = st.columns([1, 1, 1])
            with cols[0]:
                data_inicio_prioritaria = st.date_input("Data de Inicio", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_inicio_prioritaria")
            with cols[1]:
                data_fim_prioritaria = st.date_input("Data de Fim", format="DD/MM/YYYY", value=MIN_DATE, min_value=MIN_DATE, max_value=MAX_DATE, key="dt_fim_prioritaria")
            with cols[2]:
                if st.button("Adicionar", key="prioritaria"):
                    if data_fim_prioritaria < data_inicio_prioritaria:
                        st.error("A data de fim não pode ser anterior à data de início.")
                    elif data_inicio_prioritaria and data_fim_prioritaria and data_fim_prioritaria >= data_inicio_prioritaria:
                        delta_ano = data_fim_prioritaria.year - data_inicio_prioritaria.year
                        delta_mes = data_fim_prioritaria.month - data_inicio_prioritaria.month
                        qntd_meses_prioritaria = delta_ano * 12 + delta_mes
                        st.session_state.prioritaria_lista.append(( qntd_meses_prioritaria))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")

            # Mostrar atuações prioritárias cadastradas
            
            if st.session_state.prioritaria_lista:
                st.write("**Atuação(es) Prioritária(s) Cadastrada(s):**")
                cols = st.columns(4)
                for idx6, meses in enumerate(st.session_state.prioritaria_lista):
                    col = cols[idx6 % 4]
                    with col:
                        st.write(f" 1 Atuação → Durante {meses} mês(es)")
                        if st.button("Remover", key=f"remover_prioritaria{idx6}"):
                            st.session_state.prioritaria_lista = [
                                item for i, item in enumerate(st.session_state.prioritaria_lista) if i != idx6
                            ]
            if data_fim_prioritaria > data_inicio_prioritaria:
                st.session_state.pts_prioritaria = 0.333

        pts_prioritaria = st.session_state.pts_prioritaria if 'pts_prioritaria' in st.session_state else 0

        pts_prioritaria_total = sum(
            0.333 * meses
            for meses in st.session_state.prioritaria_lista
        )

        pts_responsabilidade_mensais = pts_comissao + pts_func_c + pts_func_d + pts_agente + pts_conselho + pts_prioritaria

        pts_responsabilidade_mensais_total = pts_comissao_total + pts_func_c_total + pts_func_d_total + pts_agente_total + pts_conselho_total + pts_prioritaria_total
        if pts_responsabilidade_mensais_total >= 144: pts_responsabilidade_mensais_total = 144

### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- RESPONSABILIDADES ÚNICAS ---------- ###

    with sub_tabs[0]:

        ### ---------- ARTIGOS ---------- ###

        if "artigos_lista" not in st.session_state:
            st.session_state.artigos_lista = []
        if "pts_artigos" not in st.session_state:
            st.session_state.pts_artigos = 0

        if st.checkbox("Quantidade de Artigos Científicos Completos Publicados em Periódicos...", value=False):
            cols = st.columns([1, 1, 1])
            with cols[0]: 
                qntd_periodicos_nid = st.number_input("**NÃO** Indexados", min_value=0, key="nid")
            with cols[1]: 
                qntd_periodicos_id = st.number_input("Indexados", min_value=0, key="id")
            with cols[2]:
                if st.button("Adicionar", key="artigos"):
                    if qntd_periodicos_nid > 0 or qntd_periodicos_id > 0:
                        st.session_state.artigos_lista.append((qntd_periodicos_nid, qntd_periodicos_id))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")

            if st.session_state.artigos_lista:
                st.write("**Artigos Cadastrados:**")
                cols = st.columns(6)
                for idx, (nid, id_) in enumerate(st.session_state.artigos_lista):
                    col = cols[idx % 6]
                    with col:
                        st.write(f"NÃO Indexados: {nid} | Indexados: {id_}")
                        if st.button("Remover", key=f"remover_artigo{idx}"):
                            st.session_state.artigos_lista = [
                                item for i, item in enumerate(st.session_state.artigos_lista) if i != idx
                            ]

        total_pts = 0
        for nid, id_ in st.session_state.artigos_lista:
            total_pts += (nid * 0.5) + (id_ * 4)

        st.session_state.pts_artigos = total_pts
        pts_artigos = st.session_state.pts_artigos if 'pts_artigos' in st.session_state else 0

        ### ---------- LIVROS ---------- ###

        if "livros_lista" not in st.session_state:
            st.session_state.livros_lista = []
        if "pts_livros" not in st.session_state:
            st.session_state.pts_livros = 0

        if st.checkbox("Quantidade de Publicações de Livros e Capítulos", value=False):
            cols = st.columns([1, 1, 1, 1])
            with cols[0]: 
                qntd_org_livros = st.number_input("Publicações como 'Organizador de Livro'", min_value=0, key="org")
            with cols[1]: 
                qntd_capitulos = st.number_input("Capitulos Publicados", min_value=0, key="cap")
            with cols[2]: 
                qntd_livros_completos = st.number_input("Livros Completos Publicados", min_value=0, key="lv")
            with cols[3]:
                if st.button("Adicionar", key="livros"):
                    if qntd_org_livros > 0 or qntd_capitulos > 0 or qntd_livros_completos > 0:
                        st.session_state.livros_lista.append((qntd_org_livros, qntd_capitulos, qntd_livros_completos))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")

            # Mostrar livros cadastrados
            if st.session_state.livros_lista:
                st.write("**Livros ou Capitulos Cadastrados:**")
                cols = st.columns(7)
                for idx2, (org, cap, lv) in enumerate(st.session_state.livros_lista):
                    col = cols[idx2 % 7]
                    with col:
                        st.write(f"Organizador: {org} | Capitulos: {cap}  Livro Completo: {lv}")
                        if st.button("Remover", key=f"remover_livro{idx2}"):
                            st.session_state.livros_lista = [
                                item for i, item in enumerate(st.session_state.livros_lista) if i != idx2
                            ]

        total_pts = 0
        for org, cap, lv in st.session_state.livros_lista:
            total_pts += (org * 1) + (cap * 4) + (lv * 6)

        st.session_state.pts_livros = total_pts
        pts_livros = st.session_state.pts_livros if 'pts_livros' in st.session_state else 0

        ### ---------- PESQUISAS CIENTÍFICAS ---------- ###

        if "pesquisas_lista" not in st.session_state:
            st.session_state.pesquisas_lista = []
        if "pts_pesquisas" not in st.session_state:
            st.session_state.pts_pesquisas = 0

        if st.checkbox("Quantidade de Publicações de Pesquisas Científicas Aprovadas", value=False):
            cols = st.columns([1, 1, 1, 1, 1])
            with cols[0]: 
                qntd_estadual = st.number_input("Estadualmente",min_value = 0, key="est")
            with cols[1]: 
                qntd_regional = st.number_input("Regionalmente",min_value = 0, key="reg")
            with cols[2]: 
                qntd_nacional = st.number_input("Nacionalmente",min_value = 0, key="nac")
            with cols[3]:
                qntd_internacional = st.number_input("Internacionalmente",min_value = 0, key="inter")
            with cols[4]:
                if st.button("Adicionar", key="pesquisas"):
                    if qntd_estadual > 0 or qntd_regional > 0 or qntd_nacional > 0 or qntd_internacional > 0:
                        st.session_state.pesquisas_lista.append((qntd_estadual, qntd_regional, qntd_nacional, qntd_internacional))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")
            
            # Mostrar pesquisas cadastradas
            if st.session_state.pesquisas_lista:
                st.write("**Pesquisas Aprovadas Cadastradas:**")
                cols = st.columns(5)
                for idx3, (est, reg, nac, inter) in enumerate(st.session_state.pesquisas_lista):
                    col = cols[idx3 % 5]
                    with col:
                        st.write(f"Estadualmente: {est} | Regionalmente: {reg}  Nacionalmente: {nac} | Internacionalmente: {inter}")
                        if st.button("Remover", key=f"remover_pesquisa{idx3}"):
                            st.session_state.pesquisas_lista = [
                                item for i, item in enumerate(st.session_state.pesquisas_lista) if i != idx3
                            ]

        total_pts = 0
        for est, reg, nac, inter in st.session_state.pesquisas_lista:
            total_pts += (est * 1) + (reg * 3) + (nac * 3) + (inter * 4)

        st.session_state.pts_pesquisas = total_pts
        pts_pesquisas = st.session_state.pts_pesquisas if 'pts_pesquisas' in st.session_state else 0

        ### ---------- REGISTROS DE PATENTES OU CULTIVAR ---------- ###

        if "patentes_lista" not in st.session_state:
            st.session_state.patentes_lista = []
        if "pts_patentes" not in st.session_state:
            st.session_state.pts_patentes = 0

        if st.checkbox("Quantidade de Registros de Patentes ou Cultivar", value=False):
            cols = st.columns([1, 1, 1])
            with cols[0]: 
                qntd_patente = st.number_input("Patente", min_value=0, key="pat")
            with cols[1]: 
                qntd_cultivar = st.number_input("Cultivar", min_value=0, key="cult")
            with cols[2]:
                if st.button("Adicionar", key="patentes"):
                    if qntd_patente > 0 or qntd_cultivar > 0:
                        st.session_state.patentes_lista.append((qntd_patente, qntd_cultivar))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")

            # Mostrar registros cadastradas
            if st.session_state.patentes_lista:
                st.write("**Patentes ou Cultivar Cadastrados:**")
                cols = st.columns(6)
                for idx4, (pat, cult) in enumerate(st.session_state.patentes_lista):
                    col = cols[idx4 % 6]
                    with col:
                        st.write(f"Patentes: {pat} | Cultivar: {cult}")
                        if st.button("Remover", key=f"remover_patente{idx4}"):
                            st.session_state.patentes_lista = [
                                item for i, item in enumerate(st.session_state.patentes_lista) if i != idx4
                            ]

        total_pts = 0
        for pat, cult in st.session_state.patentes_lista:
            total_pts += (pat * 8) + (cult * 8)

        st.session_state.pts_patentes = total_pts
        pts_patentes = st.session_state.pts_patentes if 'pts_patentes' in st.session_state else 0

        ### ---------- CURSOS ---------- ###

        valores_curso = {
            'Nenhum': None,
            'Estágio Pós-Doutoral no Orgão (6 meses)': 6,   
            'Pós-Doutorado (6 a 12 meses)': 8,   
            'Pós-Doutorado (13 a 24 meses)': 12,  
            'Pós-Doutorado (25 a 48 meses)': 24,
            'Pós-Doutorado (maior que 48 meses)': 48  
        }

        if "pts_cursos_lista" not in st.session_state:
            st.session_state.pts_cursos_lista = []
        if "pts_cursos_total" not in st.session_state:
            st.session_state.pts_cursos_total = 0

        if st.checkbox("Cursos e Treinamentos", value=False):
            cols = st.columns([1, 1, 1])
            with cols[0]:
                qntd_curso = st.number_input("Quantidade de Cursos", min_value=0)
            with cols[1]:
                tipo_doc = st.selectbox("Tipo", list(valores_curso.keys()))
            with cols[2]:
                if st.button("Adicionar", key="cursos"):
                    if qntd_curso > 0 and tipo_doc != 'Nenhum':
                        st.session_state.pts_cursos_lista.append((qntd_curso, tipo_doc))
                    else:
                        st.error("Todas as informações precisam ser preenchidas.")

            # Mostrar cursos cadastradas
            if st.session_state.pts_cursos_lista:
                st.write("**Cursos Cadastrados:**")
                cols = st.columns(4)
                for idx5, (qntd, tipo) in enumerate(st.session_state.pts_cursos_lista):
                    col = cols[idx5 % 4]
                    with col:
                        st.write(f"{qntd} → {tipo} |")
                        if st.button("Remover", key=f"remover_doc{idx5}"):
                            st.session_state.pts_cursos_lista = [
                                item for i, item in enumerate(st.session_state.pts_cursos_lista) if i != idx5
                            ]
                            
        tot_pts_c = 0
        for qntd_c, tipo_c in st.session_state.pts_cursos_lista:
            pontos_cursos = valores_curso.get(tipo_c, 0)
            restantes = max(0, 144 - tot_pts_c)
            aproveitados = min(pontos_cursos * qntd_c, restantes)  # multiplica pela quantidade
            tot_pts_c += aproveitados

        st.session_state.pts_cursos_total = tot_pts_c
        pts_cursos = st.session_state.pts_cursos_total if 'pts_cursos_total' in st.session_state else 0
            
        pts_responsabilidade_unic = pts_artigos + pts_livros + pts_pesquisas + pts_patentes + pts_cursos 
        if pts_responsabilidade_unic >= 144: pts_responsabilidade_unic = 144
        
    ### ---------- RESULTADOS ---------- ###
    with sub_tabs[2]:
        pts_responsabilidade =  pts_responsabilidade_mensais_total + pts_responsabilidade_unic
        if pts_responsabilidade >= 144: pts_responsabilidade = 144

        cols = st.columns(3)
        cols[0].metric("Responsabilidade Mensais", round(pts_responsabilidade_mensais, 4))
        cols[1].metric("Total", round(pts_responsabilidade, 4))
        cols[2].metric("Responsabilidade Unicas", round(pts_responsabilidade_unic, 4))

    # Garante que os valores são números antes de retornar
    pts_responsabilidade_mensais = float(pts_responsabilidade_mensais) if 'pts_responsabilidade_mensais' in locals() else 0.0
    pts_responsabilidade_unic = float(pts_responsabilidade_unic) if 'pts_responsabilidade_unic' in locals() else 0.0
    
### ---------- FUNÇÃO CONCLUIDA ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####

### ---------- MAIN ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- CALCULO MULTIPLO ---------- ###

with tabs[1]:
    carreira = [[0 for _ in range(10)] for _ in range(DATA_CONCLUSAO)]
    arquivo = st.file_uploader("Arquivo", type=["xlsx","xls", "csv"])

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

with tabs[0]:
    if st.button("Calcular Pontuações de Responsabilidades"):
        calculo_responsabilidades()

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
            else:
                st.error("Todas as informações precisam ser preenchidas.")

    # Mostrar pontos cadastrados
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
            else:
                st.error("Todas as informações precisam ser preenchidas.")

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
            if data_conclusao and horas_curso > 0:
                st.session_state.aperfeicoamentos.append((data_conclusao, horas_curso))
            else:
                st.error("Todas as informações precisam ser preenchidas.")

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
        'Nenhuma': None,
        'Graduação': 6,   # Graduação
        'Especialização': 12,   # Especialização
        'Mestrado': 24,  # Mestrado
        'Doutorado': 48    # Doutorado
    }

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
            if data_conclusao_tit and tipo_tit != 'Nenhuma':
                st.session_state.titulacoes.append((data_conclusao_tit, tipo_tit))
            else:
                st.error("Todas as informações precisam ser preenchidas.")

    # Mostrar titulações cadastradas
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
        pontos_resp_unic = st.number_input("Pontos Responsabilidades Únicas", value=0.0, min_value=0.0, key="pts_ru")
    with col3:
        if st.button("Adicionar", key="resp_uni"):
            if data_resp_unic and pontos_resp_unic > 0:
                st.session_state.resp_unicas.append((data_resp_unic, pontos_resp_unic))
            else:
                st.error("Todas as informações precisam ser preenchidas.")

    # Mostrar responsabilidades cadastradas 
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
    qntd_meses_rm = 0
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        data_inicio_rm = st.date_input("Data de Início", format="DD/MM/YYYY", value=data_inicial, min_value=MIN_DATE, max_value=MAX_DATE, key="m_resp_mes")
    with col2:
        data_fim_rm = st.date_input("Data de Fim", format="DD/MM/YYYY", value=data_inicial, min_value=MIN_DATE, max_value=MAX_DATE, key="f_resp_mes")
    with col3:
        pontos_resp_mensal = st.number_input("Pontos de Responsabilidade p/Mês", value=0.0, min_value=0.0, format="%.3f", key="pts_rm")
    with col4:
        if st.button("Adicionar", key="resp_mes"):
            if data_fim_rm < data_inicio_rm:
                st.error("A data de fim não pode ser anterior à data de início.")
            elif data_inicio_rm  and data_fim_rm and pontos_resp_mensal > 0:
                delta_ano = data_fim_rm.year - data_inicio_rm.year
                delta_mes = data_fim_rm.month - data_inicio_rm.month
                qntd_meses_rm = delta_ano * 12 + delta_mes 
                st.session_state.resp_mensais.append((data_inicio_rm, pontos_resp_mensal, qntd_meses_rm))
            else:
                st.error("Todas as informações precisam ser preenchidas.")

    # Mostrar responsabilidades cadastradas
    if st.session_state.resp_mensais:
        st.write("**Responsabilidades Mensais cadastradas:**")
        cols = st.columns(5)
        for idx3, (data, pontos_m, qntd_m) in enumerate(st.session_state.resp_mensais):
            col = cols[idx3 % 5]  # escolhe a coluna certa
            with col:
                st.write(f"{pontos_m:.3f} ponto(s) → Durante {qntd_m} mês(es)")
                if st.button(f"Remover", key=f"remover_rm{idx3}"):
                    st.session_state.resp_mensais.pop(idx3)
                    st.rerun()    

    # Exemplo de dados do usuário
    responsabilidades_mensais = [
        {
            'data_inicio': data_inicio_rm,
            'meses': qntd_meses_rm,
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
            carreira[i][9] = carreira[i-1][9] + carreira[i][2] + carreira[i][4] + carreira[i][5] + carreira[i][6] + carreira[i][7] + carreira[i][8] + pts_remanescentes 
        else:
            carreira[i][9] = carreira[i-1][9] + carreira[i][2] + carreira[i][4] + carreira[i][5] + carreira[i][6] + carreira[i][7] + carreira[i][8] 
    
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

        meses_passados = (data_atual.year - data_inicio.year) * 12 + (data_atual.month - data_inicio.month) + 1 # para contar o primeirio mes

        # Regra do mínimo de meses
        if meses_passados < 12:
            continue

        if 12 <= meses_passados < 18:
            if pontos >= 96:
                evolucao = data_atual # adiciona 1 mes
                meses_ate_evolucao = meses_passados
                pts_resto = pontos - 48
                break

        if meses_passados >= 18:
            if pontos >= 96 or pontos >= 48:
                evolucao = data_atual # adiciona 1 mes
                meses_ate_evolucao = meses_passados
                pts_resto = pontos - 48
                break
        
    diff = relativedelta(evolucao, data_inicial)
    qtd_meses = diff.years * 12 + diff.months
    desempenho = aperfeicoamento = 0
    for linha in carreira:
        data = linha[0]
        if data <= evolucao:
            desempenho += linha[2] 
            aperfeicoamento += linha[5]

    col = st.columns(2)
    col[0].metric(f"Pontos de Desempenho:", value=round(desempenho,4))
    col[1].metric(f"Pontos de Aperfeiçoamento:", value=round(aperfeicoamento,4))
    
    pendencias = False
    if round(aperfeicoamento, 4) < 5.4:
        resto_hr_a = 60 - total_horas
        resto_a = 5.4 - round(aperfeicoamento, 4)
        st.error(f"O servidor não cumpriu os requisitos mínimos obrigatórios para a evolução funcional: 60 horas de curso ou 5,4 pontos do requisito Aperfeiçoamento. Faltam {resto_hr_a} horas de curso ou {round(resto_a, 4)} pontos.")
        pendencias = True
    
    if round(desempenho, 4) < 2.4:
        resto_d = 2.4 - round(desempenho, 4)
        st.error(f"O servidor não cumpriu os requisitos mínimos obrigatórios para a evolução funcional: 2,4 pontos do requisito Desempenho. Faltam {round(resto_d, 4)} pontos.")
        pendencias = True

    if not pendencias and evolucao:
        resultado_niveis.append({
            "Data da Próxima Evolução": evolucao.strftime("%d/%m/%Y"),
            "Meses Gastos para Evolução": meses_ate_evolucao,
            "Pontos Remanescentes": pts_resto
        })

        df_resultados = pd.DataFrame(resultado_niveis)
        st.dataframe(df_resultados, hide_index=True, height=700)

    ### ---------- CONCLUIDO ---------- ###
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
### ---------- DATAFRAME DE CONTROLE ---------- ###
with tabs[2]:
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