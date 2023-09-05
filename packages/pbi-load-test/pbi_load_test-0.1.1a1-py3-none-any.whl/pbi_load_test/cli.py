import click

from . import __version__
from .pbi import PowerBIClient
from .run import run as _run


@click.group(invoke_without_command=True)
@click.option("-v", "--version", required=False, is_flag=True)
def cli(version):
    """Application to simplify Power BI Load Test."""
    ctx = click.get_current_context()
    if ctx.invoked_subcommand is None:
        if version:
            click.echo(__version__)
        else:
            click.echo(ctx.get_help())


@cli.command()
def token():
    pbi_client = PowerBIClient()
    click.echo(pbi_client.token, color=True)


@cli.command()
def run():
    _run()
