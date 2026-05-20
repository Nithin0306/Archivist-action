# 🏛️ Archivist: Autonomous Architecture Governance Engine

> An event-driven, AI-native orchestrator that enforces plain-text Architecture Decision Records (ADRs) directly on GitHub Pull Requests.

## 📖 The Problem: Architectural Drift
Engineering teams spend weeks defining system boundaries in Notion or markdown files (e.g., *"Frontend components must never connect directly to the database"* or *"Do not use `localStorage` for session tokens"*). However, developers don't memorize 50 pages of documentation. Slowly, the codebase degrades into spaghetti code. 

Standard CI/CD tools (like ESLint or Husky) rely on **static analysis** and regex—they can catch syntax errors, but they cannot enforce **semantic architectural boundaries**.

## 🚀 The Solution
**Archivist** acts as an automated Staff Engineer. It listens to GitHub Webhooks, dynamically fetches the relevant architectural rules via the **Model Context Protocol (MCP)**, semantically evaluates the PR diff using an LLM, and posts a Traceability Report directly on GitHub. 

By keeping the application **headless and event-driven**, the AI integrates seamlessly into the developer's existing workflow without requiring a custom UI dashboard.

---

## 🛠️ Tech Stack & Architecture

- **Orchestration:** Python + **LangGraph** (Stateful, multi-agent workflow management).
- **LLM:** **Google Gemini 1.5 Pro** (Chosen for its massive context window, capable of reading large PR diffs and multiple ADR documents simultaneously).
- **Integrations:** **Model Context Protocol (MCP)** Python SDK (Decouples the LLM from the data sources for zero-trust security).
- **Version Control:** GitHub API (Webhook listener & PR comment generation).
- **Knowledge Base:** Notion API / Local Markdown (Dynamic RAG via MCP).

---

## ⚙️ The Agentic Workflow (Vertical Slice)

Archivist uses a stateful LangGraph pipeline to execute a multi-step reasoning chain:

1. **Ingestion:** A developer opens a Pull Request. A GitHub webhook triggers the LangGraph `StateGraph`.
2. **Context Agent:** Uses the **GitHub MCP Server** to securely read the PR's file paths and code diffs.
3. **Knowledge Agent:** Uses the **Notion/Markdown MCP Server** to perform semantic retrieval, fetching *only* the Architecture Decision Records (ADRs) relevant to the modified files.
4. **Evaluation Agent:** The LLM cross-references the code against the plain-text architectural rules.
5. **Handoff:** If a violation is found, Archivist posts a comment on the PR detailing the architectural breach, linking to the specific ADR, and suggesting a refactor.

---

## 🧠 Architectural Decisions & Trade-offs

### 1. Why Model Context Protocol (MCP)?
**Security and Decoupling.** Instead of hardcoding API requests into the LangGraph nodes or giving the LLM raw API keys, Archivist uses MCP Servers. The AI only has access to a sandboxed `get_pr_diff` or `search_adrs` tool. This ensures the LLM cannot accidentally delete a repository or overwrite a database.

### 2. Why LangGraph instead of a single prompt?
**State Management and Traceability.** Dumping 50 pages of ADRs and a massive code diff into a single system prompt leads to hallucinations and lost context. LangGraph allows the system to store intermediate outputs in a `TypedDict` state. The agent fetches the code, *then* fetches the rules, *then* evaluates. 

### 3. Why Headless (No React/Next.js Frontend)?
**Developer Empathy.** The best developer tool is one that doesn't require developers to leave their terminal or GitHub. By using an event-driven webhook architecture, Archivist operates entirely in the background, treating the GitHub PR timeline as its UI.

