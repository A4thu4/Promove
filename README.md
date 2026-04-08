# 📈 Simulador PROMOVE - Sistema de Evolução Funcional (Nova Stack)

O sistema PROMOVE foi refatorado para uma arquitetura moderna e escalável, separando as preocupações entre Backend e Frontend.

---

## 🏗️ Arquitetura Atual (Refatorada)

- **Backend**: [FastAPI](https://api.tiangolo.com/) (Python)
  - Lógica de cálculo unificada (Promove + UEG).
  - Autenticação e Autorização com JWT.
  - Persistência de dados com SQLAlchemy e SQLite.
- **Frontend**: [Next.js](https://nextjs.org/) (React + Tailwind CSS)
  - Interface moderna e responsiva.
  - Gerenciamento de estado de autenticação.
  - Dashboard para histórico de simulações.
- **Antigo (Legado)**: O sistema anterior em Streamlit ainda está disponível nas pastas `app/` e `ueg/`.

---

## 🚀 Funcionalidades

- 📊 **Cálculo Unificado**: Uma única lógica para Promove e UEG, parametrizada.
- 📅 **Projeção Futura**: Detecta a data exata em que o servidor atingirá os requisitos.
- 🧪 **Testes Automatizados**: Suite de testes para garantir paridade de cálculo.
- ⚡ **Performance**: Backend leve e frontend otimizado com Next.js App Router.

---

## ⚙️ Como rodar (Nova Stack)

Recomendamos o uso dos scripts automatizados para facilitar a execução no Windows:

1. **Setup Inicial**: 
   - Abra o PowerShell na raiz do projeto.
   - Execute: `.\setup.ps1` (Isso criará o ambiente virtual e instalará as dependências do Backend e Frontend).

2. **Execução**:
   - Execute: `.\run.ps1` (Isso iniciará o Backend na porta 8000 e o Frontend na porta 3000 automaticamente).

### Alternativa Manual:

#### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate 
$env:PYTHONPATH=".."
uvicorn backend.app.main:app --reload
```

#### 2. Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Segurança e Dados

- **Autenticação**: Sistema completo de Registro e Login usando **JWT**.
- **Histórico**: Usuários logados podem salvar e visualizar suas simulações anteriores no Dashboard.
- **Banco de Dados**: Utiliza SQLite por padrão (`sql_app.db`), facilmente migrável para PostgreSQL/MySQL alterando a `DATABASE_URL` no `.env`.

---

## 📁 Estrutura do Projeto

```bash
📦 Promove/
├── backend/                # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints (Auth, Evolution)
│   │   ├── core/           # Lógica, Configurações e Segurança
│   │   ├── crud/           # Operações de Banco de Dados
│   │   ├── db/             # Sessão e Base SQLAlchemy
│   │   ├── models/         # Modelos de Tabela (User, History)
│   │   └── schemas/        # Schemas Pydantic (Validação)
│   └── tests_logic.py      # Testes unitários da lógica
├── frontend/               # Frontend Next.js
│   ├── app/                # Páginas (Login, Register, Dashboard)
│   ├── components/         # Componentes Reutilizáveis
│   └── context/            # AuthContext (Estado Global)
├── requirements.txt        # Dependências do Backend
├── setup.ps1               # Script de Instalação Automática
└── run.ps1                 # Script de Execução Automática
```

---

## 🧪 Exemplo de uso

- Informe os dados obrigatórios e opcionais necessários.
- O sistema calcula automaticamente:
  - Se está Apto a evoluir.
  - Próximo Nível.
  - Quando atinge o próximo nível.
  - Quantos meses levou.
- Mostra o resultado com total de pontos e tempo acumulado.

---

## 👨‍💻 Desenvolvedor

> Feito por Arthur Mamedes – Estudante de Ciência da Computação e estagiário na Gerência de Normas e Critérios de Produtividade (GNCP).

📬 <arthurmamedesborges@gmail.com>

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).
