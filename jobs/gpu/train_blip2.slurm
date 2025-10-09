#!/bin/bash
#SBATCH --job-name=blip2_finetune
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/blip2_train_%j.out
#SBATCH --error=logs/blip2_train_%j.err

# Load required modules
module load cuda/11.7

# Activate virtual environment (adjust path as needed)
source .venv/bin/activate

# Print some info
echo "Job started on $(hostname) at $(date)"
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
nvidia-smi

# Run training
python blip2/train_blip2.py

echo "Job finished at $(date)"
