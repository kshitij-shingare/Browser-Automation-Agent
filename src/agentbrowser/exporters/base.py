from abc import ABC, abstractmethod
from pathlib import Path


class BaseExporter(ABC):
    def __init__(self, output_dir: str) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def export(self, data: dict, filename: str | None = None) -> Path:
        pass
