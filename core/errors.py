class ApplicationError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


class CommandError(ApplicationError):
    def __init__(self, command, command_out, command_error, return_code):
        self.msg = f"command -- {command} -- failed with return code {return_code} and stderr {command_out or command_error}"


class CommandTimeoutError(ApplicationError):
    def __init__(self, command, timeout):
        self.msg = f"command -- {command} -- timeouted after {timeout} seconds"


class ValidationFailure(ApplicationError):
    def __bool__(self):
        return False
