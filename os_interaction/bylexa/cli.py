import click
from .token import login as do_login
from .websocket_client import start_client

@click.group()
def main():
    pass

@main.command()
def login():
    """Login to Bylexa and store the token."""
    do_login()

@main.command()
def start():
    """Start listening for commands from the Bylexa server."""
    start_client()
