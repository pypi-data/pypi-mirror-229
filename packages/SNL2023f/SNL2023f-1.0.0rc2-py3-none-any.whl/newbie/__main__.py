import click
import newbie

__version__ = "1.0.0-pre2"

@click.version_option(prog_name="SNL2023f", version=__version__)
@click.group()
def main():
    pass

@main.command("server")
def server():
    newbie.server()

@main.command("container")
def container():
    newbie.container()

@main.command("client")
def client():
    newbie.client()

if __name__ == "__main__":
    main()
