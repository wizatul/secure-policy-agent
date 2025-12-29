import json
import re
from pathlib import Path
import os
import logging

# --------------------------------------------------
# Logger setup
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [POLICY_EXTRACTOR] %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Paths
# --------------------------------------------------
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()

INPUT = WORKSPACE / "merged-copilot-policy.md"
OUTPUT = WORKSPACE / "security-policies" / "policy.json"

# --------------------------------------------------
# Extraction logic
# --------------------------------------------------
def extract_red_flags(markdown: str):
    logger.info("Searching for 'Red flags' section in merged policy")

    match = re.search(
        r"##\s+Red flags.*?(.*?)(\n## |\Z)",
        markdown,
        re.S | re.I,
    )
    if not match:
        logger.warning("No 'Red flags' section found")
        return []

    bullets = re.findall(r"^- (.+)", match.group(1), re.M)
    logger.info("Found %d red-flag bullet points", len(bullets))

    return [b.strip() for b in bullets]

# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    if not INPUT.exists():
        logger.error("Merged policy file not found at %s", INPUT)
        raise RuntimeError(f"Missing merged policy: {INPUT}")

    logger.info("Reading merged policy from %s", INPUT)

    text = INPUT.read_text(encoding="utf-8")
    red_flags = extract_red_flags(text)

    policy = {
        "red_flags": [
            {
                "id": f"policy-red-flag-{i+1}",
                "text": flag,
            }
            for i, flag in enumerate(red_flags)
        ]
    }

    logger.info("Extracted enforceable policy rules:")
    for rf in policy["red_flags"]:
        logger.info("  - %s: %s", rf["id"], rf["text"])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(policy, indent=2), encoding="utf-8")

    logger.info(
        "Policy file written to %s (%d rules)",
        OUTPUT,
        len(policy["red_flags"]),
    )

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    main()
