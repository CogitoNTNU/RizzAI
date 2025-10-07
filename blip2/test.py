import requests
import torch
from PIL import Image
from transformers import (
    BitsAndBytesConfig,
    Blip2ForConditionalGeneration,
    Blip2Processor,
)


device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
dtype = torch.float16 if device == "cuda" else torch.float32

print("Loading model...")
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b",
    device_map={"": 0} if device == "cuda" else None,
    dtype=dtype,
    quantization_config=BitsAndBytesConfig(load_in_8bit=True, llm_int8_threshold=6.0),
)

url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(requests.get(url, stream=True).raw)


print("Testing image captioning...")
# First test: Image captioning
inputs_caption = processor(images=image, return_tensors="pt").to(device, dtype=dtype)
generated_ids_caption = model.generate(**inputs_caption, max_new_tokens=20)
caption = processor.batch_decode(generated_ids_caption, skip_special_tokens=True)[
    0
].strip()
print(f"Caption: '{caption}'")

print("\nTesting question answering...")


def ask_question(question: str) -> str:
    inputs = processor(images=image, text=question, return_tensors="pt").to(
        device=device, dtype=dtype
    )
    generated_ids = model.generate(**inputs, max_new_tokens=50)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[
        0
    ].strip()

    answer = generated_text[len(question) :].strip()

    return answer


questions = [
    "Question: what is this a picture of? Answer:",
    "Question: how many cats are there? Answer:",
    "Question: what are the cats doing? Answer:",
    "Question: what is the color of the blanket? Answer:",
    "Question: Describe the image in detail. Answer:",
]

for question in questions:
    answer = ask_question(question)
    print(f"Prompt: '{question}'")
    print(f"Answer: '{answer}'\n")
