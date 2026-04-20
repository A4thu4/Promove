"use client";

import React, { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/navbar";
import { api } from "@/lib/api";

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("As senhas não coincidem");
      return;
    }

    if (!token) {
      setError("Token de redefinição não encontrado");
      return;
    }

    setLoading(true);
    try {
      await api.resetPassword(token, password);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao redefinir senha");
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <main className="max-w-md mx-auto p-6 bg-white shadow rounded-lg mt-10 text-center">
        <div className="bg-red-50 text-red-600 p-4 rounded">Token de redefinição inválido ou ausente.</div>
        <Link href="/forgot-password" className="mt-4 inline-block text-primary-600 hover:underline">
          Solicitar novo link
        </Link>
      </main>
    );
  }

  return (
    <main className="max-w-md mx-auto p-6 bg-white shadow rounded-lg mt-10">
      <h1 className="text-2xl font-bold mb-6 text-center">Redefinir senha</h1>

      {success ? (
        <div className="space-y-4 text-center">
          <div className="bg-green-50 text-green-700 p-4 rounded">Senha redefinida com sucesso!</div>
          <Link href="/login" className="inline-block bg-primary-600 text-white py-2 px-6 rounded hover:bg-primary-700">
            Ir para o Login
          </Link>
        </div>
      ) : (
        <>
          {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">{error}</div>}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Nova senha</label>
              <input
                type="password"
                required
                minLength={8}
                className="mt-1 block w-full border rounded p-2"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">Mínimo 8 caracteres, 1 maiúscula e 1 número</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Confirmar senha</label>
              <input
                type="password"
                required
                minLength={8}
                className="mt-1 block w-full border rounded p-2"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-2 px-4 rounded hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? "Redefinindo..." : "Redefinir senha"}
            </button>
          </form>
        </>
      )}
    </main>
  );
}

export default function Page() {
  return (
    <>
      <Navbar />
      <Suspense fallback={<main className="max-w-md mx-auto p-6 mt-10 text-center text-gray-600">Carregando...</main>}>
        <ResetPasswordForm />
      </Suspense>
    </>
  );
}
