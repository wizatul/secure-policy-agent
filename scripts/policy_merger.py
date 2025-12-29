from pathlib import Path
import os

ACTION_PATH = Path(os.environ.get("GITHUB_ACTION_PATH", ".")).resolve()
WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", ".")).resolve()

CENTRAL_POLICY = ACTION_PATH / "copilot-instructions.md"
REPO_POLICY = WORKSPACE / "copilot-instructions.md"
MERGED_POLICY = WORKSPACE / "merged-copilot-policy.md"

def merge():
    parts = []

    if not CENTRAL_POLICY.exists():
        raise RuntimeError(
            f"Central policy not found at {CENTRAL_POLICY}"
        )

    parts = [CENTRAL_POLICY.read_text(encoding="utf-8")]

    if REPO_POLICY.exists():
        parts.append(
            "\n\n---\n\n## Repository-specific additions\n"
        )
        parts.append(REPO_POLICY.read_text(encoding="utf-8"))

    MERGED_POLICY.write_text("\n".join(parts), encoding="utf-8")
    print(f"[OK] merged policy written to {MERGED_POLICY}")

if __name__ == "__main__":
    merge()
