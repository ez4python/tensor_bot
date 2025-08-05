import re

def split_by_phone_line(text):
    """Telefon raqam chiqqan QATORdan KEYIN bo‘lish (har xil ko‘rinishlarga moslangan)"""
    lines = text.splitlines(keepends=True)
    blocks = []
    buffer = []

    # Keng qamrovli telefon raqami andozasi (maxsus belgilar: +, 998, boshida nolli yoki YO‘Q)
    phone_pattern = re.compile(r'(?:\+?\d{1,3})?\d{7,12}')

    for line in lines:
        buffer.append(line)
        if phone_pattern.search(line):
            blocks.append(''.join(buffer))
            buffer = []

    if buffer:
        blocks.append(''.join(buffer))
    return blocks


def split_by_symbols(text):
    """Ko‘p belgilar ketma-ket kelgan joydan ajratish"""
    pattern = re.compile(r'([^\w\s])\1{2,}')  # ❗️❗️❗️ yoki 🔥🔥🔥🔥
    matches = list(pattern.finditer(text))
    if not matches:
        return [text]

    blocks = []
    last_index = 0
    for match in matches:
        end = match.end()
        blocks.append(text[last_index:end])
        last_index = end
    if last_index < len(text):
        blocks.append(text[last_index:])
    return [b for b in blocks if b.strip()]


def split_by_max_and_one_less(text):
    """Faqat eng katta va undan 1 kam bo‘lgan bo‘sh qatorlar bilan ajratadi"""
    # Barcha bo‘sh qator segmentlarini topish
    all_empty_matches = list(re.finditer(r'(\n\s*\n+)', text))

    if not all_empty_matches:
        return [text.strip()]

    # Har bir topilgan bo‘shlik uzunligini o‘lchaymiz
    lengths = [len(match.group(1)) for match in all_empty_matches]
    max_len = max(lengths)
    allowed_lengths = {max_len, max_len - 1}

    # Har bir bo‘sh qator segmentining boshlanish pozitsiyasi va uzunligini olamiz
    split_positions = [m.span() for m in all_empty_matches if len(m.group(1)) in allowed_lengths]

    # Bo‘lish
    segments = []
    last_index = 0
    for start, end in split_positions:
        segment = text[last_index:start].strip()
        if segment:
            segments.append(segment)
        last_index = end

    # Oxirgi qismni ham qo‘shamiz
    final_segment = text[last_index:].strip()
    if final_segment:
        segments.append(final_segment)

    return segments

def smart_split_blocks(text):
    # 1. Telefon raqami orqali ajrat
    blocks = split_by_phone_line(text)

    if len(blocks) >= 2 and (len(blocks[0]) < len(blocks[1])*2):
                return blocks
    else:
        # 2. Belgilar orqali ajrat
        blocks = split_by_symbols(text)
        if  len(blocks) >= 2 and (len(blocks[0]) < len(blocks[1])*2):
            return blocks
        else:
            # 3. 2 va undan ortiq bo‘sh qatordan ajrat
            blocks = split_by_max_and_one_less(text)
            return blocks

