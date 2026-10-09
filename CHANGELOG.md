# Changelog

<!-- markdownlint-configure-file {"MD024": {"siblings_only": true}} -->

All notable release changes are recorded here. The project follows Semantic
Versioning for its public skill contract.

## 2.0.0 - 2026-10-10

### Changed

- **Breaking:** renamed the PowerShell package-validation entrypoint from
  `scripts/verify-pack.ps1` to `scripts/verify-package.ps1`. Update existing <!-- markdown-check: nonbinding-resource -->
  commands to use the new path. The standalone Python entrypoint and all
  package-validation rules are unchanged.

### Fixed

- Restored local package validation where Windows refused to recreate the
  original quarantined script path, using a new transparent PowerShell launcher
  without antivirus exclusions or changes to protection settings.
- Select the first native Python executable when multiple installations are
  present, and preserve validation failures as nonzero process exit codes.

## 1.0.3 - 2026-10-10

### Fixed

- Replaced the PowerShell package checker with a small launcher and a standalone
  Python implementation after Bitdefender quarantined the original validator.
  Preserved icon integrity, file and path checks, legal content guardrails, and
  the preflight YAML schema without antivirus exclusions.
- Shared preflight schema validation between both command-line validators and
  added installed-package mutation tests for the package checker and launcher.

## 1.0.2 - 2026-08-21

- Kept the public package Member State-neutral; country-specific legal source
  baselines belong in local extensions.
- Added exact final Guidelines and Code document identifiers and hashes.
- Added the Article 50 temporal-scope and guidance-based output-scope checks.
- Added repository-wide LF and generated-artifact validation on both supported
  CI operating systems.
- Expanded the suite to 26 tests with runtime timestamp validation, strict
  template mode, icon-manifest bijection, web-asset containment checks, and a
  bytecode-free contributor workflow contract.
- Restored the narrow Article 50(4) criminal-law exceptions for deepfakes and
  public-interest text, protected them with a legal-content regression test,
  and identified the audio-at-the-beginning pattern as a Code implementation.
- Tracked the Article 50 overview update independently from the final
  Guidelines library page and made local test commands bytecode-free.
- Hardened checkout credentials and Actions permissions, added CodeQL, grouped
  Dependabot updates, CODEOWNERS, and documented repository safeguards.

## 1.0.1 - 2026-08-21

- Fixed GitHub Actions dependency-cache discovery for `requirements-dev.txt`.
- Added a regression check for the workflow cache dependency path.

## 1.0.0 - 2026-08-21

- Added the installable EU AI Act Article 50 web-compliance skill.
- Added mandatory live official-source preflight and structured YAML evidence.
- Added decision, generation, labelling, web implementation, enforcement, and
  official-source guidance.
- Added 24 integrity-checked official European Commission AI content icons.
- Added accessible HTML and CSS disclosure patterns.
- Added cross-platform repository and pack validation in GitHub Actions.
