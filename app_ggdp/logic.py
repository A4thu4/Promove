import streamlit as st
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from data_utils import DATA_CONCLUSAO, NIVEIS

def ensure_states():
    """Inicializa todos os session_states necessários"""
    from data_utils import val_states
    import copy
    for key, val in val_states.items():
        st.session_state.setdefault(key, copy.deepcopy(val))
        

def clear_states():
    """Limpa todos os valores nos session_states"""
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
            st.session_state[key] = default_val

        
def zerar_carreira(carreira):
    from layout import ensure_states
    ensure_states()

    # ZERA todos os campos de cálculo antes de começar
    for i in range(len(carreira)):
        for j in range(1, 8):  # Zera das colunas 1 a 9
            carreira[i][j] = 0


def calcular_evolucao(data_inicial, nivel_atual, carreira, ult_evo, afastamentos, aperfeicoamentos, titulacoes, resp_unicas, resp_mensais):
    """
    Calcula a proxima evolução da carreira e projeta as futuras 18 evoluções possiveis
    aplicando os dados na matriz Carreira
    TODAS as pontuações são aplicadas no dia 1 do mês seguinte
    """
    if not carreira:
        return carreira, [], []
    elif not data_inicial:
        st.error("Sem data de Inicio.")
        return carreira, [], []
    
    zerar_carreira(carreira)

# ---------- APLICA AFASTAMENTOS ---------- #
    afastamentos_dict = {}
    for mes, faltas in sorted(afastamentos, key=lambda data: data[0]):
        mes = mes.date() if isinstance(mes, datetime) else mes
        
        # Calcula data de aplicação (dia 1 do mês seguinte)
        if mes.month == 12:
            data_aplicacao = date(mes.year + 1, 1, 1)
        else:
            data_aplicacao = date(mes.year, mes.month + 1, 1)
        
        if data_aplicacao in afastamentos_dict:
            afastamentos_dict[data_aplicacao] += faltas
        else:
            afastamentos_dict[data_aplicacao] = faltas

    # Aplica os afastamentos nas datas correspondentes
    for i in range(len(carreira)):
        data_atual = carreira[i][0]
        data_atual = data_atual.date() if isinstance(data_atual, datetime) else data_atual
        
        # Verifica se há afastamento para aplicar nesta data
        falta = afastamentos_dict.get(data_atual, 0)

        desconto = 0.0067 * falta
        desconto_des = 0.05 * falta

        # Aplica pontuação padrão ou com desconto no dia 1
        if data_atual.day == 1 and data_atual != data_inicial:
            carreira[i][1] = 0.2
            carreira[i][2] = 1.5
            
            if falta > 0:
                # Aplica desconto se houver afastamento
                carreira[i][1] = max(min(0.2 - desconto, 0.2), 0)
                carreira[i][2] = max(min(1.5 - desconto_des, 1.5), 0)
            else:
                # Pontuação padrão sem desconto
                carreira[i][1] = 0.2
                carreira[i][2] = 1.5

# ---------- APLICA APERFEIÇOAMENTOS ---------- #
    total_horas = 0
    pontos_excedentes = 0
    for data_conclusao, horas_curso in sorted(aperfeicoamentos, key=lambda data: data[0]):
        data_conclusao = data_conclusao.date() if isinstance(data_conclusao, datetime) else data_conclusao

        # Achar dia 1
        if data_conclusao.month == 12:
            data_aplicacao = date(data_conclusao.year + 1, 1, 1)
        else:
            data_aplicacao = date(data_conclusao.year, data_conclusao.month + 1, 1)

        # Quanto desse curso ainda pode ser aproveitado
        horas_restantes = max(0, 100 - total_horas)
        horas_aproveitadas = min(horas_curso, horas_restantes)
        horas_excedentes = max(0, horas_curso - horas_aproveitadas)

        # Atualiza acumulado de horas
        total_horas += horas_aproveitadas

        # Só calcula pontos se ainda tiver horas aproveitáveis (máx 100h)
        if horas_aproveitadas > 0:
            pontos = horas_aproveitadas * 0.09
            # Encontra a linha na matriz carreira e insere os pontos
            for idx, linha in enumerate(carreira):
                data_linha = linha[0]
                data_linha = data_linha.date() if isinstance(data_linha, datetime) else data_linha
                if data_linha == data_aplicacao:
                    carreira[idx][3] += pontos
                    break
        
        # Se passar de 100h, adiciona os pontos excedentes aos remanescentes do usuário
        if horas_excedentes > 0:
            pontos_excedentes = horas_excedentes * 0.09

# ---------- APLICA TITULAÇÕES ---------- #
    from data_utils import dados_tit
    
    total_pontos_tit = 0
    ultima_titulacao = None
    LIMITE_TIT = 144
    
    for data_concl, tipo in sorted(titulacoes, key=lambda data: data[0]):
        data_concl = data_concl.date() if isinstance(data_concl, datetime) else data_concl

        # Bloqueia se já teve uma titulação nos últimos 12 meses (dupla confirmação)
        if ultima_titulacao and data_concl < (ultima_titulacao + relativedelta(months=12)):
            continue # Ignora esta titulação

        # Achar dia 1
        if data_concl.month == 12:
            data_aplicacao = date(data_concl.year + 1, 1, 1)
        else:
            data_aplicacao = date(data_concl.year, data_concl.month + 1, 1)

        pontos_titulo = dados_tit.get(tipo, 0)
        pontos_restantes = max(0, LIMITE_TIT - total_pontos_tit)
        pontos_aproveitados = min(pontos_titulo, pontos_restantes)
        
        total_pontos_tit += pontos_aproveitados
        ultima_titulacao = data_concl

        if pontos_aproveitados > 0:
            for i, linha in enumerate(carreira):
                d = linha[0]
                d = d.date() if isinstance(d, datetime) else d
                if d == data_aplicacao:
                    carreira[i][4] += pontos_aproveitados
                    break

# ---------- APLICA RESPONSABILIDADES ÚNICAS ---------- #
    total_pontos_resp = 0
    LIMITE_RESP = 144

    ru_dict = {}
    for data, pontos in sorted(resp_unicas, key=lambda data: data[0]):
        data = data.date() if isinstance(data, datetime) else data

        # Achar dia 1
        if data.month == 12:
            data_aplicacao = date(data.year + 1, 1, 1)
        else:
            data_aplicacao = date(data.year, data.month + 1, 1)

        if data_aplicacao in ru_dict:
            ru_dict[data_aplicacao] += pontos
        else:
            ru_dict[data_aplicacao] = pontos

    for data_aplicacao in sorted(ru_dict.keys()):
        pts = ru_dict[data_aplicacao]

        # Não ultrapassar limite
        if total_pontos_resp + pts > LIMITE_RESP:
            pontos_aj = max(0, LIMITE_RESP - total_pontos_resp)
        else:
            pontos_aj = pts
        
        if pontos_aj <= 0:
            continue

        # Encontra a linha correspondente na carreira
        for i, linha in enumerate(carreira):
            d = linha[0]
            d = d.date() if isinstance(d, datetime) else d
            
            if d == data_aplicacao:
                carreira[i][5] += pontos_aj
                total_pontos_resp += pontos_aj
                break

# ---------- APLICA RESPONSABILIDADES MENSAIS ---------- #
    for tipo, inicio, meses, pontos in sorted(resp_mensais, key=lambda data: data[0]):
        # garante que seja datetime.date
        inicio = inicio.date() if isinstance(inicio, datetime) else inicio

        # Caso o início seja até 5 anos antes da data_inicial
        if inicio < data_inicial and inicio >= data_inicial - relativedelta(years=5):
            # Quantos meses retroativos até a data_inicial
            delta = relativedelta(data_inicial, inicio)
            meses_anteriores = delta.years * 12 + delta.months
            if meses_anteriores > 0:
                # Soma todos os pontos retroativos na primeira linha da carreira
                carreira[0][6] += meses_anteriores * pontos

        # primeiro mês de aplicação é o mês seguinte
        mes_aplicacao = inicio.month + 1
        ano_aplicacao = inicio.year
        if mes_aplicacao > 12:
            mes_aplicacao = 1
            ano_aplicacao += 1

        for _ in range(meses):
            # calcula a data do dia 1 do mês atual
            data_aplicacao = date(ano_aplicacao, mes_aplicacao, 1)

            # aplica na carreira
            for i, linha in enumerate(carreira):
                d = linha[0]
                d = d.date() if isinstance(d, datetime) else d
                if d == data_aplicacao:
                    # pega falta do mês anterior
                    mes_anterior = mes_aplicacao - 1
                    ano_anterior = ano_aplicacao
                    if mes_anterior < 1:
                        mes_anterior = 12
                        ano_anterior -= 1

                    falta = next((faltas for mes, faltas in afastamentos
                                if mes.month == mes_anterior and mes.year == ano_anterior), 0)
                    
                    desconto = (pontos / 30) * falta

                    # verifica limite
                    if total_pontos_resp + (pontos - desconto) > LIMITE_RESP:
                        pontos_aj = max(0, LIMITE_RESP - total_pontos_resp)
                    else:
                        pontos_aj = pontos - desconto

                    if pontos_aj > 0:
                        carreira[i][6] += pontos_aj
                        total_pontos_resp += pontos_aj
                    break

            # avança para o próximo mês
            mes_aplicacao += 1
            if mes_aplicacao > 12:
                mes_aplicacao = 1
                ano_aplicacao += 1

### ---------- CALCULAR ACUMULADO ---------- ###
    if ult_evo:
        pts_ultima_evolucao = ult_evo
    else:
        pts_ultima_evolucao = 0

    for i in range(DATA_CONCLUSAO):
        if i == 0:
            carreira[i][7] = sum(carreira[i][1:7]) + pts_ultima_evolucao 
        else:
            carreira[i][7] = carreira[i-1][7] + sum(carreira[i][1:7]) 

### ---------- CÁLCULO DE TEMPO DA 1º EVOLUÇÃO ---------- ###
    resultado_niveis = []

    # Dados iniciais
    data_inicio = data_inicial  # primeira data 
    evolucao = None
    implementacao = None
    meses_ate_evolucao = None
    pts_resto = None
    novo_nivel = None

    for i in range(DATA_CONCLUSAO):
        data_atual = carreira[i][0]
        pontos = carreira[i][7]

        ano = data_atual.year - data_inicio.year
        mes = data_atual.month - data_inicio.month
        meses_passados = ano * 12 + mes

        data_prevista18 = data_inicio + relativedelta(months=18)
        data_prevista12 = data_inicio + relativedelta(months=12)
        
        if data_atual < data_prevista12:
            continue
        
        if data_prevista12 <= data_atual < data_prevista18 :
            if pontos >= 96:
                evolucao = data_atual
                implementacao = evolucao + relativedelta(day=1, months=1)
                meses_ate_evolucao = meses_passados
                pts_resto = pontos - 48
                break

        if data_atual >= data_prevista18:
            if pontos >= 48:
                evolucao = data_atual
                implementacao = evolucao + relativedelta(day=1, months=1)
                meses_ate_evolucao = meses_passados
                pts_resto = pontos - 48
                break
        
    desempenho, aperfeicoamento = 0, 0
    for linha in carreira:
        data = linha[0]
        if data <= evolucao:
            desempenho += linha[2] 
            aperfeicoamento += linha[3]

    desempenho = round(desempenho,4) if evolucao else 0
    aperfeicoamento = round(aperfeicoamento,4) if evolucao else 0
    
    pendencias = False
    motivos = []

    if not evolucao:
        pendencias = True
        motivos.append("Pontuação mínima.")
    if aperfeicoamento < 5.4:
        pendencias = True
        motivos.append("Aperfeiçoamento mínimo de 60 horas.")
    if desempenho < 2.4:
        pendencias = True
        motivos.append("Desempenho mínimo de 2.4 pontos.")

    motivo = "Não atingiu requisito de " + " e ".join(motivos) if motivos else ""

    novo_nivel = NIVEIS[NIVEIS.index(nivel_atual) + 1] if nivel_atual != 'S' else 'S'

    if pendencias:
        resultado_niveis.append({
            "Status": "Não apto a evoluir",
            "Observação": motivo,
            "Próximo Nível": "-",
            "Data da Pontuação Atingida": "-",
            "Data da Implementação": "-",
            "Interstício de Evolução": "-",
            "Pontuação Alcançada": "-",
            "Pontos Excedentes": "-"
        })
    else:
        resultado_niveis.append({
            "Status": "Apto a evoluir",
            "Observação": "-",
            "Próximo Nível": novo_nivel,
            "Data da Pontuação Atingida": evolucao.strftime("%d/%m/%Y"),
            "Data da Implementação": implementacao.strftime("%d/%m/%Y"),
            "Interstício de Evolução": meses_ate_evolucao,
            "Pontuação Alcançada": pontos,
            "Pontos Excedentes": round(pts_resto, 4)
        })
    
### ---------- CÁLCULO DE TEMPO DA PROJEÇÃO DE 18 EVOLUÇÕES---------- ###
    resultado_projecao = []
    
    # só projeta se houve uma evolução válida
    if not resultado_niveis or resultado_niveis[0]["Status"] != "Apto a evoluir":
        return carreira, resultado_niveis, resultado_projecao

    data_inicio = datetime.strptime(
        resultado_niveis[0]["Data da Implementação"], "%d/%m/%Y"
    ).date()
    pts_resto = float(resultado_niveis[0]["Pontos Excedentes"])
    nivel_atual = resultado_niveis[0]["Próximo Nível"]

    meses_totais = resultado_niveis[0]["Interstício de Evolução"]  # inicia do 1º ciclo

    for ciclo in range(2,19):
        if nivel_atual == "S":
            break

        pontos_ciclo = pts_resto
        pts_resto = 0.0
        data_base = data_inicio
        evolucao = None
        meses_ate_evolucao = None

        for i in range(len(carreira)):
            data_atual = carreira[i][0]
            if data_atual <= data_base:
                continue

            delta = relativedelta(data_atual, data_base)
            meses_passados = delta.years * 12 + delta.months
            pontos_ciclo += (
                carreira[i][1] + carreira[i][2] + carreira[i][3]
                + carreira[i][4] + carreira[i][5] + carreira[i][6]
            )

            data_prevista12 = data_base + relativedelta(months=12)
            data_prevista18 = data_base + relativedelta(months=18)

            if data_prevista12 <= data_atual < data_prevista18:
                if pontos_ciclo >= 96:
                    evolucao = data_atual
                    meses_ate_evolucao = meses_passados
                    pts_resto = pontos_ciclo - 48
                    break

            if data_atual >= data_prevista18:
                if pontos_ciclo >= 48:
                    evolucao = data_atual
                    meses_ate_evolucao = meses_passados
                    pts_resto = pontos_ciclo - 48
                    break

        if not evolucao:
            break

        implementacao = evolucao + relativedelta(day=1, months=1)
        meses_totais += meses_ate_evolucao  # acumula o total de tempo

        anos_total = meses_totais // 12
        resto_total = meses_totais % 12

        proximo_nivel = (
            NIVEIS[NIVEIS.index(nivel_atual) + 1]
            if nivel_atual != "S"
            else "S"
        )

        resultado_projecao.append({
            "Nível": proximo_nivel,
            "Evolução (Projeção)": f" {ciclo}ª Evolução",
            "Data Inicial": data_inicio.strftime("%d/%m/%Y"),
            "Data Alcançada": evolucao.strftime("%d/%m/%Y"),
            "Meses Entre Níveis": meses_ate_evolucao,
            "Pontuação Alcançada": round(pontos_ciclo, 3),
            "Total": f"{anos_total} ano(s) {resto_total} mês(es)"
        })

        data_inicio = implementacao
        nivel_atual = proximo_nivel

    return carreira, resultado_niveis, resultado_projecao


def calcular_planilha(arquivo):
    import numpy as np
    import pandas as pd
    import openpyxl as px

    result_niveis = []
    
    arq = px.load_workbook(arquivo, data_only=True)  
    aba = arq.active  # pega a aba ativa
    
    # pega os valores das células
    data = list(aba.values)

    # primeira linha = cabeçalho
    colunas = data[1]
    valores = data[2:]
    
    # cria DataFrame
    df = pd.DataFrame(valores, columns=colunas)
    df = df.drop_duplicates()
    df = df.replace([None, np.nan], '')

    # Remove linhas completamente vazias ou com dados inválidos
    colunas_validas = ["Servidor", "CPF", "Cód. Vinculo", "Nível Atual", "Data de Enquadramento ou Última Evolução"]
    st.markdown("<h2 style='text-align:center; color:#000000; '>Detalhamento</h2>", unsafe_allow_html=True)
    
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
            <strong>⚠️ Caso os dados 'Obrigátorios' de algum servidor não tenha sido preenchido corretamente na planilha ele não será cálculado. </strong>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Função para verificar valores válidos
    def limpar_coluna(serie):
        return (
            serie.notna()
            & (serie.astype(str).str.strip().str.lower() != "none")
            & (serie.astype(str).str.strip() != "")
        )

    # Filtrar linhas que têm todas as colunas válidas
    for col in colunas_validas:
        df = df[limpar_coluna(df[col])]
    
    # Converter ID para string e remover duplicatas baseadas no ID
    df["Cód. Vinculo"] = df["Cód. Vinculo"].astype(str).str.strip()
    df = df.drop_duplicates(subset=["Cód. Vinculo"], keep="first")
    df["Data de Enquadramento ou Última Evolução"] = pd.to_datetime(df["Data de Enquadramento ou Última Evolução"], errors="coerce")

    df.columns = [str(c).strip() if not pd.isna(c) else "" for c in df.columns]

    st.dataframe(
        df.head(),
        hide_index=True,
        column_config={
            "Cód. Vinculo": st.column_config.NumberColumn(format="%d"),
            "Data de Enquadramento ou Última Evolução": st.column_config.DateColumn(format="DD/MM/YYYY")
        }
    )
    st.markdown("<h2 style='text-align:center; color:#000000; '>Resultado(s) da Simulação</h2>", unsafe_allow_html=True)
    
    ids_processados = set()
    for i in range (len(df)):
        nome_servidor = df['Servidor'].iloc[i]
        cpf_servidor = df['CPF'].iloc[i]
        identificador = df["Cód. Vinculo"].iloc[i]
        nivel_atual = df["Nível Atual"].iloc[i]
        
        if any(pd.isna(v) or str(v).strip().lower() in ('none', 'nat', 'nan', 'null', '') 
                for v in [nome_servidor, cpf_servidor, identificador, nivel_atual]):
            continue

        ids_processados.add(identificador)
        
        data_inicio = df["Data de Enquadramento ou Última Evolução"].iloc[i].date()

        faltas_inicial = 0
        if data_inicio:
            faltas_inicial = data_inicio.day - 1
            if faltas_inicial > 0:
                # aplica as faltas do início no mês de enquadramento
                data_aplicacao = date(data_inicio.year, data_inicio.month+1, 1)
                afastamentos_dict = {data_aplicacao: faltas_inicial}
            else:
                afastamentos_dict = {}
        else:
            afastamentos_dict = {}
                
        DATA_FIM = data_inicio + relativedelta(years=20)
        
        carreira = [
            [data_inicio + timedelta(days=i)] + [0] * 7
            for i in range(DATA_CONCLUSAO)
        ]
        
        pts_remanescentes = df["Pontos Última Evolução"].iloc[i]
        if pts_remanescentes in ('None', 'NaT', 'Nan','', None): 
            pts_remanescentes = 0
        pts_remanescentes = float(pts_remanescentes)
        pts_remanescentes = round(pts_remanescentes, 4) if pts_remanescentes else 0

        mes_falta = str(df["Mês"].iloc[i])
        mes_falta = mes_falta.split(';')
        qntd_faltas = str(df["N° de faltas"].iloc[i]).split(';')

        mes_curso = str(df["Datas de Conclusão"].iloc[i])
        mes_curso = mes_curso.split(';')
        hrs_curso = str(df["Carga Horaria"].iloc[i])
        hrs_curso = hrs_curso.split(';')

        mes_tit = str(df["Data de Conclusao"].iloc[i])
        mes_tit = mes_tit.split(';')
        tipo_tit = df["Tipo"].iloc[i].split(';')
        
        artigos = df["Artigos"].iloc[i].split(';')
        livros = df["Livros"].iloc[i].split(';')
        pesquisas = df["Pesquisas"].iloc[i].split(';')
        registros = df["Registros"].iloc[i].split(';')
        cursos = df["Cursos"].iloc[i].split(';')
        
        art_id, art_nid = [], []
        for art in artigos:
            partes = art.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            numero, tipo, data = partes[0], partes[1], partes[2]
            numero = int(numero)
            
            if tipo == 'ID':
                art_id.append((numero,data))
            elif tipo == 'NID':
                art_nid.append((numero,data))
            elif tipo not in ('ID','NID'):
                st.error("Erro de Codigo em Artigos")

        lv_org, lv_cap, lv_comp = [], [], []
        for lv in livros:
            partes = lv.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            numero, tipo, data = partes[0], partes[1], partes[2]
            numero = int(numero)
            
            if tipo == 'O':
                lv_org.append((numero,data))
            elif tipo == 'C':
                lv_cap.append((numero,data))
            elif tipo == 'L':
                lv_comp.append((numero,data))
            elif tipo not in ('O','C','L'):
                st.error("Erro de Codigo em Livros")

        pesq_est, pesq_reg, pesq_nac, pesq_int = [], [], [], []
        for pesq in pesquisas:
            partes = pesq.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            numero, tipo, data = partes[0], partes[1], partes[2]
            numero = int(numero)
            
            if tipo == 'E':
                pesq_est.append((numero,data))
            elif tipo == 'R':
                pesq_reg.append((numero,data))
            elif tipo == 'N':
                pesq_nac.append((numero,data))
            elif tipo == 'I':
                pesq_int.append((numero,data))
            elif tipo not in ('E','R','N','I'):
                st.error("Erro de Codigo em Pesquisas")
        
        reg_pat, reg_cult = [], []
        for reg in registros:
            partes = reg.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado-

            numero, tipo, data = partes[0], partes[1], partes[2]
            numero = int(numero)
            
            if tipo == 'P':
                reg_pat.append((numero,data))
            elif tipo == 'C':
                reg_cult.append((numero,data))
            elif tipo not in ('P','C'):
                st.error("Erro de Codigo em Registros")

        doc_1, doc_2, doc_3, doc_4, doc_5 = [], [], [], [], []
        pt_curso = {
            'P1': 6,   
            'P2': 8,   
            'P3': 12,  
            'P4': 24,
            'P5': 48 
        }
        for doc in cursos:
            partes = doc.split('-')
            if len(partes) < 2:
                continue  # pula se não tiver o formato esperado

            tipo, data = partes[0], partes[1]
            
            if tipo == 'P1':
                doc_1.append((pt_curso.get(tipo, 0),data))
            elif tipo == 'P2':
                doc_2.append((pt_curso.get(tipo, 0),data))
            elif tipo == 'P3':
                doc_3.append((pt_curso.get(tipo, 0),data))
            elif tipo == 'P4':
                doc_4.append((pt_curso.get(tipo, 0),data))
            elif tipo == 'P5':
                doc_5.append((pt_curso.get(tipo, 0),data))
            elif tipo not in ('P1','P2','P3','P4','P5',''):
                st.error("Erro de Codigo em Cursos")

        c_comissao = df["C.Comissão"].iloc[i].split(';')
        f_comissionada = df["F.Comissionada"].iloc[i].split(';')
        f_designada = df["F.Designada"].iloc[i].split(';')
        a_agente = df["A.Agente"].iloc[i].split(';')
        a_conselho = df["A.Conselho"].iloc[i].split(';')
        a_prioritaria = df["A.Prioritária"].iloc[i].split(';')
        
        resp_c_comissao = []
        pt_cargos = {
            "DAS1": 1.000, "DAS2": 1.000,
            "DAS3": 0.889, "DAS4": 0.889,
            "DAS5": 0.800, "DAS6": 0.800, "DAS7": 0.800, "DAID1A": 0.800, "AEG": 0.800,
            "DAI1": 0.667, "DAID1": 0.667, "DAID1B": 0.667, "DAID2": 0.667, "AE1": 0.667, "AE2": 0.667,
            "DAI2": 0.500, "DAI3": 0.500, "DAID3": 0.500, "DAID4": 0.500, "DAID5": 0.500, "DAID6": 0.500, "DAID7": 0.500,
            "DAID8": 0.500, "DAID9": 0.500, "DAID10": 0.500, "DAID11": 0.500, "DAID12": 0.500,
            "DAID13": 0.500, "DAID14": 0.500
        }
        for cargo in c_comissao:
            partes = cargo.split('-')
            if len(partes) < 2:
                continue  # pula se não tiver o formato esperado

            tipo, data_i, data_f = partes[0], partes[1], partes[2]
            
            if tipo in list(pt_cargos.keys()):
                resp_c_comissao.append((tipo, data_i, data_f))
            elif tipo not in list(pt_cargos.keys()):
                st.error("Erro de Codigo em C.Comissão")
            
        resp_f_comissionada = []
        pt_func_c = {
            "T1": 0.333, 
            "T2": 0.364, 
            "T3": 0.400, 
            "T4": 0.444,  
            "T5": 0.500
        }
        for func in f_comissionada:
            partes = func.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            tipo, data_i, data_f = partes[0], partes[1], partes[2]
            
            if tipo in list(pt_func_c.keys()):
                resp_f_comissionada.append((tipo,data_i,data_f))
            elif tipo not in list(pt_func_c.keys()):
                st.error("Erro de Codigo em F.Comissionada")

        resp_f_designada = []
        for func in f_designada:
            partes = func.split('-')
            if len(partes) < 2:
                continue  # pula se não tiver o formato esperado

            data_i, data_f = partes[0], partes[1]
            
            if data_i and data_f is not None:
                resp_f_designada.append((data_i,data_f))
            
        resp_a_agente = []
        pt_agente = {
            "I": 0.333, 
            "II": 0.364, 
            "III": 0.400, 
            "IV": 0.444,  
            "V": 0.500
        }
        for at in a_agente:
            partes = at.split('-')
            if len(partes) < 3:
                continue  # pula se não tiver o formato esperado

            tipo, data_i, data_f = partes[0], partes[1], partes[2]
            
            if tipo in list(pt_agente.keys()):
                resp_a_agente.append((tipo,data_i,data_f))
            elif tipo not in list(pt_agente.keys()):
                st.error("Erro de Codigo em A.Agente")

        resp_a_conselho = []
        for func in a_conselho:
            partes = func.split('-')
            if len(partes) < 2:
                continue  # pula se não tiver o formato esperado

            data_i, data_f = partes[0], partes[1]
            
            if data_i and data_f is not None:
                resp_a_conselho.append((data_i,data_f))
            

        resp_a_prioritaria = []
        for func in a_prioritaria:
            partes = func.split('-')
            if len(partes) < 2:
                continue  # pula se não tiver o formato esperado

            data_i, data_f = partes[0], partes[1]
            
            if data_i and data_f is not None:
                resp_a_prioritaria.append((data_i,data_f))

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        # ---------- APLICA AFASTAMENTOS ---------- #
        for mes_str, falta_str in zip(mes_falta, qntd_faltas):
            if mes_str and falta_str:  
                mes_date = pd.to_datetime(mes_str, dayfirst=False, errors="coerce").date()
                faltas_int = int(float(falta_str))
                
            # Calcula data de aplicação (dia 1 do mês seguinte)
            if mes_date.month == 12:
                data_aplicacao = date(mes_date.year + 1, 1, 1)
            else:
                data_aplicacao = date(mes_date.year, mes_date.month + 1, 1)
            
            if data_aplicacao in afastamentos_dict:
                afastamentos_dict[data_aplicacao] += faltas_int
            else:
                afastamentos_dict[data_aplicacao] = faltas_int

        # Aplica os afastamentos nas datas correspondentes
        for i in range(len(carreira)):
            data_atual = carreira[i][0]
            
            # Verifica se há afastamento para aplicar nesta data
            falta = afastamentos_dict.get(data_atual, 0)

            desconto = 0.0067 * falta
            desconto_des = 0.05 * falta

            # Aplica pontuação padrão ou com desconto no dia 1 
            if data_atual.day == 1 and data_atual != data_inicio:
                carreira[i][1] = 0.2  
                carreira[i][2] = 1.5  
                
                if falta > 0:
                    # Aplica desconto se houver afastamento
                    carreira[i][1] = max(min(0.2 - desconto, 0.2), 0)
                    carreira[i][2] = max(min(1.5 - desconto_des, 1.5), 0)
                else:
                    # Pontuação padrão sem desconto
                    carreira[i][1] = 0.2
                    carreira[i][2] = 1.5

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        # ---------- APLICA APERFEIÇOAMENTOS ---------- #
        total_horas = 0
        pontos_excedentes = 0
        for mes_str, horas_str in zip(mes_curso, hrs_curso):
            if mes_str.strip() and horas_str.strip():  
                data_conclusao = pd.to_datetime(mes_str, dayfirst=True, errors="coerce").date()
                horas_curso_val = int(horas_str.strip())
                
                # Calcula data de aplicação (dia 1 do mês seguinte) - IGUAL À calcular_evolucao
                if data_conclusao.month == 12:
                    data_aplicacao = date(data_conclusao.year + 1, 1, 1)
                else:
                    data_aplicacao = date(data_conclusao.year, data_conclusao.month + 1, 1)

                # Quanto desse curso ainda pode ser aproveitado
                horas_restantes = max(0, 100 - total_horas)
                horas_aproveitadas = min(horas_curso_val, horas_restantes)
                horas_excedentes = max(0, horas_curso_val - horas_aproveitadas)

                total_horas += horas_aproveitadas

                if horas_aproveitadas > 0:
                    pontos = horas_aproveitadas * 0.09
                    # Encontra a linha na matriz carreira e insere os pontos
                    for idx, linha in enumerate(carreira):
                        if linha[0] == data_aplicacao:
                            carreira[idx][3] += pontos  # Coluna 3 = Aperfeiçoamento
                            break
                
                # Se passar de 100h, adiciona os pontos excedentes aos remanescentes do usuário
                if horas_excedentes > 0:
                    pontos_excedentes = horas_excedentes * 0.09

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        # ---------- APLICA TITULAÇÕES ---------- #
        valores_tit = {
            'Nenhuma': 0,
            'Graduação': 6,
            'Especialização': 8,
            'Mestrado': 24,
            'Doutorado': 48
        }
        
        total_pontos_tit = 0
        ultima_titulacao = None
        LIMITE_TIT = 144
        
        for mes_str, tipo_str in zip(mes_tit, tipo_tit):
            if mes_str.strip() and tipo_str.strip():
                data_concl = pd.to_datetime(mes_str, dayfirst=True, errors="coerce").date()
                tipo = str(tipo_str.strip())
                
                # Bloqueia se já teve uma titulação nos últimos 12 meses (dupla confirmação)
                if ultima_titulacao and data_concl < (ultima_titulacao + relativedelta(months=12)):
                    continue # Ignora esta titulação

                # Calcula data de aplicação (dia 1 do mês seguinte)
                if data_concl.month == 12:
                    data_aplicacao = date(data_concl.year + 1, 1, 1)
                else:
                    data_aplicacao = date(data_concl.year, data_concl.month + 1, 1)

                pontos_titulo = valores_tit.get(tipo, 0)
                pontos_restantes = max(0, LIMITE_TIT - total_pontos_tit)
                pontos_aproveitados = min(pontos_titulo, pontos_restantes)
                
                total_pontos_tit += pontos_aproveitados
                ultima_titulacao = data_concl
                
                if pontos_aproveitados > 0:
                    for i, linha in enumerate(carreira):
                        if linha[0] == data_aplicacao:
                            carreira[i][4] += pontos_aproveitados  # Coluna 4 = Titulação
                            break

####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        LIMITE_RESP = 144
        pts_acumulado_ru = 0
        resp_u_dict = {}

### ---------- ARTIGOS ---------- ###
        st.session_state.artigos_lista_pl = []
        for numero, data_dt in art_id:
            st.session_state.artigos_lista_pl.append((numero, 0, data_dt))  
        for numero, data_dt in art_nid:
            st.session_state.artigos_lista_pl.append((0, numero, data_dt)) 
        
        # Agrupar por data e aplicar limite
        for art_id, nid, data_art in st.session_state.artigos_lista_pl:
            if nid is not None and nid != 0:
                pontos = nid * 0.5 
            if art_id is not None and art_id != 0:
                pontos = art_id * 3

            data_orig = datetime.strptime(data_art, "%d/%m/%Y").date()
    
            # Calcula data de aplicação (dia 1 do mês seguinte)
            if data_orig.month == 12:
                data_aplicacao = date(data_orig.year + 1, 1, 1)
            else:
                data_aplicacao = date(data_orig.year, data_orig.month + 1, 1)

            if data_aplicacao in resp_u_dict:
                resp_u_dict[data_aplicacao] += pontos
            else:
                resp_u_dict[data_aplicacao] = pontos
            
### ---------- LIVROS ---------- ##
        st.session_state.livros_lista_pl = []
        for numero, data_dt in lv_org:
            st.session_state.livros_lista_pl.append((numero, 0, 0, data_dt))  
        for numero, data_dt in lv_cap:
            st.session_state.livros_lista_pl.append((0, numero, 0, data_dt))  
        for numero, data_dt in lv_comp:
            st.session_state.livros_lista_pl.append((0, 0, numero, data_dt)) 
        
        # Agrupar por data e aplicar limite
        for org, cap, comp, data_lv in st.session_state.livros_lista_pl:
            if org is not None and org != 0:
                pontos = org * 1
            if cap is not None and cap != 0:
                pontos = cap * 3
            if comp is not None and comp != 0:
                pontos = comp * 6

            data_orig = datetime.strptime(data_lv, "%d/%m/%Y").date()
    
            # Calcula data de aplicação (dia 1 do mês seguinte)
            if data_orig.month == 12:
                data_aplicacao = date(data_orig.year + 1, 1, 1)
            else:
                data_aplicacao = date(data_orig.year, data_orig.month + 1, 1)

            if data_aplicacao in resp_u_dict:
                resp_u_dict[data_aplicacao] += pontos
            else:
                resp_u_dict[data_aplicacao] = pontos

### ---------- PESQUISAS ---------- ###
        st.session_state.pesq_lista_pl = []
        for numero, data_dt in pesq_est:
            st.session_state.pesq_lista_pl.append((numero, 0, 0, 0, data_dt))  
        for numero, data_dt in pesq_reg:
            st.session_state.pesq_lista_pl.append((0, numero, 0, 0, data_dt))  
        for numero, data_dt in pesq_nac:
            st.session_state.pesq_lista_pl.append((0, 0, numero, 0, data_dt)) 
        for numero, data_dt in pesq_int:
            st.session_state.pesq_lista_pl.append((0, 0, 0, numero, data_dt)) 

        # Agrupar por data e aplicar limite
        for est, reg, nac, inter, data_pesq in st.session_state.pesq_lista_pl:
            if est is not None and est != 0:
                pontos = est * 1
            if reg is not None and reg != 0:
                pontos = reg * 2
            if nac is not None and nac != 0:
                pontos = nac * 3
            if inter is not None and inter != 0:
                pontos = inter * 4

            data_orig = datetime.strptime(data_pesq, "%d/%m/%Y").date()

            # Calcula data de aplicação (dia 1 do mês seguinte)
            if data_orig.month == 12:
                data_aplicacao = date(data_orig.year + 1, 1, 1)
            else:
                data_aplicacao = date(data_orig.year, data_orig.month + 1, 1)

            if data_aplicacao in resp_u_dict:
                resp_u_dict[data_aplicacao] += pontos
            else:
                resp_u_dict[data_aplicacao] = pontos
           
### ---------- REGISTROS ---------- ###
        st.session_state.reg_lista_pl = []
        for numero, data_dt in reg_pat:
            st.session_state.reg_lista_pl.append((numero, 0, data_dt))  
        for numero, data_dt in reg_cult:
            st.session_state.reg_lista_pl.append((0, numero, data_dt))  
            
        # Agrupar por data e aplicar limite
        for pat, cult, data_reg in st.session_state.reg_lista_pl:
            if pat is not None and pat != 0:
                pontos = pat * 6
            if cult is not None and cult != 0:
                pontos = cult * 6
            
            data_orig = datetime.strptime(data_reg, "%d/%m/%Y").date()
    
            # Calcula data de aplicação (dia 1 do mês seguinte)
            if data_orig.month == 12:
                data_aplicacao = date(data_orig.year + 1, 1, 1)
            else:
                data_aplicacao = date(data_orig.year, data_orig.month + 1, 1)

            if data_aplicacao in resp_u_dict:
                resp_u_dict[data_aplicacao] += pontos
            else:
                resp_u_dict[data_aplicacao] = pontos

### ---------- CURSOS ---------- ###
        st.session_state.cursos_lista_pl = []
        for tipo, data_dt in doc_1:
            st.session_state.cursos_lista_pl.append((tipo, data_dt))  
        for tipo, data_dt in doc_2:
            st.session_state.cursos_lista_pl.append((tipo, data_dt))  
        for tipo, data_dt in doc_3:
            st.session_state.cursos_lista_pl.append((tipo, data_dt)) 
        for tipo, data_dt in doc_4:
            st.session_state.cursos_lista_pl.append((tipo, data_dt)) 
        for tipo, data_dt in doc_5:
            st.session_state.cursos_lista_pl.append((tipo, data_dt)) 

        # Agrupar por data e aplicar limite
        for tipo, data_doc in st.session_state.cursos_lista_pl:
            if tipo is not None and tipo != 0:
                pontos = tipo

            data_orig = datetime.strptime(data_doc, "%d/%m/%Y").date()
    
            # Calcula data de aplicação (dia 1 do mês seguinte)
            if data_orig.month == 12:
                data_aplicacao = date(data_orig.year + 1, 1, 1)
            else:
                data_aplicacao = date(data_orig.year, data_orig.month + 1, 1)

            if data_aplicacao in resp_u_dict:
                resp_u_dict[data_aplicacao] += pontos
            else:
                resp_u_dict[data_aplicacao] = pontos
        
# ---------- APLICA RESPONSABILIDADES ÚNICAS---------- #
        for data_aplicacao, pontos in sorted(resp_u_dict.items(), key=lambda data: data[0]):
            if pts_acumulado_ru + pontos > LIMITE_RESP:
                pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
            else:
                pontos_aj = pontos
            
            if pontos_aj <= 0:
                continue
            
            # Aplicar na matriz carreira 
            for i, linha in enumerate(carreira):
                d = linha[0]
                if d == data_aplicacao:
                    carreira[i][5] += pontos_aj
                    pts_acumulado_ru += pontos_aj
                    break
        
### ---------- C.COMISSÃO ---------- ###
        st.session_state.comissao_lista_pl = []
        for tipo, data_i, data_f in resp_c_comissao:
            data_dti = pd.to_datetime(data_i, dayfirst=True).date()
            data_dtf = pd.to_datetime(data_f, dayfirst=True).date() if data_f != 'SF' else DATA_FIM
            
            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            
            st.session_state.comissao_lista_pl.append((tipo, data_dti, qntd_meses))
        
        for cargo_c in st.session_state.comissao_lista_pl:
            inicio = cargo_c[1]
            pontos = pt_cargos.get(cargo_c[0], 0)
            meses = cargo_c[2]

            inicio = pd.to_datetime(inicio, dayfirst=True).date()
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                falta = 0
                falta += next((faltas for mes, faltas in afastamentos_dict.items()
                                    if d.month == mes.month and d.year == mes.year), 0)

                desconto = (pontos/30) * falta

                # verifica limite
                if pts_acumulado_ru + (pontos - desconto) > LIMITE_RESP:
                    pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
                else:
                    pontos_aj = pontos - desconto

                if d.day == 1 and d != data_inicio:
                    carreira[i][6] += pontos_aj
                    pts_acumulado_ru += pontos_aj
                

### ---------- F.COMISSIONADA ---------- ###
        st.session_state.func_c_lista_pl = []
        for tipo, data_i, data_f in resp_f_comissionada:
            data_dti = pd.to_datetime(data_i, dayfirst=True).date()
            data_dtf = pd.to_datetime(data_f, dayfirst=True).date() if data_f != 'SF' else DATA_FIM
            
            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            
            st.session_state.func_c_lista_pl.append((tipo, data_dti, qntd_meses))

        for func_c in st.session_state.func_c_lista_pl:
            inicio = func_c[1]
            pontos = pt_func_c.get(func_c[0], 0)
            meses = func_c[2]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                falta = 0
                falta += next((faltas for mes, faltas in afastamentos_dict.items()
                                    if d.month == mes.month and d.year == mes.year), 0)

                desconto = (pontos/30) * falta

                # verifica limite
                if pts_acumulado_ru + (pontos - desconto) > LIMITE_RESP:
                    pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
                else:
                    pontos_aj = pontos - desconto

                if d.day == 1 and d != data_inicio:
                    carreira[i][6] += pontos_aj
                    pts_acumulado_ru += pontos_aj
                

### ---------- F.DESIGNADA ---------- ###
        st.session_state.func_d_lista_pl = []
        for data_i, data_f in resp_f_designada:
            data_dti = pd.to_datetime(data_i, dayfirst=True).date()
            data_dtf = pd.to_datetime(data_f, dayfirst=True).date() if data_f != 'SF' else DATA_FIM

            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            
            st.session_state.func_d_lista_pl.append((data_dti, qntd_meses))

        for func_d in st.session_state.func_d_lista_pl:
            inicio = func_d[0]
            pontos = 0.333
            meses = func_d[1]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                falta = 0
                falta += next((faltas for mes, faltas in afastamentos_dict.items()
                                    if d.month == mes.month and d.year == mes.year), 0)

                desconto = (pontos/30) * falta

                # verifica limite
                if pts_acumulado_ru + (pontos - desconto) > LIMITE_RESP:
                    pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
                else:
                    pontos_aj = pontos - desconto

                if d.day == 1 and d != data_inicio:
                    carreira[i][6] += pontos_aj
                    pts_acumulado_ru += pontos_aj
                

### ---------- A.AGENTE ---------- ###
        st.session_state.agente_lista_pl = []
        for tipo, data_i, data_f in resp_a_agente:
            data_dti = pd.to_datetime(data_i, dayfirst=True).date()
            data_dtf = pd.to_datetime(data_f, dayfirst=True).date() if data_f != 'SF' else DATA_FIM
            
            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            
            st.session_state.agente_lista_pl.append((tipo, data_dti, qntd_meses))

        for at_agente in st.session_state.agente_lista_pl:
            inicio = at_agente[1]
            pontos = pt_agente.get(at_agente[0], 0)
            meses = at_agente[2]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                falta = 0
                falta += next((faltas for mes, faltas in afastamentos_dict.items()
                                    if d.month == mes.month and d.year == mes.year), 0)

                desconto = (pontos/30) * falta

                # verifica limite
                if pts_acumulado_ru + (pontos - desconto) > LIMITE_RESP:
                    pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
                else:
                    pontos_aj = pontos - desconto

                if d.day == 1 and d != data_inicio:
                    carreira[i][6] += pontos_aj
                    pts_acumulado_ru += pontos_aj
                

### ---------- A.CONSELHO ---------- ###
        st.session_state.a_conselho_lista_pl = []
        for data_i, data_f in resp_a_conselho:
            data_dti = pd.to_datetime(data_i, dayfirst=True).date()
            data_dtf = pd.to_datetime(data_f, dayfirst=True).date() if data_f != 'SF' else DATA_FIM

            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            
            st.session_state.a_conselho_lista_pl.append((data_dti, qntd_meses))

        for at_conselho in st.session_state.a_conselho_lista_pl:
            inicio = at_conselho[0]
            pontos = 0.333
            meses = at_conselho[1]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                falta = 0
                falta += next((faltas for mes, faltas in afastamentos_dict.items()
                                    if d.month == mes.month and d.year == mes.year), 0)

                desconto = (pontos/30) * falta

                # verifica limite
                if pts_acumulado_ru + (pontos - desconto) > LIMITE_RESP:
                    pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
                else:
                    pontos_aj = pontos - desconto

                if d.day == 1 and d != data_inicio:
                    carreira[i][6] += pontos_aj
                    pts_acumulado_ru += pontos_aj
                

### ---------- A.PRIORITARIA ---------- ###
        st.session_state.a_prioritaria_lista_pl = []
        for data_i, data_f in resp_a_prioritaria:
            data_dti = pd.to_datetime(data_i, dayfirst=True).date()
            data_dtf = pd.to_datetime(data_f, dayfirst=True).date() if data_f != 'SF' else DATA_FIM

            delta_ano = data_dtf.year - data_dti.year
            delta_mes = data_dtf.month - data_dti.month
            qntd_meses = delta_ano * 12 + delta_mes
            
            st.session_state.a_prioritaria_lista_pl.append((data_dti, qntd_meses))

        for at_prioritaria in st.session_state.a_prioritaria_lista_pl:
            inicio = at_prioritaria[0]
            pontos = 0.333
            meses = at_prioritaria[1]
            
            for i in range(len(carreira)):
                d = carreira[i][0]
                
                falta = 0
                falta += next((faltas for mes, faltas in afastamentos_dict.items()
                                    if d.month == mes.month and d.year == mes.year), 0)

                desconto = (pontos/30) * falta

                # verifica limite
                if pts_acumulado_ru + (pontos - desconto) > LIMITE_RESP:
                    pontos_aj = max(0, LIMITE_RESP - pts_acumulado_ru)
                else:
                    pontos_aj = pontos - desconto

                if d.day == 1 and d != data_inicio:
                    carreira[i][6] += pontos_aj
                    pts_acumulado_ru += pontos_aj
                
        
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        pts_remanescentes = int(pts_remanescentes)
        
        for i in range(DATA_CONCLUSAO):
            if i == 0:
                carreira[i][7] = sum(carreira[i][1:7]) + pts_remanescentes
            else:
                carreira[i][7] = carreira[i-1][7] + sum(carreira[i][1:7])
####------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------####
        df_preview = pd.DataFrame(
                carreira,
                columns=['Data', 'Efetivo Exercício', 'Desempenho', 'Aperfeiçoamentos', 'Titulação Acadêmica', 'R.Únicas', 'R.Mensais', 'Soma Total']
            )
        df_preview['Data'] = pd.to_datetime(df_preview['Data'])
        df_preview = df_preview[df_preview['Data'].dt.day == 1]
        df_preview['Data'] = df_preview['Data'].dt.strftime('%d/%m/%Y')

### ---------- RESULTADOS ---------- ###
        # Dados iniciais
        dt_inicial = carreira[0][0]  # primeira data 
        evo = None
        implem = None
        meses_ate_evo = None
        pts_resto = None
        novo_nivel = None

        for i in range(DATA_CONCLUSAO):            
            dt_atual = carreira[i][0]
            pts_loop = carreira[i][7]

            ano_loop = dt_atual.year - dt_inicial.year
            mes_loop = dt_atual.month - dt_inicial.month
            meses_passados = ano_loop * 12 + mes_loop

            data_prevista12 = dt_inicial + relativedelta(months=12)
            data_prevista18 = dt_inicial + relativedelta(months=18)

            if dt_atual < data_prevista12:
                continue

            if data_prevista12 <= dt_atual < data_prevista18 :
                if pts_loop >= 96:     
                    evo = dt_atual
                    implem = evo + relativedelta(day=1, months=1)
                    meses_ate_evo = meses_passados
                    pts_resto = pts_loop - 48
                    break

            if dt_atual >= data_prevista18:
                if pts_loop >= 48:
                    evo = dt_atual
                    implem = evo + relativedelta(day=1, months=1)
                    meses_ate_evo = meses_passados
                    pts_resto = pts_loop - 48
                    break
            
        desempenho, aperfeicoamento = 0, 0
        for linha in carreira:
            data = linha[0]
            if data <= evo:
                desempenho += linha[2] 
                aperfeicoamento += linha[3]

        desempenho = round(desempenho,4) if evo else 0
        aperfeicoamento = round(aperfeicoamento,4) if evo else 0

        pendencias = False
        motivos = []

        if not evo:
            pendencias = True
            motivos.append("Pontuação mínima.")
        if aperfeicoamento < 5.4:
            pendencias = True
            motivos.append("Aperfeiçoamento mínimo de 60 horas.")
        if desempenho < 2.4:
            pendencias = True
            motivos.append("Desempenho mínimo de 2.4 pontos.")

        motivo = "Não atingiu requisito de " + " e ".join(motivos) if motivos else ""
        
        novo_nivel = NIVEIS[NIVEIS.index(nivel_atual) + 1] if nivel_atual != 'S' else 'S'
        identificador = int(float(identificador))

        if pendencias:
            result_niveis.append({
                "Status": "Não apto a evolução",
                "Observação": motivo,
                "Servidor": nome_servidor,
                "CPF": cpf_servidor,
                "Cód. Vinculo": identificador,
                "Próximo Nível": "-",
                "Data da Pontuação Atingida": "-",
                "Data da Implementação": "-",
                "Interstício de Evolução": "-",
                "Pontuação Alcançada": "-",
                "Pontos Excedentes": "-"
            })
        else:
            result_niveis.append({
                "Status": "Apto a evolução",
                "Observação": "-",
                "Servidor": nome_servidor,
                "CPF": cpf_servidor,
                "Cód. Vinculo": identificador,
                "Próximo Nível": novo_nivel,
                "Data da Pontuação Atingida": evo.strftime("%d/%m/%Y"),
                "Data da Implementação": implem.strftime("%d/%m/%Y"),
                "Interstício de Evolução": meses_ate_evo,
                "Pontuação Alcançada": round(pts_loop, 4),
                "Pontos Excedentes": round(pts_resto, 4)
            })
        
    df_results = pd.DataFrame(result_niveis)
    st.dataframe(
        df_results, 
        hide_index=True,
        column_config={
            "Cód. Vinculo": st.column_config.NumberColumn(format="%d")
        }    
    )

    if len(ids_processados) == 1:
        st.markdown("<h3 style='text-align:center; color:#000000; '>Pontuações Mensais</h3>", unsafe_allow_html=True)
        st.dataframe(df_preview.head(240), hide_index=True)

    import io 
    excel_buffer = io.BytesIO()
    df_results.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)

    c1, c2, c3 = st.columns([2, 2, 1])
    with c2:
        st.write("")
        st.download_button(
            label="Exportar Resultados para Excel",
            data=excel_buffer.getvalue(),
            file_name="Resultado Evoluções.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )
