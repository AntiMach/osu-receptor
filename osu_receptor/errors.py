class OsuReceptorError(Exception): ...


class UnknownCommandError(OsuReceptorError):
    def __init__(self, cmd, line) -> None:
        super().__init__(f"Unknown command '{cmd}' in line {line}")


class ArgumentError(OsuReceptorError):
    def __init__(self, arg, line) -> None:
        super().__init__(f"Invalid value for argument [{arg}] in line {line}")


class ArgumentCountError(OsuReceptorError):
    def __init__(self, line) -> None:
        super().__init__(f"Incorrect number of arguments in line {line}")


class BracketError(OsuReceptorError):
    def __init__(self, line) -> None:
        super().__init__(f"Missing end bracket for line {line}")
