import requests
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch


device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading model...")
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b", dtype=torch.float16
)
model.to(device)


# Load and process the image
img_url = "https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg"
raw_image = Image.open(requests.get(img_url, stream=True).raw).convert("RGB")

print("Testing image captioning...")
# First test: Image captioning
inputs_caption = processor(images=raw_image, return_tensors="pt")
generated_ids_caption = model.generate(**inputs_caption, max_new_tokens=20)
caption = processor.batch_decode(generated_ids_caption, skip_special_tokens=True)[0]
print(f"Caption: '{caption}'")

print("\nTesting question answering...")
# Second test: Question answering with proper prompt format
prompt = "Question: how many dogs are in the picture? Answer:"
inputs_qa = processor(images=raw_image, text=prompt, return_tensors="pt").to(device)

# Debug: check what's in the inputs
print(f"Input IDs shape: {inputs_qa.input_ids.shape}")
print(f"Pixel values shape: {inputs_qa.pixel_values.shape}")

generated_ids_qa = model.generate(**inputs_qa, max_new_tokens=20)

full_response = processor.batch_decode(generated_ids_qa, skip_special_tokens=True)[0]
print(f"Full response: '{full_response}'")

# Extract just the answer part
if "Answer:" in full_response:
    answer = full_response.split("Answer:")[-1].strip()
    print(f"Extracted answer: '{answer}'")
else:
    print("No 'Answer:' found in response")
