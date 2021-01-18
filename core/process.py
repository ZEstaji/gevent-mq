import collections

import gevent
from gevent.subprocess import Popen, PIPE, TimeoutExpired

from core.errors import CommandTimeoutError, CommandError

stub_output = collections.namedtuple("StubOutput", "command out error return_code")


def call_stub(command, by_shell=False, cwd=None):
    """ Executes a shell command

    Args:
        command (str): Shell command
        by_shell (bool): True if command should be executed using shell
        cwd (str): Working directory to run command


    Returns:
        gevent.subprocess.Popen
    """

    try:
        if not by_shell:

            array_command = command.split()
            proc = Popen(
                array_command,
                stdout=PIPE,
                stderr=PIPE,
                cwd=cwd,
                # set universal_newlines in True to get data in text, not binary
                universal_newlines=True,
                # ignore errors while encoding response. not all responses decodable in 'utf-8'
                errors="ignore",
            )
        else:
            proc = Popen(
                command.strip(),
                shell=True,
                stdout=PIPE,
                # set universal_newlines in True to get data in text, not binary
                universal_newlines=True,
                # ignore errors while encoding response. not all responses decodable in 'utf-8'
                errors="ignore",
                stderr=PIPE,
                executable="/bin/bash",
                cwd=cwd,
            )
        return proc
    except Exception as err:
        raise err


def run(command, by_shell=True, ignore_return_code=True, cwd=None, timeout=None):
    """

    Args:
        command (str): shell command
        by_shell (bool): True if command should be executed using shell
        ignore_return_code (bool): True if
        cwd (str):
        timeout (int):

    Returns:

    """

    try:
        command_out = command_error = []
        proc = call_stub(command, by_shell=by_shell, cwd=cwd)

        def print_stdout():
            for line in proc.stdout:
                command_out.append(line)

        def print_stderr():
            for line in proc.stderr:
                command_error.append(line)

        print(f"command -- {command} -- started...")
        g1 = gevent.spawn(print_stdout)
        g2 = gevent.spawn(print_stderr)

        return_code = proc.wait(timeout=timeout)
        g1.kill()
        g2.kill()
        print(f"command -- {command} -- finished...")
    except TimeoutExpired:
        raise CommandTimeoutError(command, timeout)

    if ignore_return_code is False and return_code is not 0:
        raise CommandError(command, command_out, command_error, return_code)

    return stub_output(command=command, out=command_out, error=command_error, return_code=return_code)
