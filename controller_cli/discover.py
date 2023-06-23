from ocacomms.OcaDiscovery import OcaDiscovery
import logging
from time import sleep
import click

@click.command()
def discover() -> None:
    logging.basicConfig(
        format="[%(asctime)s]:\t%(message)s", level=logging.DEBUG
    )
    discovery = OcaDiscovery("udp")
    while True:
        try:
            sleep(.1)
        except KeyboardInterrupt:
            del discovery
            exit(0)