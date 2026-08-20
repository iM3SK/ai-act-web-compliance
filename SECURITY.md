# Security Policy

## Supported versions

Security fixes are applied to the current `1.x` release line. Users should
upgrade to the latest published release before reporting a problem already
fixed on `main`.

## Report a vulnerability

Use GitHub's private **Report a vulnerability** form when it is available in
the repository Security tab. Include the affected version, reproducible steps,
impact, and the smallest safe proof of concept.

If private reporting is unavailable, open a minimal public issue asking the
maintainer for a private contact channel. Do not include exploit details,
credentials, personal data, or a live vulnerable target in that issue.

Expect an acknowledgement within seven days. No resolution deadline is
promised because impact and legal-source dependencies vary. Coordinated public
disclosure should wait until a fix or documented mitigation is available.

## Scope

Relevant reports include unsafe execution paths in scripts, path traversal,
malicious-file handling, dependency compromise, leaked secrets, or a
fail-open validation path that could produce an unsupported legal conclusion.
Disagreements about legal interpretation without a security impact belong in a
regular issue.
