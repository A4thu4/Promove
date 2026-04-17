"""
Orquestrador do Cálculo Múltiplo: recebe a planilha bruta, processa
linha-a-linha reutilizando `run_calculation`, e produz tanto o JSON
agregado quanto o Excel exportável com o mesmo layout do app antigo.
"""
from __future__ import annotations

import io
from typing import List

import pandas as pd

from backend.app.schemas.evolution import (
    BatchCalculationOutput,
    BatchRowResult,
)
from backend.app.services.batch_parser import iter_rows, ler_planilha, row_to_input
from backend.app.services.calculator import run_calculation


# Ordem idêntica à do Streamlit antigo (app/logic.py:845)
EXPORT_COLUMNS = [
    "Status",
    "Observação",
    "Processo SEI",
    "Servidor",
    "CPF",
    "Vínculo",
    "Próximo Nível",
    "Data da Pontuação Atingida",
    "Data da Implementação",
    "Interstício de Evolução",
    "Pontuação Alcançada",
    "Pontos Excedentes",
]


def run_batch(
    file_bytes: bytes,
    filename: str,
    is_ueg: bool,
    apo_especial: bool,
) -> BatchCalculationOutput:
    df = ler_planilha(file_bytes)
    if df.empty:
        raise ValueError("Nenhum servidor válido encontrado na planilha.")

    resultados: List[BatchRowResult] = []
    for row in iter_rows(df):
        info, input_data = row_to_input(row, is_ueg, apo_especial)
        output = run_calculation(input_data)
        resultados.append(
            BatchRowResult(info=info, input=input_data, resumo=output.resumo)
        )

    return BatchCalculationOutput(
        filename=filename,
        total_linhas=len(resultados),
        is_ueg=is_ueg,
        apo_especial=apo_especial,
        resultados=resultados,
    )


def to_excel_bytes(output: BatchCalculationOutput) -> bytes:
    linhas = []
    for r in output.resultados:
        linhas.append(
            {
                "Status": r.resumo.status,
                "Observação": r.resumo.observacao,
                "Processo SEI": r.info.processo_sei,
                "Servidor": r.info.servidor,
                "CPF": r.info.cpf,
                "Vínculo": r.info.vinculo,
                "Próximo Nível": r.resumo.proximo_nivel,
                "Data da Pontuação Atingida": r.resumo.data_pontuacao,
                "Data da Implementação": r.resumo.data_implementacao,
                "Interstício de Evolução": r.resumo.intersticio,
                "Pontuação Alcançada": r.resumo.pontuacao_alcancada,
                "Pontos Excedentes": r.resumo.pontos_excedentes,
            }
        )

    df = pd.DataFrame(linhas, columns=EXPORT_COLUMNS)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    return buf.getvalue()


def export_filename(original: str) -> str:
    base = original.rsplit(".", 1)[0] if "." in original else original
    return f"Resultado(s) {base}.xlsx"
