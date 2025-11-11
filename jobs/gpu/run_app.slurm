#!/bin/bash
#SBATCH --partition=GPUQ
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4 # Number of CPU cores required. Most V100 nodes has 4 CPU cores per GPU, so to maximize usage of the nodes, leave it to 4 (unless you know that your specific node has more than 4 cores/GPU).
#SBATCH --account=studiegrupper-cogito # Only use this one
#SBATCH --job-name=rizz_app
#SBATCH --time=24:00:00
#SBATCH --export=ALL # Export all environment variables.
#SBATCH --output=job_output/app/%j_rizz_app.txt
#SBATCH --gres=gpu:1
#SBATCH --constraint="a100"


mkdir -p job_output/app

# Print some info
echo "Job started on $(hostname) at $(date)"

git pull

# Run the backend server
uv run uvicorn app:app --host 0.0.0.0 --port 8000

echo "-------------------------------------"
echo "Job finished at $(date)"
