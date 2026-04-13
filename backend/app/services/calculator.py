try:
    from app.core.logic import calcular_carreira, validar_evolucao
    from app.schemas.evolution import EvolutionInput, EvolutionOutput, CareerRow, EvolutionResult
except ImportError:
    from backend.app.core.logic import calcular_carreira, validar_evolucao
    from backend.app.schemas.evolution import EvolutionInput, EvolutionOutput, CareerRow, EvolutionResult

dados_tit = {
    'Nenhuma': 0.0,
    'Graduação': 6.0,
    'Especialização': 8.0,
    'Mestrado': 24.0,
    'Doutorado': 48.0,
}

dados_tit_ueg = {
    **dados_tit,
    'Pós-graduação em Nível de Certificação': 6,
    'Pós-doutorado – igual a 6 meses': 6,
    'Pós-doutorado - (6 a 12 meses)': 8,
    'Pós-doutorado - (13 a 24 meses)': 12,
    'Pós-doutorado - (25 a 48 meses)': 24,
    'Pós-doutorado - (maior ou igual a 48 meses)': 48,
}


def run_calculation(input_data: EvolutionInput) -> EvolutionOutput:
    # Converter Schemas para Tuplas/Formatos esperados pela logic.py
    afastamentos     = [(a.data, a.dias) for a in input_data.afastamentos]
    aperfeicoamentos = [(a.data, a.horas) for a in input_data.aperfeicoamentos]
    titulacoes       = [(t.data, t.tipo) for t in input_data.titulacoes]
    resp_unicas      = [(r.data, r.pontos) for r in input_data.resp_unicas]
    resp_mensais     = [(rm.tipo, rm.inicio, rm.fim, rm.pontos) for rm in input_data.resp_mensais]
    dados_titulacao  = dados_tit_ueg if input_data.is_ueg else dados_tit

    carreira_raw = calcular_carreira(
        is_ueg=input_data.is_ueg,
        data_enquadramento=input_data.data_enquadramento,
        data_inicial=input_data.data_inicio,
        afastamentos=afastamentos,
        aperfeicoamentos=aperfeicoamentos,
        titulacoes=titulacoes,
        resp_unicas=resp_unicas,
        resp_mensais=resp_mensais,
        dados_tit=dados_titulacao,
        pts_ultima_evolucao=input_data.pts_remanescentes,
    )

    resumo_dict = validar_evolucao(
        is_ueg=input_data.is_ueg,
        nivel_atual=input_data.nivel_atual,
        carreira=carreira_raw,
        data_inicial=input_data.data_inicio,
        apo_especial=input_data.apo_especial
    )

    # Formatar CareerRows
    carreira_rows = [
        CareerRow(
            data=r[0],
            efetivo=round(r[1], 4),
            desempenho=round(r[2], 4),
            aperfeicoamento=round(r[3], 4),
            titulacao=round(r[4], 4),
            resp_unica=round(r[5], 4),
            resp_mensal=round(r[6], 4),
            acumulado=round(r[7], 4)
        )
        for r in carreira_raw
    ]

    resumo = EvolutionResult(
        status=resumo_dict["Status"],
        observacao=resumo_dict["Observação"],
        proximo_nivel=resumo_dict["Próximo Nível"],
        data_pontuacao=resumo_dict["Data da Pontuação Atingida"],
        data_implementacao=resumo_dict["Data da Implementação"],
        intersticio=str(resumo_dict["Interstício de Evolução"]),
        pontuacao_alcancada=resumo_dict["Pontuação Alcançada"],
        pontos_excedentes=resumo_dict["Pontos Excedentes"]
    )

    return EvolutionOutput(resumo=resumo, carreira=carreira_rows)
