import streamlit as st
import pandas as pd

from data_utils_ueg import DECRETO_DATE, MIN_DATE, MAX_DATE, NIVEIS, val_states
from dateutil.relativedelta import relativedelta
from datetime import date


def ensure_states() -> None:
    """Inicializa todos os session_states necessários"""

    import copy
    for key, val in val_states.items():
        st.session_state.setdefault(key, copy.deepcopy(val))
        

def clear_states():
    """Limpa todos os valores nos session_states"""

    for key, default_val in val_states.items():
        if isinstance(default_val, list):
            st.session_state[key] = []
        elif isinstance(default_val, (int, float)):
            st.session_state[key] = 0.0 if isinstance(default_val, float) else 0
        elif isinstance(default_val, bool):
            st.session_state[key] = False
        else:
            # deepcopy garante que nenhum valor mutável seja reaproveitado
            st.session_state[key] = default_val


def build_obrigatorios(key_prefix="obg"):
    """Renderiza inputs para 'Requisitos Obrigatórios' e atualiza st.session_state.obrigatorios."""

    st.markdown("<h1 class='left'>Requisitos Obrigatórios</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='left'>Dados do Servidor</h2>", unsafe_allow_html=True)

    existing_data = st.session_state.obrigatorios[0] if st.session_state.obrigatorios else (None, None, None, None)
    existing_nivel, existing_data_inicial, existing_data_enquadramento, existing_pts = existing_data

    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        st.session_state[f"{key_prefix}_nvl_atual"] = existing_nivel if existing_nivel else None
        st.session_state[f"{key_prefix}_data_inicial"] = None
        st.session_state[f"{key_prefix}_data_enquad"] = None
        st.session_state[f"{key_prefix}_pts_rem"] = None
        st.session_state[f"{key_prefix}_reset_fields"] = False

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
        col0, col1, col2, col3 = st.columns([2, 2, 2, 2])
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
            st.session_state.enquadramento = st.date_input(
                "Data do Enquadramento",
                format="DD/MM/YYYY",
                value=existing_data_enquadramento if existing_data_enquadramento else None,
                min_value=None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_enquad"
            )
        with col2:
            st.session_state.data_inicial = st.date_input(
                "Data de Início dos Pontos",
                format="DD/MM/YYYY",
                value=existing_data_inicial if existing_data_inicial else None,
                min_value=MIN_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_inicial",
                help="Conforme disposições finais e transitórios do Decreto nº 10.802/2025"
            )   
        with col3:
            pts_remanescentes = st.number_input(
                "Pontuação Excedente da Última Evolução",
                value=existing_pts if existing_pts else None,
                min_value=0.0,
                format="%.3f",
                key=f"{key_prefix}_pts_rem",
                help="Caso não haja pontuação remanescente, preencha com o número 0 (zero)."
            )     
        with col1:
            c0, c1 =st.columns([2,2])
            with c1: submitted = st.form_submit_button("Enviar", use_container_width=True, type='primary')
        with col2:
            c0, c1 = st.columns([2,2])    
            with c0: remove = st.form_submit_button("Remover", use_container_width=True)

    if submitted:
        if not nivel_atual:
            st.error("O campo 'Nivel Atual' é obrigatório. Preencha com valores entre A e S.")
        elif nivel_atual not in NIVEIS:
            st.error(f"O nível '{nivel_atual}' não é válido. Níveis permitidos: {NIVEIS}.")
        
        if not st.session_state.data_inicial:
            st.error("O campo 'Data inicial' é obrigatório. Preencha com a data da última evolução ou do último enquadramento.")
        
        if pts_remanescentes == None:
            st.error("O campo 'Pontos Remanescentes da Última Evolução' é obrigatório. Caso não haja pontuação remanescente, preencha com o número 0 (zero).")
        
        if st.session_state.data_inicial and st.session_state.enquadramento and nivel_atual in NIVEIS and pts_remanescentes != None:
            st.session_state.pts_ultima_evolucao = float(pts_remanescentes)
            st.session_state.nivel_atual = nivel_atual if nivel_atual else 'A'
            st.session_state.obrigatorios = [(nivel_atual, st.session_state.data_inicial, st.session_state.enquadramento,  float(pts_remanescentes))]
            st.session_state.carreira = []

    # Mostrar dados cadastrados 
    if st.session_state.obrigatorios:
        cols = st.columns(2)
        for i, (nivel, data1, data2, pts) in enumerate(st.session_state.obrigatorios):
            col = cols[i % 4]
            with col:
                st.write(f"Nivel Atual: {nivel}.")
                st.write(f"Data de Início: {data1.strftime('%d/%m/%Y')}.")
                st.write(f"Data do Enquadramento: {data2.strftime('%d/%m/%Y')}.")
                st.write(f"Pontuação Inicial: {pts}")
                if remove:
                    st.session_state.obrigatorios.pop(i)
                    st.session_state[f"{key_prefix}_reset_fields"] = True
                    st.rerun()


def build_afastamentos(key_prefix="afast"):
    """
    Renderiza inputs para 'Afastamentos' e atualiza st.session_state.afastamentos.
    """
    st.markdown("<h2 class='left'>Afastamentos Não Considerados como Efetivo Exercício</h2>", unsafe_allow_html=True)

    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        st.session_state[f"{key_prefix}_mes"] = None
        st.session_state[f"{key_prefix}_qntd"] = 0
        st.session_state[f"{key_prefix}_reset_fields"] = False

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
        col0, col1 = st.columns([1, 1])
        with col0:
            mes_faltas = st.date_input(
                "Mês dos Afastamentos",
                format="DD/MM/YYYY",
                min_value=st.session_state.enquadramento - relativedelta(years=5) if st.session_state.enquadramento else None,
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
        if not st.session_state.obrigatorios: 
            st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
        
        if not mes_faltas:
            st.error("Preencha o campo 'Mês do Afastamento' com a data completa no formato DD/MM/AAAA. O cálculo levará em conta apenas o mês e o ano, independemente do dia preenchido. ")
        
        if not qntd_faltas or qntd_faltas == 0:
            st.error("Preencha o campo 'Quantitativo Total de Afastamentos no Mês' com um valor númerico acima de 0 (zero).")
        
        if st.session_state.obrigatorios and mes_faltas:
            if any((mes.month, mes.year) == (mes_faltas.month, mes_faltas.year) for mes, _ in st.session_state.afastamentos):
                st.warning("Mês e ano já registrados.")
            if qntd_faltas > 0 and not any((mes.month, mes.year) == (mes_faltas.month, mes_faltas.year) for mes, _ in st.session_state.afastamentos):
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
                st.write(f"{faltas} afastamento(s).")
                if remove:
                    st.session_state.afastamentos.pop()
                    st.session_state[f"{key_prefix}_reset_fields"] = True
                    st.rerun()


def build_desempenho(key_prefix="des"):
    """Renderiza inputs para 'Desempenhos' e atualiza st.session_state.afastamentos."""

    st.markdown("<h2 class='left'>Desempenho no Exercício das Atribuições de Ensino, Pesquisa e Extensão</h2>", unsafe_allow_html=True)

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False, enter_to_submit=False):
        col0, col1, col2 = st.columns([1, 1, 1])
        with col0:
            st.text_input(
                "Pontuação Mensal",
                value="1.8",
                key=f"{key_prefix}_pts_mes",
                disabled=True,
                help="Valor referencial padrão para pontuação mensal"
            )
        with col1:
            st.text_input(
                "Pontuação Semestral",
                value="10.8",
                key=f"{key_prefix}_pts_semestre",
                disabled=True,
                help="Valor referencial padrão para pontuação semestral"
            )
        with col2:
            st.text_input(
                "Pontuação Final por Ciclo de Evolução",
                value="43.2",
                key=f"{key_prefix}_pts_final",
                disabled=True,
                help="Valor referencial padrão para pontuação final"
            )
        
        st.form_submit_button(
            "Obs.: a pontuação referente ao desempenho no exercício das atribuições será calculada nesta simulação com os valores referenciais padrões. Os campos deste bloco não deverão ser preenchidos", 
            use_container_width=True, 
            disabled=True
        )
 

def build_titulacoes(key_prefix="tit"):
    """
    Renderiza inputs para 'Titulações' (data de conclusão + tipo da titulação) e atualiza st.session_state.titulacoes.
    """
    st.markdown("<h1 class='left'>Requisitos Aceleradores</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='left'>Titulação e Qualificação Acadêmica</h2>", unsafe_allow_html=True)

    from data_utils_ueg import dados_tit

    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        st.session_state[f"{key_prefix}_data"] = None
        st.session_state[f"{key_prefix}_tipo"] = "Nenhuma"
        st.session_state[f"{key_prefix}_reset_fields"] = False

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
        col1, col2 = st.columns([1, 1])
        with col1:
            data_conclusao = st.date_input(
                "Data de Validação",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data"
            )
            c, c13 =st.columns([2,1])
            with c13: submitted = st.form_submit_button("➕", use_container_width=True, type='primary')
        with col2:
            tipo_tit = st.selectbox(
                "Tipo de Titulação",
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
        if not st.session_state.obrigatorios: 
            st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
        
        if not data_conclusao:
            st.error("O campo “Data de Conclusão” é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
        
        if tipo_tit == 'Nenhuma':
            st.error("Selecione um tipo de titulação válido.")
        
        if ultima_titulacao and data_conclusao:
            if isinstance(ultima_titulacao, date) and isinstance(data_conclusao, date):
                if data_conclusao < (ultima_titulacao + relativedelta(months=12)) or data_conclusao < (ultima_titulacao - relativedelta(months=12)):
                    st.warning("Limite de titulações excedido no período (art. 44, § 10.: poderá ser validada uma titulação acadêmica por ano civil, com interstício mínimo de 12 (doze) meses entre uma e outra validação).") 
        
        if st.session_state.obrigatorios:
            if ultima_titulacao is None or (data_conclusao > (ultima_titulacao + relativedelta(months=12) - relativedelta(days=1)) or data_conclusao < (ultima_titulacao - relativedelta(months=12) + relativedelta(days=1))):
                if tipo_tit != 'Nenhuma':
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


def build_responsabilidades_mensais(key_prefix="resp_mensal"):
    """
    Renderiza inputs para 'Responsabilidades' e atualiza st.session_state.{referencia_responsabilidade}.
    """
    st.markdown("<h1 class='left'>Assunção de Responsabilidades</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='left'>Pontuação Mensal</h3>", unsafe_allow_html=True)

    from data_utils_ueg import dados_cargos, dados_func_c, dados_unicos, dados_agente, DECRETO_DATE
    def natural_key(s):
        import re
        return [int(t) if t.isdigit() else t for t in re.findall(r'\d+|\D+', s)]

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
        st.markdown("<h5 class='left'>Exercício de Cargo em Comissão</h5>", unsafe_allow_html=True)
        cargos_ordenados = sorted(dados_cargos.keys(), key=natural_key)
        cargos_ordenados = ['Nenhum'] + [x for x in cargos_ordenados if x != 'Nenhum']
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            cargo_comissao = st.selectbox(
                "Símbolo",
                cargos_ordenados,
                key=f"{key_prefix}_tipo_cc"
            )
        with col1:
            data_i_cc = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.enquadramento - relativedelta(years=5) if st.session_state.enquadramento else None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_cc"
            )
        with col2:
            data_f_cc = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.enquadramento - relativedelta(years=5) if st.session_state.enquadramento else None,
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
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
            
            if not data_i_cc:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_cc:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            
            if cargo_comissao == 'Nenhum':
                st.error("Selecione um cargo de comissão válido.")

            if data_i_cc and data_f_cc:
                if data_f_cc < data_i_cc:
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            
            if st.session_state.obrigatorios and data_f_cc and data_i_cc and data_f_cc > data_i_cc and cargo_comissao != 'Nenhum':
                tempo = (data_f_cc.year - data_i_cc.year) * 12 + (data_f_cc.month - data_i_cc.month)
                st.session_state.comissao_lista.append((f"C. Comissão: {cargo_comissao}", data_i_cc, data_f_cc, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.comissao_lista:
            if remove1:
                st.session_state.comissao_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- FUNÇÃO COMISSIONADA ---------- #
        st.markdown("<h5 class='left'>Exercício de Função Comissionada/Gratificada</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            funcao_comissionada = st.selectbox(
                "Valor",
                list(dados_func_c.keys()),
                key=f"{key_prefix}_tipo_fc"
            )
        with col1:
            data_i_fc = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.enquadramento - relativedelta(years=5) if st.session_state.enquadramento else None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_fc"
            )
        with col2:
            data_f_fc = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.enquadramento- relativedelta(years=5) if st.session_state.enquadramento else None,
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
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")

            if not data_i_fc:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_fc:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            
            if funcao_comissionada == 'Nenhum':
                st.error("Selecione uma função comissionada válida.")

            if data_i_fc and data_f_fc:
                if data_f_fc < data_i_fc:
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            
            if st.session_state.obrigatorios and data_f_fc and data_i_fc and data_f_fc > data_i_fc and funcao_comissionada != 'Nenhum':
                tempo = (data_f_fc.year - data_i_fc.year) * 12 + (data_f_fc.month - data_i_fc.month)
                st.session_state.func_c_lista.append((f"F. Comissionada: {funcao_comissionada}", data_i_fc, data_f_fc, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.func_c_lista:
            if remove2:
                st.session_state.func_c_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- FUNÇÃO DESIGNADA ---------- #
        st.markdown("<h5 class='left'>Exercício de Função Designada</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            funcao_designada = st.selectbox(
                "Selecione",
                list(dados_unicos.keys()),
                key=f"{key_prefix}_tipo_fd"
            )
        with col1:
            data_i_fd = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.enquadramento - relativedelta(years=5) if st.session_state.enquadramento else None,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_fd"
            )
        with col2:
            data_f_fd = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.enquadramento - relativedelta(years=5) if st.session_state.enquadramento else None,
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
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
            
            if not data_i_fd:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_fd:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            
            if funcao_designada == 'Nenhum':
                st.error("Selecione uma função designada válida.")

            if data_i_fd and data_f_fd:
                if data_f_fd < data_i_fd:
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            
            if st.session_state.obrigatorios and data_f_fd and data_i_fd and data_f_fd > data_i_fd and funcao_designada != 'Nenhum':
                tempo = (data_f_fd.year - data_i_fd.year) * 12 + (data_f_fd.month - data_i_fd.month)
                st.session_state.func_d_lista.append((f"F. Designada: {funcao_designada}", data_i_fd, data_f_fd, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.func_d_lista:
            if remove3:
                st.session_state.func_d_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- ATUAÇÃO COMO AGENTE ---------- #
        st.markdown("<h5 class='left'>Atuação como Agente de Contratação, Gestor/Fiscal de Contratos/Convênios</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            atuacao_agente = st.selectbox(
                "Faixa",
                list(dados_agente.keys()),
                key=f"{key_prefix}_tipo_at_a"
            )
        with col1:
            data_i_at_a = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_at_a"
            )
        with col2:
            data_f_at_a = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
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
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
            
            if not data_i_at_a:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_at_a:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            
            if atuacao_agente == 'Nenhum':
                st.error("Selecione uma atuação como agente válida.")

            if data_i_at_a and data_f_at_a:
                if data_f_at_a < data_i_at_a:
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            
            if st.session_state.obrigatorios and data_f_at_a and data_i_at_a and data_f_at_a > data_i_at_a  and atuacao_agente != 'Nenhum':
                tempo = (data_f_at_a.year - data_i_at_a.year) * 12 + (data_f_at_a.month - data_i_at_a.month)
                st.session_state.agente_lista.append((f"At. Agente: {atuacao_agente}", data_i_at_a, data_f_at_a, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.agente_lista:
            if remove4:
                st.session_state.agente_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- ATUAÇÃO EM CONSELHO ---------- #
        st.markdown("<h5 class='left'>Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            atuacao_conselho = st.selectbox(
                "Selecione",
                list(dados_unicos.keys()),
                key=f"{key_prefix}_tipo_at_c"
            )
        with col1:
            data_i_at_c = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_at_c"
            )
        with col2:
            data_f_at_c = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
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
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
            
            if not data_i_at_c:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_at_c:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            
            if atuacao_conselho == 'Nenhum':
                st.error("Selecione uma atuação em conselho válida.")

            if data_i_at_c and data_f_at_c:
                if data_f_at_c < data_i_at_c:
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            
            if st.session_state.obrigatorios and data_f_at_c and data_i_at_c and data_f_at_c > data_i_at_c and atuacao_conselho != 'Nenhum':
                ano = data_f_at_c.year - data_i_at_c.year
                mes = data_f_at_c.month - data_i_at_c.month
                tempo = (data_f_at_c.year - data_i_at_c.year) * 12 + (data_f_at_c.month - data_i_at_c.month)
                st.session_state.conselho_lista.append((f"At. Conselho: {atuacao_conselho}", data_i_at_c, data_f_at_c, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.conselho_lista:
            if remove5:
                st.session_state.conselho_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- ATUAÇÃO PRIORITÁRIA ---------- #
        st.markdown("<h5 class='left'>Exercício em Atuação Prioritária</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            atuacao_prioritaria = st.selectbox(
                "Selecione",
                list(dados_unicos.keys()),
                key=f"{key_prefix}_tipo_at_p"
            )
        with col1:
            data_i_at_p = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_at_p"
            )
        with col2:
            data_f_at_p = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
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
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
            
            if not data_i_at_p:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_at_p:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            
            if atuacao_prioritaria == 'Nenhum':
                st.error("Selecione uma atuação prioritária válida.")

            if data_i_at_p and data_f_at_p:
                if data_f_at_p < data_i_at_p:
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            
            if st.session_state.obrigatorios and data_f_at_p and data_i_at_p and data_f_at_p > data_i_at_p and atuacao_prioritaria != 'Nenhum':
                tempo = (data_f_at_p.year - data_i_at_p.year) * 12 + (data_f_at_p.month - data_i_at_p.month)
                st.session_state.prioritaria_lista.append((f"At. Prioritária: {atuacao_prioritaria}", data_i_at_p, data_f_at_p, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.prioritaria_lista:
            if remove6:
                st.session_state.prioritaria_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- EXECUÇÃO/EXTENSÃO ---------- #
        st.markdown("<h5 class='left'>Execução de Projeto de Ensino, Pesquisa e/ou Extensão com Captação de Recursos</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3, col4 = st.columns([2, 2, 2, 1, 2])
        with col0:
            exec_projeto = st.selectbox(
                "Selecione",
                list(dados_unicos.keys()),
                key=f"{key_prefix}_tipo_ex_p"
            )
        with col1:
            data_i_ex_p = st.date_input(
                "Data de Início",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_i_ex_p"
            )
        with col2:
            data_f_ex_p = st.date_input(
                "Data de Fim",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_f_ex_p"
            )
        with col3:
            st.write("")
            st.write("")
            data_sf_ex_p = st.checkbox("Sem Data Fim", key=f"{key_prefix}_sem_data_ex_p")
            if data_sf_ex_p:
                data_f_ex_p = st.session_state.data_fim
        with col4:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted7 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add7", type='primary')
            with c1: remove7 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r7")

        if submitted7:
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
            
            if not data_i_ex_p:
                st.error("O campo 'Data de Início' é obrigatório. Preencha com a data de início da responsabilidade mensal.")
            if not data_f_ex_p:
                st.error("O campo 'Data de Fim' é obrigatório. Preencha com a data de fim da responsabilidade mensal ou marque a opção 'Sem Data Fim'.")
            
            if exec_projeto == 'Nenhum':
                st.error("Selecione uma atuação prioritária válida.")
                
            if data_i_ex_p and data_f_ex_p:
                if data_f_ex_p < data_i_ex_p:
                    st.error("A data de fim não pode ser anterior à data de início ou menor que 1 mês.")
            
            if st.session_state.obrigatorios and data_f_ex_p and data_i_ex_p and data_f_ex_p > data_i_ex_p and exec_projeto != 'Nenhum':
                tempo = (data_f_ex_p.year - data_i_ex_p.year) * 12 + (data_f_ex_p.month - data_i_ex_p.month)
                st.session_state.projeto_lista.append((f"Ex. Projeto: {exec_projeto}", data_i_ex_p, data_f_ex_p, tempo))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.projeto_lista:
            if remove7:
                st.session_state.projeto_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()


    def _norm_tipo(s: str) -> str:
        # remove prefixo até ": " se existir
        return s.split(": ", 1)[-1] 

### USAR 1 SÓ PARA TODAS AS RESPONSABILIDADES MENSAIS ###
    from itertools import chain
    dados_dict_m = {**dados_cargos, **dados_func_c, **dados_unicos, **dados_agente}
    st.session_state.resp_mensais = [
        (tipo, data_i_rm, data_f_rm, tempo, dados_dict_m.get(_norm_tipo(tipo), 0))
        for tipo, data_i_rm, data_f_rm, tempo in chain(
            st.session_state.comissao_lista, st.session_state.func_c_lista,
            st.session_state.func_d_lista, st.session_state.agente_lista,
            st.session_state.conselho_lista, st.session_state.prioritaria_lista,
            st.session_state.projeto_lista
        )
    ]

    if any([st.session_state.comissao_lista, st.session_state.func_c_lista,
            st.session_state.func_d_lista, st.session_state.agente_lista,
            st.session_state.conselho_lista, st.session_state.prioritaria_lista,
            st.session_state.projeto_lista
        ]):
        
        total_rm = len(st.session_state.resp_mensais)

        cl0, cl1, cl2= st.columns([2,2,1])
        
        with cl0: st.write("**-Responsabilidades Mensais Registradas-**")
        with cl1: st.write(f"**Total de Responsabilidades Mensais: {total_rm}**")
        with cl2: cleared = st.button("🗑️", use_container_width=True, type='primary', key=f"{key_prefix}_clear")

        cols = st.columns(4)
        all_items = list(chain(
            st.session_state.comissao_lista, st.session_state.func_c_lista,
            st.session_state.func_d_lista, st.session_state.agente_lista,
            st.session_state.conselho_lista, st.session_state.prioritaria_lista,
            st.session_state.projeto_lista
        ))

        all_lists = ["comissao_lista", "func_c_lista", "func_d_lista", "agente_lista", "conselho_lista", "prioritaria_lista", "projeto_lista", "resp_mensais" ]

        for i, (tipo, data_i_rm, data_f_rm, tempo) in enumerate(sorted(all_items, key=lambda data: data[1])):
            col = cols[i % 4]
            with col:
                st.write(f"{tipo} por {tempo} mês(es)")
                st.write(f"Início: {data_i_rm.strftime('%d/%m/%Y')}")
                st.write(f"Fim: {data_f_rm.strftime('%d/%m/%Y')}")

        if cleared:
            for nome in all_lists:
                st.session_state[nome].clear()
            st.session_state[f"{key_prefix}_reset_fields"] = True
            st.rerun()


def build_responsabilidades_unicas(key_prefix="resp_unic"):
    """
    Renderiza inputs para 'Responsabilidades' e atualiza st.session_state.{referente_a_responsabilidade}.
    """
    st.markdown("<h3 class='left'>Pontuação Única</h3>", unsafe_allow_html=True)

    from data_utils_ueg import dados_artigo, dados_livro, dados_pesquisas, dados_registros, DECRETO_DATE

    suffixes = ["art", "liv", "pesq", "reg"]
    if st.session_state.get(f"{key_prefix}_reset_fields", False):
        for key_suffix in suffixes:
            st.session_state[f"{key_prefix}_data_{key_suffix}"] = None
            st.session_state[f"{key_prefix}_qntd_{key_suffix}"] = 0
            st.session_state[f"{key_prefix}_tipo_{key_suffix}"] = "Nenhum"
        st.session_state[f"{key_prefix}_reset_fields"] = False

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
# ---------- ARTIGOS ---------- #
        st.markdown("<h5 class='left'>Publicação de Artigos ou Pesquisas Científicos com ISSN</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3 = st.columns([2, 2, 2, 1])
        with col0:
            tipo_art = st.selectbox(
                "Faixa",
                list(dados_artigo.keys()),
                key=f"{key_prefix}_tipo_art"
            )
        with col1:
            qntd_art = st.number_input(
                "Quantidade",
                min_value=0,
                key=f"{key_prefix}_qntd_art"
            )
        with col2:
            data_publi_art = st.date_input(
                "Data de Validação",
                format="DD/MM/YYYY",
                value=None,
                min_value=st.session_state.enquadramento,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_art"
            )
        with col3:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted1 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add1", type='primary')
            with c1: remove1 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r1")

        if submitted1:
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
            
            if not data_publi_art:
                st.error("O campo 'Data de Conclusão' é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
            
            if not qntd_art: 
                st.error("O campo 'Quantidade' é obrigatório. Preencha com um valor numérico igual ou superior a 1 (um).")
            
            if tipo_art == 'Nenhum':
                st.error("Selecione um tipo de responsabilidade única válido.")
            
            if st.session_state.obrigatorios and data_publi_art and qntd_art and tipo_art != 'Nenhum':
                st.session_state.artigos_lista.append((data_publi_art, qntd_art, tipo_art))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.artigos_lista:
            if remove1:
                st.session_state.artigos_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- LIVROS ---------- #
        st.markdown("<h5 class='left'>Publicações de Livros com Corpo Editorial e ISBN</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3 = st.columns([2, 2, 2, 1])
        with col0:
            tipo_liv = st.selectbox(
                "Faixa",
                list(dados_livro.keys()),
                key=f"{key_prefix}_tipo_liv"
            )
            
        with col1:
            qntd_liv = st.number_input(
                "Quantidade",
                min_value=0,
                key=f"{key_prefix}_qntd_liv"
            )
        with col2:
            data_publi_liv = st.date_input(
                "Data de Validação",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_liv"
            )
        with col3:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted2 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add2", type='primary')
            with c1: remove2 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r2")

        if submitted2:
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
            
            if not data_publi_liv:
                st.error("O campo 'Data de Conclusão' é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
            
            if not qntd_liv: 
                st.error("O campo 'Quantidade' é obrigatório. Preencha com um valor numérico igual ou superior a 1 (um).")
            
            if tipo_liv == 'Nenhum':
                st.error("Selecione um tipo de responsabilidade única válido.")
            
            if st.session_state.obrigatorios and data_publi_liv and qntd_liv and tipo_liv != 'Nenhum':
                st.session_state.livros_lista.append((data_publi_liv, qntd_liv, tipo_liv))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.livros_lista:
            if remove2:
                st.session_state.livros_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- PESQUISAS CIENTIFICAS ---------- #
        st.markdown("<h5 class='left'>Publicações de Artigos ou Pesquisas Científicos Aprovados em Eventos Científicos</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3 = st.columns([2, 2, 2, 1])
        with col0:
            tipo_pesq = st.selectbox(
                "Faixa",
                list(dados_pesquisas.keys()),
                key=f"{key_prefix}_tipo_pesq"
            )
            
        with col1:
            qntd_pesq = st.number_input(
                "Quantidade",
                min_value=0,
                key=f"{key_prefix}_qntd_pesq"
            )
        with col2:
            data_publi_pesq = st.date_input(
                "Data de Validação",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_pesq"
            )
        with col3:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted3 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add3", type='primary')
            with c1: remove3 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r3")

        if submitted3:
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
            
            if not data_publi_pesq:
                st.error("O campo 'Data de Conclusão' é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
            
            if not qntd_pesq: 
                st.error("O campo 'Quantidade' é obrigatório. Preencha com um valor numérico igual ou superior a 1 (um).")
            
            if tipo_pesq == 'Nenhum':
                st.error("Selecione um tipo de responsabilidade única válido.")
            
            if st.session_state.obrigatorios and data_publi_pesq and qntd_pesq and tipo_pesq != 'Nenhum':
                st.session_state.pesquisas_lista.append((data_publi_pesq, qntd_pesq, tipo_pesq))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.pesquisas_lista:
            if remove3:
                st.session_state.pesquisas_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

# ---------- PATENTES E CULTIVARES ---------- #
        st.markdown("<h5 class='left'>Registro de Patente ou Cultivar</h5>", unsafe_allow_html=True)
        col0, col1, col2, col3 = st.columns([2, 2, 2, 1])
        with col0:
            tipo_reg = st.selectbox(
                "Faixa",
                list(dados_registros.keys()),
                key=f"{key_prefix}_tipo_reg"
            )
            
        with col1:
            qntd_reg = st.number_input(
                "Quantidade",
                min_value=0,
                key=f"{key_prefix}_qntd_reg"
            )
        with col2:
            data_publi_reg = st.date_input(
                "Data de Validação",
                format="DD/MM/YYYY",
                value=None,
                min_value=DECRETO_DATE,
                max_value=MAX_DATE,
                key=f"{key_prefix}_data_reg"
            )
        with col3:
            st.write("")            
            c0, c1 = st.columns([1,1])
            with c0: submitted4 = st.form_submit_button("➕", use_container_width=True, key=f"{key_prefix}_add4", type='primary')
            with c1: remove4 = st.form_submit_button("➖",use_container_width=True, key=f"{key_prefix}_r4")

        if submitted4:
            if not st.session_state.obrigatorios: 
                st.error("Adicione a 'Data de Enquadramento' e a 'Data de Início dos Pontos'.")
            
            if not data_publi_reg:
                st.error("O campo 'Data de Conclusão' é obrigatório. Preencha a data completa no formato DD/MM/AAAA (exemplo: 01/01/2025).")
            
            if not qntd_reg: 
                st.error("O campo 'Quantidade' é obrigatório. Preencha com um valor numérico igual ou superior a 1 (um).")
            
            if tipo_reg == 'Nenhum':
                st.error("Selecione um tipo de responsabilidade única válido.")
            
            if st.session_state.obrigatorios and data_publi_reg and qntd_reg and tipo_reg != 'Nenhum':
                st.session_state.registros_lista.append((data_publi_reg, qntd_reg, tipo_reg))
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()

        if st.session_state.registros_lista:
            if remove4:
                st.session_state.registros_lista.pop()
                st.session_state[f"{key_prefix}_reset_fields"] = True
                st.rerun()


### USAR 1 SÓ PARA TODAS AS RESPONSABILIDADES UNICAS ###
    from itertools import chain
    dados_dict_u = {**dados_artigo, **dados_livro, **dados_pesquisas, **dados_registros}
    st.session_state.resp_unicas = [
        (data, qntd * dados_dict_u.get(tipo, 0))
        for data, qntd, tipo in chain(
            st.session_state.artigos_lista, st.session_state.livros_lista,
            st.session_state.pesquisas_lista, st.session_state.registros_lista
        )
    ]

    if any([st.session_state.artigos_lista, st.session_state.livros_lista,
            st.session_state.pesquisas_lista, st.session_state.registros_lista
        ]):
        
        all_items = list(chain(
            st.session_state.artigos_lista, st.session_state.livros_lista,
            st.session_state.pesquisas_lista, st.session_state.registros_lista
        ))
        
        total_ru = sum(f for _, f, _ in all_items)

        cl0, cl1, cl2= st.columns([2,2,1])
        
        with cl0: st.write("**-Responsabilidades Únicas Registradas-**")
        with cl1: st.write(f"**Total de Responsabilidades Únicas: {total_ru}**")
        with cl2: cleared = st.button("🗑️", use_container_width=True, type='primary', key=f"{key_prefix}_clear")

        cols = st.columns(4)

        all_lists = ["artigos_lista", "livros_lista", "pesquisas_lista", "registros_lista", "resp_unicas"]

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


def renderizar_planilha(df:pd.DataFrame):
    st.markdown("<h2 class='center'>Detalhamento</h2>", unsafe_allow_html=True)
    st.dataframe(
        df,
        hide_index=True,
        column_config={
            "Vínculo": st.column_config.NumberColumn(format="%d") if df["Vínculo"].str.strip().ne("").all() else st.column_config.TextColumn(),
            "Data de Início dos Pontos": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Data do Enquadramento": st.column_config.DateColumn(format="DD/MM/YYYY")
        }
    )
