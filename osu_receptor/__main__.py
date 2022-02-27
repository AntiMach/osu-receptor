from pathlib import Path
import traceback
from .errors import OsuReceptorError
from .commands import OsuReceptorSkin
from .consts import SOURCE_PREFIX


def select(skins: list[str]):
    print("Select a skin to use:")

    for i, skin in enumerate(skins):
        print(f"{i+1}. {skin}")

    print()

    opt = 0
    while opt < 1 or opt > len(skins):
        try:
            opt = int(input("> "))
        except ValueError:
            opt = 0
    
    return skins[opt-1]
    

def main():
    skins = []
    prefix = f"{SOURCE_PREFIX}-"

    for f in Path(".").iterdir():
        if f.is_dir() and f.stem.startswith(prefix):
            skins.append(f.with_stem(f.stem.removeprefix(prefix)))

    if len(skins) == 0:
        raise OsuReceptorError("Found no skin folder...")
    elif len(skins) == 1:
        selected = skins[0].stem.removeprefix(prefix)
    else:
        selected = select(skins)

    try:
        skin = OsuReceptorSkin(selected)
        skin.load_ini()
        skin.process()
        skin.create_elements()
        skin.save_ini()
    except OsuReceptorError as err:
        print(err.args[0])
    except Exception:
        traceback.print_exc()
        print("\nAn unexpected error has occured, please report this error on my github.")


main()