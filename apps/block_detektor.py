import spacy

nlp = spacy.load(r"/media/tensor/Windows/Users/User/PycharmProjects/Logistika/apps/single_multiple_classifier")

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
