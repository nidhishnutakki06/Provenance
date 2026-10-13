Provenance: Master Specification (3 Hours, Free Stack, 5 People)
Oct 13, 2026 · Save this document as PLAN.md in the repo root.
Provenance is a trust-first enterprise knowledge assistant for pharma. It answers from SharePoint, SOP, email, Teams and PDF sources with exact citations, flags conflicting or outdated documents, respects user roles, and says “I don’t know” when evidence is weak. Four backend developers build in parallel with no dependency on each other, then the frontend is built last. Everything is free and runs on localhost: Groq is the LLM and Antigravity writes the code.
How to read this document: §1 and §2 say what and who. §3 is the API and LLM handling rules. §4 to §6 are the repo layout, contracts and corpus. §7 and §8 are the schedule and setup. §9 and §10 are the agent rules and the prompts you paste. §11 and §12 are the demo and the done checks. Appendix A holds the starter-pack files.
1. What we are building
Problem (from the brief): Critical knowledge is spread across SharePoint, Teams, emails, PDFs and SOPs. Employees spend considerable time searching instead of doing productive work.
Our angle: Every team will build “chat with documents.” We build trust. In pharma, acting on an outdated or conflicting SOP is a compliance failure. Our answers show proof, flag disagreement, hide what a role may not see, and refuse to guess.
Pitch line: Search tells you where. Provenance tells you whether to trust it.
Honest scope: Connectors read local folders that mimic SharePoint, Teams, email and SOP exports. Swapping in Microsoft Graph means replacing one file per connector. This avoids tenant and OAuth risk in a 3-hour window. Role is chosen in the UI for the demo; in production it would come from SSO group membership.
1.1 Features, owners and priority
#
Feature
Priority
Backend owner
Maps to
F1
Natural-language Q&A over 5 source types (SharePoint, SOP, PDF, email, Teams)
MUST
Dev 3 (data from Dev 2)
Objectives 1, 2, 5
F2
Citations with highlighted passage, version, date, status
MUST
Dev 3
Objective 3
F3
Confidence level and “I don’t know” with what is missing
MUST
Dev 3
Trust
F4
Role-based access (Intern, Analyst, Manager)
MUST
Dev 2 tags, Dev 3 filters, Dev 4 re-checks
Enterprise readiness
F5
Conflict and staleness detector
MUST
Dev 4
The demo’s wow moment
F6
Glossary query expansion (CAPA, OOS, GMP...)
MUST
Dev 3
Objective 5
F7
Knowledge gap dashboard
MUST
Dev 4
Outcome 5
F8
Minutes-saved estimate (one formula)
MUST
Dev 4
Objective 4
F9
Onboarding reading path
SHOULD
Dev 2
Outcome 4
F10
Expert finder
SHOULD
Dev 2
Outcome 3

Cut order if time slips: F10, then F9, then F8. Never cut F1 to F5.
1.2 Brief objectives and outcomes mapped to features
Brief item
How we meet it
Objective 1: single AI search interface
One chat tab over all sources (F1)
Objective 2: connect multiple repositories
Four connectors covering five source types
Objective 3: contextual responses with citations
F2, F3, F5
Objective 4: reduce search effort
One question instead of five searches, plus the minutes-saved estimate (F8)
Objective 5: natural-language interaction
F1 and glossary expansion (F6)
Outcome 1: single source of enterprise knowledge
One unified index across all sources
Outcome 2: faster retrieval
Cited answer in a few seconds, cached repeats in milliseconds
Outcome 3: increased collaboration
Expert finder (F10)
Outcome 4: improved onboarding
Role-based reading path (F9)
Outcome 5: better knowledge utilization
Gap dashboard shows documents that should exist (F7)

Roadmap (pitch slide only, not built): verified answers, audit-ready evidence report, ask-the-owner message, weekly what-changed digest, a notice that a newer restricted source may exist, embeddings for hybrid search, and Microsoft Graph connectors with real permission sync.
2. Team, ownership and the zero-dependency rules
Person
Owns (only edits these paths)
Works against (never waits on anyone)
Dev 1: Corpus
corpus_gen/, data/raw/
The document table in §6 and the raw corpus contract in §5.4
Dev 2: Ingestion
modules/ingestion/, data/fixtures/raw_sample/
The raw corpus contract and its own sample files
Dev 3: LLM and retrieval
app/llm.py, modules/retrieval/
data/fixtures/chunks_sample.json
Dev 4: Intelligence and API
modules/intelligence/, app/main.py, tests/, warm_cache.py
The stubs and chunks_sample.json
Dev 5: Lead and frontend
contracts.py, app/config.py, root files, frontend/, README.md
Starter pack first, merges at 1:15, frontend UI after integration

2.1 How nobody blocks anybody
Starter pack (Phase 0, 15 minutes, Appendix A). Dev 5 commits the frozen contracts.py, app/config.py, a complete requirements.txt, .env.example, stub versions of every public function, and fixture chunks. From minute 15 every endpoint already returns fake data.
Folder ownership. Each person edits only their own paths. Shared files are touched only by Dev 5, so Git merges never conflict.
Own fixtures. Dev 1 needs nothing. Dev 2 builds its own small sample raw files. Dev 3 and Dev 4 use chunks_sample.json.
Automatic switch to real data. app/config.py returns the real files when they exist and the fixtures when they do not. No code changes at integration.
Stable public surface. Cross-module calls use only the function names exported from each package’s __init__.py. Stubs exist for all of them, so an import never breaks.
LLM isolation. Only app/llm.py calls an LLM (Dev 1 has one tiny client for one-off generation). USE_MOCK_LLM=1 makes everything run with no network, so no one is ever blocked by a rate limit.
Module
Needs
Uses during Phase 1
Real input switches on
Dev 1 corpus
Nothing
Its own manifest and templates
Not applicable
Dev 2 ingestion
data/raw/
data/fixtures/raw_sample/
Automatically once data/raw/ has files
Dev 3 retrieval
chunks.json
data/fixtures/chunks_sample.json
Automatically once data/processed/chunks.json exists
Dev 4 intelligence and API
Chunks and other modules
chunks_sample.json and the stubs
Automatically when real modules replace stubs
Dev 5 frontend
Backend
The stub backend (shell only)
After integration

3. Free stack and API handling
3.1 Stack
Rule: nothing may cost money or need a credit card. The demo runs on localhost.
Need
Choice
Cost
LLM (primary)
Groq free plan, each dev makes a key at console.groq.com/keys
Free, no card
LLM (backup 1)
A second, smaller Groq model on the same key
Free (limits are per model)
LLM (backup 2, optional)
Google Gemini free tier via plain REST with requests
Free, tight limits
LLM (last resort)
Extractive answer built in code, no LLM
Free
Coding tool
Antigravity, signed in with a personal Gmail
Free preview with usage limits
Search
rank_bm25 keyword search, no embeddings
Free
Parsing and files
pypdf, python-docx, reportlab, stdlib email
Free
Storage
SQLite and JSON files
Free
Backend
Python 3.11+, FastAPI, Uvicorn, Pydantic v2
Free
Frontend
React, Vite, Tailwind 3, plain fetch, Node 20+
Free
Version control
Git and one private GitHub repo
Free

Do not sign up for: Microsoft Graph, SharePoint, Teams or Outlook APIs, any embedding API, any vector database, any hosting, OpenAI.
3.2 Rules for every LLM call (whole team)
Each dev creates their own Groq account and key for development. The demo laptop uses one key. Groq limits apply per organization and per model, so spreading dev work across accounts avoids collisions.
Free limits and model names change. After creating a key, open console.groq.com/settings/limits and console.groq.com/docs/models once, pick one large model and one small model, and put the names in .env. Never hardcode model names or keys.
Environment variables: GROQ_API_KEY, GROQ_MODEL_MAIN (large, for answers), GROQ_MODEL_FAST (small, also the fallback), GEMINI_API_KEY (optional), USE_MOCK_LLM (1 means never touch the network).
Only app/llm.py calls an LLM. The single exception is corpus_gen/client.py, used once to generate the corpus.
At most 2 LLM calls per question: one answer call, and one conflict-explanation call only when numbers differ.
No LLM calls during ingestion, indexing, search, gap reporting or anything at server startup. Retrieval must work with zero LLM requests.
Every call is cached on disk in SQLite, so repeated demo questions cost zero requests.
Develop with USE_MOCK_LLM=1. Switch it to 0 only when you are testing a prompt. Do not loop over the API.
For JSON output, ask for JSON only and use the model’s JSON mode (the prompt must contain the word JSON). Parse defensively: strip code fences, and treat any parse failure as an empty result.
The corpus is fictional, so sending it to a free-tier API is fine.
3.3 app/llm.py behaviour (Dev 3 implements exactly this)
Item
Specification
Signatures
complete_text(prompt: str, system: str = '') -> str and complete_json(prompt: str, system: str = '') -> dict
Order of attempts
Cache lookup, then (if USE_MOCK_LLM=1 return '' or {}), then Groq main model, then Groq fast model, then Gemini if a key exists, then return '' or {}
Retries
One retry after 2 seconds on HTTP 429, 5xx or timeout, per model, then move to the next model
Timeout
20 seconds per request, temperature 0
Cache
SQLite at data/cache/llm.sqlite, key is a SHA-256 of model name, system prompt and prompt. Store only successful, non-empty results
Failure contract
Never raises. An empty string or empty dict means “LLM unavailable”, and every caller must have a deterministic fallback
Logging
Log model used, cache hit or miss and errors to stderr. Never log keys

3.4 HTTP API between backend and frontend
Base URL http://localhost:8000. JSON only. CORS allows http://localhost:5173 and http://127.0.0.1:5173. Response shapes are exactly the models in contracts.py.
Endpoint
Request
Response
POST /ask
Body AskRequest (question, role)
AskResponse
GET /onboarding
?job_role=QA&role=analyst (job roles: QA, Production, Regulatory)
OnboardingPath
GET /experts
?topic=deviation&role=analyst
list of Expert
GET /gaps
none
list of GapItem
GET /stats
none
Stats
GET /health
none
Health

Conventions (everyone follows these):
An invalid role returns 422 from Pydantic. Nothing else may return a 5xx. If something fails internally, /ask returns a safe AskResponse with answerable=false, confidence='low', empty citations and a plain missing_info message.
Refusals and “don’t know” look identical. answerable=false, confidence='low', citations=[], conflicts=[], and a missing_info sentence. The text must never reveal that a restricted document exists.
Answer text uses bracketed numbers like [1] and [2] that match the order of citations, so the UI can render clickable chips.
latency_ms is measured in main.py. minutes_saved is an estimate and the UI labels it that way.
Defence in depth: main.py re-checks every returned citation and conflict source against the role in chunks.json and drops anything not allowed, even though retrieval already filtered.
3.5 Environment and ports
Backend 8000, frontend 5173. Run everything from the repo root: uvicorn app.main:app --reload --port 8000, and selftests as python -m modules.ingestion.selftest. Python 3.11+ in a virtual environment, Node 20+. All paths come from app/config.py; no module builds its own file paths.
4. Architecture and repo layout
data/raw/ (corpus + .meta.json sidecars)  [Dev 1]
  -> Ingestion (4 connectors) -> data/processed/{docs,chunks,people}.json  [Dev 2]
  -> Retrieval (role filter first, then BM25 + glossary) -> Groq answer or extractive fallback  [Dev 3]
  -> Intelligence (conflicts, gaps, stats, query log in SQLite)  [Dev 4]
  -> FastAPI: /ask /onboarding /experts /gaps /stats /health  [Dev 4]
  -> React UI (3 tabs, built last)  [Dev 5 + Devs 1 to 4]
Golden rule: modules talk only through the Pydantic models in contracts.py and the JSON files in data/processed/. Nobody imports another module’s internals, only the names exported in its __init__.py.
provenance/
  PLAN.md  AGENT_RULES.md  README.md  run.sh  requirements.txt  .env.example  .gitignore   [Dev 5]
  contracts.py                      [Dev 5, FROZEN after Phase 0]
  app/__init__.py
  app/config.py                     [Dev 5, read-only for everyone else]
  app/llm.py                        [Dev 3]
  app/main.py                       [Dev 4]
  modules/__init__.py
  modules/ingestion/                [Dev 2]  __init__.py (exports 3 functions), connectors, chunker, build, experts, onboarding, make_sample_raw.py, selftest.py
  modules/retrieval/                [Dev 3]  __init__.py (exports 2 functions), glossary.json, index.py, search.py, answer.py, selftest.py
  modules/intelligence/             [Dev 4]  __init__.py (exports 4 functions), conflicts.py, gaps.py, selftest.py
  corpus_gen/                       [Dev 1]  manifest.py, generate.py, client.py, validate.py, golden_questions.json
  data/raw/                         [Dev 1, committed]
  data/processed/                   [Dev 2, gitignored until integration, then force-added]
  data/fixtures/chunks_sample.json  [Dev 5, FROZEN]
  data/fixtures/raw_sample/         [Dev 2]
  data/cache/                       [gitignored]
  tests/smoke.py  warm_cache.py     [Dev 4]
  frontend/                         [Dev 5 shell, then Devs 1 to 4 own the components listed in §10.8]
5. Contracts (frozen after Phase 0)
5.1 contracts.py
If a bug is found, tell Dev 5. Only additive changes with default values are allowed, made on main, and everyone then runs git pull origin main.
from pydantic import BaseModel
from typing import Literal, Optional

Role = Literal['intern', 'analyst', 'manager']
Source = Literal['sharepoint', 'sop', 'pdf', 'email', 'teams']

class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    source_type: Source
    title: str
    version: Optional[str] = None
    date: str                          # ISO yyyy-mm-dd
    author: str
    owner: Optional[str] = None
    status: Literal['current', 'superseded', 'draft'] = 'current'
    supersedes: Optional[str] = None   # doc_id it replaces
    allowed_roles: list[Role]
    location: str                      # 'page 3', 'section 2', 'msg 12-16'
    topics: list[str] = []

class Citation(BaseModel):
    chunk_id: str
    doc_id: str
    title: str
    source_type: Source
    version: Optional[str] = None
    date: str
    status: str
    snippet: str
    location: str

class Conflict(BaseModel):
    topic: str
    kind: Literal['contradiction', 'superseded'] = 'contradiction'
    explanation: str
    source_a: Citation
    source_b: Citation
    recommendation: str

class Expert(BaseModel):
    name: str
    role: str
    evidence_count: int
    topics: list[str]
    sample_source: str

class AskRequest(BaseModel):
    question: str
    role: Role

class AskResponse(BaseModel):
    answer: str
    answerable: bool
    confidence: Literal['high', 'medium', 'low']
    citations: list[Citation]
    conflicts: list[Conflict] = []
    missing_info: Optional[str] = None
    expanded_terms: dict[str, str] = {}
    experts: list[Expert] = []
    minutes_saved: float = 0.0
    latency_ms: int = 0

class ReadingItem(BaseModel):
    order: int
    doc_id: str
    title: str
    why: str
    est_minutes: int

class OnboardingPath(BaseModel):
    job_role: str
    days: dict[str, list[ReadingItem]]   # 'Day 1' .. 'Day 5'

class GapItem(BaseModel):
    question: str
    asked_count: int
    last_asked: str
    reason: str

class Stats(BaseModel):
    total_questions: int = 0
    answered: int = 0
    unanswered: int = 0
    total_minutes_saved: float = 0.0
    conflicts_flagged: int = 0
    by_role: dict[str, int] = {}

class Health(BaseModel):
    status: str = 'ok'
    chunks: int = 0
    llm: str = 'mock'            # mock | groq | offline
    data_source: str = 'fixtures'  # fixtures | real
5.2 Function signatures (the only cross-module surface)
Package
Exported functions
modules.ingestion
build_corpus() -> None (writes docs.json, chunks.json, people.json), find_experts(topic: str, role: Role) -> list[Expert], onboarding_path(job_role: str, role: Role) -> OnboardingPath
modules.retrieval
search(question: str, role: Role, k: int = 8) -> list[Chunk], answer(question: str, role: Role) -> AskResponse (core answer only; no conflicts, experts, minutes or latency)
modules.intelligence
detect_conflicts(chunks: list[Chunk]) -> list[Conflict], log_query(req: AskRequest, resp: AskResponse) -> None, gap_report() -> list[GapItem], get_stats() -> Stats
app.llm
complete_text(prompt: str, system: str = '') -> str, complete_json(prompt: str, system: str = '') -> dict
app.config
raw_dir(), chunks_path(), PROCESSED_DIR, FIXTURES_DIR, CACHE_DIR, llm_mode(), use_mock_llm()

/ask flow (Dev 4 wires it): retrieval.search for the chunks, retrieval.answer for the core answer, detect_conflicts on the retrieved chunks, find_experts for the detected topic, compute minutes_saved and latency_ms, re-check roles, log_query, return.
5.3 Processed files (written by Dev 2, read by others)
data/processed/chunks.json: a list of Chunk objects. This is the only file Dev 3 and Dev 4 read.
data/processed/docs.json: a list of document records: doc_id, title, source_type, version, date, author, owner, status, supersedes, allowed_roles, topics, word_count, file.
data/processed/people.json: a list of {name, role, topics: {topic: count}, sources: [doc_id], evidence_count}. Only Dev 2 reads it.
5.4 Raw corpus contract (Dev 1 writes, Dev 2 reads)
Every document is one file plus a sidecar named <file>.meta.json, for example SOP-014-v3.pdf and SOP-014-v3.pdf.meta.json.
Folder
Format
Notes
data/raw/sop/
.pdf
Real text (made with reportlab, not images), numbered sections, 1 to 3 pages
data/raw/pdf/
.pdf
Same, for non-SOP PDFs
data/raw/sharepoint/
.docx
Headings and paragraphs, made with python-docx
data/raw/email/
.eml
Headers From, To, Subject, Date, plain-text body, a short thread is fine
data/raw/teams/
.json
One file per channel: a list of {msg_id (int), author, timestamp (ISO), text}, 10 to 25 messages

Sidecar fields (all required): doc_id, title, source_type (sharepoint, sop, pdf, email or teams), version (string or null), date (ISO), author, owner, status (current, superseded or draft), supersedes (a doc_id or null), allowed_roles (list drawn from intern, analyst, manager), topics (list from the vocabulary below).
5.5 Shared vocabularies
Topic vocabulary (the only allowed topic values): deviation, capa, oos, cold-chain, storage-temperature, audit, onboarding, data-integrity, stability, equipment, regulatory, quality-system, new-joiner.
Chunk IDs: <doc_id>#001, #002 and so on, stable across rebuilds.
Location strings: PDFs page N, Word documents section N, emails email body, Teams msg A-B (message id range).
Chunking: about 150 words with 20 words of overlap for documents; Teams uses 3 to 5 messages per chunk.
6. Corpus blueprint (fictional company Novacure Labs, 20 documents)
The corpus is the shared truth that every module, fixture, test and demo question depends on. Dev 1 generates it; everyone else reads this section, never the generated files, during Phase 1.
6.1 People (use these names consistently)
Name
Title
Dr. Meera Iyer
QA Head
Priya Rao
QA Lead (owns deviation management)
Arjun Menon
Cold-Chain Supervisor
Sana Khan
QA Analyst
Kavya Nair
Regulatory Affairs Manager
Vikram Shah
Production Manager
Rahul Verma
New QA joiner

6.2 The 20 documents
Roles: I = intern, A = analyst, M = manager. Dates are ISO and fall in 2024 to 2026 unless stated. doc_id is also the file name stem.
doc_id
Folder
Title
Type
Ver
Status
Roles
Topics
SOP-001
sop
SOP-001 Deviation Handling
sop
1.0
current
I A M
deviation, quality-system
SOP-014-v2
sop
SOP-014 Cold-Chain Storage v2
sop
2.0
superseded
A M
cold-chain, storage-temperature
SOP-014-v3
sop
SOP-014 Cold-Chain Storage v3
sop
3.0
current
I A M
cold-chain, storage-temperature
SOP-021
sop
SOP-021 CAPA Management
sop
1.0
current
A M
capa, oos, deviation
QM-001
sharepoint
Quality Manual
sharepoint
4.1
current
I A M
quality-system, deviation
ONB-001
sharepoint
New QA Hire Onboarding Guide
sharepoint
2.0
current
I A M
onboarding, new-joiner, deviation
DI-001
sharepoint
Data Integrity Policy
sharepoint
1.2
current
A M
data-integrity, quality-system
AUD-001
sharepoint
Audit Findings Summary
sharepoint
1.0
current
M only
audit, deviation, cold-chain
EML-001
email
Storage temperature change (from QA Head)
email
null
current
A M
cold-chain, storage-temperature
EML-002
email
Deviation closure thread
email
null
current
A M
deviation
EML-003
email
CAPA overdue reminder
email
null
current
A M
capa, deviation
EML-004
email
Audit prep
email
null
current
M only
audit, deviation
EML-005
email
New joiner welcome
email
null
current
I A M
onboarding, new-joiner
TEAMS-COLDCHAIN
teams
#cold-chain
teams
null
current
A M
cold-chain, storage-temperature
TEAMS-QAHELP
teams
#qa-help
teams
null
current
I A M
deviation, onboarding
TEAMS-DEVIATIONS
teams
#deviations
teams
null
current
A M
deviation, capa
TEAMS-NEWJOINERS
teams
#new-joiners
teams
null
current
I A M
onboarding, new-joiner
REG-001
pdf
Regulatory Guideline Summary
pdf
1.0
current
A M
regulatory, data-integrity
EQP-001
pdf
Cold Storage Unit Equipment Manual
pdf
1.0
current
A M
equipment, cold-chain
STB-001
pdf
Stability Study Report
pdf
1.0
current
A M
stability, storage-temperature

Fixed metadata: SOP-014-v2 is dated 2024-11-05 and authored by Arjun Menon. SOP-014-v3 is dated 2025-06-20, authored by Arjun Menon, and has supersedes set to SOP-014-v2. EML-001 is dated 2026-09-18 and sent by Dr. Meera Iyer. TEAMS-COLDCHAIN messages are dated 2026-09-19 to 2026-09-22. All other supersedes values are null. Owners are the document authors unless stated.
Access rule: An intern sees exactly: Quality Manual, onboarding guide, SOP-001, SOP-014-v3, #qa-help, #new-joiners, and the welcome email. An analyst sees everything except AUD-001 and EML-004. A manager sees everything.
6.3 Fixed sentences (must appear verbatim in the generated documents)
The LLM may write any surrounding prose, but these sentences are the planted facts. generate.py checks each one appears verbatim and, if it does not, appends it as a clearly marked paragraph. Write temperature ranges exactly as digit, space, to, space, digit, space, degree sign, C.
doc_id
Fixed sentence
SOP-014-v3
Vaccine batches must be stored at 2 to 8 °C.
SOP-014-v3
Any temperature excursion longer than 4 hours requires a deviation report.
SOP-014-v2
Vaccine batches must be stored at 2 to 8 °C.
SOP-014-v2
Temperature excursions of up to 12 hours do not require a deviation report.
EML-001
Until SOP-014 is revised, store vaccine batches at 2 to 6 °C.
TEAMS-COLDCHAIN
Per Dr. Meera Iyer, hold vaccine batches at 2 to 6 °C until SOP-014 is revised. (posted by Arjun Menon)
SOP-001
Every deviation must be reported to QA within 24 hours of discovery.
SOP-021
A CAPA must be raised and the investigation completed within 15 working days of an OOS result being confirmed.
AUD-001
The audit identified a recurring deviation: temperature excursions in cold-chain storage during Q2 and Q3.
ONB-001
In your first week, read the Quality Manual, SOP-001, SOP-021 and the Data Integrity Policy.
Ten documents (see 6.4, scenario 5)
Priya Rao, QA Lead, owns deviation management. (or a natural sentence naming Priya Rao as the sender, author, reviewer or replier)

Hard rules for all prose: the string HPLC must never appear in any document. REG-001, EQP-001 and STB-001 must not state any temperature range other than 2 to 8 °C (they may omit ranges entirely). SOP-021 should use the abbreviations CAPA and OOS (spelled out at most once) so glossary expansion has work to do.
6.4 Planted scenarios (validate.py must confirm all 7)
Conflict: SOP-014-v3 says 2 to 8 °C. EML-001 and TEAMS-COLDCHAIN say 2 to 6 °C pending revision.
Superseded: SOP-014-v2 exists with status superseded and a different excursion rule (12 hours against 4 hours).
Restricted: AUD-001 (manager only) mentions a recurring deviation, so an intern asking about it gets no citation from it and no hint that it exists.
Unanswerable: nothing anywhere mentions HPLC or column calibration.
Expert: Priya Rao appears by name in at least 8 documents tagged deviation. Plan: SOP-001, SOP-021, QM-001, ONB-001, AUD-001, EML-002, EML-003, EML-004, TEAMS-QAHELP, TEAMS-DEVIATIONS.
Glossary: SOP-021 defines the OOS timeline using the abbreviations, so the question needs both terms expanded.
Onboarding: QA reading material exists (Quality Manual, SOP-001, SOP-021, Data Integrity Policy, onboarding guide).
6.5 Twelve golden questions (Dev 1 writes them to corpus_gen/golden_questions.json)
Each entry has id, question, role, expected_behavior (answer, conflict, refuse or unanswerable), expected_docs and must_not_cite.
id
Question
Role
Expected behaviour
Expected docs
G1
What temperature should vaccine batches be stored at?
analyst
conflict (contradiction)
SOP-014-v3, EML-001, TEAMS-COLDCHAIN; SOP-014-v2 flagged superseded
G2
What temperature should vaccine batches be stored at?
intern
answer 2 to 8 °C, no conflict
SOP-014-v3 only
G3
What temperature should vaccine batches be stored at?
manager
conflict
same as G1
G4
What is the CAPA timeline for an OOS result?
analyst
answer 15 working days, CAPA and OOS expanded
SOP-021
G5
What is the CAPA timeline for an OOS result?
intern
refuse
must not cite SOP-021
G6
What recurring deviation did the audit find?
intern
refuse
must not cite AUD-001, EML-004
G7
What recurring deviation did the audit find?
manager
answer (cold-chain temperature excursions)
AUD-001
G8
How do I calibrate an HPLC column?
analyst
unanswerable, logged as a gap
none
G9
Who knows about deviation handling?
analyst
answer plus experts list led by Priya Rao
SOP-001, TEAMS-DEVIATIONS
G10
How do I report a deviation?
intern
answer within 24 hours
SOP-001
G11
What should I read in my first week as a new QA hire?
analyst
answer
ONB-001
G12
What happens if a temperature excursion occurs in cold storage?
analyst
answer 4 hours, superseded 12-hour rule flagged
SOP-014-v3; SOP-014-v2 flagged

6.6 Fixture chunks (data/fixtures/chunks_sample.json, created by Dev 5 in Phase 0)
14 chunks in the Chunk schema, one per row. Each text is the fixed sentence from 6.3 verbatim plus one or two filler sentences. Use source_type, version, status, allowed_roles, author and date from 6.2. Chunk IDs follow <doc_id>#001.
chunk_id
Fixed sentence it carries
Location
SOP-014-v3#001
2 to 8 °C storage rule
page 1
SOP-014-v3#002
4-hour excursion rule
page 2
SOP-014-v2#001
2 to 8 °C storage rule
page 1
SOP-014-v2#002
12-hour excursion rule
page 2
EML-001#001
2 to 6 °C pending revision
email body
TEAMS-COLDCHAIN#001
Per Dr. Meera Iyer 2 to 6 °C message
msg 4-8
SOP-021#001
15 working days for an OOS result
page 1
SOP-001#001
24 hours to report a deviation
page 1
TEAMS-DEVIATIONS#001
Priya Rao advising on deviation classification
msg 2-6
EML-002#001
Priya Rao closing deviation DEV-2026-044
email body
AUD-001#001
Recurring deviation finding
section 1
ONB-001#001
First-week reading list
section 1
QM-001#001
Priya Rao owns deviation management
section 2
TEAMS-QAHELP#001
Intern asks how to report a deviation, Priya Rao replies
msg 1-4

7. Schedule (3 hours) and integration
Time
What
Checkpoint
0:00 to 0:15
Phase 0. Dev 5 builds and pushes the starter pack (Appendix A, prompt in §10.1). Devs 1 to 4 install tools, create Groq keys, clone, and wait for the push
main exists, every endpoint returns fake data
0:15 to 1:15
Phase 1, parallel. Devs 1 to 4 build their modules on fixtures, each on their own branch. Dev 5 prepares the empty frontend shell, README and pitch slides
Each dev’s selftest passes on their branch
1:15 to 1:20
Merge. Dev 5 merges the five branches into main (order dev1, dev2, dev3, dev4, dev5)
main has everything
1:20 to 1:50
Integration (30 min cap). Runbook below
/ask works for all 3 roles, smoke test green
1:50 to 2:35
Frontend. Dev 5 plus Devs 1 to 4, one component set each, in parallel (§10.8)
Demo path is clickable
2:35 to 2:50
Polish, warm_cache.py, offline test, 2-minute backup screen recording
Demo works with the network off
2:50 to 3:00
Code freeze. Rehearse the pitch twice
Done

If integration runs over, take the extra time (up to 15 minutes) from the polish window, never from rehearsal.
7.1 Integration runbook (Dev 5 leads, everyone online)
Min
Step
Owner
0 to 5
Merge all branches to main. Everyone: git checkout main, git pull, pip install -r requirements.txt
Dev 5
5 to 10
Run python -m corpus_gen.validate on the merged data/raw and confirm all 7 scenarios pass
Dev 1
5 to 12
Run build_corpus() on the real corpus, check about 20 documents and a sane chunk count, then git add -f data/processed/*.json, commit and push
Dev 2
12 to 17
Start the backend, open /health (must show data_source real), run python tests/smoke.py for all 3 roles
Dev 4
17 to 27
Fix failures. The owner of the failing behaviour fixes it (table below). No new features
All
27 to 30
Run python warm_cache.py (all 12 golden questions, 3 roles) and review the results against §6.5
Dev 4 and Dev 3


Symptom
Owner
Wrong or missing documents, missing planted sentences
Dev 1
Wrong chunk text, locations, roles, experts, reading path
Dev 2
Bad answers, wrong refusals, LLM errors, glossary
Dev 3
Conflicts missing, wrong stats or gaps, API errors, role leak
Dev 4

7.2 Cut rules
At 1:15, anything that fails its selftest is merged only if it does not break imports; otherwise the stub stays and the owner fixes it during integration.
No corpus at 1:00: Dev 1 switches to --offline templates for the 12 most important documents (all fixed-sentence ones first).
At 1:50 with /ask not working for all 3 roles: everyone helps Dev 3 and Dev 4 until it does. The frontend starts only when /ask works.
At 2:35 with the UI unfinished: drop the Onboarding and Experts screens from the UI (keep the endpoints), then the dashboard bar chart. Never drop citations, the conflict banner, the refusal card or the role switcher.
8. Setup (first 15 minutes) and Git workflow
Everyone: install Python 3.11+, Node.js 20+, Git and Antigravity; sign in to Antigravity with a Google account; create a Groq account and API key; check the model names in the Groq console and note one large and one small model.
Dev 5 (lead): create a private GitHub repo named provenance, invite the four devs, save this document as PLAN.md, add AGENT_RULES.md (§9), run the Phase 0 prompt (§10.1), verify the backend, push to main, then tell the team “main is ready”.
Devs 1 to 4, after the push:
git clone <repo-url> && cd provenance
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # add your GROQ_API_KEY and model names
git checkout -b dev1-corpus      # dev2-ingestion, dev3-retrieval, dev4-intel
Git rules:
One branch per dev: dev1-corpus, dev2-ingestion, dev3-retrieval, dev4-intel, dev5-frontend.
Nobody commits to main except Dev 5, who merges. .env is never committed.
Commit small and push your own branch every 20 to 30 minutes, so a dead laptop never costs more than 30 minutes.
Because folders are disjoint, merges are conflict-free. If you touched a file outside your folder, undo it: git checkout main -- <path>.
requirements.txt already lists every package. If you truly need another package, message Dev 5, who adds it on main.
In Antigravity: open the repo, use the Agent Manager, one agent per dev, always start in Plan mode (read the plan, skim, then approve).
9. AGENT_RULES.md (paste into the repo root)
Project: Provenance, a trust-first enterprise knowledge assistant (pharma, fictional company Novacure Labs).
Build window: 3 hours. Simple and working beats clever.
Read PLAN.md first, especially sections 2 (ownership), 3 (APIs), 5 (contracts) and 6 (corpus).

Rules:
1. Never edit contracts.py or app/config.py. If a change seems needed, stop and tell the human.
2. Only create or edit files inside the paths you own (PLAN.md section 2). Never touch another dev's files.
3. Every public function must match the signature in PLAN.md section 5.2 exactly, and be exported from your package __init__.py (replace the stub).
4. Functions never raise on bad input. Return an empty or safe result and log the error to stderr.
5. Everything must be free and local. LLM calls only through app/llm.py (corpus_gen/client.py is the one exception).
6. Never hardcode secrets or model names. Read GROQ_API_KEY, GROQ_MODEL_MAIN, GROQ_MODEL_FAST, USE_MOCK_LLM from the environment.
7. Do not call the LLM during ingestion, indexing, search, gap reporting or server startup.
8. Security: filter chunks by role BEFORE ranking and before any text reaches the LLM. A refusal must never reveal that a restricted document exists.
9. Get all file paths from app/config.py. Never build your own paths.
10. Add a selftest runnable as python -m <your.module>.selftest that uses fixtures and needs no network and no API key.
11. Keep code short, commented and dependency-light. Do not add packages.
12. Use the exact doc_ids, fixed sentences and topic vocabulary from PLAN.md sections 5.5 and 6.
13. Commit only to your own branch. Never push to main.
14. Before finishing, run your selftest, fix failures, then summarize what works and what does not.
10. Prompts (paste into your Antigravity agent, in Plan mode)
Every prompt starts with the same context block, so each agent understands the whole project, its own boundary, and what it must not depend on.
10.0 Context block (paste at the top of EVERY prompt)
CONTEXT (read first): You are building one part of Provenance, a trust-first enterprise knowledge assistant for pharma (fictional company Novacure Labs), in a 3-hour hackathon with 5 people. Users ask natural-language questions; the system answers from SharePoint, SOP, PDF, email and Teams documents with exact citations, flags conflicting or superseded documents, enforces roles (intern, analyst, manager), and says it does not know when evidence is weak. Everything is free and local: Python 3.11, FastAPI, rank_bm25, SQLite, Groq through app/llm.py, React + Vite + Tailwind.
Before writing code, read AGENT_RULES.md and PLAN.md completely. PLAN.md is your authority: ownership (section 2), API and LLM rules (section 3), contracts (section 5), corpus and fixed sentences (section 6). You work alone, in your own folders, on your own branch, and you must NOT depend on any other developer's code: use the fixtures and stubs described in your task. Start in Plan mode: write a short plan, then implement, run your selftest, fix failures, commit to your branch, and finish with a summary of what works and what does not.
10.1 Phase 0: starter pack (Dev 5, 0:00 to 0:15)
[paste context block]
You are Dev 5 (lead). Create the starter pack on branch main. 1) Create every file listed in PLAN.md Appendix A exactly as written (requirements.txt, .env.example, .gitignore, run.sh, app/__init__.py, app/config.py, app/llm.py stub, app/main.py stub, modules/__init__.py and the three stub modules/*/__init__.py). 2) Create contracts.py by copying the code in PLAN.md section 5.1 exactly. 3) Create AGENT_RULES.md from PLAN.md section 9, and keep PLAN.md in the root. 4) Create data/fixtures/chunks_sample.json with the 14 chunks in PLAN.md section 6.6, using the Chunk schema, the metadata in section 6.2 and the fixed sentences in section 6.3 verbatim, plus one or two filler sentences per chunk. 5) Create empty folders with a .gitkeep: corpus_gen/, data/raw/, data/fixtures/raw_sample/, data/cache/, tests/. 6) Verify: python -c 'import contracts, app.main' passes, then start uvicorn app.main:app --port 8000 and call every endpoint (POST /ask for each role, GET /onboarding, /experts, /gaps, /stats, /health) and confirm each returns valid JSON. 7) Commit and push to main. Do not implement real logic anywhere.
10.2 Dev 1: corpus generator (owns corpus_gen/ and data/raw/)
[paste context block]
You are Dev 1. You own corpus_gen/ and data/raw/. Do not import from app/ or modules/. Build a generator for the 20 documents in PLAN.md section 6.2, with the exact doc_ids, titles, versions, statuses, roles, topics and dates there, and the file and sidecar format in section 5.4.
Step 1, corpus_gen/manifest.py: a Python list of 20 spec dicts holding every sidecar field, a 3-line content brief, the fixed sentences from section 6.3 for that document, and the people from section 6.1 who must appear. Use only topics from the vocabulary in section 5.5.
Step 2, corpus_gen/client.py: a tiny standalone Groq client (groq SDK). Read GROQ_API_KEY, GROQ_MODEL_MAIN and GROQ_MODEL_FAST from the environment (python-dotenv), 20 second timeout, one retry after 2 seconds on HTTP 429 or 5xx, fall back to the fast model, return an empty string on any failure, never raise, and return an empty string immediately when USE_MOCK_LLM=1.
Step 3, corpus_gen/generate.py: for each spec, ask the client for realistic content (SOPs: numbered sections for purpose, scope, responsibilities and procedure; emails: headers plus a short thread; Teams: 10 to 25 short casual messages with msg_id, author, ISO timestamp; SharePoint pages: headings and paragraphs). If the client returns an empty string, use a built-in offline template that still reads like a real document. Always ensure every fixed sentence appears verbatim, appending it as its own paragraph if the text lacks it. Remove the string HPLC if it ever appears. Render SOPs and other PDFs with reportlab (real extractable text), SharePoint documents with python-docx, emails with the stdlib email package as .eml, and Teams channels as JSON lists. Write each sidecar <file>.meta.json. Pause 2 seconds between LLM calls. Make it resumable (skip existing files unless --force), and support --offline (no LLM at all) and --only DOC_ID. IMPORTANT ORDER: first run with --offline so a complete valid corpus exists within minutes and commit it; then re-run with the LLM for richer prose, overwriting a document only if the validator still passes.
Step 4, corpus_gen/validate.py (this is your selftest, run as python -m corpus_gen.validate): check there are exactly the 20 doc_ids; every file has a complete sidecar with allowed values; PDFs yield text through pypdf; the access rule in section 6.2 holds; every fixed sentence is present; and all 7 planted scenarios in section 6.4 hold (including: no document contains HPLC, and Priya Rao appears in at least 8 documents tagged deviation). Print a PASS or FAIL line per check and exit non-zero on failure.
Step 5, corpus_gen/golden_questions.json: the 12 questions in section 6.5 with id, question, role, expected_behavior, expected_docs and must_not_cite.
Run the generator and the validator and fix until everything passes. Commit data/raw/ and corpus_gen/ to your branch dev1-corpus.
10.3 Dev 2: ingestion, experts, onboarding (owns modules/ingestion/ and data/fixtures/raw_sample/)
[paste context block]
You are Dev 2. You own modules/ingestion/ and data/fixtures/raw_sample/. The real corpus does not exist yet, so build against your own sample files; the code must pick up the real corpus automatically through app.config.raw_dir().
Step 1, modules/ingestion/make_sample_raw.py: generate 8 or more small sample documents that follow the raw corpus contract in section 5.4 exactly, using real doc_ids from section 6.2 (include SOP-014-v2 superseded, SOP-014-v3, SOP-021 as PDFs via reportlab; QM-001 and AUD-001 as .docx via python-docx; EML-001 as .eml; TEAMS-COLDCHAIN as a channel JSON; plus at least one more of each type). Include one manager-only file and a few mentions of Priya Rao. Write them to data/fixtures/raw_sample/<folder>/ with sidecars.
Step 2, connectors: SharePointConnector (.docx), SopConnector (PDF through pypdf, one location per page: 'page N', used for both sop and pdf folders), EmailConnector (.eml with Subject, From, To, Date; location 'email body') and TeamsConnector (one chunk per 3 to 5 messages, location 'msg A-B' using msg_id). Each has load(raw_dir) -> list[Chunk], reads metadata only from the sidecar (never infer roles or status), and has a docstring explaining how the Microsoft Graph API would replace the local folder (SharePoint drive items, Teams channel messages, Outlook messages, delta queries for incremental sync, and item permissions for allowed_roles). This docstring is used in the pitch.
Step 3, chunker: about 150 words with 20 words of overlap for documents, stable chunk_ids like SOP-014-v3#001, and the Chunk fields in section 5.1.
Step 4, build_corpus(): run all connectors on app.config.raw_dir(), write data/processed/chunks.json, docs.json and people.json (section 5.3) into app.config.PROCESSED_DIR, create the folder if needed, be idempotent, and print counts. Internally call a helper build(raw_dir, out_dir) so your selftest can write to a temp folder.
Step 5, people and find_experts(topic, role): people come from authors, email senders, Teams participants, and names from the section 6.1 list found in text. Hardcode the name-to-title map from section 6.1. Normalize the topic to the vocabulary in section 5.5 by keyword or substring match (for example 'deviation handling' becomes deviation). Count evidence only in chunks the given role may see, rank descending, return up to 3 Expert objects with role (title), evidence_count, top topics and sample_source (title of the document with the most evidence). For deviation, Priya Rao must rank first for every role.
Step 6, onboarding_path(job_role, role): hardcode ordered doc_id lists: QA = ONB-001, QM-001, SOP-001, DI-001, SOP-021, SOP-014-v3; Production = QM-001, SOP-014-v3, EQP-001, SOP-001, STB-001; Regulatory = QM-001, REG-001, DI-001, SOP-021, AUD-001. Keep only documents the role may see that are current (never superseded), place the first two items on Day 1 and then one item per day up to Day 5, omit empty days, write a one-line deterministic why from a template per topic, and estimate minutes from word count (200 words per minute, minimum 5). Unknown job roles return an empty OnboardingPath.
Export build_corpus, find_experts and onboarding_path from modules/ingestion/__init__.py, replacing the stub. No LLM calls anywhere. Selftest (python -m modules.ingestion.selftest, no network, writes to a temp folder): assert all four connectors return chunks, chunk_ids are unique, the manager-only document's chunks list only manager, superseded status is preserved, Priya Rao is the top deviation expert for analyst, and the onboarding path contains no superseded or restricted document. Do not commit data/processed/ (it is gitignored). Commit to branch dev2-ingestion.
10.4 Dev 3: LLM wrapper, retrieval, answering (owns app/llm.py and modules/retrieval/)
[paste context block]
You are Dev 3. You own app/llm.py and modules/retrieval/. Work against data/fixtures/chunks_sample.json through app.config.chunks_path(), which switches to the real chunks.json automatically later. Develop with USE_MOCK_LLM=1.
Step 1 (first 15 minutes), app/llm.py exactly as in PLAN.md section 3.3: complete_text and complete_json; order cache, mock check, Groq main model, Groq fast model, optional Gemini through plain REST with requests, then empty result; one retry after 2 seconds on 429, 5xx or timeout; 20 second timeout; temperature 0; SQLite cache at app.config.CACHE_DIR/llm.sqlite keyed by a SHA-256 of model, system and prompt; cache only successful results; JSON mode for complete_json with defensive parsing (strip code fences); never raise; never log keys.
Step 2, modules/retrieval/glossary.json: about 40 pharma terms as {abbreviation: {expansion, also: [related words]}}: CAPA, OOS, OOT, GMP, GDP, SOP, BMR, QA, QC, deviation, change control, cold chain, excursion, ALCOA, stability, batch record, and others. Add related words that bridge vocabulary, for example 'vaccine' and 'storage' to 'cold chain', 'temperature' to 'excursion'.
Step 3, index and search(question, role, k=8): load chunks through app.config.chunks_path(), build one rank_bm25 index PER ROLE over only the chunks that role may see (so restricted text never touches ranking), tokenize by lowercasing and splitting on non-alphanumerics with a small stopword list, expand the query with the glossary, rank, multiply the score of non-current chunks by 0.85 but still return them, return the top k as Chunk objects. Rebuild if the file changes.
Step 4, answer(question, role) -> AskResponse (core only): take the top 8 chunks. Apply an answerability gate BEFORE calling the LLM: the share of distinctive query tokens (stopwords removed, glossary expansions included) that appear in the top chunks must be at least 0.5 and the top BM25 score must exceed a MIN_SCORE constant that you tune on the 12 golden questions. If the gate fails, return answerable=false, confidence low, no citations, and a helpful missing_info (what kind of source would be needed), with no invented content and no mention of restricted documents. Otherwise call complete_json once with a strict system prompt: answer ONLY from the numbered passages; if passages give different values, mention each with its source and prefer current documents; return JSON with keys answer, answerable, confidence (high, medium or low), used_passages (list of passage numbers) and missing_info; write citation markers as [n] using passage numbers. Validate the result, map used passages to Citation objects (snippet = the most relevant 40-word window), renumber markers to match the citation order, and set confidence low if every cited chunk is non-current. If complete_json returns an empty dict, return the extractive answer: the top 2 passages as the answer text with [1] and [2] markers, their citations, confidence medium. Fill expanded_terms (abbreviation to expansion) for glossary terms found in the question. Leave conflicts, experts, minutes_saved and latency_ms at defaults.
Export search and answer from modules/retrieval/__init__.py, replacing the stub. Selftest (python -m modules.retrieval.selftest, USE_MOCK_LLM=1, no network): an intern search never returns AUD-001 or EML-004 chunks; the vaccine storage question returns SOP-014-v3 chunks for an analyst; the HPLC question and the intern audit question are answerable=false; the OOS question returns expanded_terms with CAPA and OOS; the extractive path returns at least one citation. Commit to branch dev3-retrieval.
10.5 Dev 4: intelligence, API, smoke test (owns modules/intelligence/, app/main.py, tests/, warm_cache.py)
[paste context block]
You are Dev 4. You own modules/intelligence/, app/main.py, tests/ and warm_cache.py. The other modules are stubs until integration; call them only through the names exported in their __init__.py. Test on data/fixtures/chunks_sample.json.
Step 1, detect_conflicts(chunks) in modules/intelligence/conflicts.py. (a) Staleness: every chunk whose status is superseded becomes a Conflict of kind superseded, naming the current document (the document in the list whose supersedes equals this doc_id; if none is in the list say a newer version exists). Deduplicate one per superseded document. (b) Contradictions: group non-superseded chunks by topic across DIFFERENT doc_ids; extract temperature ranges from the text (two numbers joined by 'to' or a dash, followed by a degree sign and C); when two documents in a group give different ranges, create a Conflict of kind contradiction with topic 'cold-chain storage temperature' (or the shared topic), source_a and source_b as Citation objects (snippet = the sentence holding the range), and call app.llm.complete_json once with a prompt asking for JSON {explanation, recommendation}. If the result is empty, build the explanation deterministically from the facts (both ranges, both sources, the newer date, and whether either source says pending revision) and recommend following the newest source while confirming with QA. Return at most 3 conflicts. Durations are an optional stretch only.
Step 2, modules/intelligence/gaps.py: SQLite at app.config.CACHE_DIR/queries.sqlite with a queries table (id, ts, role, question, answerable, confidence, minutes_saved, n_citations, n_conflicts, reason). log_query(req, resp) inserts a row and never raises. gap_report() groups rows where answerable is 0 or confidence is low by question similarity (lowercase, strip stopwords and punctuation, token Jaccard 0.6 or higher, stdlib only) into GapItem(question, asked_count, last_asked, reason), sorted by count then recency. get_stats() returns Stats from the same table.
Step 3, app/main.py: FastAPI with CORS for http://localhost:5173 and http://127.0.0.1:5173 and the six endpoints in PLAN.md section 3.4. /ask: start a timer; chunks = retrieval.search(question, role); resp = retrieval.answer(question, role); if resp.answerable, resp.conflicts = intelligence.detect_conflicts(chunks) and resp.experts = ingestion.find_experts(topic, role) where topic comes from a TOPIC_KEYWORDS dict you write mapping keywords to the vocabulary in section 5.5 (empty topic means no experts); resp.minutes_saved = 6.0 * (1 + 0.5 * distinct source types cited) when answerable else 0; set latency_ms; RE-CHECK ROLES by loading chunk_id to allowed_roles from app.config.chunks_path() and dropping any citation or conflict source the role may not see; log_query; return. Wrap the whole handler in try/except and return a safe AskResponse (answerable false, confidence low, missing_info 'Something went wrong, please try again.') on any error. /health returns chunk count, app.config.llm_mode() and data_source 'real' when app.config.chunks_path().name is chunks.json, else 'fixtures'. Keep all endpoints returning valid JSON even when modules are stubs.
Step 4, selftest python -m modules.intelligence.selftest: detect_conflicts on the fixture chunks returns one contradiction between SOP-014-v3 and EML-001 or TEAMS-COLDCHAIN and one superseded conflict for SOP-014-v2 (with USE_MOCK_LLM=1); log_query then gap_report and get_stats work on a temp database.
Step 5, tests/smoke.py: use FastAPI TestClient (no server needed). Call every endpoint for all 3 roles; assert an intern never receives a citation or conflict source from AUD-001 or EML-004 for any question in the golden set; assert the analyst vaccine-storage question returns at least one conflict (run this assertion only when /health says data_source is real, otherwise print SKIPPED); assert unanswerable responses have no citations.
Step 6, warm_cache.py: read corpus_gen/golden_questions.json (skip with a warning if missing), run every question for all 3 roles through the TestClient, and print a table of role, answerable, confidence, citation count, conflict count and PASS or FAIL against expected_behavior for the entry's own role.
Commit to branch dev4-intel.
10.6 Dev 5: frontend shell prep, README and pitch (Phase 1, 0:15 to 1:15, owns frontend/, README.md, root files)
This is preparation that depends on nobody: the shell runs against the stub backend. The real UI is built after integration (§10.8).
[paste context block]
You are Dev 5. You own frontend/, README.md and the root files. 1) Scaffold frontend/ with Vite + React + Tailwind 3 (npm create vite@latest frontend -- --template react, then npm install -D tailwindcss@3 postcss autoprefixer and npx tailwindcss init -p). Allowed npm packages: react, react-dom, vite, @vitejs/plugin-react, tailwindcss, postcss, autoprefixer. Nothing else: no router, no state library, no chart library. 2) Create src/api.js with BASE_URL = import.meta.env.VITE_API_URL or http://localhost:8000 and these functions, each using plain fetch and returning parsed JSON or throwing an Error: ask(question, role), getOnboarding(jobRole, role), getExperts(topic, role), getGaps(), getStats(), getHealth(). 3) Create src/context/RoleContext.jsx exposing useRole() with {role, setRole}, default analyst. 4) Create src/App.jsx: header with the Provenance name, the pitch line, a role switcher (Intern, Analyst, Manager), a small health dot from getHealth() showing llm mode and data source, and three tabs: Chat, Onboarding and Experts, Dashboard (no router). 5) Create PLACEHOLDER files for every component in the table in PLAN.md section 10.8 with the exact file names and props, each rendering a minimal visible box, so every import resolves. 6) Verify npm run dev shows the shell talking to the stub backend. 7) Write README.md (how to run: pip install, .env, run.sh) and a one-page slide outline mapping the 5 objectives and 5 outcomes to F1 to F10 (PLAN.md section 1.2) plus the roadmap. Commit to branch dev5-frontend.
10.7 Integration (Dev 4 with Dev 5, 1:20 to 1:50, after the five branches are merged)
[paste context block]
All five branches are merged into main. Follow PLAN.md section 7.1 exactly. Pull main, install requirements, confirm python -m corpus_gen.validate passes, run build_corpus() on data/raw (Dev 2 force-adds data/processed/*.json), start the backend, confirm GET /health shows data_source real, and run python tests/smoke.py for all 3 roles. Fix integration bugs only: no new features and no changes to contracts.py or app/config.py. If a failure belongs to another module, tell its owner (PLAN.md section 7.1 table) instead of editing their files. Then run warm_cache.py and report, for all 3 roles, the results for: vaccine storage temperature (analyst must show a contradiction conflict and a superseded flag, intern must show a plain answer), the CAPA timeline for an OOS result (analyst must show CAPA and OOS expanded, intern must be refused), the audit deviation question (intern must be refused with no citation, manager must be answered), HPLC column calibration (must say it does not know), and who knows about deviation handling (Priya Rao first).
10.8 Frontend (1:50 to 2:35, all five in parallel, one component set each)
One Vite + React + Tailwind page with 3 tabs and no router. The shell, API client and placeholders already exist from §10.6, so every dev only replaces their own placeholder files. The backend is live and real by now.
Component file
Owner
Props
App.jsx, api.js, context/RoleContext.jsx, layout and polish
Dev 5
useRole() returns {role, setRole}
components/Chat.jsx
Dev 1
none (uses useRole and api.ask)
components/CitationPanel.jsx
Dev 1
{citation, onClose}
components/ConfidenceBadge.jsx
Dev 3
{confidence}
components/ConflictBanner.jsx
Dev 3
{conflicts} (array of Conflict)
components/IDontKnowCard.jsx
Dev 3
{missingInfo}
components/StalenessTag.jsx
Dev 3
{status}
components/ExpandedTerms.jsx
Dev 3
{terms} (object of abbreviation to expansion)
components/Onboarding.jsx, components/Experts.jsx
Dev 2
none
components/Dashboard.jsx
Dev 4
none

Shared opening line for all five prompts:
[paste context block]
The frontend lives in frontend/ (Vite, React, Tailwind 3, plain fetch). The backend is running at http://localhost:8000 and the response shapes are the Pydantic models in contracts.py (PLAN.md section 5.1). The shell, api.js, RoleContext and placeholder components already exist: replace ONLY the files assigned to you, keep the exact file names and props from the table in PLAN.md section 10.8, add no npm packages, and import other people's components only by that contract. Backend is live: test every state against it by switching roles in the header.
Dev 5 (shell and polish): make the layout responsive and clean, make the role switcher refetch and clear the current answer on change, show a clear error banner when the backend is unreachable, add a footer note that minutes saved is an estimate, and own the final visual pass and the screen recording.
You are Dev 5. Finish App.jsx polish: consistent spacing, a readable type scale, a tab bar with an active state, a role switcher with a one-line description of what each role can see, and an error banner for network failures. When teammates push components, pull and run the complete demo path from PLAN.md section 11, fixing layout issues only.
Dev 1 (chat tab):
You are Dev 1. Build components/Chat.jsx and components/CitationPanel.jsx. Chat: a question box with a send button and Enter to submit; 5 example-question chips taken from the demo script in PLAN.md section 11; a loading state; then show, in this order, ConflictBanner (when conflicts is not empty), the answer text with each [n] marker rendered as a clickable numbered chip that opens the matching citation, ConfidenceBadge, ExpandedTerms (when expanded_terms is not empty), a row of source chips (title, source type, version), the experts list as small chips when present, and a 'saved about N minutes (estimate)' badge plus latency. When answerable is false show IDontKnowCard with missing_info and nothing else. CitationPanel is a side panel showing the title, source type badge, version, date, StalenessTag for the status, location and the snippet in a highlighted block, with a close button. Keep a short conversation history on screen, newest at the bottom.
Dev 2 (onboarding and experts):
You are Dev 2. Build components/Onboarding.jsx and components/Experts.jsx. Onboarding: a job-role picker (QA, Production, Regulatory) calling api.getOnboarding with the current role, rendering a Day 1 to Day 5 timeline where each item shows order, title, the why line and an estimated minutes badge, with a total reading time and a friendly empty state when no days come back. Experts: a topic text box with suggestion chips (deviation, capa, cold-chain, audit), calling api.getExperts, rendering each expert as a card with name, title, evidence count, topics and the sample source. Both react to role changes through useRole.
Dev 3 (trust components):
You are Dev 3. Build the five trust components with the exact props in PLAN.md section 10.8. ConfidenceBadge: green for high, amber for medium, red for low, with a short label. ConflictBanner: an amber banner per conflict that shows the kind (Conflicting sources or Outdated source), the explanation, the two sources side by side (title, version, date, status, snippet), and the recommendation in bold. IDontKnowCard: a calm neutral card saying the answer was not found with the missing_info text. StalenessTag: a small pill that says Superseded (red) for superseded, Draft (grey) for draft and Current (green) for current. ExpandedTerms: small chips showing abbreviation and expansion. Make each component robust to empty or missing props.
Dev 4 (dashboard):
You are Dev 4. Build components/Dashboard.jsx. Fetch api.getGaps and api.getStats on mount and every time the tab is opened. Show stat cards for total questions, answered, unanswered, conflicts flagged and total minutes saved (labelled as an estimate), a knowledge-gap list (question, times asked, last asked, reason) and a simple horizontal bar chart of asked_count per gap built with plain Tailwind divs (no chart library). Include a refresh button and an empty state that explains gaps appear when questions go unanswered.
11. Demo script (3 minutes) and pitch
Step
Role
Action
Time
1
Analyst (new QA hire)
Open Onboarding and show the 5-day reading path
10 s
2
Analyst
Ask “What temperature should vaccine batches be stored at?” Show the cited answer, the conflict banner (SOP-014 v3 says 2 to 8 °C, the QA head’s email and #cold-chain say 2 to 6 °C) and the superseded SOP-014 v2 flagged
60 s
3
Analyst
Ask “What is the CAPA timeline for an OOS result?” Show the expanded terms and the citation
20 s
4
Intern
Switch role, ask “What recurring deviation did the audit find?” Show the refusal with no leaked citation
30 s
5
Analyst
Ask the HPLC question to get “I don’t know”, then open the Dashboard and show it in the gap list
30 s
6
Analyst
Open Experts, ask for deviation handling, end on the minutes-saved counter
20 s

Pitch lines:
“Search tells you where. Provenance tells you whether to trust it.”
“Connectors are one file each. Swapping in Microsoft Graph is a configuration change, not a redesign.”
“The role filter runs before retrieval and again before the response, so restricted text never reaches the model or the screen.”
Slide: the 5 objectives and 5 outcomes from the brief mapped to features F1 to F10 (§1.2), then the roadmap, then one honest line: role comes from the UI in this demo and from SSO in production.
12. Definition of done, fallbacks and tips
Definition of done
./run.sh starts the backend and the frontend on one laptop.
The 6-step demo runs without errors across all role switches.
With the network off (or USE_MOCK_LLM=1), /ask still returns an extractive answer with citations.
tests/smoke.py proves an intern never receives a manager-only citation.
python -m corpus_gen.validate passes all 7 scenarios and all 12 golden questions behave as in §6.5.
Fallback checklist before the demo: Groq key works on the demo laptop; warm_cache.py has run; the network-off fallback is tested; a 2-minute backup screen recording exists; everything is merged to main by 2:35 with only bug fixes after.
Antigravity tips
Always start in Plan mode, skim the plan, then approve. This stops agents from rewriting files outside your folder.
Use the review setting that asks before installing packages or deleting files. Avoid “always proceed” on a shared repo.
Commit small and often on your own branch; Dev 5 merges.
If an agent changes contracts.py or another dev’s files, revert it with Git immediately.
Antigravity’s free usage has limits. If you run out, paste the same prompt into any free chat assistant and apply the code yourself.
Free-tier limits and model names change: verify them in the Groq console once, then trust .env.
Appendix A. Starter pack (Dev 5 commits these in Phase 0)
Create each file exactly as shown. Empty __init__.py files are needed in app/ and modules/. After Phase 0 each dev replaces only the stub in their own folder, keeping the same exported function names.
A.1 requirements.txt (complete, so nobody edits it)
fastapi
uvicorn[standard]
pydantic>=2
python-dotenv
groq
rank_bm25
pypdf
python-docx
reportlab
requests
httpx
A.2 .env.example
GROQ_API_KEY=
GROQ_MODEL_MAIN=
GROQ_MODEL_FAST=
GEMINI_API_KEY=
USE_MOCK_LLM=1
A.3 .gitignore
.env
.venv/
__pycache__/
*.pyc
node_modules/
frontend/dist/
data/cache/
data/processed/
data/processed/ is ignored during Phase 1 so a sample-built chunks.json can never leak into main. At integration Dev 2 builds from the real corpus and force-adds the files with git add -f data/processed/*.json.
A.4 run.sh
#!/usr/bin/env bash
set -e
uvicorn app.main:app --port 8000 &
BACK=$!
trap 'kill $BACK' EXIT
if [ -f frontend/package.json ]; then
  (cd frontend && npm run dev)
else
  wait $BACK
fi
A.5 app/config.py (single source of paths and mode; nobody else edits it)
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
RAW_DIR = DATA / 'raw'
PROCESSED_DIR = DATA / 'processed'
FIXTURES_DIR = DATA / 'fixtures'
CACHE_DIR = DATA / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def raw_dir() -> Path:
    # Real corpus if Dev 1 has produced it, otherwise Dev 2's sample files.
    if any(RAW_DIR.rglob('*.meta.json')):
        return RAW_DIR
    return FIXTURES_DIR / 'raw_sample'


def chunks_path() -> Path:
    # Real chunks if built, otherwise the frozen fixture.
    real = PROCESSED_DIR / 'chunks.json'
    return real if real.exists() else FIXTURES_DIR / 'chunks_sample.json'


def use_mock_llm() -> bool:
    return os.getenv('USE_MOCK_LLM', '0') == '1'


def llm_mode() -> str:
    if use_mock_llm():
        return 'mock'
    return 'groq' if os.getenv('GROQ_API_KEY') else 'offline'
A.6 app/llm.py (stub, Dev 3 replaces)
def complete_text(prompt: str, system: str = '') -> str:
    return ''


def complete_json(prompt: str, system: str = '') -> dict:
    return {}
A.7 app/main.py (stub, Dev 4 replaces)
import json
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contracts import AskRequest, AskResponse, Expert, GapItem, Health, OnboardingPath, Stats
from app import config
from modules import ingestion, intelligence, retrieval

app = FastAPI(title='Provenance')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/ask', response_model=AskResponse)
def ask(req: AskRequest):
    start = time.time()
    resp = retrieval.answer(req.question, req.role)
    resp.latency_ms = int((time.time() - start) * 1000)
    return resp


@app.get('/onboarding', response_model=OnboardingPath)
def onboarding(job_role: str = 'QA', role: str = 'analyst'):
    return ingestion.onboarding_path(job_role, role)


@app.get('/experts', response_model=list[Expert])
def experts(topic: str = 'deviation', role: str = 'analyst'):
    return ingestion.find_experts(topic, role)


@app.get('/gaps', response_model=list[GapItem])
def gaps():
    return intelligence.gap_report()


@app.get('/stats', response_model=Stats)
def stats():
    return intelligence.get_stats()


@app.get('/health', response_model=Health)
def health():
    path = config.chunks_path()
    try:
        count = len(json.loads(path.read_text(encoding='utf-8')))
    except Exception:
        count = 0
    source = 'real' if path.name == 'chunks.json' else 'fixtures'
    return Health(status='ok', chunks=count, llm=config.llm_mode(), data_source=source)
A.8 modules/ingestion/__init__.py (stub, Dev 2 replaces)
from contracts import Expert, OnboardingPath, ReadingItem, Role


def build_corpus() -> None:
    return None


def find_experts(topic: str, role: Role) -> list[Expert]:
    return [Expert(name='Priya Rao', role='QA Lead', evidence_count=9, topics=['deviation'], sample_source='SOP-001 Deviation Handling')]


def onboarding_path(job_role: str, role: Role) -> OnboardingPath:
    item = ReadingItem(order=1, doc_id='QM-001', title='Quality Manual', why='Start here for the quality system overview', est_minutes=20)
    return OnboardingPath(job_role=job_role, days={'Day 1': [item]})
A.9 modules/retrieval/__init__.py (stub, Dev 3 replaces)
import json
from contracts import AskResponse, Chunk, Citation, Role
from app.config import chunks_path


def _load() -> list[Chunk]:
    return [Chunk(**c) for c in json.loads(chunks_path().read_text(encoding='utf-8'))]


def search(question: str, role: Role, k: int = 8) -> list[Chunk]:
    return [c for c in _load() if role in c.allowed_roles][:k]


def answer(question: str, role: Role) -> AskResponse:
    hits = search(question, role, 2)
    cites = [
        Citation(chunk_id=c.chunk_id, doc_id=c.doc_id, title=c.title, source_type=c.source_type,
                 version=c.version, date=c.date, status=c.status, snippet=c.text[:200], location=c.location)
        for c in hits
    ]
    text = '(stub) ' + hits[0].text + ' [1]' if hits else '(stub) No data.'
    return AskResponse(answer=text, answerable=bool(hits), confidence='low', citations=cites)
A.10 modules/intelligence/__init__.py (stub, Dev 4 replaces)
from contracts import AskRequest, AskResponse, Chunk, Conflict, GapItem, Stats


def detect_conflicts(chunks: list[Chunk]) -> list[Conflict]:
    return []


def log_query(req: AskRequest, resp: AskResponse) -> None:
    return None


def gap_report() -> list[GapItem]:
    return [GapItem(question='How do I calibrate an HPLC column?', asked_count=1, last_asked='2026-10-13', reason='No source found')]


def get_stats() -> Stats:
    return Stats()
A.11 Phase 0 verification (Dev 5)
python -c 'import contracts, app.main'
uvicorn app.main:app --port 8000
curl http://localhost:8000/health
curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' -d '{"question":"vaccine storage","role":"analyst"}'
If every endpoint returns valid JSON, commit to main, push, and tell the team “main is ready”.

