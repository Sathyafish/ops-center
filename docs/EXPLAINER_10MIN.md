# Ops Center GraphRAG — 10-Minute Explainer (plain-language version)

**Timing plan:** Problem (1) → Data (2) → Loading the data (2) → How it answers (2) → How I tested it (1.5) → Demo (1.5)

**Tip:** Each section has a **"Say it simply"** line. Use that for a mixed audience. The technical detail underneath is for when someone asks.

---

## 0. The problem and the idea (1 min)

> When a company system breaks, the support team has to answer four questions fast:
> 1. **Who do I call?**
> 2. **What else will break because of this?**
> 3. **Is someone already changing this system right now?**
> 4. **What steps do I follow to escalate?**
>
> The answers are scattered. Some are **connections between things** (who owns which system, which system relies on which). Others are **written instructions** (runbooks, checklists).
>
> I built a **chat assistant** that you log in to and ask in plain English. It looks up the connections in one place, the written instructions in another, and then an AI writes a clear answer using **only** what it found. If it can't find the answer, it says so instead of guessing.

**Why two places to look?** Think of a company org chart plus a policy handbook.
- The **org chart / map** (graph database) answers "who owns this?" and "what depends on what?"
- The **handbook** (document search) answers "what are the steps to escalate?"

One alone answers only half the questions well, so the assistant uses both. This approach is called **GraphRAG**.

**Jargon cheat-sheet (only if asked)**

| Term | Plain meaning |
|---|---|
| Graph database (Neo4j) | Stores things and the links between them, like a map |
| Vector store (Chroma) | A search tool that finds documents by *meaning*, not exact words |
| Runbook | A step-by-step guide for handling a specific problem |
| LangGraph | The "traffic controller" that decides where to look and in what order |
| LLM (llama3.2:3b via Ollama) | The AI that writes the final answer. It runs on our own server, so no data leaves the company |
| Blast radius | Everything that could be affected if one system fails |
| SME | Subject Matter Expert: the person who knows a system best |

---

## 1. Where the data comes from (2 min)

**Say it simply:** *"The assistant only knows what I gave it: a list of 100 applications with their owners and connections, and a small library of how-to guides."*

| What | In plain words | Where it lives |
|---|---|---|
| **Application list** | 100 applications. For each: what it does, how important it is, who the expert, engineering manager, product manager and director are, and which other apps it relies on | `data/graph/applications_catalog.json` |
| **Runbooks** | About 9 written guides: troubleshooting for key apps, the first-line triage checklist, how to write an escalation report, how to acknowledge a change, how to communicate during a major incident | `data/runbooks/*.md` |
| **Live-incident extras** | Sample "work in progress" info: 3 change tickets (e.g. CR-10482), the escalation levels with their time limits, and who is on call for key apps | `backend/app/graph/seed_catalog.py` |
| **Test questions** | 13 questions with the answers I expect, used to check the assistant works | `eval/golden_dataset.json` |

**Be upfront:** the application list is **sample data I generated**. It stands in for the company's real system inventory (often called a CMDB). The same steps would work with a real export.

---

## 2. How the data gets loaded (2 min)

**Say it simply:** *"Before anyone can ask a question, I load the information into two 'filing cabinets': one for connections, one for written guides. This is done once up front, not every time someone asks."*

### Filing cabinet 1: the connections map (Neo4j)

Steps:
1. **Start with the application list** (a file with 100 apps).
2. **A script reads it** and creates a "dot" for each application, each team and each person.
3. **It draws the lines between dots**, for example:
   - Team *owns* application
   - Person is the *expert / manager / director* for application
   - Application *depends on* application (this is how we know what breaks if something fails)
4. **It adds the live-incident extras**: change tickets, escalation levels, on-call people.
5. **Check:** ask the database "how many applications?" The answer should be **100**.

Result: a map you can follow. From *PaymentGateway* you can walk to its expert, its director, the apps relying on it and any change ticket touching it.

### Filing cabinet 2: the written guides (Chroma)

Steps:
1. **Read** each runbook file.
2. **Clean it up**: remove hidden comments and extra blank lines, and note the title and which application it's about.
3. **Cut it into small pieces** (about 600 characters each, split at headings) so each piece covers one idea. Small pieces are easier to match to a question.
4. **Turn each piece into numbers that capture its meaning** (an "embedding"). Similar meanings get similar numbers, which is how the search later finds relevant pieces even if the words differ.
5. **Store the pieces** in the vector store. Re-loading replaces the old copy, so there are no duplicates.

**Good to know:** when a runbook changes, I re-run the load by hand. A production version would update automatically from the company's systems.

---

## 3. How the assistant answers a question (2 min)

**Say it simply:** *"It works like a good help-desk person: understand the question, look in the right places, then write an answer using only what was found."*

### What the user sees
1. Log in (secure login).
2. Type a question, optionally choosing **Auto**, **Graph only** or **Vector only**.
3. Get an answer, with a note of which source it came from.

### What happens behind the scenes (4 steps)

| Step | Plain description |
|---|---|
| **1. Decide where to look** | Reads the question for clue words. "Who", "depends", "change", "escalate" point to the **connections map**. "How", "steps", "template", "procedure" point to the **written guides**. A mix means use both. |
| **2. Search the map** | Finds the application name in the question and looks up its owners, dependencies, active changes and escalation levels |
| **3. Search the guides** | Finds the 4 pieces of runbook text closest in meaning to the question |
| **4. Write the answer** | The AI gets the question plus what was found and writes a clear answer |

### The safety rule (most important point)
The AI is told: *"Answer ONLY from the information provided. If it isn't there, say you can't find it. Show where each fact came from."* That is why it should refuse a question like "What's our SaaS pricing?" instead of making something up.

### The AI model
- Answers are written by a small AI (**llama3.2:3b**) running on **our own server**, so company data stays in-house.
- It can be swapped for OpenAI with a setting change.
- Trade-off: free and private, but a small model is less polished and can occasionally drift off the facts.

> Accuracy note (for me): in the code, both searches run on every question. The "decide where to look" step controls which results are **given to the AI**. Don't say it skips the other search.

---

## 4. How I tested it (1.5 min)

**Say it simply:** *"I wrote an exam with 13 questions where I already know the right answer, then checked how well the assistant does."*

### The "golden" questions
`eval/golden_dataset.json`. "Golden" means the expected answers are known and trusted. Each question comes with a list of **must-have words** that a good answer has to include (e.g. a person's name or a ticket number).

| Type | How many | Example |
|---|---|---|
| Connections (who / depends on / changes) | 7 | "PaymentGateway is down — who should Ops contact first?" |
| Written procedures | 4 | "What fields are required in an SME L2 escalation report?" |
| Mixed | 1 | "PaymentGateway incident — contacts, dependencies, active change and ack steps" |
| Should refuse | 1 | "What is the pricing model for our SaaS product?" |

### How it's scored
**Score = must-have words found ÷ must-have words expected.** Example: 2 of 3 expected words found → 67%.

Two checks:
1. **Did the search find the right information?** Done separately for the connections map and the written guides, to show which one wins for each question. Fast, and doesn't need the AI.
2. **Did the final answer contain it?** Also checks that the "should refuse" question really is refused.

Run it:
```bash
docker compose exec api python -m app.scripts.run_eval --with-llm --report /tmp/eval_report.json
```

### What I expect the results to show
- Map wins on **who / depends on / change** questions.
- Guides win on **procedure / checklist** questions.
- Mixed questions need both.

### Limits to mention honestly
- It counts keywords. It doesn't judge whether the wording is good.
- 13 questions is a small test.
- The expected answers are based on my sample data.

> **TODO before presenting:** run the eval and put the real numbers here: map wins __ / guides win __ / ties __ / average answer score __. (`docs/comparison_analysis.md` is still a blank template. The 8/4/1 in `PROJECT_DOCUMENT.md` is only an *example*.)

---

## 5. Live demo (1.5 min)

**Say it simply:** *"Four questions: one from the map, one from the guides, one that needs both, and one it should refuse."*

Log in to the UI (demo user is in the README), then:

| # | Mode | Ask | What to point out |
|---|---|---|---|
| 1 | Graph | "Who is the director for SettlementService?" | Matches `applications_reference.csv` |
| 2 | Vector | "What mitigation does the PaymentGateway runbook recommend for 502 during cert rotation?" | Answer comes from the runbook |
| 3 | Auto | "PaymentGateway incident — SME, director, and active change ack ticket" | It used **both** sources |
| 4 | Auto | "What is our SaaS pricing model?" | It **refuses**, so it isn't making things up |

Optional: open the Neo4j Browser (SSH tunnel to :7474) to show the PaymentGateway "map".

---

## 5b. Prompt bank — one example per scenario

All names, tickets and facts below exist in the seeded data. "Expect" = what a correct answer should contain. Pick 1 per scenario for the talk; keep the rest as backup.

### A. Who to contact (owners / people)

| Prompt | Expect |
|---|---|
| PaymentGateway is down — who should Ops contact first? | Alice Chen (SME), Payments Platform, Frank Li (Eng Mgr), Diana Roth (Director) |
| Who is the SME for OrderService? | Bob Martinez, Commerce Core |
| Who is the director for SettlementService? | Diana Roth (same director as PaymentGateway) |
| Who is on call for AuthService? | Carol Okonkwo (primary contact, on-call) |

### B. What else breaks (dependencies / blast radius)

| Prompt | Expect |
|---|---|
| What does OrderService depend on? | PaymentGateway, AuthService, InventoryAPI |
| What applications depend on OrderService and could be impacted? | CustomerPortal, MobileBackend, CheckoutHub, … |
| What is the blast radius if PaymentGateway fails? | BillingEngine, OrderService, SettlementService, … |
| What is the blast radius if AuthService fails? | Very large (91 apps depend on it). Good to show why a map beats text search. The answer may be cut off by the 6000-character limit; say so if it happens |

### C. Is a change in progress? (change tickets)

| Prompt | Expect |
|---|---|
| Are there any in-progress changes affecting PaymentGateway? | CR-10482, TLS cert rotation, IN_PROGRESS, owner Alice Chen, ack ticket OPS-8891 |
| Is anything scheduled on OrderService? | CR-10490, DB index rebuild, SCHEDULED, OPS-8902 |
| Which change ticket should I use to acknowledge the AuthService migration incident? | CR-10477, ack ticket OPS-8875 (also affects CustomerPortal) |
| Which changes affect CustomerPortal? | CR-10477 (via AuthService migration) |

### D. Escalation levels and time limits

| Prompt | Expect |
|---|---|
| What escalation SLA applies at level 2? | Service Owner SME, 30 minutes |
| What are the escalation levels in the Ops Center? | L1 15 min → L2 30 min → L3 Director/Major Incident 60 min |

### E. Steps and procedures (runbooks)

| Prompt | Expect |
|---|---|
| What fields are required in an SME L2 escalation report? | incident_id, severity, timeline, blast_radius, active_change_ids, … |
| Describe the Ops Center L1 triage checklist. | CMDB lookup, 15-minute target, when to escalate to L2 |
| PaymentGateway returns 502 during cert rotation — what mitigation does the runbook recommend? | Fail over to secondary region per DR-12 |
| How do I acknowledge a change that correlates with an incident? | Ack ticket, CR- id, info pulled from the change record |
| When should we engage the Director (L3)? | >10% transactions impacted for 15+ min, Tier-0 SLA breach >30 min, media/exec inquiry |
| How often do we update the status page for a SEV1? | Every 30 minutes |
| What should I do if database connections are timing out? | Scale read replicas, engage DBA if >15 min |

### F. Full incident (needs both sources)

| Prompt | Expect |
|---|---|
| PaymentGateway incident — give contacts, dependencies, and any active change with ack steps. | Alice Chen + Diana Roth, dependency list, CR-10482 / OPS-8891, plus ack procedure from runbook |
| AuthService users are getting logged out — who do I call, is a change running, and what should I check? | Carol Okonkwo, CR-10477 (users re-login once per region), runbook quick checks |
| OrderService is slow — what depends on it, any change in flight, and what does the runbook say? | CR-10490 index rebuild (read latency spike), dependents, OrderService runbook |

### G. Safety checks (it should not make things up)

| Prompt | Expect |
|---|---|
| What is the pricing model for our SaaS product? | Refusal: "cannot find it in the knowledge base" |
| Who is the SME for NonExistentApp? | Should say it can't find it |
| Who should I call? *(no app name)* | Should ask which application you mean |

### H. Same question, three modes

Ask **"PaymentGateway is down — who should Ops contact first?"** in **Graph only**, **Vector only**, then **Auto**.
Expect: Graph gives named contacts; Vector gives only generic runbook text; Auto picks graph. This is the best single slide for "why we need both."

> Tips: the AI's wording changes each time, so check the key facts, not exact phrasing. If an answer looks wrong, check the returned context: if the fact is there, the AI missed it; if not, the search missed it.
> The "Expect" column comes from the seed data and runbooks, not from live runs. Spot-check a few before the talk.

---

## 6. Questions people may ask

| Question | Simple answer |
|---|---|
| Why not just use a normal AI chat? | It doesn't know our systems and may invent answers. This one only uses our data and cites it. |
| Why not search documents only? | Document search finds similar *text*, but can't follow links like "what depends on what". |
| How do you stop it making things up? | Strict instruction to use only the found information, plus a test that checks it refuses unknown questions. |
| Is the question routing smart? | Not yet. It uses keyword clues. A next step is to let the AI decide. |
| Is the data real and up to date? | Sample data, updated by hand. A production version would sync from the company's inventory and ticketing systems. |
| What's the weakest part? | Finding the application name in a question (exact match), and the small AI sometimes drifting from the facts. |
| Is company data safe? | The AI runs on our own server, and the app needs a login. |

---

## Cheat sheet (commands)

| Task | Command |
|---|---|
| Load connections map + runbooks | `docker compose exec api python -m app.scripts.seed_all` |
| Reload runbooks only | `docker compose exec api python -m app.scripts.ingest_runbooks` |
| Check the AI connection | `docker compose exec api python -m app.scripts.diagnose_llm` |
| Run the test | `docker compose exec api python -m app.scripts.run_eval --with-llm --report /tmp/eval_report.json` |

Deeper technical detail: [PROJECT_DOCUMENT.md](PROJECT_DOCUMENT.md)
