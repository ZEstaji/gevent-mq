from unittest import mock

import pytest
from gevent import subprocess
from gevent.subprocess import PIPE

from core.errors import CommandTimeoutError, CommandError
from core.process import run, stub_output


class TestProcess:
    @mock.patch('core.process.Popen')
    def test_call_stub_timeout(self, mock_popen):
        command = "test_cmd"
        mock_popen.return_value.wait.side_effect = subprocess.TimeoutExpired('command', 25)
        with pytest.raises(CommandTimeoutError, match=f"command -- {command} -- timeouted after 3 seconds"):
            run(command, timeout=3)

    @mock.patch('core.process.Popen')
    def test_call_stub__error(self, mock_poepn):
        command = "test_cmd"
        mock_poepn.return_value.wait.return_value = -1
        mock_poepn.return_value.stderr = "error"
        with pytest.raises(CommandError):
            run(command, timeout=3, ignore_return_code=False)
