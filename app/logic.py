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
    rm_dict = {}
    for tipo, inicio, meses, pontos in sorted(resp_mensais, key=lambda data: data[0]):
        inicio = inicio.date() if isinstance(inicio, datetime) else inicio

        # --- Caso o início seja até 5 anos antes da data_inicial ---
        if inicio < data_inicial and inicio >= data_inicial - relativedelta(years=5):
            delta = relativedelta(data_inicial, inicio)
            meses_anteriores = delta.years * 12 + delta.months
            if meses_anteriores > 0:
                carreira[0][6] += meses_anteriores * pontos  # soma na primeira data
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
            falta = next((f for m, f in afastamentos if m.month == mes_ant and m.year == ano_ant), 0)
            desconto = (pontos / 30) * falta

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
                carreira[i][6] += pts
                total_pontos_resp += pts
                break

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
        
        # Calcula desempenho e aperfeicoamento acumulados até a data atual
        desempenho_atual = 0
        aperfeicoamento_atual = 0
        
        for j in range(min(len(carreira), 1000)):
            data = carreira[j][0]
            if data.day == 1 and data <= data_atual:
                desempenho_atual += carreira[j][2]
                aperfeicoamento_atual += carreira[j][3]
        
        desempenho_atual = round(desempenho_atual, 2)
        aperfeicoamento_atual = round(aperfeicoamento_atual, 2)
        
        # Verifica condições para evolução
        if data_prevista12 <= data_atual < data_prevista18:
            if pontos >= 96 and desempenho_atual >= 2.4 and aperfeicoamento_atual >= 5.4:
                evolucao = data_atual
                implementacao = evolucao + relativedelta(day=1, months=1)
                meses_ate_evolucao = meses_passados
                pts_resto = pontos - 48
                break

        if data_atual >= data_prevista18:
            if pontos >= 48 and desempenho_atual >= 2.4 and aperfeicoamento_atual >= 5.4:
                evolucao = data_atual
                implementacao = evolucao + relativedelta(day=1, months=1)
                meses_ate_evolucao = meses_passados
                pts_resto = pontos - 48
                break
    
    pendencias, motivos = False, []
    if not evolucao:
        pendencias = True
        motivos.append("pontuação mínima")
    if aperfeicoamento_atual < 5.4:
        pendencias = True
        motivos.append("aperfeiçoamento mínimo de 60 horas")
    if desempenho_atual < 2.4:
        pendencias = True
        motivos.append("desempenho mínimo de 2.4 pontos")

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
    
### ---------- CÁLCULO DE TEMPO DA PROJEÇÃO DE 18 EVOLUÇÕES---------- ###
    resultado_projecao = []
    
    # # só projeta se houve uma evolução válida
    # if not resultado_niveis or resultado_niveis[0]["Status"] != "Apto a evoluir":
    #     return carreira, resultado_niveis, resultado_projecao

    # data_inicio = datetime.strptime(
    #     resultado_niveis[0]["Data da Implementação"], "%d/%m/%Y"
    # ).date()
    # pts_resto = float(resultado_niveis[0]["Pontos Excedentes"])
    # nivel_atual = resultado_niveis[0]["Próximo Nível"]

    # meses_totais = resultado_niveis[0]["Interstício de Evolução"]  # inicia do 1º ciclo

    # for ciclo in range(2,19):
    #     if nivel_atual == "S":
    #         break

    #     pontos_ciclo = pts_resto
    #     pts_resto = 0.0
    #     data_base = data_inicio
    #     evolucao = None
    #     meses_ate_evolucao = None

    #     for i in range(len(carreira)):
    #         data_atual = carreira[i][0]
    #         if data_atual <= data_base:
    #             continue

    #         delta = relativedelta(data_atual, data_base)
    #         meses_passados = delta.years * 12 + delta.months
    #         pontos_ciclo += (
    #             carreira[i][1] + carreira[i][2] + carreira[i][3]
    #             + carreira[i][4] + carreira[i][5] + carreira[i][6]
    #         )

    #         data_prevista12 = data_base + relativedelta(months=12)
    #         data_prevista18 = data_base + relativedelta(months=18)

    #         if data_prevista12 <= data_atual < data_prevista18:
    #             if pontos_ciclo >= 96:
    #                 evolucao = data_atual
    #                 meses_ate_evolucao = meses_passados
    #                 pts_resto = pontos_ciclo - 48
    #                 break

    #         if data_atual >= data_prevista18:
    #             if pontos_ciclo >= 48:
    #                 evolucao = data_atual
    #                 meses_ate_evolucao = meses_passados
    #                 pts_resto = pontos_ciclo - 48
    #                 break

    #     if not evolucao:
    #         break

    #     implementacao = evolucao + relativedelta(day=1, months=1)
    #     meses_totais += meses_ate_evolucao  # acumula o total de tempo

    #     anos_total = meses_totais // 12
    #     resto_total = meses_totais % 12

    #     proximo_nivel = (
    #         NIVEIS[NIVEIS.index(nivel_atual) + 1]
    #         if nivel_atual != "S"
    #         else "S"
    #     )

    #     resultado_projecao.append({
    #         "Nível": proximo_nivel,
    #         "Evolução (Projeção)": f" {ciclo}ª Evolução",
    #         "Data Inicial": data_inicio.strftime("%d/%m/%Y"),
    #         "Data Alcançada": evolucao.strftime("%d/%m/%Y"),
    #         "Meses Entre Níveis": meses_ate_evolucao,
    #         "Pontuação Alcançada": round(pontos_ciclo, 3),
    #         "Total": f"{anos_total} ano(s) {resto_total} mês(es)"
    #     })

    #     data_inicio = implementacao
    #     nivel_atual = proximo_nivel

    return carreira, resultado_niveis, resultado_projecao


def calcular_planilha(arquivo):
    """Executa o cálculo múltiplo de evolução funcional a partir de planilha Excel."""
    import pandas as pd
    from planilha_utils import ler_planilha_excel, extrair_dados_basicos, processar_afastamentos, processar_aperfeicoamentos, processar_responsabilidades_mensais, processar_responsabilidades_unicas, processar_titulacoes
   
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
            [data_inicio + timedelta(days=i)] + [0] * 7
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

        # ---------- APERFEIÇOAMENTOS ----------
        carreira = processar_aperfeicoamentos(df, i, carreira)

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
                carreira[i][7] = sum(carreira[i][1:7]) + pts_remanescentes
            else:
                carreira[i][7] = carreira[i-1][7] + sum(carreira[i][1:7])

### ---------- CRIA DATAFRAME DE VISUALIZAÇÃO ---------- ###
        df_preview = pd.DataFrame(
            carreira,
            columns=[
                "Data",
                "Efetivo Exercício",
                "Desempenho",
                "Aperfeiçoamentos",
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
            pts_loop = carreira[i][7]

            meses_passados = (dt_atual.year - dt_inicial.year) * 12 + (dt_atual.month - dt_inicial.month)
            data_prevista12 = dt_inicial + relativedelta(months=12)
            data_prevista18 = dt_inicial + relativedelta(months=18)

            if dt_atual < data_prevista12:
                continue
            
            # Calcula desempenho e aperfeicoamento acumulados até a data atual
            desempenho_atual = 0
            aperfeicoamento_atual = 0
            
            for j in range(min(len(carreira), 1000)):
                data = carreira[j][0]
                if data.day == 1 and data <= dt_atual:
                    desempenho_atual += carreira[j][2]
                    aperfeicoamento_atual += carreira[j][3]
            
            desempenho_atual = round(desempenho_atual, 2)
            aperfeicoamento_atual = round(aperfeicoamento_atual, 2)

            # Verifica condições para evolução
            if data_prevista12 <= dt_atual < data_prevista18: 
                if pts_loop >= 96 and desempenho_atual >= 2.4 and aperfeicoamento_atual >= 5.4:
                    evolucao = dt_atual
                    implementacao = evolucao + relativedelta(day=1, months=1)
                    meses_ate_evo = meses_passados
                    pts_resto = pts_loop - 48
                    break

            if dt_atual >= data_prevista18: 
                if pts_loop >= 48 and desempenho_atual >= 2.4 and aperfeicoamento_atual >= 5.4:
                    evolucao = dt_atual
                    implementacao = evolucao + relativedelta(day=1, months=1)
                    meses_ate_evo = meses_passados
                    pts_resto = pts_loop - 48
                    break

        # Se não encontrou evolução, recalcula os totais até o final do período
        if not evolucao:
            desempenho_atual = 0
            aperfeicoamento_atual = 0
            
            for j in range(min(len(carreira), 1000)):
                data = carreira[j][0]
                if data.day == 1 and data <= carreira[-1][0]:  # até a última data disponível
                    desempenho_atual += carreira[j][2]
                    aperfeicoamento_atual += carreira[j][3]
            
            desempenho_atual = round(desempenho_atual, 2)
            aperfeicoamento_atual = round(aperfeicoamento_atual, 2)
        
        pendencias, motivos = False, []
        if not evolucao:
            pendencias, motivos = True, ["Pontuação mínima."]
        if aperfeicoamento_atual < 5.4:
            pendencias, motivos = True, motivos + ["Aperfeiçoamento mínimo de 60 horas."]
        if desempenho_atual < 2.4:
            pendencias, motivos = True, motivos + ["Desempenho mínimo de 2.4 pontos."]

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

