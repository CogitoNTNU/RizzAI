#!/bin/bash
RED='\e[31m'
GREEN='\e[32m'
MAGENTA='\e[35m'
CYAN='\e[36m'
LIGHTCORAL="\033[38;5;210m"
DARKRED="\033[48;5;88m"

RESET='\e[0m\033[0m'
ITALIC='\e[3m'
BOLD='\033[1m'

trap 'echo -e "Output monitoring ${RED}stopped. Have a nice day ${GREEN}:)${RESET}"; exit 130' INT

RIZZCOL="${BOLD}${LIGHTCORAL}${DARKRED}"

JOB_INPUT="$1"

monitor_file () {
    # Get output file
    HAS_FILE=$1
    JOB_ID=$2
    OUTPUT_FILE=$3

    if [[ "$HAS_FILE" == false ]]; then
        for i in {1..10}; do
            OUTPUT_FILE=$(find job_output -name "*$JOB_ID*.out" 2>/dev/null | head -1)

            if [ -n "$OUTPUT_FILE" ]; then
                echo -e "$RIZZCOL[RizzAI]${RESET} Found Job output file: ${GREEN}$OUTPUT_FILE${RESET}"
                break
            fi

            echo -e "$RIZZCOL[RizzAI]${RESET} Attempt $i/10: ${RED}File not found, waiting...${RESET}"
            sleep 5
        done
    fi

    if [ -z "$OUTPUT_FILE" ]; then
        echo -e "$RIZZCOL[RizzAI]${RESET} ${BOLD}${RED}Error:${RESET} ${RED}Output file not found after 10 attempts.${RESET}"
        echo -e "$RIZZCOL[RizzAI]${RESET} ${BOLD}${RED}Error:${RESET} ${RED}Expected pattern: job_output/*${JOB_ID}*.out${RESET}"
        exit 1
    fi

    echo -e "$RIZZCOL[RizzAI]${RESET} Monitoring the output file: $OUTPUT_FILE"

    tail -n +1 -F "$OUTPUT_FILE"
}

# Read JOB_INPUT
if [[ "$JOB_INPUT" == *.slurm ]]; then
    echo -e "$RIZZCOL[RizzAI]${RESET} Found Job file: ${GREEN}$JOB_INPUT${RESET}"
    JOB_ID=$(sbatch $JOB_INPUT | grep -o '[0-9]*')
    echo -e "$RIZZCOL[RizzAI]${RESET} Sent out batch job. Job ID: ${GREEN}$JOB_ID${RESET}"
    sleep 1
    monitor_file false "$JOB_ID" ""
elif [[ "$JOB_INPUT" == -m ]]; then
    JOB_DEST=$2
    monitor_file true 0 "$JOB_DEST"
else
    echo -e "Job file was not found. Create a valid slurm file, you noob!"
    exit 1
fi

# Wait a second