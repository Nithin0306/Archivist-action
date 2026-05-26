# 🏛️ Archivist: Autonomous Architecture Governance Engine

> An event-driven, AI-native Staff Engineer that enforces plain-text Architecture Decision Records (ADRs) directly on GitHub Pull Requests.

## 📖 The Problem: Architectural Drift
Engineering teams spend weeks defining system boundaries in Notion, Google Docs, or Markdown files (e.g., *"Frontend components must never connect directly to the database"*). However, developers don't memorize 50 pages of documentation. Slowly, the codebase degrades into spaghetti code. 

Standard CI/CD tools (like ESLint) rely on **static analysis** and regex—they can catch syntax errors, but they cannot enforce **semantic architectural boundaries**.

## 🚀 The Solution
**Archivist** is a drop-in GitHub Action that acts as an automated Staff Engineer. It reads your Pull Requests, dynamically fetches relevant architectural rules via **Model Context Protocol (MCP)** integrations, semantically evaluates the code using an LLM, and blocks the merge button if a violation occurs. 

By operating entirely within GitHub Actions, Archivist requires zero external servers, webhooks, or infrastructure to maintain.

---

## 🛠️ Tech Stack & Architecture

- **Execution:** **GitHub Actions** (Zero-infrastructure, Docker-based execution).
- **Orchestration:** Python + **LangGraph** (Stateful, multi-agent workflow management).
- **LLM:** **Google Gemini 1.5 Pro** (Massive context window for reading large PR diffs and multiple ADR documents).
- **Integrations:** **Model Context Protocol (MCP)** (Safely fetches data from Notion, Google Docs, and Local Markdown).
- **Version Control:** GitHub API (Automated PR reviews and Commit Status checks).

---

## 📦 Quick Start: Add Archivist to your Repo

You can add Archivist to any repository in under two minutes.

**1. Add your API Key**
Go to your repository's **Settings > Secrets and variables > Actions** and add a new secret:
* `GEMINI_API_KEY`: Your Google Gemini API Key.

**2. Add your Rules**
Create an `ADR/` folder in the root of your repository and add your architectural rules as simple `.md` files.

**3. Create the Workflow**
Add the following file to `.github/workflows/archivist.yml`:

```yaml
name: Archivist Architecture Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  archivist-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        
      - name: Run Archivist AI
        uses: your-username/archivist-action@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
          # Optional: Add Notion or Google Docs tokens here!

          # notion_token: ${{ secrets.NOTION_TOKEN }}
          # notion_db_id: ${{ secrets.NOTION_DB_ID }}
          # gdocs_folder_id: ${{ secrets.GDOCS_FOLDER_ID }}
```
## ⚙️ The Agentic Workflow (Vertical Slice)

Archivist uses a stateful LangGraph pipeline to execute a multi-step reasoning chain:

1. **Ingestion:** A developer opens or updates a Pull Request. The **GitHub Action** automatically spins up a secure, isolated runner and initializes the LangGraph `StateGraph`.
2. **Metadata Matcher:** Evaluates the quality of the PR title and description. It dynamically routes the graph to a lightweight **Fast Path** for well-documented PRs, or forces a **Deep Path** to pull the raw code diff if the description is vague.
3. **Context Agent:** Analyzes the PR context (and full code diff, if on the Deep Path) to identify the specific architectural domains being modified (e.g., "Frontend", "Database", "CI/CD").
4. **Knowledge Agent:** Queries the **Knowledge Base Router** (seamlessly checking Local Markdown, Notion, and Google Docs) to retrieve *only* the Architecture Decision Records (ADRs) relevant to those exact domains.
5. **Evaluation Agent:** The LLM cross-references the code changes against the plain-text architectural rules. If the code complies, it uses the GitHub API to set a passing (green) status check on the commit.
6. **Handoff:** If a violation is found, Archivist posts a detailed markdown comment on the PR outlining the breach, and forces a failed (red) status check to explicitly block the merge button.

---
