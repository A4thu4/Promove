# 📈 Simulador PROMOVE - Cálculo de Progressão Funcional

- Foram feitos 2 Sistemas em Python para simular e calcular progressões funcionais com base em critérios de tempo, pontuação, titulação, responsabilidades e carreira.
- O 1º é um simulador geral que, baseado em uma **pontuação média irá, calcular a possível próxima evolução e após irá *fazer uma projeção*** de quanto tempo levaria para atingir o nível máximo da carreira e o tempo necessário entre cada evolução.
- O 2º é um simulador criado para facilitar o trabalho das GGDP's em fazer o cálculo da **possível próxima evolução** de um ou mais servidores, através de uma planilha do excel montada exclusivamente com esse propósito.
- Obs.: existe umsimulador separado destinado a UEG, devido a alguns requisitos serem diferentes.

---

## 🧠 Objetivo

Facilitar a análise de **progressão de servidores públicos**, simulando automaticamente o avanço entre níveis/ciclos, com base nas **tabelas de pontuação** e **regras da unidade de produtividade** conforme regras pré-estabelecidas pelo Governo para os Orgãos.

---

## 🚀 Funcionalidades

- 📊 Cálculo automático da progressão de nível.
- 📅 Detecção de **tempo necessário** entre interstício.
- ⚖️ Verificação de atingimento de requisitos mínimos.
- 📈 Exibição em tabela dos resultados com pontuações e datas.
- ✅ Ajuste dinâmico de critérios (nível, início, etc).
- 🎯 Ideal para simulações individuais ou em lote.

---

## 🛠 Tecnologias Usadas

- [Python 3.11+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- Pandas
- Numpy
- Openpyxl

---

## ⚙️ Como rodar localmente

1. Clone o repositório:

```bash
git clone https://github.com/A4thu4/Promove.git
cd Promove/app
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
streamlit run master.py
```

---

## 📁 Estrutura do Projeto

```bash
📦 Promove/
├── app
    └── data_utils.py       # Referências de dados para os Cálculos 
    └── layout.py           # Renderização dos Inputs
    └── logic.py            # 'Cérebro' do sistema
    └── master.py           # Código principal
├── assets/                 # Arquivos extras, imagens e licença
├── Dockerfile              # Arquivo para hospedagem em nuvem com Docker
├── README.md               # Este arquivo
├── requirements.txt        # Dependências
```

---

## 🧪 Exemplo de uso

- Digite os valores conforme requisitado.
- Clique para calcular resultados
- O sistema calcula automaticamente:
  - Se está Apto a evoluir.
  - Próximo Nível.
  - Quando atinge o próximo nível.
  - Quantos meses levou.
  - Pontuação Excedente.
- Mostra o resultado final com total de pontos e tempo acumulado.
- Mostra projeção de carreira até último nível.

---
## 🌐 Link do Simulador

- [SIMULADOR](https://simuladorpromove.streamlit.app/)
- [SIMULADOR-UEG](https://simuladorpromove-ueg.streamlit.app/)

---

## 👨‍💻 Desenvolvedor

> Feito por Arthur Mamedes Borges – Estudante de Ciência da Computação e estagiário na Gerência de Normas e Critérios de Produtividade (GNCP) da SEAD-GO.

📬 arthurmamedesborges@gmail.com

---

## 📄 Licença

Este projeto está sob a licença [MIT](assets/LICENSE).

