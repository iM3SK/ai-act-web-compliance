"""Validate the installed AI Act Web Compliance skill package."""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import sys

sys.dont_write_bytecode = True

from validation_core import ValidationError, validate_preflight


SKILL_ROOT = Path(__file__).resolve().parents[1]
ICON_ROOT = SKILL_ROOT / "assets" / "eu-icons"
CHECKSUM_FILE = ICON_ROOT / "SHA256SUMS.txt"
REQUIRED_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/legal-preflight.md",
    "references/decision-tree.md",
    "references/generation-workflow.md",
    "references/icons-and-labels.md",
    "references/web-implementation.md",
    "references/enforcement-and-evidence.md",
    "references/official-sources.md",
    "assets/eu-icons/SOURCE.md",
    "assets/web/ai-disclosure.css",
    "assets/web/examples.html",
    "scripts/validation_core.py",
    "scripts/verify-package.ps1",
    "scripts/verify-preflight-yaml.py",
)
GENERATED_NAMES = {"__pycache__", ".pytest_cache", ".ds_store", "thumbs.db"}
GENERATED_SUFFIXES = {".pyc", ".pyo"}
AUTHORED_TEXT_SUFFIXES = {
    ".css", ".html", ".md", ".ps1", ".py", ".txt", ".yaml", ".yml"
}
REQUIRED_SKILL_TEXT = (
    "Always perform a live official-source preflight",
    "The EU icons are optional",
    "Stop each definitive legal conclusion whose controlling source cannot be",
    "do not suppress a separately supported EU-law conclusion",
    "Prefix every material wording, timing, placement, repetition, and persistence",
    "the Code's audio-at-the-beginning implementation",
    "Use only the exact official URL that was opened during the current preflight",
    "Before returning, open or otherwise verify every cited URL",
    "shorten, or guess a citation path",
    "End every legal or compliance answer with the complete `Preflight record` YAML",
    "a prose summary does not replace it",
    "parse the final fenced block as YAML",
    "with no stray delimiter",
    "Never headline or summarize an assessment as `PASS`, `compliant`",
    "State the narrower Article 50 classification",
    "perform an adversarial self-check",
    "Test one expected path and one forbidden or failure path",
    "A string-presence assertion",
)
CONTENT_CONTRACTS = {
    "references/legal-preflight.md": (
        "This is a fail-closed gate",
        "checked_at: YYYY-MM-DDTHH:MM:SS+TZ",
        "national_sources:",
        "the named successor and record both process identifiers",
        "An HTTP success",
        "map the gap to the conclusions it could change",
        "do not use it to block an independently supported",
    ),
    "references/decision-tree.md": (
        "## 0. Fix the relevant date",
        "2 December 2026",
        "do not need retroactive marking or",
        "It does not postpone Article 50(1)",
        "source code and integral code comments or configuration",
        "machine-to-machine",
        "closed-loop industrial or product-",
        "**Deepfake criminal-law exception:**",
        "**Public-interest-text criminal-law exception:**",
    ),
    "references/generation-workflow.md": (
        "## Before generation", "## During generation", "## After generation",
        "**LAW, chatbot/agent:**", "**CODE, audio-only:**",
        "Do not ask a tool or pipeline to remove a watermark",
    ),
    "references/icons-and-labels.md": (
        "The icon is optional", "official-looking audio mark",
        "Fully AI-generated", "Partially AI-modified", "Basic AI",
        "A law-enforcement context alone", "does not establish that exception",
    ),
    "references/web-implementation.md": (
        "**CODE implementation:**",
        "include the audible disclaimer at the beginning",
        "Article 50(1) chatbot",
        "Never absolutely position a custom control",
        "fullscreen the labelled wrapper",
    ),
    "references/enforcement-and-evidence.md": (
        "Authorities do not need a universal `AI detector`",
        "EUR 15 million", "EUR 7.5 million",
    ),
    "references/official-sources.md": (
        "Baseline observed on 21 August 2026", "Article 50 overview",
        "5 August 2026", "Official document ID", "`131215`", "`129555`",
        "30861FC5DE31205846F023068069C92FABC7271EBEAC6AF7BEF68B97F0A33F66",
        "7BD22C5A3C56EAEFDA27A5BF7A6118198EF2A9C9255241BD97ABF7CDEDF9BC28",
    ),
}
YAML_BLOCK = re.compile(
    r"^```yaml[ \t]*\r?\n(?P<body>.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL
)
HTML_ASSET = re.compile(r'(?:src|href)="(?P<path>[^"#]+)"')


def read_text(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        relative = path.relative_to(SKILL_ROOT).as_posix()
        errors.append(f"Unable to read {relative}: {error}")
        return None


def is_rooted(path_text: str) -> bool:
    return PurePosixPath(path_text).is_absolute() or PureWindowsPath(path_text).is_absolute()


def path_parts(path_text: str) -> tuple[str, ...]:
    return tuple(part for part in re.split(r"[\\/]", path_text) if part)


def contained_icon_path(path_text: str) -> tuple[Path, str] | None:
    if is_rooted(path_text) or ".." in path_parts(path_text):
        return None
    candidate = (ICON_ROOT / PurePosixPath(path_text.replace("\\", "/"))).resolve()
    try:
        relative = candidate.relative_to(ICON_ROOT.resolve()).as_posix()
    except ValueError:
        return None
    return candidate, relative


def check_required_files(errors: list[str]) -> None:
    for relative in REQUIRED_FILES:
        if not (SKILL_ROOT / relative).is_file():
            errors.append(f"Missing required file: {relative.replace('/', chr(92))}")


def check_generated_and_text_files(errors: list[str]) -> None:
    for path in SKILL_ROOT.rglob("*"):
        relative = path.relative_to(SKILL_ROOT).as_posix().replace("/", "\\")
        if (
            path.name.casefold() in GENERATED_NAMES
            or path.suffix.lower() in GENERATED_SUFFIXES
        ):
            errors.append(f"Forbidden generated artifact: {relative}")
        if path.is_file() and path.suffix.lower() in AUTHORED_TEXT_SUFFIXES:
            try:
                raw = path.read_bytes()
            except OSError as error:
                errors.append(f"Unable to read {relative}: {error}")
                continue
            if b"\r" in raw:
                errors.append(f"Authored text must use LF line endings: {relative}")


def check_icons(errors: list[str]) -> None:
    manifest_paths: dict[str, str] = {}
    if not CHECKSUM_FILE.is_file():
        errors.append("Missing icon checksum manifest.")
    else:
        manifest_text = read_text(CHECKSUM_FILE, errors)
        if manifest_text is not None:
            lines = [line for line in manifest_text.splitlines() if line.strip()]
            if len(lines) != 24:
                errors.append(f"Expected 24 icon checksums, found {len(lines)}.")
            for line in lines:
                match = re.fullmatch(
                    r"(?P<hash>[0-9a-f]{64})  (?P<path>.+)",
                    line,
                    flags=re.IGNORECASE,
                )
                if match is None:
                    errors.append(f"Invalid checksum line: {line}")
                    continue
                relative_icon = match.group("path")
                contained = contained_icon_path(relative_icon)
                if contained is None:
                    errors.append(f"Icon checksum path escapes asset root: {relative_icon}")
                    continue
                icon_path, manifest_path = contained
                key = manifest_path.casefold()
                if key in manifest_paths:
                    errors.append(f"Duplicate icon checksum path: {manifest_path}")
                    continue
                manifest_paths[key] = manifest_path
                if not icon_path.is_file():
                    errors.append(f"Missing icon: {relative_icon}")
                    continue
                try:
                    actual_hash = hashlib.sha256(icon_path.read_bytes()).hexdigest()
                except OSError as error:
                    errors.append(f"Unable to read icon {relative_icon}: {error}")
                    continue
                if actual_hash != match.group("hash").lower():
                    errors.append(f"Checksum mismatch: {relative_icon}")

    icon_files = sorted(
        path for path in ICON_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".svg", ".png"}
    )
    if len(icon_files) != 24:
        errors.append(f"Expected 24 icon files, found {len(icon_files)}.")
    actual_paths = {
        path.relative_to(ICON_ROOT).as_posix().casefold(): path.relative_to(ICON_ROOT).as_posix()
        for path in icon_files
    }
    for key, relative in actual_paths.items():
        if key not in manifest_paths:
            errors.append(f"Missing icon checksum entry: {relative}")
    for key, relative in manifest_paths.items():
        if key not in actual_paths:
            errors.append(f"Checksum entry has no bundled icon: {relative}")


def check_content_contracts(errors: list[str]) -> None:
    skill_text = read_text(SKILL_ROOT / "SKILL.md", errors)
    if skill_text is not None:
        for required in REQUIRED_SKILL_TEXT:
            if required not in skill_text:
                errors.append(f"Missing fail-closed skill contract: {required}")
    for relative, required_texts in CONTENT_CONTRACTS.items():
        path = SKILL_ROOT / relative
        if not path.is_file():
            continue
        text = read_text(path, errors)
        if text is None:
            continue
        display_path = relative.replace("/", "\\")
        for required in required_texts:
            if required not in text:
                errors.append(f"Missing content contract in {display_path}: {required}")


def check_preflight_template(errors: list[str]) -> None:
    path = SKILL_ROOT / "references" / "legal-preflight.md"
    if not path.is_file():
        return
    text = read_text(path, errors)
    if text is None:
        return
    blocks = list(YAML_BLOCK.finditer(text))
    if len(blocks) != 1:
        errors.append(f"Expected one preflight YAML block, found {len(blocks)}.")
        return
    try:
        validate_preflight(blocks[0].group("body"), template=True)
    except ValidationError as error:
        errors.append(f"Preflight YAML schema validation failed: {error}")


def check_web_example(errors: list[str]) -> None:
    example = SKILL_ROOT / "assets" / "web" / "examples.html"
    if not example.is_file():
        return
    text = read_text(example, errors)
    if text is None:
        return
    for match in HTML_ASSET.finditer(text):
        reference = match.group("path")
        if re.match(r"^(?:https?:|data:|mailto:)", reference, flags=re.IGNORECASE):
            continue
        if is_rooted(reference):
            errors.append(f"Local example asset escapes skill root: {reference}")
            continue
        asset_path = (
            example.parent / PurePosixPath(reference.replace("\\", "/"))
        ).resolve()
        try:
            asset_path.relative_to(SKILL_ROOT.resolve())
        except ValueError:
            errors.append(f"Local example asset escapes skill root: {reference}")
            continue
        if not asset_path.is_file():
            errors.append(f"Broken local example asset: {reference}")


def main() -> None:
    errors: list[str] = []
    check_required_files(errors)
    check_generated_and_text_files(errors)
    check_icons(errors)
    check_content_contracts(errors)
    check_preflight_template(errors)
    check_web_example(errors)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(
        "PASS: skill structure, parsed preflight schema, and all 24 official "
        "icon assets match."
    )


if __name__ == "__main__":
    main()
