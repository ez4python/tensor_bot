def funcsion(text,entity_pairs):
    entities=[]
    for value,label in entity_pairs.items():
        print(label)
        start= text.find(label)
        if start !=-1:
            end=start +len(label)
            entities.append((start,end,value))
        else:
            print("value not found")
    return {"text": text, "entities": entities}


text="""Sirdaryo - G'ijduvon 
25tonna 
Tent fura 
330631013
331421013"""

entity_pairs={'FROM':'Sirdaryo','TO':"G'ijduvon"}

converted = funcsion(text,entity_pairs)
print(converted)

