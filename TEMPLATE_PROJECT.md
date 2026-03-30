# 📐 TEMPLATE: GitHub Project (v2) — ArthemizLabs Standard

> Modelo reutilizável para criação de novos projetos GitHub Projects (v2) dentro da organização ArthemizLabs.
> Baseado na estrutura do **IMIGRATION_2030 Roadmap**.

---

## ✏️ Como usar este template

1. Copie este arquivo para `.github/projects/<nome-do-projeto>.json`
2. Preencha os campos marcados com `<!-- PREENCHA -->` abaixo
3. Execute o workflow `setup-projects.yml` com `dry_run=true` para validar
4. Execute com `dry_run=false` para criar o projeto na organização

---

## 📋 Template JSON — Kanban Board (Projetos Técnicos)

```json
{
  "name": "<!-- NOME DO PROJETO -->",
  "description": "<!-- DESCRIÇÃO CURTA -->",
  "type": "board",
  "organization": "ArthemizLabs",
  "readme": "<!-- DESCRIÇÃO LONGA DO OBJETIVO DO PROJETO -->",
  "custom_fields": [
    {
      "name": "Prioridade",
      "data_type": "SINGLE_SELECT",
      "options": [
        { "name": "🔴 Alta",  "color": "RED",    "description": "Bloqueador crítico" },
        { "name": "🟡 Média", "color": "YELLOW", "description": "Importante, não bloqueador" },
        { "name": "🟢 Baixa", "color": "GREEN",  "description": "Nice to have" }
      ]
    },
    {
      "name": "Estimativa",
      "data_type": "NUMBER",
      "description": "Story Points: 1, 2, 3, 5, 8, 13"
    },
    {
      "name": "Sprint",
      "data_type": "ITERATION",
      "description": "Sprint atual"
    },
    {
      "name": "Tipo",
      "data_type": "SINGLE_SELECT",
      "options": [
        { "name": "Feature",     "color": "BLUE",   "description": "Nova funcionalidade" },
        { "name": "Bug Fix",     "color": "RED",    "description": "Correção de bug" },
        { "name": "Tech Debt",   "color": "YELLOW", "description": "Dívida técnica" },
        { "name": "Docs",        "color": "GRAY",   "description": "Documentação" },
        { "name": "Infra",       "color": "PURPLE", "description": "Infraestrutura" }
      ]
    }
  ],
  "status_field": {
    "name": "Status",
    "options": [
      { "name": "🗄️ Backlog",      "color": "GRAY",   "description": "Ideias brutas, sem DoD" },
      { "name": "✅ Ready to Dev", "color": "BLUE",   "description": "DoD definido, pronto para iniciar" },
      { "name": "🔧 In Progress",  "color": "YELLOW", "description": "Trabalho ativo" },
      { "name": "🔍 In Review",    "color": "PURPLE", "description": "Aguardando PR/review" },
      { "name": "🚀 Done",         "color": "GREEN",  "description": "Finalizado e deployed" }
    ]
  },
  "views": [
    {
      "name": "Board",
      "layout": "BOARD_LAYOUT",
      "group_by": "Status",
      "description": "Kanban padrão"
    },
    {
      "name": "Backlog",
      "layout": "TABLE_LAYOUT",
      "filter": "Status = '🗄️ Backlog'",
      "sort_by": "Prioridade",
      "description": "Backlog priorizado"
    },
    {
      "name": "Sprint",
      "layout": "BOARD_LAYOUT",
      "filter": "Sprint = @current",
      "description": "Itens da sprint atual"
    }
  ],
  "milestones": [
    { "title": "<!-- v0.1 — MVP -->",    "description": "<!-- Funcionalidades mínimas -->" },
    { "title": "<!-- v0.2 — Feature -->", "description": "<!-- Expansão de features -->" },
    { "title": "<!-- v1.0 — Stable -->",  "description": "<!-- Versão estável com CI/CD -->" }
  ],
  "labels": [
    "bug", "enhancement", "documentation",
    "ready-to-dev", "in-progress", "in-review",
    "wontfix", "duplicate", "help-wanted"
  ]
}
```

---

## 📋 Template JSON — Table (Roadmaps e Planejamento)

```json
{
  "name": "<!-- NOME DO ROADMAP -->",
  "description": "<!-- DESCRIÇÃO DO ROADMAP -->",
  "type": "table",
  "organization": "ArthemizLabs",
  "readme": "<!-- OBJETIVO ESTRATÉGICO DO ROADMAP -->",
  "custom_fields": [
    {
      "name": "Fase",
      "data_type": "SINGLE_SELECT",
      "options": [
        { "name": "<!-- FASE_1 -->", "color": "BLUE",   "description": "<!-- Descrição da fase 1 -->" },
        { "name": "<!-- FASE_2 -->", "color": "GREEN",  "description": "<!-- Descrição da fase 2 -->" },
        { "name": "<!-- FASE_3 -->", "color": "YELLOW", "description": "<!-- Descrição da fase 3 -->" },
        { "name": "<!-- FASE_4 -->", "color": "RED",    "description": "<!-- Descrição da fase 4 -->" }
      ]
    },
    {
      "name": "Categoria",
      "data_type": "SINGLE_SELECT",
      "options": [
        { "name": "<!-- Categoria 1 -->", "color": "BLUE" },
        { "name": "<!-- Categoria 2 -->", "color": "GREEN" },
        { "name": "<!-- Categoria 3 -->", "color": "PURPLE" }
      ]
    },
    {
      "name": "Prioridade",
      "data_type": "SINGLE_SELECT",
      "options": [
        { "name": "🔴 Alta",  "color": "RED" },
        { "name": "🟡 Média", "color": "YELLOW" },
        { "name": "🟢 Baixa", "color": "GREEN" }
      ]
    },
    {
      "name": "Data Início", "data_type": "DATE"
    },
    {
      "name": "Data Fim", "data_type": "DATE"
    }
  ],
  "views": [
    {
      "name": "Timeline",
      "layout": "BOARD_LAYOUT",
      "group_by": "Fase",
      "sort_by": "Data Início",
      "description": "Visão cronológica por fase"
    },
    {
      "name": "All Items",
      "layout": "TABLE_LAYOUT",
      "description": "Tabela completa de itens"
    },
    {
      "name": "By Category",
      "layout": "TABLE_LAYOUT",
      "group_by": "Categoria",
      "description": "Agrupado por categoria"
    }
  ]
}
```

---

## 📋 Template JSON — List (Tracking e Monitoramento)

```json
{
  "name": "<!-- NOME DA LISTA -->",
  "description": "<!-- DESCRIÇÃO DA LISTA -->",
  "type": "list",
  "organization": "ArthemizLabs",
  "custom_fields": [
    {
      "name": "<!-- Campo 1 -->",
      "data_type": "TEXT",
      "description": "<!-- Descrição do campo -->"
    },
    {
      "name": "Status",
      "data_type": "SINGLE_SELECT",
      "options": [
        { "name": "<!-- Status 1 -->", "color": "GRAY" },
        { "name": "<!-- Status 2 -->", "color": "BLUE" },
        { "name": "<!-- Status 3 -->", "color": "GREEN" },
        { "name": "<!-- Status 4 -->", "color": "RED" }
      ]
    },
    {
      "name": "<!-- Métrica -->",
      "data_type": "NUMBER",
      "description": "<!-- Métrica numérica relevante -->"
    },
    {
      "name": "Data", "data_type": "DATE"
    }
  ],
  "views": [
    {
      "name": "All Items",
      "layout": "TABLE_LAYOUT",
      "sort_by": "Data DESC",
      "description": "Todos os itens em ordem cronológica"
    },
    {
      "name": "Active",
      "layout": "TABLE_LAYOUT",
      "filter": "Status != '<!-- Status Final -->'",
      "description": "Apenas itens ativos"
    }
  ]
}
```

---

## 🤖 Template de Workflow — Automação de Projeto

Crie um arquivo `.github/workflows/project-<nome>.yml` baseado no template abaixo:

```yaml
name: 🤖 <Nome do Projeto> — Auto Move Cards

on:
  issues:
    types: [opened, reopened, assigned, closed, labeled]
  pull_request:
    types: [opened, closed, ready_for_review]

jobs:
  move-to-backlog:
    name: Move to Backlog on Open
    runs-on: ubuntu-latest
    if: >
      github.event_name == 'issues' &&
      (github.event.action == 'opened' || github.event.action == 'reopened')
    steps:
      - uses: actions/add-to-project@v1.0.2
        with:
          project-url: https://github.com/orgs/ArthemizLabs/projects/<PROJECT_NUMBER>
          github-token: ${{ secrets.PROJECT_TOKEN }}

  move-to-ready:
    name: Move to Ready to Dev
    runs-on: ubuntu-latest
    if: >
      github.event_name == 'issues' &&
      github.event.action == 'labeled' &&
      github.event.label.name == 'ready-to-dev'
    steps:
      - uses: titoportas/update-project-fields@v0.1.0
        with:
          project-url: https://github.com/orgs/ArthemizLabs/projects/<PROJECT_NUMBER>
          github-token: ${{ secrets.PROJECT_TOKEN }}
          field-keys: Status
          field-values: "✅ Ready to Dev"

  move-to-in-progress:
    name: Move to In Progress on Assign
    runs-on: ubuntu-latest
    if: >
      github.event_name == 'issues' &&
      github.event.action == 'assigned'
    steps:
      - uses: titoportas/update-project-fields@v0.1.0
        with:
          project-url: https://github.com/orgs/ArthemizLabs/projects/<PROJECT_NUMBER>
          github-token: ${{ secrets.PROJECT_TOKEN }}
          field-keys: Status
          field-values: "🔧 In Progress"

  move-to-review:
    name: Move to In Review on PR open
    runs-on: ubuntu-latest
    if: >
      github.event_name == 'pull_request' &&
      github.event.action == 'opened' &&
      github.event.pull_request.draft == false
    steps:
      - uses: titoportas/update-project-fields@v0.1.0
        with:
          project-url: https://github.com/orgs/ArthemizLabs/projects/<PROJECT_NUMBER>
          github-token: ${{ secrets.PROJECT_TOKEN }}
          field-keys: Status
          field-values: "🔍 In Review"

  move-to-done:
    name: Move to Done on PR merge
    runs-on: ubuntu-latest
    if: >
      github.event_name == 'pull_request' &&
      github.event.action == 'closed' &&
      github.event.pull_request.merged == true
    steps:
      - uses: titoportas/update-project-fields@v0.1.0
        with:
          project-url: https://github.com/orgs/ArthemizLabs/projects/<PROJECT_NUMBER>
          github-token: ${{ secrets.PROJECT_TOKEN }}
          field-keys: Status
          field-values: "🚀 Done"
```

---

## 🏷️ Labels Padrão (Aplicar em todos os repositórios)

| Label           | Cor      | Uso                                      |
|-----------------|----------|------------------------------------------|
| `ready-to-dev`  | `#0075ca` | Issue com DoD claro, pronta para iniciar |
| `in-progress`   | `#e4e669` | Trabalho ativo                           |
| `in-review`     | `#7057ff` | Aguardando PR/review                     |
| `bug`           | `#d73a4a` | Bug reportado                            |
| `enhancement`   | `#a2eeef` | Nova feature                             |
| `documentation` | `#0075ca` | Atualização de docs                      |
| `help-wanted`   | `#008672` | Contribuição externa bem-vinda           |
| `wontfix`       | `#ffffff` | Não será corrigido                       |
| `roadmap-2030`  | `#f9d0c4` | Relacionado ao roadmap de imigração      |
| `oss-contribution` | `#bfd4f2` | Contribuição open-source externa       |

---

## ✅ Checklist de Criação de Projeto

Ao criar um novo projeto usando este template:

- [ ] JSON de configuração criado em `.github/projects/`
- [ ] Workflow de automação criado em `.github/workflows/`
- [ ] Issue templates relevantes adicionados em `.github/ISSUE_TEMPLATE/`
- [ ] Labels padrão criadas no repositório
- [ ] `PROJECT_TOKEN` configurado como secret da organização
- [ ] Projeto criado na organização ArthemizLabs
- [ ] Campos personalizados configurados
- [ ] Views configuradas
- [ ] Workflow de automação testado com `dry_run=true`
- [ ] Projeto linkado ao repositório correspondente
