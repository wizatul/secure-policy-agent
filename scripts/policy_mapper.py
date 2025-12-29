import json
import yaml
from pathlib import Path
import os
import logging

# --------------------------------------------------
# Logger setup
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [POLICY_MAPPER] %(message)s"
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Paths
# --------------------------------------------------
ACTION_PATH = Path(os.environ.get("GITHUB_ACTION_PATH", ".")).resolve()
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()

POLICY_FILE = WORKSPACE / "security-policies" / "policy.json"
MAPPING_FILE = ACTION_PATH / "mappings" / "semgrep-mapping.yaml"
OUTPUT_FILE = WORKSPACE / "security-policies" / "semgrep.yaml"

VALID_SEVERITIES = {"ERROR", "WARNING", "INFO"}

# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    logger.info("Starting policy → Semgrep mapping")
    logger.info("Policy file   : %s", POLICY_FILE)
    logger.info("Mapping file  : %s", MAPPING_FILE)
    logger.info("Output file   : %s", OUTPUT_FILE)

    if not POLICY_FILE.exists():
        logger.error("policy.json not found")
        raise RuntimeError("policy.json not found")

    if not MAPPING_FILE.exists():
        logger.error("semgrep-mapping.yaml not found")
        raise RuntimeError("semgrep-mapping.yaml not found")

    policy = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
    mappings = yaml.safe_load(MAPPING_FILE.read_text(encoding="utf-8")) or {}

    policy_ids = [rf["id"] for rf in policy.get("red_flags", [])]
    mapping_ids = list(mappings.keys())

    logger.info("Policy rules discovered:")
    for pid in policy_ids:
        logger.info("  - %s", pid)

    logger.info("Available Semgrep mappings:")
    for mid in mapping_ids:
        logger.info("  - %s", mid)

    rules = []
    skipped = 0  # ✅ track downgraded rules

    for red_flag in policy["red_flags"]:
        rule_id = red_flag["id"]
        rule_text = red_flag["text"]

        logger.info("Processing policy rule %s", rule_id)

        # --------------------------------------------------
        # Skip explicitly non-enforceable rules
        # --------------------------------------------------
        if not red_flag.get("enforce", True):
            logger.info(
                "Skipping enforcement for local-only rule %s",
                rule_id,
            )
            skipped += 1
            continue

        # --------------------------------------------------
        # Missing mapping → downgrade to local-only
        # --------------------------------------------------
        if rule_id not in mappings:
            logger.warning(
                "No Semgrep mapping found for rule %s. "
                "Automatically treating as local-only (not enforced).",
                rule_id,
            )
            logger.warning("Policy text: %s", rule_text)

            red_flag["enforce"] = False
            red_flag["scope"] = "local-only"
            skipped += 1
            continue

        mapping = mappings[rule_id]

        severity = mapping.get("severity")
        if severity not in VALID_SEVERITIES:
            logger.error(
                "Invalid severity for rule %s: %s",
                rule_id,
                severity,
            )
            raise ValueError(
                f"Rule {rule_id} has invalid or missing severity: {severity}"
            )

        rule = {
            "id": rule_id,
            "message": rule_text,
            "languages": mapping["languages"],
            "severity": severity,
        }

        # Copy detection logic explicitly
        copied_keys = []
        for key in ("pattern", "pattern-regex", "patterns"):
            if key in mapping:
                rule[key] = mapping[key]
                copied_keys.append(key)

        logger.info(
            "Enforced %s → severity=%s, languages=%s, detectors=%s",
            rule_id,
            severity,
            mapping["languages"],
            copied_keys,
        )

        rules.append(rule)

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(
        yaml.safe_dump({"rules": rules}, sort_keys=False),
        encoding="utf-8",
    )

    logger.info(
        "Semgrep rules generated successfully (%d enforced, %d skipped)",
        len(rules),
        skipped,
    )

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------
if __name__ == "__main__":
    main()
