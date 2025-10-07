import json
from PIL import Image

def to_conversational(input_path, supervised_path):
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
        if(count != 0 or 4):
            profile_text += str(key)
            if type(key) is not list:
                profile_text += str(data[key])+". "
            else:
                for elem in data[key]:
                    profile_text += str(elem)
                profile_text += ". "
        count += 1
    
    image_list = []
    image_prompt_list = []
    for i in input_path:
        image_list.append(Image.open(i).convert("RGB"))
        image_prompt_list.append({"type": "image"})
        
    image_prompt_list.append({"type": "text", "text": "Her profile:"+profile_text})
    prompt = [{"role": "user", "content": image_prompt_list}]
    chosen = [{"role": "assistant", "content": [{"type": "text", "text": corrective_data["chosen"]}]}]
    rejected = [{"role": "assistant", "content": [{"type": "text", "text": corrective_data["rejected"]}]}]
    return {"prompt": prompt, "images": image_list, "chosen": chosen, "rejected": rejected}

