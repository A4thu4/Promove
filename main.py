import streamlit as st
import pandas as pd 
from datetime import datetime 
from dateutil.relativedelta import relativedelta

MIN_DATE = datetime(2000, 1, 1)
MAX_DATE = datetime(2050, 12, 31)

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
st.set_page_config(page_title="Simulador PROMOVE GNCP", layout="wide")
st.markdown(
        """
        <style>
            img {
                margin-top: -3rem !important;
                margin-bottom: -1.2rem !important;
                align: center !important;
            }
            h1 {
                font-size: 2.12rem !important;
                margin-bottom: 1rem !important;
                margin-left: 1.6rem !important;
            }
            :root {
                --primary-color: #1bb50b !important;  /* Verde */
                --background-color: #FFFFFF !important;  /* Branco */
                --secondary-background-color: #FFFFFF !important;  /* Branco */
                --text-color: #000000 !important;  /* Preto */
            }

            /* Aplica cinza SOMENTE nos inputs */
            .stTextInput>div>div>input,
            .stNumberInput>div>div>input,
            .stTextArea>div>div>textarea,
            .stSelectbox>div>div>select,
            .stDateInput>div>div>input {
                background-color: #F3F3F3 !important;  /* Cinza claro */
                border-radius: 8px !important;
            }

            /* Mantém fundo branco em outros containers */
            .stApp, .stSidebar, .stAlert, .stMarkdown {
                background-color: #FFFFFF !important;
            }

            /* Estilo para botões */
            .stButton > button {
                border-radius: 8px !important;
                border: 1px solid #e0e0e0 !important;
                transition: all 0.3s ease !important;
                font-weight: 500 !important;
                color: #ff666f !important;
            }

            .stButton > button:hover {
                background: linear-gradient(135deg, #FFF, #FFF) !important;
                color: #ff666f !important; /* texto verde */
                border: 2px solid #ff666f !important; /* borda verde */
                box-shadow: 0 2px 8px rgba(27,181,11,0.15) !important; /* sombra suave */
                transform: translateY(-2px) scale(1.03) !important; /* leve efeito de elevação */
                transition: all 0.2s !important;
            }

            /* Estilo para botões primários e de Download*/
            .stButton > button[kind="primary"],
            .stDownloadButton > button {
                background: linear-gradient(135deg, #FFF, #FFF) !important;
                border-radius: 10px !important;
                color: green !important;
            }
            .stButton > button[kind="primary"]:hover,
            .stDownloadButton > button:hover {
                background: linear-gradient(135deg, #FFF, #FFF) !important;
                color: #1bb50b !important; /* texto verde */
                border: 2px solid #1bb50b !important; /* borda verde */
                box-shadow: 0 2px 8px rgba(27,181,11,0.15) !important; /* sombra suave */
                transform: translateY(-2px) scale(1.03) !important; /* leve efeito de elevação */
                transition: all 0.2s !important;
            }

            /* Estilo para DataFrames */
            .stDataFrame {
                border-radius: 8px !important;
                border: 1px solid #e0e0e0 !important;
                overflow: hidden !important;
            }

            /* Estilo para as abas */
            .stTabs [data-baseweb="tab-list"] {
                gap: 10px;
            }
            
            /* Linha da aba ativa */
            div[data-baseweb="tab-highlight"] {
                background-color: #1bb50b; 
            }
            .stTabs [aria-selected="false"] {
                color: #000000 !important;
            }
            .stTabs [aria-selected="true"] {
                color: #1bb50b !important;
            }

            /* Estilo para file uploader */
            .stFileUploader {
                border: 2px dashed #e0e0e0 !important;
                border-radius: 8px !important;
                padding: 8px !important;
                text-align: center !important;
            }
        </style>
        """,unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Simulador PROMOVE</h1>", unsafe_allow_html=True)

carreira = [[0 for _ in range(10)] for _ in range(721)] # matriz de 721 linhas e 10 colunas

tipo_calculo = "Geral"
tab1, tab2, tab3, tab4 = st.tabs(["**Critérios Obrigatórios**", "**Titulação Acadêmica**", "**Assunção de Responsabilidades**", "**Pontuação Final**"])

##Critérios obrigatórios##
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        tempo_exercicio = st.date_input("Inicio do Efetivo Exercício", format="DD/MM/YYYY", min_value=MIN_DATE, max_value=datetime.now().date())

    # Calcular o tempo de exercício em meses
    if tempo_exercicio:
        data_atual = datetime.now().date() # Data atual
        if tempo_exercicio <= data_atual:
            delta = relativedelta(data_atual, tempo_exercicio)
            qntd_meses_tee = delta.years * 12 + delta.months
        else:
            st.error("A data de início deve ser anterior ou igual à data atual.")
    else:
        qntd_meses_tee = 0
    with col2:
        st.text_input("Quantidade de Meses em Exercício", value=str(qntd_meses_tee))

    pts_desempenho = st.number_input("Avaliação de Desempenho Individual", min_value=7.0, max_value=11.4)

    pts_aperfeicoamento = 0
    aperfeicoamento = st.text_input("Aperfeiçoamento (Horas Totais)")
    if aperfeicoamento:
        try:
            aperfeicoamento = int(aperfeicoamento)
            if aperfeicoamento < 60 or aperfeicoamento > 100:
                st.error("Valor Inválido.")
            else:
                pts_aperfeicoamento = aperfeicoamento * 0.09
        except ValueError:
            st.error("Insira um número.")

pts_obrigatorios = (pts_desempenho / 6) + (pts_aperfeicoamento / 24)

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####

with tab2:
    pts_titulacao = 0
    datas_tit = {}

    graduacao = st.number_input("Graduação", min_value=0, key="graduacao")
    if graduacao > 0:
        with st.expander("Data(s) de Conclusão(s)", expanded=True):
            for i in range(1,graduacao+1):
                datas_tit[f"grad_{i}"] = st.date_input(f"Data de Conclusão da Graduação {i}", format="DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE, key=f"grad_{i}")  
    
    especializacao = st.number_input("Especialização", min_value=0, key="especializacao")
    if especializacao > 0:
        with st.expander("Data(s) de Conclusão(s)", expanded=True):
            for i in range(1,especializacao+1):
                datas_tit[f"esp_{i}"] = st.date_input(f"Data de Conclusão da Especializacao {i}", format="DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE, key=f"esp_{i}")
    
    mestrado = st.number_input("Mestrado", min_value=0, key="mestrado")
    if mestrado > 0:
        with st.expander("Data(s) de Conclusão(s)", expanded=True):
            for i in range(1,mestrado+1):
                datas_tit[f"mest_{i}"] = st.date_input(f"Data de Conclusão do Mestrado {i}", format="DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE, key=f"mest_{i}")
    
    doutorado = st.number_input("Doutorado", min_value=0, key="doutorado")
    if doutorado > 0:
        with st.expander("Data(s) de Conclusão(s)", expanded=True):
            for i in range(1,doutorado+1):
                datas_tit[f"doc_{i}"] = st.date_input(f"Data de Conclusão do Doutorado {i}", format="DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE, key=f"doc_{i}")

    pts_titulacao = (graduacao * 6) + (especializacao * 12) + (mestrado * 24) + (doutorado * 48)

    if pts_titulacao >= 144:
        pts_titulacao = 144

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####

with tab3:
    subtabs = st.tabs(["**Assunção de Responsabilidade dos últimos 5 anos**", "**Assunção de Responsabilidades Atuais**"])

    #rsponsabilidades ultimos 5 anos
    pts_resp_inical = 0
    with subtabs[0]:
            col1,col2 = st.columns(2)
            with col1:
                cargo_comissao_5 = st.selectbox("Exercício em Cargo de Comissão", ["Nenhuma", "AE-1","AE-2","AEG","DAI-1","DAI-2","DAI-3","DAID-1","DAID-2","DAID-3","DAID-4","DAID-5","DAID-6","DAID-7","DAID-8","DAID-9","DAID-10","DAID-11","DAID-12","DAID-13","DAID-14","DAID-1A","DAID-1B","DAS-1","DAS-2","DAS-3","DAS-4","DAS-5","DAS-6","DAS-7"], key="cargo_5anos")
            with col2:
                tmp_comissao_5 = st.number_input("Quantidade de Meses em Cargo",  min_value=0, key="meses_cargo_5anos")

            if cargo_comissao_5 == "Nenhuma":
                pts_comissao_5 = 0
            elif cargo_comissao_5 in ["DAS-1", "DAS-2"]:
                pts_comissao_5 =  1.000
            elif cargo_comissao_5 in ["DAS-3", "DAS-4"]:
                pts_comissao_5 =  0.889
            elif cargo_comissao_5 in ["DAS-5", "DAS-6", "DAS-7", "DAID-1A", "AEG"]:
                pts_comissao_5 =  0.800
            elif cargo_comissao_5 in ["DAI-1", "DAID-1", "DAID-1B", "DAID-2", "AE-1", "AE-2"]:
                pts_comissao_5 =  0.667
            elif cargo_comissao_5 in ["DAI-2", "DAI-3", "DAID-4", "DAID-5", "DAID-6", "DAID-7", "DAID-8", "DAID-9", "DAID-10", "DAID-11", "DAID-12", "DAID-13", "DAID-14"]:
                pts_comissao_5 =  0.500


            col1,col2 = st.columns(2)
            with col1:
                funcao_comissionada_5 = st.selectbox("Exercício de Função Comissionada ou Gratificada",["Nenhuma", "até R$ 750,00","R$ 751,00 a R$ 1.200,00","R$ 1.201,00 a R$ 1.650,00","R$ 1.651,00 a R$ 2.250,00","acima de 2.250,00"], key="comissao_5anos")
            with col2:
                tmp_func_comissionada_5 = st.number_input("Quantidade de Meses em Função",  min_value=0, key="meses_funcao_5anos")

            if funcao_comissionada_5 == "Nenhuma":
                pts_func_comissionada_5 = 0
            elif funcao_comissionada_5 == "até R$ 750,00":
                pts_func_comissionada_5 = 0.333
            elif funcao_comissionada_5 == "R$ 751,00 a R$ 1.200,00":
                pts_func_comissionada_5 = 0.364
            elif funcao_comissionada_5 == "R$ 1.201,00 a R$ 1.650,00":
                pts_func_comissionada_5 = 0.400
            elif funcao_comissionada_5 == "R$ 1.651,00 a R$ 2.250,00":
                pts_func_comissionada_5 = 0.444
            elif funcao_comissionada_5 == "acima de 2.250,00":
                pts_func_comissionada_5 = 0.500

            col1,col2 = st.columns(2)
            with col1:
                sn_func_designada_5 = st.selectbox("Exercício de Função Designada", ["Nenhuma", "Sim"], key="designada_5anos")
            with col2:
                func_designada_5 = st.number_input("Quantidade de Meses em Exercício de Função Designada", min_value=0, key="funcao_designada_5anos")

            col1,col2 = st.columns(2)
            with col1:
                atuacao_agente_5 = st.selectbox("Agente de Contratação, Gestor/Fiscal de Contratos/Convênios",["Nenhum","I","II","III","IV","V"], key="agente_5anos")
            with col2:
                tmp_atuacao_agente_5 = st.number_input("Quantidade de Meses em Atuação", min_value=0, key="meses_agente_5anos")

            if atuacao_agente_5 == "Nenhum":
                pts_agente_5 = 0
            elif atuacao_agente_5 == "I":
                pts_agente_5 = 0.333
            elif atuacao_agente_5 == "II":
                pts_agente_5 = 0.364
            elif atuacao_agente_5 == "III":
                pts_agente_5 = 0.400
            elif atuacao_agente_5 == "IV":
                pts_agente_5 = 0.444
            elif atuacao_agente_5 == "V":
                pts_agente_5 = 0.500

            col1,col2 = st.columns(2)
            with col1:
                atuacao_conselho_5 = st.selectbox("Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho", ["Nenhum", "Sim"], key="conselho_5anos")
            with col2:
                tmp_atuacao_conselho_5 = st.number_input("Quantidade de Meses de Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho", min_value=0, key="meses_conselho_5anos")

            col1,col2 = st.columns(2)
            with col1:
                atuacao_prioritaria_5 = st.selectbox("Atuação Prioritária", ["Nenhuma", "Sim"], key="prioritaria_5anos")
            with col2:
                tmp_atuacao_prioritaria_5 = st.number_input("Quantidade de Meses de Atuação Prioritária", min_value=0, key="meses_prioritaria_5anos")

    pts_resp_inical_comissao = pts_comissao_5 * tmp_comissao_5
    pts_resp_inical_func_comissionada = pts_func_comissionada_5 * tmp_func_comissionada_5
    pts_resp_inicial_func_designada = func_designada_5 * 0.333 if sn_func_designada_5 == "Sim" else 0
    pts_resp_inicial_agente = pts_agente_5 * tmp_atuacao_agente_5   
    pts_resp_inical_conselho = tmp_atuacao_conselho_5 * 0.333 if atuacao_conselho_5 == "Sim" else 0
    pts_resp_inical_prioritaria = tmp_atuacao_prioritaria_5 * 0.333 if atuacao_prioritaria_5 == "Sim" else 0

    pts_resp_inical_mes = pts_comissao_5 + pts_func_comissionada_5 + (0.333 if sn_func_designada_5 == "Sim" else 0) + pts_agente_5 + (0.333 if atuacao_conselho_5 == "Sim" else 0) + (0.333 if atuacao_prioritaria_5 == "Sim" else 0)
    pts_resp_inical = pts_resp_inical_comissao + pts_resp_inical_func_comissionada + pts_resp_inicial_func_designada + pts_resp_inicial_agente + pts_resp_inical_conselho + pts_resp_inical_prioritaria

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####

    #responsabilidades atuais
    with subtabs[1]:
        sub_tabs = st.tabs(["**Responsabilidades Mensais**", "**Responsabilidades Únicas**"])
        
        pts_responsabilidade_mensais = 0
        with sub_tabs[0]:
            #cargo de comissao
            with st.expander("Exercício em Cargo de Comissão"):     
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    cargo_comissao = st.selectbox("Cargo de Comissão", ["Nenhum", "AE-1","AE-2","AEG","DAI-1","DAI-2","DAI-3","DAID-1","DAID-2","DAID-3","DAID-4","DAID-5","DAID-6","DAID-7","DAID-8","DAID-9","DAID-10","DAID-11","DAID-12","DAID-13","DAID-14","DAID-1A","DAID-1B","DAS-1","DAS-2","DAS-3","DAS-4","DAS-5","DAS-6","DAS-7"])
                with col2:
                    data_inicio_comissao = st.date_input("Data de Inicio no Cargo", format="DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)
                with col3:
                    data_fim_comissao = st.date_input("Data de Encerramento no Cargo", format="DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)

            qntd_meses_comissao = 0
            pts_comissao = 0
            if data_inicio_comissao and data_fim_comissao:
                if data_inicio_comissao <= data_fim_comissao:
                    delta = relativedelta(data_fim_comissao, data_inicio_comissao)
                    qntd_meses_comissao = delta.years * 12 + delta.months
                else:
                    st.error("A data de início deve ser anterior ou igual à data de fim.")
                with col4:
                    qntd_meses_comissao = st.number_input("Quantidade de Meses em Cargo",  min_value=0, value= "" or qntd_meses_comissao)
                if cargo_comissao in ["DAS-1", "DAS-2"]:
                    pts_comissao =  1.000
                elif cargo_comissao in ["DAS-3", "DAS-4"]:
                    pts_comissao =  0.889
                elif cargo_comissao in ["DAS-5", "DAS-6", "DAS-7", "DAID-1A", "AEG"]:
                    pts_comissao =  0.800
                elif cargo_comissao in ["DAI-1", "DAID-1", "DAID-1B", "DAID-2", "AE-1", "AE-2"]:
                    pts_comissao =  0.667
                elif cargo_comissao in ["DAI-2", "DAI-3", "DAID-4", "DAID-5", "DAID-6", "DAID-7", "DAID-8", "DAID-9", "DAID-10", "DAID-11", "DAID-12", "DAID-13", "DAID-14"]:
                    pts_comissao =  0.500

            pts_comissao_total = pts_comissao * qntd_meses_comissao

            #função comissionada
            with st.expander("Exercício de Função Comissionada ou Gratificada"):
                col1, col2, col3, col4 = st.columns(4)
                qntd_meses_funcao = 0
                pts_func_comissionada = 0
                with col1: 
                    funcao_comissionada = st.selectbox("Exercício de Função Comissionada ou Gratificada",["Nenhum","até R$ 750,00","R$ 751,00 a R$ 1.200,00","R$ 1.201,00 a R$ 1.650,00","R$ 1.651,00 a R$ 2.250,00","acima de 2.250,00"])
                with col2: 
                    data_inicio_fun_com = st.date_input("Data de Inicio na Função", format = "DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)
                with col3: 
                    data_fim_func_com = st.date_input("Data de Encerramento na Função", format = "DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)

                if data_fim_func_com and data_inicio_fun_com:
                    delta = relativedelta(data_fim_func_com, data_inicio_fun_com)
                    qntd_meses_funcao = delta.years * 12 + delta.months
                with col4: 
                    qntd_meses_funcao = st.number_input("Quantidade de Meses em Função", value="" or qntd_meses_funcao)
                if funcao_comissionada == "até R$ 750,00":
                    pts_func_comissionada = 0.333
                elif funcao_comissionada == "R$ 751,00 a R$ 1.200,00":
                    pts_func_comissionada = 0.364
                elif funcao_comissionada == "R$ 1.201,00 a R$ 1.650,00":
                    pts_func_comissionada = 0.400
                elif funcao_comissionada == "R$ 1.651,00 a R$ 2.250,00":
                    pts_func_comissionada = 0.444
                elif funcao_comissionada == "acima de 2.250,00":
                    pts_func_comissionada = 0.500

            pts_func_comissionada_total = pts_func_comissionada * qntd_meses_funcao

            #função designada
            with st.expander("Exercício de Função Designada"):
                col1, col2, col3 = st.columns(3)
                with col1: 
                    data_inicio_fun_des = st.date_input("Data de Inicio do Exercício de Função Designada", format = "DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)
                with col2: 
                    data_fim_func_des = st.date_input("Data de Encerramento do Exercício de Função Designada", format = "DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)
                qntd_meses_func_des = 0
                if data_fim_func_des and data_inicio_fun_des:
                    delta = relativedelta(data_fim_func_des, data_inicio_fun_des)
                    qntd_meses_func_des = delta.years * 12 + delta.months
                with col3: 
                    qntd_meses_func_des = st.number_input("Quantidade de Meses em Exercício de Função Designada", value="" or qntd_meses_func_des)

            pts_func_designada = qntd_meses_func_des * 0.333

            #atuação como agente
            with st.expander("Atuação como Agente de Contratação, Gestor/Fiscal de Contratos/Convênios"):
                col1, col2, col3, col4 = st.columns(4)
                with col1: 
                    atuacao_agente = st.selectbox("Agente de Contratação, Gestor/Fiscal de Contratos/Convênios",["Nenhum","I","II","III","IV","V"])
                with col2: 
                    data_inicio_atuacao = st.date_input("Data de Inicio na Atuação", format = "DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)
                with col3: 
                    data_fim_atuacao = st.date_input("Data de Encerramento na Atuação", format = "DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)
                qntd_meses_atuacao = 0
                if atuacao_agente != "Não Atuou":
                    if data_fim_atuacao and data_inicio_atuacao:
                        delta = relativedelta(data_fim_atuacao, data_inicio_atuacao)
                        qntd_meses_atuacao = delta.years * 12 + delta.months
                with col4: 
                    qntd_meses_atuacao = st.number_input("Quantidade de Meses em Atuação", value="" or qntd_meses_atuacao)
                pts_agente = 0
                if atuacao_agente == "I":
                    pts_agente = 0.333
                elif atuacao_agente == "II":
                    pts_agente = 0.364
                elif atuacao_agente == "III":
                    pts_agente = 0.400
                elif atuacao_agente == "IV":
                    pts_agente = 0.444
                elif atuacao_agente == "V":
                    pts_agente = 0.500

            pts_agente_total = pts_agente * qntd_meses_atuacao

            #atuação em conselho
            with st.expander("Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho"):
                col1, col2, col3 = st.columns(3)
                with col1: 
                    data_inicio_atuacao_cons = st.date_input("Data de Iniciamento da Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho", format = "DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)
                with col2: 
                    data_fim_atuacao_cons = st.date_input("Data de Encerramento da Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho", format = "DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)
                qntd_meses_atuacao_conselho = 0
                if data_fim_atuacao_cons and data_inicio_atuacao_cons:
                    delta = relativedelta(data_fim_atuacao_cons, data_inicio_atuacao_cons)
                    qntd_meses_atuacao_conselho = delta.years * 12 + delta.months
                with col3: 
                    qntd_meses_atuacao_conselho = st.number_input("Quantidade de Meses de Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho", value="" or qntd_meses_atuacao_conselho)
            
            pts_conselho = qntd_meses_atuacao_conselho * 0.333

            #atuação prioritaria
            with st.expander("Exercício de Atuação Prioritária"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    data_inicio_atuacao_priori = st.date_input("Data de Início do Exercício de Atuação Prioritária", format = "DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)
                with col2:
                    data_fim_atuacao_priori = st.date_input("Data de Encerramento do Exercício de Atuação Prioritária", format = "DD/MM/YYYY", min_value=MIN_DATE, max_value=MAX_DATE)
                qntd_meses_atuacao_prioritaria = 0
                if data_fim_atuacao_priori and data_inicio_atuacao_priori:
                    delta = relativedelta(data_fim_atuacao_priori, data_inicio_atuacao_priori)
                    qntd_meses_atuacao_prioritaria = delta.years * 12 + delta.months
                with col3: 
                    qntd_meses_atuacao_prioritaria = st.number_input("Quantidade de Meses em Exercício de Atuação Prioritária", value="" or qntd_meses_atuacao_prioritaria)

            pts_prioritaria = qntd_meses_atuacao_prioritaria * 0.333

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####

        pts_responsabilidade_unic = 0
        with sub_tabs[1]:
            #publicação de artigos
            pts_artigos = 0
            if st.checkbox("Quantidade de Artigos Científicos Publicados", value=False):
                col1,col2 = st.columns(2)
                with col1: 
                    qntd_periodicos_nid = st.number_input("Artigos Científicos Completos Publicados em Periódicos **NÃO** Indexados em Base de Dados Reconhecidos Nacional ou Internacionalmente, com ISSN",min_value=0)
                with col2: 
                    qntd_periodicos_id = st.number_input("Artigos Científicos Completos Publicados em Periódicos Indexados em Base de Dados Reconhecidos Nacional ou Internacionalmente, com ISSN",min_value = 0)
                st.session_state.pts_artigos =  (qntd_periodicos_nid * 0.5) + (qntd_periodicos_id * 4)

            #publicação de livros
            pts_livros = 0
            if st.checkbox("Quantidade de Publicações de Livros e Capítulos",value=False):
                col1,col2,col3 = st.columns(3)
                with col1: 
                    qntd_org_livros = st.number_input("Publicações como 'Organizador de Livro' com Editorial e ISBN",min_value = 0)
                with col2: 
                    qntd_capitulos = st.number_input("Capitulos Publicados",min_value = 0)
                with col3: 
                    qntd_livros_completos = st.number_input("Livros Completos Publicados",min_value = 0)
                st.session_state.pts_livros = (qntd_org_livros * 1) + (qntd_capitulos * 4) + (qntd_livros_completos * 6)

            #publicação de pesquisas
            pts_pesquisas = 0
            if st.checkbox("Quantidade de Publicações de Pesquisas Científicas", value=False):
                col1,col2,col3,col4 = st.columns(4)
                with col1: 
                    qntd_estadual = st.number_input("Pesquisas Científicas Aprovadas Estadualmente",min_value = 0)
                with col2: 
                    qntd_regional = st.number_input("Pesquisas Científicas Aprovadas Regionalmente",min_value = 0)
                with col3: 
                    qntd_nacional = st.number_input("Pesquisas Científicas Aprovadas Nacionalmente",min_value = 0)
                with col4: 
                    qntd_internacional = st.number_input("Pesquisas Científicas Aprovadas Internacionalmente",min_value = 0)
                st.session_state.pts_pesquisas = (qntd_estadual * 1) + (qntd_regional * 3) + (qntd_nacional * 3) + (qntd_internacional * 4)

            #registro de patente ou cultivar
            pts_registros = 0
            if st.checkbox("Quantidade de Registros de Patentes ou Cultivar", value=False):
                col1,col2 = st.columns(2)
                with col1: 
                    qntd_patente = st.number_input("Registros de Patente",min_value = 0)
                with col2: 
                    qntd_cultivar = st.number_input("Registros de Cultivar",min_value = 0)
                st.session_state.pts_registros = (qntd_patente * 8) + (qntd_cultivar * 8)

            #cursos
            pts_cursos = 0
            qntd_curso = 0
            if st.checkbox("Cursos e Treinamentos", value=False):
                col1,col2 = st.columns(2)
                with col1: 
                    tipo_curso = st.selectbox("Tipo de Curso",["Nenhum", "Estágio Pós-Doutoral no Orgão(6 meses)", "Pós-Doutorado(6 a 12 meses)", "Pós-Doutorado(13 a 24 meses)", "Pós-Doutorado(25 a 48 meses)", "Pós-Doutorado(maior que 48 meses)"])
                pts_doc1 = 0;pts_doc2 = 0;pts_doc3 = 0;pts_doc4 = 0;pts_doc5 = 0
                if tipo_curso != "Estágio Pós-Doutoral(6 meses)" and tipo_curso != "Nenhum":
                    with col2 : qntd_curso = st.number_input("Quantidade de Meses do Curso", min_value=0)
                if tipo_curso == "Estágio Pós-Doutoral no Orgão(6 meses)":
                    pts_doc1 = qntd_curso * 6
                if tipo_curso == "Pós-Doutorado(6 a 12 meses)":
                    pts_doc2 = qntd_curso * 8
                if tipo_curso == "Pós-Doutorado(13 a 24 meses)":
                    pts_doc3 = qntd_curso * 12
                if tipo_curso == "Pós-Doutorado(25 a 48 meses)":
                    pts_doc4 = qntd_curso * 24
                if tipo_curso == "Pós-Doutorado(maior que 48 meses)":
                    pts_doc5 = qntd_curso * 48
                st.session_state.pts_cursos = pts_doc1 + pts_doc2 + pts_doc3 + pts_doc4 + pts_doc5

    pts_artigos = st.session_state.pts_artigos if 'pts_artigos' in st.session_state else 0
    pts_livros = st.session_state.pts_livros if 'pts_livros' in st.session_state else 0
    pts_pesquisas = st.session_state.pts_pesquisas if 'pts_pesquisas' in st.session_state else 0
    pts_registros = st.session_state.pts_registros if 'pts_registros' in st.session_state else 0
    pts_cursos = st.session_state.pts_cursos if 'pts_cursos' in st.session_state else 0

    pts_responsabilidade_unic = pts_artigos + pts_livros + pts_pesquisas + pts_registros + pts_cursos + pts_conselho + pts_prioritaria
    pts_responsabilidade_mensais = pts_comissao + pts_func_comissionada + pts_func_designada + pts_agente + pts_conselho + pts_prioritaria

    pts_responsabilidade =  pts_comissao_total + pts_func_comissionada_total + pts_func_designada + pts_agente_total + pts_conselho + pts_prioritaria + pts_artigos + pts_livros + pts_pesquisas + pts_registros + pts_cursos
    if pts_responsabilidade >= 144:
        pts_responsabilidade = 144

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####

mes_t = 1
for i in range(721):
    carreira[i][0] = mes_t
    carreira[i][1] = 0.2
    carreira[i][2] = pts_desempenho / 6
    carreira[i][3] = pts_aperfeicoamento / 24
    mes_t += 1

for i in range(qntd_meses_comissao if qntd_meses_comissao != 0 else qntd_meses_funcao):
    carreira[i][6] = pts_responsabilidade_mensais

carreira[0][6] = pts_resp_inical + pts_responsabilidade_mensais

# Adicionar as titulações nos meses correspondentes
if 'tempo_exercicio' in locals() and tempo_exercicio:  # Verifica se a variável existe e foi definida
    pts_distribuidos = 0
    for key, data_conclusao in datas_tit.items():
        # Calcula quantos meses após o início do exercício a titulação foi concluída
        delta = relativedelta(data_conclusao, tempo_exercicio)
        meses_desde_inicio = delta.years * 12 + delta.months
        
        # Ajusta o índice (0 = mês inicial, 1 = mês seguinte, etc.)
        idx = min(720, max(0, meses_desde_inicio))  # Limita a 720 meses (60 anos)
        
        # Adiciona os pontos conforme o tipo de titulação
        pts_tit = 0
        if key.startswith('grad_'):
            pts_tit = 6  # Pontos por graduação
        elif key.startswith('esp_'):
            pts_tit = 12  # Pontos por especialização
        elif key.startswith('mest_'):
            pts_tit = 24  # Pontos por mestrado
        elif key.startswith('doc_'):
            pts_tit = 48  # Pontos por doutorado
        
         # Verifica se ainda podemos adicionar pontos sem ultrapassar o limite
        if (pts_distribuidos + pts_tit) <= pts_titulacao:
            carreira[idx][4] += pts_tit
            pts_distribuidos += pts_tit
        else:
            # Adiciona apenas o restante necessário para completar 144 pontos
            restante = pts_titulacao - pts_distribuidos
            if restante > 0:
                carreira[idx][4] += restante
                pts_distribuidos += restante
            break


carreira[0][5] = pts_responsabilidade_unic


carreira[0][7] = sum(carreira[0][1:7])
for i in range(721):
    carreira[i][7] = carreira[i-1][7] + sum(carreira[i][1:7])

with tab4:

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Obrigatórios", round(pts_obrigatorios, 4))
    col2.metric("Titulações", round(pts_titulacao, 4))
    col3.metric("Responsabilidade Inicial (5 anos)", round(pts_resp_inical, 4))
    col3.metric("Responsabilidade Mensal", round(pts_resp_inical_mes, 4))
    col4.metric("Responsabilidade Atual", round(pts_responsabilidade, 4))
    col5.metric("Responsabilidade Unicas", round(pts_responsabilidade_unic, 4))
    col5.metric("Responsabilidade Mensais", round(pts_responsabilidade_mensais, 4))
    col6.metric("Acumulado (1° Mês)", round(carreira[0][7], 4))

    ##Calculo Acumulado##
    resultado_niveis = []
    if st.button("Calcular", type='primary'):
        try:

            print("Calculando...")
            for linha in carreira:
                print(" | ".join(f"{valor:10.4f}" for valor in linha))

            
             # Criar DataFrame com todas as colunas
            df_carreira = pd.DataFrame(carreira, columns=[
                "Mês",
                "Pontos Base (0.2)",
                "Desempenho",
                "Aperfeiçoamento",
                "Titulação",
                "Resp. Únicas",
                "Resp. Mensais",
                "Total Acumulado",
                "Coluna 9",  
                "Coluna 10"  
            ])
            
            # Arredondar para 4 casas decimais
            df_carreira = df_carreira.round(4)
            
            # Selecionar meses para exibição (primeiros 12 + um por ano após)
            meses_exibir = list(range(721))
            df_exibir = df_carreira.iloc[meses_exibir]
            
            # Configurar formatação de exibição
            pd.options.display.float_format = '{:.4f}'.format
            
            # Mostrar tabela com colunas selecionadas
            st.dataframe(
                df_exibir[[
                    "Mês",
                    "Pontos Base (0.2)",
                    "Desempenho",
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
                    "Mês": st.column_config.NumberColumn(format="%d"),
                    "Pontos Base (0.2)": st.column_config.NumberColumn(format="%.4f"),
                    "Desempenho": st.column_config.NumberColumn(format="%.4f"),
                    "Aperfeiçoamento": st.column_config.NumberColumn(format="%.4f"),
                    "Titulação": st.column_config.NumberColumn(format="%.4f"),
                    "Resp. Únicas":st.column_config.NumberColumn(format="%.4f"),
                    "Resp. Mensais": st.column_config.NumberColumn(format="%.4f"),
                    "Total Acumulado": st.column_config.NumberColumn(format="%.4f")
                }
            )
            
        

            # Nível A (sempre 1 mês)
            resultado_niveis.append({
                "Nível": "A",
                "Mês Alcançado": 1,
                "Tempo Entre Níveis (meses)": 1,
                "Total": "1 mês"
            })

            # Dados dos níveis subsequentes
            niveis = [
                {"letra": "B", "subtracao": 0},
                {"letra": "C", "subtracao": 48},
                {"letra": "D", "subtracao": 96},
                {"letra": "E", "subtracao": 144},
                {"letra": "F", "subtracao": 192},
                {"letra": "G", "subtracao": 240},
                {"letra": "H", "subtracao": 288},
                {"letra": "I", "subtracao": 336},
                {"letra": "J", "subtracao": 384},
                {"letra": "K", "subtracao": 432},
                {"letra": "L", "subtracao": 480},
                {"letra": "M", "subtracao": 528},
                {"letra": "N", "subtracao": 576},
                {"letra": "O", "subtracao": 624},
                {"letra": "P", "subtracao": 672},
                {"letra": "Q", "subtracao": 720},
                {"letra": "R", "subtracao": 768},
                {"letra": "S", "subtracao": 816}
            ]

            mes_t = 12  # Começa no mês 12 para o nível B
            mes_i = 12

            for nivel in niveis:
                letra = nivel["letra"]
                subtracao = nivel["subtracao"]
                
                if letra != "B":
                    mes_i = 12
                    mes_t += 12
                
                acumulado = carreira[mes_t - 1][7] - subtracao
                
                if acumulado >= 96:
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": letra,
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })
                    continue
                
                encontrado = False
                # Verifica os próximos 6 meses (13 a 18)
                for j in range(6):
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t - 1][7] - subtracao
                    
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": letra,
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        encontrado = True
                        break
                
                if encontrado:
                    continue
                
                # Se não encontrou nos 6 meses seguintes, procura até atingir 48
                if acumulado >= 48:
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": letra,
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })
                else:
                    i = mes_t - 1  # Começa no último mês verificado
                    meses_adicionais = 0
                    while True:
                        i += 1
                        meses_adicionais += 1
                        acumulado = carreira[i][7] - subtracao
                        if acumulado >= 48:
                            mes_t = carreira[i][0]
                            mes_i = 12 + 6 + meses_adicionais  # 12 meses base + 6 meses verificados + meses adicionais
                            break
                    
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": letra,
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            df_resultados = pd.DataFrame(resultado_niveis)
            st.subheader("Resumo dos Níveis")
            st.dataframe(df_resultados.head(20), hide_index=True, height=700)

        except Exception as e:
            st.error(f"Erro ao calcular: {e}")

