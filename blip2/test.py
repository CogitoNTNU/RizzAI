import requests
import torch
from PIL import Image
from transformers import Blip2Model, Blip2Processor


device = "cpu"

processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2Model.from_pretrained("Salesforce/blip2-opt-2.7b", dtype=torch.float16)
model.to(device)
url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(requests.get(url, stream=True).raw)

prompt = "Her is her profile description: ... give me an opening line"
inputs = processor(images=image, text=prompt, return_tensors="pt").to(
    device, torch.float16
)

outputs = model(**inputs)
