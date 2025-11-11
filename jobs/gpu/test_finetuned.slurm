#!/bin/bash
#SBATCH --partition=GPUQ
#SBATCH --mem=32G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4 # Number of CPU cores required. Most V100 nodes has 4 CPU cores per GPU, so to maximize usage of the nodes, leave it to 4 (unless you know that your specific node has more than 4 cores/GPU).
#SBATCH --account=studiegrupper-cogito # Only use this one
#SBATCH --job-name=test_finetuned_model
#SBATCH --time=24:00:00
#SBATCH --export=ALL # Export all environment variables.
#SBATCH --output=job_output/test/%j_test_finetuned.txt
#SBATCH --gres=gpu:1
#SBATCH --constraint="a100"


mkdir -p job_output/test

# Print some info
echo "Job started on $(hostname) at $(date)"

git pull

# Run training
uv run python -m blip2.test_finetuned

echo "-------------------------------------"
echo "Job finished at $(date)"
