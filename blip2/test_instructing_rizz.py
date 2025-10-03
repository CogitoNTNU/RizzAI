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

better_description = """\
Her name is Gabriela. She is 22 years old. \
She is a non-smoker, has a dog, drinks socially on weekends, \
sometimes works out, and loves hiking and outdoor activities. \
I am a guy that is interested in her.
"""


questions = [
    "Her name is",
    "She is",
    "If I were to take her out, I would take her to",
    "She is really pretty because",
    "Some interesting facts I could mention about her are",
    "A good opening line to start a conversation with her would be",
    "The best opening line to start a conversation with her is",
    # f"Question: What is her name? Answer:",
    # f"Question: How old is she? Answer:",
    # f"Question: What are some of her interests? Answer:",
    # f"Question: What is so pretty about her? Answer:",
    # f"Question: {description} What would be a good opening line to start a conversation? Answer:",
    # f"Question: {description} What are some interesting facts I could mention about her? Answer:",
    # f"Question: {description} What are some fun date ideas? Answer:",
]

for question in questions:
    print("Without description:")
    answer = ask_question(question)
    print(answer)
    print("-" * 10)

    print("With description:")
    answer = ask_question(
        f"{description} {question}"
    )  # add description to each question
    print(answer)
    print("-" * 10)

    print("With better description:")
    answer = ask_question(
        f"{better_description} {question}"
    )  # add description to each question
    print(answer)
    print("\n" + "=" * 20 + "\n")

    # if question.endswith("Answer:"):
    #     question = question.split("Answer:")[0].strip()
    #     answer = answer[len(question):].strip() # remove the question part from the answer

    # print(f"Prompt: '{question}'")
    # print(f"Answer: '{answer}'\n")
    # print(answer)
