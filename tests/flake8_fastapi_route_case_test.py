import ast
from textwrap import dedent
from typing import Set

from flake8_fastapi_route_case import Plugin


def _results(s: str) -> Set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
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
                def endpoint() -> None:
                    pass
                """
            )
        )
        == set()
    )


def test_mixed_routes() -> None:
    assert (
        _results(
            dedent(
                """\
                @router.get("/snake_case_route/secondCamelCase")
                def endpoint() -> None:
                    pass
                """
            )
        )
        == {
            "1:12 Value not snake case",
        }
    )


def test_route_camel_case() -> None:
    assert (
        _results(
            dedent(
                """\
                @router.get("/CamelCaseRoute")
                def endpoint() -> None:
                    pass
                """
            )
        )
        == {
            "1:12 Value not snake case",
        }
    )
