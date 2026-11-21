"""
Automated GitHub Wiki Synchronizer for AegisAgent.
Pushes all documentation pages from docs/wiki/ into dhaulagani/aegis-agent.wiki.git.
"""

import os
import shutil
import subprocess
import sys
import tempfile

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_WIKI_DIR = os.path.join(ROOT_DIR, "docs", "wiki")


def get_wiki_url():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return f"https://x-access-token:{token}@github.com/dhaulagani/aegis-agent.wiki.git"
    return "https://github.com/dhaulagani/aegis-agent.wiki.git"


def sync_wiki():
    wiki_url = get_wiki_url()
    print("[*] Checking GitHub Wiki repository status...")
    ls_res = subprocess.run(["git", "ls-remote", wiki_url], capture_output=True, text=True)
    if ls_res.returncode != 0:
        print("[!] GitHub Wiki repository is not yet initialized on GitHub servers.")
        print("[!] On GitHub, the wiki bare repository is created when you click 'Create the first page' on https://github.com/dhaulagani/aegis-agent/wiki.")
        return False

    print("[+] Wiki repository found! Cloning and syncing documentation pages...")
    with tempfile.TemporaryDirectory(prefix="aegis_wiki_") as tmp_dir:
        clone_res = subprocess.run(["git", "clone", wiki_url, tmp_dir], capture_output=True, text=True)
        if clone_res.returncode != 0:
            print(f"[!] Clone failed: {clone_res.stderr}")
            return False

        # Copy all markdown files
        wiki_files = [f for f in os.listdir(DOCS_WIKI_DIR) if f.endswith(".md")]
        for wf in wiki_files:
            src = os.path.join(DOCS_WIKI_DIR, wf)
            dst = os.path.join(tmp_dir, wf)
            shutil.copy2(src, dst)
            print(f"  [+] Synced: {wf}")

        # Git commit & push
        subprocess.run(["git", "config", "user.name", "dhaulagani"], cwd=tmp_dir, check=True)
        subprocess.run(["git", "config", "user.email", "61548549+dhaulagani@users.noreply.github.com"], cwd=tmp_dir, check=True)
        subprocess.run(["git", "add", "."], cwd=tmp_dir, check=True)

        status_res = subprocess.run(["git", "status", "--porcelain"], cwd=tmp_dir, capture_output=True, text=True)
        if not status_res.stdout.strip():
            print("[v] Wiki is already up-to-date with docs/wiki/. No changes needed.")
            return True

        subprocess.run(["git", "commit", "-m", "docs(wiki): sync full documentation suite from docs/wiki/`n`nSigned-off-by: dhaulagani <61548549+dhaulagani@users.noreply.github.com>"], cwd=tmp_dir, check=True)
        push_res = subprocess.run(["git", "push", "origin", "master"], cwd=tmp_dir, capture_output=True, text=True)
        if push_res.returncode != 0:
            push_res = subprocess.run(["git", "push", "origin", "main"], cwd=tmp_dir, capture_output=True, text=True)

        if push_res.returncode == 0:
            print("[v] Successfully synchronized all pages to GitHub Wiki!")
            return True
        else:
            print(f"[!] Push failed: {push_res.stderr}")
            return False


if __name__ == "__main__":
    success = sync_wiki()
    sys.exit(0 if success else 1)
