from typing import Any
from .utils import Node
import yaml


TSTACK = list[tuple["Node", dict[Any, Any]]]


class Config:
    def __init__(self, filename: str) -> None:
        self._filename = filename

    @property
    def filename(self) -> str:
        return self._filename

    def read(self, parent=Node()) -> Node:
        data = self._read_file()
        stack = [(parent, data)]
        self._dfs(stack)
        return parent

    def _read_file(self) -> dict[Any, Any]:
        with open(self._filename, "r") as f:
            data = yaml.safe_load(f)
            if len(data) == 0:
                raise EmptyFileError()
        return data

    def _dfs(self, stack: TSTACK) -> None:
        while stack:
            root, data = stack.pop()
            self._iterate_and_attach_to_root_node(root, data, stack)

    def _iterate_and_attach_to_root_node(
        self, root: Node, data: dict[Any, Any], stack: TSTACK
    ) -> None:
        for x in data:
            if isinstance(data[x], dict):
                child_node = Node()
                setattr(root, x, child_node)
                stack.append((child_node, data[x]))
            else:
                setattr(root, x, data[x])


class EmptyFileError(Exception):
    def __init__(self, message: str = "Empty file") -> None:
        super().__init__(message)
