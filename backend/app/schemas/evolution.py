from pydantic import BaseModel
from datetime import date
from typing import List

class AfastamentoSchema(BaseModel):
    data: date
    dias: int

class AperfeicoamentoSchema(BaseModel):
    data: date
    horas: float

class TitulacaoSchema(BaseModel):
    data: date
    tipo: str

class RespUnicaSchema(BaseModel):
    data: date
    pontos: float

class RespMensalSchema(BaseModel):
    tipo: str
    inicio: date
    fim: date
    pontos: float

class EvolutionInput(BaseModel):
    is_ueg: bool
    nivel_atual: str
    data_inicio: date
    data_enquadramento: date
    afastamentos: List[AfastamentoSchema] = []
    aperfeicoamentos: List[AperfeicoamentoSchema] = []
    titulacoes: List[TitulacaoSchema] = []
    resp_unicas: List[RespUnicaSchema] = []
    resp_mensais: List[RespMensalSchema] = []
    pts_remanescentes: float = 0.0
    apo_especial: bool = False

class EvolutionResult(BaseModel):
    status: str
    observacao: str
    proximo_nivel: str
    data_pontuacao: str
    data_implementacao: str
    intersticio: str
    pontuacao_alcancada: str
    pontos_excedentes: str

class CareerRow(BaseModel):
    data: date
    efetivo: float
    desempenho: float
    aperfeicoamento: float
    titulacao: float
    resp_unica: float
    resp_mensal: float
    acumulado: float

class EvolutionOutput(BaseModel):
    resumo: EvolutionResult
    carreira: List[CareerRow]
