# 🛡️ Welcome to the AegisAgent Wiki

Welcome to the official documentation and wiki for **AegisAgent**, the autonomous AI coding agent safety, blast-radius auditor, and hallucination shield.

AegisAgent is a hermetic, zero-dependency, pure-Python defense gate designed to sandbox and audit autonomous coding agents (Claude Code, Antigravity, Devin, Aider, Cursor, and custom LLM workflows) before they execute commands, apply git patches, or ingest untrusted instructions.

---

## 🧭 Wiki Table of Contents

| Section | Topic | Description |
|---|---|---|
| **[System Architecture](Architecture)** | Theoretical & System Topology | Deep dive into the clean-room interceptor design and threat model. |
| **[Command Execution Shield](Command-Shield)** | Pre-Flight Shell Guard | Blocking destructive disk wipes, reverse shells, and force-pushes. |
| **[Blast-Radius Engine](Blast-Radius-Engine)** | Patch Risk Analysis | Quantitative 0–100 scoring, sensitive file touches, and credential leaks. |
| **[Package Hallucination Shield](Package-Hallucination-Shield)** | Slopsquatting Protection | Damerau-Levenshtein distance and LLM synthetic dependency detection. |
| **[Molecular CoT Reasoning](Molecular-CoT-Reasoning)** | arXiv:2601.06002 Topology | Covalent, Hydrogen, and Van der Waals bonds; entropy convergence. |
| **[Prompt Injection Quarantine](Prompt-Injection-Quarantine)** | Context Sanitization | Neutralizing indirect injections, hidden HTML, and zero-width steganography. |
| **[Incident & Reputation Ledger](Incident-Ledger-Reputation)** | Embedded SQLite Audit | Persistent audit trail and 0–100 agent trust scoring engine. |
| **[Adversarial Pre-Ship Gates](Adversarial-Ship-Gates)** | CI/CD Quality Gates | AST cyclomatic complexity ($\le 15$), canary leak checks, and blast limits. |
| **[Model Context Protocol (MCP)](Model-Context-Protocol-MCP)** | Native Agent Integration | JSON-RPC 2.0 server setup for Claude Code, Antigravity, Cursor, and Codex. |

---

## ⚡ Quick Start

### Installation
```bash
git clone https://github.com/dhaulagani/aegis-agent.git
cd aegis-agent
pip install -e .
```

### 1-Line Sanity Check
```bash
aegis shield "git push --force origin main"
```

---

*Authored by [@dhaulagani](https://github.com/dhaulagani) • Distributed under MIT License*
