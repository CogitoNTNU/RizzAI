# Generate annotations for fine-tuning using BLIP-2 with multi-image support
# This script extracts visual embeddings from multiple images per profile and concatenates them
# before generating text, allowing the model to consider all profile images simultaneously.
# The concatenated embeddings are passed through the Q-Former and language model for generation.
import json
import os

import ollama
import torch
from PIL import Image
from transformers import (
    BitsAndBytesConfig,
    Blip2ForConditionalGeneration,
    Blip2Processor,
)


print(torch.__version__)
print(torch.cuda.get_arch_list())
print(torch.cuda.get_device_name(0))
print(torch.cuda.current_device())
print(torch.cuda.is_available())


device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
dtype = torch.float16 if device == "cuda" else torch.float32


print("Loading model...")
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b",
    dtype=dtype,
    device_map={"": 0} if device == "cuda" else None,
    quantization_config=BitsAndBytesConfig(load_in_8bit=True, llm_int8_threshold=6.0),
)

folder_path = "/cluster/home/kristiac/rizzai/RizzAI/data_collection/profiles/"
json_file = "text_data.json"
with open(str(folder_path + json_file)) as f:
    data = json.load(f)

profiles = {}

for profile in data:
    profiles[profile] = {
        "text": "",
        "image_descriptions": [],
    }


def extract_image_embeddings(image):
    """Extract vision embeddings for a single image.
    
    Args:
        image: PIL Image
        
    Returns:
        Image embeddings tensor
    """
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device, dtype=dtype)
    
    with torch.no_grad():
        # Get vision model outputs (image features)
        vision_outputs = model.vision_model(pixel_values, return_dict=True)
        image_embeds = vision_outputs[0]  # [batch, seq_len, hidden_size]
        
        # Apply vision projection to match Q-Former input size
        image_embeds = model.vision_model.post_layernorm(image_embeds)
        
    return image_embeds


def generate_with_multiple_images(images, question: str) -> str:
    """Generate text using concatenated embeddings from multiple images.
    
    Args:
        images: List of PIL Images
        question: Text prompt/question
        
    Returns:
        Generated text answer
    """
    if not images:
        return ask_question_no_img(question)
    
    # Extract embeddings for each image
    all_image_embeds = []
    for img in images:
        img_embeds = extract_image_embeddings(img)
        all_image_embeds.append(img_embeds)
    
    # Concatenate image embeddings along sequence dimension
    # Shape: [1, total_seq_len, hidden_size]
    concatenated_embeds = torch.cat(all_image_embeds, dim=1)
    
    # Process text input
    text_inputs = processor(text=question, return_tensors="pt").to(device)
    
    # Forward pass through Q-Former with concatenated image embeddings
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
        
        # Project to language model dimension
        language_model_inputs = model.language_projection(query_output)
        language_attention_mask = torch.ones(
            language_model_inputs.size()[:-1], dtype=torch.long, device=device
        )
        
        # Prepare language model inputs
        inputs_embeds = model.language_model.get_input_embeddings()(
            text_inputs.input_ids
        )
        inputs_embeds = torch.cat([language_model_inputs, inputs_embeds], dim=1)
        
        attention_mask = torch.cat(
            [language_attention_mask, text_inputs.attention_mask], dim=1
        )
        
        # Generate
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


def ask_question(images, question: str) -> str:
    """Single image question answering (kept for backwards compatibility)."""
    if isinstance(images, list):
        # If multiple images provided, use the new multi-image approach
        return generate_with_multiple_images(images, question)
    
    inputs = processor(images=images, text=question, return_tensors="pt").to(device)

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


def ask_question_no_img(question: str) -> str:
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


for profile_id in data:
    currProf = profiles[profile_id]
    profile = data[profile_id]

    if profile["name"] != None:
        currProf["text"] += "Name: " + profile["name"] + ". "
    if profile["about_me"] != None:
        currProf["text"] += "About Me: " + profile["about_me"] + ". "

    # Essentials
    currProf["text"] += "Essentials: "
    for ess in profile["essentials"]:
        currProf["text"] += ess + ","
    currProf["text"] += ". "

    # Basics
    currProf["text"] += "Basics: "
    for bas_prefix, bas_data in profile["basics"].items():
        currProf["text"] += bas_prefix + ": " + bas_data + ", "
    currProf["text"] += ". "

    # Lifestyle
    currProf["text"] += "Lifestyle: "
    for lf_prefix, lf_data in profile["lifestyle"].items():
        currProf["text"] += lf_prefix + ": " + lf_data + ", "
    currProf["text"] += ". "

    # Interests
    currProf["text"] += "Interests: "
    for inter in profile["interests"]:
        currProf["text"] += inter + ", "
    currProf["text"] += ". "

    # Anthem
    if profile["anthem"] != None:
        currProf["text"] += "Anthem: " + profile["anthem"]

# Append image paths
image_path = folder_path + "images"

IMAGE_AMOUNT = len(os.listdir(image_path))

prof_img_dict = {}
image_description_dict = {}  # dictionnary containing every image descriptions for each profilepir
for profile_id in data:
    currProf = profiles[profile_id]
    prof_img_dict[profile_id] = []
    image_folder = image_path + "/" + profile_id
    image_description_dict[profile_id] = []
    for i in range(IMAGE_AMOUNT):
        try:
            img = Image.open(image_folder + "/image_" + i + ".jpg").convert("RGB")
            prof_img_dict[profile_id].append(img)
            inputs_caption = processor(images=img, return_tensors="pt").to(
                device, dtype=dtype
            )
            generated_ids_caption = model.generate(**inputs_caption, max_new_tokens=20)
            image_description = processor.batch_decode(
                generated_ids_caption, skip_special_tokens=True
            )[0].strip()
            image_description_dict[profile_id].append(image_description)
            currProf["image_descriptions"].append(image_description)
        except:
            continue


# ollama
def data_to_prompt(data):
    profile_info = "This is a description of my images:"
    profile_desc = data["image_descriptions"]
    for pd in profile_desc:
        profile_info += pd

    return ("My profile description" +
        profile_info
        + ". And here is a description of my images:"
        + data["text"]
        + ". Answer with only one sentence, one perfect opening line in english to charm me"
    )


def create_first_message(data, l_model):
    """Create the first message for a user based on provided data.

    Args:
        data (dict): A dictionary containing message details.
        l_model (str): The language model name to use.
    """
    return ollama.chat(l_model, messages=[{"role": "user", "content": data_to_prompt(data)}])


annontation_set = {}
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
    chosen_line = create_first_message(profiles[pid], "llama2-uncensored:7b").message.content
    
    annontation_set[pid] = {
        "chosen": chosen_line,
        "rejected": rejected_line,
        "num_images": len(profile_images),
    }
    
    print(f"  - Images used: {len(profile_images)}")
    print(f"  - Chosen: {chosen_line[:50]}...")
    print(f"  - Rejected: {rejected_line[:50]}...")

# write JSON to file using a file object
output_path = "./data_collection/profiles/llm_lines_finetune.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(annontation_set, f, indent=4)
