from datetime import datetime, date
from typing import Dict, List, Optional

class CareerSettings:
    def __init__(self):
        self.data_conclusao = 150
        self.limite_tit = 144.0
        self.limite_resp = 144.0
        self.pontos_efetivo_mes = 0.2
        self.pontos_desempenho_mes_promove = 1.5
        self.pontos_desempenho_mes_ueg = 1.8
        self.desconto_efetivo_dia = 0.0067
        self.desconto_desempenho_dia_promove = 0.05
        self.desconto_desempenho_dia_ueg = 0.06
        self.niveis = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S']

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

DEFAULT_SETTINGS = CareerSettings()
DEFAULT_REQUIREMENTS = EvolutionRequirement()

# Mapeamento de grupos de responsabilidades (Unificado)
GRUPO_REAL = {
    "C. Comissão": "G1",
    "F. Comissionada": "G1",
    "F. Designada": "G1",
    "At. Agente": "G2",
    "At. Conselho": "G3",
    "At. Prioritária": "G5", # Usando G5 para manter compatibilidade com UEG que tem G4 para Projetos
    "Ex. Projeto": "G4"
}

LIMITES_GRUPO = {
    "G1": 1,
    "G2": 2,
    "G3": 2,
    "G4": 2,
    "G5": 1
}
