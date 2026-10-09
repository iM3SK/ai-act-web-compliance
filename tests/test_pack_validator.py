"""Contract and mutation tests for the installed skill-pack validator."""

from __future__ import annotations

from collections.abc import Callable
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALLED_PACK = ROOT / "skills" / "ai-act-web-compliance"
PYTHON_VALIDATOR = Path("scripts") / "verify-pack.py"
POWERSHELL_LAUNCHER = Path("scripts") / "verify-package.ps1"
PWSH = shutil.which("pwsh")

Mutator = Callable[[Path], None]


def replace_bytes(path: Path, old: bytes, new: bytes) -> None:
    """Replace one required byte sequence without platform newline conversion."""
    content = path.read_bytes()
    if old not in content:
        raise AssertionError(f"test mutation target is absent: {old!r} in {path}")
    path.write_bytes(content.replace(old, new, 1))


def run_python_validator(pack: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", str(pack / PYTHON_VALIDATOR)],
        cwd=pack,
        text=True,
        capture_output=True,
        check=False,
    )


def run_powershell_launcher(
    pack: Path,
    *,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    if PWSH is None:
        raise unittest.SkipTest("pwsh is not installed")
    return subprocess.run(
        [
            PWSH,
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(pack / POWERSHELL_LAUNCHER),
        ],
        cwd=pack,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def write_python_shim(
    directory: Path,
    *,
    executable: str | None = None,
    failure_marker: str = "",
    exit_code: int = 0,
) -> None:
    """Create a native command shim that PowerShell can discover as python."""
    directory.mkdir()
    if os.name == "nt":
        shim = directory / "python.cmd"
        if executable is not None:
            command = f"{subprocess.list2cmdline([executable])} %*"
        else:
            command = f"echo {failure_marker} 1>&2\r\nexit /b {exit_code}"
        shim.write_bytes(f"@echo off\r\n{command}\r\n".encode("utf-8"))
        return

    shim = directory / "python"
    if executable is not None:
        command = f'exec {shlex.quote(executable)} "$@"'
    else:
        command = (
            f"printf '%s\\n' {shlex.quote(failure_marker)} >&2\n"
            f"exit {exit_code}"
        )
    shim.write_text(f"#!/bin/sh\n{command}\n", encoding="utf-8", newline="\n")
    shim.chmod(0o755)


def run_installed_pack(
    mutator: Mutator | None = None,
    *,
    powershell: bool = False,
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="ai-act-pack-") as temporary:
        pack = Path(temporary) / "installed skill"
        shutil.copytree(INSTALLED_PACK, pack)
        if mutator is not None:
            mutator(pack)
        if powershell:
            return run_powershell_launcher(pack)
        return run_python_validator(pack)


class PackValidatorTests(unittest.TestCase):
    def assert_rejected(self, mutator: Mutator, expected: str) -> None:
        result = run_installed_pack(mutator)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn(expected.casefold(), output.casefold())

    def test_pack_001_python_cli_accepts_installed_pack(self) -> None:
        """PACK-001: both Python CLIs accept the pack without writing bytecode."""
        with tempfile.TemporaryDirectory(prefix="ai-act-pack-") as temporary:
            pack = Path(temporary) / "installed skill"
            shutil.copytree(INSTALLED_PACK, pack)
            before = (
                list(pack.rglob("__pycache__"))
                + list(pack.rglob("*.pyc"))
                + list(pack.rglob("*.pyo"))
            )
            self.assertEqual(before, [])

            plain_environment = os.environ.copy()
            plain_environment.pop("PYTHONDONTWRITEBYTECODE", None)
            plain_environment.pop("PYTHONPYCACHEPREFIX", None)
            result = subprocess.run(
                [sys.executable, str(pack / PYTHON_VALIDATOR)],
                cwd=pack,
                env=plain_environment,
                text=True,
                capture_output=True,
                check=False,
            )
            preflight_text = (
                pack / "references" / "legal-preflight.md"
            ).read_text(encoding="utf-8")
            opening = "```yaml\n"
            closing = "\n```"
            self.assertIn(opening, preflight_text)
            template_and_tail = preflight_text.split(opening, 1)[1]
            self.assertIn(closing, template_and_tail)
            documented_template = template_and_tail.split(closing, 1)[0]
            preflight_result = subprocess.run(
                [
                    sys.executable,
                    str(pack / "scripts" / "verify-preflight-yaml.py"),
                    "--template",
                ],
                cwd=pack,
                env=plain_environment,
                input=documented_template,
                text=True,
                capture_output=True,
                check=False,
            )

            after = (
                list(pack.rglob("__pycache__"))
                + list(pack.rglob("*.pyc"))
                + list(pack.rglob("*.pyo"))
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS:", result.stdout + result.stderr)
        self.assertEqual(
            preflight_result.returncode,
            0,
            preflight_result.stdout + preflight_result.stderr,
        )
        self.assertEqual(after, [])

    @unittest.skipUnless(PWSH is not None, "pwsh is not installed")
    def test_pack_002_powershell_launcher_accepts_installed_pack(self) -> None:
        """PACK-002: the public PowerShell launcher accepts the installed pack."""
        result = run_installed_pack(powershell=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS:", result.stdout + result.stderr)

    @unittest.skipUnless(PWSH is not None, "pwsh is not installed")
    def test_pack_018_powershell_launcher_uses_first_python_match(self) -> None:
        """PACK-018: multiple Python applications select the first PATH match."""
        with tempfile.TemporaryDirectory(prefix="ai-act-pack-") as temporary:
            outer = Path(temporary)
            pack = outer / "installed skill"
            first_bin = outer / "first python"
            second_bin = outer / "second python"
            shutil.copytree(INSTALLED_PACK, pack)
            write_python_shim(first_bin, executable=sys.executable)
            write_python_shim(
                second_bin,
                failure_marker="SECOND_PYTHON_SHIM_INVOKED",
                exit_code=91,
            )
            environment = os.environ.copy()
            environment["PATH"] = os.pathsep.join(
                [str(first_bin), str(second_bin), environment.get("PATH", "")]
            )

            result = run_powershell_launcher(pack, environment=environment)

        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("PASS:", output)
        self.assertNotIn("SECOND_PYTHON_SHIM_INVOKED", output)

    @unittest.skipUnless(PWSH is not None, "pwsh is not installed")
    def test_pack_019_powershell_launcher_rejects_missing_validator(self) -> None:
        """PACK-019: a missing Python validator returns the documented failure."""
        with tempfile.TemporaryDirectory(prefix="ai-act-pack-") as temporary:
            pack = Path(temporary) / "installed skill"
            shutil.copytree(INSTALLED_PACK, pack)
            (pack / PYTHON_VALIDATOR).unlink()

            result = run_powershell_launcher(pack)

        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 1, output)
        self.assertIn("Missing package validator", output)

    @unittest.skipUnless(PWSH is not None, "pwsh is not installed")
    def test_pack_020_powershell_launcher_rejects_missing_python(self) -> None:
        """PACK-020: a PATH without Python returns the documented failure."""
        with tempfile.TemporaryDirectory(prefix="ai-act-pack-") as temporary:
            outer = Path(temporary)
            pack = outer / "installed skill"
            empty_bin = outer / "empty bin"
            empty_bin.mkdir()
            shutil.copytree(INSTALLED_PACK, pack)
            environment = os.environ.copy()
            environment["PATH"] = str(empty_bin)

            result = run_powershell_launcher(pack, environment=environment)

        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 1, output)
        self.assertIn("Python with PyYAML is required", output)

    def test_pack_003_rejects_missing_required_file(self) -> None:
        """PACK-003: a required installed-pack file may not be omitted."""

        def mutate(pack: Path) -> None:
            (pack / "references" / "decision-tree.md").unlink()

        self.assert_rejected(mutate, "Missing required file")

    def test_pack_004_rejects_crlf_authored_text(self) -> None:
        """PACK-004: authored pack text must retain LF line endings."""

        def mutate(pack: Path) -> None:
            skill = pack / "SKILL.md"
            replace_bytes(skill, b"\n", b"\r\n")

        self.assert_rejected(mutate, "Authored text must use LF line endings")

    def test_pack_005_rejects_hidden_generated_artifact(self) -> None:
        """PACK-005: recursive validation includes hidden generated artifacts."""

        def mutate(pack: Path) -> None:
            artifact = pack / ".hidden" / "__pycache__" / "leak.pyc"
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(b"generated")

        self.assert_rejected(mutate, "Forbidden generated artifact")

    def test_pack_006_rejects_tampered_official_icon(self) -> None:
        """PACK-006: an icon whose bytes no longer match the manifest is rejected."""

        def mutate(pack: Path) -> None:
            icon = pack / "assets" / "eu-icons" / "png" / "ai-basic-black.png"
            icon.write_bytes(icon.read_bytes() + b"tampered")

        self.assert_rejected(mutate, "Checksum mismatch")

    def test_pack_007_rejects_case_insensitive_duplicate_manifest_path(self) -> None:
        """PACK-007: manifest paths are unique across filesystem case rules."""

        def mutate(pack: Path) -> None:
            manifest = pack / "assets" / "eu-icons" / "SHA256SUMS.txt"
            lines = manifest.read_bytes().splitlines()
            checksum, relative = lines[0].split(b"  ", 1)
            lines[1] = checksum + b"  " + relative.upper()
            manifest.write_bytes(b"\n".join(lines) + b"\n")

        self.assert_rejected(mutate, "Duplicate icon checksum path")

    def test_pack_008_rejects_manifest_path_escape(self) -> None:
        """PACK-008: checksum entries cannot resolve outside the icon root."""

        def mutate(pack: Path) -> None:
            manifest = pack / "assets" / "eu-icons" / "SHA256SUMS.txt"
            lines = manifest.read_bytes().splitlines()
            checksum, relative = lines[0].split(b"  ", 1)
            lines[0] = checksum + b"  ../" + relative
            manifest.write_bytes(b"\n".join(lines) + b"\n")

        self.assert_rejected(mutate, "Icon checksum path escapes asset root")

    def test_pack_016_accepts_uppercase_hashes_and_external_scheme(self) -> None:
        """PACK-016: preserve case-insensitive PowerShell input semantics."""
        def mutate(pack: Path) -> None:
            manifest = pack / "assets" / "eu-icons" / "SHA256SUMS.txt"
            lines = []
            for line in manifest.read_bytes().splitlines():
                checksum, relative = line.split(b"  ", 1)
                lines.append(checksum.upper() + b"  " + relative)
            manifest.write_bytes(b"\n".join(lines) + b"\n")
            example = pack / "assets" / "web" / "examples.html"
            replace_bytes(example, b'href="ai-disclosure.css"',
                          b'href="HTTPS://example.com/style.css"')

        result = run_installed_pack(mutate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pack_017_rejects_mixed_case_generated_name(self) -> None:
        """PACK-017: generated-artifact names retain case-insensitive matching."""
        def mutate(pack: Path) -> None:
            (pack / "ThUmBs.Db").write_bytes(b"generated")

        self.assert_rejected(mutate, "Forbidden generated artifact")

    def test_pack_009_rejects_missing_legal_guardrail(self) -> None:
        """PACK-009: removing a required fail-closed rule invalidates the pack."""

        def mutate(pack: Path) -> None:
            replace_bytes(
                pack / "SKILL.md",
                b"Always perform a live official-source preflight",
                b"Perform an official-source preflight when convenient",
            )

        self.assert_rejected(mutate, "Missing fail-closed skill contract")

    def test_pack_010_rejects_malformed_preflight_yaml(self) -> None:
        """PACK-010: the documented preflight block must parse as YAML."""

        def mutate(pack: Path) -> None:
            replace_bytes(
                pack / "references" / "legal-preflight.md",
                b"checked_at: YYYY-MM-DDTHH:MM:SS+TZ",
                b"checked_at: [unterminated",
            )

        self.assert_rejected(mutate, "Preflight YAML schema validation failed")

    def test_pack_011_rejects_multiple_preflight_yaml_documents(self) -> None:
        """PACK-011: the fenced preflight block is exactly one YAML document."""

        def mutate(pack: Path) -> None:
            replace_bytes(
                pack / "references" / "legal-preflight.md",
                b"checked_at: YYYY-MM-DDTHH:MM:SS+TZ",
                b"checked_at: YYYY-MM-DDTHH:MM:SS+TZ\n---\nsecond: document",
            )

        self.assert_rejected(mutate, "Preflight YAML schema validation failed")

    def test_pack_012_rejects_modified_preflight_template(self) -> None:
        """PACK-012: template mode accepts only the documented placeholder map."""

        def mutate(pack: Path) -> None:
            replace_bytes(
                pack / "references" / "legal-preflight.md",
                b"jurisdiction: EU/EEA and named Member State",
                b"jurisdiction: EU/EEA only",
            )

        self.assert_rejected(mutate, "Preflight YAML schema validation failed")

    def test_pack_013_rejects_missing_local_html_asset(self) -> None:
        """PACK-013: every local HTML asset reference must resolve to a file."""

        def mutate(pack: Path) -> None:
            replace_bytes(
                pack / "assets" / "web" / "examples.html",
                b'href="ai-disclosure.css"',
                b'href="missing-local.css"',
            )

        self.assert_rejected(mutate, "Broken local example asset")

    def test_pack_014_rejects_escaped_local_html_asset(self) -> None:
        """PACK-014: local HTML references cannot escape the skill root."""

        def mutate(pack: Path) -> None:
            replace_bytes(
                pack / "assets" / "web" / "examples.html",
                b'href="ai-disclosure.css"',
                b'href="../../../../outside.css"',
            )

        self.assert_rejected(mutate, "Local example asset escapes skill root")

    @unittest.skipUnless(PWSH is not None, "pwsh is not installed")
    def test_pack_015_powershell_propagates_python_yaml_failure(self) -> None:
        """PACK-015: the launcher preserves a real Python validation failure."""
        with tempfile.TemporaryDirectory(prefix="ai-act-pack-") as temporary:
            pack = Path(temporary) / "installed skill"
            shutil.copytree(INSTALLED_PACK, pack)
            replace_bytes(
                pack / "references" / "legal-preflight.md",
                b"checked_at: YYYY-MM-DDTHH:MM:SS+TZ",
                b"checked_at: [unterminated",
            )

            direct = run_python_validator(pack)
            launched = run_powershell_launcher(pack)

        direct_output = direct.stdout + direct.stderr
        launched_output = launched.stdout + launched.stderr
        self.assertNotEqual(direct.returncode, 0, direct_output)
        self.assertEqual(launched.returncode, direct.returncode, launched_output)
        self.assertIn(
            "preflight yaml schema validation failed",
            direct_output.casefold(),
        )
        self.assertIn(
            "preflight yaml schema validation failed",
            launched_output.casefold(),
        )


if __name__ == "__main__":
    unittest.main()
