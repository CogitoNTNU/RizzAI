import json
import os
from PIL import Image
from datasets import Dataset
from transformers import (
    Blip2ForConditionalGeneration,
    Blip2Processor,
    Trainer,
    TrainingArguments,
)
import torch

# 1) Load a *pretrained* BLIP-2 model & processor that match
model_name = "Salesforce/blip2-flan-t5-xl"
processor = Blip2Processor.from_pretrained(model_name)
model = Blip2ForConditionalGeneration.from_pretrained(model_name)

# (Optional) Freeze vision tower if you want
for p in model.vision_model.parameters():
    p.requires_grad = False

def build_profiles(text_json_path, pairs_json_path):
    """Returns a dict: id -> {'profile_text': str, 'images': [PIL,...], 'chosen': str}"""
    with open(text_json_path) as f:
        profiles_raw = json.load(f)
    with open(pairs_json_path) as f:
        pairs_raw = json.load(f)

    # Build profile text
    profiles = {}
    for pid, prof in profiles_raw.items():
        txt = []
        if prof.get("name") is not None:
            txt.append(f"Name: {prof['name']}.")
        if prof.get("about_me") is not None:
            txt.append(f"About Me: {prof['about_me']}.")
        # Essentials
        ess = prof.get("essentials", [])
        if ess:
            txt.append("Essentials: " + ",".join(ess) + ".")
        # Basics
        basics = prof.get("basics", {})
        if basics:
            txt.append("Basics: " + ", ".join([f"{k}: {v}" for k, v in basics.items()]) + ".")
        # Lifestyle
        lifestyle = prof.get("lifestyle", {})
        if lifestyle:
            txt.append("Lifestyle: " + ", ".join([f"{k}: {v}" for k, v in lifestyle.items()]) + ".")
        # Interests
        interests = prof.get("interests", [])
        if interests:
            txt.append("Interests: " + ", ".join(interests) + ".")
        # Anthem
        if prof.get("anthem") is not None:
            txt.append(f"Anthem: {prof['anthem']}.")

        profile_text = " ".join(txt).strip()

        # Images
        image_dir = os.path.join(os.path.dirname(text_json_path), "images", pid)
        images = []
        if os.path.isdir(image_dir):
            # load every file named image_*.jpg
            for fname in sorted(os.listdir(image_dir)):
                if fname.lower().endswith(".jpg") and fname.startswith("image_"):
                    path = os.path.join(image_dir, fname)
                    try:
                        images.append(Image.open(path).convert("RGB"))
                    except Exception:
                        pass

        profiles[pid] = {
            "profile_text": profile_text,
            "images": images,
            "chosen": pairs_raw.get(pid, {}).get("chosen", "").strip(),
            # "rejected": pairs_raw.get(pid, {}).get("rejected", "").strip(),  # not used here
        }
    return profiles

def flatten_to_examples(profiles_dict):
    """
    Make one example per image:
      {"image": PIL, "prompt": <string>, "answer": <string>}
    """
    examples = []
    for pid, rec in profiles_dict.items():
        prompt_text = "Her profile: " + rec["profile_text"]
        answer_text = rec["chosen"] or ""  # ensure string
        for img in rec["images"]:
            examples.append({
                "image": img,
                "prompt": prompt_text,
                "answer": answer_text
            })
    return examples

# Build/flatten
profiles = build_profiles(
    "/cluster/home/kristiac/rizzai/RizzAI/data_collection/profiles/text_data.json",
    "/cluster/home/kristiac/rizzai/RizzAI/data_collection/profiles/llm_lines_finetune.json",
)
examples = flatten_to_examples(profiles)

# IMPORTANT: from_list (NOT from_dict)
dataset = Dataset.from_list(examples)
split = dataset.train_test_split(test_size=0.5, seed=42)
train_dataset, eval_dataset = split["train"], split["test"]

# 2) Custom data collator to produce model-forward inputs
class Blip2Collator:
    def __init__(self, processor, label_pad_token_id: int = -100):
        self.processor = processor
        self.label_pad_token_id = label_pad_token_id

        # Safety: ensure a pad token exists (T5 has one, but keep this robust)
        tok = self.processor.tokenizer
        if tok.pad_token_id is None:
            if tok.eos_token_id is not None:
                tok.pad_token = tok.eos_token
            else:
                # fall back to id 0 if neither is set
                tok.add_special_tokens({"pad_token": "<pad>"})

    def __call__(self, batch):
        images = [b["image"] for b in batch]
        prompts = [b["prompt"] for b in batch]
        targets = [b["answer"] for b in batch]

        # Inputs for the model (vision + text prompt)
        inputs = self.processor(
            images=images,
            text=prompts,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )

        # Labels: tokenize with the *tokenizer* directly (no context manager)
        labels = self.processor.tokenizer(
            targets,
            padding=True,
            truncation=True,
            return_tensors="pt",
        ).input_ids

        # Ignore loss on padding
        pad_id = self.processor.tokenizer.pad_token_id
        labels[labels == pad_id] = self.label_pad_token_id

        inputs["labels"] = labels
        return inputs


data_collator = Blip2Collator(processor)

class CleanInputsTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        # Strip keys the model doesn't expect
        if "num_items_in_batch" in inputs:
            inputs = {k: v for k, v in inputs.items() if k != "num_items_in_batch"}
        outputs = model(**inputs)
        loss = outputs["loss"] if isinstance(outputs, dict) else outputs.loss
        return (loss, outputs) if return_outputs else loss



# 3) Training args (note: evaluation_strategy, not eval_strategy)
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=1,   # XL model is big; start small
    gradient_accumulation_steps=8,   # keep effective batch ~8
    num_train_epochs=300,
    learning_rate=5e-5,
    eval_strategy="epoch",
    save_strategy="no",
    logging_dir="./logs",
    fp16=torch.cuda.is_available(),
    remove_unused_columns=False,     # <-- required for multimodal
    report_to="none",
    load_best_model_at_end=False,       # since we won't be saving checkpoints
    save_safetensors=True,              # final save uses .safetensors
    include_num_input_tokens_in_batch=False,
)

# then use it:
trainer = CleanInputsTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
)

trainer.train()
model.save_pretrained("./final", safe_serialization=True)
processor.save_pretrained("./final")