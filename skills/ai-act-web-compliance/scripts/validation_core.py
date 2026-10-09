"""Shared preflight YAML validation for the package command-line tools."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    yaml = None  # type: ignore[assignment]


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


class ValidationError(ValueError):
    """Raised when a preflight document violates the public schema."""


if yaml is not None:

    class UniqueKeyLoader(yaml.SafeLoader):
        """Safe YAML loader that rejects duplicate mapping keys."""

        def construct_mapping(
            self,
            node: yaml.MappingNode,
            deep: bool = False,
        ) -> dict[Any, Any]:
            mapping: dict[Any, Any] = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                try:
                    duplicate = key in mapping
                except TypeError as error:
                    raise yaml.constructor.ConstructorError(
                        "while constructing a mapping",
                        node.start_mark,
                        "found an unhashable mapping key",
                        key_node.start_mark,
                    ) from error
                if duplicate:
                    raise yaml.constructor.ConstructorError(
                        "while constructing a mapping",
                        node.start_mark,
                        f"found duplicate key {key!r}",
                        key_node.start_mark,
                    )
                mapping[key] = self.construct_object(value_node, deep=deep)
            return mapping

else:
    UniqueKeyLoader = None


def validate_preflight(document_text: str, *, template: bool = False) -> None:
    """Validate one preflight YAML mapping or raise ``ValidationError``."""

    if yaml is None or UniqueKeyLoader is None:
        raise ValidationError("PyYAML is required to validate the preflight schema.")
    try:
        document = yaml.load(document_text, Loader=UniqueKeyLoader)
    except yaml.YAMLError as error:
        raise ValidationError(f"invalid YAML: {error}") from error
    if not isinstance(document, dict):
        raise ValidationError("preflight YAML must be one top-level mapping")

    actual_keys = set(document)
    missing = sorted(EXPECTED_KEYS - actual_keys)
    unexpected = sorted(actual_keys - EXPECTED_KEYS, key=str)
    if missing:
        raise ValidationError("missing keys: " + ", ".join(missing))
    if unexpected:
        raise ValidationError("unexpected keys: " + ", ".join(map(str, unexpected)))

    invalid_values = sorted(
        key
        for key, value in document.items()
        if not isinstance(value, str) or not value.strip()
    )
    if invalid_values:
        raise ValidationError(
            "values must be non-empty strings: " + ", ".join(invalid_values)
        )
    if template:
        if document != TEMPLATE_VALUES:
            raise ValidationError(
                "template mode accepts only the documented placeholder mapping"
            )
        return

    unresolved = sorted(
        key for key, value in document.items() if TEMPLATE_VALUES.get(key) == value
    )
    if unresolved:
        raise ValidationError("unresolved template values: " + ", ".join(unresolved))
    checked_at = document["checked_at"]
    if CHECKED_AT_PATTERN.fullmatch(checked_at) is None:
        raise ValidationError(
            "checked_at must use YYYY-MM-DDTHH:MM:SS with Z or a numeric offset"
        )
    normalised = (
        checked_at[:-1] + "+00:00" if checked_at.endswith("Z") else checked_at
    )
    try:
        parsed = datetime.fromisoformat(normalised)
    except ValueError as error:
        raise ValidationError(
            "checked_at must contain a valid calendar date and time"
        ) from error
    if parsed.utcoffset() is None:
        raise ValidationError("checked_at must include a timezone offset")
