from io import TextIOWrapper
from abc import ABC, abstractmethod
from pathlib import Path

from .builders import BUILDERS
from .errors import ArgumentCountError, BracketError, UnknownCommandError, ArgumentError
from .components import Component, StaticComponent, VariableComponent, RedirectComponent
from .consts import SOURCE_PREFIX, DEFAULT_BASE, INI, TXT, HEIGHT


class OsuReceptorSkin:
    def __init__(self, name: str) -> None:
        self.name = name
        self.src = f"{SOURCE_PREFIX}-{name}"

        self.components: dict[str, Component] = {}

        self.content: list[str] = []
        self.mania: dict[str, list[str]] = {}

        self.screen_ratio: int = 16/9
        self.center: bool = False
        self.base: list[str] = list(DEFAULT_BASE)

        self.line_nr = 0
        self.commands: dict[str, Command] = {
            SettingsCommand.NAME: SettingsCommand(self),
            ComponentCommand.NAME: ComponentCommand(self),
            KeysCommand.NAME: KeysCommand(self),
        }

    def load_ini(self) -> None:
        """
        Loads the ini file
        """
        if not Path(INI).is_file():
            return

        with open(INI, "r") as fp:
            keys = None
            is_mania = False
            buffer = []

            for line in fp.readlines():
                # Strip the line
                line = line.strip()

                # Reading mania section
                if line.startswith("[Mania]"):
                    is_mania = True

                # Finished reading a mania section
                elif line.startswith("[") and is_mania:
                    self.mania[keys] = buffer
                    buffer = []
                    is_mania = False
                    keys = None

                # On mania section, detect key count
                if line.startswith("Keys:") and is_mania:
                    keys = line.removeprefix("Keys:").strip()

                # If on a mania section, append it to a buffer
                # This buffer may be deleted if a layout for it is created
                if is_mania:
                    buffer.append(line + "\n")
                else:
                    self.content.append(line + "\n")

    def process(self) -> None:
        """
        Processes the skin's commands and creates the necessary images
        """
        Path(self.name).mkdir(exist_ok=True)

        with open(f"{self.src}/{TXT}", "r") as fp:
            self.line_nr = 0

            # Read each line until no more content is read
            while (line := fp.readline()) != "":
                self.line_nr += 1
                self.process_command(fp, line.strip())

    def save_ini(self) -> None:
        """
        Saves the ini file
        """
        with open(INI, "w") as fp:
            # Write the original ini content
            fp.writelines(self.content)

            # Write each mania layout
            for content in self.mania.values():
                fp.writelines(content)

    def process_command(self, fp: TextIOWrapper, line: str) -> None:
        """
        Processes an individual command
        """
        # Skip comments and empty lines
        # Inline comments do not work
        if line == "" or line.startswith("//"):
            return

        # Split commands and arguments
        command, *args = line.lower().split()

        lines = 0

        if args[-1] == "{":
            args.pop()

            while (line := fp.readline()).strip() != "}" or line == "":
                args.append(line.strip())
                lines += 1

            lines += 1

            if line == "":
                raise BracketError(self.line_nr)

        if command in self.commands:
            command = self.commands[command]
            command.check_args(args)
            command.run(*args)

            self.line_nr += lines
        else:
            # Command doesn't exist
            raise UnknownCommandError(command, self.line_nr)


class Command(ABC):
    def __init_subclass__(cls, params: tuple) -> None:
        """
        Generates a valid parameter count tuple for the command
        """
        cls.PARAMC = params

    def __init__(self, skin: OsuReceptorSkin) -> None:
        """
        Associates the command to the skin
        """
        self.skin = skin

    def int_arg(self, name: str, arg: str) -> int:
        """
        Return argument as integer
        Raise an argument error if not possible
        """
        try:
            return int(arg)
        except ValueError:
            raise ArgumentError(name, self.skin.line_nr) from None

    def bool_arg(self, name, arg) -> bool:
        if arg == "yes":
            return True
        elif arg == "no":
            return False
        else:
            raise ArgumentError(name, self.skin.line_nr)

    def int_range(self, name: str, arg: str, range_: range):
        arg = self.int_arg(name, arg)
        
        if arg in range_:
            return arg
        else:
            raise ArgumentError(name, self.skin.line_nr)

    def len_arg(self, name: str, arg: str, length: str) -> str:
        """
        Return argument if its length matches the desired length
        Raise an argument error if not
        """
        if len(arg) != length:
            raise ArgumentError(name, self.skin.line_nr)

        return arg

    def check_args(self, args: tuple[str]) -> None:
        """
        Raises an argument count error if the command's argument count
        is not one of the valid parameter counts
        """
        argc = len(args)

        if argc < self.PARAMC[0]:
            raise ArgumentCountError(self.skin.line_nr)

        if len(self.PARAMC) > 1 and argc > self.PARAMC[1]:
            raise ArgumentCountError(self.skin.line_nr)

    @abstractmethod
    def run(self, *args: str) -> None:
        return NotImplemented


class SettingsCommand(Command, params=(3,)):
    NAME = "settings"
    ARG_HIDE = "hide marvelous"
    ARG_CENTER = "center notefield"
    ARG_RATIO = "screen ratio"

    def run(self, hide, center, ratio, *lines) -> None:
        hide = self.bool_arg(self.ARG_HIDE, hide)
        self.skin.center = self.bool_arg(self.ARG_CENTER, center)
        
        if hide:
            self.skin.base.append(f"Hit300g: blank\n")

        try:
            left, right = ratio.split(":")
            self.skin.screen_ratio = float(left) / float(right)
        except ValueError:
            raise ArgumentError(self.ARG_RATIO, self.skin.line_nr)

        for line in lines:
            self.skin.base.append(f"{line}\n")


class ComponentCommand(Command, params=(2, 3)):
    NAME = "component"
    ARG_CENTER = "name"
    ARG_TYPE = "type"
    ARG_REDIRECT = "redirect"
    T_VARIABLE = "variable"
    T_STATIC = "static"
    T_REDIRECT = "redirect"

    def run(self, name, type_, redirect = None) -> None:
        if name not in BUILDERS:
            raise ArgumentError(self.ARG_NAME, self.skin.line_nr)

        if type_ == self.T_VARIABLE:
            self.skin.components[name] = VariableComponent(self.skin.name, name)

        elif type_ == self.T_STATIC:
            self.skin.components[name] = StaticComponent(self.skin.name, name)

        elif type_ == self.T_REDIRECT:
            if redirect not in BUILDERS:
                raise ArgumentError(self.ARG_REDIRECT, self.skin.line_nr)

            self.skin.components[name] = RedirectComponent(name, self.skin.components[redirect])

        else:
            raise ArgumentError(self.ARG_TYPE, self.skin.line_nr)


class KeysCommand(Command, params=(6,6)):
    NAME = "keys"
    ARG_KEYS = "keys"
    ARG_WIDTH = "receptor width"
    ARG_SPACING = "spacing"
    ARG_HITPOS = "hit position"
    ARG_TRANSP = "transparency"
    ARG_LAYOUT = "layout"

    def run(self, keys, width, spacing, hitpos, transp, layout) -> None:
        keys = self.int_range(self.ARG_KEYS, keys, range(1, 10))
        width = self.int_range(self.ARG_WIDTH, width, range(0, 101))
        spacing = self.int_range(self.ARG_SPACING, spacing, range(0, 101))
        hitpos = self.int_range(self.ARG_HITPOS, hitpos, range(0, 241))
        transp = self.int_range(self.ARG_TRANSP, transp, range(0, 256))

        colwidth = self.int_range(f"{self.ARG_WIDTH} + {self.ARG_SPACING}", width + spacing, range(0, 101))

        config = []

        config.append("[Mania]\n")
        config.append(f"Keys: {keys}\n")
        config.append(f"ColumnWidth: {','.join(str(colwidth) for _ in range(keys))}\n")
        config.append(f"HitPosition: {HEIGHT - hitpos}\n")

        if self.skin.center:
            config.append(f"ColumnStart: {(HEIGHT * self.skin.screen_ratio - colwidth * keys) / 2}\n")

        config.append("\n")

        config.extend(self.skin.base)
        config.append("\n")

        for key in range(keys):
            config.append(f"Colour{key+1}: 0,0,0,{transp}\n")

            for _, component in self.skin.components.items():
                variant = component.variant(layout[key], width, spacing, hitpos)
                config.append(f"{component.source.name % key}: {variant}\n")
            
            config.append("\n")

        self.skin.mania[keys] = config
