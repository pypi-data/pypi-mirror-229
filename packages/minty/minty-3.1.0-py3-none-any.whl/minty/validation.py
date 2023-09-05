# SPDX-FileCopyrightText: 2020 Mintlab B.V.
#
# SPDX-License-Identifier: EUPL-1.2

import json
from functools import wraps
from typing import NoReturn
from uuid import UUID

from jsonpointer import JsonPointer  # type: ignore
from jsonschema import Draft7Validator  # type: ignore

from .exceptions import ValidationError

_format_checker = Draft7Validator.FORMAT_CHECKER


def assert_never(value: NoReturn) -> NoReturn:  # pragma: no cover
    """
    Assert that a point in the code is never reached.

    Using this function allows the type checker to warn about the unreachable
    code when using enums or literals.

    Example:
    ```
        AllowedValues = Literal['a', 'b']

        def do_something(x: AllowedValues) -> bool:
            if x == 'a':
                return True
            elif x == 'b':
                return False
            assert_never(x)
    ```
    """
    raise AssertionError(f"This code should never be reached, got: {value}")


@_format_checker.checks("uuid", raises=ValueError)
def is_uuid(instance):
    return UUID(hex=str(instance))


def validate_with(schema_data: bytes | None):
    """Ensure the decorated function is called with valid arguments

    :param schema_data: The JSONSchema to validate against.
        Should be UTF-8-encoded JSON bytes.
    :type schema_data: bytes
    :return: Decorator for validating function arguments against `schema`
    """
    assert schema_data is not None, "No validation JSON found"

    schema = json.loads(schema_data.decode("utf-8"))

    def validity_wrapper(f):
        validator = Draft7Validator(
            schema=schema, format_checker=_format_checker
        )

        @wraps(f)
        def check_validity(*args, **kwargs):
            errors = []
            for error in validator.iter_errors(instance=kwargs):
                error_pointer = JsonPointer.from_parts(error.absolute_path)

                errors.append(
                    {
                        "context": error.validator,
                        "message": error.message,
                        "cause": str(error.cause) if error.cause else None,
                        "property": error_pointer.path,
                    }
                )

            if len(errors):
                raise ValidationError(errors)

            return f(*args, **kwargs)

        return check_validity

    return validity_wrapper
