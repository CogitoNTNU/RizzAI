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
    dtype=dtype,
    device_map={"": 0} if device == "cuda" else None,
    quantization_config=BitsAndBytesConfig(load_in_8bit=True, llm_int8_threshold=6.0),
)

image_path = "data_collection/profiles/images/1/image_1.jpg"
image = Image.open(image_path).convert("RGB")


print("Testing image captioning...")
# First test: Image captioning
inputs_caption = processor(images=image, return_tensors="pt").to(device, dtype=dtype)
generated_ids_caption = model.generate(**inputs_caption, max_new_tokens=20)
caption = processor.batch_decode(generated_ids_caption, skip_special_tokens=True)[
    0
].strip()
print(f"Caption: '{caption}'")

print("\nTesting question answering...\n")


def ask_question(question: str) -> str:
    inputs = processor(images=image, text=question, return_tensors="pt").to(
        device=device, dtype=dtype
    )
    out_ids = model.generate(
        **inputs,
        do_sample=True,
        num_beams=4,
        max_length=256,
        min_length=20,
        temperature=1.2,  # Higher creativity
        top_p=0.95,
        top_k=100,
        repetition_penalty=1.2,
        no_repeat_ngram_size=2,
        length_penalty=0.9,  # TODO: Play with shorter or longer answers
    )

    answer = processor.batch_decode(out_ids, skip_special_tokens=True)[0].strip()

    return answer


description = """\
Gender: Female;\
Name: Gabriela; \
Age: 22; \
She describes herself on her Tinder profile as Non-smoker, has a dog, drinks socially on weekends, sometimes works out, \
loves hiking and outdoor activities. \
"""

natural_description = """\
Her name is Gabriela. She is 22 years old. \
She is a non-smoker, has a dog, drinks socially on weekends, \
sometimes works out, and loves hiking and outdoor activities. \
I am a guy that is interested in her.\
"""


questions = [
    "Question: What is the best flirting opening line to start a conversation? Answer:",
    "What is the best flirting opening line to start a conversation? The best opening line is:",
    "We matched on Tinder, and given this information i want you to reply with the perfect opening line:",
    "The best flirting opening line to start a conversation is",
    'The best flirting line to get her attention is "',
    # f"Question: What would be a good opening line to start a conversation? Answer:",
    # f"Question: What are some interesting facts I could mention about her? Answer:",
    # f"Question: What are some fun date ideas? Answer:",
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
