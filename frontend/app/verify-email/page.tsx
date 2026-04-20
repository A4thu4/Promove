"use client";

import React, { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/navbar";
import { api } from "@/lib/api";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Token de verificação não encontrado.");
      return;
    }

    api.verifyEmail(token)
      .then((res) => {
        setStatus("success");
        setMessage(res.detail);
      })
      .catch((err) => {
        setStatus("error");
        setMessage(err instanceof Error ? err.message : "Erro ao verificar e-mail");
      });
  }, [token]);

  return (
    <main className="max-w-md mx-auto p-6 bg-white shadow rounded-lg mt-10 text-center">
      <h1 className="text-2xl font-bold mb-6">Verificação de E-mail</h1>

      {status === "loading" && <p className="text-gray-600">Verificando...</p>}

      {status === "success" && (
        <div className="space-y-4">
          <div className="bg-green-50 text-green-700 p-4 rounded">{message}</div>
          <Link href="/login" className="inline-block bg-primary-600 text-white py-2 px-6 rounded hover:bg-primary-700">
            Ir para o Login
          </Link>
        </div>
      )}

      {status === "error" && (
        <div className="space-y-4">
          <div className="bg-red-50 text-red-600 p-4 rounded">{message}</div>
          <Link href="/login" className="text-primary-600 hover:underline">
            Voltar ao Login
          </Link>
        </div>
      )}
    </main>
  );
}

export default function Page() {
  return (
    <>
      <Navbar />
      <Suspense fallback={<main className="max-w-md mx-auto p-6 mt-10 text-center text-gray-600">Carregando...</main>}>
        <VerifyEmailContent />
      </Suspense>
    </>
  );
}
