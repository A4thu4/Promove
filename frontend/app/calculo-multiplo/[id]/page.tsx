"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Navbar from '@/components/navbar';
import { BatchResultsTable } from '@/components/simulator/BatchResultsTable';
import { useAuth } from '@/context/auth-context';
import { api } from '@/lib/api';
import type { BatchCalculationOutput } from '@/lib/types';

export default function BatchDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { token, isLoading } = useAuth();

  const [output, setOutput] = useState<BatchCalculationOutput | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoading && !token) {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  useEffect(() => {
    if (!token) return;
    const id = Number(params.id);
    if (!id) {
      setError('ID de lote inválido.');
      setLoading(false);
      return;
    }
    api
      .batchHistoryDetail(id)
      .then(data => {
        setOutput(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err?.message ?? 'Erro ao carregar lote.');
        setLoading(false);
      });
  }, [token, params.id]);

  async function handleExport() {
    if (!output?.id) return;
    try {
      await api.batchExportSaved(output.id);
    } catch (err: any) {
      setError(err?.message ?? 'Erro ao exportar.');
    }
  }

  if (loading || isLoading) {
    return <div className="text-center mt-20">Carregando...</div>;
  }

  return (
    <>
      <Navbar />
      <main className="max-w-6xl mx-auto p-6">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm mb-6">
            {error}
          </div>
        )}

        {output && (
          <>
            <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
              <div>
                <h1 className="text-2xl font-bold">{output.filename}</h1>
                <p className="text-sm text-gray-600">
                  {output.total_linhas} servidor(es) ·{' '}
                  {output.is_ueg ? 'UEG' : 'Geral'}
                  {output.apo_especial ? ' · Aposentadoria Especial' : ''}
                </p>
              </div>
              <button type="button" className="btn-primary" onClick={handleExport}>
                Exportar para Excel
              </button>
            </div>

            <BatchResultsTable output={output} />
          </>
        )}
      </main>
    </>
  );
}
