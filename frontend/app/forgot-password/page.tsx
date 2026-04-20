"use client";

import React, { useState } from "react";
import Link from "next/link";
import Navbar from "@/components/navbar";
import { api } from "@/lib/api";

export default function Page() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao enviar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="max-w-md mx-auto p-6 bg-white shadow rounded-lg mt-10">
        <h1 className="text-2xl font-bold mb-6 text-center">Esqueci minha senha</h1>

        {sent ? (
          <div className="space-y-4 text-center">
            <div className="bg-green-50 text-green-700 p-4 rounded">
              Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha.
            </div>
            <Link href="/login" className="text-primary-600 hover:underline">
              Voltar ao Login
            </Link>
          </div>
        ) : (
          <>
            {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">{error}</div>}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">E-mail</label>
                <input
                  type="email"
                  required
                  className="mt-1 block w-full border rounded p-2"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary-600 text-white py-2 px-4 rounded hover:bg-primary-700 disabled:opacity-50"
              >
                {loading ? "Enviando..." : "Enviar link de redefinição"}
              </button>
            </form>
            <p className="mt-4 text-center text-sm text-gray-600">
              <Link href="/login" className="text-primary-600 hover:underline">Voltar ao Login</Link>
            </p>
          </>
        )}
      </main>
    </>
  );
}
