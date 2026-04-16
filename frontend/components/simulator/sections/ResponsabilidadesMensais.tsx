"use client";

import { useState } from 'react';
import { useSimulator } from '@/context/simulator-context';
import { Card } from '@/components/ui/Card';
import {
  DADOS_CARGOS,
  DADOS_FUNC_C,
  DADOS_AGENTE,
  DADOS_UNICOS,
} from '@/lib/constants';

// ── Tipos internos ─────────────────────────────────────────────────────────────

interface SubSectionConfig {
  label:      string;
  tipoBase:   string;          // prefixo usado em GRUPO_REAL do backend
  opcoes:     Record<string, number>;
}

// ── Configuração das sub-seções ────────────────────────────────────────────────
// Aqui habilita/desabilita seções por carreira

function getSubSections(isUeg: boolean): SubSectionConfig[] {
  const base: SubSectionConfig[] = [
    {
      label:      'Exercício de Cargo em Comissão',
      tipoBase:   'C. Comissão',
      opcoes:     DADOS_CARGOS,
    },
    {
      label:      'Exercício de Função Comissionada/Gratificada',
      tipoBase:   'F. Comissionada',
      opcoes:     DADOS_FUNC_C,
    },
    {
      label:      'Exercício de Função Designada',
      tipoBase:   'F. Designada',
      opcoes:     DADOS_UNICOS,
    },
    {
      label:      'Atuação como Agente de Contratação / Gestor/Fiscal de Contratos',
      tipoBase:   'At. Agente',
      opcoes:     DADOS_AGENTE,
    },
    {
      label:      'Atuação em Conselho, Comitê, Câmara Técnica, Comissão ou Grupo de Trabalho',
      tipoBase:   'At. Conselho',
      opcoes:     DADOS_UNICOS,
    },
    {
      label:      'Exercício em Atuação Prioritária',
      tipoBase:   'At. Prioritária',
      opcoes:     DADOS_UNICOS,
    },
  ];

  if (isUeg) {
    base.push({
      label:      'Execução de Projeto de Ensino, Pesquisa e/ou Extensão com Captação de Recursos',
      tipoBase:   'Ex. Projeto',
      opcoes:     DADOS_UNICOS,
    });
  }

  return base;
}

// ── Sub-componente de cada seção ───────────────────────────────────────────────

interface SubSectionProps {
  config:   SubSectionConfig;
  disabled: boolean;
  dataFim:  string;           // data_fim padrão (20 anos após início)
}

function RespMensalSubSection({ config, disabled, dataFim }: SubSectionProps) {
  const { state, dispatch } = useSimulator();

  const opcaoKeys = Object.keys(config.opcoes).filter(k => k !== 'Nenhum');

  const [simbolo,     setSimb]     = useState(opcaoKeys[0] ?? '');
  const [dataInicio,  setDI]       = useState('');
  const [dataFimLocal,setDF]       = useState('');
  const [semDataFim,  setSDF]      = useState(false);
  const [error,       setError]    = useState('');

  const dfEfetivo = semDataFim ? dataFim : dataFimLocal;

  function handleAdd() {
    if (!simbolo || simbolo === 'Nenhum') { setError('Selecione uma opção válida.'); return; }
    if (!dataInicio)                       { setError('Informe a data de início.'); return; }
    if (!dfEfetivo)                        { setError('Informe a data de fim ou marque "Sem data fim".'); return; }
    if (dfEfetivo <= dataInicio)           { setError('Data de fim deve ser posterior à data de início.'); return; }

    const pontos = config.opcoes[simbolo] ?? 0;
    if (pontos === 0) { setError('Tipo selecionado não possui pontuação.'); return; }

    setError('');
    dispatch({
      type:    'ADD_RESP_MENSAL',
      payload: {
        tipo:       `${config.tipoBase}: ${simbolo}`,
        inicio:     dataInicio,
        fim:        dfEfetivo,
        semDataFim,
        pontos,
      },
    });

    setSimb(opcaoKeys[0] ?? '');
    setDI(''); setDF(''); setSDF(false);
  }

  // Filtra apenas as responsabilidades desta sub-seção para exibição
  const itensDestaSessao = state.respMensais.filter(r =>
    r.tipo.startsWith(config.tipoBase + ':')
  );

  return (
    <div className="border-t border-gray-100 pt-4 mt-4 first:border-0 first:pt-0 first:mt-0">
      <h4 className="text-sm font-semibold text-gray-700 mb-3">{config.label}</h4>

      <div className="flex flex-wrap gap-3 items-end">
        {/* Select de opção */}
        <div>
          <label className="field-label">
            {config.tipoBase === 'C. Comissão' ? 'Símbolo' :
             config.tipoBase === 'At. Agente'  ? 'Faixa'   : 'Selecione'}
          </label>
          <select
            className="field-input"
            value={simbolo}
            onChange={e => setSimb(e.target.value)}
            disabled={disabled}
          >
            {opcaoKeys.map(k => (
              <option key={k} value={k}>{k}</option>
            ))}
          </select>
        </div>

        {/* Data início */}
        <div>
          <label className="field-label">Data de Início</label>
          <input
            type="date"
            className="field-input"
            value={dataInicio}
            onChange={e => setDI(e.target.value)}
            disabled={disabled}
          />
        </div>

        {/* Data fim */}
        <div>
          <label className="field-label">Data de Fim</label>
          <input
            type="date"
            className="field-input"
            value={dataFimLocal}
            onChange={e => setDF(e.target.value)}
            disabled={disabled || semDataFim}
          />
        </div>

        {/* Sem data fim */}
        <label className="flex items-center gap-2 cursor-pointer pb-2 text-sm text-gray-600 select-none">
          <input
            type="checkbox"
            className="w-4 h-4 accent-green-600"
            checked={semDataFim}
            onChange={e => setSDF(e.target.checked)}
            disabled={disabled}
          />
          Sem data fim
        </label>

        <button
          type="button"
          className="btn-primary"
          onClick={handleAdd}
          disabled={disabled}
        >
          + Adicionar
        </button>
      </div>

      {error && <p className="field-error mt-2">{error}</p>}

      {/* Lista dos itens desta sub-seção */}
      {itensDestaSessao.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {itensDestaSessao.map(item => {
            // Calcula tempo em meses para exibição
            const ini = new Date(item.inicio);
            const fim = new Date(item.fim);
            const meses = (fim.getFullYear() - ini.getFullYear()) * 12
                        + (fim.getMonth() - ini.getMonth());
            return (
              <span
                key={item.id}
                className="inline-flex items-center gap-1 px-3 py-1 bg-indigo-50 border border-indigo-200 rounded-full text-xs text-indigo-800"
              >
                {item.tipo.split(': ')[1]} — {meses}m
                {item.semDataFim && ' (em curso)'}
                <button
                  type="button"
                  aria-label={`Remover ${item.tipo.split(': ')[1]}`}
                  onClick={() => dispatch({ type: 'REMOVE_RESP_MENSAL', payload: item.id })}
                  className="ml-1 text-indigo-400 hover:text-red-500 font-bold text-sm leading-none"
                >×</button>
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ── Componente principal ───────────────────────────────────────────────────────

export function ResponsabilidadesMensais() {
  const { state, dispatch } = useSimulator();
  const disabled = !state.obrigatorios;

  // Data fim padrão = 20 anos após o início
  const dataFimDefault = state.obrigatorios
    ? (() => {
        const d = new Date(state.obrigatorios.dataInicio);
        d.setFullYear(d.getFullYear() + 20);
        return d.toISOString().split('T')[0];
      })()
    : '';

  const subSections  = getSubSections(state.isUeg);
  const totalMensais = state.respMensais.length;

  return (
    <Card
      title="Responsabilidades — Pontuação Mensal"
      subtitle="Pontos proporcionais ao período de exercício"
    >
      {disabled && (
        <p className="text-sm text-yellow-600 bg-yellow-50 border border-yellow-200 rounded p-2 mb-3">
          Preencha os dados obrigatórios primeiro.
        </p>
      )}

      {totalMensais > 0 && (
        <div className="flex items-center justify-between mb-4 p-2 bg-indigo-50 rounded-lg">
          <span className="text-sm text-indigo-700 font-medium">
            {totalMensais} responsabilidade(s) mensal(is) registrada(s)
          </span>
          <button
            type="button"
            className="text-xs text-red-500 hover:text-red-700"
            onClick={() => dispatch({ type: 'CLEAR_RESP_MENSAIS' })}
          >
            Limpar todas
          </button>
        </div>
      )}

      {subSections.map(config => (
        <RespMensalSubSection
          key={config.tipoBase}
          config={config}
          disabled={disabled}
          dataFim={dataFimDefault}
        />
      ))}
    </Card>
  );
}