import spacy
from spacy.tokens import DocBin
import json

nlp = spacy.blank("xx")  # Yoki "ru" / "xx" / "en"
doc_bin = DocBin()

with open(r"/test/truedata (1).json", "r", encoding="utf-8") as f:
    data = json.load(f)

for sample in data:
    doc = nlp.make_doc(sample["text"])
    ents = []
    for start, end, label in sample["entities"]:
        span = doc.char_span(start, end, label=label)
        if span:
            ents.append(span)
    doc.ents = ents
    doc_bin.add(doc)

doc_bin.to_disk("train2.spacy")
