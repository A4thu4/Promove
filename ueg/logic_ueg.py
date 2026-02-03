from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from data_utils_ueg import DATA_CONCLUSAO, NIVEIS
        
def zerar_carreira(carreira):
    # ZERA todos os campos de cálculo antes de começar
    for i in range(len(carreira)):
        for j in range(1, 7):  # Zera das colunas 1 a 8
            carreira[i][j] = 0


def calcular_evolucao(enquadramento, data_inicial, nivel_atual, carreira, ult_evo, afastamentos, titulacoes, resp_unicas, resp_mensais, apo_especial:bool):
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

    # --- Dias anteriores à Data de Início (faltas automáticas) só para Efetivo/Desempenho ---
    # Importante: essas faltas NÃO devem afetar Responsabilidades (nem normal, nem retro).
    data_aplic_auto = None
    faltas_inicial = 0
    if data_inicial:
        faltas_inicial = data_inicial.day - 1
        if faltas_inicial > 0:
            # aplica no 1º dia do mês seguinte
            if data_inicial.month == 12:
                data_aplic_auto = date(data_inicial.year + 1, 1, 1)
            else:
                data_aplic_auto = date(data_inicial.year, data_inicial.month + 1, 1)

            afastamentos_dict[data_aplic_auto] = afastamentos_dict.get(data_aplic_auto, 0) + faltas_inicial

    # ----------- AFASTAMENTOS PARA RESPONSABILIDADES (remove só o automático) -----------
    # Mantém todos os afastamentos informados (inclusive em período retroativo),
    afastamentos_dict_resp = dict(afastamentos_dict)
    if data_aplic_auto and data_aplic_auto in afastamentos_dict_resp:
        afastamentos_dict_resp[data_aplic_auto] -= faltas_inicial
        if afastamentos_dict_resp[data_aplic_auto] <= 0:
            del afastamentos_dict_resp[data_aplic_auto]


    # Aplica os afastamentos nas datas correspondentes
    for i in range(len(carreira)):
        data_atual = carreira[i][0]
        data_atual = data_atual.date() if isinstance(data_atual, datetime) else data_atual
        
        falta = afastamentos_dict.get(data_atual, 0)

        desconto = 0.0067 * falta
        desconto_des = 0.06 * falta

        if data_atual.day == 1 and data_atual != data_inicial:
            carreira[i][1] = 0.2
            carreira[i][2] = 1.8
            
            if falta > 0:
                carreira[i][1] = max(min(0.2 - desconto, 0.2), 0)
                carreira[i][2] = max(min(1.8 - desconto_des, 1.8), 0)
            else:
                carreira[i][1] = 0.2
                carreira[i][2] = 1.8

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

        if total_pontos_resp + pts > LIMITE_RESP:
            pontos_aj = max(0, LIMITE_RESP - total_pontos_resp)
        else:
            pontos_aj = pts
        
        if pontos_aj <= 0:
            continue

        for i, linha in enumerate(carreira):
            d = linha[0]
            d = d.date() if isinstance(d, datetime) else d
            
            if d == data_aplicacao:
                carreira[i][4] += pontos_aj
                total_pontos_resp += pontos_aj
                break

# ---------- APLICA RESPONSABILIDADES MENSAIS ---------- #
    from collections import defaultdict

    # Mapeamento dos tipos para grupos reais
    GRUPO_REAL = {
        "C. Comissão": "G1",        # I → só 1 no mês
        "F. Comissionada": "G1",    # II → só 1 no mês
        "F. Designada": "G1",       # III → só 1 no mês

        "At. Agente": "G2",         # IV → até 2 no mês
        "At. Conselho": "G3",       # V  → até 2 no mês
        "Ex. Projeto": "G4",        # VII  → até 2 no mês

        "At. Prioritária": "G5"     # VI → só 1 no mês (mas não pertence ao G1)
    }

    # limites de cada grupo dentro do mesmo mês
    LIMITES_GRUPO = {
        "G1": 1,    # I + II + III competem → só uma entrada
        "G2": 2,    # IV → duas maiores
        "G3": 2,    # V  → duas maiores
        "G4": 2,    # VII → duas maiores
        "G5": 1     # VI → só uma
    }

    # rm_bruto guarda: data -> grupo -> lista de pontos já descontados
    rm_bruto = defaultdict(lambda: defaultdict(list))
    retro_bruto = defaultdict(lambda: defaultdict(list))
    
    # Ordena pela data de início 
    for tipo, inicio_resp, fim_resp, tempo, pontos in sorted(resp_mensais, key=lambda data: data[1]):
        inicio_resp = inicio_resp.date() if isinstance(inicio_resp, datetime) else inicio_resp
        inicio_resp = date(inicio_resp.year, inicio_resp.month, inicio_resp.day)

        fim_resp = fim_resp.date() if isinstance(fim_resp, datetime) else fim_resp
        fim_resp = date(fim_resp.year, fim_resp.month, fim_resp.day)

        # extrai o tipo-base ("C. Comissão: DAS-1" → "C. Comissão")
        tipo_base = tipo.split(":", 1)[0].strip()
        g = GRUPO_REAL.get(tipo_base)
        if not g:
            continue

        # --- Retroativo: até 5 anos antes da data do enquadramento ---
        if g == "G1" and inicio_resp < enquadramento:
            inicio_limite = max(inicio_resp, enquadramento - relativedelta(years=5))
            fim_limite = min(fim_resp, enquadramento - relativedelta(days=1))

            mes_cursor = date(inicio_limite.year, inicio_limite.month, 1)

            while mes_cursor <= fim_limite:
                # limites reais dentro do mês
                inicio_mes = max(inicio_limite, mes_cursor)
                ultimo_dia_mes = (mes_cursor + relativedelta(months=1)) - timedelta(days=1)
                fim_mes = min(fim_limite, ultimo_dia_mes)

                if inicio_mes <= fim_mes:
                    dias_mes = (ultimo_dia_mes - mes_cursor).days + 1
                    dias_trabalhados = (fim_mes - inicio_mes).days + 1

                    proporcao = dias_trabalhados / dias_mes
                    pts_base = pontos * proporcao

                    faltas = afastamentos_dict_resp.get(mes_cursor, 0)
                    desconto = (pontos / 30.0) * faltas
                    pts_final = max(0.0, pts_base - desconto)

                    # GUARDA SÓ A MAIOR G1 DO MÊS
                    retro_bruto[mes_cursor][g].append(pts_final)

                mes_cursor += relativedelta(months=1)

        # se toda a responsabilidade foi consumida no retroativo, vai pra proxima resp
        if fim_resp < enquadramento:
            continue
        
        if inicio_resp < enquadramento:
            inicio_resp = enquadramento

        # mês seguinte ao início
        mes_cursor = date(inicio_resp.year, inicio_resp.month, 1)
        
        while mes_cursor <= fim_resp:
            # A data de aplicação é sempre o mês seguinte (M+1)
            data_aplicacao = mes_cursor + relativedelta(months=1)
            
            # 1. Definir o intervalo trabalhado dentro do mês de competência
            inicio_efetivo = max(inicio_resp, mes_cursor)
            ultimo_dia_mes = (mes_cursor + relativedelta(months=1)) - timedelta(days=1)
            fim_efetivo = min(fim_resp, ultimo_dia_mes)

            if inicio_efetivo <= fim_efetivo:
                # 2. Cálculo Proporcional (Caso 2)
                dias_mes = (ultimo_dia_mes - mes_cursor).days + 1
                dias_trabalhados = (fim_efetivo - inicio_efetivo).days + 1
                
                proporcao = dias_trabalhados / dias_mes
                pts_base = pontos * proporcao

                # 3. Desconto de faltas (na data de aplicação M+1)
                faltas = afastamentos_dict_resp.get(data_aplicacao, 0)
                desconto = (pontos / 30.0) * faltas
                pts_aj = max(0.0, pts_base - desconto)

                # 4. Adiciona no grupo para consolidação
                rm_bruto[data_aplicacao][g].append(pts_aj)
            
            # Avança para o próximo mês de competência
            mes_cursor += relativedelta(months=1)

    # ---------- CONSOLIDAÇÃO RETROATIVA  ---------- #
    retro_total = 0.0
    for data_mes, grupos in retro_bruto.items():
        for g, valores in grupos.items():
            limite = LIMITES_GRUPO[g]
            valores_ordenados = sorted(valores, reverse=True)
            retro_total  += sum(valores_ordenados[:limite])
    
    # ---------- APLICA RETRO SOBRE A CARREIRA (RESPEITA LIMITE_RESP) ---------- #
    if retro_total > 0:
        retro_aj = min(retro_total, LIMITE_RESP - total_pontos_resp)
        carreira[0][5] += retro_aj
        total_pontos_resp += retro_aj

    # ---------- CONSOLIDAÇÃO COM LIMITES POR GRUPO ---------- #
    rm_dict = {}
    for data_aplicacao, grupos in rm_bruto.items():
        total_mes = 0.0
        for g, valores in grupos.items():
            limite = LIMITES_GRUPO[g]
            valores_ordenados = sorted(valores, reverse=True)
            total_mes += sum(valores_ordenados[:limite])
        rm_dict[data_aplicacao] = total_mes

    # ---------- APLICA SOBRE A CARREIRA (RESPEITA LIMITE_RESP) ---------- #
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

        meses_passados = (data_atual.year - data_inicio.year) * 12 + (data_atual.month - data_inicio.month)

        data_prevista18 = data_inicio + relativedelta(months=18)
        data_prevista15 = data_inicio + relativedelta(months=15)

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
        if data_atual >= (data_prevista15 if apo_especial else data_prevista18):
            if pontos >= 48:
                evolucao = data_atual
                implementacao = evolucao + relativedelta(day=1, months=1)
                meses_ate_evolucao = meses_passados
                pts_resto = pontos - 48
                break
    
    pendencias, motivos = False, []
    mot = ""
    if not evolucao:
        pendencias = True
        motivos += ["obrigatórios"]
    if apo_especial:
        mot = "Aposentadoria Especial"
    
    if desempenho_atual < 2.4:
        pendencias = True
        motivos += ["de desempenho mínimo de 2.4 pontos"]

    if pendencias and motivos:
        motivo =( ((mot + ". ") if mot else "") + "Não atingiu requisito(s) " + " e ".join(motivos) )
    elif mot:
        motivo = mot
    else:
        motivo = "-"

    novo_nivel = NIVEIS[NIVEIS.index(nivel_atual) + 1] if nivel_atual != 'S' else 'S'

    resultado_niveis.append({
        "Status": "Não apto a evolução" if pendencias else "Apto a evolução",
        "Observação": motivo,
        "Próximo Nível": "-" if pendencias else novo_nivel,
        "Data da Pontuação Atingida": "-" if pendencias else evolucao.strftime("%d/%m/%Y"),
        "Data da Implementação": "-" if pendencias else implementacao.strftime("%d/%m/%Y"),
        "Interstício de Evolução": "-" if pendencias else meses_ate_evolucao,
        "Pontuação Alcançada": "-" if pendencias else f"{pontos:.2f}",
        "Pontos Excedentes": "-" if pendencias else f"{pts_resto:.2f}",
    })

    return carreira, resultado_niveis


def calcular_planilha(arquivo, apo_especial_m:bool):
    """Executa o cálculo múltiplo de evolução funcional a partir de planilha Excel."""
    import pandas as pd
    from planilha_utils_ueg import ler_planilha_excel, extrair_dados_basicos, processar_afastamentos, processar_responsabilidades_mensais, processar_responsabilidades_unicas, processar_titulacoes
   
    result_niveis = []
    
    df = ler_planilha_excel(arquivo)
    if df.empty:
        return
    
    ids_processados = set()

    servidores = extrair_dados_basicos(df)
    if not servidores:
        return
    
    for i, servidor in enumerate(servidores):
        nome_servidor = servidor["Servidor"]
        cpf_servidor = servidor["CPF"]
        vinculo = servidor["Vinculo"]
        nivel_atual = servidor["NivelAtual"]
        data_inicio = servidor["DataInicio"]
        data_enquad = servidor["DataEnquad"]
        DATA_FIM = servidor["DataFim"]
        pts_remanescentes = servidor["PontosExcedentes"]

        ids_processados.add(cpf_servidor)
        
        # ---------- CRIA MATRIZ BASE ----------
        if data_inicio.month == 12:
            data_base = date(data_inicio.year + 1, 1, 1)
        else:
            data_base = date(data_inicio.year, data_inicio.month + 1, 1)

        carreira = [
            [data_base + relativedelta(months=i)] + [0] * 6
            for i in range(DATA_CONCLUSAO)
        ]

        # ---------- AFASTAMENTOS AUTOMÁTICOS ----------
        afastamentos_dict = {}
        faltas_inicial = data_inicio.day - 1
        data_aplicacao_inicial = None

        if faltas_inicial > 0:
            mes_aplicacao = 1 if data_inicio.month == 12 else data_inicio.month + 1
            ano_aplicacao = data_inicio.year + 1 if data_inicio.month == 12 else data_inicio.year
            data_aplicacao_inicial = date(ano_aplicacao, mes_aplicacao, 1)
            afastamentos_dict[data_aplicacao_inicial] = faltas_inicial

        # ---------- AFASTAMENTOS ----------
        carreira = processar_afastamentos(df, i, afastamentos_dict, carreira)

        # dicionário para responsabilidades, SEM os dias automáticos da Data de Início
        afastamentos_dict_resp = afastamentos_dict.copy()
        if data_aplicacao_inicial and data_aplicacao_inicial in afastamentos_dict_resp:
            afastamentos_dict_resp[data_aplicacao_inicial] -= faltas_inicial
            if afastamentos_dict_resp[data_aplicacao_inicial] <= 0:
                del afastamentos_dict_resp[data_aplicacao_inicial]

        # ---------- TITULAÇÕES ----------
        carreira = processar_titulacoes(df, i, carreira)

        # ---------- R.MENSAIS ----------
        carreira = processar_responsabilidades_mensais(df, i, carreira, afastamentos_dict_resp, data_enquad, DATA_FIM)

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

        df_preview["Data"] = df_preview["Data"].apply(lambda d: d.strftime("%d/%m/%Y"))


### ---------- CÁLCULO DE EVOLUÇÃO ---------- ###
        # Dados iniciais
        dt_inicial = data_inicio  # primeira data 
        evolucao = None
        implementacao = None
        meses_ate_evo = None
        pts_resto = None
        novo_nivel = None

        for i in range(DATA_CONCLUSAO):
            dt_atual = carreira[i][0]
            pts_loop = carreira[i][6]

            # Calcula meses passados desde o início corretamente
            meses_passados = (dt_atual.year - data_inicio.year) * 12 + (dt_atual.month - data_inicio.month)
            
            data_prevista18 = dt_inicial + relativedelta(months=18)
            data_prevista15 = data_inicio + relativedelta(months=15)

            if dt_atual < data_prevista18:
                continue
            
            # Calcula desempenho e aperfeicoamento acumulados até a data atual
            desempenho_atual = 0
            
            for j in range(min(len(carreira), 1000)):
                data = carreira[j][0]
                if data.day == 1 and data <= dt_atual:
                    desempenho_atual += carreira[j][2]
            
            desempenho_atual = round(desempenho_atual, 2)

            if dt_atual >= (data_prevista15 if apo_especial_m else data_prevista18): 
                if pts_loop >= 48 and desempenho_atual >= 2.4:
                    evolucao = dt_atual
                    implementacao = evolucao + relativedelta(day=1, months=1)
                    meses_ate_evo = meses_passados
                    pts_resto = pts_loop - 48
                    break
        
        pendencias, motivos = False, []
        mot = ""
        if not evolucao:
            pendencias = True
            motivos += ["obrigatórios"]
        
        if apo_especial_m:
            mot = "Aposentadoria Especial"
        
        if desempenho_atual < 2.4:
            pendencias = True 
            motivos += ["desempenho mínimo de 2.4 pontos"]

        if pendencias and motivos:
            motivo =( ((mot + ". ") if mot else "") + "Não atingiu requisito(s) " + " e ".join(motivos) )
        elif mot:
            motivo = mot
        else:
            motivo = "-"
        
        novo_nivel = NIVEIS[NIVEIS.index(nivel_atual) + 1] if nivel_atual != 'S' else 'S'
        
        try:
            vinculo = int(float(vinculo))
        except Exception:
            vinculo = vinculo 

        result_niveis.append({
            "Status": "Não apto a evolução" if pendencias else "Apto a evolução",
            "Observação": motivo,
            "Servidor": nome_servidor,
            "CPF": cpf_servidor,
            "Vínculo": vinculo,
            "Próximo Nível": "-" if pendencias else novo_nivel,
            "Data da Pontuação Atingida": "-" if pendencias else evolucao.strftime("%d/%m/%Y"),
            "Data da Implementação": "-" if pendencias else implementacao.strftime("%d/%m/%Y"),
            "Interstício de Evolução": "-" if pendencias else meses_ate_evo,
            "Pontuação Alcançada": "-" if pendencias else f"{pts_loop:.2f}",
            "Pontos Excedentes": "-" if pendencias else f"{pts_resto:.2f}",
        })
        
    df_results = pd.DataFrame(result_niveis)
    df_results["Interstício de Evolução"] = df_results["Interstício de Evolução"].apply(
        lambda x: f"{x:>5}" if isinstance(x, int) or (isinstance(x, str) and x.isdigit()) else x
    )
    df_results["Vínculo"] = df_results["Vínculo"].apply(
        lambda x: f"{x:>5}" if isinstance(x, int) or (isinstance(x, str) and x.isdigit()) else x
    )

    return df, df_results, df_preview, ids_processados
