from datetime import date, datetime
from typing import List, Dict, Tuple, Optional
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from .config import DEFAULT_SETTINGS, DEFAULT_REQUIREMENTS, GRUPO_REAL, LIMITES_GRUPO

def consolidar_grupo(valores: List[Dict], limite: int) -> float:
    proporcionais = [v["pts"] for v in valores if v["proporcional"]]
    integrais = [v["pts"] for v in valores if not v["proporcional"]]

    resultados = []
    if proporcionais:
        resultados.append(sum(proporcionais))
    resultados.extend(integrais)

    return sum(sorted(resultados, reverse=True)[:limite])

def calcular_matriz_carreira(
    is_ueg: bool,
    data_inicio: date,
    data_enquadramento: date,
    afastamentos: List[Tuple[date, int]],
    aperfeicoamentos: List[Tuple[date, float]],
    titulacoes: List[Tuple[date, str]],
    resp_unicas: List[Tuple[date, float]],
    resp_mensais: List[Tuple[str, date, date, float]],
    dados_tit: Dict[str, float],
    pts_remanescentes: float = 0.0,
    apo_especial: bool = False
):
    settings = DEFAULT_SETTINGS
    
    # Zera e Inicializa Carreira
    data_base = date(data_inicio.year + (1 if data_inicio.month == 12 else 0), 
                     1 if data_inicio.month == 12 else data_inicio.month + 1, 1)
    
    carreira = [[data_base + relativedelta(months=i)] + [0.0] * 7 for i in range(settings.data_conclusao)]

    # 1. Afastamentos
    afastamentos_dict = {}
    for mes, faltas in sorted(afastamentos, key=lambda x: x[0]):
        data_aplic = date(mes.year + (1 if mes.month == 12 else 0), 1 if mes.month == 12 else mes.month + 1, 1)
        afastamentos_dict[data_aplic] = afastamentos_dict.get(data_aplic, 0) + faltas

    # Faltas automáticas (dias anteriores ao início)
    faltas_inicial = data_inicio.day - 1
    data_aplic_auto = None
    if faltas_inicial > 0:
        data_aplic_auto = date(data_inicio.year + (1 if data_inicio.month == 12 else 0), 
                               1 if data_inicio.month == 12 else data_inicio.month + 1, 1)
        afastamentos_dict[data_aplic_auto] = afastamentos_dict.get(data_aplic_auto, 0) + faltas_inicial

    afastamentos_dict_resp = dict(afastamentos_dict)
    if data_aplic_auto and data_aplic_auto in afastamentos_dict_resp:
        afastamentos_dict_resp[data_aplic_auto] -= faltas_inicial
        if afastamentos_dict_resp[data_aplic_auto] <= 0: del afastamentos_dict_resp[data_aplic_auto]

    # Aplica Efetivo e Desempenho
    pontos_des = settings.pontos_desempenho_mes_ueg if is_ueg else settings.pontos_desempenho_mes_promove
    desc_des = settings.desconto_desempenho_dia_ueg if is_ueg else settings.desconto_desempenho_dia_promove
    
    for i in range(len(carreira)):
        d_atual = carreira[i][0]
        falta = afastamentos_dict.get(d_atual, 0)
        carreira[i][1] = max(0, settings.pontos_efetivo_mes - (settings.desconto_efetivo_dia * falta))
        carreira[i][2] = max(0, pontos_des - (desc_des * falta))

    # 2. Aperfeiçoamentos
    if not is_ueg:
        total_h = 0
        for data_c, horas in sorted(aperfeicoamentos, key=lambda x: x[0]):
            data_aplic = date(data_c.year + (1 if data_c.month == 12 else 0), 1 if data_c.month == 12 else data_c.month + 1, 1)
            aprov = min(horas, max(0, 100 - total_h))
            total_h += aprov
            if aprov > 0:
                pts = aprov * DEFAULT_REQUIREMENTS.points_per_hour
                for row in carreira:
                    if row[0] == data_aplic:
                        row[3] += pts
                        break

    # 3. Titulações
    total_pts_tit = 0
    u_tit = None
    for data_c, tipo in sorted(titulacoes, key=lambda x: x[0]):
        if u_tit and data_c < (u_tit + relativedelta(months=12)): continue
        data_aplic = date(data_c.year + (1 if data_c.month == 12 else 0), 1 if data_c.month == 12 else data_c.month + 1, 1)
        pts_t = dados_tit.get(tipo, 0)
        aprov = min(pts_t, max(0, settings.limite_tit - total_pts_tit))
        total_pts_tit += aprov
        u_tit = data_c
        if aprov > 0:
            for row in carreira:
                if row[0] == data_aplic:
                    row[4] += aprov
                    break

    # 4. Responsabilidades Únicas
    total_pts_resp = 0
    ru_map = {}
    for d, pts in sorted(resp_unicas, key=lambda x: x[0]):
        data_aplic = date(d.year + (1 if d.month == 12 else 0), 1 if d.month == 12 else d.month + 1, 1)
        ru_map[data_aplic] = ru_map.get(data_aplic, 0) + pts
    
    for d_aplic in sorted(ru_map.keys()):
        pts_ru = min(ru_map[d_aplic], max(0, settings.limite_resp - total_pts_resp))
        if pts_ru > 0:
            for row in carreira:
                if row[0] == d_aplic:
                    row[5] += pts_ru
                    total_pts_resp += pts_ru
                    break

    # 5. Responsabilidades Mensais
    rm_bruto = defaultdict(lambda: defaultdict(list))
    retro_bruto = defaultdict(lambda: defaultdict(list))

    for tipo, ini, fim, pontos in sorted(resp_mensais, key=lambda x: x[1]):
        t_base = tipo.split(":", 1)[0].strip()
        g = GRUPO_REAL.get(t_base)
        if not g: continue

        # Retroativo (G1 e até 5 anos antes do enquadramento)
        if g == "G1" and ini < data_enquadramento:
            ini_l = max(ini, data_enquadramento - relativedelta(years=5))
            fim_l = min(fim, data_enquadramento - relativedelta(days=1))
            cursor = date(ini_l.year, ini_l.month, 1)
            while cursor <= fim_l:
                ini_m = max(ini_l, cursor)
                u_dia = (cursor + relativedelta(months=1)) - relativedelta(days=1)
                fim_m = min(fim_l, u_dia)
                fim_calc = min(fim_m, fim - relativedelta(days=1))
                if ini_m <= fim_calc:
                    dias_trab = (fim_calc - ini_m).days + 1
                    # Gambiarra 30 dias mantida para paridade
                    mes_comp = (ini_m == cursor and fim_m == u_dia)
                    dias_trab = 30 if mes_comp else min(dias_trab, 30)
                    prop = dias_trab / 30.0
                    falta = afastamentos_dict_resp.get(cursor, 0)
                    pts_f = max(0, (pontos * prop) - ((pontos / 30.0) * falta))
                    retro_bruto[cursor][g].append({"pts": pts_f, "proporcional": prop < 1.0})
                cursor += relativedelta(months=1)

        # Futuro
        if fim < data_enquadramento: continue
        cursor = date(max(ini, data_enquadramento).year, max(ini, data_enquadramento).month, 1)
        while cursor <= fim:
            data_aplic = cursor + relativedelta(months=1)
            ini_e = max(max(ini, data_enquadramento), cursor)
            u_dia = (cursor + relativedelta(months=1)) - relativedelta(days=1)
            fim_e = min(fim, u_dia)
            fim_calc = min(fim_e, fim - relativedelta(days=1))
            if ini_e <= fim_calc:
                dias_trab = (fim_calc - ini_e).days + 1
                mes_comp = (ini_e == cursor and fim_e == u_dia)
                dias_trab = 30 if mes_comp else min(dias_trab, 30)
                prop = dias_trab / 30.0
                falta = afastamentos_dict_resp.get(data_aplic, 0)
                pts_f = max(0, (pontos * prop) - ((pontos / 30.0) * falta))
                rm_bruto[data_aplic][g].append({"pts": pts_f, "proporcional": prop < 1.0})
            cursor += relativedelta(months=1)

    # Consolida Retroativo
    retro_t = 0.0
    for g_map in retro_bruto.values():
        for g, vals in g_map.items():
            retro_t += consolidar_grupo(vals, LIMITES_GRUPO[g])
    
    pts_retro = min(retro_t, max(0, settings.limite_resp - total_pts_resp))
    carreira[0][6] += pts_retro
    total_pts_resp += pts_retro

    # Consolida RM Futuro
    for d_aplic, g_map in sorted(rm_bruto.items()):
        if total_pts_resp >= settings.limite_resp: break
        pts_mes = 0.0
        for g, vals in g_map.items():
            pts_mes += consolidar_grupo(vals, LIMITES_GRUPO[g])
        
        pts_mes_aj = min(pts_mes, settings.limite_resp - total_pts_resp)
        for row in carreira:
            if row[0] == d_aplic:
                row[6] += pts_mes_aj
                total_pts_resp += pts_mes_aj
                break

    # 6. Acumulado
    for i in range(len(carreira)):
        pts_mes_total = sum(carreira[i][1:7])
        if i == 0:
            carreira[i][7] = pts_mes_total + pts_remanescentes
        else:
            carreira[i][7] = carreira[i-1][7] + pts_mes_total

    return carreira

def verificar_evolucao(
    is_ueg: bool,
    nivel_atual: str,
    carreira: List[List],
    data_inicio: date,
    apo_special: bool = False
) -> Dict:
    reqs = DEFAULT_REQUIREMENTS
    idx_nivel = DEFAULT_SETTINGS.niveis.index(nivel_atual)
    novo_nivel = DEFAULT_SETTINGS.niveis[idx_nivel + 1] if nivel_atual != 'S' else 'S'
    
    evolucao = None
    impl = None
    meses_total = 0
    pts_alcançado = 0
    pts_excedente = 0
    
    for i in range(len(carreira)):
        d_atual = carreira[i][0]
        pontos = carreira[i][7]
        meses = (d_atual.year - data_inicio.year) * 12 + (d_atual.month - data_inicio.month)
        
        # Interstícios
        min_12 = data_inicio + relativedelta(months=reqs.min_months_level_2)
        min_18 = data_inicio + relativedelta(months=reqs.min_months_special if apo_special else reqs.min_months_level_1)
        
        if d_atual < min_12: continue

        # Acumulados de Desempenho e Aperfeiçoamento
        ex_ac = sum(r[1] for r in carreira if r[0] <= d_atual)
        des_ac = sum(r[2] for r in carreira if r[0] <= d_atual)
        ap_ac = sum(r[3] for r in carreira if r[0] <= d_atual)

        atingiu_12 = d_atual >= min_12
        atingiu_18 = d_atual >= min_18
        
        # DEBUG
        if is_ueg and pontos >= reqs.min_points_level_1:
             print(f"EVOLUIU UEG? Data: {d_atual}, Pontos: {pontos}, At18: {atingiu_18}, DesAc: {des_ac}, ReqPoints: {reqs.min_points_level_1}, P >= R: {pontos >= reqs.min_points_level_1}")

        if not is_ueg and pontos >= reqs.min_points_level_2:
            if atingiu_12 and ap_ac >= reqs.min_hours_level_2 * reqs.points_per_hour:
                evolucao, impl, meses_total, pts_alcançado, pts_excedente = d_atual, d_atual + relativedelta(months=1, day=1), meses, pontos, pontos - 48
                break
        
        if pontos >= reqs.min_points_level_1:
            if atingiu_18:
                ap_req = 0 if is_ueg else reqs.min_hours_level_1 * reqs.points_per_hour
                des_req = reqs.min_desempenho_points
                if ap_ac >= ap_req and des_ac >= des_req:
                    evolucao, impl, meses_total, pts_alcançado, pts_excedente = d_atual, d_atual + relativedelta(months=1, day=1), meses, pontos, pontos - 48
                    break

    # Pendências (Análise simplificada para o retorno)
    # Recalcula estados finais para a mensagem de observação se não evoluiu
    motivos = []
    status = "Apto a evolução" if evolucao else "Não apto a evolução"
    
    if not evolucao:
        # Pega dados da última linha da carreira para checar por que não evoluiu
        last_row = carreira[-1]
        pts_f = last_row[7]
        des_f = sum(r[2] for r in carreira)
        ap_f = sum(r[3] for r in carreira)
        if pts_f < reqs.min_points_level_1: motivos.append("pontuação mínima")
        if des_f < reqs.min_desempenho_points: motivos.append("desempenho mínimo")
        # ... outros motivos podem ser adicionados
    
    obs = " - ".join(motivos) if motivos else ("Aposentadoria Especial" if apo_special else "-")
    
    return {
        "Status": status,
        "Observação": obs,
        "Próximo Nível": novo_nivel if evolucao else "-",
        "Data da Pontuação Atingida": evolucao.strftime("%d/%m/%Y") if evolucao else "-",
        "Data da Implementação": impl.strftime("%d/%m/%Y") if impl else "-",
        "Interstício de Evolução": meses_total if evolucao else "-",
        "Pontuação Alcançada": f"{pts_alcançado:.2f}" if evolucao else "-",
        "Pontos Excedentes": f"{pts_excedente:.2f}" if evolucao else "-"
    }
