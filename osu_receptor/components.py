from abc import ABC, abstractmethod
from pathlib import Path
from .builders import BUILDERS, Builder
from .consts import SOURCE_PREFIX

class Component(ABC):
    def __init__(self, skin: str, name: str) -> None:
        self.skin: str = skin
        self.name: str = name
        self.sizes: list[tuple[int, int, int]] = []

    @property
    def source(self) -> Builder:
        return BUILDERS[self.name]

    def size(self, width: int, spacing: int, hitpos: int) -> int:
        """
        Creates or gets the size index given some width, spacing and hitpos values

        When creating, it generates the images needed in the actual skin folder,
        which is considered existing.
        """
        if (width, spacing, hitpos) in self.sizes:
            return self.sizes.index((width, spacing, hitpos))
        
        idx = len(self.sizes)
        self.sizes.append((width, spacing, hitpos))

        for in_image in Path(f"{SOURCE_PREFIX}-{self.skin}").glob(f"{self.name}*"):
            self.source.create(
                str(in_image),
                width, spacing, hitpos,
                f"{self.skin}/{in_image.stem}-{idx}"
            )

        return idx

    @abstractmethod
    def variant(self, variant, width, spacing, hitpos) -> str:
        return NotImplemented


class VariableComponent(Component):
    def variant(self, variant, width, spacing, hitpos) -> str:
        return f"{self.skin}\\{self.name}{variant}-{self.size(width, spacing, hitpos)}"


class StaticComponent(Component):
    def variant(self, _, width, spacing, hitpos) -> str:
        return f"{self.skin}\\{self.name}-{self.size(width, spacing, hitpos)}"


class RedirectComponent(Component):
    def __init__(self, name: str, src: Component) -> None:
        super().__init__(src.skin, name)
        self.src = src

    def size(self, width, spacing, hitpos) -> int:
        return self.src.size(width, spacing, hitpos)

    def variant(self, variant, width, spacing, hitpos) -> str:
        return self.src.variant(variant, width, spacing, hitpos)