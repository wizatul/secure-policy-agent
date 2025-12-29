#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Running local Secure Policy Agent test"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d)"

ACTION_REPO="$TMP_DIR/action"
APP_REPO="$TMP_DIR/app"

mkdir -p "$ACTION_REPO" "$APP_REPO"

# ------------------------------------------------------------------
# Simulate CENTRAL REPO (action)
# ------------------------------------------------------------------
mkdir -p "$ACTION_REPO/mappings"
mkdir -p "$ACTION_REPO/scripts"

cp -r "$ROOT_DIR/scripts" "$ACTION_REPO/"
cp -r "$ROOT_DIR/mappings" "$ACTION_REPO/"

cat > "$ACTION_REPO/copilot-instructions.md" <<EOF
# Central Policy

## Red flags Copilot must avoid generating
- Never hardcode passwords
- Never commit API tokens
EOF

# ------------------------------------------------------------------
# Simulate APPLICATION REPO
# ------------------------------------------------------------------
cat > "$APP_REPO/copilot-instructions.md" <<EOF
# Repo-specific Copilot Instructions

- This repo uses Ansible
EOF

# ------------------------------------------------------------------
# Export GitHub Action environment
# ------------------------------------------------------------------
export GITHUB_ACTION_PATH="$ACTION_REPO"
export GITHUB_WORKSPACE="$APP_REPO"

echo "📁 GITHUB_ACTION_PATH=$GITHUB_ACTION_PATH"
echo "📁 GITHUB_WORKSPACE=$GITHUB_WORKSPACE"

# ------------------------------------------------------------------
# Run pipeline
# ------------------------------------------------------------------
python "$ACTION_REPO/scripts/policy_merger.py"
python "$ACTION_REPO/scripts/policy_extractor.py"
python "$ACTION_REPO/scripts/policy_mapper.py"

# ------------------------------------------------------------------
# Assertions
# ------------------------------------------------------------------
POLICY_JSON="$APP_REPO/security-policies/policy.json"
SEMGREP_YAML="$APP_REPO/security-policies/semgrep.yaml"

echo "🔍 Validating outputs"

if [[ ! -f "$POLICY_JSON" ]]; then
  echo "❌ policy.json not generated"
  exit 1
fi

if [[ ! -f "$SEMGREP_YAML" ]]; then
  echo "❌ semgrep.yaml not generated"
  exit 1
fi

echo "✅ policy.json generated"
echo "✅ semgrep.yaml generated"

echo "🎉 Local test PASSED"
