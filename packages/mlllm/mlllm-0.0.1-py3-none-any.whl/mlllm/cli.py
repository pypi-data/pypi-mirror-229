# imports
import os
import sys
import toml
import typer


from dotenv import load_dotenv
from typing_extensions import Annotated

# local imports
from mlllm.testing import testing_run

# configuration
# load .env file
load_dotenv()

# load config
try:
    config = toml.load("config.toml")
except FileNotFoundError:
    config = {}

# typer config
app = typer.Typer(no_args_is_help=True)


# global options
def version(value: bool):
    if value:
        version = toml.load("pyproject.toml")["project"]["version"]
        typer.echo(f"{version}")
        raise typer.Exit()


# subcommands
@app.command()
def test():
    """
    test
    """
    testing_run()


# main
@app.callback()
def cli(
    version: bool = typer.Option(
        None, "--version", help="Show version.", callback=version, is_eager=True
    ),
):
    # Do other global stuff, handle other global options here
    return


## main
if __name__ == "__main__":
    typer.run(cli)
