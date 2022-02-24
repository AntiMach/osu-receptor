import traceback
from subprocess import run as run_process, DEVNULL
from pathlib import Path
from getffmpeg import main as get_ffmpeg


class OsuReceptorError(Exception): ...

class UnknownCommandError(OsuReceptorError):
    def __init__(self, cmd, line) -> None:
        super().__init__(f"Unknown command '{cmd}' in line {line}")

class InvalidArgumentError(OsuReceptorError):
    def __init__(self, arg, line) -> None:
        super().__init__(f"Invalid value for argument [{arg}] in line {line}")


class SourceBuilder:
    MAGIC = 1.6

    def __init__(self, name) -> None:
        self.name = name

    def create(self, in_image, width, spacing, hitpos, out_image) -> str:
        run_process([
            "ffmpeg",
            "-i", in_image,
            "-vf", self.filter(width, spacing, hitpos),
            "-y", out_image
        ], stderr=DEVNULL)
        print(f"Created image {out_image}")


class ReceptorBuilder(SourceBuilder):
    def filter(self, width, spacing, hitpos) -> str:
        return f"format=rgba,scale={2*width*self.MAGIC}:-1,pad=iw+{2*spacing*self.MAGIC}:ih+{4*hitpos*self.MAGIC}:(ow-iw)/2:(oh-ih)/2:color=0x00000000"


class NoteBuilder(SourceBuilder):
    def filter(self, width, spacing, hitpos) -> str:
        return f"format=rgba,pad=iw*{1+spacing/width}:ih:round((ow-iw)/2)+2:0:color=0x00000000"


class TransformedComponent:
    ROOT = "src"

    SOURCE_COMPONENTS: dict[str, SourceBuilder] = {
        "note": NoteBuilder("NoteImage%d"),
        "hold-head": NoteBuilder("NoteImage%dH"),
        "hold-body": NoteBuilder("NoteImage%dL"),
        "hold-tail": NoteBuilder("NoteImage%dT"),
        "receptor-up": ReceptorBuilder("KeyImage%d"),
        "receptor-down": ReceptorBuilder("KeyImage%dD"),
    }

    def __init__(self, name: str) -> None:
        self.name = name
        self.sizes = []

    @property
    def source(self) -> SourceBuilder:
        return self.SOURCE_COMPONENTS[self.name]

    def size(self, width, spacing, hitpos) -> int:
        if (width, spacing, hitpos) in self.sizes:
            return self.sizes.index((width, spacing, hitpos))
        
        idx = len(self.sizes)
        self.sizes.append((width, spacing, hitpos))

        for in_image in Path(self.ROOT).glob(f"{self.name}*"):
            self.source.create(
                str(in_image),
                width, spacing, hitpos,
                f"{in_image.stem}-{idx}@2x.png"
            )

        return idx

    def variant(self, variant, width, spacing, hitpos) -> str:
        raise NotImplementedError()


class VariableComponent(TransformedComponent):
    def variant(self, variant, width, spacing, hitpos) -> str:
        return f"{self.name}{variant}-{self.size(width, spacing, hitpos)}"


class StaticComponent(TransformedComponent):
    def variant(self, variant, width, spacing, hitpos) -> str:
        return f"{self.name}-{self.size(width, spacing, hitpos)}"


class RedirectComponent(TransformedComponent):
    def __init__(self, name: str, src: TransformedComponent) -> None:
        super().__init__(name)
        self.src = src

    def size(self, width, spacing, hitpos) -> int:
        return self.src.size(width, spacing, hitpos)

    def variant(self, variant, width, spacing, hitpos) -> str:
        return self.src.variant(variant, width, spacing, hitpos)


class ReceptorStyle:
    SCREEN_RATIO = 16/9
    HEIGHT = 480
    WIDTH = HEIGHT * SCREEN_RATIO

    def __init__(self) -> None:
        self.root = Path(".").resolve().stem
        self.components: dict[str, TransformedComponent] = {}
        self.skin = ""
        self.base = ""
        self.line_nr = 0

        with open("skin.txt", "r") as fp:
            while (line := fp.readline()) != "":
                self.line_nr += 1
                self.process_command(fp, line)

        with open("../skin.ini", "w") as fp:
            fp.write(self.skin)

    def process_command(self, fp, line: str):
        if line.strip() == "" or line.startswith("//"):
            return

        command, *args = line.lower().split()
        
        if command == "config":
            self.add_config(fp)
        elif command == "base":
            self.set_base(fp, *args)
        elif command == "set":
            self.set(*args)
        elif command == "keys":
            self.keys(*args)
        else:
            raise UnknownCommandError(command, self.line_nr)

    def int_arg(self, name, value) -> int:
        try:
            return int(value)
        except ValueError:
            raise InvalidArgumentError(name, self.line_nr)

    def add_config(self, fp):
        while (line := fp.readline().strip()) != "config":
            self.skin += line + "\n"
            self.line_nr += 1

        self.line_nr += 1

        self.skin += "\n"
            
    def set_base(self, fp, hide):
        hide = self.int_arg("hide marvelous", hide)

        while (line := fp.readline().strip()) != "base":
            self.base += line + "\n"
            self.line_nr += 1
        
        self.line_nr += 1

        if hide:
            self.base += f"Hit300g: {self.root}\\blank\n"

        self.base += "\n"

    def set(self, comp, type, redirect = None) -> None:
        if comp not in TransformedComponent.SOURCE_COMPONENTS:
            raise InvalidArgumentError("name", self.line_nr)

        if type == "variable":
            self.components[comp] = VariableComponent(comp)
        elif type == "static":
            self.components[comp] = StaticComponent(comp)
        elif type == "redirect":
            self.components[comp] = RedirectComponent(comp, self.components[redirect])
        else:
            raise InvalidArgumentError("type", self.line_nr)

    def keys(self, keys, width, spacing, hitpos, transparency, layout) -> None:
        keys = self.int_arg("keys", keys)
        width = self.int_arg("receptor width", width)
        spacing = self.int_arg("spacing", spacing)
        hitpos = self.int_arg("hit position", hitpos)
        transparency = self.int_arg("transparency", transparency)
        colwidth = width + spacing

        config = f"[Mania]\nKeys: {keys}\n"
        config += f"ColumnWidth: {','.join(str(colwidth) for _ in range(keys))}\n"
        config += f"ColumnStart: {(self.WIDTH - colwidth * keys) / 2}\n"
        config += f"HitPosition: {self.HEIGHT - hitpos}\n\n"

        config += self.base

        for key in range(keys):
            config += f"Colour{key+1}: 0,0,0,{transparency}\n"

            for _, component in self.components.items():
                variant = component.variant(layout[key], width, spacing, hitpos)
                config += f"{component.source.name % key}: {self.root}\\{variant}\n"
            
            config += "\n"

        self.skin += config


def main():
    try:
        get_ffmpeg()
        ReceptorStyle()
    except OsuReceptorError as err:
        print(err.args[0])
    except Exception:
        traceback.print_exc()
        print("\nAn unexpected error has occured, please check your skin.txt file or report this error on my github.")
    
    input("Press enter to exit.")


if __name__ == "__main__":
    main()