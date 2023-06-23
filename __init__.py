import click

from controller_cli import connect, discover


__author__ = """Dave Curtis"""
__email__ = 'dave@dcurtis.co.uk'
__version__ = '0.1.0'


@click.group()
def cli():
    pass


cli.add_command(connect)
cli.add_command(discover)

if __name__ == "__main__":
    cli()