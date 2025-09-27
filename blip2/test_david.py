from transformers import Blip2Processor, Blip2Model, Blip2ForConditionalGeneration
from PIL import Image
import requests
import torch

# BLIP-2 with LM and model for feature extraction
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b", use_fast = True)
base_model = Blip2Model.from_pretrained("Salesforce/blip2-opt-2.7b", dtype=torch.float16)

device = "cpu"
base_model.to(device)


def resize_image(image, output_size=(224, 224)):
    resized_image = image.resize(output_size)
    return resized_image

# Image and input
image_path = "images/image1.png"
image = Image.open(image_path).convert("RGB")
resized_image = resize_image(image)


# url = "something_something"
# image = Image.open(requests.get(url, stream=True).raw).convert("RGB")

prompt = "Beskriv hva som skjer i dette bildet."
inputs = processor(images=resized_image, text=prompt, return_tensors="pt").to(device, torch.float16)
base_inputs = processor(images=resized_image, text=prompt, return_tensors="pt").to(device, torch.float16)


with torch.no_grad():

    outputs = base_model(**base_inputs)

    # Vision encoder output (CLIP)
    vision_hidden_states = outputs.vision_outputs.last_hidden_state
    print("Vision hidden states shape:", vision_hidden_states.shape)

    # Q-Former output (tekst-bilde kobling)
    qformer_hidden_states = outputs.qformer_outputs.last_hidden_state
    print("Q-Former hidden states shape:", qformer_hidden_states.shape)


