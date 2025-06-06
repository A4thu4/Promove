import streamlit as st
import pandas as pd 
from datetime import datetime 
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook 
import os, shutil, platform

#-----------------------------------------------------------------------------------#
st.set_page_config(page_title="PlanilhaPD", layout="wide")
st.title("Simulador Git")

tipo_calculo = st.radio("Selecione SEU Tipo:", ["Geral", "UEG"], horizontal=True)
nivel_atual = st.radio("Selecione SEU Nível Atual:", ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S"], horizontal = True)
possuir_fae = st.radio("Possui Aposentadoria Especial?", ["Sim", "Não"], horizontal=True)

# Critérios obrigatórios
st.header("Critérios Obrigatórios")

#tempo exercicio e afastamento
col1, col2 = st.columns(2)
with col1:
    tempo_exercicio = st.date_input("Tempo de Início de Efetivo Exercício", format="DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())

# Calcular o tempo de exercício em meses
if tempo_exercicio:
    data_atual = datetime.now().date()  # Data atual
    if tempo_exercicio <= data_atual:
        delta = relativedelta(data_atual, tempo_exercicio)
        qntd_meses_tee = delta.years * 12 + delta.months
    else:
        st.error("A data de início deve ser anterior ou igual à data atual.")
else:
    qntd_meses_tee = 0
with col2:
    st.text_input("Quantidade de Meses em Exercício", value=str(qntd_meses_tee))

col1,col2 = st.columns(2)
with col1: 
    afastamento_1 = st.number_input("Tempo de Afastamento Referente ao Art. 4º da Lei nº 23.241/2023 (DIAS)",min_value=0)
with col2: 
    afastamento_2 = st.number_input("Tempo de Afastamento Referente ao Art. 5º da Lei nº 23.241/2023 (DIAS)",min_value=0)
desconto = 0
if afastamento_2 != 0:
    try:
        afastamento_2 = int(afastamento_2)
        desconto = afastamento_2 * 0.0067
    except ValueError:
        st.error("Insira um número valido.")
#tempo efetivo exercicio (mensal = 0.2 | semestral = 1.2 | anual = 2.4)         
pts_TEE = 0.2 - desconto

tempo_afastamento = afastamento_1 + afastamento_2
if tempo_afastamento:
    try:
        tempo_afastamento = int(tempo_afastamento)
    except ValueError:
        st.error("Insira um número valido.")

#avaliacao Pontuação Geral(min_value=7, max_value=11.4) Pontuação UEG(min_value=8.40, max_value=13.68)
if tipo_calculo == "Geral":
    pts_desempenho = st.number_input("Avaliação de Desempenho Individual", min_value=7.0, max_value=11.4)
else:
    pts_desempenho = st.number_input("Avaliação de Desempenho Individual", min_value=8.40, max_value=13.68)

#aperfeicoamento Pontos (min = 5.34 e max = 9.00) Horas (min_value=60, max_value=100) 
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

pts_obrigatorios = pts_TEE + (pts_desempenho / 6) + (pts_aperfeicoamento / 24)
st.info("Pontuação Mensal Padrão: " + str(pts_obrigatorios))

##Aceleradores [max 144 pontos]
st.header("Titulação Acadêmica")
graduacao = st.number_input("Graduação", min_value=0)
especializacao = st.number_input("Especialização", min_value=0)
mestrado = st.number_input("Mestrado", min_value=0)
doutorado = st.number_input("Doutorado", min_value=0)

pts_titulacao = (graduacao * 6) + (especializacao * 12 ) + (mestrado * 24) + (doutorado * 48)
if pts_titulacao > 144:
    pts_titulacao  = 144

st.info("Pontuação Total de Titulação: " + str(pts_titulacao))

##Responsabilidades [max 144 pontos]
st.header("Assunção de Responsabilidade")

#cargo de comissao
col1, col2, col3, col4 = st.columns(4)
with col1:
    cargo_comissao = st.selectbox("Exercício em Cargo de Comissão", ["AE-1","AE-2","AEG","DAI-1","DAI-2","DAI-3","DAID-1","DAID-2","DAID-3","DAID-4","DAID-5","DAID-6","DAID-7","DAID-8","DAID-9","DAID-10","DAID-11","DAID-12","DAID-13","DAID-14","DAID-1A","DAID-1B","DAS-1","DAS-2","DAS-3","DAS-4","DAS-5","DAS-6","DAS-7"])
with col2:
    data_inicio_comissao = st.date_input("Data de Inicio no Cargo", format="DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
with col3:
    data_fim_comissao = st.date_input("Data de Encerramento no Cargo", format="DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())

qntd_meses_comissao = 0
if data_inicio_comissao and data_fim_comissao:
    if data_inicio_comissao <= data_fim_comissao:
        delta = relativedelta(data_fim_comissao, data_inicio_comissao)
        qntd_meses_comissao = delta.years * 12 + delta.months
    else:
        st.error("A data de início deve ser anterior ou igual à data de fim.")
with col4:
    st.number_input("Quantidade de Meses em Cargo",  min_value=0, value=qntd_meses_comissao)
if cargo_comissao in ["DAS-1", "DAS-2"]:
    pts_comissao = qntd_meses_comissao * 1.000
elif cargo_comissao in ["DAS-3", "DAS-4"]:
    pts_comissao = qntd_meses_comissao * 0.889
elif cargo_comissao in ["DAS-5", "DAS-6", "DAS-7", "DAID-1A", "AEG"]:
    pts_comissao = qntd_meses_comissao * 0.800
elif cargo_comissao in ["DAI-1", "DAID-1", "DAID-1B", "DAID-2", "AE-1", "AE-2"]:
    pts_comissao = qntd_meses_comissao * 0.667
elif cargo_comissao in ["DAI-2", "DAI-3", "DAID-4", "DAID-5", "DAID-6", "DAID-7", "DAID-8", "DAID-9", "DAID-10", "DAID-11", "DAID-12", "DAID-13", "DAID-14"]:
    pts_comissao = qntd_meses_comissao * 0.500

#função comissionada
col1, col2, col3, col4 = st.columns(4)
with col1: 
    funcao_comissionada = st.selectbox("Exercício de Função Comissionada ou Gratificada",["até R$ 750,00","R$ 751,00 a R$ 1.200,00","R$ 1.201,00 a R$ 1.650,00","R$ 1.651,00 a R$ 2.250,00","acima de 2.250,00"])
with col2: 
    data_inicio_fun_com = st.date_input("Data de Inicio na Função", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
with col3: 
    data_fim_func_com = st.date_input("Data de Encerramento na Função", format = "DD/MM/YYYY", min_value=datetime(1990, 1, 1), max_value=datetime.now().date())
qntd_meses_funcao = 0
if data_fim_func_com and data_inicio_fun_com:
    delta = relativedelta(data_fim_func_com, data_inicio_fun_com)
    qntd_meses_funcao = delta.years * 12 + delta.months
with col4: st.text_input("Quantidade de Meses em Função", value=str(qntd_meses_funcao))
if funcao_comissionada == "até R$ 750,00":
    pts_func_comissionada = qntd_meses_funcao * 0.333
elif funcao_comissionada == "R$ 751,00 a R$ 1.200,00":
    pts_func_comissionada = qntd_meses_funcao * 0.364
elif funcao_comissionada == "R$ 1.201,00 a R$ 1.650,00":
    pts_func_comissionada = qntd_meses_funcao * 0.400
elif funcao_comissionada == "R$ 1.651,00 a R$ 2.250,00":
    pts_func_comissionada = qntd_meses_funcao * 0.444
elif funcao_comissionada == "acima de 2.250,00":
    pts_func_comissionada = qntd_meses_funcao * 0.500

#função designada
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
col1, col2, col3, col4 = st.columns(4)
with col1: 
    atuacao_agente = st.selectbox("Agente de Contratação, Gestor/Fiscal de Contratos/Convênios",["Não Atuou","I","II","III","IV","V"])
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
if atuacao_agente == "I":
    pts_agente = qntd_meses_atuacao * 0.333
elif atuacao_agente == "II":
    pts_agente = qntd_meses_atuacao * 0.364
elif atuacao_agente == "III":
    pts_agente = qntd_meses_atuacao * 0.400
elif atuacao_agente == "IV":
    pts_agente = qntd_meses_atuacao * 0.444
elif atuacao_agente == "V":
    pts_agente = qntd_meses_atuacao * 0.500
else:
    pts_agente = 0

#atuação em conselho
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

#publicação de artigos
col1,col2 = st.columns(2)
with col1: 
    qntd_periodicos_nid = st.number_input("Quantidade de Artigos Científicos Completos Publicados em Periódicos NÃO Indexados em Base de Dados Reconhecidos Nacional ou Internacionalmente, com ISSN",min_value=0)
with col2: 
    qntd_periodicos_id = st.number_input("Quantidade de Artigos Científicos Completos Publicados em Periódicos Indexados em Base de Dados Reconhecidos Nacional ou Internacionalmente, com ISSN",min_value = 0)
pts_artigos =  (qntd_periodicos_nid * 0.5) + (qntd_periodicos_id * 4)

#publicação de livros
col1,col2,col3 = st.columns(3)
with col1: 
    qntd_org_livros = st.number_input("Quantidade de Publicações como 'Organizador de Livro' com Editorial e ISBN",min_value = 0)
with col2: 
    qntd_capitulos = st.number_input("Quantidade de Capitulos Publicados",min_value = 0)
with col3: 
    qntd_livros_completos = st.number_input("Quantidade de Livros Completos Publicados",min_value = 0)
pts_livros = (qntd_org_livros * 1) + (qntd_capitulos * 4) + (qntd_livros_completos * 6)

#publicação de pesquisas
col1,col2,col3,col4 = st.columns(4)
with col1: 
    qntd_estadual = st.number_input("Quantidade de Pesquisas Científicas Aprovadas Estadualmente",min_value = 0)
with col2: 
    qntd_regional = st.number_input("Quantidade de Pesquisas Científicas Aprovadas Regionalmente",min_value = 0)
with col3: 
    qntd_nacional = st.number_input("Quantidade de Pesquisas Científicas Aprovadas Nacionalmente",min_value = 0)
with col4: 
    qntd_internacional = st.number_input("Quantidade de Pesquisas Científicas Aprovadas Internacionalmente",min_value = 0)
pts_pesquisas = (qntd_estadual * 1) + (qntd_regional * 3) + (qntd_nacional * 3) + (qntd_internacional * 4)

#registro de patente ou cultivar
col1,col2 = st.columns(2)
with col1: 
    qntd_patente = st.number_input("Quantidade de Registros de Patente",min_value = 0)
with col2: 
    qntd_cultivar = st.number_input("Quantidade de Registros de Cultivar",min_value = 0)
pts_registros = (qntd_patente * 8) + (qntd_cultivar * 8)

#cursos
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
pts_cursos = pts_doc1 + pts_doc2 + pts_doc3 + pts_doc4 + pts_doc5

pts_responsabilidade =  pts_comissao + pts_func_comissionada + pts_func_designada + pts_agente + pts_conselho + pts_prioritaria + pts_artigos + pts_livros + pts_pesquisas + pts_registros + pts_cursos
if pts_responsabilidade > 144:
    pts_responsabilidade = 144
st.info("**Pontuação Total de Responsabilidade:** " + str(pts_responsabilidade))

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

caminho_planilha = "PROMOVE - Arthur 2.xlsx"
nome_planilha = "CARREIRA"

def detectar_header(excel_file, aba):
    """Tenta detectar a linha com a coluna Desejada"""
    for i in range(10):
        try:
            df_temp = pd.read_excel(excel_file, sheet_name=aba, skiprows=i, usecols="G:W")
            colunas = [str(col).strip().upper() for col in df_temp.columns]
            if "PERÍODO" in colunas:
                return i
        except:
            continue
    return 0  # fallback se não encontrar

### Calcular Pontuação ###
if st.button("Calcular"):
    if qntd_meses_tee == 0: qntd_meses_tee = 1

    caminho_copia = "PROMOVE - Resultados.xlsx"
    shutil.copy(caminho_planilha, caminho_copia)

    pts_mensal = pts_TEE + (pts_desempenho / 6) + (pts_aperfeicoamento / 24)
    pts_extras = pts_titulacao + pts_responsabilidade
    pts_alcancada = pts_mensal + pts_extras
    pontuacao_total = (pts_mensal * qntd_meses_tee) + pts_extras
    i = max(1, qntd_meses_tee + 12)

    def escrever_celula(aba, celula_ref, valor):
        try:            
            aba[celula_ref] = valor
        except Exception as e:
                st.error(f"Erro ao escrever na célula {celula_ref}: {e}")

    if caminho_planilha is not None:
        try:
            if isinstance(caminho_planilha, str):
                workbook = load_workbook(filename=caminho_copia)
            else:
                workbook = load_workbook(filename=caminho_copia.getvalue())

            aba = workbook["CARREIRA"]
                
            escrever_celula(aba, "J6", pts_desempenho)
            escrever_celula(aba, "L5", pts_aperfeicoamento)
            escrever_celula(aba, f"O{i}", pts_titulacao)
            escrever_celula(aba, f"P{i}", pts_responsabilidade)
            
            workbook.save(filename=caminho_copia)
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

    def recalcular_excel(caminho):
        if platform.system() == "Windows":
            import xlwings as xw
            # Recalcular fórmulas usando xlwings
            app = xw.App(visible=False)
            wb = app.books.open(os.path.abspath(caminho))
            wb.api.Calculate()  # Recalcula fórmulas
            wb.save()
            wb.close()
            app.quit()
        
        else:
            # Fallback para nuvem
            from openpyxl import load_workbook
            wb = load_workbook(filename=caminho)
            wb.save(filename=caminho)

    recalcular_excel(caminho_copia)

    workbook = load_workbook(filename=caminho_copia,data_only=True)
    aba = workbook.active

    try:
        # Leitura dos resultados
        df_atualizado = pd.read_excel(
            caminho_copia,
            sheet_name="CARREIRA",
            usecols="AG,AK,AM" if pts_alcancada >= 96 else "AO,AS,AU",
            skiprows=lambda x: x in list(range(13)) + [14],
            engine="openpyxl"
        )
        
        # Exibição dos resultados
        st.subheader("Planilha Atualizada")
        novos_nomes = {
            "Unnamed: 32": "Nível",
            "Unnamed: 36": "Tempo",
            "Unnamed: 38": "Entre Niveis",
            "Unnamed: 40": "Nível",
            "Unnamed: 44": "Tempo",
            "Unnamed: 46": "Entre Niveis"
        }

        df_atualizado.rename(columns=novos_nomes, inplace=True)

        nivel_idx = (df_atualizado[df_atualizado["Nível"] == nivel_atual].index) + 1
        if not nivel_idx.empty:
            df_filtrado = df_atualizado.loc[nivel_idx[0]:].reset_index(drop=True)
        else : 
            df_filtrado = df_filtrado

        qtd_linhas = 19 - nivel_idx[0] if not nivel_idx.empty else 19
        st.dataframe(df_filtrado.head(qtd_linhas), hide_index=True)
        
        # Download do arquivo modificado
        df_export = df_filtrado.head(qtd_linhas).copy()
    
        # Cria um novo arquivo Excel simplificado
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name='RESULTADOS', index=False)
        
        # Configura o botão de download
        st.download_button(
            label="Baixar Resultados Simplificados",
            data=output.getvalue(),
            file_name="RESULTADOS_PROMOVE.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
    finally:
        for path in [caminho_copia]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass