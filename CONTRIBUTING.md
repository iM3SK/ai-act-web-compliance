# Contributing

Contributions are welcome when they preserve the skill's fail-closed legal
preflight and keep the repository directly installable.

## Requirements

- Write repository-owned text, code comments, examples, and commit messages in
  English. Exact official titles and URLs may remain in their source language.
- Support legal assertions with a current primary source. Record the retrieval
  date and keep legal requirements distinct from voluntary Code commitments
  and recommendations.
- Do not replace a live official-source check with the bundled baseline, a
  search result, model memory, or a third-party summary.
- Do not redraw official icons. Preserve the bundled file bytes and update
  checksums and provenance together when the Commission publishes new assets.
- Keep secrets, personal data, symbolic links, generated caches, and local
  absolute paths out of commits.

## Development

1. Create a focused branch from `main`.
2. Install the pinned test dependency with
   `python -m pip install --no-deps -r requirements-dev.txt`.
3. Make the smallest coherent change and update tests or content contracts.
4. Run `python -B -m unittest discover -s tests -p "test_*.py" -v`.
5. Run `python tests/validate_repository.py`.
6. Run
   `pwsh -NoProfile -File skills/ai-act-web-compliance/scripts/verify-pack.ps1`.
7. Review the complete diff and open a pull request that explains the behavior,
   evidence, verification, and any remaining uncertainty.

## Legal-source changes

When an official source changes, update the affected rule, the dated baseline,
the preflight mapping, and any validator assertion in one reviewable change.
Do not silently weaken a fail-closed condition to make a test pass.

## Pull requests

A pull request must have one clear purpose, pass both validators, contain no
unrelated generated files, and identify the official evidence for every legal
change. Maintainers may request qualified legal review for disputed or
high-impact interpretations.
