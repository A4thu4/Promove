from datetime import date, timedelta
from typing import List, Dict, Tuple
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from .config import DEFAULT_SETTINGS, DEFAULT_REQUIREMENTS, GRUPO_REAL, LIMITES_GRUPO

settings = DEFAULT_SETTINGS
reqs = DEFAULT_REQUIREMENTS

def _build_carreira(data_inicio: date, is_ueg: bool) -> list:
    data_base = date(data_inicio.year + 1, 1, 1) \
        if data_inicio.month == 12 \
        else date(data_inicio.year, data_inicio.month + 1, 1)

    cols = 7 if is_ueg else 8  # UEG = 7 colunas (sem aperf), Geral = 8
    return [[data_base + relativedelta(months=i)] + [0.0] * cols
            for i in range(settings.data_conclusao)]

def _proximo_mes_1(d: date) -> date:
    """Retorna o dia 1 do mês seguinte."""
    return date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)

def consolidar_grupo(valores: List[Dict], limite: int) -> float:
    """
    Regra de negócio: pontos proporcionais somam entre si como 1 entrada,
    pontos integrais competem individualmente. Pega os 'limite' maiores.
    """
    proporcionais = [v["pts"] for v in valores if v["proporcional"]]
    integrais = [v["pts"] for v in valores if not v["proporcional"]]

    resultados = []
    if proporcionais:
        resultados.append(sum(proporcionais))
    resultados.extend(integrais)

    return sum(sorted(resultados, reverse=True)[:limite])

def zerar_carreira(carreira: List[List]) -> None:
    for linha in carreira:
        for j in range(1, len(linha)):
            linha[j] = 0.0

def calcular_carreira(
    is_ueg: bool,
    data_enquadramento: date,
    data_inicial: date,
    afastamentos: List[Tuple[date, int]],
    aperfeicoamentos: List[Tuple[date, float]],
    titulacoes: List[Tuple[date, str]],
    resp_unicas: List[Tuple[date, float]],
    resp_mensais: List[Tuple[str, date, date, float]],
    dados_tit: Dict[str, float],
    pts_ultima_evolucao: float = 0.0,
):

    # Índices das colunas (data está no índice 0)
    idx_tit         = 3 if is_ueg else 4
    idx_resp_unica  = 4 if is_ueg else 5
    idx_resp_mensal = 5 if is_ueg else 6
    idx_acumulado   = 6 if is_ueg else 7

    carreira = _build_carreira(data_inicial, is_ueg)

    # 1. Afastamentos
    afastamentos_dict: Dict[date, int] = {}
    for mes, faltas in sorted(afastamentos, key=lambda x: x[0]):
        d = mes.date() if hasattr(mes, 'date') else mes
        afastamentos_dict[_proximo_mes_1(d)] = afastamentos_dict.get(_proximo_mes_1(d), 0) + faltas

    # Faltas automáticas (dias anteriores ao início)
    faltas_inicial = data_inicial.day - 1
    data_aplica_auto = None
    if faltas_inicial > 0:
        data_aplica_auto = _proximo_mes_1(data_inicial)
        afastamentos_dict[data_aplica_auto] = afastamentos_dict.get(data_aplica_auto, 0) + faltas_inicial

    # Dicionário SEM dias automáticas para responsabilidades
    afastamentos_dict_resp = dict(afastamentos_dict)
    if data_aplica_auto and data_aplica_auto in afastamentos_dict_resp:
        afastamentos_dict_resp[data_aplica_auto] -= faltas_inicial
        if afastamentos_dict_resp[data_aplica_auto] <= 0: del afastamentos_dict_resp[data_aplica_auto]

    # Aplica Efetivo e Desempenho
    pontos_des = settings.pontos_desempenho_mes_ueg if is_ueg else settings.pontos_desempenho_mes
    desc_des = settings.desconto_desempenho_dia_ueg if is_ueg else settings.desconto_desempenho_dia
    
    for i in range(len(carreira)):
        d_atual = carreira[i][0]
        falta = afastamentos_dict.get(d_atual, 0)
        if d_atual.day == 1 and d_atual != data_inicial:
            carreira[i][1] = max(0, settings.pontos_efetivo_mes - (settings.desconto_efetivo_dia * falta))
            carreira[i][2] = max(0, pontos_des - (desc_des * falta))

    # 2. Aperfeiçoamentos
    if not is_ueg:
        total_h = 0
        for data_c, horas in sorted(aperfeicoamentos, key=lambda x: x[0]):
            data_c = data_c.date() if hasattr(data_c, 'date') else data_c
            validado = min(horas, max(0, 100 - total_h))
            total_h += validado
            if validado > 0:
                data_aplica = _proximo_mes_1(data_c)
                pts = validado * DEFAULT_REQUIREMENTS.points_per_hour
                for linha in carreira:
                    if linha[0] == data_aplica:
                        linha[3] += pts
                        break

    # 3. Titulações
    total_pts_tit = 0.0
    ultima_tit = None
    for data_c, tipo in sorted(titulacoes, key=lambda x: x[0]):
        data_c = data_c.date() if hasattr(data_c, 'date') else data_c
        if ultima_tit and data_c < (ultima_tit + relativedelta(months=12)): continue
        pts_t = dados_tit.get(tipo, 0)
        validado = min(pts_t, max(0, settings.limite_tit - total_pts_tit))
        total_pts_tit += validado
        ultima_tit = data_c
        if validado > 0:
            data_aplica = _proximo_mes_1(data_c)
            for linha in carreira:
                if linha[0] == data_aplica:
                    linha[idx_tit] += validado
                    break

    # 4. Responsabilidades Únicas
    total_pts_resp = 0
    ru_map: Dict[date, float] = {}
    for d, pts in sorted(resp_unicas, key=lambda x: x[0]):
        d = d.date() if hasattr(d, 'date') else d
        data_aplica = _proximo_mes_1(d)
        ru_map[data_aplica] = ru_map.get(data_aplica, 0) + pts
    
    for d_aplica in sorted(ru_map.keys()):
        validado = min(ru_map[d_aplica], max(0, settings.limite_resp - total_pts_resp))
        if validado > 0:
            for linha in carreira:
                if linha[0] == d_aplica:
                    linha[idx_resp_unica] += validado
                    total_pts_resp += validado
                    break

    # 5. Responsabilidades Mensais
    rm_bruto    = defaultdict(lambda: defaultdict(list))
    retro_bruto = defaultdict(lambda: defaultdict(list))

    for tipo, ini, fim, pontos in sorted(resp_mensais, key=lambda x: x[1]):
        ini = ini.date() if hasattr(ini, 'date') else ini
        fim = fim.date() if hasattr(fim, 'date') else fim

        t_base = tipo.split(":", 1)[0].strip()
        g = GRUPO_REAL.get(t_base)
        if not g: continue

        def _distribuir_mes(cursor, ini, fim, dest_dict):
            while cursor <= fim:
                d_ap = cursor + relativedelta(months=1)
                ini_m = max(ini, cursor)
                ult_dia = (cursor + relativedelta(months=1)) - timedelta(days=1)
                fim_m = min(fim, ult_dia)
                fim_calc = min(fim_m, fim - timedelta(days=1))

                if ini_m > fim_calc:
                    cursor += relativedelta(months=1)
                    continue

                dias = (fim_calc - ini_m).days + 1
                mes_completo = (ini_m == cursor and fim_m == ult_dia)
                dias = 30 if mes_completo else min(dias, 30)

                prop = dias / 30.0
                faltas = afastamentos_dict_resp.get(d_ap, 0)
                pts_aj = max(0.0, pontos * prop - (pontos / 30.0) * faltas)

                if pts_aj > 0:
                    dest_dict[d_ap][g].append({"pts": pts_aj, "proporcional": prop < 1.0})

                cursor += relativedelta(months=1)

        # Retroativo (só G1, até 5 anos antes do enquadramento)
        if g == "G1" and ini < data_enquadramento:
            ini_l = max(ini, data_enquadramento - relativedelta(years=5))
            fim_l = min(fim, data_enquadramento - relativedelta(days=1))
            cursor = date(ini_l.year, ini_l.month, 1)
            _distribuir_mes(cursor, ini_l, fim_l, retro_bruto)

        if fim < data_enquadramento: continue

        inicio_efetivo = max(ini, data_enquadramento)
        cursor = date(inicio_efetivo.year, inicio_efetivo.month, 1)
        _distribuir_mes(cursor, inicio_efetivo, fim, rm_bruto)

    # Consolida Retroativo
    retro_total = sum(
        consolidar_grupo(vals, LIMITES_GRUPO[g])
        for grupos in retro_bruto.values()
        for g, vals in grupos.items()
    )

    if retro_total > 0:
        validado = min(retro_total, max(0.0, settings.limite_resp - total_pts_resp))
        carreira[0][idx_resp_mensal] += validado
        total_pts_resp += validado

    # Consolida RM Futuro
    for d_aplica, g_map in sorted(rm_bruto.items()):
        if total_pts_resp >= settings.limite_resp: break
        pts_mes = sum(consolidar_grupo(vals, LIMITES_GRUPO[g]) for g, vals in g_map.items())
        validado = min(pts_mes, settings.limite_resp - total_pts_resp)
        if validado > 0:
            for linha in carreira:
                if linha[0] == d_aplica:
                    linha[idx_resp_mensal] += validado
                    total_pts_resp += validado
                    break

    # 6. Acumulado
    ult_evo = pts_ultima_evolucao or 0.0

    for i in range(len(carreira)):
        pts_mes_total = sum(carreira[i][1:idx_acumulado])
        carreira[i][idx_acumulado] = (carreira[i - 1][idx_acumulado] + pts_mes_total) if i > 0 else (pts_mes_total + ult_evo)

    return carreira

def validar_evolucao(
    is_ueg: bool,
    nivel_atual: str,
    carreira: List[List],
    data_inicial: date,
    apo_especial: bool = False
) -> Dict:

    niveis = settings.niveis_ueg if is_ueg else settings.niveis
    idx_nivel = niveis.index(nivel_atual)
    novo_nivel = niveis[idx_nivel + 1] if nivel_atual != niveis[-1] else niveis[-1]

    evolucao = None
    implement = None
    meses_total = 0
    pts_alcancado = 0
    pts_excedente = 0

    idx_acumulado = 6 if is_ueg else 7
    for i in range(len(carreira)):
        d_atual = carreira[i][0]
        pontos = carreira[i][idx_acumulado]
        meses = (d_atual.year - data_inicial.year) * 12 + (d_atual.month - data_inicial.month)
        
        # Interstícios
        min_12 = data_inicial + relativedelta(months=reqs.min_months_level_2)
        min_15 = data_inicial + relativedelta(months=reqs.min_months_special)
        min_18 = data_inicial + relativedelta(months=reqs.min_months_level_1)

        if d_atual < min_12: continue

        # Acumulados de Desempenho e Aperfeiçoamento
        # exercício_final = round(sum(r[1] for r in carreira if r[0] <= d_atual), 2)
        desempenho_final = round(sum(r[2] for r in carreira if r[0] <= d_atual), 2)
        aperf_final = round(sum(r[3] for r in carreira if r[0] <= d_atual), 2) if not is_ueg else 0.0

        atingiu_12 = d_atual >= min_12
        atingiu_18 = d_atual >= (min_15 if apo_especial else min_18)
        
        # Verificação de Evolução (Rápida ou Padrão)
        aperf_req = (reqs.min_hours_level_1 if not is_ueg else 0) * reqs.points_per_hour
        
        # 1. Rápida (apenas não-UEG): 96pts + 12m + 40h aperf
        apto_rapida = (not is_ueg and atingiu_12 and pontos >= reqs.min_points_level_2 and 
                       aperf_final >= reqs.min_hours_level_2 * reqs.points_per_hour and 
                       desempenho_final >= reqs.min_desempenho_points)

        # 2. Padrão: 48pts + 18m + 60h aperf
        apto_padrao = (atingiu_18 and pontos >= reqs.min_points_level_1 and 
                       aperf_final >= aperf_req and desempenho_final >= reqs.min_desempenho_points)

        if apto_rapida or apto_padrao:
            evolucao      = d_atual
            implement     = _proximo_mes_1(d_atual)
            meses_total   = meses
            pts_alcancado = pontos
            pts_excedente = pontos - 48
            break

    # Pendências (Análise simplificada para o retorno)
    # Recalcula estados finais para a mensagem de observação se não evoluiu
    motivos = []
    status = "Apto a evolução" if evolucao else "Não apto a evolução"
    required_min_months = reqs.min_months_special if apo_especial else reqs.min_months_level_1

    if apo_especial: motivos.append("Aposentadoria Especial")

    if not evolucao:
        # Pega dados da última linha da carreira para checar por que não evoluiu
        last_row = carreira[-1]
        pts_f = last_row[idx_acumulado]
        des_f = round(sum(r[2] for r in carreira), 2)
        aperf_f = round(sum(r[3] for r in carreira), 2) if not is_ueg else 0.0
        
        meses_f = (last_row[0].year - data_inicial.year) * 12 + (last_row[0].month - data_inicial.month)
        
        if pts_f < reqs.min_points_level_1:
            motivos.append(f"pontuação insuficiente ({pts_f:.2f}/48)")
        
        if des_f < reqs.min_desempenho_points:
            motivos.append(f"desempenho insuficiente ({des_f:.2f}/{reqs.min_desempenho_points})")
            
        if not is_ueg and aperf_f < (reqs.min_hours_level_1 * reqs.points_per_hour):
            req_h = reqs.min_hours_level_1
            pts_req = req_h * reqs.points_per_hour
            motivos.append(f"aperfeiçoamento insuficiente ({aperf_f:.2f}/{pts_req:.2f} pts - {req_h}h)")

        if meses_f < required_min_months:
             motivos.append(f"interstício insuficiente ({meses_f}/{reqs.min_months_level_1} meses)")

    obs = "; ".join(motivos) if motivos else "-"
    
    return {
        "Status": status,
        "Observação": obs,
        "Próximo Nível": novo_nivel if evolucao else "-",
        "Data da Pontuação Atingida": evolucao.strftime("%d/%m/%Y") if evolucao else "-",
        "Data da Implementação": implement.strftime("%d/%m/%Y") if implement else "-",
        "Interstício de Evolução": meses_total if evolucao else "-",
        "Pontuação Alcançada": f"{pts_alcancado:.2f}" if evolucao else "-",
        "Pontos Excedentes": f"{pts_excedente:.2f}" if evolucao else "-"
    }
