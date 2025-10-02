import requests
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch


device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

print("Loading model...")
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b", load_in_8bit=True, device_map={"": 0}, dtype=dtype
)

url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(requests.get(url, stream=True).raw)


print("Testing image captioning...")
# First test: Image captioning
inputs_caption = processor(images=raw_image, return_tensors="pt").to(
    device, dtype=dtype
)
generated_ids_caption = model.generate(**inputs_caption, max_new_tokens=20)
caption = processor.batch_decode(generated_ids_caption, skip_special_tokens=True)[
    0
].strip()
print(f"Caption: '{caption}'")

print("\nTesting question answering...")
# Second test: Question answering with proper prompt format
prompt = "Question: how many cats are there? Answer:"
inputs = processor(images=image, text=prompt, return_tensors="pt").to(
    device=device, dtype=dtype
)

generated_ids = model.generate(**inputs)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[
    0
].strip()
print(generated_text)
