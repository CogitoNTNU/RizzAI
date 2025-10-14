import json
#This file is to concatenate two json files into one json file, without duplicates
#load the json files

def get_last_id(current_file):
    with open(current_file, "r") as f:
        data = json.load(f)
    last_id = 0
    keys = list(data.keys())
    return int(keys[-1]) if keys else 0

print(get_last_id("data_collection/profiles/text_data.json"))
