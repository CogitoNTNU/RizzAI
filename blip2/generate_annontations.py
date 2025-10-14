#ollama pls save me, generate perfect opening line but also it has to use the vision part to get description of the pictures 
#can use the models current output as rejected "lines"
import os
import torch
from PIL import Image
from transformers import (
    BitsAndBytesConfig,
    Blip2ForConditionalGeneration,
    Blip2Processor,
)
import json
import ollama


    

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
with open(str(folder_path+json_file), "r") as f:
    data = json.load(f)

profiles = {}

for profile in data:
    profiles[profile["id"]] = {
        "text": "",
        "image_descriptions": [],
    }

for profile_id in data:
    currProf = profiles[profile_id]
    profile = data[profile_id]

    if profile['name'] != None:
        currProf['text'] += "Name: " + profile["name"] + ". "
    if profile['about_me'] != None:
        currProf['text'] += "About Me: " + profile["about_me"] + ". "
    
    # Essentials
    currProf['text'] += "Essentials: "
    for ess in profile["essentials"]:
        currProf['text'] += ess + ","
    currProf['text'] += ". "

    # Basics
    currProf['text'] += "Basics: "
    for bas_prefix, bas_data in profile['basics'].items():
        currProf['text'] += bas_prefix + ": " + bas_data + ", "
    currProf['text'] += ". "

    # Lifestyle
    currProf['text'] += "Lifestyle: "
    for lf_prefix, lf_data in profile["lifestyle"].items():
        currProf['text'] += lf_prefix + ": " + lf_data + ", "
    currProf['text'] += ". "

    # Interests
    currProf['text'] += "Interests: "
    for inter in profile["interests"]:
        currProf['text'] += inter +  ", "
    currProf['text'] += ". "

    # Anthem
    if profile['anthem'] != None:
        currProf['text'] += "Anthem: " + profile['anthem']

# Append image paths
image_path = folder_path + "images"

IMAGE_AMOUNT = len(os.listdir(image_path))

for profile_id in data:
    currProf = profiles[profile_id]
    
    image_folder = image_path + "/" + profile_id 
    for i in range(IMAGE_AMOUNT):
        try:
            inputs_caption = processor(images=Image.open(image_folder + "/image_" + i + ".jpg").convert("RGB"), return_tensors="pt").to(device, dtype=dtype)
            generated_ids_caption = model.generate(**inputs_caption, max_new_tokens=20)
            currProf["image_descriptions"].append(processor.batch_decode(generated_ids_caption, skip_special_tokens=True)[0].strip())
        finally:
            continue

#ollama
def data_to_prompt(data):
    profile_info = "This is a description of her tinder images:"
    profile_desc = data["image_descriptions"]
    for pd in profile_desc:
        profile_info += pd
    
    return profile_info + ". And here is her profile info:" + data["text"] + ". Give me the perfect opening line to this woman"

def create_first_message(data, l_model):
    """
    Create the first message for a user based on provided data.

    Args:
        data (dict): A dictionary containing message details.
        user_id (str): The ID of the user."""
    return ollama.chat(l_model, messages=[{'role': 'user', 'content': data_to_prompt(data)}])

annontation_set = {}
for pid in profiles:
    create_first_message(pid, "llama3.1")
