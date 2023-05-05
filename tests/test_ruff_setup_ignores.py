from pathlib import Path
from textwrap import dedent

import pytest

import ruff_setup_ignores


@pytest.fixture
def pyproject_tmp(tmp_path_factory):
    def wrapper(filename):
        content = Path(filename).read_text()
        tmpfile = tmp_path_factory.mktemp("ruff_setup_ignores") / "pyproject.toml"
        Path(tmpfile).write_text(content)
        return tmpfile

    return wrapper


@pytest.fixture
def ruff_tmp(tmp_path_factory):
    def wrapper(filename):
        content = Path(filename).read_text()
        tmpfile = tmp_path_factory.mktemp("ruff_setup_ignores") / "ruff.toml"
        Path(tmpfile).write_text(content)
        return tmpfile

    return wrapper


@pytest.mark.parametrize(
    "toml_file",
    [
        "tests/toml_files/pyprojecttoml_without_per_file_ignores.toml",
        "tests/toml_files/pyprojecttoml_with_per_file_ignores.toml",
    ],
)
def test_pyproject_toml(pyproject_tmp, toml_file):
    toml_file = pyproject_tmp(toml_file)
    ruff_setup_ignores.update_toml(toml_file, {"bar.py": ["E501"]})

    expected = dedent(
        """
    [foo]
    foo = "bar"

    [tool.ruff.per-file-ignores]
    "bar.py" = [ "E501",]
    """
    ).lstrip()

    assert Path(toml_file).read_text() == expected


@pytest.mark.parametrize(
    "toml_file",
    [
        "tests/toml_files/rufftoml_without_per_file_ignores.toml",
        "tests/toml_files/rufftoml_with_per_file_ignores.toml",
    ],
)
def test_ruff_toml(ruff_tmp, toml_file):
    toml_file = ruff_tmp(toml_file)
    ruff_setup_ignores.update_toml(toml_file, {"bar.py": ["E501"]})

    expected = dedent(
        """
    foo = "bar"

    [per-file-ignores]
    "bar.py" = [ "E501",]
    """
    ).lstrip()

    assert Path(toml_file).read_text() == expected


@pytest.mark.parametrize(
    "toml_file",
    [
        "tests/toml_files/rufftoml_with_tool_ruff_prefix.toml",
    ],
)
def test_ruff_toml_with_tool_ruff_prefix(ruff_tmp, toml_file):
    toml_file = ruff_tmp(toml_file)
    ruff_setup_ignores.update_toml(toml_file, {"bar.py": ["E501"]})

    expected = dedent(
        """
    [tool.ruff]
    foo = "bar"

    [tool.ruff.per-file-ignores]
    "bar.py" = [ "E501",]
    """
    ).lstrip()

    assert Path(toml_file).read_text() == expected
