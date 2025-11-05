import streamlit as st
import pandas as pd
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from logic import ensure_states
ensure_states()
from layout import build_obrigatorios, build_afastamentos, build_desempenho, build_aperfeicoamentos, build_titulacoes, build_responsabilidades_unicas, build_responsabilidades_mensais
from data_utils import DATA_CONCLUSAO

def novo_calculo():
    from layout import clear_states
    clear_states()
    st.session_state.navigation = '**Cálculo Individual**'

def go_results():
    st.session_state.navigation = '**Resultados**'

def go_individual():
    st.session_state.navigation = '**Cálculo Individual**'    

def bloco_vertical(titulo, tamanho, cor):
    return f"""
    <div style="
        writing-mode: vertical-rl;
        transform: rotate(180deg);
        background-color: {cor};
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        height: {tamanho}px;
        width: 25px;
        display: flex;
        align-items: center;
        justify-content: center;
    ">
        {titulo}
    </div>
    """


st.set_page_config(page_title="PROMOVE - Simulador", page_icon="../assets/Brasão.png", layout="wide")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("../assets/Logomarca_GNCP_transparente.png", width=800)

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
            margin-top: 3rem !important;
            margin-bottom: -1.5rem !important;
            align: center !important;
            height: 100px !important;
        }
        h1 {
            font-size: 2.50rem !important;
            margin-top: -20px !important;
            margin-bottom: 0.2rem !important;
            margin-left: 0.25rem !important;
        }
        h2 {
            font-size: 1.90rem !important;
            margin-bottom: 1rem !important;
            margin-left: 0.5rem !important;
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
            border-radius: 6px !important;
            padding: 0.2px !important;
            margin-top: 5px;
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
            color: #1bb50b !important;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #fbfbf7, #fbfbf7) !important;
            color: #1bb50b !important;
            border: 2px solid #1bb50b !important;
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
            color: green !important;  /* Corrige a cor do texto */
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
        
        /* Estilo para botões secondarios */
        .stButton > button[kind="secondary"],
        .stForm > div > div > button[kind="secondary"] { 
            width: 190px !important;
            background: linear-gradient(135deg, #1bb50b, #1bb50b) !important;
            border-radius: 10px !important;
            color: white !important;  /* Corrige a cor do texto */
            font-weight: 700 !important;
        }

        .stButton > button[kind="secondary"]:hover,
        .stForm > div > div > button[kind="secondary"]:hover,
        .stFormSubmitButton > button:hover { 
            background: linear-gradient(135deg, #1bb50b, #1bb50b) !important;
            color: #fbfbf7 !important; /* texto branco */
            border: 2px solid #fbfbf7 !important; /* borda branca */
            box-shadow: 0 2px 8px rgba(27,181,11,0.15) !important; /* sombra suave */
            transform: translateY(-2px) scale(1.03) !important; /* leve efeito de elevação */
            transition: all 0.2s !important;
        }

        /* Estilo para botões terciarios */
        .stButton > button[kind="tertiary"],
        .stForm > div > div > button[kind="tertiary"] { 
            width: 150px !important;
            background: linear-gradient(135deg, #fbfbf7, #fbfbf7) !important;
            border-radius: 10px !important;
            color: red !important;  /* Corrige a cor do texto */
        }

        .stButton > button[kind="tertiary"]:hover,
        .stForm > div > div > button[kind="tertiary"]:hover,
        .stFormSubmitButton > button:hover { 
            background: linear-gradient(135deg, #fbfbf7, #fbfbf7) !important;
            color: red !important; /* texto branco */
            border: 1.5px solid red !important; /* borda branca */
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
            color: black !important;  /* VERDE em vez de vermelho */
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


# FILE UPLOADER
st.markdown(
    """
    <style>
    /* Oculta o texto padrão "Drag and drop file here" */
    [data-testid="stFileUploaderDropzone"] div div {
        visibility: hidden;
    }
    
    /* Adiciona o novo texto de limite de arquivo */
    [data-testid="stFileUploaderDropzone"] div div::after {
        content: "Arraste e solte o arquivo aqui. \\A Limite de 200MB por arquivo • XLSX, XLS, XLSM";
        color: black;
        font-size: 1em;
        visibility: visible;
        position: relative;
        top: -20px;
        display: block;
        text-align: center;
        white-space: pre-line;  
    }
    /* Oculta o texto "Browse files" mantendo o fundo do botão */
    [data-testid="stFileUploaderDropzone"] button > div:first-child {
        visibility: hidden;
        width: 0;
        line-height: normal;
    }
    
    /* Oculta o texto original do botão "Browse files" */
    [data-testid="stFileUploaderDropzone"] button {
        visibility: hidden;
        line-height: normal;4
    }

    /* Adiciona um novo texto ao botão "Browse files" */
    [data-testid="stFileUploaderDropzone"] button::after {
        content: "Carregar arquivo";
        visibility: visible;
        display: block;
        line-height: normal;
        font-weight: 500px;
        color: black;
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
        st.markdown("<h1 style='text-align:center; color:#000000; '>PROMOVE – Simulador de evoluções funcionais</h1>", unsafe_allow_html=True)
       
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
            <strong>⚠️ IMPORTANTE: o módulo de cálculo individual deste simulador destina-se à utilização por servidores <br>
            do Poder Executivo do Estado de Goiás cujas carreiras estejam vinculadas ao programa PROMOVE. </strong>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
                """
                <style>
                /* Remove margem e padding padrão dos elementos principais */
                .block-container {
                    padding-top: 1rem !important;
                    padding-left: 0.5rem !important;
                    padding-right: 0.5rem !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        
        col1, col2 = st.columns([0.05, 1.93])
        with col1: 
            st.markdown(bloco_vertical("", 1100, "#003500"), unsafe_allow_html=True)
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
                    [data_inicio + timedelta(days=i)] + [0] * 7
                    for i in range(DATA_CONCLUSAO)
                ]

                st.success(f"✅ Carreira inicializada com {len(st.session_state.carreira)} dias!")
                st.rerun()  # Força atualização

            build_afastamentos()
            build_desempenho()
            build_aperfeicoamentos()
            st.divider()
        
        col1, col2 = st.columns([0.05, 1.93])
        with col1: 
            st.markdown(bloco_vertical("", 1980, "#fede01"), unsafe_allow_html=True)
        with col2:
            build_titulacoes()
            build_responsabilidades_mensais()
            build_responsabilidades_unicas()

        st.write("")
        st.write("")
        c1, c2, c3 = st.columns([2.2, 2, 1])
        with c2: st.button("Calcular Resultados", type='secondary', on_click=go_results)

    if tabs == '**Cálculo Múltiplo**':
        from logic import calcular_planilha
        st.markdown("<h1 style='text-align:center; color:#000000; '>PROMOVE – Simulador de evoluções funcionais</h1>", unsafe_allow_html=True)
       
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
            <strong>⚠️ IMPORTANTE: o módulo de cálculo múltiplo deste simulador destina-se à utilização por servidores lotados nas unidades setoriais e centrais de gestão e desenvolvimento de pessoas <br>
            ou em unidades a elas equivalentes, como ferramenta de apoio à gestão das carreiras do Poder Executivo do Estado de Goiás vinculadas ao programa PROMOVE. </strong>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
                """
                <style>
                /* Remove margem e padding padrão dos elementos principais */
                .block-container {
                    padding-top: 1rem !important;
                    padding-left: 0.5rem !important;
                    padding-right: 0.5rem !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
        
        if "file_reset" not in st.session_state:
            st.session_state.file_reset = 0
        
        st.markdown(
            """
            <div style='
                background-color: #cde9fe; 
                border: 1px solid #c4f7ff; 
                border-radius: 0.375rem; 
                padding: 0.5rem; 
                text-align: center; 
                color: #004a88;
                margin: 1rem 0;
                margin-top: -3px;
            '>
            <strong> Após o preenchimento da planilha do Excel fornecida pelo Órgão Central de Gestão de Pessoal,<br> segure e arraste o arquivo para a área abaixo 
            ou clique em “Carregar Arquivo” e o selecione na pasta do seu computador. </strong>
            </div>
            """, 
            unsafe_allow_html=True
        )

        st.session_state.arquivo = st.file_uploader("Selecione o arquivo", type=["xlsx", "xls", "xlsm"], key=f"wb_{st.session_state.file_reset}", label_visibility="hidden")
        
        if st.session_state.arquivo is not None:
            # try:
            calcular_planilha(st.session_state.arquivo)
            # except Exception as e:
            #     st.error(f"❌ Erro no cálculo: Verifque se todos os dados na planilha estão corretos. {e}")

    if tabs == '**Resultados**':
        from logic import calcular_evolucao

        st.markdown("<h1 style='text-align:center; color:#000000; '>Resultados da Simulação</h1>", unsafe_allow_html=True)
        
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
            <strong>⚠️ CASO ADICIONE OU ALTERE NOVOS DADOS AO CÁLCULO ATUAL LEMBRE SEMPRE DE CLICAR EM RECALCULAR. </strong>
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
            if st.button("🔄 Novo Cálculo", type="tertiary", on_click=novo_calculo):
                st.rerun()

        if not st.session_state.calculo_executado:
            # try:
                afast_total = []
                afast_total.extend(st.session_state.get("afastamentos_inicial", []))
                afast_total.extend(st.session_state.get("afastamentos", []))

                carreira_calculada, resultados_carreira, projecao_carreira = calcular_evolucao(
                    st.session_state.data_inicial,
                    st.session_state.nivel_atual, 
                    st.session_state.carreira, 
                    st.session_state.pts_ultima_evolucao, 
                    afast_total, 
                    st.session_state.aperfeicoamentos,
                    st.session_state.titulacoes,
                    st.session_state.resp_unicas,
                    st.session_state.resp_mensais
                )
                
                if carreira_calculada and resultados_carreira:
                    st.session_state.carreira = carreira_calculada
                    st.session_state.resultados_carreira = resultados_carreira
                    st.session_state.projecao_carreira = projecao_carreira
                    st.session_state.calculo_executado = True
                    st.success("✅ Cálculo concluído!")
                    st.rerun()
                else:
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
                        <strong>⚠️ Dados insuficientes para iniciar cálculo. 🔄 Necessário requisitos obrigatórios. </strong>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

            # except Exception as e:
            #     st.error(f"❌ Erro no cálculo: {str(e)}")

        if st.session_state.calculo_executado and st.session_state.carreira:
            df_view = pd.DataFrame(st.session_state.resultados_carreira)
            st.markdown("<h2 style='text-align:center; color:#000000; '>Resultado</h2>", unsafe_allow_html=True)
            st.dataframe(df_view.head(1), hide_index=True)
        
            df_preview = pd.DataFrame(
                st.session_state.carreira,
                columns=['Data', 'Efetivo Exercício', 'Desempenho', 'Aperfeiçoamentos', 'Titulação Acadêmica', 'R.Únicas', 'R.Mensais', 'Soma Total']
            )
            df_preview['Data'] = pd.to_datetime(df_preview['Data'])
            df_preview = df_preview[df_preview['Data'].dt.day == 1]
            df_preview['Data'] = df_preview['Data'].dt.strftime('%d/%m/%Y')
            st.markdown("<h3 style='text-align:center; color:#000000; '>Pontuações Mensais</h3>", unsafe_allow_html=True)
            st.dataframe(df_preview.head(241), hide_index=True)

            if st.session_state.projecao_carreira:
                df_view2 = pd.DataFrame(st.session_state.projecao_carreira)
                st.markdown("<h2 style='text-align:center; color:#000000; '>Projeção de Carreira</h2>", unsafe_allow_html=True)
                st.dataframe(df_view2, hide_index=True)
        
        c1, c2, c3, c4 = st.columns([1.2, 1.5, 1.5, 0.8])
        if 'df_preview' in locals() and not df_preview.empty:
            with c2: 
                st.button("Adicionar Novos Dados ao Cálculo Atual", type='primary', on_click=go_individual)
            with c3:
                import io 
                excel_buffer = io.BytesIO()
                df_preview.to_excel(excel_buffer, index=False, engine='openpyxl')
                excel_buffer.seek(0)
                st.download_button(
                    label="Exportar Resultado para Excel",
                    data=excel_buffer.getvalue(),
                    file_name="Resultado Evoluções.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()
