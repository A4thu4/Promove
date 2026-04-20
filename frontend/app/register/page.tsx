"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/navbar";
import { api } from "@/lib/api";

export default function Page() {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [registered, setRegistered] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.register(email, password, fullName);
      setRegistered(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha no cadastro");
    } finally {
      setLoading(false);
    }
  };

  if (registered) {
    return (
      <>
        <Navbar />
        <main className="max-w-md mx-auto p-6 bg-white shadow rounded-lg mt-10 text-center">
          <h1 className="text-2xl font-bold mb-4">Conta criada!</h1>
          <div className="bg-blue-50 text-blue-700 p-4 rounded mb-4">
            Enviamos um link de verificação para <strong>{email}</strong>. Verifique seu e-mail antes de fazer login.
          </div>
          <Link href="/login" className="text-primary-600 hover:underline">Ir para o Login</Link>
        </main>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <main className="max-w-md mx-auto p-6 bg-white shadow rounded-lg mt-10">
        <h1 className="text-2xl font-bold mb-6 text-center">Criar conta PROMOVE</h1>
        {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Nome Completo</label>
            <input 
              type="text" 
              required
              className="mt-1 block w-full border rounded p-2"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>
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
          <div>
            <label className="block text-sm font-medium text-gray-700">Senha</label>
            <input 
              type="password" 
              required
              className="mt-1 block w-full border rounded p-2"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-primary-600 text-white py-2 px-4 rounded hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? "Cadastrando..." : "Cadastrar"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          Já tem conta? <Link href="/login" className="text-primary-600 hover:underline">Entre</Link>
        </p>
      </main>
    </>
  );
}
