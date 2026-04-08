---
name: security-auditor
description: "Audits project code for security vulnerabilities — API key leaks, SQL injection, authentication flaws, misconfigured CORS, exposed secrets, unprotected endpoints, insecure Docker configs, and more. Use this skill ALWAYS when the user asks to 'audit security', 'check for vulnerabilities', 'review the code for flaws', 'security review', 'check if the project is secure', 'check secrets', 'verify the .env', 'is my code safe?', or any variation. Also triggers when the user mentions 'leak', 'exposed', 'breach', 'flaw', 'CVE', 'data leak', or asks to 'review before deploy'. Supports Python/FastAPI, Java/Spring Boot, Node.js/Next.js, and generic projects."
---

# Security Auditor

A vulnerability auditor for software projects. Analyzes code for critical flaws, bad practices, and sensitive data exposure across multiple stacks.

---

## Execution Flow

1. **Scope declaration** — Ask: *"Is this a local dev audit or a pre-deploy review?"* Severity thresholds differ.
2. **Detect stack** — Identify languages, frameworks, and infra tools in use.
3. **Run scans by module** — Follow the 9 modules below, skipping modules irrelevant to the detected stack.
4. **Classify findings** by severity: Critical / High / Medium / Low.
5. **Generate report** with real code excerpts, impact description, and suggested fixes.

---

## Stack Detection

```bash
# Detect language and framework
ls *.py pyproject.toml requirements.txt setup.py 2>/dev/null && echo "PYTHON DETECTED"
ls pom.xml build.gradle *.java 2>/dev/null && echo "JAVA DETECTED"
ls package.json tsconfig.json 2>/dev/null && echo "NODE/TS DETECTED"
ls Dockerfile docker-compose.yml 2>/dev/null && echo "DOCKER DETECTED"
ls .github/workflows/*.yml 2>/dev/null && echo "CI/CD DETECTED"

# Identify framework
grep -r "fastapi\|flask\|django" requirements.txt pyproject.toml 2>/dev/null | head -5
grep -r "spring-boot\|spring-security" pom.xml build.gradle 2>/dev/null | head -5
grep -r "next\|express\|nestjs" package.json 2>/dev/null | head -5
```

Run only the modules relevant to the detected stack. Always run Modules 1, 7, 8, and 9 regardless of stack.

---

## Module 1 — Secrets & API Keys

### What to check

```bash
# Generic secret patterns — runs on all stacks
grep -rEn "(sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|xoxb-[0-9A-Z]{10,}|SG\.[a-zA-Z0-9]{22,})" \
  --include="*.py" --include="*.java" --include="*.ts" --include="*.js" --include="*.tsx" --include="*.env" --include="*.yml" --include="*.yaml" \
  . --exclude-dir=node_modules --exclude-dir=.git

# Hardcoded assignment patterns
grep -rEn "(api_key|apikey|api-key|secret|password|token|passwd|pwd)\s*=\s*['\"][^'\"]{6,}" \
  --include="*.py" --include="*.java" --include="*.ts" --include="*.js" \
  . --exclude-dir=node_modules --exclude-dir=__pycache__ | grep -v ".env" | grep -v "test\|spec\|mock\|example"

# JWT hardcoded
grep -rEn "eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}" \
  --include="*.py" --include="*.java" --include="*.ts" --include="*.js" \
  . --exclude-dir=node_modules

# Check .gitignore covers .env
cat .gitignore 2>/dev/null | grep -i "\.env" || echo "WARNING: .env not in .gitignore"

# Find real .env files (not examples)
find . -name ".env" -o -name ".env.production" -o -name ".env.local" 2>/dev/null \
  | grep -v node_modules | grep -v ".example"
```

### High-risk patterns
| Pattern | Type |
|---------|------|
| `sk-proj-` / `sk-` | OpenAI key |
| `AKIA` | AWS Access Key |
| `ghp_` | GitHub PAT |
| `eyJ` in string literals | Hardcoded JWT / Supabase key |
| `xoxb-` / `xoxp-` | Slack token |
| `SG.` | SendGrid key |
| `AC` + 32 chars | Twilio SID |
| `_SECRET`, `_KEY`, `_PASSWORD` assigned a literal | Generic credential |

### Python-specific
```bash
# Check if secrets are loaded via os.environ or python-decouple (good) vs hardcoded (bad)
grep -rn "os.environ\|config(\|decouple\|dotenv" --include="*.py" . | head -10
grep -rn "SECRET_KEY\s*=\s*['\"]" --include="*.py" . | grep -v "os.environ\|config(\|getenv"

# Django: DEBUG=True in production settings
grep -rn "DEBUG\s*=\s*True" --include="*.py" . | grep -v "test\|local\|dev"
```

### Java/Spring-specific
```bash
# Check application.properties / application.yml for plaintext secrets
find . -name "application.properties" -o -name "application.yml" -o -name "application-prod.yml" 2>/dev/null \
  | xargs grep -En "(password|secret|key|token)\s*[=:]\s*.{6,}" 2>/dev/null | grep -v "\${" | grep -v "#"
```

---

## Module 2 — SQL Injection

### What to check

```bash
# Python: string concatenation in queries
grep -rEn "execute\(['\"].*\+|execute\(['\"].*%s.*%\s*\(" --include="*.py" . --exclude-dir=__pycache__
grep -rn "f\"SELECT\|f'SELECT\|f\"INSERT\|f\"UPDATE\|f\"DELETE" --include="*.py" . --exclude-dir=__pycache__

# Java: raw string concatenation in queries
grep -rEn "createQuery\(.*\+|createNativeQuery\(.*\+|executeQuery\(.*\+" --include="*.java" . 
grep -rn "\"SELECT.*\"\s*\+\s*" --include="*.java" .

# Node/TS: template literals in queries
grep -rn "\${" --include="*.ts" --include="*.js" . --exclude-dir=node_modules \
  | grep -i "sql\|query\|select\|insert\|update\|delete"

# Supabase: service_role in client-side code
grep -rn "service_role" --include="*.ts" --include="*.tsx" . --exclude-dir=node_modules \
  | grep -v "server\|api\|route"
```

### What to flag
- String concatenation or f-strings building SQL with user input
- Missing parameterized queries / prepared statements
- Java: raw JDBC without `PreparedStatement`
- ORM raw query calls with interpolated variables (`session.execute(f"SELECT...")`)
- Tables without Row Level Security (Supabase projects)

---

## Module 3 — Authentication & Unprotected Endpoints

### Python / FastAPI

```bash
# List all route definitions
grep -rn "@app\.\|@router\." --include="*.py" . --exclude-dir=__pycache__ | grep -E "get|post|put|delete|patch"

# Routes missing Depends(get_current_user) or any auth dependency
grep -rn "@app\.\|@router\." --include="*.py" . | grep -v "Depends\|Security\|OAuth2\|HTTPBearer" \
  | grep -Ev "health|ping|docs|redoc|openapi|login|register"

# JWT: decode vs verify
grep -rn "jwt.decode\|jwt.encode" --include="*.py" . --exclude-dir=__pycache__
# Flag: jwt.decode without 'algorithms' parameter or with verify=False
grep -rn "verify=False\|options.*verify" --include="*.py" . --exclude-dir=__pycache__

# Passwords stored or compared in plaintext
grep -rn "password\s*==\|== password\|password.*=.*request\." --include="*.py" . \
  | grep -v "hash\|bcrypt\|argon\|passlib\|werkzeug"
```

### Java / Spring Boot

```bash
# Check if Spring Security is configured
find . -name "SecurityConfig.java" -o -name "WebSecurityConfig.java" 2>/dev/null
grep -rn "@EnableWebSecurity\|SecurityFilterChain\|HttpSecurity" --include="*.java" .

# Endpoints bypassing security (permitAll on non-public routes)
grep -rn "permitAll()" --include="*.java" . | grep -v "login\|register\|health\|swagger\|public"

# Missing @PreAuthorize on sensitive endpoints
grep -rn "@DeleteMapping\|@PutMapping\|@PostMapping" --include="*.java" . -l \
  | xargs grep -L "@PreAuthorize\|@Secured\|@RolesAllowed" 2>/dev/null

# Plaintext password comparison
grep -rn "password.equals\|equals(password" --include="*.java" . \
  | grep -v "BCrypt\|PasswordEncoder\|encode"
```

### Node / TypeScript

```bash
# List API endpoints
find . -path "*/api/**/*.ts" -o -path "*/app/api/**/*.ts" -o -path "*/pages/api/**/*.ts" 2>/dev/null | head -50

# Routes without auth middleware
grep -rn "export default\|export async function" --include="*.ts" -l . \
  | xargs grep -L "auth\|session\|token\|requireAuth\|getUser\|verify" 2>/dev/null | grep "api/"

# jwt.decode vs jwt.verify
grep -rn "jwt.decode\b" --include="*.ts" --include="*.js" . --exclude-dir=node_modules
```

---

## Module 4 — CORS, Headers & Configuration

### What to check

```bash
# Python/FastAPI CORS
grep -rn "CORSMiddleware\|add_middleware.*CORS" --include="*.py" . --exclude-dir=__pycache__
grep -rn "allow_origins\s*=\s*\[.*\*\|allow_origins\s*=\s*\['\"\*" --include="*.py" .

# Python/Flask CORS
grep -rn "CORS(" --include="*.py" . | grep -v "#"

# Java: CORS config
grep -rn "@CrossOrigin\|CorsConfiguration\|addCorsMappings" --include="*.java" .
grep -rn "@CrossOrigin" --include="*.java" . | grep -v "origins\s*=\s*{" # no origins specified = all allowed

# Node/Express: CORS config
grep -rn "cors\|CORS\|Access-Control" --include="*.ts" --include="*.js" . --exclude-dir=node_modules
grep -rn "origin.*\*\|cors()" --include="*.ts" --include="*.js" . --exclude-dir=node_modules

# Security headers (Node)
grep -rn "helmet" --include="*.ts" --include="*.js" . --exclude-dir=node_modules

# Next.js config headers
cat next.config.js 2>/dev/null || cat next.config.ts 2>/dev/null || cat next.config.mjs 2>/dev/null
```

### Red flags
| Finding | Risk |
|---------|------|
| `allow_origins=["*"]` in FastAPI | Any site can call your API |
| `@CrossOrigin` with no args | CORS open for all origins |
| `cors()` with no params (Express) | Same as above |
| No `helmet` (Node) | Missing 14 security headers |
| `X-Frame-Options` absent | Clickjacking risk |
| `Content-Security-Policy` absent | XSS escalation risk |

---

## Module 5 — Input Validation & Injection (NEW)

This module covers attack vectors beyond SQL injection.

### Command Injection

```bash
# Python: shell=True with user input, or direct os.system/subprocess with variables
grep -rn "os.system\|subprocess.run\|subprocess.call\|subprocess.Popen\|os.popen" --include="*.py" . \
  | grep -v "#" | grep "shell=True\|request\.\|user\|input"

# Java: Runtime.exec with user input
grep -rn "Runtime.getRuntime().exec\|ProcessBuilder" --include="*.java" . \
  | grep -v "#\|//"
```

### Path Traversal

```bash
# Python: open() or file operations with user-supplied paths
grep -rn "open(\|Path(\|os.path.join(" --include="*.py" . \
  | grep "request\.\|param\|query\|body\|user_input\|filename" | grep -v "#"

# Java: new File() with user input
grep -rn "new File(\|Paths.get(\|Files.read" --include="*.java" . \
  | grep -v "//" | grep "request\.\|param\.\|getParameter"
```

### SSRF (Server-Side Request Forgery)

```bash
# Python: requests.get/post with user-controlled URL
grep -rn "requests.get(\|requests.post(\|httpx.get(\|httpx.post(" --include="*.py" . \
  | grep "request\.\|param\|query\|body\|url\|endpoint" | grep -v "#\|test"

# Java: HttpClient or RestTemplate with user-controlled URL
grep -rn "restTemplate.getForObject\|restTemplate.exchange\|HttpClient" --include="*.java" . \
  | grep -v "//"
```

### Deserialization

```bash
# Python: pickle with external input (critical)
grep -rn "pickle.loads\|pickle.load\|yaml.load(" --include="*.py" . | grep -v "#"
# yaml.load is safe only with yaml.safe_load — flag yaml.load without Loader=yaml.SafeLoader

# Java: ObjectInputStream (classic Java deserialization)
grep -rn "ObjectInputStream\|readObject()" --include="*.java" . | grep -v "//"
```

### Mass Assignment

```bash
# Python/FastAPI: Pydantic model passed directly without field filtering
grep -rn "\.dict()\|\.model_dump()" --include="*.py" . | grep -v "#"
# Flag when model dump is passed directly to DB insert without allowlist

# Java/Spring: @RequestBody binding to entity (not DTO)
grep -rn "@RequestBody.*Entity\|@RequestBody.*Model" --include="*.java" .
```

---

## Module 6 — Frontend Data Exposure

```bash
# Next.js: NEXT_PUBLIC_ vars that should be private
grep -rn "NEXT_PUBLIC_" --include="*.ts" --include="*.tsx" --include="*.env*" . --exclude-dir=node_modules \
  | grep -i "secret\|service_role\|private\|admin\|password\|database_url"

# Sensitive data in console.log
grep -rn "console.log\|print(" --include="*.ts" --include="*.tsx" --include="*.py" . \
  | grep -i "password\|token\|secret\|cpf\|credit\|card\|ssn"

# SELECT * returning more than needed
grep -rn "select.*\*\|\.select('\*')\|SELECT \*" --include="*.ts" --include="*.py" --include="*.java" . \
  | grep -v "//\|#\|test\|spec"

# Python: returning full SQLAlchemy model (may include password hash)
grep -rn "return.*db_user\|return.*user\b" --include="*.py" . \
  | grep -v "\.dict()\|model_dump\|#"
```

---

## Module 7 — Dependency Vulnerabilities

```bash
# Node.js
npm audit 2>/dev/null || yarn audit 2>/dev/null
npm outdated 2>/dev/null | head -30
ls -la package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null

# Python
pip-audit 2>/dev/null || safety check 2>/dev/null
pip list --outdated 2>/dev/null | head -20
ls requirements.txt requirements-lock.txt Pipfile.lock poetry.lock 2>/dev/null

# Java
# Check for known vulnerable versions in pom.xml (manual scan)
grep -n "log4j\|spring-core\|jackson-databind" pom.xml 2>/dev/null
cat pom.xml 2>/dev/null | grep -A2 "<dependency>" | grep "<version>" | head -30
```

### Interpreting results
- **Critical/High** → patch immediately before deploy
- **Moderate** → evaluate if a known exploit exists
- No lockfile → unpredictable builds → supply chain risk

---

## Module 8 — Docker & Infrastructure (NEW)

```bash
# Check if container runs as root
grep -n "USER" Dockerfile 2>/dev/null || echo "WARNING: No USER directive — container runs as root"

# Secrets baked into image via ENV
grep -rn "^ENV.*SECRET\|^ENV.*KEY\|^ENV.*PASSWORD\|^ENV.*TOKEN" Dockerfile 2>/dev/null

# COPY . . without .dockerignore — may include .env
cat .dockerignore 2>/dev/null | grep ".env" || echo "WARNING: .env not in .dockerignore"
ls .dockerignore 2>/dev/null || echo "WARNING: No .dockerignore found"

# Exposed sensitive ports
grep -n "EXPOSE" Dockerfile 2>/dev/null | grep -E "5432|3306|6379|27017|9200"
# PostgreSQL, MySQL, Redis, MongoDB, Elasticsearch should not be exposed publicly

# docker-compose: hardcoded secrets
grep -rn "password:\|POSTGRES_PASSWORD:\|MYSQL_ROOT_PASSWORD:" docker-compose.yml 2>/dev/null \
  | grep -v "\${" | grep -v "#"

# docker-compose: ports binding to 0.0.0.0 (public)
grep -n "ports:" docker-compose.yml 2>/dev/null
grep -A10 "ports:" docker-compose.yml 2>/dev/null | grep -v "127.0.0.1"

# Image using latest tag (no pinned version)
grep -n "FROM.*:latest\|FROM.*[^:]$" Dockerfile 2>/dev/null
```

### Red flags
| Finding | Risk |
|---------|------|
| No `USER` directive | Container runs as root |
| `ENV SECRET_KEY=abc123` in Dockerfile | Secret baked into image layer |
| No `.dockerignore` | `.env` may be copied into image |
| `EXPOSE 5432` without firewall | DB port publicly accessible |
| `POSTGRES_PASSWORD: mypass` (not `${VAR}`) | Hardcoded DB creds in compose |
| `FROM python:latest` | Unpinned version, unpredictable security |

---

## Module 9 — GitHub & CI/CD

```bash
# Check .gitignore covers sensitive files
cat .gitignore 2>/dev/null | grep -E "\.env|\.pem|\.key|\.p12|secrets"

# Find sensitive files that should never be committed
find . -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "*.pfx" 2>/dev/null \
  | grep -v node_modules | grep -v ".git"
find . -name ".env" -o -name ".env.production" -o -name ".env.local" 2>/dev/null \
  | grep -v node_modules | grep -v ".example"

# GitHub Actions: secrets used correctly
find . -path "./.github/workflows/*.yml" 2>/dev/null \
  | xargs grep -l "secrets\." 2>/dev/null

# GitHub Actions: hardcoded values (not using ${{ secrets.X }})
cat .github/workflows/*.yml 2>/dev/null \
  | grep -v "\${{ secrets\." | grep -iE "(key|token|password|secret)\s*[:=]\s*\S+" | grep "="

# GitHub Actions: dangerous permissions
grep -rn "permissions:\|write-all\|contents: write" .github/workflows/ 2>/dev/null
```

---

## Rate Limiting & DoS (Bonus Check)

```bash
# FastAPI: slowapi or similar rate limiter
grep -rn "slowapi\|RateLimiter\|limiter\|rate_limit" --include="*.py" . --exclude-dir=__pycache__
# If not found, flag that endpoints have no rate limiting

# Spring Boot: rate limiter (Bucket4j, Resilience4j)
grep -rn "Bucket4j\|RateLimiter\|@RateLimiter\|resilience4j" --include="*.java" --include="*.xml" .

# Express/Node: express-rate-limit
grep -rn "rate-limit\|rateLimit\|express-slow-down" --include="*.ts" --include="*.js" . --exclude-dir=node_modules
```

---

## Final Report Format

After running all relevant modules, generate a report in this format:

```markdown
# 🔐 Security Report — [Project Name]
Date: [current date]
Stack: [detected stack]
Audit scope: [Local Dev / Pre-Deploy]

## Executive Summary
[2-3 sentences on overall security posture and critical findings]

## Findings by Severity

### 🔴 CRITICAL
| # | File | Line | Issue | Impact |
|---|------|------|-------|--------|
| 1 | src/config.py | 12 | Hardcoded API key | Full API access by anyone with repo access |

**Vulnerable code:**
```[lang]
[real code excerpt]
```

**Fix:**
```[lang]
[corrected code]
```

---

### 🟠 HIGH
[same structure]

### 🟡 MEDIUM
[same structure]

### 🟢 LOW / IMPROVEMENTS
[same structure]

---

## Fix Checklist
- [ ] [critical item 1]
- [ ] [critical item 2]
...

## Recommended Next Steps
1. [Immediate action — do before any deploy]
2. [Short-term action — do this week]
3. [Medium-term improvement]
```

---

## Important Notes

- Always show the **real code excerpt** with the problem — never just describe it.
- Never print the actual value of found secrets — mask as `sk-****` or `[REDACTED]`.
- Test/mock files may have fake data — do not classify as Critical without confirming it's used in production.
- Prioritize: one exposed production secret > 100 low-severity dependency warnings.
- If the project uses Supabase, prompt the user to verify RLS in the dashboard — it cannot be checked via grep alone.
- `pip-audit` and `safety` may need to be installed: `pip install pip-audit safety --break-system-packages`.