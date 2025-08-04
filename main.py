import streamlit as st
import pandas as pd 
from datetime import datetime 
from dateutil.relativedelta import relativedelta

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
st.set_page_config(page_title="Simulador PROMOVE-GNCP", layout="wide")
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


carreira = [[0 for _ in range(10)] for _ in range(721)]

tipo_calculo = "Geral"
tab1, tab2, tab3, tab4 = st.tabs(["**Critérios Obrigatórios**", "**Titulação Acadêmica**", "**Assunção de Responsabilidades**", "**Pontuação Final**"])

##Critérios obrigatórios##
with tab1:
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
    graduacao = st.number_input("Graduação", min_value=0, key="graduacao")
    especializacao = st.number_input("Especialização", min_value=0, key="especializacao")
    mestrado = st.number_input("Mestrado", min_value=0, key="mestrado")
    doutorado = st.number_input("Doutorado", min_value=0, key="doutorado")

    pts_titulacao = (graduacao * 6) + (especializacao * 12) + (mestrado * 24) + (doutorado * 48)

    if pts_titulacao >= 144:
        pts_titulacao = 144

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####

with tab3:
    subtabs = st.tabs(["**Assunção de Responsabilidade dos últimos 5 anos**", "**Assunção de Responsabilidades Atuais**"])
    pts_resp_inical = 0
    with subtabs[0]:
            col1,col2 = st.columns(2)
            with col1:
                cargo_comissao_5 = st.selectbox("Exercício em Cargo de Comissão", ["Nenhuma", "AE-1","AE-2","AEG","DAI-1","DAI-2","DAI-3","DAID-1","DAID-2","DAID-3","DAID-4","DAID-5","DAID-6","DAID-7","DAID-8","DAID-9","DAID-10","DAID-11","DAID-12","DAID-13","DAID-14","DAID-1A","DAID-1B","DAS-1","DAS-2","DAS-3","DAS-4","DAS-5","DAS-6","DAS-7"], key="cargo_5anos")

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

            with col2:
                funcao_comissionada_5 = st.selectbox("Exercício de Função Comissionada ou Gratificada",["Nenhuma", "até R$ 750,00","R$ 751,00 a R$ 1.200,00","R$ 1.201,00 a R$ 1.650,00","R$ 1.651,00 a R$ 2.250,00","acima de 2.250,00"], key="comissao_5anos")

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

    pts_resp_inical_mes = pts_comissao_5 + pts_func_comissionada_5
    pts_resp_inical = pts_resp_inical_mes * 60

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
                    data_inicio_comissao = st.date_input("Data de Inicio no Cargo", format="DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
                with col3:
                    data_fim_comissao = st.date_input("Data de Encerramento no Cargo", format="DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())

            qntd_meses_comissao = 0
            pts_comissao = 0
            if data_inicio_comissao and data_fim_comissao:
                if data_inicio_comissao <= data_fim_comissao:
                    delta = relativedelta(data_fim_comissao, data_inicio_comissao)
                    qntd_meses_comissao = delta.years * 12 + delta.months
                else:
                    st.error("A data de início deve ser anterior ou igual à data de fim.")
                with col4:
                    st.number_input("Quantidade de Meses em Cargo",  min_value=0, value=qntd_meses_comissao)
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
                    data_inicio_fun_com = st.date_input("Data de Inicio na Função", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
                with col3: 
                    data_fim_func_com = st.date_input("Data de Encerramento na Função", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())

                if data_fim_func_com and data_inicio_fun_com:
                    delta = relativedelta(data_fim_func_com, data_inicio_fun_com)
                    qntd_meses_funcao = delta.years * 12 + delta.months
                with col4: st.text_input("Quantidade de Meses em Função", value=str(qntd_meses_funcao))
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
                    data_inicio_fun_des = st.date_input("Data de Inicio do Exercício de Função Designada", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
                with col2: 
                    data_fim_func_des = st.date_input("Data de Encerramento do Exercício de Função Designada", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
                qntd_meses_func_des = 0
                if data_fim_func_des and data_inicio_fun_des:
                    delta = relativedelta(data_fim_func_des, data_inicio_fun_des)
                    qntd_meses_func_des = delta.years * 12 + delta.months
                with col3: 
                    st.text_input("Quantidade de Meses em Exercício de Função Designada", value=str(qntd_meses_func_des))

            pts_func_designada = qntd_meses_func_des * 0.333

            #atuação como agente
            with st.expander("Atuação como Agente de Contratação, Gestor/Fiscal de Contratos/Convênios"):
                col1, col2, col3, col4 = st.columns(4)
                with col1: 
                    atuacao_agente = st.selectbox("Agente de Contratação, Gestor/Fiscal de Contratos/Convênios",["Nenhum","I","II","III","IV","V"])
                with col2: 
                    data_inicio_atuacao = st.date_input("Data de Inicio na Atuação", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
                with col3: 
                    data_fim_atuacao = st.date_input("Data de Encerramento na Atuação", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
                qntd_meses_atuacao = 0
                if atuacao_agente != "Não Atuou":
                    if data_fim_atuacao and data_inicio_atuacao:
                        delta = relativedelta(data_fim_atuacao, data_inicio_atuacao)
                        qntd_meses_atuacao = delta.years * 12 + delta.months
                with col4: 
                    st.text_input("Quantidade de Meses em Atuação", value=str(qntd_meses_atuacao))
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
                    data_inicio_atuacao_cons = st.date_input("Data de Iniciamento da Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
                with col2: 
                    data_fim_atuacao_cons = st.date_input("Data de Encerramento da Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
                qntd_meses_atuacao_conselho = 0
                if data_fim_atuacao_cons and data_inicio_atuacao_cons:
                    delta = relativedelta(data_fim_atuacao_cons, data_inicio_atuacao_cons)
                    qntd_meses_atuacao_conselho = delta.years * 12 + delta.months
                with col3: 
                    st.text_input("Quantidade de Meses de Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho", value=str(qntd_meses_atuacao_conselho))
            
            pts_conselho = qntd_meses_atuacao_conselho * 0.333

            #atuação prioritaria
            with st.expander("Exercício de Atuação Prioritária"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    data_inicio_atuacao_priori = st.date_input("Data de Início do Exercício de Atuação Prioritária", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
                with col2:
                    data_fim_atuacao_priori = st.date_input("Data de Encerramento do Exercício de Atuação Prioritária", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
                qntd_meses_atuacao_prioritaria = 0
                if data_fim_atuacao_priori and data_inicio_atuacao_priori:
                    delta = relativedelta(data_fim_atuacao_priori, data_inicio_atuacao_priori)
                    qntd_meses_atuacao_prioritaria = delta.years * 12 + delta.months
                with col3: 
                    st.text_input("Quantidade de Meses em Exercício de Atuação Prioritária", value=str(qntd_meses_atuacao_prioritaria))

            pts_prioritaria = qntd_meses_atuacao_prioritaria *0.333

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####

        pts_responsabilidade_unic = 0
        with sub_tabs[1]:
            #publicação de artigos
            pts_artigos = 0
            if st.checkbox("Publicação de Artigos Científicos", value=False):
                col1,col2 = st.columns(2)
                with col1: 
                    qntd_periodicos_nid = st.number_input("Quantidade de Artigos Científicos Completos Publicados em Periódicos NÃO Indexados em Base de Dados Reconhecidos Nacional ou Internacionalmente, com ISSN",min_value=0)
                with col2: 
                    qntd_periodicos_id = st.number_input("Quantidade de Artigos Científicos Completos Publicados em Periódicos Indexados em Base de Dados Reconhecidos Nacional ou Internacionalmente, com ISSN",min_value = 0)
                st.session_state.pts_artigos =  (qntd_periodicos_nid * 0.5) + (qntd_periodicos_id * 4)

            #publicação de livros
            pts_livros = 0
            if st.checkbox("Publicação de Livros e Capítulos",value=False):
                col1,col2,col3 = st.columns(3)
                with col1: 
                    qntd_org_livros = st.number_input("Quantidade de Publicações como 'Organizador de Livro' com Editorial e ISBN",min_value = 0)
                with col2: 
                    qntd_capitulos = st.number_input("Quantidade de Capitulos Publicados",min_value = 0)
                with col3: 
                    qntd_livros_completos = st.number_input("Quantidade de Livros Completos Publicados",min_value = 0)
                st.session_state.pts_livros = (qntd_org_livros * 1) + (qntd_capitulos * 4) + (qntd_livros_completos * 6)

            #publicação de pesquisas
            pts_pesquisas = 0
            if st.checkbox("Publicação de Pesquisas Científicas", value=False):
                col1,col2,col3,col4 = st.columns(4)
                with col1: 
                    qntd_estadual = st.number_input("Quantidade de Pesquisas Científicas Aprovadas Estadualmente",min_value = 0)
                with col2: 
                    qntd_regional = st.number_input("Quantidade de Pesquisas Científicas Aprovadas Regionalmente",min_value = 0)
                with col3: 
                    qntd_nacional = st.number_input("Quantidade de Pesquisas Científicas Aprovadas Nacionalmente",min_value = 0)
                with col4: 
                    qntd_internacional = st.number_input("Quantidade de Pesquisas Científicas Aprovadas Internacionalmente",min_value = 0)
                st.session_state.pts_pesquisas = (qntd_estadual * 1) + (qntd_regional * 3) + (qntd_nacional * 3) + (qntd_internacional * 4)

            #registro de patente ou cultivar
            pts_registros = 0
            if st.checkbox("Registro de Patente ou Cultivar", value=False):
                col1,col2 = st.columns(2)
                with col1: 
                    qntd_patente = st.number_input("Quantidade de Registros de Patente",min_value = 0)
                with col2: 
                    qntd_cultivar = st.number_input("Quantidade de Registros de Cultivar",min_value = 0)
                st.session_state.pts_registros = (qntd_patente * 8) + (qntd_cultivar * 8)

            #cursos
            pts_cursos = 0
            qntd_curso = 0
            if st.checkbox("Cursos e Treinamentos", value=False):
                col1,col2 = st.columns(2)
                with col1: 
                    tipo_curso = st.selectbox("Tipo de Curso",["Nenhum","Estágio Pós-Doutoral no Orgão(6 meses)","Pós-Doutorado(6 a 12 meses)","Pós-Doutorado(13 a 24 meses)","Pós-Doutorado(25 a 48 meses)","Pós-Doutorado(maior que 48 meses)"])
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
carreira[0][4] = pts_titulacao
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
    col6.metric("Acumulado", round(carreira[0][7], 4))

    ##Calculo Acumulado##
    resultado_niveis = []
    if st.button("Calcular", type='primary'):
        try:

            # Nível A
            resultado_niveis.append({
                "Nível": "A",
                "Mês Alcançado": 1,
                "Tempo Entre Níveis (meses)": 1,
                "Total": f"{1} mês"
            })

            # Nível B
            mes_t = 12
            mes_i = 12
            acumulado = carreira[11][7] # mês 12

            encontrado  = False
            for i in range(12, 18):
                if carreira[i][7] >= 96:
                    acumulado = carreira[i][7]
                    mes_t = i
                    mes_i = mes_t 
                    encontrado = True
                    break

            if not encontrado:
                i = 17
                mes_i -= 1  # compensar o último incremento
                while acumulado < 48:
                    i += 1
                    acumulado = carreira[i][7]
                    mes_t = carreira[i][0]
                    mes_i += 1

            anos = mes_t // 12
            resto = mes_t % 12
            resultado_niveis.append({
                "Nível": "B",
                "Mês Alcançado": mes_t,
                "Tempo Entre Níveis (meses)": mes_i,
                "Total": f"{anos} ano(s) {resto} mês(es)"
            })

            # Nível C
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t - 1][7] - 48

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "C",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                encontrado = False
                for j in range(1, 6):  # Tenta os próximos 5 meses (até mês 18)
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t - 1][7] - 48
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "C",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        encontrado = True
                        break

                if not encontrado:
                    if acumulado >= 48:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "C",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                    else:
                        i = mes_t - 1
                        while carreira[i][7] - 48 < 48:
                            i += 1
                            mes_t = carreira[i][0]
                            mes_i += 1
                        anos = mes_t // 12
                        resto = mes_t % 12
                        mes_i -= 1
                        resultado_niveis.append({
                            "Nível": "C",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                
            # Nível D
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t - 1][7] - 96

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "D",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                encontrado = False
                for _ in range(6):  # Tentativas de 13 a 18 (mais 6 meses)
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t - 1][7] - 96
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "D",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        encontrado = True
                        break

                if not encontrado:
                    if acumulado >= 48:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "D",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                    else:
                        i = mes_t - 1
                        while carreira[i][7] - 96 < 48:
                            i += 1
                            mes_t = carreira[i][0]
                            mes_i += 1
                        mes_i -= 1
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "D",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
            
            # Nível E
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 144

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "E",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 144
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "E",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 144
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 144
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "E",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível F
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 192

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "F",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 192
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "F",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 192
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 192
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "F",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })
            
            # Nível G
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 240

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "G",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 240
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "G",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 240
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 240
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "G",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível H
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 288

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "H",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 288
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "H",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 288
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 288
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "H",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível I
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 336

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "I",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 336
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "I",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 336
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 336
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "I",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível J
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 384

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "J",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 384
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "J",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 384
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 384
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "J",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível K
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 432

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "K",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 432
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "K",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 432
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 432
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "K",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível L
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 480

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "L",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 480
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "L",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 480
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 480
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "L",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível M
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 528

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "M",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 528
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "M",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 528
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 528
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "M",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível N
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 576

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "N",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 576
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "N",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 576
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 576
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "N",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível O
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 624

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "O",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 624
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "O",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 624
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 624
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "O",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível P
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 672

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "P",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 672
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "P",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 672
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 672
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "P",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível Q
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 720

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "Q",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 720
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "Q",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 720
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 720
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "Q",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível R
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 768

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "R",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 768
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "R",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 768
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 768
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "R",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            # Nível S
            mes_i = 12
            mes_t += 12
            acumulado = carreira[mes_t-1][7] - 816

            if acumulado >= 96:
                anos = mes_t // 12
                resto = mes_t % 12
                resultado_niveis.append({
                    "Nível": "S",
                    "Mês Alcançado": mes_t,
                    "Tempo Entre Níveis (meses)": mes_i,
                    "Total": f"{anos} ano(s) {resto} mês(es)"
                })
            else:
                for _ in range(6):  # mês 13 até 18
                    mes_i += 1
                    mes_t += 1
                    acumulado = carreira[mes_t-1][7] - 816
                    if acumulado >= 96:
                        anos = mes_t // 12
                        resto = mes_t % 12
                        resultado_niveis.append({
                            "Nível": "S",
                            "Mês Alcançado": mes_t,
                            "Tempo Entre Níveis (meses)": mes_i,
                            "Total": f"{anos} ano(s) {resto} mês(es)"
                        })
                        break
                else:
                    # se não encontrou dentro de 6 meses, entra em loop até atingir 48
                    i = mes_t - 1
                    acumulado = carreira[i][7] - 816
                    while acumulado < 48:
                        acumulado = carreira[i][7] - 816
                        mes_t = carreira[i][0]
                        i += 1
                        mes_i += 1

                    mes_i -= 1
                    anos = mes_t // 12
                    resto = mes_t % 12
                    resultado_niveis.append({
                        "Nível": "S",
                        "Mês Alcançado": mes_t,
                        "Tempo Entre Níveis (meses)": mes_i,
                        "Total": f"{anos} ano(s) {resto} mês(es)"
                    })

            df_resultados = pd.DataFrame(resultado_niveis)
            st.subheader("Resumo dos Níveis")
            st.dataframe(df_resultados.head(20), hide_index=True, height=700)

        except Exception as e:
            st.error(f"Erro ao calcular: {e}")

