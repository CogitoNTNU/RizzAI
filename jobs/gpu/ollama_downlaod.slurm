#!/bin/sh
#SBATCH --partition=CPUQ # CHANGE THIS TO CPUQ IF YOU DON'T NEED GPUs!!
#SBATCH --account=studiegrupper-cogito # READ THIS TO FIND YOUR ACCOUNT: https://www.hpc.ntnu.no/idun/getting-started-on-idun/accounting/
#SBATCH --mem=50GB # Total memory you need. Most DL jobs should do fine with 64GB.
#SBATCH --nodes=1 # Number of nodes. Leave this to 1 as long as you're not running multi-node/multi-gpu training
#SBATCH --job-name=rizz # Set this to whatever you want
#SBATCH --output=/cluster/home/kristiac/rizzai/RizzAI/jobs/gpu/log_ollama.txt # The output file. NOTE! The output directory (/cluster/home/haakohu/ in this case)  has to exist before you submit the job!
#SBATCH --time=2:00:00 # Maximum running time of your job.
#SBATCH --export=ALL # Export all environment variables.
#SBATCH --ntasks-per-node=1 #CPU cores

curl -fsSL https://ollama.com/install.sh | sh
