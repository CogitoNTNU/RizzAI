#!/bin/bash

# Locate the job_output folder
JOB_OUTPUT_DIR="/cluster/home/kristiac/rizzai/RizzAI/job_output"

# Check if the folder exists
if [ -n "$JOB_OUTPUT_DIR" ]; then
    echo "Found job_output folder at: $JOB_OUTPUT_DIR"
    
    # Remove all log files in the folder
    find "$JOB_OUTPUT_DIR" -type f -name "*.out" -exec rm -f {} \;
    echo "All log files removed from $JOB_OUTPUT_DIR"
else
    echo "job_output folder not found."
fi