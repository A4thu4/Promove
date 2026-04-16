"use client";

import React, { createContext, useContext, useReducer } from 'react';
import { v4 as uuid } from 'uuid';
import type {
  DadosObrigatorios, Afastamento, Aperfeicoamento,
  Titulacao, RespUnica, RespMensal, EvolutionOutput,
} from '@/lib/types';

// ── Estado ────────────────────────────────────────────────────────────────────

interface SimulatorState {
  isUeg: boolean;
  apoEspecial: boolean;
  obrigatorios: DadosObrigatorios | null;
  afastamentos: Afastamento[];
  aperfeicoamentos: Aperfeicoamento[];
  titulacoes: Titulacao[];
  respUnicas: RespUnica[];
  respMensais: RespMensal[];
  resultado: EvolutionOutput | null;
  loading: boolean;
  error: string | null;
}

const INITIAL_STATE: SimulatorState = {
  isUeg: false,
  apoEspecial: false,
  obrigatorios: null,
  afastamentos: [],
  aperfeicoamentos: [],
  titulacoes: [],
  respUnicas: [],
  respMensais: [],
  resultado: null,
  loading: false,
  error: null,
};

// ── Actions ───────────────────────────────────────────────────────────────────

type Action =
  | { type: 'SET_IS_UEG'; payload: boolean }
  | { type: 'SET_APO_ESPECIAL'; payload: boolean }
  | { type: 'SET_OBRIGATORIOS'; payload: DadosObrigatorios | null }
  | { type: 'ADD_AFASTAMENTO'; payload: Omit<Afastamento, 'id'> }
  | { type: 'REMOVE_AFASTAMENTO'; payload: string }
  | { type: 'CLEAR_AFASTAMENTOS' }
  | { type: 'ADD_APERFEICOAMENTO'; payload: Omit<Aperfeicoamento, 'id'> }
  | { type: 'REMOVE_APERFEICOAMENTO'; payload: string }
  | { type: 'CLEAR_APERFEICOAMENTOS' }
  | { type: 'ADD_TITULACAO'; payload: Omit<Titulacao, 'id'> }
  | { type: 'REMOVE_TITULACAO'; payload: string }
  | { type: 'CLEAR_TITULACOES' }
  | { type: 'ADD_RESP_UNICA'; payload: Omit<RespUnica, 'id'> }
  | { type: 'REMOVE_RESP_UNICA'; payload: string }
  | { type: 'CLEAR_RESP_UNICAS' }
  | { type: 'ADD_RESP_MENSAL'; payload: Omit<RespMensal, 'id'> }
  | { type: 'REMOVE_RESP_MENSAL'; payload: string }
  | { type: 'CLEAR_RESP_MENSAIS' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_RESULTADO'; payload: EvolutionOutput }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'RESET' };

function reducer(state: SimulatorState, action: Action): SimulatorState {
  switch (action.type) {
    case 'SET_IS_UEG':       return { ...state, isUeg: action.payload };
    case 'SET_APO_ESPECIAL': return { ...state, apoEspecial: action.payload };
    case 'SET_OBRIGATORIOS': return { ...state, obrigatorios: action.payload, resultado: null };

    case 'ADD_AFASTAMENTO':
      return { ...state, afastamentos: [...state.afastamentos, { id: uuid(), ...action.payload }] };
    case 'REMOVE_AFASTAMENTO':
      return { ...state, afastamentos: state.afastamentos.filter(x => x.id !== action.payload) };
    case 'CLEAR_AFASTAMENTOS':
      return { ...state, afastamentos: [] };

    case 'ADD_APERFEICOAMENTO':
      return { ...state, aperfeicoamentos: [...state.aperfeicoamentos, { id: uuid(), ...action.payload }] };
    case 'REMOVE_APERFEICOAMENTO':
      return { ...state, aperfeicoamentos: state.aperfeicoamentos.filter(x => x.id !== action.payload) };
    case 'CLEAR_APERFEICOAMENTOS':
      return { ...state, aperfeicoamentos: [] };

    case 'ADD_TITULACAO':
      return { ...state, titulacoes: [...state.titulacoes, { id: uuid(), ...action.payload }] };
    case 'REMOVE_TITULACAO':
      return { ...state, titulacoes: state.titulacoes.filter(x => x.id !== action.payload) };
    case 'CLEAR_TITULACOES':
      return { ...state, titulacoes: [] };

    case 'ADD_RESP_UNICA':
      return { ...state, respUnicas: [...state.respUnicas, { id: uuid(), ...action.payload }] };
    case 'REMOVE_RESP_UNICA':
      return { ...state, respUnicas: state.respUnicas.filter(x => x.id !== action.payload) };
    case 'CLEAR_RESP_UNICAS':
      return { ...state, respUnicas: [] };

    case 'ADD_RESP_MENSAL':
      return { ...state, respMensais: [...state.respMensais, { id: uuid(), ...action.payload }] };
    case 'REMOVE_RESP_MENSAL':
      return { ...state, respMensais: state.respMensais.filter(x => x.id !== action.payload) };
    case 'CLEAR_RESP_MENSAIS':
      return { ...state, respMensais: [] };

    case 'SET_LOADING':   return { ...state, loading: action.payload };
    case 'SET_RESULTADO': return { ...state, resultado: action.payload, error: null };
    case 'SET_ERROR':     return { ...state, error: action.payload };
    case 'RESET':         return INITIAL_STATE;
    default:              return state;
  }
}

// ── Context ───────────────────────────────────────────────────────────────────

interface SimulatorContextType {
  state: SimulatorState;
  dispatch: React.Dispatch<Action>;
}

const SimulatorContext = createContext<SimulatorContextType | undefined>(undefined);

export function SimulatorProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, INITIAL_STATE);
  return (
    <SimulatorContext.Provider value={{ state, dispatch }}>
      {children}
    </SimulatorContext.Provider>
  );
}

export function useSimulator() {
  const ctx = useContext(SimulatorContext);
  if (!ctx) throw new Error('useSimulator deve ser usado dentro de SimulatorProvider');
  return ctx;
}