import streamlit as st
import numpy as np
import pandas as pd
import openpyxl as px
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

def ler_planilha_excel(arquivo):
    """Lê e valida a planilha Excel, retornando um DataFrame limpo."""
    try:
        wb = px.load_workbook(arquivo, data_only=True)
        aba = wb.active
        dados = list(aba.values)
        if len(dados) < 3:
            st.error("Planilha incompleta: faltam cabeçalhos ou linhas de dados.")
            return pd.DataFrame()

        colunas = [str(c).strip() for c in dados[2]]
        valores = dados[3:]
        df = pd.DataFrame(valores, columns=colunas)

        # Limpeza básica
        df = df.drop_duplicates().replace([None, np.nan], "")
        colunas_obrigatorias = [
            "Servidor", "CPF", "Vìnculo", "Nível Atual",
            "Data do Enquadramento ou da Última Evolução",
            "Pontos Excedentes da Última Evolução"
        ]
        ausentes = [c for c in colunas_obrigatorias if c not in df.columns]
        if ausentes:
            st.error(f"Colunas obrigatórias ausentes: {ausentes}")
            return pd.DataFrame()

        # Remove linhas vazias e normaliza tipos
        df = df[
            df["Servidor"].astype(str).str.strip().ne("") &
            df["CPF"].astype(str).str.strip().ne("") &
            df["Vìnculo"].astype(str).str.strip().ne("") &
            df["Nível Atual"].astype(str).str.strip().ne("")
        ]

        df["Vìnculo"] = df["Vìnculo"].astype(str).str.strip()
        df = df.drop_duplicates(subset=["Vìnculo"], keep="first")
        df["Data do Enquadramento ou da Última Evolução"] = pd.to_datetime(
            df["Data do Enquadramento ou da Última Evolução"], errors="coerce"
        )

        st.markdown("<h2 style='text-align:center; color:#000000; '>Detalhamento</h2>", unsafe_allow_html=True)
        st.dataframe(
            df.head(),
            hide_index=True,
            column_config={
                "Vìnculo": st.column_config.NumberColumn(format="%d"),
                "Data do Enquadramento ou da Última Evolução": st.column_config.DateColumn(format="DD/MM/YYYY")
            }
        )

        return df

    except Exception as e:
        st.error(f"Erro ao ler planilha: {e}")
        return pd.DataFrame()


def extrair_dados_basicos(df):
    """Extrai e normaliza os dados obrigatórios de cada servidor da planilha."""
    servidores = []

    for i, row in df.iterrows():
        nome = str(row.get("Servidor", "")).strip()
        cpf = str(row.get("CPF", "")).strip()
        vinculo = str(row.get("Vìnculo", "")).strip()
        nivel = str(row.get("Nível Atual", "")).strip().upper()
        data_inicio = row.get("Data do Enquadramento ou da Última Evolução")
        pts_rem = row.get("Pontos Excedentes da Última Evolução")

        # Verificação mínima de integridade
        if not all([nome, cpf, vinculo, nivel, data_inicio]):
            continue

        # Normaliza data e pontos
        try:
            data_inicio = pd.to_datetime(data_inicio, errors="coerce").date()
        except Exception:
            continue

        try:
            pts_rem = float(pts_rem) if pts_rem not in ("", None, "None", "NaT", "Nan") else 0.0
        except Exception:
            pts_rem = 0.0

        data_fim = data_inicio + relativedelta(years=20)

        servidores.append({
            "Servidor": nome,
            "CPF": cpf,
            "Vinculo": vinculo,
            "NivelAtual": nivel,
            "DataInicio": data_inicio,
            "DataFim": data_fim,
            "PontosExcedentes": round(pts_rem, 4),
        })

    if not servidores:
        st.warning("Nenhum servidor válido encontrado na planilha.")
        return []

    return servidores


def processar_afastamentos(df, i, afastamentos_dict, carreira):
    """Lê afastamentos da planilha, aplica descontos e preenche Efetivo Exercício e Desempenho."""
    try:
        mes_falta_raw = str(df["Mês do Afastamento"].iloc[i]).strip()
        qntd_faltas_raw = str(df["Quantitativo de Afastamentos"].iloc[i]).strip()
    except KeyError:
        return carreira  # colunas ausentes

    # Divide em listas (múltiplos afastamentos)
    meses = [m for m in mes_falta_raw.split(";") if m.strip()]
    faltas = [f for f in qntd_faltas_raw.split(";") if f.strip()]

    for mes_str, falta_str in zip(meses, faltas):
        data_mes = pd.to_datetime(mes_str, dayfirst=True, errors="coerce")
        if pd.isna(data_mes):
            continue

        try:
            falta_int = int(float(falta_str))
        except ValueError:
            falta_int = 0

        # aplica no 1º dia do mês seguinte
        if data_mes.month == 12:
            data_aplicacao = date(data_mes.year + 1, 1, 1)
        else:
            data_aplicacao = date(data_mes.year, data_mes.month + 1, 1)

        afastamentos_dict[data_aplicacao] = afastamentos_dict.get(data_aplicacao, 0) + falta_int

    # ---------- aplica afastamentos e desempenho ----------
    for linha in carreira:
        data_atual = linha[0]
        falta = afastamentos_dict.get(data_atual, 0)

        desconto = 0.0067 * falta
        desconto_des = 0.06 * falta

        # Aplica no dia 1 (exceto na data inicial)
        if data_atual.day == 1:
            linha[1] = max(0.2 - desconto, 0)  # Efetivo Exercício
            linha[2] = max(1.8 - desconto_des, 0)  # Desempenho

    return carreira


def processar_titulacoes(df, i, carreira):
    """Aplica pontuação de titulações acadêmicas na matriz da carreira."""
    try:
        mes_raw = str(df["Data de Validação da Titulação"].iloc[i]).strip()
        tipo_raw = str(df["Tipo de Titulação"].iloc[i]).strip()
    except KeyError:
        return carreira  # colunas ausentes

    meses = [m for m in mes_raw.split(";") if m.strip()]
    tipos = [t for t in tipo_raw.split(";") if t.strip()]

    from data_utils_ueg import dados_tit
    dados_cursos = {'PGRAD': 6, 'PDOC1': 6, 'PDOC2': 8, 'PDOC3': 12, 'PDOC4': 24, 'PDOC5': 48 }
    titulacoes = {**dados_tit, **dados_cursos}

    total_pontos_tit = 0
    ultima_titulacao = None
    LIMITE_TIT = 144

    for mes_str, tipo_str in zip(meses, tipos):
        data_conclusao = pd.to_datetime(mes_str, dayfirst=True, errors="coerce")
        if pd.isna(data_conclusao):
            continue

        tipo = tipo_str.strip()
        if not tipo or tipo == "Nenhuma":
            continue

        # Ignora se ocorreu dentro de 12 meses da última titulação
        if ultima_titulacao and data_conclusao < (ultima_titulacao + relativedelta(months=12)):
            continue

        # Data de aplicação = 1º dia do mês seguinte
        if data_conclusao.month == 12:
            data_aplicacao = date(data_conclusao.year + 1, 1, 1)
        else:
            data_aplicacao = date(data_conclusao.year, data_conclusao.month + 1, 1)

        pontos_titulo = titulacoes.get(tipo, 0)
        pontos_restantes = max(0, LIMITE_TIT - total_pontos_tit)
        pontos_aproveitados = min(pontos_titulo, pontos_restantes)

        if pontos_aproveitados <= 0:
            continue

        total_pontos_tit += pontos_aproveitados
        ultima_titulacao = data_conclusao

        for idx, linha in enumerate(carreira):
            if linha[0] == data_aplicacao:
                carreira[idx][4] += pontos_aproveitados  # coluna 4 = Titulação
                break

    return carreira


def processar_responsabilidades_mensais(df, i, carreira, afastamentos_dict, data_inicio, data_fim):
    """Aplica pontos mensais (cargos, funções e atuações) na matriz da carreira."""
    LIMITE_RESP = 144
    pts_acumulado = 0
    resp_dict = {}

    # Mapas de pontos
    pt_cargos = {
        "DAS1": 1.000, "DAS2": 1.000,
        "DAS3": 0.889, "DAS4": 0.889,
        "DAS5": 0.800, "DAS6": 0.800, "DAS7": 0.800, "DAID1A": 0.800, "AEG": 0.800,
        "DAI1": 0.667, "DAID1": 0.667, "DAID1B": 0.667, "DAID2": 0.667, "AE1": 0.667, "AE2": 0.667,
        "DAI2": 0.500, "DAI3": 0.500, "DAID3": 0.500, "DAID4": 0.500, "DAID5": 0.500, "DAID6": 0.500, "DAID7": 0.500,
        "DAID8": 0.500, "DAID9": 0.500, "DAID10": 0.500, "DAID11": 0.500, "DAID12": 0.500,
        "DAID13": 0.500, "DAID14": 0.500
    }
    pt_func_c = {"FCG5": 0.333, "FCG4": 0.364, "FCG3": 0.400, "FCG2": 0.444, "FCG1": 0.500}
    pt_agente = {"GCV": 0.333, "GCIV": 0.364, "GCIII": 0.400, "GCII": 0.444, "GCI": 0.500}
    pt_fixa = {"FD": 0.333, "AP": 0.333, "GT": 0.333, "PE": 0.333}  # usada para designada, conselho e prioritária

    col_map = {
        "Exercício de Cargo em Comissão": pt_cargos,
        "Exercício de Função Comissionada/Gratificada": pt_func_c,
        "Exercício de Função Designada": pt_fixa,
        "Atuação como Agente de Contratação, Gestor/Fiscal de Contratos/Convênios": pt_agente,
        "Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho": pt_fixa,
        "Exercício em Atuação Prioritária": pt_fixa,
        "Execução de Projeto de Ensino, Pesquisa e/ou Extensão com Captação de Recursos": pt_fixa
    }

    for col, mapa in col_map.items():
        if col not in df.columns:
            continue
        texto = str(df[col].iloc[i]).strip()
        if not texto:
            continue
        partes = [p for p in texto.split(";") if p.strip()]
        for bloco in partes:
            dados = bloco.split("-")
            if len(dados) < 3:
                continue
            tipo = dados[0].strip()
            data_i = pd.to_datetime(dados[1].strip(), dayfirst=True, errors="coerce")
            data_f = pd.to_datetime(dados[2].strip(), dayfirst=True, errors="coerce")
            if pd.isna(data_i):
                continue
            data_f = data_f.date() if pd.notna(data_f) else data_fim
            data_i = data_i.date()

            pontos_base = mapa.get(tipo, 0)
            if pontos_base <= 0:
                continue
            
            # ----- ACÚMULO RETROATIVO ----- #
            if data_i < data_inicio and data_i >= data_inicio - relativedelta(years=5):
                delta = relativedelta(data_inicio, data_i)
                meses_anteriores = delta.years * 12 + delta.months

                if meses_anteriores > 0:
                    # Aplica tudo no 1º dia útil da carreira
                    carreira[0][5] += meses_anteriores * pontos_base
            
            ano, mes = data_i.year, data_i.month + 1
            if mes > 12:
                mes, ano = 1, ano + 1

            while date(ano, mes, 1) <= data_f:
                data_aplicacao = date(ano, mes, 1)
                falta = next((f for m, f in afastamentos_dict.items() if m.month == mes and m.year == ano), 0)
                pontos_aj = max(0, pontos_base - ((pontos_base / 30) * falta))

                if data_aplicacao != data_inicio:
                    resp_dict[data_aplicacao] = resp_dict.get(data_aplicacao, 0) + pontos_aj

                mes += 1
                if mes > 12:
                    mes, ano = 1, ano + 1
                if data_aplicacao >= data_f:
                    break

    # aplica acumulado total respeitando limite
    for data_mes, pontos in sorted(resp_dict.items()):
        if pts_acumulado >= LIMITE_RESP:
            break
        pontos = min(pontos, LIMITE_RESP - pts_acumulado)
        for idx, linha in enumerate(carreira):
            if linha[0] == data_mes:
                carreira[idx][5] += pontos
                pts_acumulado += pontos
                break

    return carreira


def processar_responsabilidades_unicas(df, i, carreira):
    """Aplica pontos de responsabilidades únicas (artigos, livros, pesquisas, registros, cursos)."""
    LIMITE_RESP = 144
    total_pontos = 0
    resp_dict = {}

    # Mapas de pontos
    dados_artigo = {"PUBID": 3, "PUBNID": 0.5}
    dados_livro = {"PLO": 1, "PLC": 3, "PLL": 6}
    dados_pesq = {"PUBE": 1, "PUBR": 2, "PUBN": 3, "PUBI": 4}
    dados_reg = {"PAT": 6, "CULT": 6}

    def _aplicar(dicionario, texto_coluna):
        """Divide campo, extrai (quantidade, tipo, data) e acumula pontos."""
        partes = str(texto_coluna).split(";")
        for bloco in partes:
            dados = bloco.strip().split("-")
            if len(dados) < 3:
                continue
            try:
                qtd = int(dados[0])
                tipo = dados[1].strip()
                data_str = dados[2].strip()
                if not tipo or not data_str:
                    continue
                data_concl = datetime.strptime(data_str, "%d/%m/%Y").date()
            except Exception:
                continue

            # Data de aplicação: 1º dia do mês seguinte
            if data_concl.month == 12:
                data_aplicacao = date(data_concl.year + 1, 1, 1)
            else:
                data_aplicacao = date(data_concl.year, data_concl.month + 1, 1)

            pontos = qtd * dicionario.get(tipo, 0)
            if pontos <= 0:
                continue
            resp_dict[data_aplicacao] = resp_dict.get(data_aplicacao, 0) + pontos

    col_map = {
        "Publicação de Artigos ou Pesquisas Científicas com ISSN": dados_artigo,
        "Publicações de Livros com Corpo Editorial e ISBN": dados_livro,
        "Publicações de Artigos ou Pesquisas Científicas Aprovadas em Eventos Científicos": dados_pesq,
        "Registro de Patente ou Cultivar": dados_reg
    }

    for col, mapa in col_map.items():
        if col in df.columns:
            _aplicar(mapa, df[col].iloc[i])

    # Aplica na matriz carreira respeitando o limite
    for data_aplicacao, pontos in sorted(resp_dict.items(), key=lambda x: x[0]):
        if total_pontos + pontos > LIMITE_RESP:
            pontos = max(0, LIMITE_RESP - total_pontos)
        if pontos <= 0:
            continue

        for idx, linha in enumerate(carreira):
            if linha[0] == data_aplicacao:
                carreira[idx][4] += pontos  # coluna 5 = R.Únicas
                total_pontos += pontos
                break

        if total_pontos >= LIMITE_RESP:
            break

    return carreira
