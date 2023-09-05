import click

from .pbi import PowerBIClient
from .run import run as _run


@click.group()
def cli():
    """Application to simplify Power BI Load Test."""


@cli.command()
def token():
    pbi_client = PowerBIClient()
    click.echo(pbi_client.token, color=True)


@cli.command()
def run():
    _run()
