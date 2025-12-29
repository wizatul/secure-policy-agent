import json
import os
import logging
from github import Github
from pathlib import Path

# --------------------------------------------------
# Logger setup
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [PR_COMMENTER] %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Paths
# --------------------------------------------------
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()
RESULTS = WORKSPACE / "semgrep-results.json"

# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    logger.info("Starting PR commenter")

    if not RESULTS.exists():
        logger.info("No semgrep results found – skipping comment")
        return

    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    findings = data.get("results", [])

    logger.info("Total raw findings: %d", len(findings))

    if not findings:
        logger.info("No violations detected")
        return

    if not os.getenv("PR_NUMBER"):
        logger.error("PR_NUMBER missing – cannot comment")
        return

    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])
    pr = repo.get_pull(int(os.environ["PR_NUMBER"]))

    body = "🚨 **Security policy violations detected**\n\n"

    seen = set()
    added = 0

    for f in findings:
        rule_id = f.get("check_id")
        path = f.get("path")
        line = f.get("start", {}).get("line")
        message = f.get("extra", {}).get("message")

        dedup_key = (rule_id, path, line)

        if dedup_key in seen:
            logger.info(
                "Skipping duplicate finding: %s (%s:%s)",
                rule_id,
                path,
                line,
            )
            continue

        seen.add(dedup_key)
        added += 1

        logger.info(
            "Adding finding: %s (%s:%s)",
            rule_id,
            path,
            line,
        )

        body += (
            f"- **{rule_id}**\n"
            f"  > {message}\n"
            f"  File: `{path}:{line}`\n\n"
        )

    if added == 0:
        logger.info("All findings were duplicates – no comment created")
        return

    pr.create_issue_comment(body)
    logger.info("PR comment created with %d unique findings", added)

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    main()
