from transformers import InstructBlipProcessor, InstructBlipForConditionalGeneration
import torch
from PIL import Image
import requests

device = "cuda" if torch.cuda.is_available() else "cpu"

model = InstructBlipForConditionalGeneration.from_pretrained(
    "Salesforce/instructblip-vicuna-7b"
).to(device)
processor = InstructBlipProcessor.from_pretrained("Salesforce/instructblip-vicuna-7b")

image_path = "data_collection/profiles/images/1/image_1.jpg"
image = Image.open(image_path).convert("RGB")


def ask_question(question: str) -> str:
    inputs = processor(image, question, return_tensors="pt").to(device)

    out = model.generate(
        **inputs,
        do_sample=False,
        num_beams=5,
        max_length=256,
        min_length=1,
        top_p=0.9,
        repetition_penalty=1.5,
        length_penalty=1.0,
        temperature=1,
    )
    answer = processor.batch_decode(out, skip_special_tokens=True)[0].strip()

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
    "What is her name, how old is she, and what are some of her interests?",
    "How old is she?",
    "If I were to take her out, where would I take her?",
    "Why is she really pretty?",
    "What are some interesting facts I could mention about her?",
    "What would be a good flirty opening line to start a conversation with her?",
    "What is the best flirty opening line to start a conversation with her?",
    "What are some fun date ideas?",
]

for i, question in enumerate(questions):
    print(f"Question {i + 1}\n")

    print("Without description:")
    answer = ask_question(question)
    print(answer)
    print("-" * 10)

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
