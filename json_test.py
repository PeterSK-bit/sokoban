import json
with open("lvl.json", "r") as f:
    data = json.load(f)

print(data["crates"])