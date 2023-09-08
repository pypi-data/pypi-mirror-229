# -*- coding: utf-8 -*-
# Copyright © 2023 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

import argparse
import os
import sys
import warnings

# We'll need to extern this function or investigate replacing it with shutil.which()
# "distutils is deprecated with removal planned for Python 3.12. See the What’s
# New entry for more information."
with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        "The distutils package is deprecated and slated for removal in Python 3.12. Use setuptools or check PEP 632 for potential alternatives",
        DeprecationWarning,
    )

    from distutils.spawn import find_executable  # pylint: disable=deprecated-module

from contrast import __file__
from contrast.configuration import AgentConfig
from contrast_rewriter import ENABLE_REWRITER, REWRITE_FOR_PYTEST

DESCRIPTION = """
The command-line runner for the Contrast Python Agent.
"""

USAGE = "%(prog)s [-h] -- cmd [cmd ...]"

EPILOG = """
Insert this command before the one you usually use to start your webserver
to apply Contrast's instrumentation. See our public documentation for details:
https://docs.contrastsecurity.com/en/python.html
"""


def runner() -> None:
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        usage=USAGE,
        epilog=EPILOG,
    )
    parser.add_argument(
        "--rewrite-for-pytest", action="store_true", help=argparse.SUPPRESS
    )
    # if you add public arguments here, update USAGE accordingly
    parser.add_argument("cmd", nargs="+")

    parsed = parser.parse_args()

    config = AgentConfig()

    loader_path = os.path.join(os.path.dirname(__file__), "loader")
    os.environ["PYTHONPATH"] = os.path.pathsep.join([loader_path] + sys.path)

    if parsed.rewrite_for_pytest:
        os.environ[REWRITE_FOR_PYTEST] = "true"
    elif config.should_rewrite:
        os.environ[ENABLE_REWRITER] = "true"

    os.execl(find_executable(parsed.cmd[0]), *parsed.cmd)
