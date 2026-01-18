# Security Policy

## Supported Versions

This is an active research/clinical-support project. We aim to keep the `main` branch reasonably secure. Older tags or branches may not receive security updates.

## Reporting a Vulnerability

If you find a security issue (including exposed secrets, authentication problems, or data-leak risks):

1. **Do not** create a public GitHub issue with sensitive details.
2. Use one of these options instead:
   - Open a **GitHub Security Advisory** ("Report a vulnerability" in the Security tab), or
   - Contact the maintainer privately via their GitHub profile: @ihariganesh.
3. Provide as much detail as you can to reproduce the issue.

We will:
- Acknowledge your report as quickly as possible.
- Work on a fix and coordinate a responsible disclosure timeline.

## Secrets and API Keys

- Do **not** commit real API keys, database URLs with real passwords, JWT secrets, or access tokens to this repository.
- Use environment variables and `.env` files that are **never** committed.
- If you accidentally commit a secret:
  - Immediately revoke/rotate it in the provider’s dashboard.
  - Open a private report (see above) so we can help clean up.

## Secret Scanning on GitHub

GitHub may raise **secret scanning alerts** for this repository. After this cleanup:
- Any **old keys** that were visible in docs or examples must be treated as **compromised** and rotated.
- For each alert in `Security → Secret scanning`, mark it **resolved** after you rotate the corresponding secret.

If you see a new alert and you are unsure how to handle it, please contact the maintainer before taking action.
