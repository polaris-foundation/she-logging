import re
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from typing import Dict, Tuple

import pytest

SCRIPT_FOLDER = Path(__file__).parent / "scripts"


def clean_logs(output: bytes, script: Path) -> str:
    cleaned = (
        output.decode("utf8")
        .replace(str(script), "📜")
        .replace(str(script.name), "📜")
        .replace(str(script.with_suffix("").name), "📜")
        .strip("\n")
    )
    cleaned = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[.,]\d{3,6}", "📅", cleaned)
    cleaned = re.sub(r'"lineno": \d+', r'"lineno": #', cleaned)
    cleaned = re.sub(r":\d+:", r":#:", cleaned)
    return cleaned


def run(script_name: str, env: Dict[str, str]) -> Tuple[int, str, str]:
    script: Path = SCRIPT_FOLDER / script_name
    proc = subprocess.Popen(
        [sys.executable, script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    stdout, stderr = proc.communicate()

    output = stdout.decode("utf8").replace(str(SCRIPT_FOLDER), "").strip("\n")
    output = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[.,]\d{3,6}", "📅", output)

    return (
        proc.returncode,
        clean_logs(stdout, script=script),
        clean_logs(stderr, script=script),
    )


@pytest.mark.parametrize(
    "log_level,log_format,expected_stdout,expected_stderr",
    [
        (
            "info",
            "json",
            """
                {"requestID": null, "message": "she info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "she warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
            """,
            "",
        ),
        (
            "info",
            "plain",
            """
                [📅] INFO [None] in 📜:#: she info message
                [📅] WARNING [None] in 📜:#: she warning message
                [📅] INFO [None] in 📜:#: pylogging info message
                [📅] WARNING [None] in 📜:#: pylogging warning message
            """,
            "",
        ),
        (
            "debug",
            "json",
            """
                {"requestID": null, "message": "she debug message", "timestamp": "📅", "severity": "DEBUG", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "she info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "she warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging debug message", "timestamp": "📅", "severity": "DEBUG", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
            """,
            "",
        ),
        (
            "debug",
            "plain",
            """
                    [📅] DEBUG [None] in 📜:#: she debug message
                    [📅] INFO [None] in 📜:#: she info message
                    [📅] WARNING [None] in 📜:#: she warning message
                    [📅] DEBUG [None] in 📜:#: pylogging debug message
                    [📅] INFO [None] in 📜:#: pylogging info message
                    [📅] WARNING [None] in 📜:#: pylogging warning message
                """,
            "",
        ),
    ],
    ids=["info-json", "info-plain", "debug-json", "debug-plain"],
)
def test_simple_she_logging(
    log_level: str, log_format: str, expected_stdout: str, expected_stderr: str
) -> None:
    expected_stdout = dedent(expected_stdout).strip("\n")
    expected_stderr = dedent(expected_stderr).strip("\n")
    returncode, stdout, stderr = run(
        "simple-she-logging.py", env={"LOG_LEVEL": log_level, "LOG_FORMAT": log_format}
    )

    assert returncode == 0
    assert stdout == expected_stdout
    assert stderr == expected_stderr


@pytest.mark.parametrize(
    "log_level,log_format,expected_stdout,expected_stderr",
    [
        (
            "info",
            "json",
            """
                {"requestID": null, "message": "she info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "she warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
            """,
            "DEBUG:Basic config\nWARNING:she-logging overwriting existing logging configuration",
        ),
        (
            "info",
            "plain",
            """
                [📅] INFO [None] in 📜:#: she info message
                [📅] WARNING [None] in 📜:#: she warning message
                [📅] INFO [None] in 📜:#: pylogging info message
                [📅] WARNING [None] in 📜:#: pylogging warning message
            """,
            "DEBUG:Basic config\nWARNING:she-logging overwriting existing logging configuration",
        ),
        (
            "debug",
            "json",
            """
                {"requestID": null, "message": "she debug message", "timestamp": "📅", "severity": "DEBUG", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "she info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "she warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging debug message", "timestamp": "📅", "severity": "DEBUG", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
            """,
            "DEBUG:Basic config\nWARNING:she-logging overwriting existing logging configuration",
        ),
        (
            "debug",
            "plain",
            """
                [📅] DEBUG [None] in 📜:#: she debug message
                [📅] INFO [None] in 📜:#: she info message
                [📅] WARNING [None] in 📜:#: she warning message
                [📅] DEBUG [None] in 📜:#: pylogging debug message
                [📅] INFO [None] in 📜:#: pylogging info message
                [📅] WARNING [None] in 📜:#: pylogging warning message
            """,
            "DEBUG:Basic config\nWARNING:she-logging overwriting existing logging configuration",
        ),
    ],
    ids=["info-json", "info-plain", "debug-json", "debug-plain"],
)
def test_basic_config_plus_she_logging(
    log_level: str, log_format: str, expected_stdout: str, expected_stderr: str
) -> None:
    expected_stdout = dedent(expected_stdout).strip("\n")
    expected_stderr = dedent(expected_stderr).strip("\n")
    returncode, stdout, stderr = run(
        "basic-config-plus-she-logging.py",
        env={"LOG_LEVEL": log_level, "LOG_FORMAT": log_format},
    )

    assert returncode == 0
    assert stdout == expected_stdout
    assert stderr == expected_stderr


@pytest.mark.parametrize(
    "log_level,log_format,expected_stdout,expected_stderr",
    [
        (
            "info",
            "json",
            """
                {"requestID": null, "message": "she info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "she warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
            """,
            "WARNING:Basic config - warning\nWARNING:she-logging overwriting existing logging configuration",
        ),
        (
            "info",
            "plain",
            """
                [📅] INFO [None] in 📜:#: she info message
                [📅] WARNING [None] in 📜:#: she warning message
                [📅] INFO [None] in 📜:#: pylogging info message
                [📅] WARNING [None] in 📜:#: pylogging warning message
            """,
            "WARNING:Basic config - warning\nWARNING:she-logging overwriting existing logging configuration",
        ),
        (
            "debug",
            "json",
            """
                {"requestID": null, "message": "she debug message", "timestamp": "📅", "severity": "DEBUG", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "she info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "she warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging debug message", "timestamp": "📅", "severity": "DEBUG", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging info message", "timestamp": "📅", "severity": "INFO", "pathname": "📜", "lineno": #}
                {"requestID": null, "message": "pylogging warning message", "timestamp": "📅", "severity": "WARNING", "pathname": "📜", "lineno": #}
            """,
            "WARNING:Basic config - warning\nWARNING:she-logging overwriting existing logging configuration",
        ),
        (
            "debug",
            "plain",
            """
                [📅] DEBUG [None] in 📜:#: she debug message
                [📅] INFO [None] in 📜:#: she info message
                [📅] WARNING [None] in 📜:#: she warning message
                [📅] DEBUG [None] in 📜:#: pylogging debug message
                [📅] INFO [None] in 📜:#: pylogging info message
                [📅] WARNING [None] in 📜:#: pylogging warning message
            """,
            "WARNING:Basic config - warning\nWARNING:she-logging overwriting existing logging configuration",
        ),
    ],
    ids=["info-json", "info-plain", "debug-json", "debug-plain"],
)
def test_basic_config_no_level_plus_she_logging(
    log_level: str, log_format: str, expected_stdout: str, expected_stderr: str
) -> None:
    """Basic config when no level is given explicitly should have the level overridden by she-logging"""
    expected_stdout = dedent(expected_stdout).strip("\n")
    expected_stderr = dedent(expected_stderr).strip("\n")
    returncode, stdout, stderr = run(
        "basic-config-no-level-plus-she-logging.py",
        env={"LOG_LEVEL": log_level, "LOG_FORMAT": log_format},
    )

    assert returncode == 0
    assert stdout == expected_stdout
    assert stderr == expected_stderr
