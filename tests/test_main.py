from src.main import SearchShell


def make_shell(tmp_path):
    return SearchShell(
        index_path=tmp_path / "index.json",
        start_url="https://quotes.toscrape.com/",
        politeness_delay=1.0,
    )


def test_load_missing_index_prints_error(tmp_path, capsys):
    shell = make_shell(tmp_path)

    shell.do_load("")

    output = capsys.readouterr().out
    assert "Index file not found" in output


def test_print_requires_loaded_index(tmp_path, capsys):
    shell = make_shell(tmp_path)

    shell.do_print("nonsense")

    output = capsys.readouterr().out
    assert "No index loaded" in output


def test_find_requires_loaded_index(tmp_path, capsys):
    shell = make_shell(tmp_path)

    shell.do_find("good friends")

    output = capsys.readouterr().out
    assert "No index loaded" in output


# def test_print_rejects_empty_input(tmp_path, capsys):
#     shell = make_shell(tmp_path)
#     shell.index = {"nonsense": {}}
#     shell.documents = {}
#     shell.index_data = True

#     shell.do_print("")

#     output = capsys.readouterr().out
#     assert "print expects exactly one word" in output


# def test_find_rejects_empty_input(tmp_path, capsys):
#     shell = make_shell(tmp_path)
#     shell.index = {"good": {}}
#     shell.documents = {}
#     shell.index_data = True

#     shell.do_find("")

#     output = capsys.readouterr().out
#     assert "find expects at least one search term" in output


def test_exit_command_returns_true(tmp_path, capsys):
    shell = make_shell(tmp_path)

    result = shell.do_exit("")

    output = capsys.readouterr().out
    assert result is True
    assert "Goodbye" in output


def test_quit_command_returns_true(tmp_path, capsys):
    shell = make_shell(tmp_path)

    result = shell.do_quit("")

    output = capsys.readouterr().out
    assert result is True
    assert "Goodbye" in output
