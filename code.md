---
name: code-auditor
description: "Audits project code quality, architecture, directory structure, naming conventions, clean code practices, and performance anti-patterns. Use this skill ALWAYS when the user asks to 'review my project structure', 'audit code quality', 'check my architecture', 'is my project well organized', 'review naming conventions', 'what is missing in my project', 'how can I improve my project', 'check clean code', 'review my folder structure', 'what should be in root', 'analyze my codebase', or any variation. Also triggers when the user shares a project and asks for general feedback, improvement suggestions, or says things like 'look at my project', 'what do you think of my code structure', or 'how can I upgrade this'. Supports Python/FastAPI, Java/Spring Boot, Node.js/Next.js, Vanilla HTML+CSS+JS, SQL schemas, and mixed/full-stack projects."
---
 
# Code Auditor
 
A structural, architectural, and clean-code auditor for software projects. Analyzes directory layout, naming conventions, architecture fitness, code quality, and upgrade opportunities. Does NOT audit security — use the `security-auditor` skill for that.
 
---
 
## Execution Flow
 
1. **Detect stack & project type** — identify languages, frameworks, and project scale.
2. **Recommend architecture** — based on stack and scale, suggest the best-fit pattern.
3. **Run all relevant modules** — skip modules that don't apply to the detected stack.
4. **Classify findings** — ✅ Pass / ⚠️ Warning / ❌ Fail.
5. **Generate report** — summary checklist first, then detailed findings with examples and fixes.
 
---
 
## Step 1 — Stack & Scale Detection
 
```bash
# Detect languages and frameworks
echo "=== PROJECT ROOT ==="
ls -la
 
echo "=== LANGUAGE INDICATORS ==="
ls *.py pyproject.toml requirements.txt setup.py main.py app.py 2>/dev/null && echo "[PYTHON]"
ls pom.xml build.gradle 2>/dev/null && echo "[JAVA]"
ls package.json 2>/dev/null && echo "[NODE/JS/TS]"
ls index.html 2>/dev/null && echo "[VANILLA HTML]"
ls *.sql 2>/dev/null && echo "[SQL]"
ls Dockerfile docker-compose.yml 2>/dev/null && echo "[DOCKER]"
 
echo "=== FRAMEWORK ==="
grep -s "fastapi\|flask\|django" requirements.txt pyproject.toml 2>/dev/null
grep -s "spring-boot\|spring-web" pom.xml build.gradle 2>/dev/null
grep -s "next\|express\|nestjs\|vite\|react" package.json 2>/dev/null
 
echo "=== PROJECT SCALE ==="
find . -name "*.py" -o -name "*.java" -o -name "*.ts" -o -name "*.js" 2>/dev/null \
  | grep -v node_modules | grep -v __pycache__ | grep -v ".git" | wc -l
# < 10 files = micro/script | 10-50 = small | 50-200 = medium | 200+ = large
```
 
---
 
## Step 2 — Architecture Recommendation
 
Based on detected stack and scale, recommend and then audit against the appropriate pattern.
 
### Recommendation Table
 
| Stack | Scale | Recommended Architecture |
|-------|-------|--------------------------|
| Python / FastAPI | Small | **Flat layered**: `routers/` → `services/` → `models/` |
| Python / FastAPI | Medium+ | **Layered with modules**: feature folders each containing `router.py`, `service.py`, `repository.py`, `schema.py` |
| Java / Spring Boot | Any | **Layered MVC**: `controller/` → `service/` → `repository/` → `model/` + `dto/` + `config/` |
| Java / Spring Boot | Large | **Clean / Hexagonal**: `domain/`, `application/`, `infrastructure/`, `interfaces/` |
| Node.js / Express | Small | **MVC**: `routes/` → `controllers/` → `services/` → `models/` |
| Node.js / Next.js | Medium+ | **Feature-based**: `features/[name]/{components,hooks,api,types}` + `shared/` |
| Vanilla HTML+CSS+JS | Small | **Flat**: `index.html`, `css/`, `js/`, `assets/` |
| Vanilla HTML+CSS+JS | Medium+ | **Component-like**: `pages/`, `components/`, `css/`, `js/utils/`, `assets/` |
| SQL Schema | Any | Organized by domain: `schema/`, `migrations/`, `seeds/`, `views/`, `procedures/` |
| Full-stack monorepo | Any | `apps/frontend/`, `apps/backend/`, `packages/shared/`, `infra/` |
 
State which architecture is detected or recommended, and why, before running the structural audit.
 
---
 
## Module 1 — Root Hygiene
 
Every project should have a clean, intentional root. Audit what is present, missing, or misplaced.
 
```bash
echo "=== ROOT FILES ==="
ls -la | grep "^-"
 
echo "=== DIRECTORIES ==="
ls -d */ 2>/dev/null
```
 
### Required at root (flag ❌ if missing)
| File | Purpose | All Stacks | Stack-specific |
|------|---------|------------|----------------|
| `README.md` | Project overview, setup, usage | ✅ | — |
| `.gitignore` | Ignore rules | ✅ | — |
| `.env.example` | Env var template (no real values) | ✅ | — |
| `LICENSE` | License declaration | ✅ | — |
| `requirements.txt` or `pyproject.toml` | Python deps | — | Python |
| `pom.xml` or `build.gradle` | Java deps | — | Java |
| `package.json` | Node deps | — | Node/TS |
| `Dockerfile` | Container definition | — | If Docker used |
| `.dockerignore` | Docker ignore | — | If Docker used |
 
### Should NOT be at root (flag ⚠️ if found)
- Business logic files (`main_logic.py`, `helper.js`, `utils.java` at root)
- Data files (`.csv`, `.json` data dumps)
- Compiled/build artifacts (`*.class`, `*.pyc`, `dist/` not in `.gitignore`)
- Test files directly at root (`test.py`, `Test.java`)
- Multiple entry points with unclear purpose
 
```bash
# Check for misplaced files at root
find . -maxdepth 1 -name "*.py" | grep -v "main.py\|app.py\|manage.py\|setup.py\|conftest.py"
find . -maxdepth 1 -name "*.java" 2>/dev/null
find . -maxdepth 1 -name "*.csv" -o -maxdepth 1 -name "*.json" 2>/dev/null \
  | grep -v "package.json\|tsconfig.json\|package-lock.json"
find . -maxdepth 1 -type d | grep -vE "^\.$|\.git|node_modules|__pycache__|\.idea|\.vscode"
```
 
---
 
## Module 2 — Directory Structure & Naming Conventions
 
### Python / FastAPI
 
```bash
echo "=== PYTHON STRUCTURE ==="
find . -type d | grep -vE "__pycache__|\.git|\.venv|venv|node_modules|\.idea" | sort
 
# Check for flat layered (small) vs modular (medium+)
ls app/ src/ 2>/dev/null
find . -name "router.py" -o -name "routers.py" -o -name "routes.py" 2>/dev/null
find . -name "service.py" -o -name "services.py" 2>/dev/null
find . -name "repository.py" -o -name "repositories.py" 2>/dev/null
find . -name "schema.py" -o -name "schemas.py" 2>/dev/null
find . -name "model.py" -o -name "models.py" 2>/dev/null
```
 
**Expected structure (flat layered):**
```
project/
├── app/
│   ├── main.py           # FastAPI app instance
│   ├── routers/          # Route definitions only
│   ├── services/         # Business logic
│   ├── repositories/     # DB access
│   ├── schemas/          # Pydantic models (request/response)
│   ├── models/           # SQLAlchemy / ORM models
│   ├── core/             # Config, settings, security utils
│   └── dependencies.py   # Shared Depends()
├── tests/
├── alembic/              # If using Alembic migrations
├── requirements.txt
├── .env.example
└── README.md
```
 
**Naming rules (flag ❌ if violated):**
- All directories: `snake_case`
- All Python files: `snake_case.py`
- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Pydantic schemas: `EntityCreate`, `EntityRead`, `EntityUpdate` (not `EntityDTO`)
 
```bash
# Flag camelCase or PascalCase directories
find . -type d | grep -vE "__pycache__|\.git|\.venv|venv" | grep -E "[A-Z]"
 
# Flag camelCase Python files
find . -name "*.py" | grep -E "[A-Z]" | grep -v "README\|__"
 
# Check class naming inside files
grep -rn "^class " --include="*.py" . --exclude-dir=__pycache__ | grep -v "class [A-Z]"
 
# Check function naming (should be snake_case)
grep -rn "^def [a-z]" --include="*.py" . --exclude-dir=__pycache__ | grep -E "def [a-z]+[A-Z]"
```
 
---
 
### Java / Spring Boot
 
```bash
echo "=== JAVA STRUCTURE ==="
find . -type d | grep -vE "\.git|\.idea|target|build|\.gradle" | sort
 
# Check package structure
find . -name "*.java" | head -30
find . -name "*Controller.java" | head -10
find . -name "*Service.java" | head -10
find . -name "*Repository.java" | head -10
find . -name "*DTO.java" -o -name "*Dto.java" | head -10
find . -name "*Entity.java" -o -name "*Model.java" | head -10
find . -name "*Config.java" | head -10
find . -name "*Exception.java" | head -10
```
 
**Expected package structure:**
```
src/main/java/com/company/project/
├── controller/       # @RestController — HTTP layer only
├── service/          # @Service — business logic
├── repository/       # @Repository — data access (JPA)
├── model/ or entity/ # @Entity — JPA entities
├── dto/              # Data Transfer Objects (request/response shapes)
├── config/           # @Configuration beans
├── exception/        # Custom exceptions + @ControllerAdvice
├── security/         # Spring Security config (if used)
└── util/             # Stateless utility classes only
src/main/resources/
├── application.properties (or application.yml)
├── application-dev.properties
└── application-prod.properties
src/test/
```
 
**Naming rules (flag ❌ if violated):**
- Classes: `PascalCase`
- Methods and variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Packages: all `lowercase`, no underscores
- Controllers: `EntityController.java`
- Services: `EntityService.java` (interface) + `EntityServiceImpl.java`
- Repos: `EntityRepository.java`
- DTOs: `EntityRequestDTO.java`, `EntityResponseDTO.java`
- Entities: `Entity.java` (not `EntityModel`, not `EntityBean`)
 
```bash
# Flag wrong naming
find . -name "*.java" | grep -v "src" # Java files outside src/
find . -name "*Impl.java" | xargs grep -L "implements" 2>/dev/null # Impl without interface
grep -rn "class.*Controller" --include="*.java" . | grep -v "@RestController\|@Controller" # Controller without annotation
grep -rn "class.*Service[^I]" --include="*.java" . | grep -v "@Service\|interface " # Service without annotation or interface
```
 
---
 
### Node.js / Next.js
 
```bash
echo "=== NODE STRUCTURE ==="
find . -type d | grep -vE "node_modules|\.git|\.next|dist|build" | sort
 
ls src/ app/ pages/ components/ features/ lib/ utils/ hooks/ types/ styles/ 2>/dev/null
cat package.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('Scripts:', list(d.get('scripts',{}).keys()))" 2>/dev/null
```
 
**Expected structure (Next.js App Router):**
```
project/
├── app/                  # App Router pages and layouts
│   ├── layout.tsx
│   ├── page.tsx
│   └── [feature]/
├── components/           # Shared UI components
│   └── ui/               # Primitives (Button, Input, etc.)
├── features/             # Feature-specific logic
│   └── [feature]/
│       ├── components/
│       ├── hooks/
│       ├── actions.ts
│       └── types.ts
├── lib/                  # Utilities, helpers, configs
├── hooks/                # Shared hooks
├── types/                # Global TypeScript types
├── styles/               # Global CSS
├── public/               # Static files (images, fonts, icons)
└── tests/ or __tests__/
```
 
**Naming rules:**
- Components: `PascalCase.tsx`
- Utilities/hooks: `camelCase.ts`
- Directories: `kebab-case` or `camelCase` (be consistent)
- Hooks: must start with `use` prefix (`useAuth.ts`, not `auth.ts`)
- Types/interfaces: `PascalCase`, interfaces prefixed with `I` is optional but be consistent
 
```bash
# Components not PascalCase
find . -path "*/components/*.tsx" -o -path "*/components/*.jsx" 2>/dev/null \
  | grep -v node_modules | grep -E "/[a-z]"
 
# Hooks not starting with use
find . -name "*.ts" -path "*/hooks/*" 2>/dev/null | grep -v node_modules | grep -v "^use"
```
 
---
 
### Vanilla HTML + CSS + JS
 
**Expected structure:**
```
project/
├── index.html
├── pages/            # Additional HTML pages
├── css/
│   ├── main.css      # or style.css
│   └── components/   # Component-specific styles
├── js/
│   ├── main.js       # Entry point
│   └── utils/        # Helper functions
├── assets/
│   ├── images/
│   ├── fonts/
│   └── icons/
└── README.md
```
 
```bash
find . -maxdepth 3 -type f | grep -vE "\.git" | sort
# Flag: .js or .css files directly at root
find . -maxdepth 1 -name "*.css" -o -maxdepth 1 -name "*.js" 2>/dev/null | grep -v "node_modules"
# Flag: images not in assets/
find . -name "*.png" -o -name "*.jpg" -o -name "*.svg" 2>/dev/null \
  | grep -v "assets/\|public/\|node_modules" | grep -v ".git"
```
 
---
 
### SQL Schema
 
```bash
find . -name "*.sql" | sort
find . -type d | grep -E "sql|schema|migration|seed|db" | sort
```
 
**Expected structure:**
```
db/
├── schema/           # Table definitions (CREATE TABLE)
├── migrations/       # Versioned changes (V001__description.sql)
├── seeds/            # Initial/test data
├── views/            # CREATE VIEW statements
└── procedures/       # Stored procedures / functions
```
 
**Naming rules:**
- Tables: `plural_snake_case` (`users`, `order_items`)
- Columns: `snake_case` (`created_at`, `user_id`)
- Foreign keys: `referenced_table_id` (`user_id`, `product_id`)
- Indexes: `idx_table_column` (`idx_users_email`)
- Migration files: `V001__create_users_table.sql` (versioned)
 
```bash
# Find SQL naming violations
grep -rn "CREATE TABLE [A-Z]\|CREATE TABLE [a-z]*[A-Z]" --include="*.sql" . # PascalCase tables
grep -rn "CREATE TABLE.*[a-z][A-Z]" --include="*.sql" . # camelCase tables
# Find tables without primary key
grep -B5 -A20 "CREATE TABLE" --include="*.sql" -rn . | grep -A20 "CREATE TABLE" | grep -v "PRIMARY KEY\|SERIAL\|AUTO_INCREMENT" | grep ");" 
```
 
---
 
## Module 3 — Asset Organization
 
```bash
echo "=== ASSETS AUDIT ==="
find . -type d -name "assets" -o -type d -name "static" -o -type d -name "public" 2>/dev/null \
  | grep -v node_modules | grep -v .git
 
# What's inside
find . \( -path "*/assets/*" -o -path "*/static/*" -o -path "*/public/*" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" | sort
```
 
### What belongs in `/assets` or `/static` or `/public`
✅ **Should be here:**
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg` (UI icons and illustrations)
- Fonts: `.woff`, `.woff2`, `.ttf`, `.otf`
- Static icons: `.ico`, `.svg` favicons
- PDF/documents that are served statically
 
❌ **Should NOT be here:**
- Configuration files (`.json` configs, `.yml`)
- Python/Java/JS source files
- Database dumps or CSV data files
- Private keys or certificates
- `.env` files
 
⚠️ **Flag if missing:**
- No `/assets` or `/static` or `/public` directory in a frontend project
- Images scattered across root or source directories
 
---
 
## Module 4 — Clean Code & Code Quality
 
### Function & File Size
 
```bash
# Python: functions over 50 lines (God functions)
python3 - << 'EOF'
import ast, os, sys
 
def check_functions(path):
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.venv', 'venv', '.git']]
        for f in files:
            if not f.endswith('.py'):
                continue
            fpath = os.path.join(root, f)
            try:
                tree = ast.parse(open(fpath).read())
            except:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lines = (node.end_lineno - node.lineno)
                    if lines > 50:
                        print(f"LONG FUNCTION ({lines} lines): {fpath}:{node.lineno} → {node.name}()")
 
check_functions('.')
EOF
 
# Python: files over 300 lines (God modules)
find . -name "*.py" | grep -v __pycache__ | grep -v venv | xargs wc -l 2>/dev/null \
  | sort -rn | awk '$1 > 300 {print "LARGE FILE ("$1" lines):", $2}' | head -15
 
# Java: methods over 50 lines (approximate)
awk '/\{/{depth++} /\}/{depth--} depth==1 && /\(/' src/**/*.java 2>/dev/null | head -20
 
# JS/TS: functions over 50 lines
find . -name "*.ts" -o -name "*.tsx" -o -name "*.js" 2>/dev/null | grep -v node_modules \
  | xargs wc -l 2>/dev/null | sort -rn | awk '$1 > 300 {print "LARGE FILE ("$1" lines):", $2}' | head -15
```
 
### Dead Code Detection
 
```bash
# Python: unused imports
grep -rn "^import \|^from " --include="*.py" . --exclude-dir=__pycache__ --exclude-dir=venv \
  | awk -F: '{print $1, $3}' | while read file imp; do
      mod=$(echo $imp | awk '{print $2}' | cut -d. -f1)
      grep -q "$mod" "$file" 2>/dev/null && true || echo "POSSIBLY UNUSED IMPORT: $file → $imp"
    done 2>/dev/null | head -20
 
# Python: functions defined but never called (simple heuristic)
grep -rn "^def \|^    def " --include="*.py" . --exclude-dir=__pycache__ | head -30
 
# JS/TS: exported but nothing imports it (basic check)
grep -rn "^export function\|^export const\|^export class" --include="*.ts" --include="*.tsx" . \
  --exclude-dir=node_modules | head -20
 
# Java: unused private methods (approximate)
grep -rn "private.*(" --include="*.java" . | grep -v "//" | head -20
```
 
### Naming Consistency
 
```bash
# Python: mixed naming styles in same file
grep -rn "^def " --include="*.py" . --exclude-dir=__pycache__ \
  | grep -E "def [a-z]+[A-Z]" | head -10   # camelCase functions (wrong for Python)
 
# JS/TS: variables using snake_case (wrong for JS)
grep -rn "const [a-z]+_[a-z]\|let [a-z]+_[a-z]\|var [a-z]+_[a-z]" \
  --include="*.ts" --include="*.tsx" --include="*.js" . --exclude-dir=node_modules | head -10
```
 
### Logic Leaking Into Wrong Layer
 
```bash
# Python/FastAPI: business logic in routers (DB calls or complex logic in @router.get/post)
grep -rn -A 15 "@router\.\|@app\." --include="*.py" . --exclude-dir=__pycache__ \
  | grep -E "session\.|db\.|\.query\(|\.execute\(|\.filter\(" | head -10
# Flag: DB operations directly in route handlers (should be in service/repository)
 
# Java: business logic in Controller (@RestController methods doing more than calling service)
grep -rn -A 10 "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping" --include="*.java" . \
  | grep -E "repository\.|\.save\(|\.findBy\|if.*&&|for.*:" | head -10
 
# JS/Next.js: API calls or fetch inside components directly (no service layer)
grep -rn "fetch(\|axios\." --include="*.tsx" --include="*.jsx" . --exclude-dir=node_modules \
  | grep -v "api/\|services/\|lib/\|hooks/" | head -10
```
 
### Comment Quality
 
```bash
# Python: functions without docstrings
grep -rn "^def \|^    def " --include="*.py" . --exclude-dir=__pycache__ \
  | grep -v "__init__\|__str__\|__repr__" | while read line; do
      file=$(echo $line | cut -d: -f1)
      linenum=$(echo $line | cut -d: -f2)
      nextline=$((linenum + 1))
      sed -n "${nextline}p" "$file" 2>/dev/null | grep -q '"""' || echo "NO DOCSTRING: $line"
    done 2>/dev/null | head -15
 
# TODO/FIXME/HACK left in code
grep -rn "TODO\|FIXME\|HACK\|XXX\|TEMP\b" \
  --include="*.py" --include="*.java" --include="*.ts" --include="*.tsx" --include="*.js" \
  . --exclude-dir=node_modules --exclude-dir=__pycache__ | head -20
```
 
---
 
## Module 5 — Architecture Compliance
 
Verify that the detected or recommended architecture is actually followed.
 
```bash
# Python: check for circular imports (basic)
python3 -c "
import subprocess, sys
result = subprocess.run(['python3', '-m', 'py_compile'] + 
  __import__('glob').glob('**/*.py', recursive=True), capture_output=True, text=True)
print(result.stderr[:2000] if result.stderr else 'No syntax errors detected')
" 2>/dev/null
 
# Python: service importing from router (wrong direction)
grep -rn "from.*router\|import.*router" --include="*.py" . \
  --exclude-dir=__pycache__ | grep -v "app/main\|__init__" | head -10
 
# Java: controller importing repository directly (skipping service layer)
grep -rn "import.*Repository" --include="*Controller.java" . | head -10
 
# Java: entity returned directly from controller (should return DTO)
grep -rn "ResponseEntity<.*Entity>\|ResponseEntity<.*Model>" --include="*.java" . | head -10
```
 
### Separation of Concerns Score
 
For each layer found, check if it respects its responsibility:
 
| Layer | Should contain | Should NOT contain |
|-------|---------------|-------------------|
| Router / Controller | Route definitions, input parsing, calling service | Business logic, DB calls |
| Service | Business rules, orchestration | HTTP objects, DB sessions (pass as arg) |
| Repository | DB queries only | Business logic, HTTP concepts |
| Schema / DTO | Data shapes | Methods with logic |
| Model / Entity | DB mapping | Business rules, HTTP concepts |
 
---
 
## Module 6 — Performance Anti-patterns
 
### Python / FastAPI
 
```bash
# Sync functions in async context (blocking the event loop)
grep -rn "^def " --include="*.py" . --exclude-dir=__pycache__ \
  | grep -v "async" | while read line; do
      file=$(echo $line | cut -d: -f1)
      fname=$(echo $line | grep -oE "def [a-z_]+")
      grep -q "requests.get\|requests.post\|time.sleep\|open(" "$file" 2>/dev/null \
        && echo "POTENTIAL BLOCKING CALL in sync route: $line"
    done 2>/dev/null | head -10
 
# N+1 query pattern: DB call inside a loop
grep -rn -B2 "for.*in\|\.all()\|\.filter(" --include="*.py" . --exclude-dir=__pycache__ \
  | grep -A2 "for " | grep "\.query\|\.execute\|session\." | head -10
 
# Missing async on FastAPI route handlers that do I/O
grep -rn "@router\.\|@app\." --include="*.py" . --exclude-dir=__pycache__ \
  | grep -v "async" | head -10
```
 
### Java / Spring Boot
 
```bash
# N+1: @OneToMany without LAZY or fetch join
grep -rn "@OneToMany\|@ManyToOne\|@ManyToMany" --include="*.java" . \
  | grep -v "fetch = FetchType.LAZY\|FetchType.LAZY" | head -10
 
# Missing @Transactional on multi-step DB operations
grep -rn "void.*save\|void.*update\|void.*delete\|void.*create" --include="*Service*.java" . \
  | grep -v "@Transactional" | head -10
 
# Returning List when Page/Slice should be used (no pagination)
grep -rn "List<.*> get\|List<.*> find\|List<.*> fetch" --include="*Service*.java" . | head -10
```
 
### Node / TypeScript
 
```bash
# Missing async/await — synchronous heavy operations
grep -rn "JSON.parse\|JSON.stringify\|fs.readFileSync\|fs.writeFileSync" \
  --include="*.ts" --include="*.tsx" . --exclude-dir=node_modules | head -10
 
# Fetching all records without limit/pagination
grep -rn "findMany()\|findAll()\|\.find({})" \
  --include="*.ts" . --exclude-dir=node_modules | grep -v "where\|take\|limit" | head -10
```
 
---
 
## Module 7 — Missing Configs & Tooling
 
```bash
echo "=== TOOLING AUDIT ==="
 
# Linter
ls .eslintrc* .eslintignore eslint.config.* 2>/dev/null && echo "✅ ESLint found" || echo "❌ No ESLint config (Node/TS)"
ls .flake8 setup.cfg pyproject.toml ruff.toml 2>/dev/null | xargs grep -l "flake8\|ruff\|pylint" 2>/dev/null \
  && echo "✅ Python linter found" || echo "❌ No Python linter config"
ls checkstyle*.xml .checkstyle 2>/dev/null && echo "✅ Checkstyle found (Java)" || echo "⚠️ No Checkstyle (Java)"
 
# Formatter
ls .prettierrc* prettier.config.* 2>/dev/null && echo "✅ Prettier found" || echo "⚠️ No Prettier config"
ls .editorconfig 2>/dev/null && echo "✅ EditorConfig found" || echo "⚠️ No .editorconfig"
 
# Type checking
ls tsconfig.json 2>/dev/null && echo "✅ TypeScript config found" || echo "⚠️ No tsconfig.json (Node project)"
grep -s "mypy\|pyright" pyproject.toml setup.cfg 2>/dev/null && echo "✅ Python type checker found" || echo "⚠️ No mypy/pyright config"
 
# Tests
ls tests/ test/ __tests__/ spec/ 2>/dev/null && echo "✅ Test directory found" || echo "❌ No test directory found"
grep -s "pytest\|unittest" requirements.txt pyproject.toml 2>/dev/null && echo "✅ pytest configured"
grep -s "jest\|vitest\|mocha" package.json 2>/dev/null && echo "✅ JS test runner configured"
 
# CI/CD
ls .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null && echo "✅ GitHub Actions found" || echo "⚠️ No CI/CD pipeline"
 
# Docker
ls Dockerfile 2>/dev/null && echo "✅ Dockerfile found" || echo "⚠️ No Dockerfile"
ls docker-compose.yml docker-compose.yaml 2>/dev/null && echo "✅ docker-compose found"
 
# Git hooks
ls .husky/ 2>/dev/null && echo "✅ Husky git hooks found" || echo "⚠️ No git hooks (consider husky + lint-staged)"
```
 
---
 
## Module 8 — Upgrade Suggestions
 
Check for outdated patterns that have better modern equivalents.
 
```bash
# Python: requirements.txt → pyproject.toml
ls requirements.txt 2>/dev/null && ! ls pyproject.toml 2>/dev/null \
  && echo "⬆️ UPGRADE: Migrate from requirements.txt to pyproject.toml (PEP 517)"
 
# Python: print() debugging left in code
grep -rn "^print(\|    print(" --include="*.py" . --exclude-dir=__pycache__ \
  | grep -v "test\|debug\|cli\|manage.py\|__main__" | head -10
 
# Python: bare except clauses
grep -rn "except:" --include="*.py" . --exclude-dir=__pycache__ | head -10
# Suggest: except Exception as e: (or specific exception type)
 
# Python: no type hints
grep -rn "^def \|^    def " --include="*.py" . --exclude-dir=__pycache__ \
  | grep -v "->.*:" | grep -v "#" | head -15
# Suggest: add return type hints and parameter type hints
 
# Java: using Date instead of LocalDate/LocalDateTime
grep -rn "import java.util.Date\|new Date()" --include="*.java" . | head -5
# Suggest: java.time.LocalDate / LocalDateTime (Java 8+)
 
# Java: Optional not used for nullable returns
grep -rn "return null;" --include="*Service*.java" --include="*Repository*.java" . | head -5
# Suggest: return Optional.empty()
 
# Node: var instead of const/let
grep -rn "\bvar " --include="*.ts" --include="*.tsx" --include="*.js" . \
  --exclude-dir=node_modules | head -10
 
# Node: CommonJS require() in TypeScript project
grep -rn "require(" --include="*.ts" --include="*.tsx" . --exclude-dir=node_modules | head -10
# Suggest: use ES modules (import/export)
 
# SQL: no indexes on foreign keys
grep -rn "REFERENCES\|FOREIGN KEY" --include="*.sql" . | while read line; do
  table=$(echo $line | grep -oE "REFERENCES [a-z_]+")
  file=$(echo $line | cut -d: -f1)
  grep -q "INDEX\|idx_" "$file" 2>/dev/null || echo "⚠️ Foreign key without index: $line"
done 2>/dev/null | head -10
```
 
---
 
## Report Format
 
Generate the report in this exact order:
 
```markdown
# 🏗️ Code Audit Report — [Project Name]
Date: [current date]
Stack: [detected stack]
Scale: [micro / small / medium / large — file count]
 
## 🎯 Architecture Assessment
**Detected pattern:** [what was found]
**Recommended pattern:** [what should be used and why]
**Compliance:** [% or description]
 
---
 
## 📋 Summary Checklist
 
### Structure & Root
- ✅ README.md present
- ❌ .env.example missing
- ⚠️ Business logic file found at root (utils.py)
[...all root checks]
 
### Architecture
- ✅ Layered structure detected (routers → services → repositories)
- ❌ Business logic found in router layer (3 violations)
[...all architecture checks]
 
### Clean Code
- ⚠️ 2 functions over 50 lines
- ❌ No type hints in service layer
- ✅ Naming conventions followed
[...all clean code checks]
 
### Tooling
- ✅ pytest configured
- ❌ No linter configured
- ⚠️ No CI/CD pipeline
[...all tooling checks]
 
---
 
## 🔍 Detailed Findings
 
### ❌ [Issue Title] — FAIL
**File:** `app/routers/user.py:34`
**Problem:** [description]
 
**Current code:**
```[lang]
[real code excerpt]
```
 
**How it should look:**
```[lang]
[corrected code]
```
 
**Why this matters:** [1 sentence on impact]
 
---
 
### ⚠️ [Issue Title] — WARNING
[same structure]
 
---
 
## ⬆️ Upgrade Opportunities
1. [Specific upgrade with migration path]
2. ...
 
## ✅ What's done well
[Genuine positives found — don't skip this section]
 
## 📌 Priority Action Plan
1. **Immediate** (do now): [highest-impact fix]
2. **Short-term** (this week): [structural improvements]
3. **Medium-term** (this month): [tooling and architecture upgrades]
```
 
---
 
## Important Notes
 
- This skill audits **structure, architecture, and code quality only** — for security vulnerabilities, use `security-auditor`.
- Always show **real file paths and real code excerpts** — never generic placeholders.
- Always include the **"What's done well"** section — feedback should be balanced.
- Severity: ❌ Fail = violates convention or best practice | ⚠️ Warning = suboptimal but functional | ✅ Pass = correct.
- If the project is small (< 10 files), skip Module 5 architecture compliance and note it's too early to enforce layering.
- SQL audits are often paired with a backend — cross-reference table names against the ORM models if both are present.
 