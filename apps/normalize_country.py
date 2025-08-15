import json
from transliterate import translit
from rapidfuzz import process, fuzz

from apps.normalize_text import clean_and_capitalize

# Fayldan shaharlar lug'atini o'qib olish
with open(r"C:\Users\Javoxir\PycharmProjects\tensor_bot\apps\regions.json", "r", encoding="utf8") as f:
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

def change_to_cyrillic(text):
    def is_latin(text):
        # Faqat lotin harflari (shu jumladan 'o‘', 'g‘') borligini tekshiradi
        import re
        return bool(re.match(r"^[A-Za-z0‘g‘G‘O‘O'G']+(.*)?$", text.replace(" ", "")))

    if not is_latin(text):
        return text  # Kirill bo‘lishi mumkin — tarjima qilinmaydi

    # Lotindan Kirillga o‘tkazuvchi funksiya
    latin_to_cyrillic = {
        "A": "А", "a": "а",
        "B": "Б", "b": "б",
        "D": "Д", "d": "д",
        "E": "Э", "e": "э",
        "F": "Ф", "f": "ф",
        "G": "Г", "g": "г",
        "H": "Ҳ", "h": "ҳ",
        "I": "И", "i": "и",
        "J": "Ж", "j": "ж",
        "K": "К", "k": "к",
        "L": "Л", "l": "л",
        "M": "М", "m": "м",
        "N": "Н", "n": "н",
        "O": "О", "o": "о",
        "P": "П", "p": "п",
        "Q": "Қ", "q": "қ",
        "R": "Р", "r": "р",
        "S": "С", "s": "с",
        "T": "Т", "t": "т",
        "U": "У", "u": "у",
        "V": "В", "v": "в",
        "X": "Х", "x": "х",
        "Y": "Й", "y": "й",
        "Z": "З", "z": "з",
        "O‘": "Ў", "o‘": "ў", "O'": "Ў", "o'": "ў",
        "G‘": "Ғ", "g‘": "ғ", "G'": "Ғ", "g'": "ғ",
        "Sh": "Ш", "sh": "ш",
        "Ch": "Ч", "ch": "ч",
        "Ya": "Я", "ya": "я",
        "Yo": "Ё", "yo": "ё",
        "Yu": "Ю", "yu": "ю",
        "Ts": "Ц", "ts": "ц",
        "’": "ъ", "'": "ь",
        ",": ",", ".": ".", "-": "-", " ": " "
    }

    # 2 harfli kombinatsiyalarni birinchi tarjima qilish
    replacements = [
        ("O‘", "Ў"), ("o‘", "ў"), ("O'", "Ў"), ("o'", "ў"),
        ("G‘", "Ғ"), ("g‘", "ғ"), ("G'", "Ғ"), ("g'", "ғ"),
        ("Sh", "Ш"), ("sh", "ш"),
        ("Ch", "Ч"), ("ch", "ч"),
        ("Ya", "Я"), ("ya", "я"),
        ("Yo", "Ё"), ("yo", "ё"),
        ("Yu", "Ю"), ("yu", "ю"),
        ("Ts", "Ц"), ("ts", "ц"),
    ]

    for latin, cyrillic in replacements:
        text = text.replace(latin, cyrillic)

    # Qolgan belgilarni tarjima qilish
    result = ""
    for char in text:
        result += latin_to_cyrillic.get(char, char)

    return result

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
                region = change_to_cyrillic(region)
                result.append(region)

    res=clean_and_capitalize(result[0])
    # res = clean_and_capitalize(", ".join(result))
    return res

# text="УЗБ ТОШКЕНТ,УЗБ ВОДИЙ"
#
# print(find_region_type(text))\

