"""Tests for `common.py`."""

from __future__ import annotations

import ast
import logging
import os.path
import sys
import textwrap
from pathlib import Path

import pytest

from pip_check_reqs import __version__, common


@pytest.mark.parametrize(
    ("path", "result"),
    [
        ("/", ""),
        ("__init__.py", ""),  # a top-level file like this has no package name
        ("/__init__.py", ""),  # no package name
        ("spam/__init__.py", "spam"),
        ("spam/__init__.pyc", "spam"),
        ("spam/__init__.pyo", "spam"),
        ("ham/spam/__init__.py", "ham/spam"),
        ("/ham/spam/__init__.py", "/ham/spam"),
    ],
)
def test_is_package_file(path: str, result: str) -> None:
    assert common.is_package_file(path=path) == result


def test_found_module() -> None:
    found_module = common.FoundModule(modname="spam", filename="ham")
    assert found_module.modname == "spam"
    assert found_module.filename == str(Path("ham").resolve())
    assert not found_module.locations


@pytest.mark.parametrize(
    ("stmt", "result"),
    [
        ("import ast", ["ast"]),
        ("import ast, pathlib", ["ast", "pathlib"]),
        ("from pathlib import Path", ["pathlib"]),
        ("from string import hexdigits", ["string"]),
        ("import urllib.request", ["urllib"]),
        # don't break because bad programmer imported the file we are in
        ("import spam", []),
        ("from .foo import bar", []),  # don't break on relative imports
        ("from . import baz", []),
    ],
)
def test_import_visitor(stmt: str, result: list[str]) -> None:
    vis = common._ImportVisitor(  # noqa: SLF001,E501, pylint: disable=protected-access
        ignore_modules_function=common.ignorer(ignore_cfg=[]),
    )
    vis.set_location(location="spam.py")
    vis.visit(ast.parse(stmt))
    finalise_result = vis.finalise()
    assert set(finalise_result.keys()) == set(result)
    for value in finalise_result.values():
        assert str(value.filename) not in sys.path
        assert Path(value.filename).name != "__init__.py"
        assert Path(value.filename).is_absolute()
        assert Path(value.filename).exists()


def test_pyfiles_file(tmp_path: Path) -> None:
    python_file = tmp_path / "example.py"
    python_file.touch()
    assert list(common.pyfiles(root=python_file)) == [python_file]


def test_pyfiles_file_no_dice(tmp_path: Path) -> None:
    not_python_file = tmp_path / "example"
    not_python_file.touch()

    with pytest.raises(
        expected_exception=ValueError,
        match=f"{not_python_file} is not a python file or directory",
    ):
        list(common.pyfiles(root=not_python_file))


def test_pyfiles_package(tmp_path: Path) -> None:
    python_file = tmp_path / "example.py"
    nested_python_file = tmp_path / "subdir" / "example.py"
    not_python_file = tmp_path / "example"

    python_file.touch()
    nested_python_file.parent.mkdir()
    nested_python_file.touch()

    not_python_file.touch()

    assert list(common.pyfiles(root=tmp_path)) == [
        python_file,
        nested_python_file,
    ]


@pytest.mark.parametrize(
    ("ignore_ham", "ignore_hashlib", "expect", "locs"),
    [
        (
            False,
            False,
            ["ast", "pathlib", "hashlib", "sys"],
            [
                ("spam.py", 2),
                ("ham.py", 2),
            ],
        ),
        (
            False,
            True,
            ["ast", "pathlib", "sys"],
            [("spam.py", 2), ("ham.py", 2)],
        ),
        (True, False, ["ast", "sys"], [("spam.py", 2)]),
        (True, True, ["ast", "sys"], [("spam.py", 2)]),
    ],
)
def test_find_imported_modules(
    *,
    caplog: pytest.LogCaptureFixture,
    ignore_ham: bool,
    ignore_hashlib: bool,
    expect: list[str],
    locs: list[tuple[str, int]],
    tmp_path: Path,
) -> None:
    root = tmp_path
    spam = root / "spam.py"
    ham = root / "ham.py"

    spam_file_contents = textwrap.dedent(
        """\
        from __future__ import braces
        import ast, sys
        from . import friend
        """,
    )
    ham_file_contents = textwrap.dedent(
        """\
        from pathlib import Path
        import ast, hashlib
        """,
    )

    spam.write_text(data=spam_file_contents)
    ham.write_text(data=ham_file_contents)

    caplog.set_level(logging.INFO)

    def ignore_files(path: str) -> bool:
        if Path(path).name == "ham.py" and ignore_ham:
            return True
        return False

    def ignore_mods(module: str) -> bool:
        if module == "hashlib" and ignore_hashlib:
            return True
        return False

    result = common.find_imported_modules(
        paths=[root],
        ignore_files_function=ignore_files,
        ignore_modules_function=ignore_mods,
    )
    assert set(result) == set(expect)
    absolute_locations = result["ast"].locations
    relative_locations = [
        (str(Path(item[0]).relative_to(root)), item[1])
        for item in absolute_locations
    ]
    assert sorted(relative_locations) == sorted(locs)

    if ignore_ham:
        assert caplog.records[0].message == f"ignoring: {os.path.relpath(ham)}"


@pytest.mark.parametrize(
    ("ignore_cfg", "candidate", "result"),
    [
        ([], "spam", False),
        ([], "ham", False),
        (["spam"], "spam", True),
        (["spam"], "spam.ham", False),
        (["spam"], "eggs", False),
        (["spam*"], "spam", True),
        (["spam*"], "spam.ham", True),
        (["spam*"], "eggs", False),
        (["spam"], "/spam", True),
    ],
)
def test_ignorer(
    *,
    monkeypatch: pytest.MonkeyPatch,
    ignore_cfg: list[str],
    candidate: str,
    result: bool,
) -> None:
    monkeypatch.setattr(os.path, "relpath", lambda s: s.lstrip("/"))
    ignorer = common.ignorer(ignore_cfg=ignore_cfg)
    assert ignorer(candidate) == result


def test_find_required_modules(tmp_path: Path) -> None:
    fake_requirements_file = tmp_path / "requirements.txt"
    fake_requirements_file.write_text("foobar==1\nbarfoo==2")

    reqs = common.find_required_modules(
        ignore_requirements_function=common.ignorer(ignore_cfg=["barfoo"]),
        skip_incompatible=False,
        requirements_filename=fake_requirements_file,
    )
    assert reqs == {"foobar"}


def test_find_required_modules_env_markers(tmp_path: Path) -> None:
    fake_requirements_file = tmp_path / "requirements.txt"
    fake_requirements_file.write_text(
        'spam==1; python_version<"2.0"\nham==2;\neggs==3\n',
    )

    reqs = common.find_required_modules(
        ignore_requirements_function=common.ignorer(ignore_cfg=[]),
        skip_incompatible=True,
        requirements_filename=fake_requirements_file,
    )
    assert reqs == {"ham", "eggs"}


def test_version_info_shows_version_number() -> None:
    assert __version__ in common.version_info()
