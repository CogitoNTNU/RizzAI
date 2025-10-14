# Fine-Tuning BLIP-2 for RizzAI

This guide explains how to fine-tune the Salesforce BLIP-2 model for generating personalized Tinder opening lines.

## Overview

The fine-tuning process uses **Parameter-Efficient Fine-Tuning (PEFT)** with **LoRA (Low-Rank Adaptation)**. This approach:

- ✅ Only trains a small fraction of parameters (~1-2% of the model)
- ✅ Requires much less GPU memory than full fine-tuning
- ✅ Trains faster and is more efficient
- ✅ Can be loaded on top of the base model for inference

## Prerequisites

1. **Install dependencies:**
   ```bash
   uv sync
   ```

   This will install the required packages:
   - `transformers` - For BLIP-2 model
   - `peft` - For LoRA fine-tuning
   - `datasets` - For data handling
   - `bitsandbytes` - For 8-bit quantization
   - `accelerate` - For distributed training

2. **Prepare your dataset:**
   - Ensure you have profile data in `data_collection/profiles/text_data.json`
   - Ensure images are in `data_collection/profiles/images/`

## Scripts

### 1. `prepare_dataset.py`

Prepares the training data by:
- Loading profile JSON data
- Loading associated images
- Formatting profile information into natural text
- Creating training/validation splits

**Test it:**
```bash
python blip2/prepare_dataset.py
```

This will show you a sample of how the data looks.

### 2. `train_blip2.py`

Main training script that:
- Loads BLIP-2 with 8-bit quantization
- Applies LoRA adapters to query/value projections
- Trains on your dataset
- Saves the fine-tuned adapters

**Run training:**
```bash
python blip2/train_blip2.py
```

**Training Configuration:**
- **Epochs:** 3
- **Batch size:** 2 per device (effective batch size: 8 with gradient accumulation)
- **Learning rate:** 2e-4
- **LoRA rank (r):** 16
- **LoRA alpha:** 32

The model will be saved to `./blip2_rizz_finetuned/`

### 3. `test_finetuned.py`

Tests the fine-tuned model:
- Loads the base model with LoRA adapters
- Generates opening lines for test profiles
- Shows multiple variations

**Run inference:**
```bash
python blip2/test_finetuned.py
```

## Training Process

### Step-by-Step

1. **Prepare your data** (if not already done):
   ```bash
   python data_collection/web_scraper.py  # Collect profiles
   ```

2. **Test dataset preparation:**
   ```bash
   python blip2/prepare_dataset.py
   ```
   
   This should show you examples like:
   ```
   Training examples: 96
   Validation examples: 24
   
   Sample training example:
   Profile text: Her name is Ella. Profile details: 6 kilometers away...
   ```

3. **Start training:**
   ```bash
   python blip2/train_blip2.py
   ```
   
   You'll see output like:
   ```
   trainable params: 4,718,592 || all params: 2,707,918,592 || trainable%: 0.17
   ```
   
   Training will take several hours depending on your GPU.

4. **Test the fine-tuned model:**
   ```bash
   python blip2/test_finetuned.py
   ```

## Customization

### Adjust Training Parameters

Edit `train_blip2.py`:

```python
training_args = TrainingArguments(
    num_train_epochs=5,              # More epochs
    per_device_train_batch_size=4,   # Larger batch (needs more VRAM)
    learning_rate=1e-4,              # Different learning rate
    ...
)
```

### Adjust LoRA Configuration

Edit `train_blip2.py`:

```python
lora_config = LoraConfig(
    r=32,              # Higher rank = more parameters (better but slower)
    lora_alpha=64,     # Scaling factor
    lora_dropout=0.1,  # Higher dropout = more regularization
    ...
)
```

### Modify Dataset

Edit `prepare_dataset.py`:

- Change `format_profile_text()` to include/exclude different fields
- Modify the prompt template in `create_training_examples()`
- Adjust `max_images` to use multiple images per profile

### Improve Training Data

**Important:** The current implementation uses a template target. For best results, you should:

1. Collect actual good opening lines (manually or from successful conversations)
2. Label your data with quality ratings
3. Use DPO (Direct Preference Optimization) for better results

Example data format:
```python
{
    'profile_id': '1',
    'image': <PIL.Image>,
    'text': 'Profile: ... Question: What is the best opening line?',
    'target': 'Hey! I noticed you love hiking. Have you done the XYZ trail?'
}
```

## Hardware Requirements

### Minimum (CPU Training):
- 16 GB RAM
- Will be very slow (not recommended)

### Recommended (GPU Training):
- NVIDIA GPU with 8+ GB VRAM (RTX 3060, RTX 3070, etc.)
- 16 GB system RAM
- CUDA 11.7+ installed

### Optimal (Fast Training):
- NVIDIA GPU with 16+ GB VRAM (RTX 3090, RTX 4090, A100)
- 32 GB system RAM

## Troubleshooting

### Out of Memory (OOM)

If you get CUDA out of memory errors:

1. **Reduce batch size:**
   ```python
   per_device_train_batch_size=1
   ```

2. **Increase gradient accumulation:**
   ```python
   gradient_accumulation_steps=8  # Keeps effective batch size
   ```

3. **Reduce LoRA rank:**
   ```python
   r=8  # Lower rank = fewer parameters
   ```

### Slow Training

- Ensure you're using GPU (check `torch.cuda.is_available()`)
- Enable mixed precision training (fp16=True)
- Increase batch size if you have VRAM

### Poor Results

1. **Collect more/better training data**
2. **Train for more epochs**
3. **Adjust learning rate** (try 1e-4 or 5e-5)
4. **Use larger LoRA rank** (r=32 or r=64)
5. **Add data augmentation**

## Using SLURM (For Cluster Training)

If you're using a compute cluster:

```bash
sbatch jobs/gpu/train_blip2.slurm
```

Create `jobs/gpu/train_blip2.slurm`:
```bash
#!/bin/bash
#SBATCH --job-name=blip2_finetune
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/blip2_train_%j.out

module load cuda/11.7
source .venv/bin/activate

python blip2/train_blip2.py
```

## Next Steps

After fine-tuning:

1. **Integrate with your app** - Use the fine-tuned model in your Tinder bot
2. **A/B test** - Compare base model vs fine-tuned model performance
3. **Iterate** - Collect feedback and retrain with better data
4. **Try advanced techniques:**
   - DPO (Direct Preference Optimization)
   - RLHF (Reinforcement Learning from Human Feedback)
   - Multi-task learning (generate + classify)

## References

- [BLIP-2 Paper](https://arxiv.org/abs/2301.12597)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [PEFT Documentation](https://huggingface.co/docs/peft)
- [Transformers Documentation](https://huggingface.co/docs/transformers)
