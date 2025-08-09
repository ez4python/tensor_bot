import concurrent.futures  # ThreadPoolExecutor uchun
from apps.block_detektor import detector_block
from apps.model_result import get_message
from apps.normalize_country import find_region_type
from apps.normalize_phonenumber import normalize_phone_number_list
from apps.normalize_text import clean_and_capitalize
from apps.normalize_truck import find_truck_type
from apps.separateblock import smart_split_blocks


def chek_data(text):


    if text.get('from') and text.get('to') and text.get('sellerPhoneNumber'):

        from_country = text['from'].split(',')
        to_country = text['to'].split(',')
        if len(to_country)>=1 :
            to_country=to_country[:2]
            text['to'] = ",".join(to_country)

        if len(from_country)>=1 :
            from_country=from_country[:2]
            text['from']=",".join(from_country)


        return text
    return None


def cargo_name_normalize(text):
    if not text:
        return None

    text_list = text.split(",")
    cleaned = []

    for item in text_list:
        item = item.strip()
        if item and item.upper() != "АЛОКА УЧУН":
            cleaned_item = clean_and_capitalize(item)
            cleaned.append(cleaned_item)

    # Dublikatlarni tartibni saqlagan holda olib tashlash
    unique_cleaned = list(dict.fromkeys(cleaned))

    return ", ".join(unique_cleaned)


def process_block(block, user, msg_id, username):
    blok_data = get_message(block)
    blok_data=chek_data(blok_data)
    if not blok_data:
        return None

    blok_data["text"] = block
    blok_data["sellerName"] = user
    blok_data["from"] = find_region_type(blok_data["from"])
    blok_data["to"] = find_region_type(blok_data["to"])
    blok_data["fromLatin"] = change_language(blok_data["from"])
    blok_data["toLatin"] = change_language(blok_data["to"])
    blok_data["sellerPhoneNumber"] = normalize_phone_number_list(blok_data["sellerPhoneNumber"])
    blok_data["tg_username"] = username # f"https://t.me/{username}"
    blok_data["cargoName"]=cargo_name_normalize(blok_data["cargoName"])
    blok_data["cargoNameLatin"] = change_language(blok_data["cargoName"])
    blok_data['weight'] = normalize(blok_data["weight"])
    if blok_data.get("vehicleType"):
        blok_data["vehicleType"] = find_truck_type(blok_data["vehicleType"])
        blok_data["vehicleTypeLatin"] = change_language(blok_data["vehicleType"])
    blok_data["messageId"] = msg_id
    return blok_data


def ordered_message(text, user, msg_id, username):
    data_type = detector_block(text)

    result =[]

    if data_type == "SINGLE":
        res = get_message(text)
        res=chek_data(res)
        if not res:
            return None
        elif res:
            res["sellerName"] = user
            res["text"] = text
            res["from"] = find_region_type(res["from"])
            res["to"] = find_region_type(res["to"])
            res["fromLatin"] = change_language(res["from"])
            res["toLatin"] = change_language(res["to"])
            res["cargoName"] = cargo_name_normalize(res["cargoName"])
            res["cargoNameLatin"]=change_language(res["cargoName"])
            res["sellerPhoneNumber"] = normalize_phone_number_list(res["sellerPhoneNumber"])
            res['weight']=normalize(res["weight"])
            if res.get("vehicleType"):
                res["vehicleType"] = find_truck_type(res["vehicleType"])
                res["vehicleTypeLatin"] = change_language(res["vehicleType"])
            res["messageId"] = msg_id
            res["tg_username"] = username # f"https://t.me/{username}"
            result.append(res)
    else:
        blocks = smart_split_blocks(text)

        with concurrent.futures.ThreadPoolExecutor() as executor:

            futures = [executor.submit(process_block, block, user, msg_id, username) for block in blocks]

            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    result.append(res)

    return result


def normalize(text):
    text=text.split(',')
    return text[0]

def change_language(data):
    rus_to_latin = {
        'А': 'A', 'а': 'a',
        'Б': 'B', 'б': 'b',
        'В': 'V', 'в': 'v',
        'Г': 'G', 'г': 'g',
        'Д': 'D', 'д': 'd',
        'Е': 'E', 'е': 'e',
        'Ё': 'Yo', 'ё': 'yo',
        'Ж': 'J', 'ж': 'j',
        'З': 'Z', 'з': 'z',
        'И': 'I', 'и': 'i',
        'Й': 'Y', 'й': 'y',
        'К': 'K', 'к': 'k',
        'Л': 'L', 'л': 'l',
        'М': 'M', 'м': 'm',
        'Н': 'N', 'н': 'n',
        'О': 'O', 'о': 'o',
        'П': 'P', 'п': 'p',
        'Р': 'R', 'р': 'r',
        'С': 'S', 'с': 's',
        'Т': 'T', 'т': 't',
        'У': 'U', 'у': 'u',
        'Ф': 'F', 'ф': 'f',
        'Х': 'X', 'х': 'x',
        'Ц': 'Ts', 'ц': 'ts',
        'Ч': 'Ch', 'ч': 'ch',
        'Ш': 'Sh', 'ш': 'sh',
        'Щ': 'Sh', 'щ': 'sh',
        'Ъ': '', 'ъ': '',
        'Ы': 'I', 'ы': 'i',
        'Ь': '', 'ь': '',
        'Э': 'E', 'э': 'e',
        'Ю': 'Yu', 'ю': 'yu',
        'Я': 'Ya', 'я': 'ya',
        ',':',','.':'.','-':'-',
        ' ':' '
    }
    change_data = ""
    for x in data:
        if x in rus_to_latin:
            change_data += rus_to_latin.get(x, x)

    return change_data






# text="""
#
#
# 🇷🇺Орск,Tashkent
# 🇹🇯Душанбе
# груз битум
# через хучанд
# аванс эст
# tent,ref
# лубой авто 5машина"""
#
#
# print(ordered_message(text, "javoxir", "999","user"))

