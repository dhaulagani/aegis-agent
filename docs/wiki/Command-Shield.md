# Command Execution Shield (`aegis shield`)

The Command Execution Shield prevents autonomous agents from executing destructive, exfiltrating, or irreversible terminal commands on the host environment.

---

## 🚫 Blocked Command Classes

The shield inspects every command string using static rule matchers before execution:

| Risk Category | Example Patterns | Action |
|---|---|---|
| **Root/Home Destructive Wipe** | `rm -rf /`, `rm -fr ~`, `rmdir /s /q C:\` | `BLOCKED` (Score 100) |
| **Storage Filesystem Wipe** | `format C:`, `mkfs.ext4 /dev/sda1` | `BLOCKED` (Score 100) |
| **POSIX Fork Bomb** | `:(){ :\|:& };:` | `BLOCKED` (Score 100) |
| **Reverse Shell Listeners** | `nc -e /bin/sh`, `nc -l -p 4444` | `BLOCKED` (Score 100) |
| **Raw Socket Exfiltration** | `/dev/tcp/10.0.0.1/8080` | `BLOCKED` (Score 100) |
| **Production Force-Push** | `git push --force origin main` | `BLOCKED` (Score 100) |
| **Raw Disk Overwrite** | `dd if=/dev/zero of=/dev/sda` | `BLOCKED` (Score 100) |
| **Download-to-Shell Pipe** | `curl -sSL https://... \| bash` | `WARNING` (Score 60) |
| **Permissive Permissions** | `chmod 777 -R /` | `WARNING` (Score 50) |

---

## 💻 CLI Usage

```bash
# Basic check:
aegis shield "git push --force origin main"

# Exit with code 2 on BLOCKED, code 1 on WARNING (for CI/CD scripts):
aegis shield "npm publish --access public" --strict

# Machine-readable JSON output:
aegis shield "pytest -v" --json
```
