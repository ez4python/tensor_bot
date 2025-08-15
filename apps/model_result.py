import spacy

# Modelni faqat bir marta yuklaymiz
nlp = spacy.load(r"C:\Users\Javoxir\PycharmProjects\tensor_bot\output_last\model-best")

def extract_first_number(text):
    """Matndan birinchi raqam ketma-ketligini ajratish (regexsiz)"""
    if not isinstance(text, str):
        return None
    number = ''
    for char in text:
        if char.isdigit():
            number += char
        elif number:
            break
    return int(number) if number else None


def get_message(text):
    # Tahlil
    doc = nlp(text)

    required_labels = [
        "FROM", "TO", "CARGO", "WEIGHT", "PAYMENT", "ADVANCE", "VEHICLE",
        "VEHICLE_QUANTITY", "LOADING_TIME", "PHONENUMBER", "ADDITIONAL"
    ]

    datatrue = {
        "FROM": "from",
        "TO": "to",
        "CARGO": "cargoName",
        "WEIGHT": "weight",
        "PHONENUMBER": "sellerPhoneNumber",
        "ADDITIONAL": "additionalStop",
        "VEHICLE": "vehicleType",
        "VEHICLE_QUANTITY": "vehicleQuantity",
        "LOADING_TIME": "loadingTime",
        "PAYMENT": "payment",
        "ADVANCE": "advance",
    }

    collected = {label: set() for label in required_labels}

    for ent in doc.ents:
        if ent.label_ in collected:
            collected[ent.label_].add(ent.text.strip())

    result = {

        datatrue[label]: ", ".join(sorted(collected[label])) if collected[label] else None

        for label in required_labels
    }


    if result["vehicleQuantity"]:
        result["vehicleQuantity"] = extract_first_number(result["vehicleQuantity"])

    return result
# text="""
# 🇷🇺Екатеринбург - Ташкент🇺🇿
# 🚛🚛🚛Реф
# Кондитерка🍭🍬🍫
#
# Цена:⚡️⚡️
# +998993937871"""
#
# print(get_message(text))