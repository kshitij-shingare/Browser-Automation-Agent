import csv
from datetime import datetime
from pathlib import Path

from agentbrowser.exporters.base import BaseExporter


class CSVExporter(BaseExporter):
    def export(self, data: dict, filename: str | None = None) -> Path:
        name = filename or f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if not name.endswith(".csv"):
            name += ".csv"

        filepath = self.output_dir / name

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)

        return filepath
