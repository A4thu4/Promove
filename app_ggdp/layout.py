import streamlit as st

from data_utils import  MIN_DATE, MAX_DATE, NIVEIS

def ensure_states():
    """Inicializa todos os session_states necessários"""
    from data_utils import val_states
    import copy
    for key, val in val_states.items():
        st.session_state.setdefault(key, copy.deepcopy(val))
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(val)


def clear_states():
    """Limpa todos os valores nos session_states"""
    import copy
    from data_utils import val_states
    for key, default_val in val_states.items():
        if isinstance(default_val, list):
            st.session_state[key] = []
        elif isinstance(default_val, (int, float)):
            st.session_state[key] = 0.0 if isinstance(default_val, float) else 0
        elif isinstance(default_val, bool):
            st.session_state[key] = False
        else:
            # deepcopy garante que nenhum valor mutável seja reaproveitado
            st.session_state[key] = copy.deepcopy(default_val)


def build_obrigatorios(key_prefix="obg"):
    """
    Renderiza inputs para 'Requisitos Obrigatórios' e atualiza st.session_state.obrigatorios.
    """
    ensure_states()
    st.markdown("<h2 style='text-align:center; color:#003500; '><u>Dados do Servidor</u></h2>", unsafe_allow_html=True)

    existing_data = st.session_state.obrigatorios[0] if st.session_state.obrigatorios else (None, None, None)
    existing_nivel, existing_data_inicial, existing_pts = existing_data

    # Usar st.form para evitar re-execução a cada input
    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
        col0, col1, col2 = st.columns([2, 2, 2])
        with col0:
            nivel_atual = st.text_input(
                "Nivel Atual",
                max_chars=1,  
                value=existing_nivel if existing_nivel else None,
                key=f"{key_prefix}_nvl_atual"
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
                "Pontos Remanescentes da Última Evolução",
                value=existing_pts if existing_pts else None,
                min_value=0.0,
                format="%.3f",
                key=f"{key_prefix}_pts_rem"
            )     
        with col1:
            c0, c1 =st.columns([2,2])
            with c0: submitted = st.form_submit_button("Enviar", use_container_width=True, type='primary')
            with c1: remove = st.form_submit_button("Remover", use_container_width=True)

    if submitted:
        if not nivel_atual:
            st.error("Campo 'Nivel Atual' é obrigatório.")
        elif nivel_atual not in NIVEIS:
            st.error(f"Nível '{nivel_atual}' não é válido. Níveis permitidos: {NIVEIS}.")
        if not st.session_state.data_inicial:
            st.error("Data inicial é obrigatória.")
        if pts_remanescentes == None:
            st.error("Pontos remanescentes é obrigatório (mesmo que seja 0).")
        else:
            st.session_state.obrigatorios = [(nivel_atual, st.session_state.data_inicial, float(pts_remanescentes))]
            st.session_state.nivel_atual = nivel_atual if nivel_atual else 'A'
            st.session_state.pts_ultima_evolucao = float(pts_remanescentes)
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
                st.write(f"Pontuação Inicial: {pts}.")
                if remove:
                    st.session_state.obrigatorios.pop(i)
                    st.session_state.data_inicial = None
                    st.session_state.carreira = []
                    st.rerun()


def build_afastamentos(key_prefix="afast"):
    """
    Renderiza inputs para 'Afastamentos' e atualiza st.session_state.afastamentos.
    """
    ensure_states()
    st.markdown("<h2 style='text-align:center; color:#003500; '><u>Afastamentos Não Considerados Como Efetivo Exercício</u></h2>", unsafe_allow_html=True)

    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        st.session_state[f"{key_prefix}_mes"] = None
        st.session_state[f"{key_prefix}_qntd"] = 0
        st.session_state[f"{key_prefix}_reset_fields"] = False

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
        col0, col1 = st.columns([1, 1])
        with col0:
            mes_faltas = st.date_input(
                "Mês (será considerado somente o mês)",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_mes"
            )
            c, c11 = st.columns([2,1])
            with c11: submitted = st.form_submit_button("➕", use_container_width=True, type='primary')
        with col1:
            qntd_faltas = st.number_input(
                "Faltas (nº)",
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
            st.error("Preencha a Data corretamente.")
        if not qntd_faltas or qntd_faltas == 0:
            st.error("Número de faltas precisa ser maior do que 0.")
        if st.session_state.data_inicial != None and mes_faltas:
            if mes_faltas < st.session_state.data_inicial:
                st.error("Data não pode ser anterior a data de Enquadramento/Última Evolução.")
            if mes_faltas >= st.session_state.data_inicial and qntd_faltas > 0:
                st.session_state.afastamentos.append((mes_faltas, int(qntd_faltas)))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

    if cleared:
        st.session_state.afastamentos.clear()
        st.session_state[f"{key_prefix}_reset_fields"] = True
        st.rerun()

    if st.session_state.afastamentos:
        total_afast = sum(f for _, f in st.session_state.afastamentos)

        cl = st.columns(2)
        
        with cl[0]: st.write("**-Afastamentos Registrados-**")
        with cl[1]: st.write(f"**Total de Afastamentos: {total_afast}**")
        
        cols = st.columns(6)
        for i, (mes, faltas) in enumerate(sorted(st.session_state.afastamentos, key=lambda data: data[0])):
            col = cols[i % 6]
            with col:
                st.write(f"Data: {mes.strftime('%m/%Y')}.") 
                st.write(f"{faltas} falta(s).")
                if remove:
                    st.session_state.afastamentos.pop()
                    st.session_state[f"{key_prefix}_reset_fields"] = True
                    st.rerun()


def build_aperfeicoamentos(key_prefix="aperf"):
    """
    Renderiza inputs para 'Aperfeiçoamentos' (data de conclusão + horas) e atualiza st.session_state.aperfeicoamentos.
    Aproveitamento das horas (limite 100h, pontos = horas * 0.09) fica em logic.
    """
    ensure_states()
    st.markdown("<h2 style='text-align:center; color:#003500'><u>Aperfeiçoamentos</u></h2>", unsafe_allow_html=True)

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
                "Horas do Curso",
                min_value=0,
                max_value=100,
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
            st.error("Preencha a Data Corretamente.")
        if not horas_curso or horas_curso < 4:
            st.error("Preencha as Horas. O Mínimo de horas aceitado é 4hrs.")
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
            st.warning("Limie Máximo de Horas Atingido no Interstício de Evolução: **100**")
        
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
    st.markdown("<h2 style='text-align:center; color:#003500'><u>Titulações</u></h2>", unsafe_allow_html=True)

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
                min_value=st.session_state.data_inicial,
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

    if submitted:
        if not st.session_state.data_inicial: 
            st.error("Adicione a Data de Enquadramento/Última Evolução")
        if not data_conclusao:
            st.error("Preencha a Data corretamente.")
        if tipo_tit == 'Nenhuma':
            st.error("Escolha uma Titulação válida.")
        if st.session_state.data_inicial != None:
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
    st.markdown("<h2 style='text-align:center; color:#003500'><u>Responsabilidades Únicas</u></h2>", unsafe_allow_html=True)

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
        st.markdown("<h5 style='text-align:left; color:#003500'>Publicação de Artigos ou Pesquisas Científicas com ISSN</h5>", unsafe_allow_html=True)
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
                value=0,
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
                st.error("Preencha a Data corretamente.")
            if not qntd_art: 
                st.error("Preencha Quantidade.")
            if tipo_art == 'Nenhum':
                st.error("Escolha um Tipo válido.")
            if data_publi_art and qntd_art and tipo_art != 'Nenhum':
                st.session_state.artigos_lista.append((data_publi_art, qntd_art, tipo_art))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if remove1:
            st.session_state.artigos_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

# ---------- LIVROS ---------- #
        st.markdown("<h5 style='text-align:left; color:#003500'>Publicações de Livros com Corpo Editorial e ISBN</h5>", unsafe_allow_html=True)
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
                value=0,
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
                st.error("Preencha a Data corretamente.")
            if not qntd_liv: 
                st.error("Preencha Quantidade.")
            if tipo_liv == 'Nenhum':
                st.error("Escolha um Tipo válido.")
            if data_publi_liv and qntd_liv and tipo_liv != 'Nenhum':
                st.session_state.livros_lista.append((data_publi_liv, qntd_liv, tipo_liv))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()
        
        if remove2:
            st.session_state.livros_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

# ---------- PESQUISAS CIENTIFICAS ---------- #
        st.markdown("<h5 style='text-align:left; color:#003500'>Publicações de Artigos ou Pesquisas Científicas Aprovadas em Eventos Científicos</h5>", unsafe_allow_html=True)
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
                value=0,
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
                st.error("Preencha a Data corretamente.")
            if not qntd_pesq: 
                st.error("Preencha Quantidade.")
            if tipo_pesq == 'Nenhum':
                st.error("Escolha um Tipo válido.")
            if data_publi_pesq and qntd_pesq and tipo_pesq != 'Nenhum':
                st.session_state.pesquisas_lista.append((data_publi_pesq, qntd_pesq, tipo_pesq))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if remove3:
            st.session_state.pesquisas_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

# ---------- PATENTES E CULTIVARES ---------- #
        st.markdown("<h5 style='text-align:left; color:#003500'>Registro de Patente ou Cultivar</h5>", unsafe_allow_html=True)
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
                value=0,
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
                st.error("Preencha a Data corretamente.")
            if not qntd_reg: 
                st.error("Preencha Quantidade.")
            if tipo_reg == 'Nenhum':
                st.error("Escolha um Tipo válido.")
            if data_publi_reg and qntd_reg and tipo_reg != 'Nenhum':
                st.session_state.registros_lista.append((data_publi_reg, qntd_reg, tipo_reg))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if remove4:
            st.session_state.registros_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

# ---------- PATENTES E CULTIVARES ---------- #
        st.markdown("<h5 style='text-align:left; color:#003500'>Estágio Pós-Doutoral Desenvolvido no Órgão</h5>", unsafe_allow_html=True)
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
                value=0,
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
                st.error("Preencha a Data corretamente.")
            if not qntd_curso: 
                st.error("Preencha Quantidade.")
            if tipo_curso == 'Nenhum':
                st.error("Escolha um Tipo válido.")
            if data_publi_curso and qntd_curso and tipo_curso != 'Nenhum':
                st.session_state.cursos_lista.append((data_publi_curso, qntd_curso, tipo_curso))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if remove5:
            st.session_state.cursos_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

### USAR 1 SÓ PARA TODAS AS RESPONSABILIDADES UNICAS ###
    from itertools import chain
    dados_dict = {**dados_artigo, **dados_livro, **dados_pesquisas, **dados_registros, **dados_cursos}
    st.session_state.resp_unicas = [
        (data, qntd * dados_dict.get(tipo, 0))
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
        
        total_ru = len(st.session_state.resp_unicas)

        cl = st.columns(2)
        
        with cl[0]: st.write("**-Responsabilidades Únicas Registradas-**")
        with cl[1]: st.write(f"**Total de Responsabilidades Únicas: {total_ru}**")

        cols = st.columns(4)
        all_items = list(chain(
            st.session_state.artigos_lista, st.session_state.livros_lista,
            st.session_state.pesquisas_lista, st.session_state.registros_lista,
            st.session_state.cursos_lista
        ))

        for i, (data, qntd, tipo) in enumerate(sorted(all_items, key=lambda data: data[0])):
            col = cols[i % 4]
            with col:
                st.write(f"Data: {data.strftime('%d/%m/%Y')} ")
                st.write(f"{qntd} - {tipo} ")
                st.write("")


def build_responsabilidades_mensais(key_prefix="resp_mensal"):
    """
    Renderiza inputs para 'Responsabilidades' e atualiza st.session_state.{referencia_responsabilidade}.
    """
    ensure_states()
    st.markdown("<h2 style='text-align:center; color:#003500'><u>Responsabilidades Mensais</u></h2>", unsafe_allow_html=True)

    from data_utils import dados_cargos, dados_func_c, dados_unicos, dados_agente

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
        st.markdown("<h5 style='text-align:left; color:#003500'>Exercício de Cargo em Comissão</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            cargo_comissao = st.selectbox(
                "Cargo",
                sorted(dados_cargos.keys(), key=lambda x: (x != 'Nenhum', x)),
                key=f"{key_prefix}_tipo_cc"
            )
        with col1:
            data_i_cc = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_cc"
            )
        with col2:
            data_f_cc = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_f_cc"
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
            if not data_i_cc or not data_f_cc:
                st.error("Preencha a(s) Data(s) corretamente.")
            if cargo_comissao == 'Nenhum':
                st.error("Escolha um Cargo válido.")
            if data_f_cc and data_i_cc and cargo_comissao != 'Nenhum':
                ano = data_f_cc.year - data_i_cc.year
                mes = data_f_cc.month - data_i_cc.month
                tempo = ano * 12 + mes
                st.session_state.comissao_lista.append((f"C. Comissão: {cargo_comissao}", data_i_cc, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if remove1:
            st.session_state.comissao_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

# ---------- FUNÇÃO COMISSIONADA ---------- #
        st.markdown("<h5 style='text-align:left; color:#003500'>Exercício de Função Comissionada/Gratificada</h5>", unsafe_allow_html=True)
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
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_fc"
            )
        with col2:
            data_f_fc = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
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
            if not data_i_fc or not data_f_fc:
                st.error("Preencha a(s) Data(s) corretamente.")
            if funcao_comissionada == 'Nenhum':
                st.error("Escolha um Cargo válido.")
            if data_f_fc and data_i_fc and funcao_comissionada != 'Nenhum':
                ano = data_f_fc.year - data_i_fc.year
                mes = data_f_fc.month - data_i_fc.month
                tempo = ano * 12 + mes
                st.session_state.func_c_lista.append((f"F. Comissionada: {funcao_comissionada}", data_i_fc, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if remove2:
            st.session_state.func_c_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

# ---------- FUNÇÃO DESIGNADA ---------- #
        st.markdown("<h5 style='text-align:left; color:#003500'>Exercício de Função Designada</h5>", unsafe_allow_html=True)
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
                min_value=st.session_state.data_inicial,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_fd"
            )
        with col2:
            data_f_fd = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.data_inicial,
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
            if not data_i_fd or not data_f_fd:
                st.error("Preencha a(s) Data(s) corretamente.")
            if funcao_designada == 'Nenhum':
                st.error("Escolha um Cargo válido.")
            if data_f_fd and data_i_fd and funcao_designada != 'Nenhum':
                ano = data_f_fd.year - data_i_fd.year
                mes = data_f_fd.month - data_i_fd.month
                tempo = ano * 12 + mes
                st.session_state.func_d_lista.append((f"F. Designada: {funcao_designada}", data_i_fd, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if remove3:
            st.session_state.func_d_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

# ---------- ATUAÇÃO COMO AGENTE ---------- #
        st.markdown("<h5 style='text-align:left; color:#003500'>Atuação como Agente de Contratação, Gestor/Fiscal de Contratos/Convênios</h5>", unsafe_allow_html=True)
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
            if not data_i_at_a or not data_f_at_a:
                st.error("Preencha a(s) Data(s) corretamente.")
            if atuacao_agente == 'Nenhum':
                st.error("Escolha um Cargo válido.")
            if data_f_at_a and data_i_at_a and atuacao_agente != 'Nenhum':
                ano = data_f_at_a.year - data_i_at_a.year
                mes = data_f_at_a.month - data_i_at_a.month
                tempo = ano * 12 + mes
                st.session_state.agente_lista.append((f"At. Agente: {atuacao_agente}", data_i_at_a, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if remove4:
            st.session_state.agente_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

# ---------- ATUAÇÃO EM CONSELHO ---------- #
        st.markdown("<h5 style='text-align:left; color:#003500'>Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho</h5>", unsafe_allow_html=True)
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
            if not data_i_at_c or not data_f_at_c:
                st.error("Preencha a(s) Data(s) corretamente.")
            if atuacao_conselho == 'Nenhum':
                st.error("Escolha um Cargo válido.")
            if data_f_at_c and data_i_at_c and atuacao_conselho != 'Nenhum':
                ano = data_f_at_c.year - data_i_at_c.year
                mes = data_f_at_c.month - data_i_at_c.month
                tempo = ano * 12 + mes
                st.session_state.conselho_lista.append((f"At. Conselho: {atuacao_conselho}", data_i_at_c, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if remove5:
            st.session_state.conselho_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

# ---------- ATUAÇÃO PRIORITÁRIA ---------- #
        st.markdown("<h5 style='text-align:left; color:#003500'>Exercício em Atuação Prioritária</h5>", unsafe_allow_html=True)
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
            if not data_i_at_p or not data_f_at_p:
                st.error("Preencha a(s) Data(s) corretamente.")
            if atuacao_prioritaria == 'Nenhum':
                st.error("Escolha um Cargo válido.")
            if data_f_at_p and data_i_at_p and atuacao_prioritaria != 'Nenhum':
                ano = data_f_at_p.year - data_i_at_p.year
                mes = data_f_at_p.month - data_i_at_p.month
                tempo = ano * 12 + mes
                st.session_state.prioritaria_lista.append((f"At. Prioritária: {atuacao_prioritaria}", data_i_at_p, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if remove6:
            st.session_state.prioritaria_lista.pop()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()

### USAR 1 SÓ PARA TODAS AS RESPONSABILIDADES MENSAIS ###
    from itertools import chain
    dados_dict2 = {**dados_cargos, **dados_func_c, **dados_unicos, **dados_agente}
    st.session_state.resp_mensais = [
        (tipo, data_i_cg, tempo, dados_dict2.get(tipo, 0))
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

        cl = st.columns(2)
        
        with cl[0]: st.write("**-Responsabilidades Mensais Registradas-**")
        with cl[1]: st.write(f"**Total de Responsabilidades Mensais: {total_rm}**")

        cols = st.columns(4)
        all_items = list(chain(
            st.session_state.comissao_lista, st.session_state.func_c_lista,
            st.session_state.func_d_lista, st.session_state.agente_lista,
            st.session_state.conselho_lista, st.session_state.prioritaria_lista
        ))

        for i, (tipo, data_i_cg, tempo) in enumerate(sorted(all_items, key=lambda data: data[1])):
            col = cols[i % 4]
            with col:
                st.write(f"Início: {data_i_cg.strftime('%d/%m/%Y')}")
                st.write(f"{tipo} por {tempo} meses")
