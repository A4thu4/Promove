import streamlit as st
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


from data_utils_ueg import DATA_CONCLUSAO, NIVEIS

def ensure_states():
    """Inicializa todos os session_states necessários"""
    from data_utils_ueg import val_states
    import copy
    for key, val in val_states.items():
        st.session_state.setdefault(key, copy.deepcopy(val))
        

def clear_states():
    """Limpa todos os valores nos session_states"""
    from data_utils_ueg import val_states
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
    from layout_ueg import ensure_states
    ensure_states()

    # ZERA todos os campos de cálculo antes de começar
    for i in range(len(carreira)):
        for j in range(1, 7):  # Zera das colunas 1 a 9
            carreira[i][j] = 0


def calcular_evolucao(data_inicial, nivel_atual, carreira, ult_evo, afastamentos, titulacoes, resp_unicas, resp_mensais):
    """
    Calcula a proxima evolução da carreira e projeta as futuras 18 evoluções possiveis
    aplicando os dados na matriz Carreira
    TODAS as pontuações são aplicadas no dia 1 do mês seguinte
    """
    if not carreira:
        return carreira, []
    elif not data_inicial:
        return carreira, []
    
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
        desconto_des = 0.08 * falta

        # Aplica pontuação padrão ou com desconto no dia 1
        if data_atual.day == 1 and data_atual != data_inicial:
            carreira[i][1] = 0.2
            carreira[i][2] = 2.4
            
            if falta > 0:
                # Aplica desconto se houver afastamento
                carreira[i][1] = max(min(0.2 - desconto, 0.2), 0)
                carreira[i][2] = max(min(2.4 - desconto_des, 2.4), 0)
            else:
                # Pontuação padrão sem desconto
                carreira[i][1] = 0.2
                carreira[i][2] = 2.4

# ---------- APLICA TITULAÇÕES ---------- #
    from data_utils_ueg import dados_tit
    
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
                    carreira[i][3] += pontos_aproveitados
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
                carreira[i][4] += pontos_aj
                total_pontos_resp += pontos_aj
                break

# ---------- APLICA RESPONSABILIDADES MENSAIS ---------- #
    rm_dict = {}
    for tipo, inicio, meses, pontos in sorted(resp_mensais, key=lambda data: data[0]):
        inicio = inicio.date() if isinstance(inicio, datetime) else inicio

        # --- Caso o início seja até 5 anos antes da data_inicial ---
        if inicio < data_inicial and inicio >= data_inicial - relativedelta(years=5):
            delta = relativedelta(data_inicial, inicio)
            meses_anteriores = delta.years * 12 + delta.months
            if meses_anteriores > 0:
                carreira[0][5] += meses_anteriores * pontos  # soma na primeira data
            # redefine início para continuar cálculo normal
            inicio = data_inicial

        # Cálculo  normal
        mes_aplicacao = inicio.month + 1
        ano_aplicacao = inicio.year
        if mes_aplicacao > 12:
            mes_aplicacao = 1
            ano_aplicacao += 1

        for _ in range(meses):
            data_aplicacao = date(ano_aplicacao, mes_aplicacao, 1)

            # calcula desconto de faltas
            mes_ant, ano_ant = mes_aplicacao - 1, ano_aplicacao
            if mes_ant < 1:
                mes_ant, ano_ant = 12, ano_aplicacao - 1
            faltas = next((f for m, f in afastamentos if m.month == mes_ant and m.year == ano_ant), 0)
            desconto = (pontos / 30) * faltas

            rm_dict[data_aplicacao] = rm_dict.get(data_aplicacao, 0) + max(0, pontos - desconto)

            mes_aplicacao += 1
            if mes_aplicacao > 12:
                mes_aplicacao = 1
                ano_aplicacao += 1

    for data_aplicacao, pts in sorted(rm_dict.items()):
        if total_pontos_resp >= LIMITE_RESP:
            break
        pts = min(pts, LIMITE_RESP - total_pontos_resp)
        for i, linha in enumerate(carreira):
            d = linha[0]
            d = d.date() if isinstance(d, datetime) else d
            if d == data_aplicacao:
                carreira[i][5] += pts
                total_pontos_resp += pts
                break

### ---------- CALCULAR ACUMULADO ---------- ###
    if ult_evo:
        pts_ultima_evolucao = ult_evo
    else:
        pts_ultima_evolucao = 0

    for i in range(DATA_CONCLUSAO):
        if i == 0:
            carreira[i][6] = sum(carreira[i][1:6]) + pts_ultima_evolucao 
        else:
            carreira[i][6] = carreira[i-1][6] + sum(carreira[i][1:6]) 

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
        pontos = carreira[i][6]

        ano = data_atual.year - data_inicio.year
        mes = data_atual.month - data_inicio.month
        meses_passados = ano * 12 + mes

        data_prevista18 = data_inicio + relativedelta(months=18)

        if data_atual < data_prevista18:
            continue
        
        # Calcula desempenho acumulado até a data atual
        desempenho_atual = 0
        
        for j in range(min(len(carreira), 1000)):
            data = carreira[j][0]
            if data.day == 1 and data <= data_atual:
                desempenho_atual += carreira[j][2]
        
        desempenho_atual = round(desempenho_atual, 2)
        
        # Verifica condições para evolução
        if data_atual >= data_prevista18:
            if pontos >= 48 and desempenho_atual >= 2.4:
                evolucao = data_atual
                implementacao = evolucao + relativedelta(day=1, months=1)
                meses_ate_evolucao = meses_passados
                pts_resto = pontos - 48
                break
    
    pendencias, motivos = False, []
    if not evolucao:
        pendencias = True
        motivos += ["pontuação mínima"]
    if desempenho_atual < 2.4:
        pendencias = True
        motivos += ["desempenho mínimo de 2.4 pontos"]

    motivo = "Não atingiu requisito de " + " e ".join(motivos) if motivos else ""

    novo_nivel = NIVEIS[NIVEIS.index(nivel_atual) + 1] if nivel_atual != 'S' else 'S'

    resultado_niveis.append({
        "Status": "Não apto a evolução" if pendencias else "Apto a evolução",
        "Observação": motivo if pendencias else "-",
        "Próximo Nível": "-" if pendencias else novo_nivel,
        "Data da Pontuação Atingida": "-" if pendencias else evolucao.strftime("%d/%m/%Y"),
        "Data da Implementação": "-" if pendencias else implementacao.strftime("%d/%m/%Y"),
        "Interstício de Evolução": "-" if pendencias else meses_ate_evolucao,
        "Pontuação Alcançada": "-" if pendencias else round(pontos, 4),
        "Pontos Excedentes": "-" if pendencias else round(pts_resto, 4),
    })

    return carreira, resultado_niveis


def calcular_planilha(arquivo):
    """Executa o cálculo múltiplo de evolução funcional a partir de planilha Excel."""
    import pandas as pd
    from planilha_utils_ueg import ler_planilha_excel, extrair_dados_basicos, processar_afastamentos, processar_responsabilidades_mensais, processar_responsabilidades_unicas, processar_titulacoes
   
    result_niveis = []
    
    df= ler_planilha_excel(arquivo)
    if df.empty:
        return
    
    st.markdown("<h2 style='text-align:center; color:#000000; '>Resultado(s) da Simulação</h2>", unsafe_allow_html=True)
    ids_processados = set()

    servidores = extrair_dados_basicos(df)
    if not servidores:
        return
    
    for i, servidor in enumerate(servidores):
        nome_servidor = servidor["Servidor"]
        cpf_servidor = servidor["CPF"]
        identificador = servidor["Vinculo"]
        nivel_atual = servidor["NivelAtual"]
        data_inicio = servidor["DataInicio"]
        DATA_FIM = servidor["DataFim"]
        pts_remanescentes = servidor["PontosExcedentes"]

        ids_processados.add(identificador)
        
        # ---------- CRIA MATRIZ BASE ----------
        carreira = [
            [data_inicio + timedelta(days=i)] + [0] * 6
            for i in range(DATA_CONCLUSAO)
        ]

        # ---------- AFASTAMENTOS AUTOMÁTICOS ----------
        afastamentos_dict = {}
        faltas_inicial = data_inicio.day - 1
        if faltas_inicial > 0:
            # Aplica faltas do mês de enquadramento no mês seguinte
            mes_aplicacao = 1 if data_inicio.month == 12 else data_inicio.month + 1
            ano_aplicacao = data_inicio.year + 1 if data_inicio.month == 12 else data_inicio.year
            data_aplicacao = date(ano_aplicacao, mes_aplicacao, 1)
            afastamentos_dict[data_aplicacao] = faltas_inicial

        # ---------- AFASTAMENTOS ----------
        carreira = processar_afastamentos(df, i, afastamentos_dict, carreira)

        # ---------- TITULAÇÕES ----------
        carreira = processar_titulacoes(df, i, carreira)

        # ---------- R.MENSAIS ----------
        carreira = processar_responsabilidades_mensais(df, i, carreira, afastamentos_dict, data_inicio, DATA_FIM)

        # ---------- R.ÚNICAS ----------
        carreira = processar_responsabilidades_unicas(df, i, carreira)

### ---------- CALCULAR ACUMULADO ---------- ###
        pts_remanescentes = float(pts_remanescentes)
        
        for i in range(DATA_CONCLUSAO):
            if i == 0:
                carreira[i][6] = sum(carreira[i][1:6]) + pts_remanescentes
            else:
                carreira[i][6] = carreira[i-1][6] + sum(carreira[i][1:6])

### ---------- CRIA DATAFRAME DE VISUALIZAÇÃO ---------- ###
        df_preview = pd.DataFrame(
            carreira,
            columns=[
                "Data",
                "Efetivo Exercício",
                "Desempenho",
                "Titulação Acadêmica",
                "R.Únicas",
                "R.Mensais",
                "Soma Total",
            ],
        )
        df_preview["Data"] = pd.to_datetime(df_preview["Data"])
        df_preview = df_preview[df_preview["Data"].dt.day == 1]
        df_preview["Data"] = df_preview["Data"].dt.strftime("%d/%m/%Y")

### ---------- CÁLCULO DE EVOLUÇÃO ---------- ###
        # Dados iniciais
        dt_inicial = carreira[0][0]  # primeira data 
        evolucao = None
        implementacao = None
        meses_ate_evo = None
        pts_resto = None
        novo_nivel = None

        for i in range(DATA_CONCLUSAO):
            dt_atual = carreira[i][0]
            pts_loop = carreira[i][6]

            meses_passados = (dt_atual.year - dt_inicial.year) * 12 + (dt_atual.month - dt_inicial.month)
            data_prevista18 = dt_inicial + relativedelta(months=18)

            if dt_atual < data_prevista18:
                continue
            
            # Calcula desempenho e aperfeicoamento acumulados até a data atual
            desempenho_atual = 0
            
            for j in range(min(len(carreira), 1000)):
                data = carreira[j][0]
                if data.day == 1 and data <= dt_atual:
                    desempenho_atual += carreira[j][2]
            
            desempenho_atual = round(desempenho_atual, 2)

            if dt_atual >= data_prevista18: 
                if pts_loop >= 48 and desempenho_atual >= 2.4:
                    evolucao = dt_atual
                    implementacao = evolucao + relativedelta(day=1, months=1)
                    meses_ate_evo = meses_passados
                    pts_resto = pts_loop - 48
                    break
        
        pendencias, motivos = False, []
        if not evolucao:
            pendencias = True
            motivos += ["pontuação mínima"]
        if desempenho_atual < 2.4:
            pendencias = True
            motivos += ["desempenho mínimo de 2.4 pontos"]

        motivo = "Não atingiu requisito de " + " e ".join(motivos) if motivos else ""
        
        novo_nivel = NIVEIS[NIVEIS.index(nivel_atual) + 1] if nivel_atual != 'S' else 'S'
        identificador = int(float(identificador))

        result_niveis.append({
            "Status": "Não apto a evolução" if pendencias else "Apto a evolução",
            "Observação": motivo if pendencias else "-",
            "Servidor": nome_servidor,
            "CPF": cpf_servidor,
            "Vínculo": identificador,
            "Próximo Nível": "-" if pendencias else novo_nivel,
            "Data da Pontuação Atingida": "-" if pendencias else evolucao.strftime("%d/%m/%Y"),
            "Data da Implementação": "-" if pendencias else implementacao.strftime("%d/%m/%Y"),
            "Interstício de Evolução": "-" if pendencias else meses_ate_evo,
            "Pontuação Alcançada": "-" if pendencias else round(pts_loop, 4),
            "Pontos Excedentes": "-" if pendencias else round(pts_resto, 4),
        })
        
    df_results = pd.DataFrame(result_niveis)
    st.dataframe(df_results, hide_index=True, column_config={"Vínculo": st.column_config.NumberColumn(format="%d")})

    if len(ids_processados) == 1:
        st.markdown("<h3 style='text-align:center;'>Pontuações Mensais</h3>", unsafe_allow_html=True)
        st.dataframe(df_preview.head(240), hide_index=True)

    import io
    excel_buffer = io.BytesIO()
    df_results.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    c1, c2, c3 = st.columns([2, 2, 1])
    with c2:
        st.download_button(
            label="Exportar Resultados para Excel",
            data=excel_buffer.getvalue(),
            file_name="Resultado Evoluções.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
