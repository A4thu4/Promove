"use client";

import Link from "next/link";
import { useAuth } from "@/context/auth-context";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white border-b shadow-sm mb-8">
      <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-primary-600">
          PROMOVE
        </Link>
        <div className="flex items-center gap-6">
          <Link href="/" className="text-gray-600 hover:text-primary-600">Simulador</Link>
          {user ? (
            <>
              <Link href="/dashboard" className="text-gray-600 hover:text-primary-600">Histórico</Link>
              <div className="flex items-center gap-3 border-l pl-6">
                <span className="text-sm font-medium text-gray-700">{user.full_name || user.email}</span>
                <button 
                  onClick={logout}
                  className="text-sm text-red-600 hover:text-red-800"
                >
                  Sair
                </button>
              </div>
            </>
          ) : (
            <div className="flex items-center gap-4">
              <Link href="/login" className="text-gray-600 hover:text-primary-600">Entrar</Link>
              <Link 
                href="/register" 
                className="bg-primary-600 text-white px-4 py-2 rounded text-sm hover:bg-primary-700 transition"
              >
                Cadastrar
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
