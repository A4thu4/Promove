"use client";

import { useState } from 'react';
import { useSimulator } from '@/context/simulator-context';
import { Card } from '@/components/ui/Card';

const MIN_HORAS = 4;
const MAX_HORAS = 100;

export function Aperfeicoamentos() {
  const { state, dispatch } = useSimulator();
  const [data, setData]   = useState('');
  const [horas, setHoras] = useState<number | ''>('');
  const [error, setError] = useState('');

  const disabled    = !state.obrigatorios;
  const totalHoras  = state.aperfeicoamentos.reduce((acc, a) => acc + a.horas, 0);
  const horasRestantes = MAX_HORAS - totalHoras;
  const limitAtingido  = totalHoras >= MAX_HORAS;

  function handleAdd() {
    if (!data)              { setError('Informe a data de validação.'); return; }
    if (!horas || horas < MIN_HORAS) {
      setError(`Carga horária mínima por atividade é ${MIN_HORAS} horas.`);
      return;
    }
    if (state.obrigatorios && data < state.obrigatorios.dataInicio) {
      setError('Data não pode ser anterior à data de início dos pontos.');
      return;
    }

    setError('');
    dispatch({ type: 'ADD_APERFEICOAMENTO', payload: { data, horas: Number(horas) } });
    setData(''); setHoras('');
  }

  return (
    <Card
      title="Aperfeiçoamentos"
      subtitle="Atividades de capacitação — limite de 100 horas por ciclo"
    >
      {disabled && (
        <p className="text-sm text-yellow-600 bg-yellow-50 border border-yellow-200 rounded p-2 mb-3">
          Preencha os dados obrigatórios primeiro.
        </p>
      )}

      {/* Barra de progresso das horas */}
      {state.aperfeicoamentos.length > 0 && (
        <div className="mb-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>{totalHoras}h utilizadas</span>
            <span>{limitAtingido ? 'Limite atingido' : `${horasRestantes}h restantes`}</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                limitAtingido ? 'bg-red-400' : totalHoras >= 80 ? 'bg-yellow-400' : 'bg-green-500'
              }`}
              style={{ width: `${Math.min((totalHoras / MAX_HORAS) * 100, 100)}%` }}
            />
          </div>
          {limitAtingido && (
            <p className="text-xs text-orange-600 mt-1">
              ⚠️ Limite de 100h atingido. Horas excedentes não serão computadas.
            </p>
          )}
        </div>
      )}

      <div className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="field-label">Data de Validação</label>
          <input
            type="date"
            className="field-input"
            value={data}
            onChange={e => setData(e.target.value)}
            disabled={disabled || limitAtingido}
          />
        </div>
        <div>
          <label className="field-label">Carga Horária</label>
          <input
            type="number"
            min={MIN_HORAS}
            step="1"
            placeholder="mín. 4h"
            className="field-input w-32"
            value={horas}
            onChange={e => setHoras(e.target.value === '' ? '' : parseInt(e.target.value))}
            disabled={disabled || limitAtingido}
          />
        </div>
        <button
          type="button"
          className="btn-primary"
          onClick={handleAdd}
          disabled={disabled || limitAtingido}
        >
          + Adicionar
        </button>
        {state.aperfeicoamentos.length > 0 && (
          <button
            type="button"
            className="btn-ghost text-red-500"
            onClick={() => dispatch({ type: 'CLEAR_APERFEICOAMENTOS' })}
          >
            Limpar todos
          </button>
        )}
      </div>

      {error && <p className="field-error mt-2">{error}</p>}

      {state.aperfeicoamentos.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {[...state.aperfeicoamentos]
            .sort((a, b) => a.data.localeCompare(b.data))
            .map(item => (
              <span
                key={item.id}
                className="inline-flex items-center gap-1 px-3 py-1 bg-purple-50 border border-purple-200 rounded-full text-sm text-purple-800"
              >
                {item.data} — {item.horas}h
                <button
                  onClick={() => dispatch({ type: 'REMOVE_APERFEICOAMENTO', payload: item.id })}
                  className="ml-1 text-purple-400 hover:text-red-500 font-bold"
                >×</button>
              </span>
            ))}
        </div>
      )}
    </Card>
  );
}