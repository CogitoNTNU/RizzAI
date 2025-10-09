import json
from PIL import Image
from transformers import (Blip2ForConditionalGeneration, 
                          Blip2Processor,
                          Blip2Config, 
                          TrainingArguments, 
                          Trainer, 
                          Blip2QFormerConfig, 
                          Blip2VisionConfig,
                          Blip2QFormerConfig,
                          OPTConfig)



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

configuration = Blip2Config.from_text_vision_configs(vision_config, qformer_config, text_config)#Blip2Config()
#<------------------------------


# From model we generate/load the model we are going to train ----------->
model = Blip2ForConditionalGeneration(configuration)

processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")

#<----------------

# Format data ----------------------->

def to_parsable_data(input_path, supervised_path):
    """
    Convert prompt from "xxx" to [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": "xxx"}]}]
    and chosen and rejected from "xxx" to [{"role": "assistant", "content": [{"type": "text", "text": "xxx"}]}].
    Images are wrapped into a list.
    """
    with open(input_path, "r") as f:
        data = json.load(f)
    
    with open(supervised_path, "r") as f:
        corrective_data = json.load(f)

    profile_text = ""
    count = 0
    for key in data:
        if(count != 0 and count != 4):
            profile_text += str(key)
            if type(data[key]) is not list:
                profile_text += str(data[key])+". "
            else:
                for elem in data[key]:
                    profile_text += str(elem)
                profile_text += ". "
        count += 1
    
    image_list = []
    image_prompt_list = []
    for i in data["image_path"]:
        image_list.append(Image.open(i).convert("RGB"))
        image_prompt_list.append({"type": "image"})
        
    image_prompt_list.append({"type": "text", "text": "Her profile:"+profile_text})
    prompt = [{"role": "user", "content": image_prompt_list}]
    chosen = [{"role": "assistant", "content": [{"type": "text", "text": corrective_data["chosen"]}]}]
    rejected = [{"role": "assistant", "content": [{"type": "text", "text": corrective_data["rejected"]}]}]
    return {"prompt": prompt, "images": image_list, "chosen": chosen, "rejected": rejected}

#<------------------------------------


#Define set and run training loop ---------->
# Freeze vision encoder
for param in model.vision_model.parameters():
    param.requires_grad = False

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

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset, #TODO: Replace with actual training set, see dataset_generator
    eval_dataset=val_dataset #TODO: Replace with actual validation set
)

trainer.train()

#<--------------------------------