import json
from datetime import datetime
from pathlib import Path

from agentbrowser.exporters.base import BaseExporter


class JSONExporter(BaseExporter):
    def export(self, data: dict, filename: str | None = None) -> Path:
        name = filename or f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if not name.endswith(".json"):
            name += ".json"

        filepath = self.output_dir / name

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filepath
