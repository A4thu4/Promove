"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import Navbar from "@/components/Navbar";

export default function Home() {
  const { token, user } = useAuth();
  const [formData, setFormData] = useState({
    is_ueg: false,
    nivel_atual: "A",
    data_inicio: "2022-01-01",
    data_enquadramento: "2022-01-01",
    pts_remanescentes: 0,
    apo_especial: false
  });

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Usar endpoint que salva se estiver logado
      const endpoint = token 
        ? "http://localhost:8000/evolution/calculate-save" 
        : "http://localhost:8000/evolution/calculate";
        
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token ? { "Authorization": `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          ...formData,
          afastamentos: [],
          aperfeicoamentos: [],
          titulacoes: [],
          resp_unicas: [],
          resp_mensais: []
        }),
      });

      if (!response.ok) {
        throw new Error("Erro na requisição");
      }

      const data = await response.json();
      setResult(data);
      if (token) {
        alert("Simulação salva no seu histórico!");
      }
    } catch (err) {
      alert("Erro ao calcular: " + err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="max-w-4xl mx-auto p-6">
        <header className="mb-10 text-center">
          <h1 className="text-3xl font-bold text-primary-800">Simulador de Evolução</h1>
          <p className="text-gray-600">Calcule sua próxima progressão ou promoção</p>
          {!user && (
            <div className="mt-4 p-3 bg-blue-50 text-blue-700 rounded-lg text-sm inline-block">
              Dica: Faça <a href="/login" className="font-bold underline">Login</a> para salvar suas simulações!
            </div>
          )}
        </header>

        <section className="bg-white shadow rounded-lg p-6 mb-8">
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Órgão</label>
              <select 
                className="mt-1 block w-full border rounded p-2"
                value={formData.is_ueg ? "UEG" : "Promove"}
                onChange={(e) => setFormData({...formData, is_ueg: e.target.value === "UEG"})}
              >
                <option value="Promove">Promove</option>
                <option value="UEG">UEG</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Nível Atual</label>
              <input 
                type="text" 
                className="mt-1 block w-full border rounded p-2"
                value={formData.nivel_atual}
                onChange={(e) => setFormData({...formData, nivel_atual: e.target.value.toUpperCase()})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Data Início</label>
              <input 
                type="date" 
                className="mt-1 block w-full border rounded p-2"
                value={formData.data_inicio}
                onChange={(e) => setFormData({...formData, data_inicio: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Data Enquadramento</label>
              <input 
                type="date" 
                className="mt-1 block w-full border rounded p-2"
                value={formData.data_enquadramento}
                onChange={(e) => setFormData({...formData, data_enquadramento: e.target.value})}
              />
            </div>

            <div className="md:col-span-2">
              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-primary-600 text-white py-2 px-4 rounded hover:bg-primary-700 disabled:opacity-50"
              >
                {loading ? "Calculando..." : "Calcular Evolução"}
              </button>
            </div>
          </form>
        </section>

        {result && (
          <section className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4 border-b pb-2">Resultado</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="font-semibold text-gray-600">Status:</div>
              <div className="font-bold text-primary-700">{result.resumo.status}</div>
              <div className="font-semibold text-gray-600">Próximo Nível:</div>
              <div>{result.resumo.proximo_nivel}</div>
              <div className="font-semibold text-gray-600">Data Pontuação:</div>
              <div>{result.resumo.data_pontuacao}</div>
              <div className="font-semibold text-gray-600">Implementação:</div>
              <div>{result.resumo.data_implementacao}</div>
              <div className="font-semibold text-gray-600">Pontuação Alcançada:</div>
              <div>{result.resumo.pontuacao_alcancada}</div>
            </div>
            <div className="mt-6 p-4 bg-gray-50 rounded italic text-sm text-gray-700">
              {result.resumo.observacao}
            </div>
          </section>
        )}
      </main>
    </>
  );
}
