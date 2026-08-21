# Security Policy

## Supported Versions

Security fixes are currently focused on the latest version of the `main` branch.

| Version | Supported |
|---|---|
| Latest `main` | ✅ |
| Older revisions | ❌ |

## Reporting a Vulnerability

Please **do not open a public GitHub Issue for a security vulnerability**.

If the repository's private security reporting feature is available, use it. Otherwise, contact the maintainer through the contact method listed on the GitHub profile and include `[SECURITY]` in the subject.

Please include:

- A clear description of the vulnerability
- Affected component/file
- Reproduction steps or a minimal proof of concept
- Potential impact
- Any suggested mitigation

Remove secrets, real personal data, bot tokens, API keys, and unnecessary identifying information from the report.

## What to Expect

The maintainer will attempt to:

1. Acknowledge the report.
2. Reproduce and assess the issue.
3. Determine severity and affected versions.
4. Prepare a fix or mitigation.
5. Coordinate disclosure when appropriate.

## Scope

Examples of security issues worth reporting include:

- Authentication or authorization bypass
- Secret/token exposure
- Sensitive data leakage
- Injection vulnerabilities
- Unsafe command execution
- SSRF or network-boundary issues
- Privacy-impacting logging or persistence
- Dependency vulnerabilities that materially affect the project

## Privacy

Phone Intel Bot is designed around public/technical metadata and should not be used to collect or expose private subscriber information. Do not submit real personal phone numbers or private data in issues, tests, examples, or pull requests.
