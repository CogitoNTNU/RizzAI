# Generate annotations for fine-tuning using BLIP-2 with multi-image support
# This script extracts visual embeddings from multiple images per profile and concatenates them
# before generating text, allowing the model to consider all profile images simultaneously.
# The concatenated embeddings are passed through the Q-Former and language model for generation.
import json
from pathlib import Path

import ollama
import torch
from PIL import Image
from transformers import (
    BitsAndBytesConfig,
    Blip2ForConditionalGeneration,
    Blip2Processor,
)


# Global variables initialized in main
processor = None
model = None
device = None
dtype = None


def log_device_info() -> None:
    """Log PyTorch and CUDA device information for debugging."""
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA arch list: {torch.cuda.get_arch_list()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"Current CUDA device: {torch.cuda.current_device()}")
    print(f"CUDA available: {torch.cuda.is_available()}")


def initialize_device() -> tuple[str, torch.dtype]:
    """Initialize and return device and dtype based on CUDA availability."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    dtype = torch.float16 if device == "cuda" else torch.float32
    return device, dtype


def load_blip2_model(
    device: str, dtype: torch.dtype
) -> tuple[Blip2Processor, Blip2ForConditionalGeneration]:
    """Load BLIP-2 model and processor with appropriate quantization settings."""
    print("Loading BLIP-2 model...")
    processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
    model = Blip2ForConditionalGeneration.from_pretrained(
        "Salesforce/blip2-opt-2.7b",
        dtype=dtype,
        device_map={"": 0} if device == "cuda" else None,
        quantization_config=BitsAndBytesConfig(
            load_in_8bit=True, llm_int8_threshold=6.0
        ),
    )
    return processor, model


def load_profile_data(folder_path: str) -> dict:
    """Load profile data from JSON file."""
    json_file = "text_data.json"
    with open(str(folder_path + json_file), encoding="utf-8") as f:
        data = json.load(f)
    return data


def initialize_profiles_dict(data: dict) -> dict:
    """Initialize empty profiles dictionary with text and image descriptions."""
    profiles = {}
    for profile in data:
        profiles[profile] = {
            "text": "",
            "image_descriptions": [],
        }
    return profiles


def build_profile_text(data: dict, profile_id: str, profiles: dict) -> None:
    """Build comprehensive text description for a profile.

    Args:
        data: Raw profile data dictionary
        profile_id: Profile identifier
        profiles: Dictionary to update with profile text
    """
    curr_prof = profiles[profile_id]
    profile = data[profile_id]

    if profile.get("name") is not None:
        curr_prof["text"] += "Name: " + profile["name"] + ". "
    if profile.get("about_me") is not None:
        curr_prof["text"] += "About Me: " + profile["about_me"] + ". "

    # Essentials
    curr_prof["text"] += "Essentials: "
    for ess in profile.get("essentials", []):
        curr_prof["text"] += ess + ","
    curr_prof["text"] += ". "

    # Basics
    curr_prof["text"] += "Basics: "
    for bas_prefix, bas_data in profile.get("basics", {}).items():
        curr_prof["text"] += bas_prefix + ": " + bas_data + ", "
    curr_prof["text"] += ". "

    # Lifestyle
    curr_prof["text"] += "Lifestyle: "
    for lf_prefix, lf_data in profile.get("lifestyle", {}).items():
        curr_prof["text"] += lf_prefix + ": " + lf_data + ", "
    curr_prof["text"] += ". "

    # Interests
    curr_prof["text"] += "Interests: "
    for inter in profile.get("interests", []):
        curr_prof["text"] += inter + ", "
    curr_prof["text"] += ". "

    # Anthem
    if profile.get("anthem") is not None:
        curr_prof["text"] += "Anthem: " + profile["anthem"]


def load_profile_images(
    images_path: str, profile_id: str, profiles: dict
) -> list[Image.Image]:
    """Load images for a profile and generate their captions.

    Args:
        images_path: Path to images directory
        profile_id: Profile identifier
        profiles: Dictionary to update with image descriptions

    Returns:
        List of PIL Image objects for the profile
    """
    profile_images = []
    image_folder = Path(images_path) / profile_id

    for image_i in Path(image_folder).glob("*.jpg"):
        try:
            img = Image.open(image_i).convert("RGB")
            profile_images.append(img)

            # Generate image caption
            inputs_caption = processor(images=img, return_tensors="pt").to(device, dtype=dtype)
            generated_ids_caption = model.generate(**inputs_caption, max_new_tokens=20)
            image_description = processor.batch_decode(generated_ids_caption, skip_special_tokens=True)[0].strip()
            profiles[profile_id]["image_descriptions"].append(image_description)
        except Exception as e:
            print(f"  Warning: Could not load image {image_i.name} for profile {profile_id}: {e}")
            continue

    return profile_images


def extract_image_embeddings(image: Image.Image) -> torch.Tensor:
    """Extract vision embeddings for a single image.

    Args:
        image: PIL Image

    Returns:
        Image embeddings tensor
    """
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(
        device, dtype=dtype
    )

    with torch.no_grad():
        # Get vision model outputs (image features)
        vision_outputs = model.vision_model(pixel_values, return_dict=True)
        image_embeds = vision_outputs[0]  # [batch, seq_len, hidden_size]

        # Apply vision projection to match Q-Former input size
        image_embeds = model.vision_model.post_layernorm(image_embeds)

    return image_embeds


def generate_with_multiple_images(images: list[Image.Image], question: str) -> str:
    if not images:
        return ask_question_no_img(question)

    # Extract embeddings for each image
    all_image_embeds = []
    for img in images:
        img_embeds = extract_image_embeddings(img)
        all_image_embeds.append(img_embeds)

    # Concatenate image embeddings along sequence dimension
    concatenated_embeds = torch.cat(all_image_embeds, dim=1)

    # Process text input
    text_inputs = processor(text=question, return_tensors="pt").to(device)

    with torch.no_grad():
        # Get Q-Former outputs with concatenated visual features
        image_attention_mask = torch.ones(
            concatenated_embeds.size()[:-1], dtype=torch.long, device=device
        )
        query_tokens = model.query_tokens.expand(concatenated_embeds.shape[0], -1, -1)
        query_outputs = model.qformer(
            query_embeds=query_tokens,
            encoder_hidden_states=concatenated_embeds,
            encoder_attention_mask=image_attention_mask,
            return_dict=True,
        )
        query_output = query_outputs.last_hidden_state

        # Project to language-model dimension
        lm_inputs_from_img = model.language_projection(query_output)

        lm_embed_weight = model.language_model.get_input_embeddings().weight
        lm_dtype = lm_embed_weight.dtype  # the LM’s expected dtype (Float or Half)

        lm_inputs_from_img = lm_inputs_from_img.to(lm_dtype)
        text_token_embeds = model.language_model.get_input_embeddings()(
            text_inputs.input_ids
        ).to(lm_dtype)

        # Concatenate image embeddings + text embeddings
        inputs_embeds = torch.cat([lm_inputs_from_img, text_token_embeds], dim=1)

        # Build attention masks
        language_attention_mask = torch.ones(
            lm_inputs_from_img.size()[:-1], dtype=torch.long, device=device
        )
        attention_mask = torch.cat(
            [language_attention_mask, text_inputs.attention_mask], dim=1
        )

        # Generate from LM
        outputs = model.language_model.generate(
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            do_sample=False,
            num_beams=5,
            max_length=196,
            min_length=1,
            top_p=1.0,
            repetition_penalty=1.5,
            length_penalty=1.0,
            temperature=1.0,
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
        )

    answer = processor.batch_decode(outputs, skip_special_tokens=True)[0].strip()
    return answer



def ask_question_no_img(question: str) -> str:
    """Generate text response without images.

    Args:
        question: Text prompt/question

    Returns:
        Generated text answer
    """
    inputs = processor(text=question, return_tensors="pt").to(device)
    out = model.generate(
        **inputs,
        do_sample=False,
        num_beams=5,
        max_length=196,
        min_length=1,
        top_p=1.0,
        repetition_penalty=5,
        length_penalty=1.0,
        temperature=1,
    )
    answer = processor.batch_decode(out, skip_special_tokens=True)[0].strip()

    return answer


def data_to_prompt(profile_data: dict) -> str:
    """Convert profile data to a prompt for LLM processing.

    Args:
        profile_data: Dictionary containing profile information and image descriptions

    Returns:
        Formatted prompt string
    """
    profile_info = "This is a description of my images:"
    profile_desc = profile_data["image_descriptions"]
    for pd in profile_desc:
        profile_info += pd

    return ("My profile description:" 
        + profile_data["text"]
        + profile_info
        + ". Answer with only one sentence, one perfect opening line in english to charm me"
    )


def create_first_message(profile_data: dict, language_model: str) -> str | None:
    """Create the first message for a user based on provided data using Ollama.

    Args:
        profile_data: Dictionary containing message details
        language_model: The language model name to use (e.g., "llama2-uncensored:7b")

    Returns:
        Generated message content
    """
    response = ollama.chat(language_model, messages=[{"role": "user", "content": data_to_prompt(profile_data)}],)
    return response.message.content


def generate_annotations(profiles: dict, prof_img_dict: dict, language_model: str = "llama2-uncensored:7b") -> dict:
    """Generate annotations for all profiles with chosen and rejected responses.

    Args:
        profiles: Dictionary containing profile text and image descriptions
        prof_img_dict: Dictionary mapping profile IDs to image lists
        language_model: Ollama language model to use for generation

    Returns:
        Dictionary mapping profile IDs to annotation sets with chosen/rejected responses
    """
    annotation_set = {}
    print("\nGenerating annotations with multi-image embeddings...")

    for pid in profiles:
        print(f"Processing profile {pid}...")

        # Get images for this profile
        profile_images = prof_img_dict.get(pid, [])

        # Generate "rejected" response using multi-image BLIP-2 with concatenated embeddings
        if profile_images:
            question = f"Question: Based on these images and the profile: {profiles[pid]['text']}, what is a good opening line? Answer:"
            rejected_line = generate_with_multiple_images(profile_images, question)
        else:
            rejected_line = "I want to take you to the woods. 😉"

        # Generate "chosen" response using Ollama with image descriptions
        chosen_line = create_first_message(profiles[pid], language_model)

        annotation_set[pid] = {
            "chosen": chosen_line,
            "rejected": rejected_line,
            "num_images": len(profile_images),
        }

        print(f"  - Images used: {len(profile_images)}")
        print(f"  - Chosen: {chosen_line[:50]}...")
        print(f"  - Rejected: {rejected_line[:50]}...")

    return annotation_set


def save_annotations_to_file(annotation_set: dict, output_path: str) -> None:
    """Save annotation set to JSON file.

    Args:
        annotation_set: Dictionary of annotations to save
        output_path: Path where to save the JSON file
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(annotation_set, f, indent=4, ensure_ascii=False)
    print(f"Annotations saved to {output_path}")


def main() -> None:
    """Main function to orchestrate the entire annotation generation pipeline."""
    global processor, model, device, dtype

    # Initialize device and logging
    log_device_info()
    device, dtype = initialize_device()

    # Load model
    processor, model = load_blip2_model(device, dtype)

    # Define paths
    folder_path = "../RizzAI/data_collection/profiles/"
    image_path = folder_path + "images"
    output_path = "./data_collection/profiles/llm_lines_finetune.json"

    # Load profile data
    print("Loading profile data...")
    data = load_profile_data(folder_path)

    # Initialize profiles dictionary
    profiles = initialize_profiles_dict(data)

    # Build profile text for all profiles
    print("Building profile text descriptions...")
    for profile_id in data:
        build_profile_text(data, profile_id, profiles)

    # Load images and generate descriptions
    print("Loading images and generating image descriptions...")
    prof_img_dict = {}

    for profile_id in data:
        profile_images = load_profile_images(image_path, profile_id, profiles)
        prof_img_dict[profile_id] = profile_images

    # Generate annotations using both BLIP-2 and Ollama
    annotation_set = generate_annotations(profiles, prof_img_dict)

    # Save annotations to file
    save_annotations_to_file(annotation_set, output_path)

    print("Done!")


if __name__ == "__main__":
    main()

