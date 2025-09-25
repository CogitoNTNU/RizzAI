import subprocess

import typer


app = typer.Typer()


def run(cmd: str) -> None:
    subprocess.run(cmd, shell=True, check=True)


@app.command()
def lint() -> None:
    run("uv run ruff check --fix")


@app.command()
def format() -> None:
    run("uv run ruff format")


@app.command()
def mypy() -> None:
    run("uv run mypy .")


@app.command("l")
def all_tasks() -> None:
    lint()
    format()
    mypy()


if __name__ == "__main__":
    app()
