"""Fine-tune BLIP-2 model using LoRA for generating Tinder opening lines.

This script uses Parameter-Efficient Fine-Tuning (PEFT) with LoRA to adapt
the BLIP-2 model for generating personalized conversation starters.
"""

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    BitsAndBytesConfig,
    Blip2ForConditionalGeneration,
    Blip2Processor,
    Trainer,
    TrainingArguments,
)

from prepare_dataset import prepare_dataset


def print_trainable_parameters(model):
    """Print the number of trainable parameters in the model."""
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params:,} || "
        f"all params: {all_param:,} || "
        f"trainable%: {100 * trainable_params / all_param:.2f}"
    )


def collate_fn(batch, processor, device):
    """Custom collate function to process images and text for BLIP-2."""
    images = [item["image"] for item in batch]
    texts = [item["text"] for item in batch]
    targets = [item["target"] for item in batch]

    # Process inputs
    inputs = processor(
        images=images, text=texts, return_tensors="pt", padding=True, truncation=True
    ).to(device)

    # Process labels (targets)
    labels = processor(
        text=targets, return_tensors="pt", padding=True, truncation=True
    ).input_ids.to(device)

    # Replace padding token id with -100 so it's ignored in loss
    labels[labels == processor.tokenizer.pad_token_id] = -100

    inputs["labels"] = labels

    return inputs


class BLIP2Trainer(Trainer):
    """Custom Trainer for BLIP-2 with proper collation."""

    def __init__(self, *args, processor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor = processor

    def get_train_dataloader(self):
        """Override to use custom collate function."""
        from functools import partial
        from torch.utils.data import DataLoader

        collate = partial(collate_fn, processor=self.processor, device=self.args.device)
        return DataLoader(
            self.train_dataset,
            batch_size=self.args.per_device_train_batch_size,
            collate_fn=collate,
            shuffle=True,
        )

    def get_eval_dataloader(self, eval_dataset=None):
        """Override to use custom collate function."""
        from functools import partial
        from torch.utils.data import DataLoader

        eval_dataset = eval_dataset if eval_dataset is not None else self.eval_dataset
        collate = partial(collate_fn, processor=self.processor, device=self.args.device)
        return DataLoader(
            eval_dataset,
            batch_size=self.args.per_device_eval_batch_size,
            collate_fn=collate,
        )


def main():
    """Main training function."""
    # Configuration
    model_name = "Salesforce/blip2-opt-2.7b"
    output_dir = "./blip2_rizz_finetuned"

    # Device setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load processor
    print("Loading processor...")
    processor = Blip2Processor.from_pretrained(model_name)

    # Configure 8-bit quantization for memory efficiency
    bnb_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0,
    )

    # Load model with quantization
    print("Loading model...")
    model = Blip2ForConditionalGeneration.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map={"": 0} if device == "cuda" else None,
    )

    # Prepare model for training with gradient checkpointing
    model = prepare_model_for_kbit_training(model)
    model.config.use_cache = False  # Silence warnings with gradient checkpointing

    # Configure LoRA
    # We'll apply LoRA to the query and value projection matrices
    lora_config = LoraConfig(
        r=16,  # Rank of the LoRA matrices
        lora_alpha=32,  # Scaling factor
        target_modules=[
            "q_proj",  # Query projection
            "v_proj",  # Value projection
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="SEQ_2_SEQ_LM",
    )

    # Apply LoRA to model
    print("Applying LoRA...")
    model = get_peft_model(model, lora_config)
    print_trainable_parameters(model)

    # Load dataset
    print("\nLoading dataset...")
    train_dataset, val_dataset = prepare_dataset()

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=4,  # Effective batch size = 2 * 4 = 8
        warmup_steps=100,
        learning_rate=2e-4,
        fp16=device == "cuda",  # Use mixed precision on GPU
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=50,
        save_steps=100,
        save_total_limit=3,
        load_best_model_at_end=True,
        report_to="none",  # Disable wandb/tensorboard
        remove_unused_columns=False,  # Important for custom datasets
    )

    # Initialize trainer
    print("\nInitializing trainer...")
    trainer = BLIP2Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processor=processor,
    )

    # Train!
    print("\nStarting training...")
    trainer.train()

    # Save the final model
    print("\nSaving model...")
    model.save_pretrained(output_dir)
    processor.save_pretrained(output_dir)

    print(f"\nTraining complete! Model saved to {output_dir}")
    print("To use the fine-tuned model, load it with:")
    print(f"  model = Blip2ForConditionalGeneration.from_pretrained('{output_dir}')")


if __name__ == "__main__":
    main()
