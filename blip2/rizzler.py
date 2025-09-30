# Bye bye 🤫🤫
# 🖖
# AI, Machinelearning, DeepLearning, ComputerVision, NLP
# BLIP-2, Rizzler, Rizz, Flirting, ChatGPT, GPT-4, LLM
from transformers import (
    Blip2VisionConfig,
    Blip2QFormerConfig,
    OPTConfig,
    Blip2Config,
    Blip2ForConditionalGeneration,
)

# Initializing a Blip2Config with Salesforce/blip2-opt-2.7b style configuration
configuration = Blip2Config()

# Initializing a Blip2ForConditionalGeneration (with random weights) from the Salesforce/blip2-opt-2.7b style configuration
model = Blip2ForConditionalGeneration(configuration)

# Accessing the model configuration
configuration = model.config

# We can also initialize a Blip2Config from a Blip2VisionConfig, Blip2QFormerConfig and any PretrainedConfig

# Initializing BLIP-2 vision, BLIP-2 Q-Former and language model configurations


vision_config = Blip2VisionConfig() #Image encoder Keep this 

qformer_config = Blip2QFormerConfig(hidden_size=700, 
                                    num_hidden_layers=10, 
                                    num_attention_heads=10,
                                    ) #This we want to improve and change

text_config = OPTConfig() #Language model - Keep this


config = Blip2Config.from_text_vision_configs(vision_config, qformer_config, text_config)