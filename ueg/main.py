import streamlit as st
import sys
import os
import io
import gc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pandas as pd
from datetime import timedelta
from dateutil.relativedelta import relativedelta

try:
    from layout_ueg import clear_states, ensure_states, renderizar_planilha, build_obrigatorios, build_afastamentos, build_desempenho, build_titulacoes, build_responsabilidades_unicas, build_responsabilidades_mensais
    from data_utils_ueg import DATA_CONCLUSAO, destacar_obs
    from logic_ueg import zerar_carreira, calcular_evolucao, tratar_datas, calcular_planilha
except ImportError as e:
    st.error(f"Erro ao importar módulos: {str(e)}")
    st.stop()


def novo_calculo():
    st.cache_data.clear()
    clear_states()
    gc.collect()
    st.session_state.navigation = '**Cálculo Individual**'


def go_results():
    st.session_state.navigation = '**Resultados**'


def go_individual():
    st.session_state.navigation = '**Cálculo Individual**'    


def bloco_vertical(titulo, tamanho, cor):
    """
    Cria um bloco vertical com texto rotacionado.
    
    Args:
        titulo (str): Texto a ser exibido
        tamanho (int): Altura do bloco em pixels
        cor (str): Cor do bloco ('verde' ou 'amarelo')
    
    Returns:
        str: HTML do bloco vertical
    """
    cor_classe = "verde" if cor == "#003500" else "amarelo"
    
    return f"""
    <div class="bloco-vertical {cor_classe}" style="height: {tamanho}px;">
        {titulo}
    </div>
    """


path_brasao = os.path.join(ROOT_DIR, "assets", "brasao.png")
path_logo = os.path.join(ROOT_DIR, "assets", "logomarca.png")
path_css = os.path.join(ROOT_DIR, "assets", "style.css")

st.set_page_config(page_title="PROMOVE - Simulador UEG", page_icon=path_brasao if os.path.exists(path_brasao) else "📊", layout="wide")

if os.path.exists(path_css):
    with open(path_css, "r", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
else:
    st.warning(f"Arquivo CSS não encontrado em {path_css}")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(path_logo):
        st.image(path_logo, width=800)
    else:
        st.error(f"Erro: Imagem não encontrada em {path_logo}")


def main():
    ensure_states()

    # ---------- NAVEGAÇÃO ---------- #
    with st.sidebar:
        tabs = st.radio("Navegar",
            ['**Cálculo Individual**', '**Cálculo Múltiplo**', '**Resultados**'],
            key="navigation"
        )


    if tabs == '**Cálculo Individual**':
        st.markdown("<h1 class='center'>PROMOVE – Simulador de evoluções funcionais (UEG)</h1>", unsafe_allow_html=True)
       
        st.markdown(
            """
            <div class="alert-warning">
            <strong>⚠️ IMPORTANTE: o módulo de cálculo individual deste simulador destina-se à utilização por servidores <br>
            do Poder Executivo do Estado de Goiás cujas carreiras estejam vinculadas ao programa PROMOVE. </strong>
            </div>
            """, 
            unsafe_allow_html=True
        )

        if st.session_state.nivel_atual == 'O':
            st.markdown(
                f"""
                <div class="alert-success">
                <strong> NÍVEL MÁXIMO ATINGIDO: o servidor não pode evoluir além do nível {st.session_state.nivel_atual}. </strong>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            cl0, cl1, cl2 = st.columns([3, 1, 3])
            with cl1: st.button("🔄 Novo Cálculo", type="tertiary", on_click=novo_calculo)        
        
        else:
            col1, col2 = st.columns([0.05, 1.93])
            with col1: 
                st.markdown(bloco_vertical("", 900, "#003500"), unsafe_allow_html=True)
            with col2:
                build_obrigatorios()
                
                if st.session_state.data_inicial and not st.session_state.carreira:
                    st.session_state.data_fim = st.session_state.data_inicial + relativedelta(years=20)
                    DATA_FIM = st.session_state.data_fim
                    
                    data_inicio = st.session_state.data_inicial
                    if data_inicio.month == 12:
                        data_inicio = data_inicio.replace(year=data_inicio.year + 1, month=1, day=1)
                    else:
                        data_inicio = data_inicio.replace(month=data_inicio.month + 1, day=1)

                    # Inicializa a carreira no session state
                    st.session_state.carreira = [
                        [data_inicio + relativedelta(months=i)] + [0] * 6
                        for i in range(DATA_CONCLUSAO)
                    ]

                build_afastamentos()
                st.divider()
                
                build_desempenho()
                st.divider()
            
            col1, col2 = st.columns([0.05, 1.93])
            with col1: 
                st.markdown(bloco_vertical("", 2155, "#fede01"), unsafe_allow_html=True)
            with col2:
                build_titulacoes()
                st.divider()
                
                build_responsabilidades_mensais()
                st.divider()
                
                build_responsabilidades_unicas()

            st.write("")
            st.write("")
            c1, c2, c3 = st.columns([2.2, 2, 1])
            with c2: st.button("Calcular Resultados", type='secondary', on_click=go_results)


### CÁLCULO MÚLTIPLO ###
    elif tabs == '**Cálculo Múltiplo**':

        st.markdown("<h1 class='center'>PROMOVE – Simulador de evoluções funcionais (UEG)</h1>", unsafe_allow_html=True)
       
        st.markdown(
            """
            <div class="alert-warning">
            <strong>⚠️ IMPORTANTE: o módulo de cálculo múltiplo deste simulador destina-se à utilização por servidores lotados nas unidades setoriais e centrais de gestão e desenvolvimento de pessoas <br>
            ou em unidades a elas equivalentes, como ferramenta de apoio à gestão das carreiras do Poder Executivo do Estado de Goiás vinculadas ao programa PROMOVE. </strong>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
             """
            <div class="alert-info">
            <strong> Após o preenchimento da planilha do Excel fornecida pelo Órgão Central de Gestão de Pessoal,<br> segure e arraste o arquivo para a área abaixo 
            ou clique em “Carregar Arquivo” e o selecione na pasta do seu computador. </strong>
            </div>
            """, 
            unsafe_allow_html=True
        )

        cl00, cl11, cl12 = st.columns([3, 1, 3])
        with cl11:
            st.radio("**Aposentadoria Especial**", ['Não', 'Sim'], key="apo_especial_m", help="Marque esta opção SOMENTE se o servidor possuir direito à aposentadoria especial.", horizontal=True)
            apo_especial_m = st.session_state.apo_especial_m == "Sim"

        with st.form("form_calculo_multiplo", clear_on_submit=False):
            arquivo_up = st.file_uploader(
                "Selecione o arquivo",
                type=["xlsx", "xls", "xlsm"],
                key=f"wb_{st.session_state.file_reset}",
                label_visibility="hidden"
            )

            col_enviar, col_limpar = st.columns([0.1, 1.2])
        
            with col_enviar:
                submitted = st.form_submit_button("Calcular")
            with col_limpar:
                clear = st.form_submit_button("Limpar")
            
        ids_processados = []
        df_pview = pd.DataFrame()
        nome_base = ""
        if submitted:
            if not arquivo_up:
                st.warning("Carregue a planilha.")
                st.stop()

            nome_arquivo = arquivo_up.name
            nome_base = os.path.splitext(nome_arquivo)[0]

            if st.session_state.get('calculando', False):
                st.warning("Cálculo em andamento.")
                st.stop()

            st.cache_data.clear()
            if "df_planilha" in st.session_state:
                del st.session_state.df_planilha
            if "df_results" in st.session_state:
                del st.session_state.df_results
            gc.collect() 

            st.session_state.calculando = True
            
            try:
                with st.spinner("Calculando..."):
                    arquivo_tratado = tratar_datas(arquivo_up)

                    dados_planilha = arquivo_tratado.getvalue()
                    df = calcular_planilha(dados_planilha, apo_especial_m)
                    
                    # Atribuí os novos resultados
                    st.session_state.df_planilha = df[0]
                    st.session_state.df_results = df[1]
                    df_pview = df[2]
                    ids_processados = df[3]
                    
                    del arquivo_tratado, dados_planilha 
                    
            except Exception as e:
                st.error(f"Erro no processamento: {str(e)}")
                st.stop()
            finally:
                st.session_state.calculando = False
                gc.collect() 

        if clear:
            st.cache_data.clear()
            
            chaves_para_limpar = ['df_planilha', 'df_results', 'carreira']
            for chave in chaves_para_limpar:
                if chave in st.session_state:
                    del st.session_state[chave]
            
            st.session_state.file_reset += 1 
            
            gc.collect()
            
            st.rerun()

        if st.session_state.df_planilha is not None and not st.session_state.df_planilha.empty:
            renderizar_planilha(st.session_state.df_planilha)

        if st.session_state.df_results is not None and not st.session_state.df_results.empty:
            st.markdown("<h2 class='center'>Resultado(s) da Simulação</h2>", unsafe_allow_html=True)
            st.dataframe(st.session_state.df_results.style.map(destacar_obs, subset=["Observação"]), hide_index=True)

            if len(ids_processados) == 1:
                st.markdown("<h3 class='center'>Pontuações Mensais</h3>", unsafe_allow_html=True)
                st.dataframe(df_pview.head(240), hide_index=True)

            excel_buffer = io.BytesIO()
            st.session_state.df_results.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)

            c1, c2, c3 = st.columns([2, 2, 1])
            with c2:
                st.download_button(
                    label="Exportar Resultados para Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"Resultado(s) {nome_base}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )



### RESULTADOS ###
    elif tabs == '**Resultados**':

        st.markdown("<h1 class='center'>Resultados da Simulação</h1>", unsafe_allow_html=True)
        
        cl00, cl11, cl12 = st.columns([3, 1, 3])
        with cl11:
            st.radio("**Aposentadoria Especial**", ['Não', 'Sim'], key="apo_especial", help="Marque esta opção SOMENTE se o servidor possuir direito à aposentadoria especial.", horizontal=True)
            apo_especial = st.session_state.apo_especial == "Sim"

        st.markdown(
            """
            <div class="alert-warning">
            <strong>⚠️ CASO ADICIONE OU ALTERE NOVOS DADOS AO CÁLCULO ATUAL LEMBRE SEMPRE DE CLICAR EM RECALCULAR. </strong>
            </div>
            """, 
            unsafe_allow_html=True
        )

        col0, col1, col2, col3 = st.columns([3, 2, 3, 1])
        with col1:
            if st.button("🔁 Calcular|Recalcular", type="primary"):
                zerar_carreira(st.session_state.carreira)
                st.session_state.calculo_executado = False
        with col2:
            st.button("🔄 Novo Cálculo", type="tertiary", on_click=novo_calculo)

        if not st.session_state.calculo_executado:
            if st.session_state.calculando:
                st.warning("Cálculo em andamento.")
                st.stop()

            st.session_state.calculando = True

            try:
                carreira_calculada, resultados_carreira = calcular_evolucao(
                    st.session_state.enquadramento,
                    st.session_state.data_inicial,
                    st.session_state.nivel_atual, 
                    st.session_state.carreira, 
                    st.session_state.pts_ultima_evolucao, 
                    st.session_state.afastamentos, 
                    st.session_state.titulacoes,
                    st.session_state.resp_unicas,
                    st.session_state.resp_mensais,
                    apo_especial
                )
                
                if carreira_calculada and resultados_carreira:
                    st.session_state.carreira = carreira_calculada
                    st.session_state.resultados_carreira = resultados_carreira
                    st.session_state.calculo_executado = True
                else:
                    st.markdown(
                        """
                        <div class="alert-warning">
                        <strong>⚠️ Dados insuficientes para iniciar cálculo. 🔄 Necessário requisitos obrigatórios. </strong>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

            except Exception as e:
                st.error(f"❌ Erro no cálculo: {str(e)}")
            finally:
                st.session_state.calculando = False

        if st.session_state.calculo_executado and st.session_state.carreira:
            df_view = pd.DataFrame(st.session_state.resultados_carreira)
            df_view["Interstício de Evolução"] = df_view["Interstício de Evolução"].apply(
                lambda x: f"{x:>5}" if isinstance(x, int) or (isinstance(x, str) and x.isdigit()) else x
            )
            
            st.markdown("<h2 class='center'>Resultado</h2>", unsafe_allow_html=True)
            st.dataframe(df_view.head(1).style.map(destacar_obs, subset=["Observação"]), hide_index=True)
        
            df_preview = pd.DataFrame(
                st.session_state.carreira,
                columns=['Data', 'Efetivo Exercício', 'Desempenho', 'Titulação Acadêmica', 'R.Únicas', 'R.Mensais', 'Soma Total']
            )

            df_preview["Data"] = df_preview["Data"].apply(lambda d: d.strftime("%d/%m/%Y"))
            
            st.markdown("<h3 class='center'>Pontuações Mensais</h3>", unsafe_allow_html=True)
            st.dataframe(df_preview.head(241), hide_index=True)
        
        c1, c2, c3, c4 = st.columns([1.2, 1.5, 1.5, 0.8])
        if 'df_preview' in locals() and not df_preview.empty:
            with c2: 
                st.button("Adicionar Novos Dados ao Cálculo Atual", type='primary', on_click=go_individual)
            with c3:
                excel_buffer = io.BytesIO()
                df_view.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                st.download_button(
                    label="Exportar Resultado para Excel",
                    data=excel_buffer.getvalue(),
                    file_name="Resultado Evoluções.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )


if __name__ == "__main__":
    main()
