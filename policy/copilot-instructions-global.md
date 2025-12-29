# Global Security Policy (Authoritative)

These rules apply to ALL repositories.

## Non-negotiable rules

- Never hardcode secrets (passwords, tokens, API keys, cert private keys).
- Secrets must come from Vault, environment variables, or platform secret stores.
- Never log, echo, or print secrets.
- Use placeholders like REDACTED or variables in examples.
- Mark sensitive Ansible tasks with no_log: true.

## Red flags Copilot must avoid generating

- password = "..."
- token: "..."
- API keys like AKIA*, ghp_*, xoxb-*
- JWT literals
- Embedded TLS private keys
- Base64 encoded secrets inline

## Compliance

- OWASP Top 10
- SAP Secure Coding Guidelines
