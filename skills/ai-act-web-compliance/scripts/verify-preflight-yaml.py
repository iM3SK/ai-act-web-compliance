"""Validate the flat preflight YAML template used by this skill."""

from __future__ import annotations

import argparse
from datetime import datetime
import re
import sys

try:
    import yaml
    from yaml.constructor import ConstructorError
except ModuleNotFoundError:
    print("PyYAML is required to validate the preflight schema.")
    raise SystemExit(1)


EXPECTED_KEYS = {
    "checked_at",
    "jurisdiction",
    "ai_act_consolidation",
    "official_guidance",
    "code_and_icons",
    "national_sources",
    "changes_since_baseline",
    "unavailable_sources",
}

CHECKED_AT_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})"
)
TEMPLATE_VALUES = {
    "checked_at": "YYYY-MM-DDTHH:MM:SS+TZ",
    "jurisdiction": "EU/EEA and named Member State",
    "ai_act_consolidation": "CELEX identifier and consolidation date",
    "official_guidance": "titles, statuses, and update dates",
    "code_and_icons": "title, status, and update date",
    "national_sources": (
        "exact authority and legislation-register sources, dates, and results"
    ),
    "changes_since_baseline": "none observed | concise list",
    "unavailable_sources": "none | concise list",
}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict:
        mapping: dict = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError as error:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found an unhashable mapping key",
                    key_node.start_mark,
                ) from error
            if duplicate:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def fail(message: str) -> None:
    print(message)
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--template",
        action="store_true",
        help="allow the documented placeholder values while validating the template",
    )
    arguments = parser.parse_args()

    raw_yaml = sys.stdin.read()
    try:
        document = yaml.load(raw_yaml, Loader=UniqueKeyLoader)
    except yaml.YAMLError as error:
        fail(f"invalid YAML: {error}")

    if not isinstance(document, dict):
        fail("preflight YAML must be one top-level mapping")

    actual_keys = set(document)
    missing = sorted(EXPECTED_KEYS - actual_keys)
    unexpected = sorted(actual_keys - EXPECTED_KEYS, key=str)
    if missing:
        fail("missing keys: " + ", ".join(missing))
    if unexpected:
        fail("unexpected keys: " + ", ".join(map(str, unexpected)))

    invalid_values = sorted(
        key
        for key, value in document.items()
        if not isinstance(value, str) or not value.strip()
    )
    if invalid_values:
        fail("values must be non-empty strings: " + ", ".join(invalid_values))

    if arguments.template:
        if document != TEMPLATE_VALUES:
            fail("template mode accepts only the documented placeholder mapping")
        return

    unresolved = sorted(
        key for key, value in document.items() if TEMPLATE_VALUES.get(key) == value
    )
    if unresolved:
        fail("unresolved template values: " + ", ".join(unresolved))

    checked_at = document["checked_at"]
    if CHECKED_AT_PATTERN.fullmatch(checked_at) is None:
        fail("checked_at must use YYYY-MM-DDTHH:MM:SS with Z or a numeric offset")
    normalised = (
        checked_at[:-1] + "+00:00" if checked_at.endswith("Z") else checked_at
    )
    try:
        parsed = datetime.fromisoformat(normalised)
    except ValueError:
        fail("checked_at must contain a valid calendar date and time")
    if parsed.utcoffset() is None:
        fail("checked_at must include a timezone offset")


if __name__ == "__main__":
    main()
