from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Any, Optional


@dataclass
class Argument:
    name: str
    help: str
    default: Any = ""
    required: bool = False
    short_name: Optional[str] = ""
    action: Optional[str] = ""

    def __post_init__(self) -> None:
        if not self.short_name:
            self.short_name = self.name[0]


@dataclass
class FlagArgument(Argument):
    default = 0
    action = "count"


class BuildCommand(ABC):
    project_dir: Path
    output_path: Path

    @abstractmethod
    @property
    def arguments(self) -> List[Argument]:
        pass
