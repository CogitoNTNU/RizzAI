#!/bin/sh
#SBATCH --partition=GPUQ # CHANGE THIS TO CPUQ IF YOU DON'T NEED GPUs!!
#SBATCH --account=studiegrupper-cogito # READ THIS TO FIND YOUR ACCOUNT: https://www.hpc.ntnu.no/idun/getting-started-on-idun/accounting/
#SBATCH --mem=64GB # Total memory you need. Most DL jobs should do fine with 64GB.
#SBATCH --nodes=1 # Number of nodes. Leave this to 1 as long as you're not running multi-node/multi-gpu training
#SBATCH --job-name=rizz # Set this to whatever you want
#SBATCH --output=/cluster/home/kristiac/rizzai/jobs/gpu/annontate_log.txt # The output file. NOTE! The output directory (/cluster/home/haakohu/ in this case)  has to exist before you submit the job!
#SBATCH --time=1:00:00 # Maximum running time of your job.
#SBATCH --export=ALL # Export all environment variables.
#SBATCH --gres=gpu:1
#SBATCH --ntasks-per-node=1 #CPU cores

cd
dir
cd rizzai
dir
cd RizzAI
dir
uv sync
uv run python -m blip2.generate_annontations