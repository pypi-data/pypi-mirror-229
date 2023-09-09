import typer

app = typer.Typer(
    name="Audomo",
)


@app.command(
    name="Hello World",
    help="Hello World.",
    short_help="Hello World.",
)
def main():
    """
    Hello World.
    """
    typer.echo("Hello World.")


if __name__ == "__main__":
    app()
