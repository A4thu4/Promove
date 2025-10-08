import pandas as pd
import streamlit as st
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from layout import ensure_states, build_obrigatorios, build_afastamentos, build_aperfeicoamentos, build_titulacoes, build_responsabilidades_unicas, build_responsabilidades_mensais
ensure_states()
from data_utils import DATA_CONCLUSAO

st.set_page_config(page_title="SIMULADOR GGDP", layout="wide")

st.markdown(
    """
    <style>
        :root {
            --primary-color: #1bb50b !important;  /* Verde */
            --background-color: #ffffff !important;  /* Branco */
            --secondary-background-color: #FFFFFF !important;  /* Branco */
            --text-color: #000000 !important;  /* Preto */
        }
        img {
            margin-top: -3rem !important;
            margin-bottom: -1.2rem !important;
            align: center !important;
        }
        h1 {
            font-size: 2.50rem !important;
            margin-bottom: 1rem !important;
            margin-left: 1.6rem !important;
        }
        h2 {
            font-size: 1.90rem !important;
            margin-bottom: 1rem !important;
            margin-left: 1.6rem !important;
        }

        /* Fundo de Tela */
        .stApp, .stSidebar, .stAlert, .stMarkdown {
            background-color: #fbfbf7 !important;
        }

        /* Estilo para DataFrames */
        .stDataFrame {
            border-radius: 8px !important;
            border: 1px solid #e0e0e0 !important;
            overflow: hidden !important;
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


#BOTÕES
st.markdown(
    """
    <style>
        /* Estilo para botões */
        .stButton > button {
            border-radius: 8px !important;
            border: 1px solid #e0e0e0 !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
            color: #ff666f !important;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #f1f5f1, #Ff1f5f1FF) !important;
            color: #ff666f !important;
            border: 2px solid #ff666f !important;
            box-shadow: 0 2px 8px rgba(27,181,11,0.15) !important;
            transform: translateY(-2px) scale(1.03) !important;
            transition: all 0.2s !important;
        }

        /* Estilo para botões primários e de Download*/
        .stButton > button[kind="primary"],
        .stForm > div > div > button[kind="primary"],
        .stDownloadButton > button,
        .stFormSubmitButton > button { 
            background: linear-gradient(135deg, #fbfbf7, #fbfbf7) !important;
            border-radius: 10px !important;
            color: green !important;  /* Corrige a cor do texto para verde */
        }

        .stButton > button[kind="primary"]:hover,
        .stForm > div > div > button[kind="primary"]:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover { 
            background: linear-gradient(135deg, #fbfbf7, #fbfbf7) !important;
            color: #1bb50b !important; /* texto verde */
            border: 2px solid #1bb50b !important; /* borda verde */
            box-shadow: 0 2px 8px rgba(27,181,11,0.15) !important; /* sombra suave */
            transform: translateY(-2px) scale(1.03) !important; /* leve efeito de elevação */
            transition: all 0.2s !important;
        }

        /* ESTILO ESPECÍFICO PARA FORM SUBMIT BUTTON */
        .stFormSubmitButton > button {
            border-radius: 8px !important;
            border: 1px solid #e0e0e0 !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
            color: green !important;  /* VERDE em vez de vermelho */
            background: linear-gradient(135deg, #fbfbf7, #fbfbf7) !important;
        }

        .stFormSubmitButton > button:hover {
            background: linear-gradient(135deg, #fbfbf7, #fbfbf7) !important;
            color: #1bb50b !important;  /* VERDE no hover */
            border: 2px solid #1bb50b !important;  /* BORDA VERDE */
            box-shadow: 0 2px 8px rgba(27,181,11,0.15) !important;
            transform: translateY(-2px) scale(1.03) !important;
            transition: all 0.2s !important;
        }
    </style>
    """, unsafe_allow_html=True
) 


def main():
    # ---------- NAVEGAÇÃO ---------- #
    with st.sidebar:
        tabs = st.radio("Navegar",
            ['**Cálculo Individual**', '**Cálculo Múltiplo**', '**Resultados**'],
            index=0,
            key="navigation"
            )

    if tabs == '**Cálculo Individual**':
        st.markdown("<h1 style='text-align:center; color:#003500; '><u>Critérios Obrigatórios</u></h1>", unsafe_allow_html=True)

        build_obrigatorios()
        
        if st.session_state.data_inicial and not st.session_state.carreira:
            st.session_state.data_fim = st.session_state.data_inicial + relativedelta(years=20)
            DATA_FIM = st.session_state.data_fim

            # Inicializa a carreira no session state
            st.session_state.carreira = [
                [st.session_state.data_inicial + timedelta(days=i)] + [0] * 7
                for i in range(DATA_CONCLUSAO)
            ]

            st.success(f"✅ Carreira inicializada com {len(st.session_state.carreira)} dias!")
            st.rerun()  # Força atualização

        build_afastamentos()
        build_aperfeicoamentos()
        build_titulacoes()
        build_responsabilidades_unicas()
        build_responsabilidades_mensais()

    if tabs == '**Cálculo Múltiplo**':
        from logic import calcular_planilha

        if "file_reset" not in st.session_state:
            st.session_state.file_reset = 0
        st.session_state.arquivo = st.file_uploader("Arquivo", type=["xlsx", "xls", "xlsm"], key=f"wb_{st.session_state.file_reset}")
        if st.session_state.arquivo is not None:
            calcular_planilha(st.session_state.arquivo)
            
    if tabs == '**Resultados**':
        from logic import calcular_evolucao

        st.markdown("<h1 style='text-align:center; color:#003500; '><u>Resultados da Simulação</u></h1>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='
                background-color: #fff3cd; 
                border: 1px solid #ffeaa7; 
                border-radius: 0.375rem; 
                padding: 1rem; 
                text-align: center; 
                color: #856404;
                margin: 1rem 0;
            '>
            <strong>⚠️ CASO ADICIONE NOVOS DADOS AO CÁLCULO ATUAL LEMBRE SEMPRE DE RECALCULAR ⚠️</strong>
            </div>
            """, 
            unsafe_allow_html=True
        )

        col0, col1, col2, col3 = st.columns([3, 2, 3, 1])
        with col1:
            if st.button("🔁 Cálcular|Recalcular", type="primary"):
                from logic import zerar_carreira
                zerar_carreira(st.session_state.carreira)
                st.session_state.calculo_executado = False
                st.rerun()
        with col2:
            if st.button("🔄 Novo Cálculo"):
                from layout import clear_states
                clear_states()

        if not st.session_state.calculo_executado:
            try:
                carreira_calculada, resultados_carreira = calcular_evolucao(
                    st.session_state.data_inicial,
                    st.session_state.nivel_atual, 
                    st.session_state.carreira, 
                    st.session_state.pts_ultima_evolucao, 
                    st.session_state.afastamentos, 
                    st.session_state.aperfeicoamentos,
                    st.session_state.titulacoes,
                    st.session_state.resp_unicas,
                    st.session_state.resp_mensais
                    )
                
                if carreira_calculada and resultados_carreira:
                    st.session_state.carreira = carreira_calculada
                    st.session_state.resultados_carreira = resultados_carreira
                    st.session_state.calculo_executado = True
                    st.success("✅ Cálculo concluído!")
                    st.rerun()
                else:
                    st.warning("⚠️ Dados insuficientes para iniciar cálculo. 🔄 Necessário requisitos obrigatórios.")

            except Exception as e:
                st.error(f"❌ Erro no cálculo: {str(e)}")

        if st.session_state.calculo_executado and st.session_state.carreira:
            df_view = pd.DataFrame(st.session_state.resultados_carreira)
            st.markdown("<h3 style='text-align:center; color:#003500; '><u>Resultado da Simulação</u></h3>", unsafe_allow_html=True)
            st.dataframe(df_view.head(1), hide_index=True)

            df_preview = pd.DataFrame(
                st.session_state.carreira,
                columns=['Data', 'Efetivo Exercício', 'Desempenho', 'Aperfeiçoamentos', 'Titulação Acadêmica', 'R.Únicas', 'R.Mensais', 'Soma Total']
            )
            df_preview['Data'] = pd.to_datetime(df_preview['Data'])
            df_preview = df_preview[df_preview['Data'].dt.day == 1]
            df_preview['Data'] = df_preview['Data'].dt.strftime('%d/%m/%Y')
            st.markdown("<h3 style='text-align:center; color:#003500; '><u>Pontuações Mensais</u></h3>", unsafe_allow_html=True)
            st.dataframe(df_preview, hide_index=True)

if __name__ == "__main__":
    main()