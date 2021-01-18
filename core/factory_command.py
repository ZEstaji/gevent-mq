from core.errors import ValidationFailure
from core.process import run


class Command(object):
    def __init__(self):
        """This class make an os or math command base on the input command

        """
        self.result = ""

    # Create based on command dict:
    def factory(command_dict):
        if command_dict["command_type"] == "os":
            Command.validate_os_command(command_dict)
            return OsCommand(command_dict)
        elif command_dict["command_type"] == "compute":
            Command.validate_math_command(command_dict)
            return MathCommand(command_dict)
        else:
            raise ValidationFailure(f"invalid command {command_dict}")

    @staticmethod
    def validate_os_command(command_dict):
        if "command_name" not in command_dict or "parameters" not in command_dict:
            raise ValidationFailure(
                f'command {command_dict} does not match to {{"command_type": "os", "command_name": "cmd", "parameters": []}}')
        return True

    @staticmethod
    def validate_math_command(command_dict):
        if "expression" not in command_dict:
            raise ValidationFailure(
                f'command {command_dict} does not match to {{"command_type": "compute", "expression": "math_exp}}')
        try:
            eval(command_dict["expression"])
        except Exception as e:
            raise ValidationFailure(f'expression of command {command_dict} is not valid to compute')
        return True

    factory = staticmethod(factory)


class OsCommand(Command):
    def __init__(self, command_dict):
        self.os_command = f'{command_dict["command_name"]} {" ".join(command_dict["parameters"])}' if len(
            command_dict["parameters"]) > 0 else command_dict["command_name"]

    def execute(self):
        cmd = self.os_command
        return run(command=cmd)

    def format_output(self, result):
        self.result = "".join(result.out) or "".join(result.error)
        return {
            "given_os_command": self.os_command,
            "result": self.result,
        }


class MathCommand(Command):
    def __init__(self, command_dict):
        self.math_command = command_dict["expression"]

    def execute(self):
        self.result = eval(self.math_command)
        return self.result

    def format_output(self, result):
        return {
            "given_math_expression": self.math_command,
            "result": self.result,
        }
