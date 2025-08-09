import json
from transliterate import translit
from rapidfuzz import process, fuzz

from apps.normalize_text import clean_and_capitalize


# --- TRANSLIT normalization ---
def normalize(text: str) -> str:
    text = text.strip().lower()
    try:
        text = translit(text, 'ru')  # Lotindan kirillga o‘tkazish
    except Exception:
        pass
    return text

# --- Truck variants ---
TRUCK_MATCHES = {
    "Грузовик": ["truck", "грузовик", "gruz", "gruzik", "грузик"],
    "Микроавтобус": ["mikro", "microbus", "микро", "микрик", "mikrik"],
    "Рефрижератор": ["рефрижератор", "РЕФ-ФУРА", "РЕФРИЖЕРАТОР", "реф", "реф+изотерм", "РЕФ", "ref", "REF", "refr", "рефка", "рефр", "рефр", "рэф", "рефка"],
    "Тентованный грузовик": ["тент", "ТЕНТ", "tent", "TENT", "тен", "тенк", "Тенты", "REF FURA", "ТЕНТ СТАНДАРТ", "tentovka", "тэнт", "тентованный", "тентка"],
    "Фура": ["фура", "ФУРА", "fura", "FURA", "furaa", "ТЕНТ-ФУРА", "фураг", "фуура", "пура", "фыра", "fuura"],
    "Исузу": ["исузу", "ИСУЗУ", "isuzu", "ISUZU", "ису", "исузы", "исззу", "исуз", "isusu", "исуза"],
    "Газель": ["газель", "ГАЗЕЛЬ", "gazel", "GAZEL", "gazelle", "gazil", "гзл", "гзель"],
    "Ман": ["ман", "МАН", "MAN", "maan", "мэн", "мн", "mna"],
    "Камаз": ["камаз", "КАМАЗ", "kamaz", "камз", "камас", "камазик"],
    "ДАФ": ["даф", "ДАФ", "daf", "дафф", "дафка"],
    "Вольво": ["вольво", "ВОЛЬВО", "volvo", "волво", "вольва", "вальво"],
    "Ивеко": ["ивеко", "ИВЕКО", "iveco", "ивка", "ивекко"],
    "Скания": ["скания", "СКАНИЯ", "scania", "сканея", "скан", "scannia"],
    "Самосвал": ["sam", "самосвал", "сам", "самик"],
}

# --- Oldindan normalize qilingan variantlar ---
ALL_VARIANTS = {
    normalize(alias): name
    for name, aliases in TRUCK_MATCHES.items()
    for alias in aliases
}


# --- Optimallashtirilgan truck aniqlash funksiyasi ---
def find_truck_type(user_input: str) -> list[str]:
    truck = []

    for part in user_input.split(','):
        query = normalize(part)

        match, score, _ = process.extractOne(query, ALL_VARIANTS.keys(), scorer=fuzz.ratio)

        if score >= 80:
            truck.append(ALL_VARIANTS[match])
        else:
            truck.append(part.strip())  # Aniqlanmagan holatda o'zini qaytaramiz

    res=clean_and_capitalize(truck[0])
    return res


