import ast
import re
import sys
from typing import Any
from typing import Generator
from typing import Tuple
from typing import Type
from typing import Union

if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: list[tuple[int, int, str]] = []

    def is_snake_case(self, s: str) -> bool:
        SNAKE_CASE_TEST_RE = re.compile(r"^[a-z][a-z0-9]+(_[a-z0-9]+)*$")
        if s.startswith("/"):
            s = s.lstrip("/")
        return all(SNAKE_CASE_TEST_RE.match(substr) for substr in s.split("/"))

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
                path = decorator.args[0]
                if not self.is_snake_case(path.value):
                    self.errors.append(
                        (path.lineno, path.col_offset, "Value not snake case")
                    )


class Plugin:
    name = "flake8_fastapi_route_case"
    version = importlib_metadata.version(__name__)

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    @staticmethod
    def add_options(option_manager: Any) -> None:
        option_manager.add_option(
            "--case",
            type=str,
            default="snake",
            parse_from_config=True,
            metavar="CASE",
            help=(
                "Case styling that routes should conform to, " "(default: %(default)s)"
            ),
        )

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)

        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)
        return None
