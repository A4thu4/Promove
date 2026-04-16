"use client";

import { useSimulator } from '@/context/simulator-context';
import type { CareerRow } from '@/lib/types';

function StatusBadge({ status }: { status: string }) {
  const ok = status === 'Apto a evolução';
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
      ok ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
    }`}>
      {status}
    </span>
  );
}

export function ResultsPanel() {
  const { state } = useSimulator();
  const { resultado, loading, error } = state;

  if (loading) return (
    <div className="text-center py-10 text-gray-500 animate-pulse">
      Calculando...
    </div>
  );

  if (error) return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
      {error}
    </div>
  );

  if (!resultado) return null;

  const { resumo, carreira } = resultado;
  const isApto = resumo.status === 'Apto a evolução';

  return (
    <div className="space-y-6 mt-6">
      {/* Resumo */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-800">Resultado</h2>
          <StatusBadge status={resumo.status} />
        </div>

        {resumo.observacao !== '-' && (
          <p className="text-sm text-orange-700 bg-orange-50 border border-orange-200 rounded p-3 mb-4">
            ⚠️ {resumo.observacao}
          </p>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { label: 'Próximo Nível',   value: resumo.proximo_nivel },
            { label: 'Pontuação',        value: resumo.pontuacao_alcancada },
            { label: 'Pts Excedentes',   value: resumo.pontos_excedentes },
            { label: 'Interstício',      value: `${resumo.intersticio} meses` },
            { label: 'Data Pontuação',   value: resumo.data_pontuacao },
            { label: 'Implementação',    value: resumo.data_implementacao },
          ].map(({ label, value }) => (
            <div key={label} className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500">{label}</p>
              <p className="text-base font-bold text-gray-800 mt-1">{value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Tabela mensal */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800">Pontuações Mensais</h3>
        </div>
        <div className="overflow-x-auto max-h-96">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                {['Data','Ef. Exercício','Desempenho','Aperf.','Titulação','R.Únicas','R.Mensais','Acumulado']
                  .map(h => (
                    <th key={h} className="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">
                      {h}
                    </th>
                  ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {carreira.map((row: CareerRow, i: number) => (
                <tr key={i} className="hover:bg-gray-50 transition-colors">
                  <td className="px-3 py-2 font-medium text-gray-700 whitespace-nowrap">{row.data}</td>
                  <td className="px-3 py-2 text-gray-600">{row.efetivo.toFixed(4)}</td>
                  <td className="px-3 py-2 text-gray-600">{row.desempenho.toFixed(4)}</td>
                  <td className="px-3 py-2 text-gray-600">{row.aperfeicoamento.toFixed(4)}</td>
                  <td className="px-3 py-2 text-gray-600">{row.titulacao.toFixed(4)}</td>
                  <td className="px-3 py-2 text-gray-600">{row.resp_unica.toFixed(4)}</td>
                  <td className="px-3 py-2 text-gray-600">{row.resp_mensal.toFixed(4)}</td>
                  <td className="px-3 py-2 font-semibold text-gray-800">{row.acumulado.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}