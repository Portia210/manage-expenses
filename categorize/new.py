import json

# Load the JSON data
with open('../transaction_kind.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Loop through each item and add the 'confirm' key with the value 'false'
for item in data:
    data[item]['confirm'] = False

# Save the updated data back to the JSON file
with open('../transaction_kind.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Updated JSON file with 'confirm' set to False for all items.")
