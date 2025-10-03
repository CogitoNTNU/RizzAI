import torch
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor


device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if torch.cuda.is_available() else torch.float32

processor = BlipProcessor.from_pretrained("Salesforce/blip2-opt-6.7b-coco")
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-6.7b-coco", torch_dtype=dtype
).to(device)

image_path = "data_collection/profiles/images/1/image_1.jpg"
raw_image = Image.open(image_path).convert("RGB")

print("Testing stronger rizz...")
print("Unconditional image captioning...")
inputs = processor(raw_image, return_tensors="pt").to(device, dtype)
out = model.generate(**inputs)
print(processor.decode(out[0], skip_special_tokens=True))

print("\n" + "=" * 20 + "\n")
print("Conditional image captioning...")


def ask_question(question: str) -> str:
    inputs = processor(raw_image, question, return_tensors="pt").to(device, dtype)
    out = model.generate(
        **inputs,
        do_sample=True,
        num_beams=1,
        max_length=120,
        min_length=20,
        temperature=1.1,  # Higher creativity
        top_p=0.95,
        top_k=100,
        repetition_penalty=1.2,
        no_repeat_ngram_size=2,
        length_penalty=1.0,  # TODO: Play with shorter or longer answers
    )

    answer = processor.decode(out[0], skip_special_tokens=True)

    return answer


description = """\
DESCRIPTION OF THE GIRL: \
Girl's name: Gabriela; \
Age: 22; \
Non-smoker, has a dog, drinks socially on weekends, sometimes works out, \
loves hiking and outdoor activities. \
I am a guy that is interested in her.
"""

natural_description = """\
Her name is Gabriela. She is 22 years old. \
She is a non-smoker, has a dog, drinks socially on weekends, \
sometimes works out, and loves hiking and outdoor activities. \
I am a guy that is interested in her.
"""


questions = [
    # "What is her name, how old is she, and what are some of her interests?",
    # "How old is she?",
    # "If I were to take her out, where would I take her?",
    # "Why is she really pretty?",
    # "What are some interesting facts I could mention about her?",
    # "What would be a good flirty opening line to start a conversation with her?",
    "What is the best flirty opening line to start a conversation with her?",
    # "What are some fun date ideas?",
]

for i, question in enumerate(questions):
    print(f"Question {i + 1}\n")

    # print("Without description:")
    # answer = ask_question(question)
    # print(answer)
    # print("-" * 10)

    # print("With description:")
    # answer = ask_question(
    #     f"{description} {question}"
    # )  # add description to each question
    # print(answer)
    # print("-" * 10)

    print("With a natural description:")
    answer = ask_question(
        f"{natural_description} {question}"
    )  # add description to each question
    print(answer)
    print("\n" + "=" * 20 + "\n")
