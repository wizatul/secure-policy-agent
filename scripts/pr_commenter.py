import json
import os
from github import Github
from pathlib import Path

WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()
RESULTS = WORKSPACE / "semgrep-results.json"

def main():
    if not RESULTS.exists():
        print("[OK] no semgrep results")
        return

    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    findings = data.get("results", [])

    if not findings:
        print("[OK] no violations")
        return

    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])
    pr = repo.get_pull(int(os.environ["PR_NUMBER"]))

    body = "🚨 **Security policy violations detected**\n\n"

    for f in findings:
        body += (
            f"- **{f['check_id']}**\n"
            f"  > {f['extra']['message']}\n"
            f"  File: `{f['path']}:{f['start']['line']}`\n\n"
        )

    pr.create_issue_comment(body)
    print("[OK] PR comment created")

if __name__ == "__main__":
    main()
