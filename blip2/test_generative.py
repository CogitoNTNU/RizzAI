from transformers import Blip2Processor, Blip2Model, Blip2ForConditionalGeneration
from PIL import Image
import requests
import torch

# BLIP-2 with LM and model for feature extraction
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b", use_fast = True)
gen_model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b", dtype=torch.float16)

device = "cpu"
gen_model.to(device)


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

## Faktisk chat 
# while True:
#     user_input = input("Spør BLIP-2 om bildet (eller skriv 'exit'): ")
#     if user_input.lower() == "exit":
#         break
#     inputs = processor(images=image, text=user_input, return_tensors="pt").to(device, torch.float16)
#     generated_ids = gen_model.generate(**inputs, max_new_tokens=100)
#     generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
#     print("BLIP-2 svar:", generated_text)

generated_ids = gen_model.generate(**inputs, max_new_tokens=100)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
print("BLIP-2 svar:", generated_text)



