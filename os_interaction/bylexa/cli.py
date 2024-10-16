import click
from .token import login
from .websocket_client import start_client

@click.group()
def main():
    pass

@main.command()
def login_command():
    """Login to Bylexa and store the token."""
    login()

@main.command()
def start():
    """Start listening for commands from the Bylexa server."""
    start_client()
