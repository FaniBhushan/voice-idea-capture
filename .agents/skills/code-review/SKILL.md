---
name: code-review
description: |
  Audits, reviews, or analyzes Python code changes for safety, error handling, performance, PEP 8 style, and overall quality.
---

# Code Review Guidelines

Use this skill when auditing and reviewing code modifications in this project.

## Quality Standards

### Safety & Error Handling
- Audit changes for safety, error handling, performance bottlenecks, and correctness.
- Verify exception boundaries around external APIs (like Google GenAI SDK).
- Check file I/O operations for proper open/close handling (always use context managers).

### Performance
- Check for redundant file reads/writes or unoptimized loops.
- Ensure the vault manager scans note files efficiently.

### Style Review
- Check that docstrings exist on all public functions and modules.
- Confirm Python code conforms to PEP 8 standards.

### Review Presentation
When acting as a reviewer, present your findings categorized as:
1. **Critical / Blocking**: Bugs, syntax errors, or resource leaks.
2. **Recommended / Non-blocking**: Performance optimizations or structural improvements.
3. **Nitpicks**: Minor formatting or style adjustments.
Always provide inline diff examples showing how to resolve the issues.
