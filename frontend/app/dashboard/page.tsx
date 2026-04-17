"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import Navbar from "@/components/navbar";
import { api } from "@/lib/api";
import type { BatchHistoryItem } from "@/lib/types";

export default function Page() {
  const { token, isLoading } = useAuth();
  const [history, setHistory] = useState<any[]>([]);
  const [batchHistory, setBatchHistory] = useState<BatchHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !token) {
      router.push("/login");
    }
  }, [token, isLoading, router]);

  useEffect(() => {
    if (!token) return;
    Promise.all([api.history(), api.batchHistory()])
      .then(([individual, batch]) => {
        setHistory(individual);
        setBatchHistory(batch);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [token]);

  if (isLoading || loading) {
    return <div className="text-center mt-20">Carregando...</div>;
  }

  return (
    <>
      <Navbar />
      <main className="max-w-4xl mx-auto p-6 space-y-10">
        <section>
          <h1 className="text-2xl font-bold mb-4">Simulações Individuais</h1>
          {history.length === 0 ? (
            <div className="bg-white p-6 shadow rounded text-center text-gray-500">
              Nenhuma simulação individual salva ainda.
            </div>
          ) : (
            <div className="space-y-4">
              {history.map(item => (
                <div
                  key={item.id}
                  className="bg-white p-6 shadow rounded-lg border-l-4 border-primary-500"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <span className="text-xs text-gray-500">
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                      <h2 className="font-bold text-lg">
                        {item.input_data.is_ueg ? "UEG" : "Promove"} - Nível{" "}
                        {item.input_data.nivel_atual}
                      </h2>
                    </div>
                    <div
                      className={`px-3 py-1 rounded text-xs font-bold ${
                        item.result_data.resumo.status === "Apto a evolução"
                          ? "bg-green-100 text-green-700"
                          : "bg-yellow-100 text-yellow-700"
                      }`}
                    >
                      {item.result_data.resumo.status}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-500">Implementação</div>
                      <div className="font-medium">
                        {item.result_data.resumo.data_implementacao}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-500">Próximo Nível</div>
                      <div className="font-medium">
                        {item.result_data.resumo.proximo_nivel}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-500">Pontuação</div>
                      <div className="font-medium">
                        {item.result_data.resumo.pontuacao_alcancada}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-4">Cálculos Múltiplos</h2>
          {batchHistory.length === 0 ? (
            <div className="bg-white p-6 shadow rounded text-center text-gray-500">
              Nenhum lote salvo ainda.{" "}
              <Link
                href="/calculo-multiplo"
                className="text-primary-600 hover:underline"
              >
                Executar novo cálculo múltiplo
              </Link>
              .
            </div>
          ) : (
            <div className="space-y-3">
              {batchHistory.map(item => (
                <Link
                  key={item.id}
                  href={`/calculo-multiplo/${item.id}`}
                  className="block bg-white p-4 shadow rounded-lg border-l-4 border-primary-400 hover:bg-gray-50"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="text-xs text-gray-500">
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                      <h3 className="font-semibold">{item.filename}</h3>
                      <p className="text-xs text-gray-500">
                        {item.total_linhas} servidor(es) ·{" "}
                        {item.is_ueg ? "UEG" : "Promove"}
                        {item.apo_especial ? " · Aposentadoria Especial" : ""}
                      </p>
                    </div>
                    <span className="text-sm text-primary-600">
                      Ver detalhes →
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>
      </main>
    </>
  );
}
