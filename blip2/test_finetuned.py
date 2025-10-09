"""Test the fine-tuned BLIP-2 model with LoRA adapters.

This script loads the fine-tuned model and generates opening lines for profiles.
"""

import torch
from PIL import Image
from peft import PeftModel
from transformers import (
    BitsAndBytesConfig,
    Blip2ForConditionalGeneration,
    Blip2Processor,
)


def load_finetuned_model(base_model_name: str, adapter_path: str, device: str):
    """Load the base model with fine-tuned LoRA adapters.

    Args:
        base_model_name: Name of the base BLIP-2 model
        adapter_path: Path to the fine-tuned LoRA adapters
        device: Device to load the model on ('cuda' or 'cpu')

    Returns:
        Tuple of (model, processor)
    """
    print("Loading processor...")
    processor = Blip2Processor.from_pretrained(base_model_name)

    # Configure quantization
    bnb_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0,
    )

    print("Loading base model...")
    model = Blip2ForConditionalGeneration.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map={"": 0} if device == "cuda" else None,
    )

    print("Loading LoRA adapters...")
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()

    return model, processor


def generate_opening_line(
    model,
    processor,
    image_path: str,
    profile_text: str,
    device: str,
    max_new_tokens: int = 100,
    temperature: float = 1.0,
) -> str:
    """Generate an opening line for a profile.

    Args:
        model: Fine-tuned BLIP-2 model
        processor: BLIP-2 processor
        image_path: Path to profile image
        profile_text: Text description of the profile
        device: Device to run inference on
        max_new_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (higher = more creative)

    Returns:
        Generated opening line
    """
    # Load image
    image = Image.open(image_path).convert("RGB")

    # Create prompt
    prompt = f"{profile_text}\n\nQuestion: What is the best flirting opening line to start a conversation with her on Tinder? Answer:"

    # Process inputs
    dtype = torch.float16 if device == "cuda" else torch.float32
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(
        device, dtype=dtype
    )

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=0.9,
            num_beams=4,
            repetition_penalty=1.2,
        )

    # Decode
    generated_text = processor.batch_decode(outputs, skip_special_tokens=True)[
        0
    ].strip()

    return generated_text


def main():
    """Main inference function."""
    # Configuration
    base_model_name = "Salesforce/blip2-opt-2.7b"
    adapter_path = "./blip2_rizz_finetuned"

    # Device setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # Load model
    model, processor = load_finetuned_model(base_model_name, adapter_path, device)

    # Example profile
    profile_text = (
        "Her name is Maren. "
        "Profile details: 27 kilometers away. "
        "Lifestyle: Non-smoker, has a dog, drinks socially on weekends, sometimes works out. "
        "She seems to love outdoor activities."
    )
    image_path = "data_collection/profiles/images/1/image_1.jpg"

    print("\n" + "=" * 60)
    print("Testing fine-tuned model")
    print("=" * 60)
    print(f"\nProfile: {profile_text}")
    print(f"Image: {image_path}")
    print("\nGenerating opening line...")

    # Generate opening line
    opening_line = generate_opening_line(
        model=model,
        processor=processor,
        image_path=image_path,
        profile_text=profile_text,
        device=device,
        temperature=1.0,
    )

    print(f"\nGenerated opening line:\n{opening_line}")
    print("\n" + "=" * 60)

    # Generate a few more variations
    print("\nGenerating alternative opening lines...")
    for i in range(3):
        alt_line = generate_opening_line(
            model=model,
            processor=processor,
            image_path=image_path,
            profile_text=profile_text,
            device=device,
            temperature=1.2,  # Higher temperature for more variety
        )
        print(f"\nAlternative {i + 1}:\n{alt_line}")


if __name__ == "__main__":
    main()
