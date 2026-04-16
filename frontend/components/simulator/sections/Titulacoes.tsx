"use client";

import { useState } from 'react';
import { useSimulator } from '@/context/simulator-context';
import { Card } from '@/components/ui/Card';
import { DADOS_TIT_PROMOVE, DADOS_TIT_UEG } from '@/lib/constants';

export function Titulacoes() {
  const { state, dispatch } = useSimulator();
  const tiposDisponiveis = Object.keys(
    state.isUeg ? DADOS_TIT_UEG : DADOS_TIT_PROMOVE
  ).filter(t => t !== 'Nenhuma');

  const [data, setData]   = useState('');
  const [tipo, setTipo]   = useState(tiposDisponiveis[0] ?? '');
  const [error, setError] = useState('');

  const disabled = !state.obrigatorios;

  function handleAdd() {
    if (!data) { setError('Informe a data de validação.'); return; }
    if (!tipo) { setError('Selecione o tipo de titulação.'); return; }

    // Verifica interstício de 12 meses
    const ultimaData = state.titulacoes.length > 0
      ? Math.max(...state.titulacoes.map(t => new Date(t.data).getTime()))
      : null;

    if (ultimaData) {
      const diff = (new Date(data).getTime() - ultimaData) / (1000 * 60 * 60 * 24 * 30);
      if (Math.abs(diff) < 12) {
        setError('Interstício mínimo de 12 meses entre titulações (art. 44, §10).');
        return;
      }
    }

    setError('');
    dispatch({ type: 'ADD_TITULACAO', payload: { data, tipo } });
    setData('');
  }

  return (
    <Card title="Titulações Acadêmicas">
      {disabled && (
        <p className="text-sm text-yellow-600 bg-yellow-50 border border-yellow-200 rounded p-2 mb-3">
          Preencha os dados obrigatórios primeiro.
        </p>
      )}

      <div className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="field-label">Data de Validação</label>
          <input
            type="date"
            className="field-input"
            value={data}
            onChange={e => setData(e.target.value)}
            disabled={disabled}
          />
        </div>
        <div>
          <label className="field-label">Tipo de Titulação</label>
          <select
            className="field-input"
            value={tipo}
            onChange={e => setTipo(e.target.value)}
            disabled={disabled}
          >
            {tiposDisponiveis.map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
        <button
          type="button"
          className="btn-primary"
          onClick={handleAdd}
          disabled={disabled}
        >
          + Adicionar
        </button>
        {state.titulacoes.length > 0 && (
          <button
            type="button"
            className="btn-ghost text-red-500"
            onClick={() => dispatch({ type: 'CLEAR_TITULACOES' })}
          >
            Limpar
          </button>
        )}
      </div>

      {error && <p className="field-error mt-2">{error}</p>}

      {state.titulacoes.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {[...state.titulacoes]
            .sort((a, b) => a.data.localeCompare(b.data))
            .map(t => (
              <span key={t.id} className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 border border-blue-200 rounded-full text-sm text-blue-800">
                {t.data} — {t.tipo}
                <button
                  type="button"
                  aria-label={`Remover titulação ${t.tipo} de ${t.data}`}
                  onClick={() => dispatch({ type: 'REMOVE_TITULACAO', payload: t.id })}
                  className="ml-1 text-blue-400 hover:text-red-500 font-bold"
                >×</button>
              </span>
            ))}
        </div>
      )}
    </Card>
  );
}