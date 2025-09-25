# RizzAI

## Setup
1. Use UV to install dependencies: `uv sync`

2. Install pre-commit hooks: `uv run pre-commit install`

## Linting, Formatting and Type Checking
- To do all tasks (lint, format, mypy): `uv run tools.py l`
- To lint only: `uv run tools.py lint`
- To format only: `uv run tools.py format`
- To run mypy only: `uv run tools.py mypy`

## Running Python Scripts
- To run a Python script: `uv run python <script_name>.py`
