from abc import ABC, abstractmethod
from PIL import Image
from .consts import MAGIC, RGBA, COLOR_TRANSPARENT


class Builder(ABC):
    def __init__(self, name) -> None:
        self.name: str = name

    def create(self, in_image, width, spacing, hitpos, out_image) -> str:
        image = Image.open(in_image).convert(RGBA)
        image: Image.Image = self.edit(image, width, spacing, hitpos)
        image.save(f"{out_image}.png")
        image.close()

        image = Image.open(in_image).convert(RGBA)
        image: Image.Image = self.edit(image, 2 * width, 2 * spacing, 2 * hitpos)
        image.save(f"{out_image}@2x.png")
        image.close()

        print(f"Created images for {out_image}")

    @abstractmethod
    def edit(image: Image.Image, width, spacing, hitpos) -> Image.Image:
        return NotImplemented


class ReceptorBuilder(Builder):
    def edit(self, in_image: Image.Image, width, spacing, hitpos) -> Image.Image:
        horz_pad = spacing * MAGIC
        vert_pad = 2 * hitpos * MAGIC

        part_width = width * MAGIC
        part_height = part_width * in_image.height / in_image.width

        part_image = in_image.resize((round(part_width), round(part_height)))

        full_width = part_width + horz_pad
        full_height = part_height + vert_pad
        
        out_image = Image.new(RGBA, (round(full_width), round(full_height)), COLOR_TRANSPARENT)

        out_image.paste(part_image, (round(horz_pad / 2), round(vert_pad / 2)))

        part_image.close()
        in_image.close()
        
        return out_image


class NoteBuilder(Builder):
    def edit(self, in_image: Image.Image, width, spacing, _) -> Image.Image:
        scale_factor = 1 + spacing / width
        
        out_image = Image.new(RGBA, (round(in_image.width * scale_factor), in_image.height), COLOR_TRANSPARENT)
        out_image.paste(in_image, ((out_image.width - in_image.width) // 2 + 2, 0))
        in_image.close()

        return out_image

BUILDERS: dict[str, Builder] = {
    "note": NoteBuilder("NoteImage%d"),
    "hold-head": NoteBuilder("NoteImage%dH"),
    "hold-body": NoteBuilder("NoteImage%dL"),
    "hold-tail": NoteBuilder("NoteImage%dT"),
    "receptor-up": ReceptorBuilder("KeyImage%d"),
    "receptor-down": ReceptorBuilder("KeyImage%dD"),
}
