import pytest

from interest_tracker import main


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_can_output_top_level_help(capsys, option):
    help_output = [
        "usage: interest-tracker.py <command> [<args>]",
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
