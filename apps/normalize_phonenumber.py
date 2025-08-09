import re

def normalize_phone_number_list(input_str: str | None) -> str | None:
    if input_str is None:
        return None

    input_str = input_str.strip()
    if not input_str:
        return None

    normalized_numbers = []

    for raw_number in input_str.split(","):
        raw_number = raw_number.strip()
        if not raw_number:
            continue

        # Belgilarni tozalash (qavs, bo‘sh joy, tirelar)
        cleaned = re.sub(r"[ \-\(\)]", "", raw_number)
        digits = re.sub(r"[^\d]", "", cleaned)

        normalized = None

        # 1. Agar allaqachon + bilan boshlansa, faqat raqamlarni olamiz
        if cleaned.startswith("+"):
            digits = digits  # already cleaned from above
        # 2. 0 bilan boshlangan (O‘zbekiston ichki format) ➜ +998
        elif len(digits) == 10 and digits.startswith("0"):
            digits = "998" + digits[1:]
        # 3. 9 xonali (Uzbek format) ➜ +998 qo‘shamiz
        elif len(digits) == 9:
            digits = "998" + digits
        # 4. Agar 998 bilan boshlansa lekin + yo‘q bo‘lsa ➜ +998
        elif digits.startswith("998") and len(digits) == 12:
            pass  # ok
        # 5. Agar 7 yoki 77 bilan boshlansa ➜ Rossiya/Qozog‘iston
        elif digits.startswith("7") and len(digits) == 11:
            pass  # Russia
        elif digits.startswith("77") and len(digits) == 11:
            pass  # Kazakhstan
        else:
            return None  # ❌ noto‘g‘ri raqam yoki boshqa davlat

        # 6. Raqam uzunligini tekshiramiz (998 bilan: 12, 7/77 bilan: 11)
        if digits.startswith("998") and len(digits) != 12:
            return None
        elif digits.startswith("7") and len(digits) != 11:
            return None
        elif digits.startswith("77") and len(digits) != 11:
            return None
        if len(digits) ==0:
            return None
        else:
            normalized = "+" + digits
        normalized_numbers.append(normalized)

    return ",".join(normalized_numbers) if normalized_numbers else None



