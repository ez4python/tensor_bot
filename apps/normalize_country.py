import json
from transliterate import translit
from rapidfuzz import process, fuzz

from apps.normalize_text import clean_and_capitalize

# Fayldan shaharlar lug'atini o'qib olish
with open(r"C:\Users\User\PycharmProjects\Logistika\apps\regions.json", "r", encoding="utf8") as f:
    city_to_region = json.load(f)

# Barcha variantlarni normalize qilib, lug'atni tayyorlab qo'yamiz
all_variants = {}
for standard_name, variants in city_to_region.items():
    for v in variants:
        try:
            normalized_v = translit(v.strip().lower(), 'ru')  # Latin -> Cyrillic
        except Exception:
            normalized_v = v.strip().lower()
        all_variants[normalized_v] = standard_name


# Foydalanuvchi inputini normalize qiluvchi funksiya
def normalize(text: str) -> str:
    text = text.strip().lower()
    # Faqat lotin harfligina translit qilinadi
    if all('a' <= ch <= 'z' for ch in text if ch.isalpha()):
        try:
            text = translit(text, 'ru')
        except Exception:
            pass
    return text

def remove_suffix(word: str) -> str:
    suffixes = ['dan', 'ga', 'tan', 'ka', 'sha', 'gan','дан', 'га', 'тан', 'ка', 'ша', 'ган']
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 1:
            return word[: -len(suffix)]
    return word

# Topilgan shahar bo‘yicha standart regionni qaytaruvchi funksiya
def find_region_type(user_input: str) -> str:
    result = []

    regions = user_input.split(',')

    regions = regions[0].split(' ')

    for region in regions:
        region = region.strip()

        if region != "НАЛИЧНЫЙ💵":
            region = remove_suffix(region)
            query = normalize(region)

            match, score, _ = process.extractOne(query, all_variants.keys(), scorer=fuzz.ratio)

            if score >= 80:
                return all_variants[match]
            else:
                result.append(region)

    res=clean_and_capitalize(result[0])
    # res = clean_and_capitalize(", ".join(result))
    return res

# text="УЗБ ТОШКЕНТ,УЗБ ВОДИЙ"
#
# print(find_region_type(text))