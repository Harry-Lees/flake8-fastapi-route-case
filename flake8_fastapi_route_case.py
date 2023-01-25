import argparse
import ast
import re
import sys
from enum import Enum
from typing import Any
from typing import Generator
from typing import Tuple
from typing import Type
from typing import Union

if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


class SupportedCase(Enum):
    SNAKE = "snake"
    CAMEL = "camel"


patterns = {
    # snake_case regex
    SupportedCase.SNAKE: re.compile(r"^[a-z][a-z0-9]+(_[a-z0-9]+)*$"),
    # lowerCamelCase regex
    SupportedCase.CAMEL: re.compile(r"[a-z]+((\d)|([A-Z0-9][a-z0-9]+))*([A-Z])?"),
}


class Visitor(ast.NodeVisitor):
    def __init__(self, route_case: SupportedCase) -> None:
        self.errors: list[tuple[int, int, str]] = []
        self.route_case = route_case

    def match_case(self, path: str, pattern: re.Pattern) -> bool:
        if path.startswith("/"):
            path = path.lstrip("/")
        for subpath in path.split("/"):
            # Skip route params e.g. /users/{user_id}
            if subpath.startswith("{") and subpath.endswith("}"):
                continue

            if not pattern.fullmatch(subpath):
                return False
        return True

    def generic_visit(self, node: ast.AST) -> None:
        for node in ast.walk(node):
            if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                self._visit_func(node)

    def _visit_func(self, node: Union[ast.AsyncFunctionDef, ast.FunctionDef]):
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr in ("get", "post", "put", "delete")
            ):
                route = decorator.args[0]
                if isinstance(route, ast.Constant) and not self.match_case(
                    route.value, patterns[self.route_case]
                ):
                    self.errors.append(
                        (
                            route.lineno,
                            route.col_offset,
                            f"FRC001 Route path not {self.route_case.value} case",
                        )
                    )


class Plugin:
    name = "flake8_fastapi_route_case"
    version = importlib_metadata.version(__name__)
    route_case = SupportedCase.SNAKE

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    @staticmethod
    def add_options(option_manager: Any) -> None:
        option_manager.add_option(
            "--route-case",
            type=SupportedCase,
            default=SupportedCase.SNAKE,
            parse_from_config=True,
            metavar="route_case",
            help=(
                "Case styling that routes should conform to, "
                "supported options: {} (default: {})".format(
                    ", ".join(case.value for case in list(SupportedCase)),
                    SupportedCase.SNAKE.value,
                )
            ),
        )

    @classmethod
    def parse_options(cls, options: argparse.Namespace) -> None:
        cls.route_case = options.route_case

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor(self.route_case)
        visitor.visit(self._tree)

        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)
        return None
