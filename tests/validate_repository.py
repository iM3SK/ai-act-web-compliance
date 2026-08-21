"""Validate the public repository and installable skill package."""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "ai-act-web-compliance"
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".md",
    ".ps1",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}
REQUIRED_PATHS = {
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "THIRD_PARTY_NOTICES.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "SECURITY.md",
    ROOT / "CHANGELOG.md",
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".github" / "dependabot.yml",
    ROOT / ".github" / "CODEOWNERS",
    SKILL_ROOT / "SKILL.md",
    SKILL_ROOT / "agents" / "openai.yaml",
    SKILL_ROOT / "scripts" / "verify-pack.ps1",
}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PINNED_ACTION = re.compile(r"^\s*uses:\s*[^\s@]+@[0-9a-f]{40}(?:\s*#.*)?$", re.MULTILINE)


class AssetParser(HTMLParser):
    """Collect local HTML assets and the document language."""

    def __init__(self) -> None:
        super().__init__()
        self.assets: list[str] = []
        self.language: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang")
        for attribute in ("href", "src"):
            value = values.get(attribute)
            if value:
                self.assets.append(value)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {
            ".gitattributes",
            ".gitignore",
            "CODEOWNERS",
            "LICENSE",
        }:
            files.append(path)
    return sorted(files)


def check_required_paths(errors: list[str]) -> None:
    for path in sorted(REQUIRED_PATHS):
        if not path.is_file():
            fail(errors, f"missing required file: {path.relative_to(ROOT)}")


def check_repository_entries(errors: list[str]) -> None:
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_symlink():
            fail(errors, f"symbolic links are not allowed: {path.relative_to(ROOT)}")

    requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    if requirements.splitlines() != ["PyYAML==6.0.3"]:
        fail(errors, "requirements-dev.txt must contain only pinned PyYAML 6.0.3")


def check_safe_english_text(errors: list[str]) -> None:
    windows_user_path = re.compile(r"(?i)[a-z]:" + r"[\\/]" + "users" + r"[\\/]")
    posix_home_path = re.compile("/" + "home" + r"/[^/]+/")
    for path in text_files():
        relative = path.relative_to(ROOT)
        raw = path.read_bytes()
        if raw.startswith((b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")):
            fail(errors, f"byte-order mark is not allowed: {relative}")
        if b"\r" in raw:
            fail(errors, f"authored text must use LF line endings: {relative}")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            fail(errors, f"invalid UTF-8 in {relative}: {error}")
            continue
        non_ascii = sorted({character for character in text if ord(character) > 127})
        if non_ascii:
            rendered = " ".join(f"U+{ord(character):04X}" for character in non_ascii)
            fail(errors, f"non-ASCII maintained text in {relative}: {rendered}")
        if windows_user_path.search(text) or posix_home_path.search(text):
            fail(errors, f"local absolute path in {relative}")


def check_generated_artifacts(errors: list[str]) -> None:
    forbidden_names = {"__pycache__", ".pytest_cache", ".DS_Store", "Thumbs.db"}
    forbidden_suffixes = {".pyc", ".pyo"}
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts:
            continue
        if any(part in forbidden_names for part in relative.parts):
            fail(errors, f"forbidden generated artifact: {path.relative_to(ROOT)}")
        elif path.is_file() and path.suffix.lower() in forbidden_suffixes:
            fail(errors, f"forbidden generated artifact: {path.relative_to(ROOT)}")


def check_markdown_links(errors: list[str]) -> None:
    for path in (item for item in text_files() if item.suffix.lower() == ".md"):
        text = path.read_text(encoding="utf-8")
        for target in MARKDOWN_LINK.findall(text):
            target = target.strip().strip("<>")
            if target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_part = target.split("#", 1)[0]
            if not file_part:
                continue
            resolved = (path.parent / file_part).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                fail(errors, f"link escapes repository in {path.relative_to(ROOT)}: {target}")
                continue
            if not resolved.exists():
                fail(errors, f"broken local link in {path.relative_to(ROOT)}: {target}")


def check_skill_metadata(errors: list[str]) -> None:
    skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(?P<body>.*?)\n---\n", skill_text, re.DOTALL)
    if match is None:
        fail(errors, "SKILL.md must start with YAML front matter")
        return
    metadata = yaml.safe_load(match.group("body"))
    if not isinstance(metadata, dict):
        fail(errors, "SKILL.md front matter must be a mapping")
        return
    if set(metadata) != {"name", "description"}:
        fail(errors, "SKILL.md front matter must contain only name and description")
    if metadata.get("name") != "ai-act-web-compliance":
        fail(errors, "SKILL.md name does not match the install directory")
    description = metadata.get("description")
    if not isinstance(description, str) or "live official-source preflight" not in description:
        fail(errors, "SKILL.md description must advertise the mandatory live preflight")

    agent = yaml.safe_load(
        (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    )
    if not isinstance(agent, dict) or not isinstance(agent.get("interface"), dict):
        fail(errors, "agents/openai.yaml must contain interface metadata")
        return
    interface = agent["interface"]
    if interface.get("display_name") != "EU AI Act Web Compliance":
        fail(errors, "agent display name is inconsistent")
    prompt = interface.get("default_prompt")
    if not isinstance(prompt, str) or "$ai-act-web-compliance" not in prompt:
        fail(errors, "default prompt must explicitly invoke the skill")


def check_web_example(errors: list[str]) -> None:
    example = SKILL_ROOT / "assets" / "web" / "examples.html"
    parser = AssetParser()
    parser.feed(example.read_text(encoding="utf-8"))
    if parser.language != "en":
        fail(errors, "web example must declare lang=en")
    for target in parser.assets:
        if target.startswith(("#", "data:", "http://", "https://", "mailto:")):
            continue
        resolved = (example.parent / target).resolve()
        if not resolved.is_file():
            fail(errors, f"broken web example asset: {target}")


def check_icon_integrity(errors: list[str]) -> None:
    icon_root = SKILL_ROOT / "assets" / "eu-icons"
    icons = sorted(
        path for path in icon_root.rglob("*") if path.suffix.lower() in {".png", ".svg"}
    )
    if len(icons) != 24:
        fail(errors, f"expected 24 EU icon files, found {len(icons)}")

    manifest = icon_root / "SHA256SUMS.txt"
    entries = [line for line in manifest.read_text(encoding="utf-8").splitlines() if line]
    if len(entries) != 24:
        fail(errors, f"expected 24 icon checksums, found {len(entries)}")
        return
    for line in entries:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            fail(errors, f"invalid icon checksum line: {line}")
            continue
        expected, relative = match.groups()
        path = icon_root / Path(relative)
        if not path.is_file():
            fail(errors, f"missing icon from checksum manifest: {relative}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            fail(errors, f"icon checksum mismatch: {relative}")


def check_workflow(errors: list[str]) -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    uses_lines = [line for line in workflow.splitlines() if "uses:" in line]
    if not uses_lines:
        fail(errors, "CI workflow must use explicit actions")
    for line in uses_lines:
        if PINNED_ACTION.fullmatch(line) is None:
            fail(errors, f"GitHub Action is not pinned to a commit: {line.strip()}")
    if "permissions:\n  contents: read" not in workflow:
        fail(errors, "CI workflow must declare read-only contents permission")
    if "cache-dependency-path: requirements-dev.txt" not in workflow:
        fail(errors, "setup-python cache must track requirements-dev.txt")
    if workflow.count(
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1"
    ) != 2:
        fail(errors, "CI must use the verified actions/checkout v7.0.1 commit")
    if "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97" not in workflow:
        fail(errors, "CI must use the verified actions/setup-python v7.0.0 commit")
    checkout_count = workflow.count("uses: actions/checkout@")
    if workflow.count("persist-credentials: false") != checkout_count:
        fail(errors, "every checkout step must disable persisted credentials")
    if "concurrency:\n" not in workflow or "cancel-in-progress: true" not in workflow:
        fail(errors, "CI workflow must cancel superseded runs")
    if "PIP_NO_INPUT: \"1\"" not in workflow:
        fail(errors, "CI dependency installation must be non-interactive")
    if "python -m pip install --no-deps -r requirements-dev.txt" not in workflow:
        fail(errors, "CI must install the pinned validation dependency without dependencies")
    if workflow.count("github/codeql-action/") != 2:
        fail(errors, "CI must initialise and analyse Python with CodeQL")
    if "security-events: write" not in workflow:
        fail(errors, "CodeQL job must have security-events write permission")


def check_dependabot(errors: list[str]) -> None:
    path = ROOT / ".github" / "dependabot.yml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("version") != 2:
        fail(errors, "Dependabot configuration must use version 2")
        return
    updates = document.get("updates")
    if not isinstance(updates, list):
        fail(errors, "Dependabot configuration must contain updates")
        return
    ecosystems = {
        update.get("package-ecosystem"): update
        for update in updates
        if isinstance(update, dict)
    }
    if set(ecosystems) != {"pip", "github-actions"}:
        fail(errors, "Dependabot must cover pip and github-actions")
        return
    for ecosystem, update in ecosystems.items():
        schedule = update.get("schedule")
        if not isinstance(schedule, dict) or schedule.get("interval") != "weekly":
            fail(errors, f"Dependabot {ecosystem} updates must run weekly")
        if update.get("open-pull-requests-limit") != 5:
            fail(errors, f"Dependabot {ecosystem} must cap open pull requests at 5")
        if not isinstance(update.get("groups"), dict):
            fail(errors, f"Dependabot {ecosystem} updates must be grouped")


def check_readme_contract(errors: list[str]) -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    headings = [line for line in readme.splitlines() if line.startswith("## ")]
    if not headings or headings[0] != "## Clickable map":
        fail(errors, "README.md must use Clickable map as its first H2")
    if "not legal advice" not in readme.lower():
        fail(errors, "README.md must state the legal-advice boundary")
    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    if "not covered by this repository's MIT License" not in " ".join(
        notices.split()
    ):
        fail(errors, "third-party icon license boundary is missing")

    codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    if codeowners.strip() != "* @iM3SK":
        fail(errors, "CODEOWNERS must assign all repository paths to @iM3SK")


def main() -> None:
    errors: list[str] = []
    check_required_paths(errors)
    check_repository_entries(errors)
    check_safe_english_text(errors)
    check_generated_artifacts(errors)
    check_markdown_links(errors)
    check_skill_metadata(errors)
    check_web_example(errors)
    check_icon_integrity(errors)
    check_workflow(errors)
    check_dependabot(errors)
    check_readme_contract(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print(
        "PASS: repository structure, LF English-only text, generated-artifact "
        "exclusion, links, metadata, workflow, web assets, and 24 EU icon "
        "checksums are valid."
    )


if __name__ == "__main__":
    main()
