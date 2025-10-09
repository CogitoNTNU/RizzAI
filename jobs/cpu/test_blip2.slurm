#!/bin/bash
#SBATCH --partition=CPUQ
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4 # Number of CPU cores required. Most V100 nodes has 4 CPU cores per GPU, so to maximize usage of the nodes, leave it to 4 (unless you know that your specific node has more than 4 cores/GPU).
#SBATCH --account=studiegrupper-cogito # Only use this one
#SBATCH --job-name=blip2_test
#SBATCH --time=24:00:00
#SBATCH --export=ALL # Export all environment variables.
#SBATCH --output=job_output/%j_blip2_train.out


# Print some info
echo "Job started on $(hostname) at $(date)"
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
nvidia-smi

git pull
uv sync

# Run training
uv run python -m blip2.train_blip2

echo "Job finished at $(date)"
