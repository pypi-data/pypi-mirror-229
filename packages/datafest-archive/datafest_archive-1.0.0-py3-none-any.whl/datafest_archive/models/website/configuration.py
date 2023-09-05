from typing import List, Optional

from dataclasses import dataclass


@dataclass
class Menu:
    _main: list["MenuItem"]

    @property
    def main(self) -> list["MenuItem"]:
        return sorted(self._main, key=lambda x: x.weight)

    @main.setter
    def name(self, value: str):
        self._name = value

    def __repr__(self) -> str:
        return f"<Menu {self.name}>"


@dataclass
class MenuItem:
    name: str
    url: str
    weight: int
    parent: Optional[str]
