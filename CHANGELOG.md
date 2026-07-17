# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] - 2026-07-17

### Added
- Added `SECURITY.md` detailing vulnerability reporting, key management, and data privacy policies.
- Added `CONTRIBUTING.md` defining conventional commit guidelines, branch rules, and local setup.
- Enforced 15-second fail-fast timeout configurations on upstream Groq completions.
- Implemented `ENVIRONMENT=production` checks to restrict public `/groq-debug` route exposures.

### Changed
- Refactored `ALLOWED_HOSTS` CORS configuration to block wide-open wildcard permissions when credentials are enabled.
- Hardened the global exception handler in `backend/exceptions.py` to mask raw Python exceptions and stack traces behind sanitized server error payloads.
- Replaced raw `json.loads` calls in the AI service wrapper with the robust Pydantic-based `ResponseParser.validate_response` helper.
- Made the dashboard fully responsive across Mobile (Landscape/Portrait) and Tablet viewports, transforming hidden navigation columns into wrapping horizontal tab bars.

---

## [1.0.0] - 2026-07-17

### Added
- Initial release of the FIFA World Cup 2026 Smart Stadium Operations Command Center.
- Implemented multi-agent orchestrations (Coordinator, Crowd, Security, Emergency, Transport, Maintenance, Weather, and Visitor agents).
- Integrated Groq API using Llama 3.3 70B Versatile model.
- Added real-time stadium status simulation controls and interactive SVG Gate visualizer.
- Provided 45 unit/integration test cases achieving 94% test coverage.
