import pathlib
import shutil
import tempfile

import pytest

from saltfactories.utils import tempfiles


@pytest.mark.parametrize("name", ["foo", "foo/bar"])
def test_temp_directory_with_name(name):
    try:
        expected_path = pathlib.Path(tempfile.gettempdir()) / name
        assert expected_path.is_dir() is False
        with tempfiles.temp_directory(name=name) as tpath:
            assert tpath.is_dir()
            assert tpath == expected_path
        assert expected_path.is_dir() is False
    finally:
        shutil.rmtree(str(expected_path), ignore_errors=True)


def test_temp_directory_without_name():
    try:
        expected_parent_path = pathlib.Path(tempfile.gettempdir())
        with tempfiles.temp_directory() as tpath:
            assert tpath.is_dir()
            assert tpath.parent == expected_parent_path
        assert tpath.is_dir() is False
    finally:
        shutil.rmtree(str(tpath), ignore_errors=True)


def test_temp_directory_with_basepath(tmp_path):
    with tempfiles.temp_directory(basepath=tmp_path) as tpath:
        assert tpath.is_dir()
        assert str(tpath.parent) == str(tmp_path)
    assert tpath.is_dir() is False
    assert tmp_path.is_dir() is True


@pytest.mark.parametrize("name", ["foo.txt", "foo/bar.txt"])
def test_temp_file_with_name(tmp_path, name):
    expected_path = tmp_path / name
    assert expected_path.is_file() is False
    with tempfiles.temp_file(name=name, directory=tmp_path) as tpath:
        assert tpath.is_file()
        assert str(tpath) == str(expected_path)
    assert expected_path.is_file() is False


def test_temp_file_without_name(tmp_path):
    expected_parent_path = tmp_path
    with tempfiles.temp_file(directory=tmp_path) as tpath:
        assert tpath.is_file()
        assert str(tpath.parent) == str(expected_parent_path)
    assert tpath.is_file() is False


@pytest.mark.parametrize("name", ["foo.txt", "foo/bar.txt"])
def test_temp_file_with_name_no_directory(name):
    try:
        expected_path = pathlib.Path(tempfile.gettempdir()) / name
        assert expected_path.is_file() is False
        with tempfiles.temp_file(name=name) as tpath:
            assert tpath.is_file()
            assert str(tpath) == str(expected_path)
        assert expected_path.is_file() is False
    finally:
        shutil.rmtree(str(expected_path), ignore_errors=True)


def test_temp_file_without_name_no_directory():
    try:
        expected_parent_path = pathlib.Path(tempfile.gettempdir())
        with tempfiles.temp_file() as tpath:
            assert tpath.is_file()
            assert str(tpath.parent) == str(expected_parent_path)
        assert tpath.is_file() is False
    finally:
        shutil.rmtree(str(tpath), ignore_errors=True)


def test_temp_file_does_not_delete_non_empty_directories(tmp_path):
    expected_parent_path = tmp_path
    level1_path = expected_parent_path / "level1"
    level2_path = level1_path / "level2"
    assert not level1_path.is_dir()
    assert not level2_path.is_dir()
    with tempfiles.temp_file("level1/foo.txt", directory=expected_parent_path) as tpath1:
        assert tpath1.is_file()
        assert level1_path.is_dir()
        assert not level2_path.is_dir()
        with tempfiles.temp_file("level1/level2/foo.txt", directory=expected_parent_path) as tpath2:
            assert tpath2.is_file()
            assert level1_path.is_dir()
            assert level2_path.is_dir()
        assert not tpath2.is_file()
        assert not level2_path.is_dir()
        assert tpath1.is_file()
        assert level1_path.is_dir()
    assert not level1_path.is_dir()
    assert not level2_path.is_dir()


@pytest.mark.parametrize("strip_first_newline", [True, False])
def test_temp_file_contents(strip_first_newline):
    contents = """
     These are the contents, first line
      Second line
    """
    if strip_first_newline:
        expected_contents = "These are the contents, first line\n Second line\n"
    else:
        expected_contents = "\nThese are the contents, first line\n Second line\n"
    with tempfiles.temp_file(contents=contents, strip_first_newline=strip_first_newline) as tpath:
        assert tpath.is_file()
        assert tpath.read_text() == expected_contents
