import json
import yaml
from pathlib import Path
import os

ACTION_PATH = Path(os.environ.get("GITHUB_ACTION_PATH", ".")).resolve()
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()

POLICY_FILE = WORKSPACE / "security-policies" / "policy.json"
MAPPING_FILE = ACTION_PATH / "mappings" / "semgrep-mapping.yaml"
OUTPUT_FILE = WORKSPACE / "security-policies" / "semgrep.yaml"


VALID_SEVERITIES = {"ERROR", "WARNING", "INFO"}

def main():
    if not POLICY_FILE.exists():
        raise RuntimeError("policy.json not found")

    if not MAPPING_FILE.exists():
        raise RuntimeError("semgrep-mapping.yaml not found")
    
    policy = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
    mappings = yaml.safe_load(MAPPING_FILE.read_text(encoding="utf-8"))

    rules = []

    for red_flag in policy["red_flags"]:
        rule_id = red_flag["id"]

        if rule_id not in mappings:
            raise ValueError(f"No Semgrep mapping found for rule id: {rule_id}")

        mapping = mappings[rule_id]

        # 🔒 Enforce Semgrep schema
        severity = mapping.get("severity")
        if severity not in VALID_SEVERITIES:
            raise ValueError(
                f"Rule {rule_id} has invalid or missing severity: {severity}"
            )

        rule = {
            "id": rule_id,
            "message": red_flag["text"],
            "languages": mapping["languages"],
            "severity": severity,
        }

        # Copy detection logic explicitly
        for key in ("pattern", "pattern-regex", "patterns"):
            if key in mapping:
                rule[key] = mapping[key]

        rules.append(rule)

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(
        yaml.safe_dump({"rules": rules}, sort_keys=False),
        encoding="utf-8",
    )

    print(f"[OK] generated {len(rules)} Semgrep rules")

if __name__ == "__main__":
    main()
