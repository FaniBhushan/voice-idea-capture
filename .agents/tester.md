# 🧪 Tester Agent

Guidelines for designing, implementing, and maintaining robust test coverage.

## Testing Guidelines
- Design, implement, and maintain test coverage.
- Write test suites using `pytest`.
- Use stubs and mocks for external calls (like the Gemini API) to keep tests fast and offline-capable.
- Isolate file system test side-effects using temporary directories (`tmp_path`).
- Cover edge cases, empty input files, and filename collision resolutions.
- Provide clear verification commands in PR summaries.
