import ast
from textwrap import dedent
from typing import Set

import pytest

from flake8_fastapi_route_case import Plugin
from flake8_fastapi_route_case import SupportedCase


def _results(s: str, check_case: SupportedCase = SupportedCase.SNAKE) -> Set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    plugin.route_case = check_case
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_trivial_case() -> None:
    assert _results("") == set()


def test_route_snake_case() -> None:
    assert (
        _results(
            dedent(
                """\
                @router.get("/snake_case_route")
                def endpoint() -> None:
                    pass
                """
            )
        )
        == set()
    )


def test_route_snake_case_multi() -> None:
    assert (
        _results(
            dedent(
                """\
                @router.get("/snake_case_route/second_snake_case")
                def endpoint() -> None: ...
                """
            )
        )
        == set()
    )


# Since this test has a mix of different cases, it should fail
# on all supported cases.
@pytest.mark.parametrize("check_case", list(SupportedCase))
def test_mixed_routes(check_case) -> None:
    assert (
        _results(
            dedent(
                """\
                @router.get("/snake_case_route/secondCamelCase")
                def endpoint() -> None: ...
                """
            ),
            check_case=check_case,
        )
        == {
            f"1:12 FRC001 Route path not {check_case.value} case",
        }
    )


def test_route_camel_case() -> None:
    assert (
        _results(
            dedent(
                """\
                @router.get("/CamelCaseRoute")
                def endpoint() -> None: ...
                """
            )
        )
        == {
            "1:12 FRC001 Route path not snake case",
        }
    )


def test_route_camel_case_passes() -> None:
    assert (
        _results(
            dedent(
                """\
                @router.get("/camelCaseRoute")
                def endpoint() -> None: ...
                """
            ),
            check_case=SupportedCase.CAMEL,
        )
        == set()
    )


def test_route_camel_case_multi() -> None:
    assert (
        _results(
            dedent(
                """\
                @router.get("/camelCaseRoute/secondCamelCaseRoute")
                def endpoint() -> None: ...
                """
            ),
            check_case=SupportedCase.CAMEL,
        )
        == set()
    )
