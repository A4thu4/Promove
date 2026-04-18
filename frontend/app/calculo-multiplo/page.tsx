"use client";

import { useState } from 'react';
import Link from 'next/link';
import Navbar from '@/components/navbar';
import { BatchResultsTable } from '@/components/simulator/BatchResultsTable';
import { useAuth } from '@/context/auth-context';
import { api } from '@/lib/api';
import type { BatchCalculationOutput } from '@/lib/types';

export default function CalculoMultiploPage() {
  const { token } = useAuth();

  const [file, setFile] = useState<File | null>(null);
  const [isUeg, setIsUeg] = useState(false);
  const [apoEspecial, setApoEspecial] = useState(false);

  const [resultado, setResultado] = useState<BatchCalculationOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'simulate' | 'save' | null>(null);

  async function run(saveToHistory: boolean) {
    if (!file) {
      setError('Selecione uma planilha Excel (.xlsx) primeiro.');
      return;
    }
    setLoading(true);
    setError(null);
    setMode(saveToHistory ? 'save' : 'simulate');
    try {
      const output = saveToHistory
        ? await api.batchCalculateAndSave(file, isUeg, apoEspecial)
        : await api.batchCalculate(file, isUeg, apoEspecial);
      setResultado(output);
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao processar planilha.');
      setResultado(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleExport() {
    if (!resultado) return;
    try {
      if (resultado.id) {
        await api.batchExportSaved(resultado.id);
      } else {
        await api.batchExportFromOutput(resultado);
      }
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao exportar.');
    }
  }

  return (
    <>
      <Navbar />
      <main className="max-w-6xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-2">Cálculo Múltiplo</h1>
        <p className="text-sm text-gray-600 mb-6">
          Envie uma planilha Excel (.xlsx) com uma linha por servidor. O sistema
          processará todos e permitirá exportar os resultados.
        </p>

        <div className="p-3 mb-6 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm">
          ⚠️ Ferramenta de simulação. Os resultados não têm valor oficial.
          Use o modelo de planilha publicado pela SEAD.
        </div>

        <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 space-y-4">
          <div>
            <label className="field-label">Planilha (.xlsx, .xls, .xlsm)</label>
            <input
              type="file"
              accept=".xlsx,.xls,.xlsm"
              onChange={e => setFile(e.target.files?.[0] ?? null)}
              className="block w-full text-sm"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <fieldset>
              <legend className="field-label">Carreira</legend>
              <label className="inline-flex items-center gap-2 mr-4">
                <input
                  type="radio"
                  name="carreira"
                  checked={!isUeg}
                  onChange={() => setIsUeg(false)}
                />
                GERAL
              </label>
              <label className="inline-flex items-center gap-2">
                <input
                  type="radio"
                  name="carreira"
                  checked={isUeg}
                  onChange={() => setIsUeg(true)}
                />
                UEG
              </label>
            </fieldset>

            <fieldset>
              <legend className="field-label">Aposentadoria Especial</legend>
              <label className="inline-flex items-center gap-2 mr-4">
                <input
                  type="radio"
                  name="apo"
                  checked={!apoEspecial}
                  onChange={() => setApoEspecial(false)}
                />
                Não
              </label>
              <label className="inline-flex items-center gap-2">
                <input
                  type="radio"
                  name="apo"
                  checked={apoEspecial}
                  onChange={() => setApoEspecial(true)}
                />
                Sim
              </label>
            </fieldset>
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              type="button"
              className="btn-primary"
              onClick={() => run(false)}
              disabled={loading || !file}
            >
              {loading && mode === 'simulate' ? 'Processando...' : 'Simular'}
            </button>
            {token && (
              <button
                type="button"
                className="btn-primary bg-green-600 hover:bg-green-700"
                onClick={() => run(true)}
                disabled={loading || !file}
              >
                {loading && mode === 'save' ? 'Processando...' : 'Calcular e Salvar'}
              </button>
            )}
            {!token && (
              <span className="text-xs text-gray-500">
                Faça login para salvar o lote no seu histórico.
              </span>
            )}
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        {resultado && (
          <section className="mt-8 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold">
                  Resultado: {resultado.filename}
                </h2>
                <p className="text-sm text-gray-600">
                  {resultado.total_linhas} servidor(es) processado(s)
                  {resultado.id ? ` · lote #${resultado.id} salvo no histórico` : ''}
                </p>
              </div>
              <div className="flex gap-2">
                <button type="button" className="btn-primary" onClick={handleExport}>
                  Exportar para Excel
                </button>
                {resultado.id && (
                  <Link href="/dashboard" className="btn-ghost">
                    Ver no histórico
                  </Link>
                )}
              </div>
            </div>

            <BatchResultsTable output={resultado} />
          </section>
        )}
      </main>
    </>
  );
}
