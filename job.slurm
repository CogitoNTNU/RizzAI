#!/bin/sh
#SBATCH --partition=GPUQ # CHANGE THIS TO CPUQ IF YOU DON'T NEED GPUs!!
#SBATCH --account=studiegrupper-cogito # Only use this one
#SBATCH --mem=32GB # Total memory you need. Most DL jobs should do fine with 64GB.
#SBATCH --nodes=1 # Number of nodes. Leave this to 1 as long as you're not running multi-node/multi-gpu training
#SBATCH --cpus-per-task=4 # Number of CPU cores required. Most V100 nodes has 4 CPU cores per GPU, so to maximize usage of the nodes, leave it to 4 (unless you know that your specific node has more than 4 cores/GPU).
#SBATCH --job-name=hourglass_prior_freq_50 # Set this to whatever you want
#SBATCH --time=00:20:00 # Maximum running time of your job.
#SBATCH --export=ALL # Export all environment variables.
#SBATCH --gres=gpu:1 # GPU type and number of GPUs.
#SBATCH --output=job_output/myjob-%j.out

# Ensure the job_output directory exists
mkdir -p job_output

echo "We are running from this directory: $SLURM_SUBMIT_DIR"
echo "The name of the job is: $SLURM_JOB_NAME"
echo "The job ID is $SLURM_JOB_ID"
echo "The job was run on these nodes: $SLURM_JOB_NODELIST"
echo "Number of nodes: $SLURM_JOB_NUM_NODES"
echo "We are using $SLURM_CPUS_ON_NODE cores"
echo "We are using $SLURM_CPUS_ON_NODE cores per node"
echo "Total of $SLURM_NTASKS cores"
if [ -z "$CUDA_VISIBLE_DEVICES" ]; then
  echo "Total of GPUS: None (CPU-only job)"
else
  echo "Total of GPUS: $CUDA_VISIBLE_DEVICES"
fi
uv sync
# uv run python -m blip2.test2
uv run python -m blip2.test
