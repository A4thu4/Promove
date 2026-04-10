class CareerSettings:
    def __init__(self):
        self.data_conclusao = 241
        self.limite_tit = 144.0
        self.limite_resp = 144.0
        self.pontos_efetivo_mes = 0.2
        self.pontos_desempenho_mes = 1.5
        self.pontos_desempenho_mes_ueg = 1.8
        self.desconto_efetivo_dia = 0.0067
        self.desconto_desempenho_dia = 0.05
        self.desconto_desempenho_dia_ueg = 0.06
        self.niveis = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']
        self.niveis_ueg = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O']

class EvolutionRequirement:
    def __init__(self):
        self.min_points_level_1 = 48.0
        self.min_points_level_2 = 96.0
        self.min_months_level_1 = 18
        self.min_months_level_2 = 12
        self.min_months_special = 15
        self.min_hours_level_1 = 60.0
        self.min_hours_level_2 = 40.0
        self.points_per_hour = 0.09
        self.min_desempenho_points = 2.4
        self.min_desempenho_points_ueg = 3.6

DEFAULT_SETTINGS = CareerSettings()
DEFAULT_REQUIREMENTS = EvolutionRequirement()

# Mapeamento de grupos de responsabilidades (Unificado)
# G1 = cargo/função comissionada/designada (limite 1 por mês)
# G2 = agente de contratação (limite 2)
# G3 = conselho/comitê (limite 2)
# G4 = execução de projeto (UEG, limite 2)
# G5 = atuação prioritária (limite 1, separado do G1)
GRUPO_REAL = {
    "C. Comissão": "G1",
    "F. Comissionada": "G1",
    "F. Designada": "G1",
    "At. Agente": "G2",
    "At. Conselho": "G3",
    "Ex. Projeto": "G4",
    "At. Prioritária": "G5",
}

LIMITES_GRUPO = {
    "G1": 1,
    "G2": 2,
    "G3": 2,
    "G4": 2,
    "G5": 1,
}
