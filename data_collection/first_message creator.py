import json
import os
import ollama

def data_to_prompt(data):
    return data["description"] + data["context"]

def create_first_message(data, user_id, model="mistral", output_dir="data_collection/first_messages"):
    """
    Create the first message for a user based on provided data.

    Args:
        data (dict): A dictionary containing message details.
        user_id (str): The ID of the user."""
    response = ollama.chat(model='mistral', messages=[
        {
            'role': 'user',
            'content': data_to_prompt(data)
        }
    ])
    
    
    


