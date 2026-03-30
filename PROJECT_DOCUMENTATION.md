# 🌏 IMIGRATION_2030 — Documentação do Roadmap

> **Base de Conhecimento** para estruturação dos GitHub Projects (v2) na organização **ArthemizLabs**.
> Última atualização: 2026

---

## 🎯 Visão Geral

O roadmap **IMIGRATION_2030** concentra todas as iniciativas técnicas, acadêmicas e de idiomas necessárias para viabilizar a imigração qualificada até 2030. O acompanhamento é feito via GitHub Projects (v2), dividido em quatro camadas principais:

| Projeto                  | Tipo     | Foco                                        |
|--------------------------|----------|---------------------------------------------|
| Master Roadmap 2030      | Tabela   | Visão macro de carreira e fases             |
| OpsLedger & Sentinel     | Kanban   | Backend Java/C e Telemetria                 |
| Vendas3D                 | Kanban   | E-commerce Python/FastAPI                   |
| Arthemiz & SystemHealth  | Kanban   | Infra, Go e Monitoramento Docker            |
| The Global Resume        | Lista    | Contribuições Open Source e networking      |

---

## 🏛️ Pilares de Imigração

Todo item movido para **Done** deve contribuir com pelo menos um dos três pilares:

1. 🎓 **Diploma** — Formação acadêmica reconhecida (graduação, pós, certificações homologadas).
2. 🗣️ **Idioma C1/N2** — Proficiência comprovada em inglês (C1+) e/ou japonês (N2+).
3. 💼 **Portfólio de Alta Qualificação** — Contribuições open-source, projetos deployed, PRs merged.

---

## 📅 Fases do Roadmap

### PHASE_2026 — Fundação Técnica
**Objetivo:** Consolidar a base técnica em linguagens e certificações.

| Item                               | Tipo         | País Alvo | Repositório              |
|------------------------------------|--------------|-----------|--------------------------|
| Certificação AWS Solutions Arch.   | Certificação | Global    | ArthemizLabs/Certifications|
| Curso JLPT N3 (base)              | Idioma       | Japão     | —                        |
| English B2 → C1 Transition        | Idioma       | Canadá    | —                        |
| OpsLedger MVP (Java backend)       | Tech         | Global    | ArthemizLabs/OpsLedger   |
| Sentinel Agent v0.1 (C telemetria) | Tech         | Global    | ArthemizLabs/SentinelAgent|

### PHASE_2027 — Especialização e Portfólio
**Objetivo:** Projetos deployed e primeiras contribuições open-source reconhecidas.

| Item                               | Tipo         | País Alvo | Repositório              |
|------------------------------------|--------------|-----------|--------------------------|
| Vendas3D v1 (FastAPI + React)      | Tech         | Global    | ArthemizLabs/Vendas3D    |
| JLPT N2 Prep + Exam               | Idioma       | Japão     | —                        |
| IELTS 7.0+ (C1)                   | Idioma       | Canadá    | —                        |
| Contribuição Top-100 OSS Repo     | Tech         | Global    | The Global Resume        |
| Pós-Graduação / MBA TI (início)    | Acadêmico    | Global    | —                        |

### PHASE_2028 — Reconhecimento Internacional
**Objetivo:** Networking global e credenciais internacionais.

| Item                               | Tipo         | País Alvo | Repositório              |
|------------------------------------|--------------|-----------|--------------------------|
| Arthemiz Infra (Go + K8s)          | Tech         | Global    | ArthemizLabs/Arthemiz    |
| SystemHealth Dashboard (Docker)    | Tech         | Global    | ArthemizLabs/SystemHealth|
| JLPT N2 Pass + N1 Prep            | Idioma       | Japão     | —                        |
| CKA (Certified Kubernetes Admin)   | Certificação | Global    | ArthemizLabs/Certifications|
| 10 PRs merged em projetos externos | Tech         | Global    | The Global Resume        |

### PHASE_2029 — Transição e Aplicações
**Objetivo:** Candidatura a vistos e posicionamento final.

| Item                               | Tipo         | País Alvo | Repositório              |
|------------------------------------|--------------|-----------|--------------------------|
| Portfólio finalizado (GitHub Pages)| Tech         | Global    | ArthemizLabs/Portfolio   |
| Candidatura Express Entry (Canadá) | Acadêmico    | Canadá    | —                        |
| Candidatura Visto Tech (Japão)     | Acadêmico    | Japão     | —                        |
| Pós-Graduação concluída            | Acadêmico    | Global    | —                        |
| JLPT N1 (meta)                    | Idioma       | Japão     | —                        |

---

## 📋 Estrutura dos Projetos GitHub

### 1. Master Roadmap 2030

**Tipo:** Table (visão macro)
**Organização:** ArthemizLabs

#### Campos Personalizados

| Campo         | Tipo   | Opções                                                    |
|---------------|--------|-----------------------------------------------------------|
| Fase          | Select | PHASE_2026, PHASE_2027, PHASE_2028, PHASE_2029           |
| País Alvo     | Select | Japão 🇯🇵, Canadá 🇨🇦, Global 🌍                        |
| Tipo          | Select | Certificação 📜, Idioma 🗣️, Acadêmico 🎓, Tech 💻        |
| Pilar         | Select | Diploma 🎓, Idioma C1/N2 🗣️, Portfólio 💼                |
| Prioridade    | Select | 🔴 Alta, 🟡 Média, 🟢 Baixa                              |
| Estimativa    | Number | Story Points (1, 2, 3, 5, 8, 13)                         |
| Data Início   | Date   | —                                                         |
| Data Fim      | Date   | —                                                         |

#### Views

| View        | Configuração                                                     |
|-------------|------------------------------------------------------------------|
| Timeline    | Agrupado por **Fase**, ordenado por Data Início                 |
| Priority    | Filtrado por Tipo = Certificação OU Idioma; ordenado por Fase   |
| By Country  | Agrupado por **País Alvo**                                       |
| Kanban View | Status: Backlog → In Progress → Done                            |

---

### 2. Projetos Técnicos (Kanban Boards)

Cada repositório técnico possui um board Kanban individual com as seguintes colunas:

#### Colunas Padrão (Workflow Sênior)

| Coluna        | Descrição                                                      |
|---------------|----------------------------------------------------------------|
| 🗄️ Backlog     | Ideias brutas, requisitos sem DoD definido                    |
| ✅ Ready to Dev | Issues com Definition of Done (DoD) claro e critérios aceitos |
| 🔧 In Progress  | Trabalho ativo — máximo de 2 issues por pessoa simultâneas    |
| 🔍 In Review    | Código aguardando Pull Request / revisão de pares             |
| 🚀 Done         | Finalizado, testado e deployed                                |

#### OpsLedger & Sentinel Agent
- **Repositórios:** `ArthemizLabs/OpsLedger`, `ArthemizLabs/SentinelAgent`
- **Stack:** Java (Spring Boot), C (telemetria/daemon)
- **Labels padrão:** `backend`, `java`, `c-lang`, `telemetria`, `api`, `bug`, `enhancement`

#### Vendas3D
- **Repositório:** `ArthemizLabs/Vendas3D`
- **Stack:** Python, FastAPI, React
- **Labels padrão:** `backend`, `frontend`, `python`, `fastapi`, `ecommerce`, `bug`, `enhancement`

#### Arthemiz & SystemHealth
- **Repositórios:** `ArthemizLabs/Arthemiz`, `ArthemizLabs/SystemHealth`
- **Stack:** Go, Docker, Kubernetes, Prometheus/Grafana
- **Labels padrão:** `infra`, `go`, `docker`, `monitoring`, `k8s`, `bug`, `enhancement`

---

### 3. The Global Resume

**Tipo:** List (lista de contribuições)
**Objetivo:** Monitorar contribuições open-source para o portfólio de imigração.

#### Campos Personalizados

| Campo                  | Tipo   | Opções                          |
|------------------------|--------|---------------------------------|
| Link do PR             | Text   | URL do Pull Request             |
| Repositório Pai        | Text   | `owner/repo` do projeto externo |
| Status da Contribuição | Select | Draft 📝, Merged ✅, Rejected ❌ |
| Linguagem Principal    | Select | Java, Python, Go, C, TypeScript, Other |
| Stars do Repo          | Number | Número de estrelas do projeto   |
| Pilar                  | Select | Diploma 🎓, Idioma 🗣️, Portfólio 💼 |
| Data de Submissão      | Date   | —                               |

---

## 🤖 Automação (GitHub Actions)

### Regras de Automação por Projeto

| Trigger                            | Ação Automática                              |
|------------------------------------|----------------------------------------------|
| Issue aberta                       | Mover para coluna **Backlog**                |
| PR aberta com `Closes #issue`      | Mover issue para **In Review**               |
| PR merged                          | Mover issue para **Done**                    |
| Label `ready-to-dev` adicionada    | Mover issue para **Ready to Dev**            |
| Issue assigned                     | Mover para **In Progress**                   |

---

## 📐 Definition of Done (DoD)

Para que uma issue possa entrar em **Ready to Dev**, ela deve ter:

- [ ] Descrição clara do problema ou funcionalidade
- [ ] Critérios de aceite definidos
- [ ] Labels adequadas atribuídas
- [ ] Estimativa de esforço (story points)
- [ ] Milestone/Fase atribuída
- [ ] Alinhamento com pelo menos um **Pilar de Imigração**

Para mover para **Done**:

- [ ] Código implementado e testado
- [ ] PR aberta e revisada (mínimo 1 aprovação)
- [ ] CI/CD passou (build + testes)
- [ ] Documentação atualizada (se aplicável)
- [ ] Deployed em ambiente de produção/staging

---

## 🗂️ Referências e Links

- [GitHub Projects (v2) Docs](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub GraphQL API — Projects](https://docs.github.com/en/graphql/reference/objects#projectv2)
- [Express Entry (Canadá)](https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry.html)
- [Engineer Visa (Japão)](https://www.meti.go.jp/english/policy/mono_info_service/joho/it_jinzai.html)
- [JLPT Official](https://www.jlpt.jp/e/)
- [IELTS](https://www.ielts.org/)
