from PIL import Image
import requests
import torch

from transformers import (
    Blip2ForConditionalGeneration,
    Blip2Processor,
    Blip2Config,
    TrainingArguments,
    Trainer,
    Blip2QFormerConfig,
    Blip2VisionConfig,
    Blip2QFormerConfig,
    OPTConfig,
)

qformer_config = Blip2QFormerConfig()
vision_config = Blip2VisionConfig()  # Image encoder Keep this
text_config = OPTConfig()  # Language model - Keep this

configuration = Blip2Config.from_text_vision_configs(
    vision_config, qformer_config, text_config
)  # Blip2Config()

model = Blip2ForConditionalGeneration(configuration)

processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")

url = "https://static.wikia.nocookie.net/dreamworks/images/3/34/Fiona_Profile.jpg/revision/latest?cb=20231223034631"
image = Image.open(requests.get(url, stream=True).raw)

prompt = "Here is her profile description: - Princess, - Loves Shrekians, - Has a human form, - 25 y.o, - Rich, - Loves a true man, - Long Term. Give me an opening line for this person"
inputs = processor(images=image, text=prompt, return_tensors="pt").to(
    "gpu", torch.float16
)

# outputs = model(**inputs)

generated_ids_qa = model.generate(**inputs)

# Ensure generated_ids_qa is a list of integers
generated_ids_qa = (
    [int(token) for token in generated_ids_qa]
    if not isinstance(generated_ids_qa[0], int)
    else generated_ids_qa
)

full_response = processor.batch_decode(generated_ids_qa, skip_special_tokens=True)[0]
print(f"Full response: '{full_response}'")

# Extract just the answer part
if "Answer:" in full_response:
    answer = full_response.split("Answer:")[-1].strip()
    print(f"Extracted answer: '{answer}'")
else:
    print("No 'Answer:' found in response")
