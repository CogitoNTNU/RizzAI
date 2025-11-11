import os
import json
from pathlib import Path

#To merge your data without making copies of the data, store it in a folder structured the same way as the original data. (profiles)
# Then change the last line of this script to iterate over relevant ids in the person2 folder.


def get_last_id() -> int:
    path = Path('data_collection/profiles/text_data.json')
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return list(data.keys())[-1]

print(get_last_id())



def check_if_same_dict(dict1, dict2):
    if dict1["name"]==dict2["name"]:
        print("names are the same")
        print(dict1.keys(),dict2.keys())
        if dict1.keys()==dict2.keys():
            print(list(dict1.values()), list(dict2.values()))
            if list(dict1.values())==list(dict2.values()):
                return True
    return False

def merge_data_without_copies(origin_id:int):
    with open('data_collection/profiles/text_data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    with open('data_collection/profiles2/text_data.json', 'r', encoding='utf-8') as file:
        data2 = json.load(file)
        data_to_merge = data2.get(str(origin_id))
    last_id = get_last_id()
    j=int(last_id)+1
    i=0 
    is_already_there=False
    while i < len(data):
        if check_if_same_dict(data_to_merge, data.get(str(i))):
            print("Data, already exists as id:", i)
            return False
        else:
            i+=1


    if not is_already_there:
        #move associated images from profiles2/images to profiles/images and rename them to match new id
        src_folder = Path(f'data_collection/profiles2/images/{origin_id}')
        dest_folder = Path(f'data_collection/profiles/images/{j}')
            
    if src_folder.exists():
        os.rename(src_folder, dest_folder)
    data[str(j)] = data_to_merge
    with open('data_collection/profiles/text_data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        print(f'Merged data with new ID: {j}')
    return True

profiles_merged=0
fails=0
for i in range(1,11):
    a=merge_data_without_copies(i)
    if a:
        profiles_merged+=1
    else:fails+=1

print("Successfully merged",profiles_merged,"profiles.")
print("Failed to merge", fails,"profiles.")


