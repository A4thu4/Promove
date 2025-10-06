import streamlit as st
import pandas as pd
import openpyxl as px
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from data_utils import DATA_CONCLUSAO, NIVEIS, dados_tit

def zerar_carreira(carreira):
    from layout import ensure_states
    ensure_states()

    # ZERA todos os campos de cálculo antes de começar
    for i in range(len(carreira)):
        for j in range(1, 8):  # Zera das colunas 1 a 9
            carreira[i][j] = 0


def calcular_evolucao(data_inicial, nivel_atual, carreira, ult_evo, afastamentos, aperfeicoamentos, titulacoes, resp_unicas, resp_mensais):
    """
    Calcula a evolução da carreira aplicando os dados
    TODAS as pontuações são aplicadas no dia 1 do mês seguinte
    """
    if not carreira:
        return carreira, []
    elif not data_inicial:
        st.error("Sem data de Inicio.")
        return carreira, []
    
    zerar_carreira(carreira)

# ---------- APLICA AFASTAMENTOS ---------- #
    afastamentos_dict = {}
    for mes, faltas in sorted(afastamentos, key=lambda data: data[0]):
        mes = mes.date() if isinstance(mes, datetime.datetime) else mes
        
        # Calcula data de aplicação (dia 1 do mês seguinte)
        if mes.month == 12:
            data_aplicacao = datetime.date(mes.year + 1, 1, 1)
        else:
            data_aplicacao = datetime.date(mes.year, mes.month + 1, 1)
        
        if data_aplicacao in afastamentos_dict:
            afastamentos_dict[data_aplicacao] += faltas
        else:
            afastamentos_dict[data_aplicacao] = faltas

    # Aplica os afastamentos nas datas correspondentes
    for i in range(len(carreira)):
        data_atual = carreira[i][0]
        data_atual = data_atual.date() if isinstance(data_atual, datetime.datetime) else data_atual
        
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
        data_conclusao = data_conclusao.date() if isinstance(data_conclusao, datetime.datetime) else data_conclusao

        # Achar dia 1
        if data_conclusao.month == 12:
            data_aplicacao = datetime.date(data_conclusao.year + 1, 1, 1)
        else:
            data_aplicacao = datetime.date(data_conclusao.year, data_conclusao.month + 1, 1)

        # Quanto desse curso ainda pode ser aproveitado
        horas_restantes = max(0, 100 - total_horas)
        horas_aproveitadas = min(horas_curso, horas_restantes)

        # Atualiza acumulado de horas
        total_horas += horas_aproveitadas

        # Só calcula pontos se ainda tiver horas aproveitáveis
        if horas_aproveitadas > 0:
            pontos = horas_aproveitadas * 0.09

            # Encontra a linha na matriz carreira e insere os pontos
            for idx, linha in enumerate(carreira):
                data_linha = linha[0]
                data_linha = data_linha.date() if isinstance(data_linha, datetime.datetime) else data_linha
                
                if data_linha == data_aplicacao:
                    carreira[idx][3] += pontos
                    break

# ---------- APLICA TITULAÇÕES ---------- #
    total_pontos_tit = 0
    LIMITE_TIT = 144
    for data_concl, tipo in sorted(titulacoes, key=lambda data: data[0]):
        data_concl = data_concl.date() if isinstance(data_concl, datetime.datetime) else data_concl

        # Achar dia 1
        if data_concl.month == 12:
            data_aplicacao = datetime.date(data_concl.year + 1, 1, 1)
        else:
            data_aplicacao = datetime.date(data_concl.year, data_concl.month + 1, 1)

        pontos_titulo = dados_tit.get(tipo, 0)
        pontos_restantes = max(0, LIMITE_TIT - total_pontos_tit)
        pontos_aproveitados = min(pontos_titulo, pontos_restantes)
        total_pontos_tit += pontos_aproveitados

        if pontos_aproveitados > 0:
            for i, linha in enumerate(carreira):
                d = linha[0]
                d = d.date() if isinstance(d, datetime.datetime) else d

                if d == data_aplicacao:
                    carreira[i][4] += pontos_aproveitados
                    break

# ---------- APLICA RESPONSABILIDADES ÚNICAS ---------- #
    total_pontos_resp = 0
    LIMITE_RESP = 144

    ru_dict = {}
    for data, pontos in sorted(resp_unicas, key=lambda data: data[0]):
        data = data.date() if isinstance(data, datetime.datetime) else data

        # Achar dia 1
        if data.month == 12:
            data_aplicacao = datetime.date(data.year + 1, 1, 1)
        else:
            data_aplicacao = datetime.date(data.year, data.month + 1, 1)

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
            d = d.date() if isinstance(d, datetime.datetime) else d
            
            if d == data_aplicacao:
                carreira[i][5] += pontos_aj
                total_pontos_resp += pontos_aj
                break

# ---------- APLICA RESPONSABILIDADES MENSAIS ---------- #
    for tipo, inicio, meses, pontos in sorted(resp_mensais, key=lambda data: data[1]):
        # garante que seja datetime.date
        inicio = inicio.date() if isinstance(inicio, datetime.datetime) else inicio

        # primeiro mês de aplicação é o mês seguinte
        mes_aplicacao = inicio.month + 1
        ano_aplicacao = inicio.year
        if mes_aplicacao > 12:
            mes_aplicacao = 1
            ano_aplicacao += 1

        for _ in range(meses):
            # calcula a data do dia 1 do mês atual
            data_aplicacao = datetime.date(ano_aplicacao, mes_aplicacao, 1)

            # aplica na carreira
            for i, linha in enumerate(carreira):
                d = linha[0]
                d = d.date() if isinstance(d, datetime.datetime) else d
                if d == data_aplicacao:
                    # pega falta do mês anterior
                    mes_anterior = mes_aplicacao - 1
                    ano_anterior = ano_aplicacao
                    if mes_anterior < 1:
                        mes_anterior = 12
                        ano_anterior -= 1

                    falta = next((faltas for mes, faltas in st.session_state.afastamentos
                                if mes.month == mes_anterior and mes.year == ano_anterior), 0)
                    desconto = (pontos / 30) * falta

                    # verifica limite
                    if total_pontos_resp + pontos - desconto > LIMITE_RESP:
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
            carreira[i][7] = carreira[i][1] + carreira[i][2] + carreira[i][3] + carreira[i][4] + carreira[i][5] + carreira[i][6] + pts_ultima_evolucao 
        else:
            carreira[i][7] = carreira[i-1][7] + carreira[i][1] + carreira[i][2] + carreira[i][3] + carreira[i][4] + carreira[i][5] + carreira[i][6] 

### ---------- CÁLCULO DE TEMPO ---------- ###
    resultado_niveis = []

    # Dados iniciais
    data_inicio = carreira[0][0]  # primeira data 
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
                pts_resto = pontos - 48 # ou 96?
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
    aperfeicoamento = round(aperfeicoamento,4) if aperfeicoamento else 0
    
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
            "Pontos Remanescentes": "-"
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
            "Pontos Remanescentes": round(pts_resto, 4)
        })
    
    return carreira, resultado_niveis

def calcular_planilha(arquivo):
    pass