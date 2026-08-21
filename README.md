# AI Act Web Compliance

An installable Codex skill for assessing and implementing EU AI Act Article 50
transparency on websites and in public AI-content workflows. It covers live
official-source checks, decision paths, labels, official EU icons, accessible
web patterns, provenance, enforcement evidence, and penalty questions.

The skill is designed to fail closed: it requires a fresh official-source
preflight before every legal conclusion or compliance action. The bundled
legal baseline is only a change-detection aid, not a substitute for the live
law.

The public package is intentionally Member State-neutral and contains no
country-specific legislative baseline. A use involving national law must open
the relevant Member State's official authority and legislation-register
sources during that run; country-specific maintained baselines belong in local
extensions.

## Clickable map

- AI Act Web Compliance repository - installation, operating guidance, evidence, and project governance.
  - [Skill contract](skills/ai-act-web-compliance/SKILL.md) - defines activation, mandatory live preflight, workflow, output contract, and safety boundaries.
    - [Legal preflight](skills/ai-act-web-compliance/references/legal-preflight.md) - specifies the fail-closed source check and machine-validated record.
    - [Decision tree](skills/ai-act-web-compliance/references/decision-tree.md) - classifies provider, deployer, chatbot, deepfake, and public-interest text cases.
    - [Generation workflow](skills/ai-act-web-compliance/references/generation-workflow.md) - separates legal duties, voluntary Code commitments, and recommended controls before, during, and after generation.
    - [Icons and labels](skills/ai-act-web-compliance/references/icons-and-labels.md) - selects semantic and visual icon variants, wording, placement, and accessibility.
    - [Web implementation](skills/ai-act-web-compliance/references/web-implementation.md) - provides reusable HTML and CSS integration guidance.
    - [Enforcement and evidence](skills/ai-act-web-compliance/references/enforcement-and-evidence.md) - explains investigation evidence, detection limits, authorities, and penalty ceilings.
    - [Official sources](skills/ai-act-web-compliance/references/official-sources.md) - maps the primary EU sources and the national-source categories that must be checked live.
    - [EU icon provenance](skills/ai-act-web-compliance/assets/eu-icons/SOURCE.md) - records official downloads, archive hashes, filename mapping, and reuse terms.
  - [Contributing](CONTRIBUTING.md) - defines English-only changes, source evidence, tests, and pull-request expectations.
  - [Security policy](SECURITY.md) - explains supported versions and private vulnerability reporting.
  - [Changelog](CHANGELOG.md) - records release-level changes.
  - [Third-party notices](THIRD_PARTY_NOTICES.md) - separates official EU icon terms from the repository's MIT license.
  - [MIT license](LICENSE) - grants permission for repository-authored code and documentation.

## Install

Ask Codex to install the skill from this repository path:

```text
https://github.com/iM3SK/ai-act-web-compliance/tree/main/skills/ai-act-web-compliance
```

Or use the bundled Codex skill installer:

```bash
python <skill-installer-root>/scripts/install-skill-from-github.py \
  --repo iM3SK/ai-act-web-compliance \
  --path skills/ai-act-web-compliance
```

Restart the conversation after installation so the skill catalog reloads.

## Use

Typical requests include:

```text
Use $ai-act-web-compliance to assess the AI disclosures on this website.
```

```text
Use $ai-act-web-compliance to choose an EU icon and accessible disclosure for
this generated video. Check current official sources before deciding.
```

The skill distinguishes legal requirements from voluntary Code commitments and
recommended risk controls. It does not treat an icon, metadata, or an AI
detector score as proof of compliance or authorship.

## Included assets

The package contains 24 official European Commission icon files: three
semantic variants, four visual variants, and both SVG and PNG formats. Their
byte integrity is protected by `SHA256SUMS.txt`; their separate reuse terms and
source archives are documented in the icon provenance file.

The HTML and CSS examples are implementation patterns, not automatic legal
answers. Translate their English disclosure text for the actual audience and
rerun the legal preflight before deployment.

## Verification

Python 3.12 and PowerShell are the verified runtime for the complete local check.
Install the pinned test dependency, then run the validator test suite and both
package checks:

```bash
python -m pip install --no-deps -r requirements-dev.txt
python -B -m unittest discover -s tests -p "test_*.py" -v
python tests/validate_repository.py
pwsh -NoProfile -File skills/ai-act-web-compliance/scripts/verify-pack.ps1
```

The 26 positive and mutation tests prove that the validators accept the valid
package and reject malformed preflight records, CRLF-authored text, generated
caches anywhere in the repository, broken links, modified icons, unpinned
actions, persisted checkout credentials, a missing CodeQL upload permission,
escaped web assets, duplicate icon checksum paths, unresolved preflight
templates, altered documentation templates, invalid or timezone-free preflight
timestamps, and contributor instructions that would generate repository
bytecode. A legal-content regression test also preserves both narrow Article
50(4) criminal-law exceptions in the decision tree.
The repository validator also checks package structure, symbolic links, the
exact validation dependency, English-only maintained text, prompt metadata,
workflow pinning, local web assets, and icon hashes. The pack validator checks
the legal guardrails, current source baseline, and preflight YAML schema.
GitHub Actions runs the same validation on Ubuntu 24.04 and Windows 2025 and a
separate least-privilege CodeQL Python job on Ubuntu 24.04.

## Legal boundary

This project provides compliance-oriented information and implementation
support. It is not legal advice, does not guarantee compliance, and cannot
replace qualified counsel for disputed or high-impact cases.

## License

Repository-authored code and documentation are available under the
[MIT License](LICENSE). Official European Commission icons are third-party
assets governed by the terms documented in
[Third-party notices](THIRD_PARTY_NOTICES.md).
