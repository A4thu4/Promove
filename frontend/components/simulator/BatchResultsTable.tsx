"use client";

import { useRouter } from 'next/navigation';
import type { BatchCalculationOutput } from '@/lib/types';
import { batchRowToHydrate, stashPendingBatchInput } from '@/lib/batch-handoff';

interface Props {
  output: BatchCalculationOutput;
}

export function BatchResultsTable({ output }: Props) {
  const router = useRouter();

  function openInSimulator(rowIndex: number) {
    const row = output.resultados[rowIndex];
    stashPendingBatchInput(batchRowToHydrate(row));
    router.push('/');
  }

  if (output.resultados.length === 0) {
    return (
      <p className="text-sm text-gray-500 italic">
        Nenhuma linha foi encontrada.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto border border-gray-200 rounded-lg">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-100 text-gray-700">
          <tr>
            <th className="text-left px-3 py-2">Status</th>
            <th className="text-left px-3 py-2">Servidor</th>
            <th className="text-left px-3 py-2">CPF</th>
            <th className="text-left px-3 py-2">Vínculo</th>
            <th className="text-left px-3 py-2">Próximo Nível</th>
            <th className="text-left px-3 py-2">Implementação</th>
            <th className="text-left px-3 py-2">Pontuação</th>
            <th className="text-left px-3 py-2">Observação</th>
            <th className="text-left px-3 py-2">Ações</th>
          </tr>
        </thead>
        <tbody>
          {output.resultados.map((r, idx) => {
            const apto = r.resumo.status === 'Apto a evolução';
            return (
              <tr key={idx} className="border-t border-gray-100">
                <td className="px-3 py-2 align-top">
                  <span
                    className={`inline-block px-2 py-0.5 rounded-full text-xs font-semibold ${
                      apto
                        ? 'bg-green-100 text-green-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}
                  >
                    {r.resumo.status}
                  </span>
                </td>
                <td className="px-3 py-2 align-top">{r.info.servidor || '-'}</td>
                <td className="px-3 py-2 align-top">{r.info.cpf || '-'}</td>
                <td className="px-3 py-2 align-top">{r.info.vinculo || '-'}</td>
                <td className="px-3 py-2 align-top">{r.resumo.proximo_nivel}</td>
                <td className="px-3 py-2 align-top">{r.resumo.data_implementacao}</td>
                <td className="px-3 py-2 align-top">{r.resumo.pontuacao_alcancada}</td>
                <td className="px-3 py-2 align-top text-gray-600">{r.resumo.observacao}</td>
                <td className="px-3 py-2 align-top">
                  <button
                    type="button"
                    className="text-primary-600 hover:underline text-xs"
                    onClick={() => openInSimulator(idx)}
                  >
                    Abrir no simulador
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
