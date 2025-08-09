import json

with open("../data/test.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for idx, item in enumerate(data):
    text = item["text"]
    for ent in item["entities"]:
        start, end, label = ent
        entity_text = text[start:end]
        print(f"[{idx}] {label}: '{entity_text}' ({start}-{end})")
        if entity_text.strip() == "":
            print(f"⚠ Bo'sh entity matn: {start}-{end} in text: {text}")
        if start >= len(text) or end > len(text):
            print(f"❌ Xato koordinata: {start}-{end} text uzunligi {len(text)}")