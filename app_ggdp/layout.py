import streamlit as st
from data_utils import  MIN_DATE, MAX_DATE, NIVEIS
from logic import ensure_states, clear_states
from dateutil.relativedelta import relativedelta


def build_obrigatorios(key_prefix="obg"):
    """
    Renderiza inputs para 'Requisitos Obrigatórios' e atualiza st.session_state.obrigatorios.
    """
    ensure_states()
    st.markdown("<h1 style='text-align:left; color:#000000; '>Requisitos Obrigatórios</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:left; color:#000000; '>Dados do Servidor</h2>", unsafe_allow_html=True)

    existing_data = st.session_state.obrigatorios[0] if st.session_state.obrigatorios else (None, None, None)
    existing_nivel, existing_data_inicial, existing_pts = existing_data

    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        st.session_state[f"{key_prefix}_nvl_atual"] = existing_nivel if existing_nivel else None
        st.session_state[f"{key_prefix}_data_inicial"] = None
        st.session_state[f"{key_prefix}_pts_rem"] = None
        st.session_state[f"{key_prefix}_reset_fields"] = False

    # Usar st.form para evitar re-execução a cada input
    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
        col0, col1, col2 = st.columns([2, 2, 2])
        with col0:
            nivel_atual = st.text_input(
                "Nivel Atual",
                max_chars=1,
                value=existing_nivel if existing_nivel else None,
                key=f"{key_prefix}_nvl_atual",
                help="Informe a letra do nível em que o servidor se encontra atualmente na carreira, com valores entre A e S."
            )
            if nivel_atual:
                nivel_atual = nivel_atual.upper()
        with col1:
            st.session_state.data_inicial = st.date_input(
                "Data do Enquadramento ou Última Evolução",
                format="DD/MM/YYYY",
                value=existing_data_inicial if existing_data_inicial else None,
                min_value=MIN_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_inicial"
            )   
        with col2:
            pts_remanescentes = st.number_input(
                "Pontos Excedentes da Última Evolução",
                value=existing_pts if existing_pts else None,
                min_value=0.0,
                format="%.3f",
                key=f"{key_prefix}_pts_rem",
                help="Caso não haja pontuação remanescente, preencha com o número 0 (zero)."
            )     
        with col1:
            c0, c1 =st.columns([2,2])
            with c0: submitted = st.form_submit_button("Enviar", use_container_width=True, type='primary')
            with c1: remove = st.form_submit_button("Remover", use_container_width=True)

    faltas = 0
    if st.session_state.data_inicial:
        # Remove qualquer registro anterior automático de faltas
        st.session_state.afastamentos_inicial = [
            (mes, faltas)
            for mes, faltas in st.session_state.afastamentos_inicial
            if mes != st.session_state.get("data_inicial_anterior")
        ]

        data = st.session_state.data_inicial
        faltas = data.day - 1  # dias antes do início
        if faltas > 0:
            st.session_state.afastamentos_inicial.append((data, int(faltas)))
        else:
            st.session_state.afastamentos_inicial.append((data, 0))

        # Atualiza o controle da última data usada
        st.session_state.data_inicial_anterior = data

    if submitted:
        if not nivel_atual:
            st.error("O campo 'Nivel Atual' é obrigatório. Preencha com valores entre A e S.")
        elif nivel_atual not in NIVEIS:
            st.error(f"O nível '{nivel_atual}' não é válido. Níveis permitidos: {NIVEIS}.")
        if not st.session_state.data_inicial:
            st.error("O campo 'Data inicial' é obrigatório. Preencha com a data da última evolução ou do último enquadramento.")
        if pts_remanescentes == None:
            st.error("O campo 'Pontos Remanescentes da Última Evolução' é obrigatório. Caso não haja pontuação remanescente, preencha com o número 0 (zero).")
        if st.session_state.data_inicial and nivel_atual in NIVEIS and pts_remanescentes != None:
            st.session_state.pts_ultima_evolucao = float(pts_remanescentes)
            st.session_state.nivel_atual = nivel_atual if nivel_atual else 'A'
            st.session_state.obrigatorios = [(nivel_atual, st.session_state.data_inicial, float(pts_remanescentes))]
            st.session_state.carreira = []
            st.rerun()

    # Mostrar pontos cadastrados 
    if st.session_state.obrigatorios:
        cols = st.columns(2)
        for i, (nivel, data, pts) in enumerate(st.session_state.obrigatorios):
            col = cols[i % 4]
            with col:
                st.write(f"Nivel Atual: {nivel}.")
                st.write(f"Data de Início: {data.strftime('%d/%m/%Y')}.")
                st.write(f"Pontuação Inicial: {pts}")
                if remove:
                    st.session_state.obrigatorios.pop(i)
                    st.session_state[f"{key_prefix}_reset_fields"] = True
                    st.rerun()


def build_afastamentos(key_prefix="afast"):
    """
    Renderiza inputs para 'Afastamentos' e atualiza st.session_state.afastamentos.
    """
    ensure_states()
    st.markdown("<h2 style='text-align:left; color:#000000; '>Afastamentos Não Considerados Como Efetivo Exercício</h2>", unsafe_allow_html=True)

    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        st.session_state[f"{key_prefix}_mes"] = None
        st.session_state[f"{key_prefix}_qntd"] = 0
        st.session_state[f"{key_prefix}_reset_fields"] = False

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
        col0, col1 = st.columns([1, 1])
        with col0:
            mes_faltas = st.date_input(
                "Mês do Afastamento",
                format="DD/MM/YYYY",
                value=None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_mes",
                help="Preencha a data completa, no formato DD/MM/AAAA (exemplo: 01/01/2025). Será considerado apenas o mês e o ano no cálculo."
            )
            c, c11 = st.columns([2,1])
            with c11: submitted = st.form_submit_button("➕", use_container_width=True, type='primary')
        with col1:
            qntd_faltas = st.number_input(
                "Quantitativo Total de Afastamentos no Mês",
                min_value=0,
                step=1,
                key=f"{key_prefix}_qntd"
            )
            c00, _, c = st.columns([1, 1 ,1])
            with c00: remove = st.form_submit_button("➖",use_container_width=True)
            with c: cleared = st.form_submit_button("🗑️",use_container_width=True)

    if submitted:
        if not st.session_state.data_inicial: 
            st.error("Adicione a Data de Enquadramento/Última Evolução.")
        if not mes_faltas:
            st.error("Preencha o campo 'Mês do Afastamento' com a data completa no formato DD/MM/AAAA. O cálculo levará em conta apenas o mês e o ano, independemente do dia preenchido. ")
        if not qntd_faltas or qntd_faltas == 0:
            st.error("Preencha o campo 'Quantitativo Total de Afastamentos no Mês' com um valor númerico acima de 0 (zero).")
        if st.session_state.data_inicial != None and mes_faltas:
            if mes_faltas < st.session_state.data_inicial:
                st.error("O mês do afastamento não pode ser anterior à data do enquadramento ou da última evolução.")
            if any((mes.month, mes.year) == (mes_faltas.month, mes_faltas.year) for mes, _ in st.session_state.afastamentos):
                st.warning("Mês e ano já registrados.")
            if mes_faltas >= st.session_state.data_inicial and qntd_faltas > 0 and not any((mes.month, mes.year) == (mes_faltas.month, mes_faltas.year) for mes, _ in st.session_state.afastamentos):
                st.session_state.afastamentos.append((mes_faltas, int(qntd_faltas)))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

    if cleared:
        st.session_state.afastamentos.clear()
        st.session_state[f"{key_prefix}_reset_fields"] = True
        ensure_states()
        st.rerun()

    if st.session_state.afastamentos:
        total_afast = sum(f for _, f in st.session_state.afastamentos)

        cl = st.columns(2)
        
        with cl[0]: st.write("**-Afastamentos Registrados-**")
        with cl[1]: st.write(f"**Total de Afastamentos: {total_afast}**")
        
        cols = st.columns(6)
        print("")

        for i, (mes, faltas) in enumerate(sorted(st.session_state.afastamentos, key=lambda data: data[0])):
            col = cols[i % 6]
            with col:
                st.write(f"Data: {mes.strftime('%m/%Y')}.") 
                st.write(f"{faltas} falta(s).")
                if remove and st.session_state.afastamentos:
                    st.session_state.afastamentos.pop()
                    st.session_state[f"{key_prefix}_reset_fields"] = True
                    st.rerun()


def build_desempenho(key_prefix="des"):
    """
    Renderiza inputs para 'Desempenhos' e atualiza st.session_state.afastamentos.
    """
    ensure_states()
    st.markdown("<h2 style='text-align:left; color:#000000; '>Desempenho no Exercício das Atribuições</h2>", unsafe_allow_html=True)

    st.markdown("""
        <style>
        /* Campos desabilitados com melhor visibilidade */
        input[disabled] {
            color: #000000 !important;
            opacity: 1 !important;
            cursor: default !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            padding: 8px 12px !important;
        }
        input[disabled]:focus {
            outline: none !important;
            box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Label em negrito para melhor visibilidade */
        .stTextInput label {
            font-weight: 600 !important;
            color: #000000 !important;
        }
        
        /* Garantir que o texto fique realmente preto */
        .stTextInput input[disabled] {
            -webkit-text-fill-color: #000000 !important;
        }
        </style>
        """, unsafe_allow_html=True)

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False, enter_to_submit=False):
        col0, col1, col2 = st.columns([1, 1, 1])
        with col0:
            st.text_input(
                "Pontuação Mensal",
                value="1.5",
                key=f"{key_prefix}_pts_mes",
                disabled=True,
                help="Valor referencial padrão para pontuação mensal"
            )
        with col1:
            st.text_input(
                "Pontuação Semestral",
                value="9",
                key=f"{key_prefix}_pts_semestre",
                disabled=True,
                help="Valor referencial padrão para pontuação semestral"
            )
        with col2:
            st.text_input(
                "Pontuação Final por Ciclo de Evolução",
                value="36",
                key=f"{key_prefix}_pts_final",
                disabled=True,
                help="Valor referencial padrão para pontuação final"
            )
        
        st.form_submit_button(
            "Obs.: a pontuação referente ao desempenho no exercício das atribuições será calculada nesta simulação com os valores referenciais padrões. Os campos deste bloco não deverão ser preenchidos", 
            use_container_width=True, 
            disabled=True
        )


def build_aperfeicoamentos(key_prefix="aperf"):
    """
    Renderiza inputs para 'Aperfeiçoamentos' (data de conclusão + horas) e atualiza st.session_state.aperfeicoamentos.
    Aproveitamento das horas (limite 100h, pontos = horas * 0.09) fica em logic.
    """
    ensure_states()
    st.markdown("<h2 style='text-align:left; color:#000000'>Aperfeiçoamentos</h2>", unsafe_allow_html=True)

    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        st.session_state[f"{key_prefix}_data"] = None
        st.session_state[f"{key_prefix}_hrs"] = 0
        st.session_state[f"{key_prefix}_reset_fields"] = False

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            data_conclusao = st.date_input(
                "Data de Conclusão",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data"
            )
            c, c12 = st.columns([2,1])
            with c12: submitted = st.form_submit_button("➕", use_container_width=True, type='primary')
        with col2:
            horas_curso = st.number_input(
                "Carga Horária por Atividade de Capacitação",
                min_value=0,
                step=1,
                key=f"{key_prefix}_hrs"
            )
            c02, _,  c = st.columns([1, 1, 1])
            with c02: remove = st.form_submit_button("➖",use_container_width=True)
            with c: cleared = st.form_submit_button("🗑️",use_container_width=True)
    
    if submitted:
        if not st.session_state.data_inicial: 
            st.error("Adicione a Data de Enquadramento/Última Evolução")
        if not data_conclusao:
            st.error("Preencha o campo 'Data de Conclusão' com a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
        if not horas_curso or horas_curso < 4:
            st.error("O número mínimo de horas aceita por atividade de aperfeiçoamento é 4.")
        if st.session_state.data_inicial != None and data_conclusao:
            if data_conclusao < st.session_state.data_inicial:
                st.error("Data não pode ser anterior a data de Enquadramento/Última Evolução.")
            if data_conclusao >= st.session_state.data_inicial and horas_curso >= 4:
                st.session_state.aperfeicoamentos.append((data_conclusao, int(horas_curso)))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

    if cleared:
        st.session_state.aperfeicoamentos.clear()
        st.session_state[f"{key_prefix}_reset_fields"] = True
        st.rerun()

    if st.session_state.aperfeicoamentos:
        total_hrs = sum(f for _, f in st.session_state.aperfeicoamentos)

        cl = st.columns(2)
        
        with cl[0]: st.write("**-Aperfeiçoamentos Registrados-**")
        with cl[1]: st.write(f"**Total de Horas: {total_hrs}**")
        if total_hrs > 100:
            total_hrs = 100
            st.warning("O limite máximo de horas válidas de atividades de aperfeiçoamento (100 horas) no ciclo de evolução foi atingido. As horas excedentes não serão computadas.")
        
        cols = st.columns(6)
        for i, (data, hrs) in enumerate(sorted(st.session_state.aperfeicoamentos, key=lambda data: data[0])):
            col = cols[i % 6]
            with col:
                st.write(f"Data: {data.strftime('%d/%m/%Y')}." )
                st.write(f"Carga Horária: {hrs}h.")
                if remove:
                    st.session_state.aperfeicoamentos.pop()
                    st.session_state[f"{key_prefix}_reset_fields"] = True
                    st.rerun()
    

def build_titulacoes(key_prefix="tit"):
    """
    Renderiza inputs para 'Titulações' (data de conclusão + tipo da titulação) e atualiza st.session_state.titulacoes.
    """
    ensure_states()
    st.markdown("<h1 style='text-align:left; color:#000000; '>Requisitos Aceleradores</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:left; color:#000000; '>Titulações</h2>", unsafe_allow_html=True)

    from data_utils import dados_tit

    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        st.session_state[f"{key_prefix}_data"] = None
        st.session_state[f"{key_prefix}_tipo"] = "Nenhuma"
        st.session_state[f"{key_prefix}_reset_fields"] = False

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            data_conclusao = st.date_input(
                "Data de Conclusão",
                format="DD/MM/YYYY",
                value=None,
                min_value=MIN_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data"
            )
            c, c13 =st.columns([2,1])
            with c13: submitted = st.form_submit_button("➕", use_container_width=True, type='primary')
        with col2:
            tipo_tit = st.selectbox(
                "Tipo de Titlução",
                list(dados_tit.keys()),
                key=f"{key_prefix}_tipo"
            )
            c03, _, c = st.columns([1, 1, 1])
            with c03: remove = st.form_submit_button("➖",use_container_width=True)
            with c: cleared = st.form_submit_button("🗑️",use_container_width=True)

    ultima_titulacao = None
    if st.session_state.titulacoes:
        # Pega a última titulação cadastrada (a mais recente)
        ultima_titulacao = max(data for data, _ in st.session_state.titulacoes)

    if submitted:
        if not st.session_state.data_inicial: 
            st.error("Adicione a Data de Enquadramento/Última Evolução")
        if not data_conclusao:
            st.error("O campo “Data de Conclusão” é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
        if tipo_tit == 'Nenhuma':
            st.error("Selecione um tipo de titulação válido.")
        if ultima_titulacao and data_conclusao < (ultima_titulacao + relativedelta(months=12)):
            st.warning("Limite de titulações excedido no período (art. 44, § 10.: poderá ser validada uma titulação acadêmica por ano civil, com interstício mínimo de 12 (doze) meses entre uma e outra validação).") 
        if st.session_state.data_inicial != None and (ultima_titulacao is None or data_conclusao > (ultima_titulacao + relativedelta(months=12) - relativedelta(days=1))):
            if data_conclusao < st.session_state.data_inicial:
                st.error("Data não pode ser anterior a data de Enquadramento/Última Evolução.")
            if data_conclusao >= st.session_state.data_inicial and tipo_tit != 'Nenhuma':
                st.session_state.titulacoes.append((data_conclusao, tipo_tit))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

    if cleared:
        st.session_state.titulacoes.clear()
        st.session_state[f"{key_prefix}_reset_fields"] = True
        st.rerun()

    if st.session_state.titulacoes:
        total_tit = len(st.session_state.titulacoes)

        cl = st.columns(2)
        
        with cl[0]: st.write("**-Titulações Registradas-**")
        with cl[1]: st.write(f"**Total de Titulações: {total_tit}**")
        
        cols = st.columns(4)
        for i, (data, tipo) in enumerate(sorted(st.session_state.titulacoes, key=lambda data: data[0])):
            col = cols[i % 4]
            with col:
                st.write(f"Data: {data.strftime('%d/%m/%Y')}." )
                st.write(f"Titulação: {tipo}.")
                if remove:
                    st.session_state.titulacoes.pop()
                    st.session_state[f"{key_prefix}_reset_fields"] = True
                    st.rerun()


def build_responsabilidades_unicas(key_prefix="resp_unic"):
    """
    Renderiza inputs para 'Responsabilidades' e atualiza st.session_state.{referente_a_responsabilidade}.
    """
    ensure_states()
    st.markdown("<h2 style='text-align:left; color:#000000'>Responsabilidades Únicas</h2>", unsafe_allow_html=True)

    from data_utils import dados_artigo, dados_livro, dados_pesquisas, dados_registros, dados_cursos

    suffixes  = ["art", "liv", "pesq", "reg", "curso"]
    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        for key_suffix in suffixes:
            st.session_state[f"{key_prefix}_data_{key_suffix}"] = None
            st.session_state[f"{key_prefix}_qntd_{key_suffix}"] = 0
            st.session_state[f"{key_prefix}_tipo_{key_suffix}"] = "Nenhum"
        st.session_state[f"{key_prefix}_reset_fields"] = False

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
# ---------- ARTIGOS ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Publicação de Artigos ou Pesquisas Científicas com ISSN</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3 = st.columns([2, 2, 2, 1])
        with col0:
            data_publi_art = st.date_input(
                "Data de Conclusão",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_art"
            )
        with col1:
            qntd_art = st.number_input(
                "Quantidade",
                min_value=0,
                key=f"{key_prefix}_qntd_art"
            )
        with col2:
            tipo_art = st.selectbox(
                "Tipo de Artigo",
                list(dados_artigo.keys()),
                key=f"{key_prefix}_tipo_art"
            )
        with col3:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted1 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add1", type='primary')
            with c1: remove1 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r1")

        if submitted1:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_publi_art:
                st.error("O campo 'Data de Conclusão' é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
            if not qntd_art: 
                st.error("O campo 'Quantidade' é obrigatório. Preencha com um valor numérico igual ou superior a 1 (um).")
            if tipo_art == 'Nenhum':
                st.error("Selecione um tipo de responsabilidade única válido.")
            if data_publi_art and qntd_art and tipo_art != 'Nenhum':
                st.session_state.artigos_lista.append((data_publi_art, qntd_art, tipo_art))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.artigos_lista:
            if remove1:
                st.session_state.artigos_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- LIVROS ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Publicações de Livros com Corpo Editorial e ISBN</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3 = st.columns([2, 2, 2, 1])
        with col0:
            data_publi_liv = st.date_input(
                "Data de Conclusão",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_liv"
            )
        with col1:
            qntd_liv = st.number_input(
                "Quantidade",
                min_value=0,
                key=f"{key_prefix}_qntd_liv"
            )
        with col2:
            tipo_liv = st.selectbox(
                "Tipo de Livro",
                list(dados_livro.keys()),
                key=f"{key_prefix}_tipo_liv"
            )
        with col3:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted2 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add2", type='primary')
            with c1: remove2 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r2")

        if submitted2:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_publi_liv:
                st.error("O campo 'Data de Conclusão' é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
            if not qntd_liv: 
                st.error("O campo 'Quantidade' é obrigatório. Preencha com um valor numérico igual ou superior a 1 (um).")
            if tipo_liv == 'Nenhum':
                st.error("Selecione um tipo de responsabilidade única válido.")
            if data_publi_liv and qntd_liv and tipo_liv != 'Nenhum':
                st.session_state.livros_lista.append((data_publi_liv, qntd_liv, tipo_liv))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()
        
        if st.session_state.livros_lista:
            if remove2:
                st.session_state.livros_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- PESQUISAS CIENTIFICAS ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Publicações de Artigos ou Pesquisas Científicas Aprovadas em Eventos Científicos</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3 = st.columns([2, 2, 2, 1])
        with col0:
            data_publi_pesq = st.date_input(
                "Data de Conclusão",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_pesq"
            )
        with col1:
            qntd_pesq = st.number_input(
                "Quantidade",
                min_value=0,
                key=f"{key_prefix}_qntd_pesq"
            )
        with col2:
            tipo_pesq = st.selectbox(
                "Tipo de Pesquisa Aprovada",
                list(dados_pesquisas.keys()),
                key=f"{key_prefix}_tipo_pesq"
            )
        with col3:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted3 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add3", type='primary')
            with c1: remove3 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r3")

        if submitted3:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_publi_pesq:
                st.error("O campo 'Data de Conclusão' é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
            if not qntd_pesq: 
                st.error("O campo 'Quantidade' é obrigatório. Preencha com um valor numérico igual ou superior a 1 (um).")
            if tipo_pesq == 'Nenhum':
                st.error("Selecione um tipo de responsabilidade única válido.")
            if data_publi_pesq and qntd_pesq and tipo_pesq != 'Nenhum':
                st.session_state.pesquisas_lista.append((data_publi_pesq, qntd_pesq, tipo_pesq))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.pesquisas_lista:
            if remove3:
                st.session_state.pesquisas_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- PATENTES E CULTIVARES ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Registro de Patente ou Cultivar</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3 = st.columns([2, 2, 2, 1])
        with col0:
            data_publi_reg = st.date_input(
                "Data de Conclusão",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_reg"
            )
        with col1:
            qntd_reg = st.number_input(
                "Quantidade",
                min_value=0,
                key=f"{key_prefix}_qntd_reg"
            )
        with col2:
            tipo_reg = st.selectbox(
                "Tipo de Registro",
                list(dados_registros.keys()),
                key=f"{key_prefix}_tipo_reg"
            )
        with col3:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted4 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add4", type='primary')
            with c1: remove4 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r4")

        if submitted4:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_publi_reg:
                st.error("O campo 'Data de Conclusão' é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
            if not qntd_reg: 
                st.error("O campo 'Quantidade' é obrigatório. Preencha com um valor numérico igual ou superior a 1 (um).")
            if tipo_reg == 'Nenhum':
                st.error("Selecione um tipo de responsabilidade única válido.")
            if data_publi_reg and qntd_reg and tipo_reg != 'Nenhum':
                st.session_state.registros_lista.append((data_publi_reg, qntd_reg, tipo_reg))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.registros_lista:
            if remove4:
                st.session_state.registros_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- CURSOS ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Estágio Pós-doutoral Desenvolvido no Órgão</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3 = st.columns([2, 2, 2, 1])
        with col0:
            data_publi_curso = st.date_input(
                "Data de Conclusão",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_curso"
            )
        with col1:
            qntd_curso = st.number_input(
                "Quantidade",
                min_value=0,
                key=f"{key_prefix}_qntd_curso"
            )
        with col2:
            tipo_curso = st.selectbox(
                "Tipo de Curso",
                list(dados_cursos.keys()),
                key=f"{key_prefix}_tipo_curso"
            )
        with col3:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted5 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add5", type='primary')
            with c1: remove5 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r5")

        if submitted5:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_publi_curso:
                st.error("O campo 'Data de Conclusão' é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
            if not qntd_curso: 
                st.error("O campo 'Quantidade' é obrigatório. Preencha com um valor numérico igual ou superior a 1 (um).")
            if tipo_curso == 'Nenhum':
                st.error("Selecione um tipo de responsabilidade única válido.")
            if data_publi_curso and qntd_curso and tipo_curso != 'Nenhum':
                st.session_state.cursos_lista.append((data_publi_curso, qntd_curso, tipo_curso))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.cursos_lista:
            if remove5:
                st.session_state.cursos_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

### USAR 1 SÓ PARA TODAS AS RESPONSABILIDADES UNICAS ###
    from itertools import chain
    dados_dict_u = {**dados_artigo, **dados_livro, **dados_pesquisas, **dados_registros, **dados_cursos}
    st.session_state.resp_unicas = [
        (data, qntd * dados_dict_u.get(tipo, 0))
        for data, qntd, tipo in chain(
            st.session_state.artigos_lista,
            st.session_state.livros_lista,
            st.session_state.pesquisas_lista,
            st.session_state.registros_lista,
            st.session_state.cursos_lista
        )
    ]

    if any([st.session_state.artigos_lista, st.session_state.livros_lista,
            st.session_state.pesquisas_lista, st.session_state.registros_lista,
            st.session_state.cursos_lista]):
        
        all_items = list(chain(
            st.session_state.artigos_lista, st.session_state.livros_lista,
            st.session_state.pesquisas_lista, st.session_state.registros_lista,
            st.session_state.cursos_lista
        ))
        
        total_ru = sum(f for _, f, _ in all_items)

        cl0, cl1, cl2= st.columns([2,2,1])
        
        with cl0: st.write("**-Responsabilidades Únicas Registradas-**")
        with cl1: st.write(f"**Total de Responsabilidades Únicas: {total_ru}**")
        with cl2: cleared = st.button("🗑️", use_container_width=True, type='primary', key=f"{key_prefix}_clear")

        cols = st.columns(4)

        all_lists = ["artigos_lista", "livros_lista", "pesquisas_lista", "registros_lista", "cursos_lista", "resp_unicas"]

        for i, (data, qntd, tipo) in enumerate(sorted(all_items, key=lambda data: data[0])):
            col = cols[i % 4]
            with col:
                st.write(f"Data: {data.strftime('%d/%m/%Y')} ")
                st.write(f"{qntd} - {tipo} ")
                st.write("")
        
        if cleared:
            for nome in all_lists:
                st.session_state[nome].clear()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()


def build_responsabilidades_mensais(key_prefix="resp_mensal"):
    """
    Renderiza inputs para 'Responsabilidades' e atualiza st.session_state.{referencia_responsabilidade}.
    """
    ensure_states()
    st.markdown("<h2 style='text-align:left; color:#000000'>Responsabilidades Mensais</h2>", unsafe_allow_html=True)

    from data_utils import dados_cargos, dados_func_c, dados_unicos, dados_agente
    from natsort import natsorted

    suffixes = ["cc", "fc", "fd", "at_a", "at_c", "at_p" ]
    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        for key_suffix in suffixes:
            st.session_state[f"{key_prefix}_tipo_{key_suffix}"] = "Nenhum"
            st.session_state[f"{key_prefix}_data_i_{key_suffix}"] = None
            st.session_state[f"{key_prefix}_data_f_{key_suffix}"] = None
            st.session_state[f"{key_prefix}_sem_data_{key_suffix}"] = False
        st.session_state[f"{key_prefix}_reset_fields"] = False

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
# ---------- CARGO DE COMISSÃO ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Exercício de Cargo em Comissão</h5>", unsafe_allow_html=True)
        cargos_ordenados = natsorted(dados_cargos.keys())
        cargos_ordenados = ['Nenhum'] + [x for x in cargos_ordenados if x != 'Nenhum']
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            cargo_comissao = st.selectbox(
                "Cargo",
                cargos_ordenados,
                key=f"{key_prefix}_tipo_cc"
            )
        with col1:
            data_i_cc = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial - relativedelta(years=5) if st.session_state.data_inicial else None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_cc"
            )
        with col2:
            data_f_cc = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial - relativedelta(years=5) if st.session_state.data_inicial else None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_f_cc",
            )
        with col3:
            st.write("")
            st.write("")
            data_sf_cc = st.checkbox("Sem Data Fim", key=f"{key_prefix}_sem_data_cc")
            if data_sf_cc:
                data_f_cc = st.session_state.data_fim
        with col4:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted1 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add1", type='primary')
            with c1: remove1 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r1")

        if submitted1:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_i_cc:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_cc:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            if cargo_comissao == 'Nenhum':
                st.error("Selecione um cargo de comissão válido.")
            if data_i_cc and data_f_cc:
                if data_f_cc <= data_i_cc or not data_f_cc > data_i_cc + relativedelta(months=1):
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            if st.session_state.data_inicial and data_i_cc < st.session_state.data_inicial:

                print("Funcionou")
            if data_f_cc and data_i_cc and (data_f_cc > data_i_cc + relativedelta(months=1)) and cargo_comissao != 'Nenhum':
                ano = data_f_cc.year - data_i_cc.year
                mes = data_f_cc.month - data_i_cc.month
                tempo = ano * 12 + mes
                st.session_state.comissao_lista.append((f"C. Comissão: {cargo_comissao}", data_i_cc, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.comissao_lista:
            if remove1:
                st.session_state.comissao_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- FUNÇÃO COMISSIONADA ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Exercício de Função Comissionada/Gratificada</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            funcao_comissionada = st.selectbox(
                "Função Comissionada",
                list(dados_func_c.keys()),
                key=f"{key_prefix}_tipo_fc"
            )
        with col1:
            data_i_fc = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial - relativedelta(years=5) if st.session_state.data_inicial else None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_fc"
            )
        with col2:
            data_f_fc = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial- relativedelta(years=5) if st.session_state.data_inicial else None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_f_fc"
            )
        with col3:
            st.write("")
            st.write("")
            data_sf_fc = st.checkbox("Sem Data Fim", key=f"{key_prefix}_sem_data_fc")
            if data_sf_fc:
                data_f_fc = st.session_state.data_fim
        with col4:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted2 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add2", type='primary')
            with c1: remove2 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r2")

        if submitted2:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_i_fc:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_fc:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            if funcao_comissionada == 'Nenhum':
                st.error("Selecione uma função comissionada válida.")
            if data_i_fc and data_f_fc:
                if data_f_fc <= data_i_fc or not data_f_fc > data_i_fc + relativedelta(months=1):
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            if data_f_fc and data_i_fc and (data_f_fc > data_i_fc + relativedelta(months=1)) and funcao_comissionada != 'Nenhum':
                ano = data_f_fc.year - data_i_fc.year
                mes = data_f_fc.month - data_i_fc.month
                tempo = ano * 12 + mes
                st.session_state.func_c_lista.append((f"F. Comissionada: {funcao_comissionada}", data_i_fc, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.func_c_lista:
            if remove2:
                st.session_state.func_c_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- FUNÇÃO DESIGNADA ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Exercício de Função Designada</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            funcao_designada = st.selectbox(
                "Função Designada",
                list(dados_unicos.keys()),
                key=f"{key_prefix}_tipo_fd"
            )
        with col1:
            data_i_fd = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial - relativedelta(years=5) if st.session_state.data_inicial else None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_fd"
            )
        with col2:
            data_f_fd = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial - relativedelta(years=5) if st.session_state.data_inicial else None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_f_fd"
            )
        with col3:
            st.write("")
            st.write("")
            data_sf_fd = st.checkbox("Sem Data Fim", key=f"{key_prefix}_sem_data_fd")
            if data_sf_fd:
                data_f_fd = st.session_state.data_fim
        with col4:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted3 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add3", type='primary')
            with c1: remove3 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r3")

        if submitted3:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_i_fd:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_fd:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            if funcao_designada == 'Nenhum':
                st.error("Selecione uma função designada válida.")
            if data_i_fd and data_f_fd:
                if data_f_fd <= data_i_fd or not data_f_fd > data_i_fd + relativedelta(months=1):
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            if data_f_fd and data_i_fd and (data_f_fd > data_i_fd + relativedelta(months=1)) and funcao_designada != 'Nenhum':
                ano = data_f_fd.year - data_i_fd.year
                mes = data_f_fd.month - data_i_fd.month
                tempo = ano * 12 + mes
                st.session_state.func_d_lista.append((f"F. Designada: {funcao_designada}", data_i_fd, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.func_d_lista:
            if remove3:
                st.session_state.func_d_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- ATUAÇÃO COMO AGENTE ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Atuação como Agente de Contratação, Gestor/Fiscal de Contratos/Convênios</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            atuacao_agente = st.selectbox(
                "Atuação Como Agente",
                list(dados_agente.keys()),
                key=f"{key_prefix}_tipo_at_a"
            )
        with col1:
            data_i_at_a = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_at_a"
            )
        with col2:
            data_f_at_a = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_f_at_a"
            )
        with col3:
            st.write("")
            st.write("")
            data_sf_at_a = st.checkbox("Sem Data Fim", key=f"{key_prefix}_sem_data_at_a")
            if data_sf_at_a:
                data_f_at_a = st.session_state.data_fim
        with col4:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted4 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add4", type='primary')
            with c1: remove4 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r4")

        if submitted4:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_i_at_a:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_at_a:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            if atuacao_agente == 'Nenhum':
                st.error("Selecione uma atuação como agente válida.")
            if data_i_at_a and data_f_at_a or not data_f_at_a > data_i_at_a + relativedelta(months=1):
                if data_f_at_a <= data_i_at_a:
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            if data_f_at_a and data_i_at_a and (data_f_at_a > data_i_at_a + relativedelta(months=1)) and atuacao_agente != 'Nenhum':
                ano = data_f_at_a.year - data_i_at_a.year
                mes = data_f_at_a.month - data_i_at_a.month
                tempo = ano * 12 + mes
                st.session_state.agente_lista.append((f"At. Agente: {atuacao_agente}", data_i_at_a, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.agente_lista:
            if remove4:
                st.session_state.agente_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- ATUAÇÃO EM CONSELHO ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            atuacao_conselho = st.selectbox(
                "Atuação em Conselho",
                list(dados_unicos.keys()),
                key=f"{key_prefix}_tipo_at_c"
            )
        with col1:
            data_i_at_c = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_at_c"
            )
        with col2:
            data_f_at_c = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_f_at_c"
            )
        with col3:
            st.write("")
            st.write("")
            data_sf_at_c = st.checkbox("Sem Data Fim", key=f"{key_prefix}_sem_data_at_c")
            if data_sf_at_c:
                data_f_at_c = st.session_state.data_fim
        with col4:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted5 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add5", type='primary')
            with c1: remove5 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r5")

        if submitted5:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_i_at_c:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_at_c:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            if atuacao_conselho == 'Nenhum':
                st.error("Selecione uma atuação em conselho válida.")
            if data_i_at_c and data_f_at_c or not data_f_at_c > data_i_at_c + relativedelta(months=1):
                if data_f_at_c <= data_i_at_c:
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            if data_f_at_c and data_i_at_c and (data_f_at_c > data_i_at_c + relativedelta(months=1)) and atuacao_conselho != 'Nenhum':
                ano = data_f_at_c.year - data_i_at_c.year
                mes = data_f_at_c.month - data_i_at_c.month
                tempo = ano * 12 + mes
                st.session_state.conselho_lista.append((f"At. Conselho: {atuacao_conselho}", data_i_at_c, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()
        
        if st.session_state.conselho_lista:
            if remove5:
                st.session_state.conselho_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- ATUAÇÃO PRIORITÁRIA ---------- #
        st.markdown("<h5 style='text-align:left; color:#000000'>Exercício em Atuação Prioritária</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            atuacao_prioritaria = st.selectbox(
                "Atuação Prioritária",
                list(dados_unicos.keys()),
                key=f"{key_prefix}_tipo_at_p"
            )
        with col1:
            data_i_at_p = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_at_p"
            )
        with col2:
            data_f_at_p = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_f_at_p"
            )
        with col3:
            st.write("")
            st.write("")
            data_sf_at_p = st.checkbox("Sem Data Fim", key=f"{key_prefix}_sem_data_at_p")
            if data_sf_at_p:
                data_f_at_p = st.session_state.data_fim
        with col4:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted6 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add6", type='primary')
            with c1: remove6 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r6")

        if submitted6:
            if not st.session_state.data_inicial: 
                st.error("Adicione a Data de Enquadramento/Última Evolução.")
            if not data_i_at_p:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_at_p:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            if atuacao_prioritaria == 'Nenhum':
                st.error("Selecione uma atuação prioritária válida.")
            if data_i_at_p and data_f_at_p:
                if data_f_at_p <= data_i_at_p or not data_f_at_p > data_i_at_p + relativedelta(months=1):
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            if data_f_at_p and data_i_at_p and (data_f_at_p > data_i_at_p + relativedelta(months=1)) and atuacao_prioritaria != 'Nenhum':
                ano = data_f_at_p.year - data_i_at_p.year
                mes = data_f_at_p.month - data_i_at_p.month
                tempo = ano * 12 + mes
                st.session_state.prioritaria_lista.append((f"At. Prioritária: {atuacao_prioritaria}", data_i_at_p, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.prioritaria_lista:
            if remove6:
                st.session_state.prioritaria_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

    def _norm_tipo(s: str) -> str:
        # remove prefixo até ": " se existir
        return s.split(": ", 1)[-1] 

### USAR 1 SÓ PARA TODAS AS RESPONSABILIDADES MENSAIS ###
    from itertools import chain
    dados_dict_m = {**dados_cargos, **dados_func_c, **dados_unicos, **dados_agente}
    st.session_state.resp_mensais = [
        (tipo, data_i_cg, tempo, dados_dict_m.get(_norm_tipo(tipo), 0))
        for tipo, data_i_cg, tempo in chain(
            st.session_state.comissao_lista, st.session_state.func_c_lista,
            st.session_state.func_d_lista, st.session_state.agente_lista,
            st.session_state.conselho_lista, st.session_state.prioritaria_lista
        )
    ]

    if any([st.session_state.comissao_lista, st.session_state.func_c_lista,
            st.session_state.func_d_lista, st.session_state.agente_lista,
            st.session_state.conselho_lista, st.session_state.prioritaria_lista]):
        
        total_rm = len(st.session_state.resp_mensais)

        cl0, cl1, cl2= st.columns([2,2,1])
        
        with cl0: st.write("**-Responsabilidades Mensais Registradas-**")
        with cl1: st.write(f"**Total de Responsabilidades Mensais: {total_rm}**")
        with cl2: cleared = st.button("🗑️", use_container_width=True, type='primary', key=f"{key_prefix}_clear")

        cols = st.columns(4)
        all_items = list(chain(
            st.session_state.comissao_lista, st.session_state.func_c_lista,
            st.session_state.func_d_lista, st.session_state.agente_lista,
            st.session_state.conselho_lista, st.session_state.prioritaria_lista
        ))

        all_lists = ["comissao_lista", "func_c_lista", "func_d_lista", "agente_lista", "conselho_lista", "prioritaria_lista", "resp_mensais"]

        for i, (tipo, data_i_cg, tempo) in enumerate(sorted(all_items, key=lambda data: data[1])):
            col = cols[i % 4]
            with col:
                st.write(f"Início: {data_i_cg.strftime('%d/%m/%Y')}")
                st.write(f"{tipo} por {tempo} mese(s)")

        if cleared:
            for nome in all_lists:
                st.session_state[nome].clear()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()


