"""Validate the flat preflight YAML template used by this skill."""

from __future__ import annotations

import argparse
import sys

sys.dont_write_bytecode = True

from validation_core import ValidationError, validate_preflight


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--template",
        action="store_true",
        help="allow the documented placeholder values while validating the template",
    )
    arguments = parser.parse_args()

    try:
        validate_preflight(sys.stdin.read(), template=arguments.template)
    except ValidationError as error:
        print(error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
