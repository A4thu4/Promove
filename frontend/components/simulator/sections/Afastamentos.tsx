"use client";

import { useState } from 'react';
import { useSimulator } from '@/context/simulator-context';
import { Card } from '@/components/ui/Card';

export function Afastamentos() {
  const { state, dispatch } = useSimulator();
  const [mes, setMes] = useState('');
  const [dias, setDias] = useState(0);
  const [error, setError] = useState('');

  const disabled = !state.obrigatorios;

  function handleAdd() {
    if (!mes) { setError('Informe o mês.'); return; }
    if (dias <= 0) { setError('Quantidade deve ser maior que zero.'); return; }

    // Verifica duplicata (mesmo mês/ano)
    const [ano, mesNum] = mes.split('-');
    const jaExiste = state.afastamentos.some(a => {
      const [aAno, aMes] = a.data.split('-');
      return aAno === ano && aMes === mesNum;
    });
    if (jaExiste) { setError('Mês já registrado.'); return; }

    setError('');
    dispatch({ type: 'ADD_AFASTAMENTO', payload: { data: mes, dias } });
    setMes(''); setDias(0);
  }

  const totalDias = state.afastamentos.reduce((acc, a) => acc + a.dias, 0);

  return (
    <Card
      title="Afastamentos"
      subtitle="Não considerados como efetivo exercício"
    >
      {disabled && (
        <p className="text-sm text-yellow-600 bg-yellow-50 border border-yellow-200 rounded p-2 mb-3">
          Preencha os dados obrigatórios primeiro.
        </p>
      )}

      <div className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="field-label">Mês / Ano</label>
          <input
            type="month"
            className="field-input"
            value={mes}
            onChange={e => setMes(e.target.value)}
            disabled={disabled}
          />
        </div>
        <div>
          <label className="field-label">Dias Afastados</label>
          <input
            type="number"
            min="1"
            className="field-input w-28"
            value={dias || ''}
            onChange={e => setDias(parseInt(e.target.value) || 0)}
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
        {state.afastamentos.length > 0 && (
          <button
            type="button"
            className="btn-ghost text-red-500"
            onClick={() => dispatch({ type: 'CLEAR_AFASTAMENTOS' })}
          >
            Limpar todos
          </button>
        )}
      </div>

      {error && <p className="field-error mt-2">{error}</p>}

      {state.afastamentos.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-medium text-gray-600 mb-2">
            Total: <strong>{totalDias} dias</strong> afastados
          </p>
          <div className="flex flex-wrap gap-2">
            {[...state.afastamentos]
              .sort((a, b) => a.data.localeCompare(b.data))
              .map(item => (
                <span
                  key={item.id}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 rounded-full text-sm"
                >
                  {item.data.slice(0, 7)} — {item.dias}d
                  <button
                    onClick={() => dispatch({ type: 'REMOVE_AFASTAMENTO', payload: item.id })}
                    className="ml-1 text-gray-400 hover:text-red-500 font-bold"
                  >
                    ×
                  </button>
                </span>
              ))}
          </div>
        </div>
      )}
    </Card>
  );
}