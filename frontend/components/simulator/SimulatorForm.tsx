"use client";

import { useSimulator } from '@/context/simulator-context';
import { useAuth } from '@/context/auth-context';
import { api } from '@/lib/api';
import { DADOS_ARTIGO, DADOS_LIVRO, DADOS_PESQUISAS, DADOS_REGISTROS, DADOS_CURSOS } from '@/lib/constants';

import { Obrigatorios }               from './sections/Obrigatorios';
import { Afastamentos }               from './sections/Afastamentos';
import { Aperfeicoamentos }           from './sections/Aperfeicoamentos';
import { Titulacoes }                 from './sections/Titulacoes';
import { ResponsabilidadesMensais }   from './sections/ResponsabilidadesMensais';
import { ResponsabilidadesUnicas }    from './sections/ResponsabilidadesUnicas';
import { ResultsPanel }               from './ResultsPanel';
import type { CalculoInput } from '@/lib/types';

export function SimulatorForm() {
  const { state, dispatch } = useSimulator();
  const { token } = useAuth();

  function isAuthError(err: any) {
    const status = err?.status ?? err?.response?.status;
    const message = String(err?.message ?? '').toLowerCase();

    return (
      status === 401 ||
      status === 403 ||
      message.includes('unauthorized') ||
      message.includes('forbidden') ||
      message.includes('token') ||
      message.includes('auth')
    );
  }

  async function handleCalcular() {
    if (!state.obrigatorios) {
      dispatch({ type: 'SET_ERROR', payload: 'Preencha os dados obrigatórios primeiro.' });
      return;
    }

    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      const { obrigatorios } = state;

      // Monta o mapa de pontos para R.Únicas
      const dadosRu = {
        ...DADOS_ARTIGO, ...DADOS_LIVRO,
        ...DADOS_PESQUISAS, ...DADOS_REGISTROS, ...DADOS_CURSOS,
      };

      const payload: CalculoInput = {
        is_ueg:            state.isUeg,
        nivel_atual:       obrigatorios.nivelAtual,
        data_inicio:       obrigatorios.dataInicio,
        data_enquadramento:obrigatorios.dataEnquadramento,
        pts_remanescentes: obrigatorios.pontosExcedentes,
        apo_especial:      state.apoEspecial,

        afastamentos: state.afastamentos.map(a => ({
          data: a.data + '-01',   // YYYY-MM-01 (backend usa só mês/ano)
          dias: a.dias,
        })),

        aperfeicoamentos: state.aperfeicoamentos.map(a => ({
          data:  a.data,
          horas: a.horas,
        })),

        titulacoes: state.titulacoes.map(t => ({
          data: t.data,
          tipo: t.tipo,
        })),

        resp_unicas: state.respUnicas.map(r => ({
          data:   r.data,
          pontos: r.quantidade * (dadosRu[r.tipo] ?? 0),
        })),

        resp_mensais: state.respMensais.map(r => ({
          tipo:   r.tipo,
          inicio: r.inicio,
          fim:    r.fim,
          pontos: r.pontos,
        })),
      };

      let resultado;

      if (token) {
        resultado = await api.calculateAndSave(payload);
      } else {
        try {
          resultado = await api.calculateAndSave(payload);
        } catch (err: any) {
          if (!isAuthError(err)) {
            throw err;
          }

          resultado = await api.calculate(payload);
        }
      }

      dispatch({ type: 'SET_RESULTADO', payload: resultado });
    } catch (err: any) {
      dispatch({ type: 'SET_ERROR', payload: err.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }

  return (
    <div className="space-y-6">
      {/* Controles globais */}
      <div className="flex flex-wrap items-center gap-6 p-4 bg-white rounded-xl border border-gray-200 shadow-sm">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            className="w-4 h-4 accent-green-600"
            checked={state.isUeg}
            onChange={e => dispatch({ type: 'SET_IS_UEG', payload: e.target.checked })}
          />
          <span className="text-sm font-medium text-gray-700">Carreira UEG</span>
        </label>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            className="w-4 h-4 accent-green-600"
            checked={state.apoEspecial}
            onChange={e => dispatch({ type: 'SET_APO_ESPECIAL', payload: e.target.checked })}
          />
          <span className="text-sm font-medium text-gray-700">Aposentadoria Especial</span>
        </label>

        <div className="ml-auto flex gap-3">
          <button
            type="button"
            className="btn-primary px-8"
            onClick={handleCalcular}
            disabled={state.loading || !state.obrigatorios}
          >
            {state.loading ? 'Calculando...' : 'Calcular'}
          </button>
          <button
            type="button"
            className="btn-ghost text-red-500"
            onClick={() => dispatch({ type: 'RESET' })}
          >
            Novo Cálculo
          </button>
        </div>
      </div>

      {/* Seções do formulário */}
      <div className="space-y-4">
        <SectionHeader label="Requisitos Obrigatórios" color="green" />
        <Obrigatorios />
        <Afastamentos />
        {!state.isUeg && <Aperfeicoamentos />}
      </div>

      <div className="space-y-4">
        <SectionHeader label="Requisitos Aceleradores" color="yellow" />
        <Titulacoes />
        <ResponsabilidadesMensais />
        <ResponsabilidadesUnicas />
      </div>

      <ResultsPanel />
    </div>
  );
}

function SectionHeader({ label, color }: { label: string; color: 'green' | 'yellow' }) {
  const colors = {
    green:  'border-green-700 text-green-800 bg-green-50',
    yellow: 'border-yellow-500 text-yellow-800 bg-yellow-50',
  };
  return (
    <div className={`border-l-4 px-4 py-2 rounded-r-lg ${colors[color]}`}>
      <h2 className="font-bold text-base">{label}</h2>
    </div>
  );
}