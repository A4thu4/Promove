"""
Converte uma planilha Excel (fluxo Cálculo Múltiplo) em uma sequência de
EvolutionInput, reaproveitando o motor de cálculo já existente para o
fluxo individual.
"""
from __future__ import annotations

import io
from datetime import date, datetime
from typing import Iterable, List, Tuple

import numpy as np
import openpyxl as px
import pandas as pd

from backend.app.core.spreadsheet_tables import (
    COLUNAS_OBRIGATORIAS,
    COLUNAS_RESP_MENSAIS,
    COLUNAS_RESP_UNICAS,
)
from backend.app.schemas.evolution import (
    AfastamentoSchema,
    AperfeicoamentoSchema,
    BatchServidorInfo,
    EvolutionInput,
    RespMensalSchema,
    RespUnicaSchema,
    TitulacaoSchema,
)


def ler_planilha(file_bytes: bytes) -> pd.DataFrame:
    """Lê e valida a planilha Excel, retornando um DataFrame limpo."""
    wb = px.load_workbook(io.BytesIO(file_bytes), data_only=True)
    try:
        aba = wb.active
        dados = list(aba.values)
    finally:
        wb.close()

    linha_header = None
    for idx, linha in enumerate(dados[:5]):
        if linha and "Servidor" in [str(c).strip() for c in linha]:
            linha_header = idx
            break

    if linha_header is None:
        raise ValueError("Cabeçalho não encontrado na planilha.")

    raw_cols = dados[linha_header]
    colunas: List[str] = []
    contador: dict = {}
    for c in raw_cols:
        nome = str(c).strip() if c not in (None, "", "None") else None
        if not nome:
            nome = "COL_VAZIA"
        if nome in contador:
            contador[nome] += 1
            nome = f"{nome}_{contador[nome]}"
        else:
            contador[nome] = 1
        colunas.append(nome)

    df = pd.DataFrame(dados[linha_header + 1:], columns=colunas)
    df = df.drop_duplicates().replace([None, np.nan], "")

    ausentes = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if ausentes:
        raise ValueError(f"Colunas obrigatórias ausentes: {ausentes}")

    df = df[
        df["CPF"].astype(str).str.strip().ne("")
        & df["Nível Atual"].astype(str).str.strip().ne("")
        & df["Data de Início dos Pontos"].astype(str).str.strip().ne("")
        & df["Data do Enquadramento"].astype(str).str.strip().ne("")
    ].copy()

    df["Vínculo"] = df["Vínculo"].astype(str).str.strip() if "Vínculo" in df.columns else ""
    df["CPF"] = df["CPF"].astype(str).str.strip()
    df["Processo SEI"] = (
        df["Processo SEI"].astype(str).str.strip() if "Processo SEI" in df.columns else ""
    )

    # Dedup por (Vínculo, CPF) — mantém linhas com o mesmo Vínculo quando o CPF difere.
    v = df["Vínculo"]
    com_v = df[v.ne("")].drop_duplicates(subset=["Vínculo", "CPF"], keep="first")
    sem_v = df[v.eq("")]
    df = pd.concat([com_v, sem_v], ignore_index=True)

    df["Data de Início dos Pontos"] = pd.to_datetime(
        df["Data de Início dos Pontos"], format="%d/%m/%Y", errors="coerce"
    )
    df["Data do Enquadramento"] = pd.to_datetime(
        df["Data do Enquadramento"], format="%d/%m/%Y", errors="coerce"
    )

    return df


def _first_day_next_month(d: date) -> date:
    return date(d.year + 1, 1, 1) if d.month == 12 else date(d.year, d.month + 1, 1)


def _to_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _get(row: pd.Series, col: str) -> str:
    if col not in row.index:
        return ""
    val = row[col]
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return ""
    return str(val).strip()


def _split_multi(value: str) -> List[str]:
    return [p.strip() for p in value.split(";") if p.strip()]


def parse_afastamentos(row: pd.Series) -> List[AfastamentoSchema]:
    meses = _split_multi(_get(row, "Mês do Afastamento"))
    faltas = _split_multi(_get(row, "Quantitativo de Afastamentos"))
    out: List[AfastamentoSchema] = []
    for mes_str, falta_str in zip(meses, faltas):
        d = _to_date(mes_str)
        if d is None:
            continue
        try:
            qtd = int(float(falta_str))
        except ValueError:
            continue
        if qtd <= 0:
            continue
        out.append(AfastamentoSchema(data=d, dias=qtd))
    return out


def parse_aperfeicoamentos(row: pd.Series, is_ueg: bool) -> List[AperfeicoamentoSchema]:
    if is_ueg:
        return []
    datas = _split_multi(_get(row, "Data de Validação do Aperfeiçoamento"))
    horas = _split_multi(_get(row, "Carga Horária"))
    out: List[AperfeicoamentoSchema] = []
    for d_str, h_str in zip(datas, horas):
        d = _to_date(d_str)
        if d is None:
            continue
        try:
            h = float(h_str)
        except ValueError:
            continue
        if h <= 0:
            continue
        out.append(AperfeicoamentoSchema(data=d, horas=h))
    return out


def parse_titulacoes(row: pd.Series) -> List[TitulacaoSchema]:
    datas = _split_multi(_get(row, "Data de Validação da Titulação"))
    tipos = _split_multi(_get(row, "Tipo"))
    out: List[TitulacaoSchema] = []
    for d_str, tipo in zip(datas, tipos):
        d = _to_date(d_str)
        if d is None or not tipo or tipo == "Nenhuma":
            continue
        out.append(TitulacaoSchema(data=d, tipo=tipo))
    return out


def parse_resp_mensais(row: pd.Series, data_fim: date) -> List[RespMensalSchema]:
    out: List[RespMensalSchema] = []
    for coluna, (tipo_base, mapa) in COLUNAS_RESP_MENSAIS.items():
        texto = _get(row, coluna)
        if not texto:
            continue
        for bloco in _split_multi(texto):
            partes = [p.strip() for p in bloco.split("-")]
            if len(partes) < 3:
                continue
            simbolo, di_raw, df_raw = partes[0], partes[1], partes[2]
            pontos = mapa.get(simbolo)
            if not pontos:
                continue
            inicio = _to_date(di_raw)
            if inicio is None:
                continue
            fim = _to_date(df_raw) or data_fim
            if fim <= inicio:
                continue
            out.append(
                RespMensalSchema(
                    tipo=f"{tipo_base}: {simbolo}",
                    inicio=inicio,
                    fim=fim,
                    pontos=float(pontos),
                )
            )
    return out


def parse_resp_unicas(row: pd.Series) -> List[RespUnicaSchema]:
    acumulado: dict[date, float] = {}
    for coluna, mapa in COLUNAS_RESP_UNICAS.items():
        texto = _get(row, coluna)
        if not texto:
            continue
        for bloco in _split_multi(texto):
            partes = [p.strip() for p in bloco.split("-")]
            if len(partes) < 3:
                continue
            try:
                qtd = int(partes[0])
            except ValueError:
                continue
            tipo = partes[1]
            d_concl = _to_date(partes[2])
            if d_concl is None or not tipo:
                continue
            pontos = qtd * mapa.get(tipo, 0)
            if pontos <= 0:
                continue
            acumulado[d_concl] = acumulado.get(d_concl, 0.0) + float(pontos)
    return [RespUnicaSchema(data=d, pontos=p) for d, p in sorted(acumulado.items())]


def row_to_input(
    row: pd.Series, is_ueg: bool, apo_especial: bool
) -> Tuple[BatchServidorInfo, EvolutionInput]:
    nome = _get(row, "Servidor")
    cpf = _get(row, "CPF")
    vinculo = _get(row, "Vínculo")
    processo = _get(row, "Processo SEI")
    nivel = _get(row, "Nível Atual").upper()

    data_inicio_raw = row.get("Data de Início dos Pontos")
    data_enquad_raw = row.get("Data do Enquadramento")
    data_inicio = _to_date(data_inicio_raw)
    data_enquad = _to_date(data_enquad_raw)
    if data_inicio is None or data_enquad is None:
        raise ValueError(f"Datas obrigatórias inválidas para o servidor '{nome or cpf}'.")

    try:
        raw_pts = row.get("Pontos Excedentes da Última Evolução")
        pts_rem = float(raw_pts) if raw_pts not in ("", None) else 0.0
    except (TypeError, ValueError):
        pts_rem = 0.0

    data_fim = date(data_inicio.year + 20, data_inicio.month, data_inicio.day)

    input_data = EvolutionInput(
        is_ueg=is_ueg,
        nivel_atual=nivel,
        data_inicio=data_inicio,
        data_enquadramento=data_enquad,
        afastamentos=parse_afastamentos(row),
        aperfeicoamentos=parse_aperfeicoamentos(row, is_ueg),
        titulacoes=parse_titulacoes(row),
        resp_unicas=parse_resp_unicas(row),
        resp_mensais=parse_resp_mensais(row, data_fim),
        pts_remanescentes=round(pts_rem, 4),
        apo_especial=apo_especial,
    )

    info = BatchServidorInfo(
        processo_sei=processo,
        servidor=nome,
        cpf=cpf,
        vinculo=vinculo,
    )
    return info, input_data


def iter_rows(df: pd.DataFrame) -> Iterable[pd.Series]:
    for _, row in df.iterrows():
        yield row
