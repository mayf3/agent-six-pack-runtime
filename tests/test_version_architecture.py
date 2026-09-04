"""Architecture properties for the packaged version-reporting boundary."""

from __future__ import annotations

import ast
import inspect
import textwrap
import tomllib
from collections.abc import Callable
from pathlib import Path

import sixpack
from sixpack import cli


def _function_tree(function: Callable[..., object]) -> ast.Module:
    return ast.parse(textwrap.dedent(inspect.getsource(function)))


def test_runtime_version_has_not_drifted_from_distribution_metadata() -> None:
    """The public package value remains tied to the declared distribution version."""
    project_root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((project_root / "pyproject.toml").read_text(encoding="utf-8"))

    assert sixpack.__version__ == project["project"]["version"]


def test_version_handler_uses_only_the_package_metadata_boundary() -> None:
    """Reject workspace access, hidden I/O, and locally duplicated metadata."""
    tree = _function_tree(cli.cmd_version)
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)
    body_nodes = [node for statement in function.body for node in ast.walk(statement)]
    calls = [node for node in body_nodes if isinstance(node, ast.Call)]
    loaded_names = {
        node.id
        for node in body_nodes
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    string_literals = {
        node.value
        for node in body_nodes
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }

    assert len(calls) == 1
    assert isinstance(calls[0].func, ast.Name)
    assert calls[0].func.id == "print"
    assert loaded_names == {"print", "__version__", "GOVERNANCE_SOURCE_COMMIT"}
    assert sixpack.__version__ not in string_literals
    assert sixpack.GOVERNANCE_SOURCE_COMMIT not in string_literals


def test_package_metadata_layer_does_not_depend_on_cli() -> None:
    """Keep the CLI dependent on package metadata, never metadata on the CLI."""
    package_tree = ast.parse(Path(sixpack.__file__).read_text(encoding="utf-8"))
    imported_modules = {
        alias.name
        for node in ast.walk(package_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    relative_imports = {
        node.module
        for node in ast.walk(package_tree)
        if isinstance(node, ast.ImportFrom)
    }

    assert "sixpack.cli" not in imported_modules
    assert "cli" not in relative_imports
