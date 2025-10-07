#!/bin/bash
RED='\e[31m'
GREEN='\e[32m'
MAGENTA='\e[35m'
CYAN='\e[36m'
SALMON='\033[38;5;204;48;5;231m'
RESET='\e[0m\033[0m'
ITALIC='\e[3m'
BOLD='\033[1m'

JOB_OUTPUT_DIR="/cluster/home/kristiac/rizzai/RizzAI/job_output"

JOB_INPUT="$1"

if [[ "$JOB_INPUT" == *.slurm ]]; then
    echo -e "${BOLD}${SALMON}[RizzAI]${RESET} Found Job file"
else
    echo "Job file was not found. Create a valid slurm file, you noob!"
    exit 1
fi

BATCH_ID=$(sbatch $JOB_INPUT | grepo -o '[0-9]*')
echo "${BOLD}${SALMON}[RizzAI]${RESET} Sent out batch jon. Job ID: ${GREEN}$BATCH_ID${RESET}"