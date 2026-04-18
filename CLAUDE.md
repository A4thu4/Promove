# CLAUDE.md — Simulador Promove

Contexto e convenções para assistentes (Claude Code CLI, IDE) trabalharem
neste repositório. Este arquivo é lido automaticamente pelo Claude Code;
edite-o quando as premissas mudarem.

## Visão geral

Aplicação que simula a evolução funcional das carreiras **Promove** (Geral)
e **UEG** (Universidade Estadual de Goiás) do estado de Goiás. Substitui o
app antigo Streamlit (`/home/user/Promove`) por uma stack web moderna:

- **Backend**: FastAPI (Python) em `backend/app/`.
- **Frontend**: Next.js 14 (App Router, Client Components) em `frontend/`.
- **Banco**: SQLAlchemy (provavelmente SQLite local / Postgres em prod via
  `DATABASE_URL`). Modelos em `backend/app/models/`.
- **Auth**: JWT, token guardado no `localStorage` do browser; `useAuth()`
  em `frontend/context/auth-context.tsx`.
- **Orquestração**: `docker-compose.yml` na raiz.

## Estrutura relevante

```
backend/
  app/
    api/
      auth.py, simulator.py, history.py, batch.py
    core/
      logic.py              # motor de cálculo + validação de evolução
      config.py             # CareerSettings, EvolutionRequirement
      spreadsheet_tables.py # símbolos curtos (DAS1, FCG5, …) → pontos
    models/
      user.py, history.py, batch_history.py
    schemas/
      evolution.py          # Pydantic: EvolutionInput/Output, Batch*
    services/
      calculator.py         # run_calculation(EvolutionInput)
      batch_parser.py       # Excel → EvolutionInput
      batch_calculator.py   # run_batch + to_excel_bytes
    main.py                 # registra routers + Base.metadata.create_all

frontend/
  app/
    page.tsx                   # simulador individual
    dashboard/page.tsx         # histórico (individual + lotes)
    calculo-multiplo/
      page.tsx                 # upload + "Simular" / "Calcular e Salvar"
      [id]/page.tsx            # detalhe de lote salvo
  components/
    navbar.tsx
    simulator/
      SimulatorForm.tsx
      BatchResultsTable.tsx
      sections/Obrigatorios.tsx, Afastamentos.tsx, …
  context/
    auth-context.tsx
    simulator-context.tsx      # HYDRATE_FROM_BATCH + BatchHydratePayload
  lib/
    api.ts                     # cliente HTTP tipado
    types.ts
    constants.ts               # labels amigáveis: "DAS-1", "Mestrado", …
    batch-handoff.ts           # BatchRowResult → payload p/ simulador
```

## Branches

Desenvolvimento ativo em:

- `ArthemizLabs/simulador-promove` → `claude/add-bulk-calculation-excel-fpV1I`
  (e espelhada em `feature/calculo-multiplo`).
- Não subir para `main` sem PR. Nunca force-push em main.

## Regras de negócio — motor de cálculo (`backend/app/core/logic.py`)

Duas carreiras, ambas com 240 meses de simulação (`data_conclusao = 241`).

Colunas da matriz `carreira` (índice 0 = data, o resto são pontos do mês):

| idx | Geral            | UEG              |
|-----|------------------|------------------|
|  1  | efetivo exerc.   | efetivo exerc.   |
|  2  | desempenho       | desempenho       |
|  3  | aperfeiçoamento  | titulação        |
|  4  | titulação        | resp. única      |
|  5  | resp. única      | resp. mensal     |
|  6  | resp. mensal     | **acumulado**    |
|  7  | **acumulado**    | —                |

Pontos por mês (sem absentismo):

| Grandeza            | Geral   | UEG     |
|---------------------|---------|---------|
| Efetivo exercício   | 0.20    | 0.20    |
| Desempenho          | 1.50    | 1.80    |
| Aperfeiçoamento     | 0.09/h, cap em 100h (9 pts) | n/a |

Outros tetos: titulação 144 pts; responsabilidades (únicas + mensais) 144 pts
combinados. Afastamentos descontam efetivo (0.0067/dia) e desempenho
(`pontos_desempenho / 30` por dia).

### Regra de evolução (crítica — corrigida em `e913f8b`)

Três requisitos **simultâneos** para evoluir de nível:

1. **Pontuação** ≥ 48 (via padrão) **ou** ≥ 96 (via rápida).
2. **Aperfeiçoamento** (não-UEG): ≥ 60h (5.4 pts) na via padrão; 40h (3.6
   pts) é aceito **apenas** se a pontuação ≥ 96 for atingida entre os meses
   12 e 18 (ou 12 e 15 com aposentadoria especial). UEG não exige aperf.
3. **Efetivo exercício** acumulado ≥ 2.4 pts.

Interstícios mínimos: 12 meses (rápida), 18 meses (padrão), 15 meses
(padrão com aposentadoria especial).

Pitfalls já quebrados:

- Antes o check era contra `desempenho_final >= 2.4`, que passava
  trivialmente (1.5 pts/mês → 2.4 em 2 meses). Agora é contra efetivo
  exercício (0.2 pts/mês → 2.4 em 12 meses, que é o alinhamento natural
  com o interstício).
- Antes a via rápida disparava em qualquer mês ≥ 12 enquanto a pontuação
  estivesse ≥ 96, o que permitia "evoluir" em meses bem altos (ex.: 55)
  com apenas 40h, porque a pontuação chegava a 96 só pelo acúmulo de
  desempenho. Agora a rápida é restrita à janela [12, min_padrao).

## Cálculo Múltiplo (batch por upload de Excel)

- Endpoint `POST /batch/calculate` (público, stateless, botão **Simular**).
- Endpoint `POST /batch/calculate-save` (autenticado, botão **Calcular e
  Salvar** — persiste um `BatchHistory` por upload; não polui o histórico
  individual).
- Endpoint `GET /batch/history` + `/history/{id}` + `/history/{id}/export`
  (autenticado, dono).
- Endpoint `POST /batch/export` (stateless, para o fluxo Simular).
- A tabela na UI tem botão "Abrir no simulador" que hidrata o
  `SimulatorContext` via `sessionStorage` (`lib/batch-handoff.ts`) e
  redireciona pra `/`.

### Leitura da planilha (`services/batch_parser.py`)

- 7 colunas obrigatórias (`Servidor`, `CPF`, `Vínculo`, `Nível Atual`,
  `Data do Enquadramento`, `Data de Início dos Pontos`, `Pontos Excedentes
  da Última Evolução`). Datas em `dd/mm/yyyy`.
- **Dedup** (alterado em `e913f8b`): chave é `(Vínculo, CPF)`. Linhas com
  Vínculo igual mas CPF diferente são mantidas. Linhas sem Vínculo são
  sempre mantidas.
- Parsers de campos `;`-separados para afastamentos, aperfeiçoamentos,
  titulações, responsabilidades mensais (split `-` = `simbolo-inicio-fim`)
  e únicas (split `-` = `qtd-tipo-data`).
- Símbolos curtos da planilha (ex.: `DAS1`, `FCG5`, `PUBID`, `PLO`) são
  mapeados em `core/spreadsheet_tables.py` — mantenha-os sincronizados
  com o Excel modelo da SEAD se ele mudar.

## Convenções

### Código

- Não adicionar features/abstrações/handlers de erro além do necessário.
- Comentários só quando o "porquê" não é óbvio.
- Frontend é **pt-BR** na UI. Em datas: formato BR (dd/mm/yyyy) nos forms,
  ISO no JSON (ver `toBRDate` / `fromBRDate` em `lib/api.ts`).
- Tipos TypeScript vivem em `lib/types.ts` e devem espelhar os Pydantic
  schemas de `backend/app/schemas/`.

### Git

- Mensagens de commit em pt-BR.
- Rodapé padrão: `https://claude.ai/code/session_*` (mantido pelo Claude
  Code — não remover manualmente).
- Nunca `--amend` em commit já pushado; sempre commit novo.

## Testes e verificação

```bash
# Backend
cd backend && uvicorn app.main:app --reload
python -m unittest tests.test_logic -v

# Frontend
cd frontend && npm run dev

# Diff contra o app antigo (referência de comportamento)
cd /home/user/Promove && streamlit run app/master.py
```

Casos-âncora ao mexer em `validar_evolucao`:

- Geral, 18m, 10h aperf → "Não apto" com motivo "aperfeiçoamento
  insuficiente".
- Geral, 18m, 100h aperf, 12m de DAS1 — evolui (padrão, apo especial).
- UEG, 24m, sem aperf → evolui (UEG não exige aperf).
- Geral, 40h aperf apenas, 55m (pontos = 97 por desempenho) → **Não apto**
  (regressão do bug corrigido em `e913f8b`).
- Geral, 40h aperf + boost de resp única para atingir 96 no mês 12 → evolui
  via rápida em 12m.

Planilhas: testar dedup com duas linhas mesmo Vínculo + CPFs diferentes →
ambas processadas.

## Referências ao app antigo

O app Streamlit em `/home/user/Promove` continua como referência de
comportamento. Arquivos mais relevantes:

- `app/logic.py` — motor original (inclui bugs que NÃO foram portados).
- `app/planilha_utils.py` — leitura de Excel + símbolos curtos.
- `app/master.py` — UI original, útil pra reproduzir casos de diff.

Divergências deliberadas: (1) rápida restrita a [12, 18)m; (2) check de
efetivo exercício explícito em `validar_evolucao`; (3) dedup por
`(Vínculo, CPF)` em vez de só Vínculo. Qualquer outra divergência é bug —
reportar antes de "sincronizar".
