#!/bin/sh
#SBATCH --partition=CPUQ # CHANGE THIS TO CPUQ IF YOU DON'T NEED GPUs!!
#SBATCH --account=studiegrupper-cogito # Only use this one
#SBATCH --mem=32GB # Total memory you need. Most DL jobs should do fine with 64GB.
#SBATCH --nodes=1 # Number of nodes. Leave this to 1 as long as you're not running multi-node/multi-gpu training
#SBATCH --cpus-per-task=4 # Number of CPU cores required. Most V100 nodes has 4 CPU cores per GPU, so to maximize usage of the nodes, leave it to 4 (unless you know that your specific node has more than 4 cores/GPU).
#SBATCH --job-name=hourglass_prior_freq_50 # Set this to whatever you want
#SBATCH --time=00:20:00 # Maximum running time of your job.
#SBATCH --export=ALL # Export all environment variables.
#SBATCH --output=job_output/salesforce-blip2-opt-6.7b-coco/%j_cpu_strong_rizz.out

# Ensure the output directory exists
mkdir -p job_output/salesforce-blip2-opt-6.7b-coco

if [ -z "$CUDA_VISIBLE_DEVICES" ]; then
  echo "Total of GPUS: None (CPU-only job)"
else
  echo "Total of GPUS: $CUDA_VISIBLE_DEVICES"
fi
uv sync
# uv run python -m blip2.test2
# uv run python -m blip2.test
# uv run python -m blip2.test_rizz
uv run python -m blip2.test_stronger_rizz
