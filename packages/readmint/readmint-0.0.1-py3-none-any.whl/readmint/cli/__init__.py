# SPDX-FileCopyrightText: 2023-present Alvaro Leiva Geisse <aleivag@gmail.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path

import click
import sys
from marko import Markdown

from readmint.__about__ import __version__
from readmint.lib import renderer


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="readmint")
def readmint():
    ...


@readmint.command()
@click.option("--output-file", metavar="OUTPUT_FILE", type=Path, required=True, help="Output file")
@click.argument("input_file", type=Path)
def render_file(input_file: Path, output_file: Path):
    """
    writes [INPUT FILE] into --out file
    """
    output_file.write_text(renderer.render_file(input_file))


@readmint.command()
@click.option("--check/--execute", "check", default=False, help="execute (a.k.a do the rendering) or check (fail if there is need for rendering)")
@click.option("--output-dir", metavar="OUTPUT_DIR", type=Path,required=True, help="Output file")
@click.argument("input_dir", type=Path)
def render_dir(input_dir: Path, output_dir: Path, check:bool):
    input_dir = input_dir.resolve()
    output_dir = output_dir.resolve()

    for f in input_dir.glob("**/*.md"):
        output_text = renderer.render_file(f)
        finalf = output_dir / f.relative_to(input_dir)
        if check:
            if finalf.read_text() != output_text:
                click.echo(f"file {f} needs to be renderer", err=True)
                sys.exit(-1)
        else:
            finalf.write_text(output_text)

    if check:
        click.echo("No changes needed", err=True)






