from pathlib import Path
import os
import logging

# --------------------------------------------------
# Logger setup (simple, CI-friendly)
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [POLICY_MERGER] %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Paths
# --------------------------------------------------
ACTION_PATH = Path(os.environ.get("GITHUB_ACTION_PATH", ".")).resolve()
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()

CENTRAL_POLICY = ACTION_PATH / "policy/copilot-instructions-global.md"
REPO_POLICY = WORKSPACE / "copilot-instructions.md"
MERGED_POLICY = WORKSPACE / "merged-copilot-policy.md"

# --------------------------------------------------
# Merge logic
# --------------------------------------------------
def merge():
    logger.info("Starting policy merge")
    logger.info("GITHUB_ACTION_PATH = %s", ACTION_PATH)
    logger.info("GITHUB_WORKSPACE   = %s", WORKSPACE)

    if not CENTRAL_POLICY.exists():
        logger.error("Central policy NOT found at %s", CENTRAL_POLICY)
        raise RuntimeError(
            f"Central policy not found at {CENTRAL_POLICY}"
        )

    logger.info("Central policy found: %s", CENTRAL_POLICY)

    parts = []
    parts.append(CENTRAL_POLICY.read_text(encoding="utf-8"))

    if REPO_POLICY.exists():
        logger.info("Repository policy found: %s", REPO_POLICY)
        logger.info("Including repository-specific policy additions")
        parts.append("\n\n---\n\n## Repository-specific additions\n")
        parts.append(REPO_POLICY.read_text(encoding="utf-8"))
    else:
        logger.info("No repository-specific policy found (this is OK)")

    MERGED_POLICY.write_text("\n".join(parts), encoding="utf-8")

    logger.info("Merged policy written to %s", MERGED_POLICY)
    logger.info(
        "Policy merge completed (sources: central%s)",
        " + repo" if REPO_POLICY.exists() else ""
    )

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    merge()
