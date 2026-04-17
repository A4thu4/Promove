"""
Tabelas de símbolos → pontos usadas para interpretar a planilha Excel do
fluxo de Cálculo Múltiplo. Os símbolos curtos (DAS1, FCG5, PUBID, ...) são
os mesmos adotados pelo app antigo em Streamlit; aqui eles são convertidos
para os rótulos esperados pelo motor de cálculo atual.
"""

# ---- Responsabilidades Mensais ----
pt_cargos = {
    "DAS1": 1.000, "DAS2": 1.000,
    "DAS3": 0.889, "DAS4": 0.889,
    "DAS5": 0.800, "DAS6": 0.800, "DAS7": 0.800, "DAID1A": 0.800, "AEG": 0.800,
    "DAI1": 0.667, "DAID1": 0.667, "DAID1B": 0.667, "DAID2": 0.667,
    "AE1": 0.667, "AE2": 0.667,
    "DAI2": 0.500, "DAI3": 0.500, "DAID3": 0.500, "DAID4": 0.500, "DAID5": 0.500,
    "DAID6": 0.500, "DAID7": 0.500, "DAID8": 0.500, "DAID9": 0.500, "DAID10": 0.500,
    "DAID11": 0.500, "DAID12": 0.500, "DAID13": 0.500, "DAID14": 0.500,
}

pt_func_c = {
    "FCG5": 0.333,
    "FCG4": 0.364,
    "FCG3": 0.400,
    "FCG2": 0.444,
    "FCG1": 0.500,
}

pt_agente = {
    "GCV": 0.333,
    "GCIV": 0.364,
    "GCIII": 0.400,
    "GCII": 0.444,
    "GCI": 0.500,
}

pt_fixa = {"FD": 0.333, "AP": 0.333, "GT": 0.333}

# coluna da planilha -> (tipo_base esperado pelo motor, mapa de pontos)
COLUNAS_RESP_MENSAIS = {
    "Exercício de Cargo em Comissão": ("C. Comissão", pt_cargos),
    "Exercício de Função Comissionada/Gratificada": ("F. Comissionada", pt_func_c),
    "Exercício de Função Designada": ("F. Designada", pt_fixa),
    "Atuação como Agente de Contratação, Gestor/Fiscal de Contratos/Convênios": ("At. Agente", pt_agente),
    "Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho": ("At. Conselho", pt_fixa),
    "Exercício em Atuação Prioritária": ("At. Prioritária", pt_fixa),
}

# ---- Responsabilidades Únicas ----
dados_artigo = {"PUBID": 3, "PUBNID": 0.5}
dados_livro = {"PLO": 1, "PLC": 3, "PLL": 6}
dados_pesq = {"PUBE": 1, "PUBR": 2, "PUBN": 3, "PUBI": 4}
dados_reg = {"PAT": 6, "CULT": 6}
dados_curso = {"PDOC1": 6, "PDOC2": 8, "PDOC3": 12, "PDOC4": 24, "PDOC5": 48}

COLUNAS_RESP_UNICAS = {
    "Publicação de Artigos ou Pesquisas Científicas com ISSN": dados_artigo,
    "Publicações de Livros com Corpo Editorial e ISBN": dados_livro,
    "Publicações de Artigos ou Pesquisas Científicas Aprovadas em Eventos Científicos": dados_pesq,
    "Registro de Patente ou Cultivar": dados_reg,
    "Estágio Pós-doutoral Desenvolvido no Órgão": dados_curso,
}

# ---- Titulações (rótulos longos já aceitos pelo motor) ----
TIPOS_TITULACAO_PROMOVE = {
    "Nenhuma", "Graduação", "Especialização", "Mestrado", "Doutorado",
}
TIPOS_TITULACAO_UEG = TIPOS_TITULACAO_PROMOVE | {
    "Pós-graduação em Nível de Certificação",
    "Pós-doutorado – igual a 6 meses",
    "Pós-doutorado - (6 a 12 meses)",
    "Pós-doutorado - (13 a 24 meses)",
    "Pós-doutorado - (25 a 48 meses)",
    "Pós-doutorado - (maior ou igual a 48 meses)",
}

COLUNAS_OBRIGATORIAS = [
    "Servidor", "CPF", "Vínculo", "Nível Atual",
    "Data do Enquadramento", "Data de Início dos Pontos",
    "Pontos Excedentes da Última Evolução",
]
