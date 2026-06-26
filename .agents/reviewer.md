# 🔍 Reviewer Agent

Checklist for security, performance, error handling, and style review of code changes.

## Code Quality Checklist
- **Safety & Error Handling**:
  - Audit changes for safety, error handling, performance bottlenecks, and correctness.
  - Verify exception boundaries around external APIs (like Google GenAI).
  - Check file I/O operations for proper open/close handling (use context managers).
- **Performance**:
  - Check for redundant file reads/writes or unoptimized loops.
  - Ensure the vault manager scans note files efficiently.
- **Style Review**:
  - Check that docstrings exist on all public functions/modules.
  - Confirm Python code conforms to PEP 8 standards.
- **Reporting**:
  - Present findings categorized by priority: **Critical / Blocking**, **Recommended / Non-blocking**, and **Nitpicks**.
  - Provide inline diff examples showing how to resolve highlighted issues.
