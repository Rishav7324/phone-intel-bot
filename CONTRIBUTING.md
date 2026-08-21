# Contributing to Phone Intel Bot

Thanks for your interest in contributing! 🎉

Phone Intel Bot is built to be modular, privacy-conscious, and easy to extend. Contributions of code, tests, documentation, bug reports, and ideas are welcome.

## Before You Start

- Read the README and understand the project structure.
- Check existing Issues and Pull Requests before opening a duplicate.
- For large architectural changes, open an issue first so the approach can be discussed.
- Never commit tokens, API keys, `.env` files, private data, or real personal phone numbers.

## Development Setup

```bash
git clone https://github.com/Rishav7324/phone-intel-bot.git
cd phone-intel-bot

python -m venv .venv
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

## Branches

Use focused branch names:

- `feat/<short-name>` — new functionality
- `fix/<short-name>` — bug fix
- `docs/<short-name>` — documentation
- `refactor/<short-name>` — internal refactor
- `test/<short-name>` — tests

## Code Guidelines

- Keep modules small and focused.
- Keep Telegram handlers thin; business logic belongs in services.
- Follow the existing provider abstraction for external metadata providers.
- Prefer async I/O where the surrounding code is async.
- Validate and sanitize user-controlled input.
- Never log raw phone numbers, tokens, credentials, or other sensitive data.
- Avoid adding a dependency when the standard library or an existing dependency is sufficient.
- Document non-obvious security/privacy decisions.

## Testing

Run the full suite before opening a PR:

```bash
pytest -v
```

For a new feature, add regression or unit tests where practical.

## Pull Requests

A good PR should:

1. Solve one clearly defined problem.
2. Include tests for behavior that changed.
3. Update documentation when user-facing behavior changes.
4. Avoid unrelated formatting or refactoring.
5. Explain security/privacy implications when relevant.
6. Pass the project's automated checks.

### PR checklist

- [ ] Tests added/updated where appropriate
- [ ] `pytest -v` passes
- [ ] No secrets committed
- [ ] No real personal data included
- [ ] README/docs updated if needed
- [ ] Security/privacy impact reviewed
- [ ] PR is focused and easy to review

## Reporting Bugs

Use GitHub Issues and include:

- What happened
- What you expected
- Steps to reproduce
- Python version
- OS/environment
- Relevant error output with secrets and personal data removed

Do not post credentials, bot tokens, private phone numbers, or sensitive infrastructure details.

## Security Issues

Please do not disclose an exploitable vulnerability publicly before the maintainer has had a chance to investigate it. See [`SECURITY.md`](SECURITY.md).

## Code of Conduct

Please read [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) before participating.

## License

By contributing, you agree that your contributions are provided under the project's [MIT License](LICENSE).
