# Code Review Checklist

## 1. Correctness
- Does the code do what the PR description says it does?
- Are there logical errors or off-by-one mistakes?
- Are return values and error cases handled correctly?
- Does it handle null/undefined/empty inputs?

## 2. Edge Cases
- What happens with empty inputs, zero values, or max-size data?
- Are there race conditions in concurrent code?
- Are timeouts and retries handled for external calls?
- Does it degrade gracefully under unexpected conditions?

## 3. Naming and Clarity
- Are variable and function names descriptive and consistent?
- Could someone unfamiliar with the codebase understand the intent?
- Are complex algorithms or business logic explained with comments?
- Do function signatures clearly convey their purpose?

## 4. Security
- Is user input validated and sanitized?
- Are there SQL injection, XSS, or command injection risks?
- Are secrets or credentials hardcoded?
- Are API endpoints properly authenticated and authorized?
- Is sensitive data logged or exposed in error messages?

## 5. Test Coverage
- Are there tests for the new/changed functionality?
- Do tests cover the happy path AND error cases?
- Are edge cases from section 2 covered?
- If no tests: is this a risk? Should tests be added before merge?

## 6. Performance (only flag if obvious)
- Are there N+1 query patterns or unnecessary loops?
- Are large datasets loaded into memory unnecessarily?
- Are there missing indexes for database queries?

## Review Format

For each issue found, use this format:

```
**[Category]** `file.py:L42`
Description of the issue.
Suggestion: <how to fix it>
```
