import pytest

from unittest.mock import patch

from interest_tracker import main, SqliteHandler


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_can_output_top_level_help(capsys, option):
    help_output = [
        "usage: interest_tracker.py <command> [<args>]",
        "Available commands are:",
        "log         Register a new hacking interest",
        "visualize   Visualize existing interests",
        "Track your hacking sessions with this simple cli app.",
        "positional arguments:",
        "command     Subcommand to run",
        "optional arguments:",
        "-h, --help  show this help message and exit",
    ]
    try:
        main(["./interest_tracker.py", option])
    except SystemExit:
        pass
    output = capsys.readouterr().out
    for line in help_output:
        assert line in output


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_can_output_log_command_help(capsys, option):
    log_command_help_output = [
        "usage: __main__.py [-h] -e EFFORT [-t TAGS] LOG",
        "Register a new hacking interest",
        "positional arguments:",
        "  LOG                   What you've been hacking at",
        "optional arguments:",
        "  -h, --help            show this help message and exit",
        "-e EFFORT, --effort EFFORT",
        "How long you've been at it (HH:MM)",
        "-t TAGS, --tags TAGS  Comma separated tags to group your interests",
    ]
    try:
        main(["./interest_tracker.py", "log", option])
    except SystemExit:
        pass
    output = capsys.readouterr().out
    for line in log_command_help_output:
        assert line in output


def test_log_command_requires_log_and_effort(capsys):
    with pytest.raises(SystemExit, match=r"2"):
        main(["./interest_tracker.py", "log"])

    captured = capsys.readouterr()
    assert (
        "error: the following arguments are required: LOG, -e/--effort" in captured.err
    )
    assert "error: the following arguments are required: command" not in captured.err


def test_log_command_requires_effort(capsys):
    with pytest.raises(SystemExit, match=r"2"):
        main(
            [
                "./interest_tracker.py",
                "log",
                "testing argparser with pytest, capturing syserr/sysout in test cases",
            ]
        )

    captured = capsys.readouterr()

    assert "error: the following arguments are required: -e/--effort" in captured.err


def test_interest_can_be_registered_with_log_command_without_tags():
    with patch.object(SqliteHandler, "add_interest") as mock_add_interest:
        try:
            main(
                [
                    "./interest_tracker.py",
                    "log",
                    "registering interest from tests!",
                    "-e",
                    "00:15",
                ]
            )
        except SystemExit:
            pass

        mock_add_interest.assert_called_with(
            log="registering interest from tests!", effort=900, tags=[]
        )


def test_interest_can_be_registered_with_log_command_with_tags():
    with patch.object(SqliteHandler, "add_interest") as mock_add_interest:
        try:
            main(
                [
                    "./interest_tracker.py",
                    "log",
                    "registering interest from tests!",
                    "-e",
                    "00:12",
                    "-t",
                    "pytest,mocks,tests",
                ]
            )
        except SystemExit:
            pass

        mock_add_interest.assert_called_with(
            log="registering interest from tests!",
            effort=720,
            tags=["pytest", "mocks", "tests"],
        )
