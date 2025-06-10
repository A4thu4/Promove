import streamlit as st
import pandas as pd 
from openpyxl import load_workbook 
import os, shutil
from io import BytesIO 
from xlcalculator import ModelCompiler, Evaluator

#-----------------------------------------------------------------------------------#
st.set_page_config(page_title="PlanilhaPD", layout="wide")
st.title("Simulador Git")

from coleta import *
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

def recalcular_excel(caminho_arquivo, celulas_saida):
    compiler = ModelCompiler()
    model = compiler.read_and_parse_archive(caminho_arquivo)
    evaluator = Evaluator(model)
        
    resultados = {}
    for celula in celulas_saida:
        try:
            resultados[celula] = evaluator.evaluate(celula)
        except Exception as e:
            resultados[celula] = f"Erro: {e}"
    return resultados

### Calcular Pontuação ###
if st.button("Calcular"):
    if qntd_meses_tee == 0:
        qntd_meses_tee = 1

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

    try:
        workbook = load_workbook(filename=caminho_copia)
        aba = workbook["CARREIRA"]

        escrever_celula(aba, "J6", pts_desempenho)
        escrever_celula(aba, "L5", pts_aperfeicoamento)
        escrever_celula(aba, f"O{i}", pts_titulacao)
        escrever_celula(aba, f"P{i}", pts_responsabilidade)

        workbook.save(filename=caminho_copia)

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {str(e)}")

    # Define as células que serão avaliadas
    celulas_saida = (
        ['CARREIRA!AG15', 'CARREIRA!AK15', 'CARREIRA!AM15']
        if pts_alcancada >= 96
        else ['CARREIRA!AO15', 'CARREIRA!AS15', 'CARREIRA!AU15']
    )

    # Chama a função de recalcular
    resultados = recalcular_excel(caminho_copia, celulas_saida)

    # Exibe os resultados recalculados
    df_resultados = pd.DataFrame(resultados.items(), columns=["Célula", "Valor"])
    st.subheader("Resultados Recalculados")
    st.dataframe(df_resultados)

    # Permitir download dos resultados
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_resultados.to_excel(writer, sheet_name='RESULTADOS', index=False)

    st.download_button(
        label="Baixar Resultados",
        data=output.getvalue(),
        file_name="RESULTADOS - PROMOVE.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Remove arquivo temporário
    if os.path.exists(caminho_copia):
        try:
            os.remove(caminho_copia)
        except:
            pass
