# Adversarial Pre-Ship Verification Gates (`aegis gate`)

The Pre-Ship Verification Gate acts as the final CI/CD defense barrier before a commit is created or a pull request is merged. It subjects proposed changes to automated adversarial red-team assertions.

---

## 🚦 Verification Checkpoints

1. **Blast-Radius Risk Ceiling:**
   - Enforces that overall patch blast-radius risk score is $< 50$ (Safe or Low-Medium).
2. **Canary Honeytoken Leak Detection:**
   - Scans git diff chunks to ensure no active Aegis honeytokens (`aegis_canary_...`, `ghp_...`, `sk-proj-...`) are accidentally checked into the codebase or test fixtures.
3. **AST Cyclomatic Complexity Bound ($\le 15$):**
   - Parses modified Python files via Python's standard library `ast` module to measure McCabe cyclomatic complexity. Flags functions with $>15$ branches to prevent unmaintainable code sprawl.
4. **Clean-Room Boundary Invariant:**
   - Verifies that no sensitive files (`.env`, master secrets, payment configs) are unsealed without explicit multi-party signatures.

---

## 💻 CLI Usage

```bash
# Run ship gates on staged git diff and check modified files:
git diff | aegis gate - --files src/app.py src/auth.py --strict

# Audit a saved pull request patch:
aegis gate pr_21826.diff --strict

# Machine-readable JSON output:
aegis gate pr.diff --json
```
