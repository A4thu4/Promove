import type {
  BatchCalculationOutput,
  BatchHistoryItem,
  CalculoInput,
  EvolutionOutput,
} from './types';

const BASE = process.env.NEXT_PUBLIC_API_URL ?? '';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'Erro na requisição');
  }

  return res.json();
}

async function uploadBatch(
  path: string,
  file: File,
  is_ueg: boolean,
  apo_especial: boolean,
): Promise<BatchCalculationOutput> {
  const fd = new FormData();
  fd.append('file', file);
  fd.append('is_ueg', String(is_ueg));
  fd.append('apo_especial', String(apo_especial));

  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    credentials: 'include',
    body: fd,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'Erro na requisição');
  }

  return res.json();
}

async function downloadBlob(path: string, init?: RequestInit): Promise<void> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    ...init,
    headers: {
      ...init?.headers,
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'Erro na requisição');
  }

  const disposition = res.headers.get('Content-Disposition') ?? '';
  const match = disposition.match(/filename="?([^"]+)"?/i);
  const filename = match?.[1] ?? 'resultado.xlsx';

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
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

  logout: () =>
    request('/auth/logout', { method: 'POST' }),

  verifyEmail: (token: string) =>
    request<{ detail: string }>('/auth/verify-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ token }).toString(),
    }),

  resendVerification: (email: string) =>
    request<{ detail: string }>('/auth/resend-verification', {
      method: 'POST',
      body: JSON.stringify({ email }),
    }),

  forgotPassword: (email: string) =>
    request<{ detail: string }>('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    }),

  resetPassword: (token: string, new_password: string) =>
    request<{ detail: string }>('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, new_password }),
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

  // Batch (Cálculo Múltiplo)
  batchCalculate: (file: File, is_ueg: boolean, apo_especial: boolean) =>
    uploadBatch('/batch/calculate', file, is_ueg, apo_especial),

  batchCalculateAndSave: (file: File, is_ueg: boolean, apo_especial: boolean) =>
    uploadBatch('/batch/calculate-save', file, is_ueg, apo_especial),

  batchHistory: () => request<BatchHistoryItem[]>('/batch/history'),

  batchHistoryDetail: (id: number) =>
    request<BatchCalculationOutput>(`/batch/history/${id}`),

  batchExportSaved: (id: number) => downloadBlob(`/batch/history/${id}/export`),

  batchExportFromOutput: (output: BatchCalculationOutput) =>
    downloadBlob('/batch/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(output),
    }),
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
