from ..core.logic import calcular_matriz_carreira, verificar_evolucao, DEFAULT_SETTINGS
from ..schemas.evolution import EvolutionInput, EvolutionOutput, CareerRow, EvolutionResult

def run_calculation(input_data: EvolutionInput) -> EvolutionOutput:
    # Converter Schemas para Tuplas/Formatos esperados pela logic.py
    afastamentos = [(a.data, a.dias) for a in input_data.afastamentos]
    aperfeicoamentos = [(a.data, a.horas) for a in input_data.aperfeicoamentos]
    titulacoes = [(t.data, t.tipo) for t in input_data.titulacoes]
    resp_unicas = [(r.data, r.pontos) for r in input_data.resp_unicas]
    
    # Responsabilidades Mensais: (tipo, ini, fim, pontos)
    resp_mensais = [(rm.tipo, rm.inicio, rm.fim, rm.pontos) for rm in input_data.resp_mensais]
    
    # Dados titulação (ex: {'Mestrado': 18.0}) - Precisamos de um mapeamento real ou padrão
    # Por enquanto usamos um padrão (pode vir do config futuramente)
    dados_tit = {
        'Aperfeiçoamento': 4.0,
        'Especialização': 9.0,
        'Mestrado': 18.0,
        'Doutorado': 36.0
    }

    carreira_raw = calcular_matriz_carreira(
        is_ueg=input_data.is_ueg,
        data_inicio=input_data.data_inicio,
        data_enquadramento=input_data.data_enquadramento,
        afastamentos=afastamentos,
        aperfeicoamentos=aperfeicoamentos,
        titulacoes=titulacoes,
        resp_unicas=resp_unicas,
        resp_mensais=resp_mensais,
        dados_tit=dados_tit,
        pts_remanescentes=input_data.pts_remanescentes,
        apo_especial=input_data.apo_especial
    )

    resumo_dict = verificar_evolucao(
        is_ueg=input_data.is_ueg,
        nivel_atual=input_data.nivel_atual,
        carreira=carreira_raw,
        data_inicio=input_data.data_inicio,
        apo_special=input_data.apo_especial
    )

    # Formatar CareerRows
    carreira_rows = []
    for r in carreira_raw:
        carreira_rows.append(CareerRow(
            data=r[0],
            efetivo=round(r[1], 2),
            desempenho=round(r[2], 2),
            aperfeicoamento=round(r[3], 2),
            titulacao=round(r[4], 2),
            resp_unica=round(r[5], 2),
            resp_mensal=round(r[6], 2),
            acumulado=round(r[7], 2)
        ))

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
