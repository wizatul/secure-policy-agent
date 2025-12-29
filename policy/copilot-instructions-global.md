# Global Copilot Security Instructions (Authoritative)

This document defines **mandatory security rules** enforced across all repositories.
GitHub Copilot **must not generate** code or configuration violating these rules.

These rules align with:
- SAP Secure Coding Guidelines
- SAP Secure Operations Map
- OWASP Top 10
- CIS Benchmarks

---

## Red flags Copilot must avoid generating

### Secutiy Findings
- Hardcoded passwords, tokens, API keys, or credentials in code, scripts, or configuration files
- Base64-encoded secrets embedded inline (credentials, tokens, private keys)
- Secrets committed into YAML, JSON, ENV, or CI/CD configuration files

### Database Security (SAP-aligned)
- Hardcoded database credentials in application code or configuration
- Database connections with TLS/SSL explicitly disabled
- SQL queries built via string concatenation instead of parameterized queries
- Use of highly privileged database users (e.g., root, sys, dba) by applications

### Operating System Security
- Shell commands that expose or echo credentials
- Insecure file permissions (e.g., chmod 777) on configuration or secret files
- Disabling OS security controls (SELinux, AppArmor)
- Use of deprecated or weak cryptographic algorithms (e.g., MD5, SHA1)

### SAP Web Dispatcher / Web Tier Security
- SAP Web Dispatcher or web server configured with HTTP instead of HTTPS
- TLS certificate verification disabled
- Hardcoded credentials in Web Dispatcher profiles or routing rules
- Web Dispatcher configurations allowing unrestricted backend access

---

## Preferred secure patterns

- Retrieve secrets from secure stores (Vault, environment variables, platform secret stores)
- Enforce TLS for all database and web connections
- Use least-privilege database and OS users
- Use parameterized queries and secure crypto libraries
- Follow SAP hardening guides for OS, database, and Web Dispatcher

---

## Compliance

- SAP Secure Coding Guidelines
- SAP Secure Operations Map
- OWASP Top 10
- CIS Benchmarks
