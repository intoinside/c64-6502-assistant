"""Interfaccia a riga di comando (CLI) per C64-6502-Assistant."""

import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from c64_assistant.core.cycle_counter import CycleCounter
from c64_assistant.core.memory import C64MemoryMap
from c64_assistant.core.validator import HardwareValidator

app = typer.Typer(
    help="C64-6502-Assistant: Motore ibrido per sviluppatori Assembly 6502 su Commodore 64.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def cycles(
    code: str = typer.Argument(..., help="Snippet di codice assembly 6502 separato da newline"),
):
    """Calcola i cicli di clock e l'equivalente in linee raster C64 (PAL/NTSC)."""
    report = CycleCounter.analyze_block(code)

    table = Table(title="Analisi Cicli di Clock 6502", border_style="cyan")
    table.add_column("Riga", justify="right", style="dim")
    table.add_column("Istruzione", style="bold yellow")
    table.add_column("Min", justify="right", style="green")
    table.add_column("Max", justify="right", style="magenta")
    table.add_column("Byte", justify="right")
    table.add_column("Note", style="italic")

    for item in report.instructions:
        table.add_row(
            str(item.line_number),
            item.raw_line,
            str(item.base_cycles),
            str(item.max_cycles),
            str(item.bytes_count),
            item.notes,
        )

    console.print(table)
    console.print(
        Panel(
            f"[bold]Totale Cicli:[/] {report.total_min_cycles} - {report.total_max_cycles} cicli | "
            f"[bold]Dimensione:[/] {report.total_bytes} byte\n"
            f"[bold]Linee Raster PAL (63 cicli/linea):[/] ~{report.pal_raster_lines} linee\n"
            f"[bold]Linee Raster NTSC (65 cicli/linea):[/] ~{report.ntsc_raster_lines} linee",
            title="Budget Hardware C64",
            border_style="green",
        )
    )


@app.command()
def validate(
    file_path: Path = typer.Argument(..., help="File sorgente Assembly .asm da validare"),
):
    """Esegue la validazione deterministica del codice rispetto alle regole hardware del C64."""
    if not file_path.exists():
        console.print(f"[bold red]Errore:[/] File {file_path} non trovato.", file=sys.stderr)
        raise typer.Exit(code=1)

    code = file_path.read_text(encoding="utf-8")
    report = HardwareValidator.validate_code(code)

    console.print(
        Panel(
            f"Stato: {'[bold green]VALIDO[/]' if report.is_valid else '[bold red]NON VALIDO[/]'}\n"
            f"Errori: [red]{report.errors_count}[/] | Warning: [yellow]{report.warnings_count}[/]",
            title=f"Report Validazione: {file_path.name}",
            border_style="green" if report.is_valid else "red",
        )
    )

    if report.issues:
        issue_table = Table(title="Problemi Rilevati", border_style="red")
        issue_table.add_column("Riga", justify="right")
        issue_table.add_column("Livello", style="bold")
        issue_table.add_column("Messaggio")
        issue_table.add_column("Suggerimento", style="italic green")

        for issue in report.issues:
            color = "red" if issue.severity == "ERROR" else "yellow"
            issue_table.add_row(
                str(issue.line_number),
                f"[{color}]{issue.severity}[/]",
                issue.message,
                issue.suggestion,
            )
        console.print(issue_table)


@app.command()
def memory(
    address: str = typer.Argument(..., help="Indirizzo esadecimale (es. $D020 o D020) o decimale"),
):
    """Ispeziona la mappa di memoria del C64 e verifica permessi e sicurezza dell'indirizzo."""
    addr_str = address.strip()
    if addr_str.startswith("$"):
        addr = int(addr_str[1:], 16)
    elif addr_str.lower().startswith("0x"):
        addr = int(addr_str, 16)
    elif any(c in "ABCDEFabcdef" for c in addr_str):
        addr = int(addr_str, 16)
    else:
        addr = int(addr_str)

    region = C64MemoryMap.get_region_for_address(addr)
    zp_info = C64MemoryMap.check_zero_page_safety(addr)

    desc = region.description if region else "RAM generale o area non mappata in tabella"
    name = region.name if region else "Libera / Custom"

    content = f"[bold yellow]Indirizzo:[/] ${addr:04X} ({addr})\n"
    content += f"[bold]Regione:[/] {name}\n"
    content += f"[bold]Descrizione:[/] {desc}\n"

    if zp_info["is_zero_page"]:
        safety = "[green]Sicura[/]" if zp_info["is_safe"] else "[red]Critica / Riservata[/]"
        content += f"[bold]Sicurezza Zero Page:[/] {safety}\n"
        content += f"[bold]Dettagli:[/] {zp_info['details']}\n"

    console.print(Panel(content, title="C64 Memory Inspector", border_style="cyan"))


@app.command()
def banking(
    value: str = typer.Argument("$37", help="Valore per il registro $0001 (es. $37, $36, $35, $30 o decimale 55)"),
):
    """Mostra la mappa di visibilità delle ROM e della RAM per un dato valore di banking nel registro $0001."""
    val_str = value.strip()
    if val_str.startswith("$"):
        port_val = int(val_str[1:], 16)
    elif val_str.lower().startswith("0x"):
        port_val = int(val_str, 16)
    else:
        port_val = int(val_str)

    config = C64MemoryMap.get_banking_config(port_val)

    table = Table(title=f"Configurazione Banking 6510: {config.value_hex}", border_style="magenta")
    table.add_column("Segnale / Bit", style="bold")
    table.add_column("Stato", justify="center")
    table.add_column("Area Influenzata")

    table.add_row("LORAM (Bit 0)", "1 (ALTO)" if config.loram else "0 (BASSO)", "$A000-$BFFF (BASIC ROM)")
    table.add_row("HIRAM (Bit 1)", "1 (ALTO)" if config.hiram else "0 (BASSO)", "$E000-$FFFF (Kernal ROM)")
    table.add_row("CHAREN (Bit 2)", "1 (ALTO)" if config.charen else "0 (BASSO)", "$D000-$DFFF (I/O o Char ROM)")

    console.print(table)

    vis_content = f"[bold]Descrizione:[/] {config.description}\n\n"
    vis_content += f"• [bold]BASIC ROM ($A000):[/] {'[green]VISIBILE[/]' if config.basic_rom_visible else '[yellow]RAM SOTTOSTANTE[/]'}\n"
    vis_content += f"• [bold]KERNAL ROM ($E000):[/] {'[green]VISIBILE[/]' if config.kernal_rom_visible else '[yellow]RAM SOTTOSTANTE[/]'}\n"
    vis_content += f"• [bold]I/O Chips ($D000):[/] {'[green]ATTIVI (VIC/SID/CIA)[/]' if config.io_visible else '[yellow]DISATTIVATI[/]'}\n"
    vis_content += f"• [bold]Character ROM ($D000):[/] {'[green]VISIBILE[/]' if config.char_rom_visible else '[dim]Non visibile[/]'}"

    console.print(Panel(vis_content, title="Visibilità Mappa di Memoria", border_style="green"))


def main():
    app()


if __name__ == "__main__":
    main()

