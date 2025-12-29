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

    # Environment diagnostics
    logger.info("Environment variables:")
    for key in ["GITHUB_TOKEN", "GITHUB_REPOSITORY", "PR_NUMBER", "GITHUB_EVENT_NAME"]:
        value = os.getenv(key)
        logger.info("  %s = %s", key, "SET" if value else "MISSING")

    if not RESULTS.exists():
        logger.warning("semgrep-results.json not found at %s", RESULTS)
        logger.info("Nothing to comment on")
        return

    logger.info("Reading Semgrep results from %s", RESULTS)
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    findings = data.get("results", [])

    logger.info("Total findings: %d", len(findings))

    if not findings:
        logger.info("No policy violations detected")
        return

    if not os.getenv("PR_NUMBER"):
        logger.error("PR_NUMBER is missing – cannot post PR comment")
        return

    if not os.getenv("GITHUB_TOKEN"):
        logger.error("GITHUB_TOKEN is missing – cannot authenticate to GitHub")
        return

    repo_name = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])

    logger.info("Target repository: %s", repo_name)
    logger.info("Target PR number : %d", pr_number)

    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    body = "🚨 **Security policy violations detected**\n\n"

    for f in findings:
        rule_id = f.get("check_id")
        message = f.get("extra", {}).get("message")
        path = f.get("path")
        line = f.get("start", {}).get("line")

        logger.info(
            "Adding violation to comment: %s (%s:%s)",
            rule_id,
            path,
            line,
        )

        body += (
            f"- **{rule_id}**\n"
            f"  > {message}\n"
            f"  File: `{path}:{line}`\n\n"
        )

    pr.create_issue_comment(body)
    logger.info("PR comment successfully created")

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    main()
