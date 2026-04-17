import type { CalculoInput, EvolutionOutput } from './types';

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = typeof window !== 'undefined'
    ? localStorage.getItem('token')
    : null;

  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'Erro na requisição');
  }

  return res.json();
}

export const api = {
  // Auth
  login: (email: string, password: string) => {
    const body = new URLSearchParams({ username: email, password });
    return request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    });
  },

  register: (email: string, password: string, full_name: string) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name }),
    }),

  // Evolution
  calculate: (data: CalculoInput) =>
    request<EvolutionOutput>('/evolution/calculate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  calculateAndSave: (data: CalculoInput) =>
    request<EvolutionOutput>('/evolution/calculate-save', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  history: () => request<any[]>('/evolution/history'),
};

// Converte DD/MM/YYYY → YYYY-MM-DD para o backend
export function toISODate(ddmmyyyy: string): string {
  const [d, m, y] = ddmmyyyy.split('/');
  return `${y}-${m}-${d}`;
}

// Converte YYYY-MM-DD → DD/MM/YYYY para exibição
export function toBRDate(iso: string): string {
  const [y, m, d] = iso.split('-');
  return `${d}/${m}/${y}`;
}