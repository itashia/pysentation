"""
██████╗ ██╗   ██╗███████╗███████╗███╗   ██╗████████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
██╔══██╗╚██╗ ██╔╝██╔════╝██╔════╝████╗  ██║╚══██╔══╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
██████╔╝ ╚████╔╝ ███████╗█████╗  ██╔██╗ ██║   ██║   ███████║   ██║   ██║██║   ██║██╔██╗ ██║
██╔═══╝   ╚██╔╝  ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
██║        ██║   ███████║███████╗██║ ╚████║   ██║   ██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
╚═╝        ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

pysentation Github repository: https://github.com/mimseyedi/pysentation
"""

import os
import click
import pickle
from pathlib import Path
from getkey import getkey, keys
from typing import Dict, Any, Optional
from rich import print as cprint
from .package import __version__
from .module import Pysentation, PysentationScreen
from .errors import PysentationError, NotAPysentationFileError


def clear_screen() -> None:
    """Clear terminal screen in a cross-platform way."""
    os.system('cls' if os.name == 'nt' else 'clear')


def screen_manager(screen: PysentationScreen) -> None:
    """
    Manage screen navigation and controls for the presentation.
    
    Args:
        screen: PysentationScreen object to manage
    """
    key_actions = {
        keys.RIGHT: screen.next_slide,
        keys.LEFT: screen.previous_slide,
        keys.UP: screen.highlight_top_line,
        keys.DOWN: screen.highlight_bottom_line,
        'S': lambda: (
            screen.display(),
            screen.search_by_title(title=input("Enter slide title: "))
        ),
        'j': lambda: (
            screen.display(),
            screen.search_by_index(index=input("Enter slide number: "))
        ),
        'r': screen.reset_slide,
        'R': screen.reset_screen,
        'f': screen.first_slide,
        'l': screen.last_slide,
        'K': screen.display_hot_keys,
        'q': lambda: (clear_screen(), exit(0))
    }

    try:
        while True:
            input_key = getkey()
            if action := key_actions.get(input_key):
                action()
    except KeyboardInterrupt:
        pass


def options_manager(screen: PysentationScreen, options: Dict[str, Any]) -> None:
    """
    Manage and prioritize presentation options.
    
    Args:
        screen: PysentationScreen object
        options: Dictionary of options to apply
    """
    if options.get('output'):
        if color := options.get('color'):
            screen.set_color(color=color)
        if theme := options.get('theme'):
            screen.set_theme(theme=theme)
        if options.get('disable'):
            screen.disable_output()
        screen.write_output(output_path=options['output'])
        return

    if 'slides' in options or 'property' in options:
        if options.get('slides'):
            cprint(screen.get_slides())
        if prop := options.get('property'):
            cprint(screen.get_property(slide_index=prop - 1))
        return

    # Apply display options
    if color := options.get('color'):
        screen.set_color(color=color)
    if theme := options.get('theme'):
        screen.set_theme(theme=theme)
    if options.get('disable'):
        screen.disable_output()

    # Start presentation
    if start_from := options.get('from'):
        screen.start_from(slide_index=start_from - 1)
    else:
        screen.display()
    
    screen_manager(screen=screen)


def validate_export_file(export_path: Path) -> bool:
    """Validate export file path and extension."""
    if export_path.suffix != '.pysent':
        raise NotAPysentationFileError(
            'The export file must be a pysentation file with (.pysent) suffix.'
        )
    if export_path.exists():
        raise FileExistsError(f'This file already exists! -> {export_path.name}')
    return True


def handle_export(source_file: str, export_path: Path) -> None:
    """Handle file export operation."""
    validate_export_file(export_path)
    
    with open(source_file, 'r') as f:
        source = f.read()
    
    with open(export_path, "wb") as f:
        pickle.dump(source, f)


@click.command(
    context_settings={'help_option_names': ['-h', '--help']},
    epilog="pysentation Github repo: https://github.com/mimseyedi/pysentation"
)
@click.argument('pysentation_file', required=False, nargs=-1)
@click.option('-f', '--from', 'start_from', type=int, help='Start from selected slide.')
@click.option('-c', '--color', help='Set color for all slides.')
@click.option('-t', '--theme', help='Set syntax highlighter theme.')
@click.option('-d', '--disable', is_flag=True, help='Disable code interpretation.')
@click.option('-p', '--property', 'slide_property', type=int, help='Display selected slide properties.')
@click.option('-s', '--slides', is_flag=True, help='Display slides with positions.')
@click.option('-e', '--export', type=Path, help='Export to .pysent file.')
@click.option('-o', '--output', type=Path, help='Write slides to text file.')
@click.option('-v', '--version', is_flag=True, help='Show version.')
def main(**options) -> None:
    """
    pysentation - CLI for displaying Python presentations.
    
    Hot keys:
      right    Next slide
      left     Previous slide
      up       Highlight top line
      down     Highlight bottom line
      f        First slide
      l        Last slide
      r        Reset current slide
      R        Reset screen
      j        Jump to slide number
      S        Search by title
      K        Show hot-keys
      q        Quit
    """
    if options['version'] and not options['pysentation_file']:
        click.echo(__version__)
        return

    if not options['pysentation_file']:
        click.echo("Error: Missing argument 'PYSENTATION_FILE'.")
        return

    if options['version']:
        click.echo("Error: --version cannot be used with file arguments.")
        return

    if options['export']:
        try:
            handle_export(options['pysentation_file'][0], 
                         Path.cwd() / options['export'])
        except (NotAPysentationFileError, FileExistsError) as e:
            cprint(f"[bold red]Error:[/bold red] {e}")
        return

    try:
        pysentation = Pysentation(source=options['pysentation_file'][0])
        screen = pysentation.build()

        filtered_options = {
            k: v for k, v in options.items() 
            if v not in (None, False) and k not in ('pysentation_file', 'export')
        }
        options_manager(screen, filtered_options)

    except (PysentationError, IsADirectoryError, FileNotFoundError) as e:
        cprint(f"[bold red]Error:[/bold red] {e}")


if __name__ == '__main__':
    main()
