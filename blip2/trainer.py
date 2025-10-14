import json
from PIL import Image
import os
from transformers import (Blip2ForConditionalGeneration, 
                          Blip2Processor,
                          Blip2Config, 
                          TrainingArguments, 
                          Trainer, 
                          Blip2QFormerConfig, 
                          Blip2VisionConfig,
                          Blip2QFormerConfig,
                          OPTConfig)
from datasets import Dataset, load_dataset



#Config for the model used --------->

qformer_config = Blip2QFormerConfig() 

"""hidden_size=700, 
                                    num_hidden_layers=10, 
                                    num_attention_heads=10,
                                    intermediate_size=2998,
                                    hidden_act="gelu_new",
                                    hidden_dropout_prob=0.08,
                                    attention_probs_dropout_prob=0.08,
                                    max_position_embeddings=2048,
                                    initializer_range=0.03,
                                    layer_norm_eps=1e-12,
                                    pad_token_id=0,
                                    position_embedding_type="absolute",
                                    cross_attention_frequency=2,
                                    encoder_hidden_size=1337,
                                    use_qformer_text_input=False) #This we want to improve and change """


vision_config = Blip2VisionConfig() #Image encoder Keep this 
text_config = OPTConfig() #Language model - Keep this

configuration = Blip2Config.from_text_vision_configs(vision_config, qformer_config, text_config) #Blip2Config()
#<------------------------------


# From model we generate/load the model we are going to train ----------->
model = Blip2ForConditionalGeneration(configuration)

processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")

#<----------------

# Format data ----------------------->

def to_parsable_data(input_path):
    """
    Convert prompt from "xxx" to [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": "xxx"}]}]
    and chosen and rejected from "xxx" to [{"role": "assistant", "content": [{"type": "text", "text": "xxx"}]}].
    Images are wrapped into a list.
    """
    with open(input_path, "r") as f:
        data = json.load(f)

    # with open(supervised_path, "r") as f:
    #     corrective_data = json.load(f)

    profiles = {}

    for profile in data:
        profiles[profile] = {
            "text": "",
            "images": [],
            "image_prompt_list": []
        }

    for profile_id in data:
        currProf = profiles[profile_id]
        profile = data[profile_id]

        if profile['name'] != None:
            currProf['text'] += "Name: " + profile["name"] + ". "
        if profile['about_me'] != None:
            currProf['text'] += "About Me: " + profile["about_me"] + ". "
        
        # Essentials
        currProf['text'] += "Essentials: "
        for ess in profile["essentials"]:
            currProf['text'] += ess + ","
        currProf['text'] += ". "

        # Basics
        currProf['text'] += "Basics: "
        for bas_prefix, bas_data in profile['basics'].items():
            currProf['text'] += bas_prefix + ": " + bas_data + ", "
        currProf['text'] += ". "

        # Lifestyle
        currProf['text'] += "Lifestyle: "
        for lf_prefix, lf_data in profile["lifestyle"].items():
            currProf['text'] += lf_prefix + ": " + lf_data + ", "
        currProf['text'] += ". "

        # Interests
        currProf['text'] += "Interests: "
        for inter in profile["interests"]:
            currProf['text'] += inter +  ", "
        currProf['text'] += ". "

        # Anthem
        if profile['anthem'] != None:
            currProf['text'] += "Anthem: " + profile['anthem']
    
    # Append image paths
    image_path = input_path.replace("text_data.json", "") + "images"

    IMAGE_AMOUNT = len(os.listdir(image_path))

    for profile_id in data:
        currProf = profiles[profile_id]
        
        image_folder = image_path + "/" + profile_id
        for i in range(IMAGE_AMOUNT):
            try:
                currProf['images'].append(Image.open(image_folder + "/image_" + i + ".jpg").convert("RGB"))
                currProf['image_prompt_list'].append({"type": "image"})
            finally:
                continue
        currProf['image_prompt_list'].append({"type": "text", "text": "Her profile: " + currProf['text']})
    
    output_dict = {}
    for id in profiles:
        prompt = [{"role": "user", "content": profiles[id]['image_prompt_list']}]
        chosen = [{"role": "assistant", "content": [{"type": "text", "text": "chosen"}]}]
        rejected = [{"role": "assistant", "content": [{"type": "text", "text": "rejected"}]}]
        output_dict[id]={"prompt": prompt, "images": profiles[id]['images'], "chosen": chosen, "rejected": rejected}
    
    return output_dict
#<------------------------------------


#Define set and run training loop ---------->
# Freeze vision encoder
for param in model.vision_model.parameters():
    param.requires_grad = False

if not os.path.exists("./results"):
    os.mkdir("./results")

if not os.path.exists("./logs"):
    os.mkdir("./logs")

training_args = TrainingArguments(
    output_dir='./results', # TODO: Add result directory
    per_device_train_batch_size=8,
    num_train_epochs=3,
    learning_rate=5e-5,
    evaluation_strategy='epoch',
    save_strategy='epoch',
    logging_dir='./logs', #TODO: Add log directory
    fp16=True
)

 
ddataset = Dataset.from_dict(to_parsable_data("string to json with data", "string to json with correction"))
split_dataset = ddataset.train_test_split(test_size=0.5, seed=42)
train_dataset, valid_dataset = split_dataset["train"], split_dataset["test"]

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset, 
    eval_dataset=valid_dataset, 
    tokenizer=processor.tokenizer
)

trainer.train()

#<--------------------------------

output_data = to_parsable_data("./data_collection/profiles/text_data.json")
