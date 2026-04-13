"use client";

import { useState, type FormEvent } from 'react';
import { useSimulator } from '@/context/simulator-context';
import { Card } from '@/components/ui/Card';
import { NIVEIS, NIVEIS_UEG } from '@/lib/constants';

export function Obrigatorios() {
  const { state, dispatch } = useSimulator();
  const niveis = state.isUeg ? NIVEIS_UEG : NIVEIS;

  const [form, setForm] = useState({
    nivelAtual:        state.obrigatorios?.nivelAtual        ?? '',
    dataEnquadramento: state.obrigatorios?.dataEnquadramento ?? '',
    dataInicio:        state.obrigatorios?.dataInicio        ?? '',
    pontosExcedentes:  state.obrigatorios?.pontosExcedentes  ?? 0,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  function validate() {
    const e: Record<string, string> = {};
    if (!form.nivelAtual)
      e.nivelAtual = 'Informe o nível atual.';
    else if (!niveis.includes(form.nivelAtual.toUpperCase()))
      e.nivelAtual = `Nível inválido. Use um entre ${niveis[0]} e ${niveis[niveis.length - 1]}.`;
    if (!form.dataEnquadramento)
      e.dataEnquadramento = 'Informe a data do enquadramento.';
    if (!form.dataInicio)
      e.dataInicio = 'Informe a data de início dos pontos.';
    if (form.pontosExcedentes < 0)
      e.pontosExcedentes = 'Valor não pode ser negativo.';
    return e;
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setErrors({});
    dispatch({
      type: 'SET_OBRIGATORIOS',
      payload: { ...form, nivelAtual: form.nivelAtual.toUpperCase() },
    });
  }

  function handleReset() {
    setForm({ nivelAtual: '', dataEnquadramento: '', dataInicio: '', pontosExcedentes: 0 });
    dispatch({ type: 'SET_OBRIGATORIOS', payload: null });
    // Limpa tudo que depende do enquadramento
    dispatch({ type: 'CLEAR_AFASTAMENTOS' });
    dispatch({ type: 'CLEAR_APERFEICOAMENTOS' });
    dispatch({ type: 'CLEAR_TITULACOES' });
    dispatch({ type: 'CLEAR_RESP_UNICAS' });
    dispatch({ type: 'CLEAR_RESP_MENSAIS' });
  }

  return (
    <Card title="Requisitos Obrigatórios" subtitle="Dados do servidor">
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

          {/* Nível */}
          <div>
            <label className="field-label">Nível Atual</label>
            <input
              type="text"
              maxLength={1}
              className={`field-input uppercase ${errors.nivelAtual ? 'border-red-400' : ''}`}
              value={form.nivelAtual}
              onChange={e => setForm(p => ({ ...p, nivelAtual: e.target.value.toUpperCase() }))}
              placeholder={`${niveis[0]} – ${niveis[niveis.length - 1]}`}
            />
            {errors.nivelAtual && <p className="field-error">{errors.nivelAtual}</p>}
          </div>

          {/* Data Enquadramento */}
          <div>
            <label className="field-label">Data do Enquadramento</label>
            <input
              type="date"
              className={`field-input ${errors.dataEnquadramento ? 'border-red-400' : ''}`}
              value={form.dataEnquadramento}
              onChange={e => setForm(p => ({ ...p, dataEnquadramento: e.target.value }))}
            />
            {errors.dataEnquadramento && <p className="field-error">{errors.dataEnquadramento}</p>}
          </div>

          {/* Data Início */}
          <div>
            <label className="field-label">Data de Início dos Pontos</label>
            <input
              type="date"
              className={`field-input ${errors.dataInicio ? 'border-red-400' : ''}`}
              value={form.dataInicio}
              onChange={e => setForm(p => ({ ...p, dataInicio: e.target.value }))}
            />
            {errors.dataInicio && <p className="field-error">{errors.dataInicio}</p>}
          </div>

          {/* Pontos excedentes */}
          <div>
            <label className="field-label">Pontos Excedentes</label>
            <input
              type="number"
              step="0.001"
              min="0"
              className={`field-input ${errors.pontosExcedentes ? 'border-red-400' : ''}`}
              value={form.pontosExcedentes}
              onChange={e => setForm(p => ({ ...p, pontosExcedentes: parseFloat(e.target.value) || 0 }))}
            />
            <p className="text-xs text-gray-400 mt-1">0 caso não haja</p>
            {errors.pontosExcedentes && <p className="field-error">{errors.pontosExcedentes}</p>}
          </div>
        </div>

        <div className="flex gap-3 mt-5">
          <button type="submit" className="btn-primary">
            Confirmar Dados
          </button>
          {state.obrigatorios && (
            <button type="button" className="btn-danger" onClick={handleReset}>
              Limpar
            </button>
          )}
        </div>
      </form>

      {/* Preview dos dados confirmados */}
      {state.obrigatorios && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800 grid grid-cols-2 sm:grid-cols-4 gap-2">
          <span><strong>Nível:</strong> {state.obrigatorios.nivelAtual}</span>
          <span><strong>Enquadramento:</strong> {state.obrigatorios.dataEnquadramento}</span>
          <span><strong>Início:</strong> {state.obrigatorios.dataInicio}</span>
          <span><strong>Pts iniciais:</strong> {state.obrigatorios.pontosExcedentes}</span>
        </div>
      )}
    </Card>
  );
}