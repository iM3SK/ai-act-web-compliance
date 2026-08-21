"""Mutation tests for the repository and preflight validators."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "ai-act-web-compliance"
PREFLIGHT_VALIDATOR = SKILL / "scripts" / "verify-preflight-yaml.py"

VALID_PREFLIGHT = """\
checked_at: "2026-08-21T12:00:00+02:00"
jurisdiction: "EU/EEA only"
ai_act_consolidation: "CELEX 02024R1689-20260727"
official_guidance: "Final Guidelines, 31 July 2026; overview, 5 August 2026"
code_and_icons: "Final Code and EU icons, 10 August 2026"
national_sources: "not in scope for this EU-only example"
changes_since_baseline: "none observed"
unavailable_sources: "none"
"""

TEMPLATE_PREFLIGHT = """\
checked_at: YYYY-MM-DDTHH:MM:SS+TZ
jurisdiction: EU/EEA and named Member State
ai_act_consolidation: CELEX identifier and consolidation date
official_guidance: titles, statuses, and update dates
code_and_icons: title, status, and update date
national_sources: exact authority and legislation-register sources, dates, and results
changes_since_baseline: none observed | concise list
unavailable_sources: none | concise list
"""


def run_preflight_validator(
    document: str,
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PREFLIGHT_VALIDATOR), *arguments],
        input=document,
        text=True,
        capture_output=True,
        check=False,
    )


class PreflightValidatorTests(unittest.TestCase):
    def assert_rejected(self, document: str, expected: str) -> None:
        result = run_preflight_validator(document)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout + result.stderr)

    def test_accepts_complete_flat_mapping(self) -> None:
        result = run_preflight_validator(VALID_PREFLIGHT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_missing_key(self) -> None:
        document = VALID_PREFLIGHT.replace(
            'unavailable_sources: "none"\n',
            "",
        )
        self.assert_rejected(document, "missing keys: unavailable_sources")

    def test_rejects_duplicate_key(self) -> None:
        self.assert_rejected(
            VALID_PREFLIGHT + 'checked_at: "duplicate"\n',
            "found duplicate key",
        )

    def test_rejects_unexpected_key(self) -> None:
        self.assert_rejected(
            VALID_PREFLIGHT + 'verdict: "pass"\n',
            "unexpected keys: verdict",
        )

    def test_rejects_blank_value(self) -> None:
        document = VALID_PREFLIGHT.replace(
            'national_sources: "not in scope for this EU-only example"',
            'national_sources: ""',
        )
        self.assert_rejected(document, "values must be non-empty strings")

    def test_rejects_non_string_value(self) -> None:
        document = VALID_PREFLIGHT.replace(
            'checked_at: "2026-08-21T12:00:00+02:00"',
            "checked_at: 20260821",
        )
        self.assert_rejected(document, "values must be non-empty strings")

    def test_rejects_non_mapping_document(self) -> None:
        self.assert_rejected("- item\n", "must be one top-level mapping")

    def test_rejects_multiple_documents(self) -> None:
        self.assert_rejected(
            VALID_PREFLIGHT + "---\nsecond: document\n",
            "invalid YAML",
        )

    def test_rejects_malformed_timestamp(self) -> None:
        document = VALID_PREFLIGHT.replace(
            'checked_at: "2026-08-21T12:00:00+02:00"',
            'checked_at: "21 August 2026 at noon"',
        )
        self.assert_rejected(document, "checked_at must use")

    def test_rejects_impossible_timestamp(self) -> None:
        document = VALID_PREFLIGHT.replace(
            'checked_at: "2026-08-21T12:00:00+02:00"',
            'checked_at: "2026-02-30T12:00:00+02:00"',
        )
        self.assert_rejected(document, "valid calendar date")

    def test_rejects_timestamp_without_timezone(self) -> None:
        document = VALID_PREFLIGHT.replace(
            'checked_at: "2026-08-21T12:00:00+02:00"',
            'checked_at: "2026-08-21T12:00:00"',
        )
        self.assert_rejected(document, "checked_at must use")

    def test_rejects_unresolved_template_in_runtime_mode(self) -> None:
        self.assert_rejected(TEMPLATE_PREFLIGHT, "unresolved template values")

    def test_accepts_documented_template_in_template_mode(self) -> None:
        result = run_preflight_validator(TEMPLATE_PREFLIGHT, "--template")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_modified_template_in_template_mode(self) -> None:
        modified = TEMPLATE_PREFLIGHT.replace(
            "jurisdiction: EU/EEA and named Member State",
            "jurisdiction: EU/EEA only",
        )
        result = run_preflight_validator(modified, "--template")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "template mode accepts only the documented placeholder mapping",
            result.stdout + result.stderr,
        )


Mutator = Callable[[Path], None]


def run_repository_validator(
    mutator: Mutator | None = None,
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="ai-act-validator-") as temporary:
        checkout = Path(temporary) / "repo"
        shutil.copytree(
            ROOT,
            checkout,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                ".pytest_cache",
                "*.pyc",
                "*.pyo",
            ),
        )
        if mutator is not None:
            mutator(checkout)
        return subprocess.run(
            [sys.executable, "tests/validate_repository.py"],
            cwd=checkout,
            text=True,
            capture_output=True,
            check=False,
        )


class RepositoryValidatorMutationTests(unittest.TestCase):
    def assert_mutation_rejected(self, mutator: Mutator, expected: str) -> None:
        result = run_repository_validator(mutator)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout + result.stderr)

    def test_accepts_clean_repository(self) -> None:
        result = run_repository_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_crlf_in_authored_text(self) -> None:
        def mutate(checkout: Path) -> None:
            readme = checkout / "README.md"
            readme.write_bytes(readme.read_bytes().replace(b"\n", b"\r\n", 1))

        self.assert_mutation_rejected(mutate, "must use LF line endings")

    def test_rejects_generated_python_cache(self) -> None:
        def mutate(checkout: Path) -> None:
            cache = checkout / "tests" / "__pycache__" / "leak.pyc"
            cache.parent.mkdir()
            cache.write_bytes(b"generated")

        self.assert_mutation_rejected(mutate, "forbidden generated artifact")

    def test_rejects_broken_markdown_link(self) -> None:
        def mutate(checkout: Path) -> None:
            readme = checkout / "README.md"
            text = readme.read_text(encoding="utf-8") + "\n[Broken](missing.md)\n"
            readme.write_bytes(text.encode("utf-8"))

        self.assert_mutation_rejected(mutate, "broken local link")

    def test_rejects_modified_official_icon(self) -> None:
        def mutate(checkout: Path) -> None:
            icon = (
                checkout
                / "skills"
                / "ai-act-web-compliance"
                / "assets"
                / "eu-icons"
                / "png"
                / "ai-basic-black.png"
            )
            icon.write_bytes(icon.read_bytes() + b"tampered")

        self.assert_mutation_rejected(mutate, "icon checksum mismatch")

    def test_rejects_unpinned_github_action(self) -> None:
        def mutate(checkout: Path) -> None:
            workflow = checkout / ".github" / "workflows" / "ci.yml"
            text = workflow.read_text(encoding="utf-8")
            text = text.replace(
                "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
                "actions/checkout@v7",
            )
            workflow.write_bytes(text.encode("utf-8"))

        self.assert_mutation_rejected(mutate, "not pinned to a commit")

    def test_rejects_persisted_checkout_credentials(self) -> None:
        def mutate(checkout: Path) -> None:
            workflow = checkout / ".github" / "workflows" / "ci.yml"
            text = workflow.read_text(encoding="utf-8")
            text = text.replace("persist-credentials: false", "persist-credentials: true", 1)
            workflow.write_bytes(text.encode("utf-8"))

        self.assert_mutation_rejected(mutate, "disable persisted credentials")

    def test_rejects_missing_codeql_upload_permission(self) -> None:
        def mutate(checkout: Path) -> None:
            workflow = checkout / ".github" / "workflows" / "ci.yml"
            text = workflow.read_text(encoding="utf-8")
            text = text.replace("security-events: write", "security-events: read")
            workflow.write_bytes(text.encode("utf-8"))

        self.assert_mutation_rejected(mutate, "security-events write permission")

    def test_rejects_web_asset_escape(self) -> None:
        def mutate(checkout: Path) -> None:
            example = (
                checkout
                / "skills"
                / "ai-act-web-compliance"
                / "assets"
                / "web"
                / "examples.html"
            )
            text = example.read_text(encoding="utf-8")
            text = text.replace(
                "</body>",
                '<img src="../../../../README.md" alt="">\n  </body>',
            )
            example.write_bytes(text.encode("utf-8"))

        self.assert_mutation_rejected(mutate, "web example asset escapes skill root")

    def test_rejects_duplicate_icon_checksum_path(self) -> None:
        def mutate(checkout: Path) -> None:
            manifest = (
                checkout
                / "skills"
                / "ai-act-web-compliance"
                / "assets"
                / "eu-icons"
                / "SHA256SUMS.txt"
            )
            lines = manifest.read_text(encoding="utf-8").splitlines()
            lines[1] = lines[0]
            manifest.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))

        self.assert_mutation_rejected(mutate, "duplicate icon checksum path")

    def test_rejects_bytecode_enabled_contributing_command(self) -> None:
        def mutate(checkout: Path) -> None:
            contributing = checkout / "CONTRIBUTING.md"
            text = contributing.read_text(encoding="utf-8")
            text = text.replace(
                'python -B -m unittest discover -s tests -p "test_*.py" -v',
                'python -m unittest discover -s tests -p "test_*.py" -v',
            )
            contributing.write_bytes(text.encode("utf-8"))

        self.assert_mutation_rejected(
            mutate,
            "CONTRIBUTING test command must disable repository bytecode generation",
        )

    def test_rejects_removed_criminal_law_exception(self) -> None:
        def mutate(checkout: Path) -> None:
            decision_tree = (
                checkout
                / "skills"
                / "ai-act-web-compliance"
                / "references"
                / "decision-tree.md"
            )
            text = decision_tree.read_text(encoding="utf-8")
            text = text.replace(
                "**Deepfake criminal-law exception:**",
                "**Deepfake exception:**",
                1,
            )
            decision_tree.write_bytes(text.encode("utf-8"))

        self.assert_mutation_rejected(
            mutate,
            "decision tree is missing legal content contract",
        )


if __name__ == "__main__":
    unittest.main()
