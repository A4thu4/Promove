# 📈 Simulador PROMOVE - Cálculo de Progressão Funcional

Sistema feito em Python + Streamlit para simular e calcular progressões funcionais com base em critérios de tempo, pontuação, titulação e carreira.

---

## 🧠 Objetivo

Facilitar a análise de **progressão de servidores públicos**, simulando automaticamente o avanço entre níveis/ciclos, com base nas **tabelas de pontuação** e **regras da unidade de produtividade** de acordo com regras pré-estabelecidas pelo Governo para os Orgãos.

---

## 🚀 Funcionalidades

- 📊 Cálculo automático da progressão por nível.
- 📅 Detecção de **tempo necessário** entre ciclos.
- ⚖️ Verificação de atingimento de metas mínimas por mês.
- 📈 Exibição em tabela dos resultados com totais e tempos.
- ✅ Ajuste dinâmico de critérios (nível, meta, início, etc).
- 🎯 Ideal para simulações individuais ou em lote.

---

## 🛠 Tecnologias Usadas

- [Python 3.9+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- Pandas

---

## ⚙️ Como rodar localmente

1. Clone o repositório:

```bash
git clone https://github.com/A4thu4/Promove.git
cd promove4
```

2. Crie o ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate   # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Rode o app:

```bash
streamlit run main.py
```

---

## 📁 Estrutura do Projeto

```bash
📦 Promove/
├── main.py            # Código principal com Streamlit
├── README.md              # Este arquivo
├── requirements.txt       # Dependências
└── assets/                 # (Opcional) arquivos extras
```

---

## 🧪 Exemplo de uso

- Digite os valores de pontuação mensais.
- O sistema calcula automaticamente:
  - Se atingiu a meta
  - Quando atinge o próximo nível
  - Quantos meses levou
- Mostra o resultado final com total de pontos e tempo acumulado.

---

## 👨‍💻 Desenvolvedor

> Feito por Arthur Mamedes – Estudante de Ciência da Computação e estagiário na Gerência de Normas e Critérios de Produtividade (GNCP).

📬 arthurmamedesborges@gmail.com

---

## 📄 Licença

Este projeto está sob a licença [MIT](assets/LICENSE).