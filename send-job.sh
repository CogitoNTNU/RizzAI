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

RIZZCOL="${BOLD}${LIGHTCORAL}${DARKRED}"

JOB_INPUT="$1"

if [[ "$JOB_INPUT" == *.slurm ]]; then
    echo -e "$RIZZCOL[RizzAI]${RESET} Found Job file: ${GREEN}$JOB_INPUT${RESET}"
else
    echo -e "Job file was not found. Create a valid slurm file, you noob!"
    exit 1
fi

BATCH_ID=$(sbatch $JOB_INPUT | grep -o '[0-9]*')
echo -e "$RIZZCOL[RizzAI]${RESET} Sent out batch job. Job ID: ${GREEN}$BATCH_ID${RESET}"

# Wait a second
sleep 1

# Reading part

trap 'echo -e "Output monitoring ${RED}stopped. Have a nice day ${GREEN}:)${RESET}"; exit 130' INT

# Get output file
OUTPUT_FILE=$(ls job_output/*${JOB_ID}*.out 2>/dev/null | head -1)

for i in {1..10}; do
    OUTPUT_FILE=$(find job_output -name "*${JOB_ID}*.out" 2>/dev/null | head -1)

    if [ -n "$OUTPUT_FILE" ]; then
        echo -e "$RIZZCOL[RizzAI]${RESET} Found Job output file: ${GREEN}$OUTPUT_FILE${RESET}"
        break
    fi

    echo -e "$RIZZCOL[RizzAI]${RESET} Attempt $i/10: ${RED}File not found, waiting...${RESET}"
    sleep 2
done

if [ -z "$OUTPUT_FILE" ]; then
    echo -e "$RIZZCOL[RizzAI]${RESET} ${BOLD}${RED}Error:${RESET} ${RED}Output file not found after 10 attempts.${RESET}"
    echo -e "$RIZZCOL[RizzAI]${RESET} ${BOLD}${RED}Error:${RESET} ${RED}Expected pattern: job_output/*${JOB_ID}*.out${RESET}"
    exit 1
fi

echo -e "$RIZZCOL[RizzAI]${RESET} Monitoring the output file: $OUTPUT_FILE"
PREVIOUS_LINE_COUNT=0
while true; do
    if [ -f "$OUTPUT_FILE" ]; then
        FILE_CONTENT=$(cat "$OUTPUT_FILE")

        # Count lines (including empty)
        CURRENT_LINE_COUNT=$(echo "$FILE_CONTENT" | wc -l)

        # Move cursor up and clear previous output
        if [ $PREVIOUS_LINE_COUNT -gt 0 ]; then
            # Move up by the number of lines
            for ((i=0; i<$PREVIOUS_LINE_COUNT-1; i++)); do
                # Move up cursor
                printf "\033[1A"
                printf "\033[2K"
            done
        fi 

        printf "%s\n" "$FILE_CONTENT"
        PREVIOUS_LINE_COUNT=$CURRENT_LINE_COUNT
    fi

    sleep 0.5
done