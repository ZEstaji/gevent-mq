import collections
from unittest import mock

import pytest

from core.errors import ValidationFailure
from core.factory_command import Command, OsCommand, MathCommand


class TestFactoryCommand:
    def test_command_type_os(self):
        command_dict = {
            "command_type": "os",
            "command_name": "sleep 4 ; ls -ll",
            "parameters": [""]
        }
        assert isinstance(Command.factory(command_dict), OsCommand)

    def test_command_type_math(self):
        command_dict = {
            "command_type": "compute",
            "expression": "20+(30*(4+5))"
        }
        assert isinstance(Command.factory(command_dict), MathCommand)

    def test_command_type_math_validate_1(self):
        command_dict = {
            "command_type": "compute",

        }
        with pytest.raises(ValidationFailure,
                           match=f'command {command_dict} does not match to {{"command_type": "compute", "expression": "math_exp}}'):
            Command.factory(command_dict)

    def test_command_type_math_validate_2(self):
        command_dict = {
            "command_type": "compute",
            "expression": "wrong"
        }
        with pytest.raises(ValidationFailure, match=f'expression of command {command_dict} is not valid to compute'):
            Command.factory(command_dict)

    def test_command_type_os_validate(self):
        command_dict = {
            "command_type": "os",
            "command_name": "sleep 4 ; ls -ll",
            "parameters": [""]
        }
        assert isinstance(Command.factory(command_dict), OsCommand)

    @mock.patch("core.factory_command.run")
    def test_os_output_format(self, mock_process_run):
        stub_output = collections.namedtuple("StubOutput", "command out error return_code")
        mock_process_run.return_value = stub_output(command="ls", out="Estaji", error="", return_code=0)
        commands = [{
            "command_type": "compute",
            "expression": "20+(30*(4+5))"
        }, {
            "command_type": "os",
            "command_name": "sleep 4 ; ls -ll",
            "parameters": []
        }]
        commands_ = [Command.factory(cmd) for cmd in commands]
        output = []
        for cmd in commands_:
            output.append(cmd.format_output(cmd.execute()))
        print(output)
        expected_output = [{'given_math_expression': '20+(30*(4+5))', 'result': 290},
                           {'given_os_command': 'sleep 4 ; ls -ll', 'result': 'Estaji'}]
        assert output == expected_output
