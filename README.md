# Provenance: Trust-First Enterprise Knowledge Assistant for Pharma

> *“Search tells you where. Provenance tells you whether to trust it.”*

Provenance is an enterprise knowledge assistant built for pharmaceutical environments (Novacure Labs). In pharma compliance, acting on an outdated SOP or conflicting communication is a critical audit finding. Provenance ingests across SharePoint (.docx), SOPs (.pdf), general PDFs, emails (.eml), and Teams conversations (.json), delivers answers with verifiable citations down to the exact passage, detects conflicting or superseded sources, strictly enforces role-based access control (Intern, Analyst, Manager), and refuses to hallucinate when evidence is weak.

---

## 🚀 Quickstart & Setup

### 1. Backend Setup (Python 3.11+)

```bash
# 1. Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Open .env and configure:
# USE_MOCK_LLM=1 (for free offline extractive mode) or USE_MOCK_LLM=0 (with GROQ_API_KEY)
# GROQ_API_KEY=gsk_...
# GROQ_MODEL_MAIN=llama-3.3-70b-versatile
# GROQ_MODEL_FAST=llama-3.1-8b-instant

# 4. Generate & validate corpus (already validated)
python -m corpus_gen.validate
python -c "from modules.ingestion import build_corpus; build_corpus()"

# 5. Warm cache & verify golden questions
python warm_cache.py
```

### 2. Frontend Setup (Node.js 20+)

```bash
cd frontend
npm install
npm run build   # Validate production build
npm run dev     # Starts Vite dev server on http://localhost:5173
```

### 3. Running Both (Single Command)

```bash
# On Linux/macOS or Git Bash:
chmod +x run.sh
./run.sh

# Or run separately in two terminals:
# Terminal 1:
uvicorn app.main:app --port 8000
# Terminal 2:
cd frontend && npm run dev
```

Visit the application at **`http://localhost:5173`** with the backend at **`http://localhost:8000`**.

---

## 🧪 Verification & Selftests

Run any module's self-contained test without network or API keys:

```bash
python -m modules.ingestion.selftest     # Ingestion & Connectors
python -m modules.retrieval.selftest     # BM25 & Retrieval Filtering
python -m modules.intelligence.selftest  # Conflict & Gap Detection
python tests/smoke.py                   # Full End-to-End API Smoke Test
python warm_cache.py                    # 12 Golden Question Benchmark (3 Roles)
```

---

## 📑 Slide Outline: Objectives, Outcomes & Architecture

### F1–F10 Feature Matrix

| ID | Feature | Priority | Brief Item & Outcome | Description |
|:---|:---|:---:|:---|:---|
| **F1** | Unified Natural-Language Q&A | MUST | Obj 1, 2, 5 · Outcome 1 | One search interface querying SharePoint, SOP, PDF, email, and Teams simultaneously. |
| **F2** | Grounded Passage Citations | MUST | Obj 3 · Outcome 2 | Direct click-through citation side panel showing doc ID, version, date, status, location, and verbatim text. |
| **F3** | Confidence & Refusal Card | MUST | Trust · Obj 3 | Confidence grading (High/Med/Low) and calm "I don't know" cards when evidence is insufficient. |
| **F4** | Role-Based Access Control | MUST | Enterprise Security | Pre-ranking role filtering ensuring Interns never see or leak restricted records (AUD-001, EML-004). |
| **F5** | Conflict & Staleness Detection | MUST | The Wow Factor | Detects contradictions (2–8 °C vs 2–6 °C) and superseded documents (SOP-014-v2 vs v3) side-by-side. |
| **F6** | Pharma Glossary Expansion | MUST | Obj 5 | Automatic expansion of acronyms (CAPA, OOS, GMP) during query ingestion. |
| **F7** | Knowledge Gap Dashboard | MUST | Outcome 5 | Tracks unanswered queries to highlight missing organizational documentation. |
| **F8** | Minutes-Saved Estimate | MUST | Obj 4 | Algorithmic calculation estimating operational time saved per query and organization-wide. |
| **F9** | Role-Based Onboarding Path | SHOULD | Outcome 4 | Curated 5-day reading curriculum tailored for QA, Production, and Regulatory roles. |
| **F10** | Subject Matter Expert Finder | SHOULD | Outcome 3 | Surfaces top experts based on approved document authorship and verifiable evidence. |

---

## 🎬 3-Minute Demo Walkthrough

1. **Analyst (New QA Hire)**: Open **Onboarding and Experts** tab to inspect the 5-day QA reading curriculum.
2. **Analyst (Cold Chain Excursion)**: Ask *"What temperature should vaccine batches be stored at?"* Show the cited answer, the prominent **Conflict Banner** highlighting 2 to 8 °C (SOP-014-v3) vs 2 to 6 °C (Teams #cold-chain), and the superseded SOP-014-v2 flag.
3. **Analyst (Compliance Investigation)**: Ask *"What is the CAPA timeline for an OOS result?"* Show expanded terms (`CAPA`, `OOS`) and SOP-021 citation.
4. **Intern (Security Boundary)**: Switch role to **Intern**, ask *"What recurring deviation did the audit find?"* Show clean refusal card with zero citations and zero leak of AUD-001.
5. **Analyst (Knowledge Gaps)**: Switch back to **Analyst**, ask *"How do I calibrate an HPLC column?"* Observe the system say *"I don't know"*, then open the **Intelligence Dashboard** to see HPLC in the knowledge gap table.
6. **Analyst (Collaboration)**: Open **Experts**, search *"deviation"*, confirm Priya Rao (QA Lead) is ranked #1 with 8 document citations, ending on the total minutes-saved counter.

---

## 🗺️ Product Roadmap

- **Verified Human Answers**: Enable QA leads to pin verified canonical answers to common compliance questions.
- **Audit-Ready Evidence Reports**: One-click PDF export compiling full chain of custody and cited documents for regulatory auditors (FDA / EMA).
- **Ask-the-Owner Messaging**: Direct Teams/Slack message dispatch to verified document authors when questions go unanswered.
- **Weekly "What Changed" Digest**: Automated diff notifications when newer SOP versions supersede older processes.
- **Hybrid Search & Real SSO**: Embeddings-based dense search and native Microsoft Graph connectors with enterprise Azure AD / Okta SSO group claims synchronization.

---

## 🔒 Enterprise Security Disclosure

*In this demonstration application, security clearance (Intern, Analyst, Manager) is toggled in the header for interactive testing. In enterprise production, role permissions are securely synchronized from enterprise SSO group claims (e.g., Azure AD SAML/OIDC tokens).*