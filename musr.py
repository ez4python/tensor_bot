text1="""Гулистондан - Наманганга 
Нужен тент площадка срочно
889260200"""

text2="""Гулистондан - Наманганга 
Нужен тент площадка срочно
889260200"""

text3="""
🇷🇺 КИРОВ МУРАШИ
🇺🇿 УЗБ ТОШКЕНТ
ГРУЗ: ДСП МДФ
🚛 ТЕНТ-ФУРА
ОПЛАТА НАЛ
+998917503699
"""

text_list=[text1,text2,text3]

from  bot.forward import get_message_hash,process_message_time



for i in text_list:

    if process_message_time(i):
        print("bir")

    else:
        print("ikki")





