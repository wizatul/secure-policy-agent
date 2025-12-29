# secure-policy-agent
Policy-as-Code enforcement using Copilot Instructions, Semgrep, and PR feedback

## Summary

Secure Policy Agent converts human-written security policy into enforceable, auditable controls that:

- Prevent insecure code generation
- Scan only Pull Request deltas
- Explain violations in policy language
- Align with SAP Secure Coding & OWASP

This repository treats policy as the primary artifact, not tooling.

## Why This Exists (Problem Statement)

Traditional AppSec tooling fails because:

- Policies live in PDFs or wikis
- Scanners detect issues without explaining why
- Developers ignore noisy findings
- Copilot generates insecure patterns by default
- Makes Copilot safe
- Makes developers accountable

## High-Level Architecture
### Logical Flow

~~~ css
copilot-instructions.md (repo / central)
            │
            ▼
policy_merger.py
            │
            ▼
merged-copilot-policy.md
            │
            ▼
policy_extractor.py   (PURE PARSER)
            │
            ▼
policy.json           (CANONICAL POLICY)
            │
            ▼
policy_mapper.py      (TOOL BINDING)
            │
            ▼
semgrep.yaml
            │
            ▼
semgrep (PR diff only)
            │
            ▼
pr_commenter.py
~~~

### Architecture Diagram (Developer View)

~~~ css
┌─────────────────────────────┐
│ copilot-instructions.md     │
│ (Human policy & standards)  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ policy_extractor.py         │
│ - Parses red flags          │
│ - Preserves policy text     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ policy.json                 │
│ - Rule IDs                  │
│ - Policy text               │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ policy_mapper.py            │
│ + semgrep-mapping.yaml      │
│ - Validates mappings        │
│ - Generates Semgrep config  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ semgrep.yaml                │
│ (Executable rules)          │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Semgrep (PR baseline scan)  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ pr_commenter.py             │
│ - Quotes violated policy    │
│ - Posts PR comments         │
└─────────────────────────────┘

~~~

## Policy Definition

### copilot-instructions.md

- Written by humans
- Reviewed by security
- Read by Copilot
- Used by enforcement tooling

## Policy Extraction
### policy_extractor.py

- Reads Copilot instructions
- Extracts “Red flags”
- Assigns stable IDs
- Outputs policy.json

## Policy Mapping
### semgrep-mapping.yaml

- Maps policy IDs → detection logic
- Owned by security engineers

## Policy Compilation
### policy_mapper.py

- Merges policy + detection logic
- Validates Semgrep schema.
- Injects policy text into rule messages.
- Outputs semgrep.yaml

## PR-Only Enforcement
### semgrep scan
> semgrep scan 
  --config secure-policy-agent/security-policies/semgrep-rules.yaml
  --baseline-commit "$(git merge-base HEAD origin/master)"
  --json > semgrep-results.json

### Pull Request feedback
PR comments include:
- File & line number
- Violated rule ID
- Quoted policy text


## Local Execution

~~~ css
python scripts/policy_extractor.py
python scripts/policy_mapper.py
semgrep scan \
  --config security-policies/semgrep.yaml \
  --baseline-commit origin/master \
  --json > semgrep-results.json
python scripts/pr_commenter.py
~~~

## CI Execution (GitHub Actions)

Triggered on: 
- pull_request
Pipeline:

- Checkout full git history
- Extract policy
- Compile enforcement rules
- Run Semgrep with baseline
- Comment on PR
- Fail build if blocking violations exist