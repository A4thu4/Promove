# 📈 Simulador PROMOVE - Cálculo de Progressão Funcional

- Foram feitos 2 Sistemas em Python + Streamlit para simular e calcular progressões funcionais com base em critérios de tempo, pontuação, titulação
e carreira.
- O 1º (main.py) é um simulador geral que, baseado em uma **pontuação média irá, *fazer uma previsão*** de quanto tempo levaria para atingir o nível máximo da carreira e o tempo necessário entre cada evolução.
- O 2º (app_ggdp/master.py) é um simulador criado para facilitar o trabalho da GGDP para fazer o cálculo da **possível próxima evolução** de um ou mais servidores, através de uma planilha do excel montada exclusivamente com esse propósito.

---

## 🧠 Objetivo

Facilitar a análise de **progressão de servidores públicos**, simulando automaticamente o avanço entre níveis/ciclos, com base nas **tabelas de pontuação** e **regras da unidade de produtividade** de acordo com regras pré-estabelecidas pelo Governo para os Orgãos.

---

## 🚀 Funcionalidades

- 📊 Cálculo automático da progressão de nível.
- 📅 Detecção de **tempo necessário** entre interstício.
- ⚖️ Verificação de atingimento de requisitos mínimos.
- 📈 Exibição em tabela dos resultados com pontuações e datas.
- ✅ Ajuste dinâmico de critérios (nível, meta, início, etc).
- 🎯 Ideal para simulações individuais ou em lote.

---

## 🛠 Tecnologias Usadas

- [Python 3.9+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- Numpy
- Pandas
- Openpyxl

---

## ⚙️ Como rodar localmente

1. Clone o repositório:

```bash
git clone https://github.com/A4thu4/Promove.git
cd Promove
cd app_ggdp # para o segundo sistema
```

2.Crie o ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate   # Windows
```

3.Instale as dependências:

```bash
pip install -r requirements.txt
```

4.Rode o app:

```bash
streamlit run main.py # ou (master.py)
```

---

## 📁 Estrutura do Projeto

```bash
📦 Promove/
├── app_ggdp
    └── data_utils.py       # Referências de dados para os Cálculos 
    └── layout.py           # Renderização dos Inputs
    └── logic.py            # 'Cérebro' do sistema
    └── master.py           # Código principal (GGDP)
├── assets/                 # Arquivos extras, imagens e licença
├── Dockerfile              # Arquivo para hospedagem em nuvem com Docker
├── README.md               # Este arquivo
├── main.py                 # Código principal (Simulador)
├── requirements.txt        # Dependências
```

---

## 🧪 Exemplo de uso

- Digite os valores de pontuação mensais.
- O sistema calcula automaticamente:
  - Se está Apto a evoluir.
  - Próximo Nível.
  - Quando atinge o próximo nível.
  - Quantos meses levou.
- Mostra o resultado final com total de pontos e tempo acumulado.

---

## 👨‍💻 Desenvolvedor

> Feito por Arthur Mamedes – Estudante de Ciência da Computação e estagiário na Gerência de Normas e Critérios de Produtividade (GNCP).

📬 <arthurmamedesborges@gmail.com>

---

## 📄 Licença

Este projeto está sob a licença [MIT](assets/LICENSE).
