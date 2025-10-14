"""Prepare dataset for BLIP-2 fine-tuning from collected Tinder profiles.

This script loads profile data and images, formats them for training.
"""

import json
from pathlib import Path
from typing import Any

from datasets import Dataset
from PIL import Image


def load_profile_data(json_path: str) -> dict[str, Any]:
    """Load profile data from JSON file."""
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def format_profile_text(profile: dict[str, Any]) -> str:
    """Format profile information into a natural text description.

    Args:
        profile: Dictionary containing profile information

    Returns:
        Formatted string describing the profile
    """
    parts = []

    # Name
    if profile.get("name"):
        parts.append(f"Her name is {profile['name']}.")

    # Essentials (location, height, etc)
    if profile.get("essentials"):
        essentials = [str(e) for e in profile["essentials"] if e]
        if essentials:
            parts.append(f"Profile details: {', '.join(essentials)}.")

    # About me
    if profile.get("about_me"):
        parts.append(f"About her: {profile['about_me']}")

    # Basics (love style, communication, etc)
    if profile.get("basics"):
        basics_list = [f"{k}: {v}" for k, v in profile["basics"].items() if v]
        if basics_list:
            parts.append(f"Her basics: {', '.join(basics_list)}.")

    # Lifestyle
    if profile.get("lifestyle"):
        lifestyle_list = [f"{k}: {v}" for k, v in profile["lifestyle"].items() if v]
        if lifestyle_list:
            parts.append(f"Lifestyle: {', '.join(lifestyle_list)}.")

    # Interests
    if profile.get("interests"):
        interests = [str(i) for i in profile["interests"] if i]
        if interests:
            parts.append(f"Interests: {', '.join(interests)}.")

    return " ".join(parts)


def load_profile_images(
    profile_id: str, images_dir: str, max_images: int = 3
) -> list[Image.Image]:
    """Load images for a profile.

    Args:
        profile_id: Profile ID (folder name)
        images_dir: Base directory containing image folders
        max_images: Maximum number of images to load per profile

    Returns:
        List of PIL Images
    """
    profile_image_dir = Path(images_dir) / profile_id
    images: list[Image.Image] = []

    if not profile_image_dir.exists():
        return images

    # Load images in order
    for i in range(max_images):
        image_path = profile_image_dir / f"image_{i}.jpg"
        if image_path.exists():
            try:
                img = Image.open(image_path).convert("RGB")
                images.append(img)
            except Exception as e:
                print(f"Warning: Could not load {image_path}: {e}")

    return images


def create_training_examples(
    profiles_data: dict[str, Any], images_dir: str, max_images: int = 3
) -> list[dict[str, Any]]:
    """Create training examples from profile data.

    Args:
        profiles_data: Dictionary of profile data
        images_dir: Directory containing profile images
        max_images: Maximum images per profile

    Returns:
        List of training examples with image, text, and target
    """
    examples = []

    for profile_id, profile in profiles_data.items():
        # Skip if no name (invalid profile)
        if not profile.get("name"):
            continue

        # Load images
        images = load_profile_images(profile_id, images_dir, max_images)
        if not images:
            print(f"Warning: No images found for profile {profile_id}")
            continue

        # Format profile text
        profile_text = format_profile_text(profile)

        # Create prompt for opening line generation
        prompt = f"{profile_text}\n\nQuestion: What is the best flirting opening line to start a conversation with her on Tinder? Answer:"

        # For now, we'll use a template target (you should replace this with actual good opening lines)
        # In a real scenario, you'd have labeled data with good/bad opening lines
        target = f"Hey {profile.get('name', 'there')}! I noticed we both seem to enjoy similar things. What's your favorite way to spend a weekend?"

        examples.append(
            {
                "profile_id": profile_id,
                "image": images[0],  # Use first image as primary
                "text": prompt,
                "target": target,
                "profile_text": profile_text,
            }
        )

    return examples


def prepare_dataset(
    json_path: str = "data_collection/profiles/text_data.json",
    images_dir: str = "data_collection/profiles/images",
    max_images: int = 1,
    train_split: float = 0.8,
) -> tuple[Dataset, Dataset]:
    """Prepare training and validation datasets.

    Args:
        json_path: Path to profile JSON data
        images_dir: Directory containing images
        max_images: Maximum images per profile
        train_split: Fraction of data to use for training

    Returns:
        Tuple of (train_dataset, val_dataset)
    """
    print("Loading profile data...")
    profiles_data = load_profile_data(json_path)
    print(f"Loaded {len(profiles_data)} profiles")

    print("Creating training examples...")
    examples = create_training_examples(profiles_data, images_dir, max_images)
    print(f"Created {len(examples)} training examples")

    if not examples:
        raise ValueError("No training examples created! Check your data.")

    # Split into train and validation
    split_idx = int(len(examples) * train_split)
    train_dataset = Dataset.from_list(examples[:split_idx])
    val_dataset = Dataset.from_list(examples[split_idx:])

    print(f"Training examples: {len(train_dataset)}")
    print(f"Validation examples: {len(val_dataset)}")

    return train_dataset, val_dataset


if __name__ == "__main__":
    # Test the dataset preparation
    train_ds, val_ds = prepare_dataset()

    print("\n" + "=" * 50)
    print("Sample training example:")
    print("=" * 50)
    sample = train_ds[0]
    print(f"Profile ID: {sample['profile_id']}")
    print(f"Profile text: {sample['profile_text'][:200]}...")
    print(f"Prompt: {sample['text'][:200]}...")
    print(f"Target: {sample['target']}")
    print(f"Image size: {sample['image'].size}")
