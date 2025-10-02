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

### Web Scraper
- To run the web scraper: `uv run python -m data_collection.web_scraper
- Ensure you have set up the `.env` file in the `data_collection` directory with the necessary environment variables, as shown in `.env-example`.
- NOTE: To run the scraper automatically, remove the `input()` line in the scraper code.


## How to Access the Server

1. You need to have your public SSH key added to the server's `~/.ssh/authorized_keys` file. If you don't have a public/private key pair, you can generate one using the command:
```bash
ssh-keygen
```
Select the file path (path `.ssh/idun` will be used in this case) and set a passphrase if desired. This will create two files: the private key (e.g., `idun`) and the public key (e.g., `idun.pub`).
Then, ask Kristian to add your public key to the server.

2. To connect to the server, you need to create an SSH agent and add your private key to it. There are two ways to do this:

   a) Use Remote-SSH in VSCode
   In your `.ssh/config` file, add the following configuration:
   ```bash
   Host rizzler
       HostName HOSTNAME
       User USERNAME
       IdentityFile ~/.ssh/idun
   ```
   Replace `HOSTNAME` and `USERNAME` with the appropriate values (see Slack to get these).
   Then, in VSCode:
   - Press `F1`, type `Remote-SSH: Connect to Host...`, and select `rizzler`.
   - You will be prompted to enter the passphrase for your private key if you set one.

   b) Use a terminal that supports SSH agent forwarding
   You can do this with the following commands (in Git Bash or WSL):
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/idun
   ssh USERNAME@HOSTNAME
   ```
   Replace `USERNAME` and `HOSTNAME` with the appropriate values (see Slack to get these).