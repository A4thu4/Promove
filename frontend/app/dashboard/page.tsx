"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import Navbar from "@/components/navbar";

export default function Page() {
  const { token, isLoading } = useAuth();
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !token) {
      router.push("/login");
    }
  }, [token, isLoading, router]);

  useEffect(() => {
    if (token) {
      fetch("http://localhost:8000/evolution/history", {
        headers: { "Authorization": `Bearer ${token}` }
      })
      .then(res => res.json())
      .then(data => {
        setHistory(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
    }
  }, [token]);

  if (isLoading || loading) {
    return <div className="text-center mt-20">Carregando...</div>;
  }

  return (
    <>
      <Navbar />
      <main className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">Meu Histórico de Simulações</h1>
        {history.length === 0 ? (
          <div className="bg-white p-6 shadow rounded text-center text-gray-500">
            Nenhuma simulação salva ainda.
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((item) => (
              <div key={item.id} className="bg-white p-6 shadow rounded-lg border-l-4 border-primary-500">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className="text-xs text-gray-500">{new Date(item.created_at).toLocaleString()}</span>
                    <h2 className="font-bold text-lg">
                      {item.input_data.is_ueg ? "UEG" : "Promove"} - Nível {item.input_data.nivel_atual}
                    </h2>
                  </div>
                  <div className={`px-3 py-1 rounded text-xs font-bold ${
                    item.result_data.resumo.status === "Apto a evolução" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                  }`}>
                    {item.result_data.resumo.status}
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500">Implementação</div>
                    <div className="font-medium">{item.result_data.resumo.data_implementacao}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Próximo Nível</div>
                    <div className="font-medium">{item.result_data.resumo.proximo_nivel}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Pontuação</div>
                    <div className="font-medium">{item.result_data.resumo.pontuacao_alcancada}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
