import json
import os
import logging
import hashlib
from github import Github
from pathlib import Path

# --------------------------------------------------
# Logger
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [PR_COMMENTER] %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Constants
# --------------------------------------------------
MARKER = "<!-- SECURE-POLICY-AGENT -->"

# --------------------------------------------------
# Paths
# --------------------------------------------------
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()
RESULTS = WORKSPACE / "semgrep-results.json"

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    logger.info("Starting PR commenter")

    if not RESULTS.exists():
        logger.info("No semgrep results found – skipping")
        return

    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    findings = data.get("results", [])

    if not findings:
        logger.info("No violations detected – skipping")
        return

    if not os.getenv("PR_NUMBER"):
        logger.error("PR_NUMBER missing – cannot comment")
        return

    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])
    pr = repo.get_pull(int(os.environ["PR_NUMBER"]))

    # --------------------------------------------------
    # Deduplicate findings using Semgrep fingerprint
    # --------------------------------------------------
    seen = set()
    entries = []

    for f in findings:
        fingerprint = f.get("fingerprint")
        if not fingerprint:
            fingerprint = f"{f.get('check_id')}:{f.get('path')}:{f.get('start', {}).get('line')}"

        if fingerprint in seen:
            continue

        seen.add(fingerprint)

        entries.append(
            f"- **{f['check_id']}**\n"
            f"  > {f['extra']['message']}\n"
            f"  File: `{f['path']}:{f['start']['line']}`\n"
        )

    if not entries:
        logger.info("All findings were duplicates – skipping")
        return

    core_body = "\n".join(entries)
    content_hash = compute_hash(core_body)

    body = (
        f"{MARKER}\n"
        f"🚨 **Security policy violations detected**\n\n"
        f"{core_body}\n"
        f"<!-- HASH:{content_hash} -->"
    )

    # --------------------------------------------------
    # Find existing comment
    # --------------------------------------------------
    existing_comment = None
    existing_hash = None

    for comment in pr.get_issue_comments():
        if MARKER in comment.body:
            existing_comment = comment
            for line in comment.body.splitlines():
                if line.startswith("<!-- HASH:"):
                    existing_hash = line.replace("<!-- HASH:", "").replace(" -->", "")
            break

    # --------------------------------------------------
    # Idempotent decision
    # --------------------------------------------------
    if existing_comment and existing_hash == content_hash:
        logger.info("No change in violations – not updating comment")
        return

    if existing_comment:
        logger.info("Updating existing security policy comment")
        existing_comment.edit(body)
    else:
        logger.info("Creating new security policy comment")
        pr.create_issue_comment(body)

    logger.info("PR comment operation completed")

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    main()
