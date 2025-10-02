from PIL import Image
import requests
import torch

from transformers import (Blip2ForConditionalGeneration, 
                          Blip2Processor,
                          Blip2Config, 
                          TrainingArguments, 
                          Trainer, 
                          Blip2QFormerConfig, 
                          Blip2VisionConfig,
                          Blip2QFormerConfig,
                          OPTConfig)

qformer_config = Blip2QFormerConfig() 
vision_config = Blip2VisionConfig() #Image encoder Keep this 
text_config = OPTConfig() #Language model - Keep this

configuration = Blip2Config.from_text_vision_configs(vision_config, qformer_config, text_config)#Blip2Config()

model = Blip2ForConditionalGeneration(configuration)

processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")

url = "write some image url here"
image = Image.open(requests.get(url, stream=True).raw)

prompt = "Here is her profile description: ... give me an opening line"
inputs = processor(images=image, text=prompt, return_tensors="pt").to("gpu", torch.float16)

outputs = model(**inputs)
