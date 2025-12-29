import json
import re
from pathlib import Path
import os

WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()

INPUT = WORKSPACE / "merged-copilot-policy.md"
OUTPUT = WORKSPACE / "security-policies" / "policy.json"

def extract_red_flags(markdown: str):
    match = re.search(
        r"##\s+Red flags.*?(.*?)(\n## |\Z)",
        markdown,
        re.S | re.I,
    )
    if not match:
        return []

    bullets = re.findall(r"^- (.+)", match.group(1), re.M)
    return [b.strip() for b in bullets]

def main():
    if not INPUT.exists():
        raise RuntimeError(f"Missing merged policy: {INPUT}")

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

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(policy, indent=2), encoding="utf-8")

    print(f"[OK] extracted {len(red_flags)} red flags")

if __name__ == "__main__":
    main()
