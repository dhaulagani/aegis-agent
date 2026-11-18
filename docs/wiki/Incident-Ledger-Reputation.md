# Persistent Incident & Agent Reputation Ledger (`aegis ledger`)

AegisAgent maintains an embedded, zero-dependency SQLite audit trail (`~/.aegis/ledger.db`) recording all security events, blocked commands, and violations over time.

---

## 📊 Agent Trust Score Formulation

Every agent starts with a baseline Trust Score of **100/100**. Violations deduct points based on severity:

$$\text{Trust Score} = \max\Big(0, \, 100 - (25 \times N_{\text{CRITICAL}} + 10 \times N_{\text{HIGH}} + 4 \times N_{\text{MEDIUM}} + 1 \times N_{\text{LOW}})\Big)$$

| Trust Bracket | Rating | Status |
|---|---|---|
| **85 – 100** | Highly Trusted | Autonomous operations approved |
| **60 – 84** | Supervised | Human confirmation recommended for high-risk actions |
| **0 – 59** | Untrusted / High Risk | Autonomous execution halted; manual review mandatory |

---

## 💻 CLI Usage

```bash
# View overall ledger summary and recent incidents:
aegis ledger

# Filter reputation metrics for a specific agent:
aegis ledger --agent claude-code

# Increase number of recent incidents displayed:
aegis ledger --limit 25

# Machine-readable JSON output:
aegis ledger --json
```
