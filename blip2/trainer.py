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