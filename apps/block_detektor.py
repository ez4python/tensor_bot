import spacy

nlp = spacy.load(r"C:\Users\Javoxir\PycharmProjects\tensor_bot\apps\single_multiple_classifier")

def detector_block(text):
    doc = nlp(text)

    return max(doc.cats, key=doc.cats.get)

# text = """🔥🔥🔥🔥🔥🔥🔥🔥
#
#
# 🇰🇬 BISHKEK 📤
#
#
# 🇹🇷 MERSIN  📥
#
#
# 📦 NAPITKA
#
#
# ⚖ 20 TONNA
#
#
# 🚚  TENT
#
#
# 💸 👍👍👍
#
#
# ☎️ +998934542976
# ☎️+998334717017"""
#
# print(detector_block(text))
