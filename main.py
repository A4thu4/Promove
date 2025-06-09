import streamlit as st
import pandas as pd 
from openpyxl import load_workbook 
import os, shutil, platform
from io import BytesIO 

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
            df_filtrado = df_atualizado

        qtd_linhas = 19 - nivel_idx[0] if not nivel_idx.empty else 19
        st.dataframe(df_filtrado.head(qtd_linhas), hide_index=True)
        
        # Download do arquivo modificado

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtrado.head(qtd_linhas).to_excel(
                writer,
                sheet_name='RESULTADOS',
                index=False
            )
        
        st.download_button(
            label="Baixar Resultados",
            data=output.getvalue(),
            file_name="RESULTADOS - PROMOVE.xlsx",
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