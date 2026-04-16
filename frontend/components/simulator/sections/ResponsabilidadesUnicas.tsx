"use client";

import { useState } from 'react';
import { useSimulator } from '@/context/simulator-context';
import { Card } from '@/components/ui/Card';
import {
  DADOS_ARTIGO,
  DADOS_LIVRO,
  DADOS_PESQUISAS,
  DADOS_REGISTROS,
  DADOS_CURSOS,
  DECRETO_DATE,
} from '@/lib/constants';
import type { RespUnica } from '@/lib/types';

// ── Configuração das sub-seções ────────────────────────────────────────────────

interface UnicoConfig {
  label:     string;
  categoria: RespUnica['categoria'];
  opcoes:    Record<string, number>;
  dataMin:   'enquadramento' | 'decreto';  // de onde parte a data mínima
}

function getSubSections(isUeg: boolean): UnicoConfig[] {
  const base: UnicoConfig[] = [
    {
      label:     'Publicação de Artigos ou Pesquisas Científicos com ISSN',
      categoria: 'artigo',
      opcoes:    DADOS_ARTIGO,
      dataMin:   'enquadramento',
    },
    {
      label:     'Publicações de Livros com Corpo Editorial e ISBN',
      categoria: 'livro',
      opcoes:    DADOS_LIVRO,
      dataMin:   'decreto',
    },
    {
      label:     'Artigos ou Pesquisas Aprovados em Eventos Científicos',
      categoria: 'pesquisa',
      opcoes:    DADOS_PESQUISAS,
      dataMin:   'decreto',
    },
    {
      label:     'Registro de Patente ou Cultivar',
      categoria: 'registro',
      opcoes:    DADOS_REGISTROS,
      dataMin:   'decreto',
    },
  ];

  // Pós-doc só existe no GERAL
  if (!isUeg) {
    base.push({
      label:     'Estágio Pós-doutoral Desenvolvido no Órgão',
      categoria: 'curso',
      opcoes:    DADOS_CURSOS,
      dataMin:   'decreto',
    });
  }

  return base;
}

// ── Sub-componente ─────────────────────────────────────────────────────────────

interface SubUnicaProps {
  config:            UnicoConfig;
  disabled:          boolean;
  dataEnquadramento: string;
}

function RespUnicaSubSection({ config, disabled, dataEnquadramento }: SubUnicaProps) {
  const { state, dispatch } = useSimulator();

  const opcaoKeys = Object.keys(config.opcoes).filter(k => k !== 'Nenhum');

  const [tipo,       setTipo]  = useState(opcaoKeys[0] ?? '');
  const [quantidade, setQtd]   = useState<number | ''>('');
  const [data,       setData]  = useState('');
  const [error,      setError] = useState('');

  const dataMinima = config.dataMin === 'enquadramento'
    ? dataEnquadramento
    : DECRETO_DATE;

  function handleAdd() {
    if (!tipo || tipo === 'Nenhum')         { setError('Selecione uma faixa válida.'); return; }
    if (!quantidade || quantidade < 1)      { setError('Quantidade mínima é 1.'); return; }
    if (!data)                              { setError('Informe a data de validação.'); return; }
    if (dataMinima && data < dataMinima)    { setError(`Data não pode ser anterior a ${dataMinima}.`); return; }

    const pontos = config.opcoes[tipo] ?? 0;
    if (pontos === 0) { setError('Tipo selecionado não possui pontuação.'); return; }

    setError('');
    dispatch({
      type:    'ADD_RESP_UNICA',
      payload: {
        data,
        quantidade: Number(quantidade),
        tipo,
        categoria: config.categoria,
      },
    });

    setTipo(opcaoKeys[0] ?? '');
    setQtd(''); setData('');
  }

  // Apenas itens desta categoria
  const itensDesta = state.respUnicas.filter(r => r.categoria === config.categoria);

  // Total de pontos desta categoria (para exibição)
  const ptsDesta = itensDesta.reduce(
    (acc, r) => acc + r.quantidade * (config.opcoes[r.tipo] ?? 0),
    0
  );

  return (
    <div className="border-t border-gray-100 pt-4 mt-4 first:border-0 first:pt-0 first:mt-0">
      <h4 className="text-sm font-semibold text-gray-700 mb-3">{config.label}</h4>

      <div className="flex flex-wrap gap-3 items-end">
        {/* Faixa/tipo */}
        <div>
          <label className="field-label">Faixa</label>
          <select
            className="field-input"
            value={tipo}
            onChange={e => setTipo(e.target.value)}
            disabled={disabled}
          >
            {opcaoKeys.map(k => (
              <option key={k} value={k}>{k}</option>
            ))}
          </select>
        </div>

        {/* Quantidade */}
        <div>
          <label className="field-label">Quantidade</label>
          <input
            type="number"
            min="1"
            step="1"
            className="field-input w-28"
            placeholder="ex: 2"
            value={quantidade}
            onChange={e => setQtd(e.target.value === '' ? '' : parseInt(e.target.value))}
            disabled={disabled}
          />
        </div>

        {/* Data */}
        <div>
          <label className="field-label">Data de Validação</label>
          <input
            type="date"
            className="field-input"
            value={data}
            min={dataMinima}
            onChange={e => setData(e.target.value)}
            disabled={disabled}
          />
        </div>

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

      {/* Itens registrados */}
      {itensDesta.length > 0 && (
        <div className="mt-3">
          <p className="text-xs text-gray-500 mb-2">
            {itensDesta.length} item(s) — <strong>{ptsDesta.toFixed(1)} pts</strong>
          </p>
          <div className="flex flex-wrap gap-2">
            {[...itensDesta]
              .sort((a, b) => a.data.localeCompare(b.data))
              .map(item => (
                <span
                  key={item.id}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-teal-50 border border-teal-200 rounded-full text-xs text-teal-800"
                >
                  {item.data} — {item.quantidade}× {item.tipo}
                  <span className="text-teal-500 ml-1">
                    (+{(item.quantidade * (config.opcoes[item.tipo] ?? 0)).toFixed(1)}pts)
                  </span>
                  <button
                    type="button"
                    aria-label={`Remover item ${item.data} — ${item.quantidade}× ${item.tipo}`}
                    onClick={() => dispatch({ type: 'REMOVE_RESP_UNICA', payload: item.id })}
                    className="ml-1 text-teal-400 hover:text-red-500 font-bold text-sm leading-none"
                  >×</button>
                </span>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Componente principal ───────────────────────────────────────────────────────

export function ResponsabilidadesUnicas() {
  const { state, dispatch } = useSimulator();
  const disabled = !state.obrigatorios;

  const dataEnquad   = state.obrigatorios?.dataEnquadramento ?? '';
  const subSections  = getSubSections(state.isUeg);
  const totalUnicas  = state.respUnicas.length;

  // Mapa completo de pontos para calcular o total geral
  const todosDados   = {
    ...DADOS_ARTIGO, ...DADOS_LIVRO,
    ...DADOS_PESQUISAS, ...DADOS_REGISTROS, ...DADOS_CURSOS,
  };
  const ptsTotal = state.respUnicas.reduce(
    (acc, r) => acc + r.quantidade * (todosDados[r.tipo] ?? 0),
    0
  );

  return (
    <Card
      title="Responsabilidades — Pontuação Única"
      subtitle="Produções científicas, publicações e registros"
    >
      {disabled && (
        <p className="text-sm text-yellow-600 bg-yellow-50 border border-yellow-200 rounded p-2 mb-3">
          Preencha os dados obrigatórios primeiro.
        </p>
      )}

      {totalUnicas > 0 && (
        <div className="flex items-center justify-between mb-4 p-2 bg-teal-50 rounded-lg">
          <span className="text-sm text-teal-700 font-medium">
            {totalUnicas} item(s) — total de <strong>{ptsTotal.toFixed(1)} pts</strong>
          </span>
          <button
            type="button"
            className="text-xs text-red-500 hover:text-red-700"
            onClick={() => dispatch({ type: 'CLEAR_RESP_UNICAS' })}
          >
            Limpar todos
          </button>
        </div>
      )}

      {subSections.map(config => (
        <RespUnicaSubSection
          key={config.categoria}
          config={config}
          disabled={disabled}
          dataEnquadramento={dataEnquad}
        />
      ))}
    </Card>
  );
}