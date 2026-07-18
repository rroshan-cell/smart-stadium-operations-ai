# Security Policy

We take the security of the Smart Stadium Operations AI project seriously. This document outlines our security policies, key management guidelines, and instructions on how to report vulnerabilities.

---

## 📞 Responsible Disclosure

If you discover a security vulnerability in this project, please do **NOT** open a public issue. Instead, report it responsibly:
1. Email the maintainer at `ritikroshan223901@gmail.com` with a detailed description of the vulnerability.
2. Include steps to reproduce, potential impact, and a proof of concept if available.
3. Allow us reasonable time to investigate, address, and release a patch before making any public disclosure.

---

## 🛡️ Supported Versions

Only the latest release version on the `main` branch is actively supported with security patches:

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |
| < 1.0.0 | No        |

---

## 🔑 API Key Management & Environment Variables

- **Stateless Configuration**: All sensitive keys, including `GROQ_API_KEY`, must be managed externally and loaded dynamically.
- **Never Hardcode Secrets**: Do not store credentials, keys, or passwords inside code strings, prompts, or commits.
- **`.env` Loading**: The backend uses Pydantic's `BaseSettings` to parse environment variables from `.env` files safely:
  - Default `.env` files must be locked and kept private.
  - The repository includes a template file `.env.example` to guide key naming.

---

## 🧬 Groq API Security

- **Encrypted Transmission**: All communication with the Groq inference endpoint occurs over HTTPS.
- **Data Privacy**: No personally identifiable information (PII) or telemetry variables outside of stadium metrics are sent to the LLM model.
- **Token Protection**: Offline mock frameworks verify code logic during test suites to prevent token exhaustion and key usage costs.

---

## 🔍 Input Validation

- **Pydantic Schemas**: All incoming payloads (requests, telemetry structures, simulation overrides) are verified at the network boundary using strict Pydantic model schemas.
- **Malformed Inputs**: FastAPI automatically returns `422 Unprocessable Entity` on input type mismatches, preventing execution of unexpected data parameters.

---

## ⚡ Timeout Protection

- **Resilient Connections**: All external calls to the Groq API enforce a 15-second request timeout limit to prevent socket exhaustion and blockages under load.

---

## ⚙️ Exception Handling & Error Masking

- **Traceback Protection**: The global exception handler filters raw exception tracebacks and Python error classes from API response contents.
- **Generic Server Errors**: In production mode, failures return a generic error payload: `{"status": "failed", "error": "Internal Server Error"}`. Full error tracebacks are logged securely on the server via `logger.exception()`.

---

## 🚫 No Secrets Committed

- **GitIgnore Rules**: The repository includes a strict `.gitignore` mapping to ensure local `.env`, `.venv`, and temporary `.coverage` items are never checked into Git history.
- **History Auditing**: Periodically scan commits for accidentally committed secrets using security scanning tools.

---

## 📦 Dependency Updates

- Keep all libraries updated to their latest secure versions.
- Scan for vulnerable packages regularly using automated tools:
  ```bash
  pip-audit
  ```
