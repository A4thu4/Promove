import type { BatchHydratePayload } from '@/context/simulator-context';
import type { BatchRowResult, CalculoInput } from '@/lib/types';

const KEY = 'promove:pendingBatchInput';

function toMonth(iso: string): string {
  return iso.slice(0, 7);
}

export function batchRowToHydrate(row: BatchRowResult): BatchHydratePayload {
  const input: CalculoInput = row.input;

  return {
    isUeg: input.is_ueg,
    apoEspecial: input.apo_especial,
    obrigatorios: {
      nivelAtual: input.nivel_atual,
      dataEnquadramento: input.data_enquadramento,
      dataInicio: input.data_inicio,
      pontosExcedentes: input.pts_remanescentes,
    },
    afastamentos: input.afastamentos.map(a => ({
      data: toMonth(a.data),
      dias: a.dias,
    })),
    aperfeicoamentos: input.aperfeicoamentos.map(a => ({
      data: a.data,
      horas: a.horas,
    })),
    titulacoes: input.titulacoes.map(t => ({
      data: t.data,
      tipo: t.tipo,
    })),
    // Sem metadados finos (tipo/categoria/qtd), preservamos só o total de pontos
    // do lote para manter o somatório. Exibido como categoria "artigo" + rótulo
    // neutro — pode ser editado manualmente antes de recalcular.
    respUnicas: input.resp_unicas.map(r => ({
      data: r.data,
      quantidade: 1,
      tipo: `Pré-preenchido (${r.pontos.toFixed(2)} pts)`,
      categoria: 'artigo' as const,
    })),
    respMensais: input.resp_mensais.map(r => ({
      tipo: r.tipo,
      inicio: r.inicio,
      fim: r.fim,
      semDataFim: false,
      pontos: r.pontos,
    })),
  };
}

export function stashPendingBatchInput(payload: BatchHydratePayload): void {
  if (typeof window === 'undefined') return;
  window.sessionStorage.setItem(KEY, JSON.stringify(payload));
}

export function consumePendingBatchInput(): BatchHydratePayload | null {
  if (typeof window === 'undefined') return null;
  const raw = window.sessionStorage.getItem(KEY);
  if (!raw) return null;
  window.sessionStorage.removeItem(KEY);
  try {
    return JSON.parse(raw) as BatchHydratePayload;
  } catch {
    return null;
  }
}
