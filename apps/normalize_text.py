import re


def clean_and_capitalize(text):
    # Harflar (lotin va kirill) + vergul + bo‘sh joylarga ruxsat
    cleaned = re.sub(r'[^a-zA-Zа-яА-ЯёЁўғқҳЎҒҚҲ,\s]', '', text)
    cleaned = cleaned.strip().lower()

    if not cleaned:
        return ''

    # Har bir vergul orqali bo‘linadi va har bir bo‘lak kapital qilinadi
    parts = [part.strip() for part in cleaned.split(',')]
    capitalized_parts = [p.capitalize() for p in parts if p]

    # Vergul bilan qayta birlashtiramiz
    return ', '.join(capitalized_parts)


# text="salom, menming ismnm"
#
# print(clean_and_capitalize(text))


