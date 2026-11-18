# System Architecture & Threat Model

AegisAgent operates as an inline, fail-closed pre-flight interceptor placed directly between autonomous AI coding agents and the underlying host operating system / git version control system.

```
       [ Autonomous AI Agent ]
 (Claude Code / Antigravity / Codex)
                 │
                 ▼
 ┌────────────────────────────────────────┐
 │        AEGIS INTERCEPTOR GATE          │
 │                                        │
 │  1. Ingestion Quarantine (Input Sanit) │
 │  2. Command Shield (Shell Execution)   │
 │  3. Blast-Radius Engine (Git Diffs)    │
 │  4. Slopsquatting Shield (Deps)        │
 │  5. Topology Auditor (CoT Entropy)     │
 │  6. Honeytoken Engine (Canary Traps)   │
 │  7. Adversarial Ship Gates (Pre-PR)    │
 └───────────────────┬────────────────────┘
                     │ (All Gates Clear)
                     ▼
  [ Host OS Shell & Production Git VCS ]
```

---

## 🔒 The Clean-Room Defense Model

Autonomous coding agents present unique failure modes that traditional static analyzers (like SonarQube or ESLint) fail to address:

1. **Non-Deterministic Execution:** An agent can propose a catastrophic command (`rm -rf /` or `DROP DATABASE`) based on a single hallucinated reasoning step.
2. **Context Poisoning:** Untrusted user input (issues, bug reports, scraping targets) can embed adversarial directives that override agent instructions.
3. **Supply Chain Slopsquatting:** Agents frequently hallucinate plausible package names on PyPI/NPM that threat actors register as trojans.
4. **Cognitive Drift:** Long Chain-of-Thought reasoning can diverge into loops of uncertainty, increasing the probability of error.

AegisAgent is engineered with three core invariants:
- **Zero External Dependencies:** 100% built on the Python standard library. No bloated third-party dependencies that could introduce transitive vulnerabilities.
- **Offline-First:** All checks, AST analyses, HMAC honeytoken verifications, and SQLite ledger operations run completely locally.
- **Fail-Closed:** In `--strict` mode, any detected anomaly immediately exits with a non-zero exit code to halt automated CI/CD runners or agent loops.
