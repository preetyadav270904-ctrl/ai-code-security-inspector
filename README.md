# 🛡️ AI Code Inspector

> An AI-powered DevSecOps scanner that reviews your code for security vulnerabilities, points to the exact line, and suggests a fix, right from your browser, terminal, or GitHub Actions pipeline.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-e92063)
![Groq](https://img.shields.io/badge/LLM-Groq-f55036)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)

---

## 📖 Table of Contents

- [Why I Built This](#-why-i-built-this)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [CI/CD Integration](#-cicd-integration)
- [Design Decisions](#-design-decisions)
- [Limitations](#-limitations)
- [Future Improvements](#-future-improvements)
- [What I Learned](#-what-i-learned)

---

## 💡 Why I Built This

Code security reviews usually fall into two camps, and both have problems:

| Approach | Good | Not so good |
|---|---|---|
| **Traditional static analyzers** (SonarQube, Bandit, Flake8) | Fast | Rule-based, so they throw many false positives and never explain *how to fix* the issue |
| **Manual peer reviews** | Thorough | Slow, and security reviewers become a bottleneck |

I wanted something in between: a tool that is **fast like a linter** but **understands context like a reviewer**. So this project combines Python's AST parsing with low-latency LLM inference (via [Groq](https://groq.com/)) and plugs it into the places developers already work: the browser, the terminal, and pull requests.

---

## ✨ Features

- 🔍 **CWE / OWASP-based detection** with exact line numbers
- 🛠️ **Automated fix suggestions** shown as ready-to-use code snippets
- ✅ **Schema-enforced JSON output** validated with Pydantic, so malformed model output is caught instead of trusted
- 🖥️ **Three ways to run it:** web dashboard, CLI, and GitHub Actions
- 🚦 **Build gating:** the CLI exits with code `1` when High/Critical issues are found
- 📦 **Lightweight frontend:** one HTML file, no Node.js, npm, or build step

---

## ⚙️ How It Works

```
[ Developer Input ]
  ├─ Browser Web UI      (templates/index.html)
  ├─ Terminal CLI        (inspector/cli.py)
  └─ GitHub Actions      (.github/workflows/ai-security-check.yml)
           │
           ▼
[ FastAPI App ]  inspector/api.py
  ├─ Endpoints: POST /scan, POST /scan/file
  └─ Request/response validation (inspector/models.py, Pydantic v2)
           │
           ▼
[ Core Analysis Pipeline ]  inspector/core.py
  ├─ 1. AST syntax pre-check (ast.parse)
  ├─ 2. Line indexing (adds explicit line numbers)
  └─ 3. Prompt assembly
           │
           ▼
[ Groq LLM ]  openai/gpt-oss-20b  (JSON mode)
           │
           ▼
[ Evaluation & Enforcement ]
  ├─ Pydantic parses output into Finding / ScanReport
  ├─ Computed fields: critical_count, high_count, passed
  └─ Exit code: 0 = clean, 1 = fail the build
```

### Step by step

1. **AST pre-check:** the file is first run through Python's `ast.parse`. If it has syntax errors, the scan is flagged (`valid_ast = False`) so the analyzer knows the context.
2. **Line indexing:** LLMs are bad at counting lines, so `prepare_source()` rewrites the code with line numbers baked in:
   ```
   1 | import os
   2 | import sqlite3
   3 | def unsafe_login(db_path, user, password):
   ```
   This way the model reads the line numbers instead of guessing them.
3. **LLM analysis:** the indexed code is sent to Groq with a structured prompt, requesting JSON output.
4. **Validation:** the response is parsed into typed Pydantic models. Invalid output fails validation instead of silently passing through.
5. **Verdict in plain Python:** issue counts and the pass/fail decision are computed in code, not by the LLM.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Backend | FastAPI |
| Data validation | Pydantic v2 |
| LLM inference | Groq (`openai/gpt-oss-20b`) |
| Frontend | Vanilla HTML / CSS / JavaScript |
| CI/CD | GitHub Actions |

---

## 📁 Project Structure

```
.
├── inspector/
│   ├── api.py          # FastAPI app and routes
│   ├── core.py         # AST check, line indexing, prompt + LLM call
│   ├── models.py       # Pydantic models, enums, computed fields
│   └── cli.py          # Command-line runner
├── templates/
│   └── index.html      # Web dashboard
├── fixtures/
│   └── dummy_targets.py  # Intentionally vulnerable sample code
├── .github/workflows/
│   └── ai-security-check.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A free [Groq API key](https://console.groq.com/)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Groq API key
export GROQ_API_KEY="your_api_key_here"   # On Windows (PowerShell): $env:GROQ_API_KEY="your_api_key_here"
```

---

## 🧪 Usage

### 1. Web Dashboard

```bash
uvicorn inspector.api:app --reload
```

Open **http://127.0.0.1:8000** in your browser, paste or upload a file, and click **Scan Code**.

The dashboard shows:
- Metric tiles for Critical, High, Total Issues, and Lines Analyzed
- Color-coded severity cards (🔴 Critical, 🟠 High/Medium)
- The CWE/OWASP category, a plain-English explanation, and a suggested fix for each finding

### 2. Command Line

```bash
python -m inspector.cli path/to/your_file.py
```

The CLI prints a summary table of findings and sets the exit code:

| Exit code | Meaning |
|---|---|
| `0` | No High/Critical issues, code passes |
| `1` | High or Critical issues found, code fails |

### 3. REST API

```bash
curl -X POST http://127.0.0.1:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"source": "import os\nos.system(input())", "file_name": "test.py"}'
```

Interactive API docs are auto-generated at **http://127.0.0.1:8000/docs**.

---

## 🔄 CI/CD Integration

The workflow in `.github/workflows/ai-security-check.yml` runs on every pull request to `main` (and can be triggered manually).

**What it does:**

1. Spins up an Ubuntu runner and checks out the repo
2. Sets up Python 3.11 and installs dependencies
3. Injects `GROQ_API_KEY` from **GitHub repository secrets**
4. Runs the scanner against the target files:
   ```bash
   python -m inspector.cli fixtures/dummy_targets.py || true
   ```
5. Prints the findings table and fix suggestions in the Actions log

**Setup:** go to *Repo → Settings → Secrets and variables → Actions* and add a secret named `GROQ_API_KEY`.

> 💡 The `|| true` keeps the pipeline green so the demo output is always visible. To make the scan **block merges** on serious issues, remove `|| true` and the non-zero exit code will fail the job.

---

## 🧠 Design Decisions

- **Line indexing before the LLM call:** models miscount lines, so the code is numbered up front.
- **Counting done in Python:** issue totals and the pass/fail flag use Pydantic `@computed_field` properties, because LLMs often miscount too.
- **Strict schema validation:** typed enums for severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`) and category (`SECURITY_VULNERABILITY`, `BUG`, `CODE_SMELL`) keep output consistent.
- **Zero-dependency frontend:** served straight from FastAPI, so there is nothing to build or install for the UI.

---

## ⚠️ Limitations

Being upfront about what this project is (and isn't):

- It is an **assistant, not a replacement** for a full security audit. LLMs can still miss issues or flag false positives, so review findings before acting on them.
- Currently focused on **Python** source files (the AST pre-check uses Python's `ast` module).
- Scans one file at a time and doesn't yet understand cross-file data flow.
- Code is sent to an external API (Groq), so avoid scanning proprietary or sensitive code without checking your organization's policy.

---

## 🤝 Contributing

Suggestions and pull requests are welcome. Feel free to open an issue if you spot a bug or have an idea.

---

⭐ If you found this project useful or interesting, consider giving it a star!