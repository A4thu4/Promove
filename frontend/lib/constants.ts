
export const NIVEIS     = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S'];
export const NIVEIS_UEG = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O'];

export const DADOS_TIT_PROMOVE: Record<string, number> = {
    'Nenhuma': 0,
    'Graduação': 6,
    'Especialização': 8,
    'Mestrado': 24,
    'Doutorado': 48,
};

export const DADOS_TIT_UEG: Record<string, number> = {
    ...DADOS_TIT_PROMOVE,
    'Pós-graduação em Nível de Certificação': 6,
    'Pós-doutorado – igual a 6 meses': 6,
    'Pós-doutorado - (6 a 12 meses)': 8,
    'Pós-doutorado - (13 a 24 meses)': 12,
    'Pós-doutorado - (25 a 48 meses)': 24,
    'Pós-doutorado - (maior ou igual a 48 meses)': 48,
};

export const DADOS_CARGOS: Record<string, number> = {
    'Nenhum': 0,
    'DAS-1': 1.000, 'DAS-2': 1.000,
    'DAS-3': 0.889, 'DAS-4': 0.889,
    'DAS-5': 0.800, 'DAS-6': 0.800, 'DAS-7': 0.800, 'DAID-1A': 0.800, 'AEG': 0.800,
    'DAI-1': 0.667, 'DAID-1': 0.667, 'DAID-1B': 0.667, 'DAID-2': 0.667, 'AE-1': 0.667, 'AE-2': 0.667,
    'DAI-2': 0.500, 'DAI-3': 0.500, 'DAID-3': 0.500, 'DAID-4': 0.500, 'DAID-5': 0.500,
    'DAID-6': 0.500, 'DAID-7': 0.500, 'DAID-8': 0.500, 'DAID-9': 0.500, 'DAID-10': 0.500,
    'DAID-11': 0.500, 'DAID-12': 0.500, 'DAID-13': 0.500, 'DAID-14': 0.500,
};

export const DADOS_FUNC_C: Record<string, number> = {
    'Nenhum': 0,
    'até R$ 750,00': 0.333,
    '751,00 - 1.200,00': 0.364,
    '1.201,00 - 1.650,00': 0.400,
    '1.651,00 - 2.250,00': 0.444,
    'acima de 2.250,00': 0.500,
};

export const DADOS_AGENTE: Record<string, number> = {
    'Nenhum': 0,
    'I': 0.500,
    'II': 0.444,
    'III': 0.400,
    'IV': 0.364,
    'V': 0.333,
};

export const DADOS_UNICOS: Record<string, number> = {
    'Nenhum': 0,
    'Houve': 0.333,
};

export const DADOS_ARTIGO: Record<string, number> = {
    'Nenhum': 0,
    'Indexado em Base de Dados': 3,
    'Não Indexado em Base de Dados': 0.5,
};

export const DADOS_LIVRO: Record<string, number> = {
    'Nenhum': 0,
    'Organizador de Livro': 1,
    'Capítulo de Livro': 3,
    'Livro Completo': 6,
};

export const DADOS_PESQUISAS: Record<string, number> = {
    'Nenhum': 0,
    'Estadual': 1,
    'Regional': 2,
    'Nacional': 3,
    'Internacional': 4,
};

export const DADOS_REGISTROS: Record<string, number> = {
    'Nenhum': 0,
    'Patente': 6,
    'Cultivar': 6,
};

export const DADOS_CURSOS: Record<string, number> = {
  'Nenhum': 0,
  'Pós-doutorado – igual a 6 meses': 6,
  'Pós-doutorado - (6 a 12 meses)': 8,
  'Pós-doutorado - (13 a 24 meses)': 12,
  'Pós-doutorado - (25 a 48 meses)': 24,
  'Pós-doutorado - (maior ou igual a 48 meses)': 48,
};