# Package Hallucination & Slopsquatting Shield (`aegis deps`)

AI coding agents often hallucinate library package names. Malicious threat actors monitor LLM hallucination patterns and register these non-existent packages on PyPI or NPM (a technique known as **AI Slopsquatting**).

---

## 🛡️ Detection Algorithms

AegisAgent executes dual-layer heuristics against dependency manifests (`requirements.txt`, `package.json`, `pyproject.toml`):

1. **Damerau-Levenshtein Edit Distance ($\le 1$):**
   - Catches single-character typos, swaps, and omissions from the top 50+ canonical packages (e.g., `reqeusts` $\to$ `requests`, `cryptograhpy` $\to$ `cryptography`).
2. **Synthetic LLM Pattern Recognition:**
   - Detects common compound suffixes hallucinated by LLMs: `-python`, `-sdk`, `-official`, `-api`, `-client` (e.g., `requests-python`, `openai-sdk-official`).
3. **Major Version Increments:**
   - Identifies non-existent major version package forks (e.g., `boto4` instead of `boto3`).

---

## 💻 CLI Usage

```bash
# Scan requirements.txt:
aegis deps requirements.txt

# Scan package.json:
aegis deps package.json --strict

# Machine-readable JSON output:
aegis deps requirements.txt --json
```
