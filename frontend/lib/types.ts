export interface Afastamento {
  id: string;
  data: string;
  dias: number;
}

export interface Aperfeicoamento {
  id: string;
  data: string;
  horas: number;
}

export interface Titulacao {
  id: string;
  data: string;
  tipo: string;
}

export interface RespUnica {
  id: string;
  data: string;
  quantidade: number;
  tipo: string;
  categoria: 'artigo' | 'livro' | 'pesquisa' | 'registro' | 'curso';
}

export interface RespMensal {
  id: string;
  tipo: string;       // Ex: "C. Comissão: DAS-1"
  inicio: string;
  fim: string;
  semDataFim: boolean;
  pontos: number;
}

export interface DadosObrigatorios {
  nivelAtual: string;
  dataEnquadramento: string;
  dataInicio: string;
  pontosExcedentes: number;
}

// Payload enviado ao backend
export interface CalculoInput {
  is_ueg: boolean;
  nivel_atual: string;
  data_inicio: string;           // YYYY-MM-DD
  data_enquadramento: string;
  pts_remanescentes: number;
  apo_especial: boolean;
  afastamentos:     { data: string; dias: number }[];
  aperfeicoamentos: { data: string; horas: number }[];
  titulacoes:       { data: string; tipo: string }[];
  resp_unicas:      { data: string; pontos: number }[];
  resp_mensais:     { tipo: string; inicio: string; fim: string; pontos: number }[];
}

// Resposta do backend
export interface EvolutionResult {
  status: string;
  observacao: string;
  proximo_nivel: string;
  data_pontuacao: string;
  data_implementacao: string;
  intersticio: string;
  pontuacao_alcancada: string;
  pontos_excedentes: string;
}

export interface CareerRow {
  data: string;
  efetivo: number;
  desempenho: number;
  aperfeicoamento: number;
  titulacao: number;
  resp_unica: number;
  resp_mensal: number;
  acumulado: number;
}

export interface EvolutionOutput {
  resumo: EvolutionResult;
  carreira: CareerRow[];
}

// ─── Cálculo Múltiplo ────────────────────────────────────────────────────

export interface BatchServidorInfo {
  processo_sei: string;
  servidor: string;
  cpf: string;
  vinculo: string;
}

export interface BatchRowResult {
  info: BatchServidorInfo;
  input: CalculoInput;
  resumo: EvolutionResult;
}

export interface BatchCalculationOutput {
  id?: number | null;
  filename: string;
  total_linhas: number;
  is_ueg: boolean;
  apo_especial: boolean;
  resultados: BatchRowResult[];
}

export interface BatchHistoryItem {
  id: number;
  created_at: string;
  filename: string;
  is_ueg: boolean;
  apo_especial: boolean;
  total_linhas: number;
}