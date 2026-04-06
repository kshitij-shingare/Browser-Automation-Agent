from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agentbrowser import __version__
from agentbrowser.config.settings import Settings
from agentbrowser.core.runner import run_task_sync
from agentbrowser.exporters.csv_exporter import CSVExporter
from agentbrowser.exporters.json_exporter import JSONExporter
from agentbrowser.utils.logger import setup_logger

app = typer.Typer(
    name="agentbrowser",
    help="Browser automation agent — ketik perintah Anda, agent akan menjalankannya.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


@app.command(help="Jalankan task browser otomatis dengan AI agent.")
def run(
    task: Annotated[str, typer.Argument(help="Perintah yang ingin dijalankan di browser")],
    llm: Annotated[
        Optional[str],
        typer.Option("--llm", "-l", help="Pilih LLM provider: [cyan]groq[/cyan] atau [cyan]gemini[/cyan]"),
    ] = None,
    export: Annotated[
        Optional[str],
        typer.Option("--export", "-e", help="Format export hasil: [cyan]csv[/cyan] atau [cyan]json[/cyan]"),
    ] = None,
    output: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="Nama file output (tanpa ekstensi)"),
    ] = None,
    vision: Annotated[
        Optional[bool],
        typer.Option("--vision/--no-vision", help="Aktifkan vision mode (screenshot-based)"),
    ] = None,
) -> None:
    settings = Settings()
    use_vision = vision if vision is not None else settings.use_vision
    provider = llm or settings.default_llm
    logger = setup_logger(settings.log_dir)

    console.print(
        Panel.fit(
            f"[bold white]Task   :[/bold white] {task}\n"
            f"[bold white]LLM    :[/bold white] {provider}\n"
            f"[bold white]Vision :[/bold white] {'enabled' if use_vision else 'disabled'}\n"
            f"[bold white]Export :[/bold white] {export or 'none'}",
            title="[bold green] Agent Browser [/bold green]",
            border_style="green",
        )
    )

    try:
        logger.info(f"Starting task: {task}")
        result = run_task_sync(task, settings, llm, use_vision)
        logger.info(f"Task completed in {result['duration_seconds']}s")

        table = Table(title="Hasil Eksekusi", border_style="blue", show_lines=True, expand=False)
        table.add_column("Field", style="cyan", no_wrap=True, min_width=16)
        table.add_column("Value", style="white")

        table.add_row("Task", result["task"])
        table.add_row("LLM", result["llm"])
        table.add_row("Vision", str(result["vision"]))
        table.add_row("Steps", str(result["steps_taken"]))
        table.add_row("Duration", f"{result['duration_seconds']}s")
        table.add_row("Success", "[green]Yes[/green]" if result["success"] else "[red]No[/red]")
        table.add_row("Started", result["started_at"])
        table.add_row("Ended", result["ended_at"])
        table.add_row("Result", result["result"])

        console.print()
        console.print(table)

        if export:
            fmt = export.lower()
            if fmt == "csv":
                exporter = CSVExporter(settings.output_dir)
            elif fmt == "json":
                exporter = JSONExporter(settings.output_dir)
            else:
                console.print(f"\n[bold red]Format export tidak dikenal:[/bold red] {export}")
                raise typer.Exit(1)

            filepath = exporter.export(result, output)
            console.print(f"\n[bold green]Tersimpan di:[/bold green] {filepath.resolve()}")
            logger.info(f"Result exported to {filepath.resolve()}")

    except Exception as exc:
        console.print(f"\n[bold red]Error:[/bold red] {exc}")
        logger.error(f"Task failed: {exc}", exc_info=True)
        raise typer.Exit(1)


@app.command(help="Tampilkan konfigurasi aktif saat ini.")
def config() -> None:
    settings = Settings()

    table = Table(title="Konfigurasi Aktif", border_style="blue", show_lines=True)
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    table.add_column("Status", no_wrap=True)

    table.add_row("default_llm", settings.default_llm, "")
    table.add_row("groq_model", settings.groq_model, "")
    table.add_row("gemini_model", settings.gemini_model, "")
    table.add_row(
        "GROQ_API_KEY",
        "***set***" if settings.groq_api_key else "not set",
        "[green]OK[/green]" if settings.groq_api_key else "[red]MISSING[/red]",
    )
    table.add_row(
        "GOOGLE_API_KEY",
        "***set***" if settings.google_api_key else "not set",
        "[green]OK[/green]" if settings.google_api_key else "[yellow]OPTIONAL[/yellow]",
    )
    table.add_row("use_vision", str(settings.use_vision), "")
    table.add_row("max_steps", str(settings.max_steps), "")
    table.add_row("output_dir", str(Path(settings.output_dir).resolve()), "")
    table.add_row("log_dir", str(Path(settings.log_dir).resolve()), "")

    console.print(table)


@app.command(help="Tampilkan versi aplikasi.")
def version() -> None:
    console.print(f"[bold green]Agent Browser[/bold green] v{__version__}")
