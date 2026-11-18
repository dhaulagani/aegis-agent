# Molecular CoT Reasoning Topology (`aegis topology`)

Based on groundbreaking research from ByteDance Seed, Harbin Institute of Technology, and Peking University (**[arXiv:2601.06002](https://arxiv.org/abs/2601.06002)**: *"The Molecular Structure of Thought: Mapping the Topology of Long Chain-of-Thought Reasoning"*).

---

## 🧬 Chemical Bond Typology in LLM Reasoning

Effective Long Chain-of-Thought (CoT) trajectories behave like stable molecular structures formed by three interaction types:

| Bond Type | Behavioral Analogy | Optimal Ratio | Function |
|---|---|---|---|
| **Covalent Bonds** | **Deep-Reasoning** | **60% – 75%** | High-energy, directed deductive backbone ($S_t \implies S_{t+1}$). Direct logical proof. |
| **Hydrogen Bonds** | **Self-Reflection** | **15% – 25%** | Long-range retro-folding interactions. Verifies and constrains earlier premises before final execution. |
| **Van der Waals** | **Self-Exploration** | **10% – 20%** | Transient, weak bridges testing alternative hypothesis branches before collapsing uncertainty into the backbone. |

---

## ⚖️ Semantic Isomers & Entropy Convergence

Not all reasoning paths are equal. AegisAgent evaluates the sequence for monotonic Shannon entropy reduction:

- **`STABLE_CONVERGENT`**: The optimal configuration. Uncertainty steadily decreases toward zero at the conclusion.
- **`UNSTABLE_EXPLORATION`**: Excessive Van der Waals exploration (>35%). High risk of cognitive drift and hallucinations.
- **`RIGID_DEDUCTION`**: Zero or minimal Hydrogen bonds (<8%). Blind execution of potentially false premises without verification checks.
- **`NEUROTIC_REFLECTION`**: Excessive backtrack loops (>35%). Wastes context window and leads to hesitation thrashing.

---

## 💻 CLI Usage

```bash
# Analyze saved agent reasoning log:
aegis topology reasoning_trace.log

# Pipe directly from agent execution stream:
cat trace.txt | aegis topology - --strict

# Machine-readable JSON output:
aegis topology trace.txt --json
```
