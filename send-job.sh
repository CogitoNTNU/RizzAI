#!/bin/bash
RED='\e[31m'
GREEN='\e[32m'
MAGENTA='\e[35m'
CYAN='\e[36m'
RESET='\e[0m\033[0m'
ITALIC='\e[3m'
BOLD='\033[1m'

JOB_OUTPUT_DIR="/cluster/home/kristiac/rizzai/RizzAI/job_output"

JOB_INPUT="$1"

if [[ "$JOB_INPUT" == *.slurm ]]; then
    echo "Found Job file \n"
else
    echo "Job file was not found. Create a valid slurm file, you noob!"
    exit 1
fi

BATCH_ID=$(sbatch $JOB_INPUT)
echo "$BATCH_ID"