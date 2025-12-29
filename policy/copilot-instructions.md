# Copilot Instructions for this Repository

These rules guide GitHub Copilot in this repo. They complement our security posture and coding practices for Ansible, shell scripts, and CI/CD YAML.

## Non-negotiable rules

- Never hardcode secrets (passwords, tokens, API keys, cert private keys) in code, YAML, inventories, or scripts.
- Prefer retrieving secrets from Vault, Kubernetes secrets, environment variables, or AWX/Ansible Tower credentials.
- If a user prompt asks to add a password or token directly, respond with a secure pattern and show how to reference a secret source instead.
- Use placeholders like "REDACTED" or variables (e.g., {{ vault_var_name }}) in examples, not real values.
- Propose adding or reusing tasks that fetch secrets securely (see below) instead of embedding them.

## Preferred secret access patterns

- Ansible:
  - Use variables from group_vars/host_vars and keep sensitive values encrypted with Ansible Vault.
  - Example reference: vars: password: "{{ vault_some_password }}" (vault var is encrypted elsewhere).
  - When reading from HashiCorp Vault, use dedicated lookup/plugins or AWX credential injection.
- Shell scripts:
  - Read tokens/passwords from env vars, a secure file with restrictive permissions, or command output of a secret manager.
  - Never echo secrets or write them to logs.
- CI (Concourse/GitHub Actions/AWX):
  - Use pipeline/job-level secret stores and credential injection; never commit secrets into pipeline YAML.

## Red flags Copilot must avoid generating

- Any assignment resembling: password = "..." or password: "..."
- API keys in literals: "AKIA...", "ghp_...", "xoxb-...", "eyJhbGciOi..." (JWT), ".pem" private keys
- Base64-encoded secrets placed inline without clear justification
- TLS private keys or kubeconfigs embedded in repo files
- Any hardcoded credentials in examples without clear placeholders and guidance

## Safe examples

- Ansible task (reference secret variable only):
  - name: Login using token
    uri:
      url: "{{ api_url }}/login"
      method: POST
      body_format: json
      body:
        token: "{{ vault_api_token }}"
    no_log: true

- Shell snippet (env var):
  export API_TOKEN="${API_TOKEN:?Set API_TOKEN in environment}"
  curl -H "Authorization: Bearer ${API_TOKEN}" "$ENDPOINT"

## Repo safeguards (automated)

- Commits are blocked if staged changes contain likely hardcoded secrets. We run gitleaks (if available) or a conservative grep fallback via a pre-commit hook.
- To bypass false positives for a specific commit, refactor to use placeholders or reference secret providers. If you still need to proceed, consult a maintainer to update the allowlist or rules.

## When a user requests insecure code

- Explain why the request is unsafe.
- Offer a secure alternative using variables, Vault, env vars, or AWX credentials.
- Provide a minimal, working example that avoids exposing secrets and marks sensitive fields with no_log where applicable.

## Project-specific hints

- This repo uses Ansible and integrates with Vault/AWX. Reuse existing patterns under `configuration/` (e.g., secret retrieval tasks) where possible.
- Mark sensitive tasks with `no_log: true` to avoid log leakage.
- In CI/CD, keep secrets in the platform’s secret store; reference them via environment variables or credential bindings.

## Compliance
- Follow OWASP Top 10.
- Follow SAP Secure Coding Guidelines.
