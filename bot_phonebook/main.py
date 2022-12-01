import telebot
from telebot import types
import os
import model
from dotenv import load_dotenv

load_dotenv()
secret_token = os.getenv('TOKEN')

bot = telebot.TeleBot(secret_token)

def menu(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Показать справочник", callback_data='print_table')
    btn2 = types.InlineKeyboardButton(text="Добавить запись", callback_data='start_add_record')
    btn3 = types.InlineKeyboardButton(text="Найти", callback_data='find')
    btn4 = types.InlineKeyboardButton(text="Удалить", callback_data='start_delete_record')
    btn5 = types.InlineKeyboardButton(text="Изменить запись", callback_data='start_change_record')
    btn6 = types.InlineKeyboardButton(text="Экспорт XML", callback_data='export_xml')
    btn7 = types.InlineKeyboardButton(text="Импорт XML", callback_data='import_xml')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    bot.send_message(message.chat.id, text='Выберите действие', reply_markup=markup)

def start_import_xml(message):
    bot.send_message(message.chat.id, text="Вставьте текст справочника в формате xml")
    bot.register_next_step_handler(message, import_xml)

def import_xml(message):
    text_message = message.text

    pd = model.Phonebook()
    pd.import_text(text_message)
    menu(message)

def export_xml(message):
    pb = model.Phonebook()
    text = pb.export_text()
    bot.send_message(message.chat.id, text=text)
    menu(message)

def start_delete_record(message):
    bot.send_message(message.chat.id, text='Укажите номер строки')
    bot.register_next_step_handler(message, delete_record)

def delete_record(message):
    text_message = message.text

    if text_message == "/cancel":
        menu(message)
        return

    num = None
    try:
        num = int(text_message)
    except Exception as e:
        bot.send_message(message.chat.id, text='Введено не число')
        menu(message)
        return
    pb = model.Phonebook()
    try:
        record = pb[num - 1]
        del pb[num - 1]
        pb.dump()
        bot.send_message(message.chat.id, text=f"Запись удалена: Имя: {record.name}; Телефон: {record.telephone};  Комментарий: {record.comment}")
    except Exception as e:
        bot.send_message(message.chat.id, text=str(e))
    menu(message)

def start_change_record(message):
    bot.send_message(message.chat.id, text='Укажите номер строки')
    bot.register_next_step_handler(message, change_record)

def change_record(message, *args, **kwargs):
    text_message = message.text

    if text_message == "/cancel":
        menu(message)
        return

    num = None
    try:
        num = int(text_message)
    except Exception as e:
        bot.send_message(message.chat.id, text='Введено не число')
        menu(message)
        return
    pb = model.Phonebook()
    record = None
    text = ""
    try:
        record = pb[num - 1]
        text = f"Запись: Имя: {record.name}; Телефон: {record.telephone};  Комментарий: {record.comment}"
    except Exception as e:
        bot.send_message(message.chat.id, text=str(e))
        menu(message)
        return

    btn1 = types.InlineKeyboardButton(text="Изменить имя", callback_data=f'change_name_{num}')
    btn2 = types.InlineKeyboardButton(text="Изменить телефон", callback_data=f'change_phone_{num}')
    btn3 = types.InlineKeyboardButton(text="Изменить комментарий", callback_data=f'change_comment_{num}')

    markup = types.InlineKeyboardMarkup()
    markup.add(btn1, btn2, btn3,)
    bot.send_message(message.chat.id, text, reply_markup=markup)

def change_record_name(message, num_record):
    bot.send_message(message.chat.id, "Укажите имя")
    bot.register_next_step_handler(message, change_record_pole, num_record, "name")

def change_record_phone(message, num_record):
    bot.send_message(message.chat.id, "Укажите телефон")
    bot.register_next_step_handler(message, change_record_pole, num_record, "telephone")

def change_record_comment(message, num_record):
    bot.send_message(message.chat.id, "Укажите комментарий")
    bot.register_next_step_handler(message, change_record_pole, num_record, "comment")

def change_record_pole(message, num_record, pole):
    text_message = message.text
    if text_message == "/cancel":
        menu(message)
        return
    pb = model.Phonebook()
    try:
        record = pb[num_record - 1]
        setattr(record, pole, text_message)
        pb.dump()
        bot.send_message(message.chat.id, "Запись изменена")
    except:
        bot.send_message(message.chat.id, "Возникла ошибка. Запись не изменена")
        menu(message)
        return
    menu(message)

def start_find(message):
    bot.send_message(message.chat.id, "Введите строку поиска: ")
    bot.register_next_step_handler(message, find)

def find(message):
    text_find = message.text.lower()

    pb = model.Phonebook()
    records = pb.get_records()

    text = ""

    for index, record in enumerate(records):

        if record.name.lower() != text_find and record.comment.lower() != text_find and record.telephone != text_find:
            continue

        text += f"Запись {index + 1} \n"
        text += f"Имя: {record.name} \n"
        text += f"Телефон: {record.telephone} \n"
        text += f"Комментарий: {record.comment} \n"
        text += '\n'

    if len(text) == 0:
        text = 'Записи не найдены'

    bot.send_message(message.chat.id, text)
    menu(message)

def print_table(message):
    pb = model.Phonebook()
    text = str(pb)
    bot.send_message(message.chat.id, text)
    menu(message)

def start_add_record(message):
    input_record_data(message)

def add_record(message, *args, **kwargs):
    name = kwargs.get('name', '')
    phone = kwargs.get('phone', '')
    comment = kwargs.get('comment', '')

    record = model.Record(name, phone, comment)

    pb = model.Phonebook()
    pb.add_record(record)
    pb.dump()

    bot.send_message(message.chat.id, f'Добавлена запись: Имя: {name}; Телефон: {phone}; Комментарий: {comment}')
    menu(message)

def input_record_data(message, *args, **kwargs):
    field_message = kwargs.get("field_message", None)
    message_text = message.text
    if message_text.lower() == "/cancel":
        menu(message)
        return
    if field_message is not None:
        kwargs[field_message] = message_text
    name = kwargs.get("name", None)
    if name is None:
        msg = bot.send_message(message.chat.id, "Введите имя")
        kwargs["field_message"] = "name"
        bot.register_next_step_handler(msg, input_record_data, *args, **kwargs)
        return
    phone = kwargs.get("phone", None)
    if phone is None:
        msg = bot.send_message(message.chat.id, "Введите телефон")
        kwargs["field_message"] = "phone"
        bot.register_next_step_handler(msg, input_record_data, *args, **kwargs)
        return
    comment = kwargs.get("comment", None)
    if comment is None:
        msg = bot.send_message(message.chat.id, "Введите комментарий")
        kwargs["field_message"] = "comment"
        bot.register_next_step_handler(msg, input_record_data, *args, **kwargs)
        return

    add_record(message, **kwargs)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    try:
        if call.data == "print_table":
            print_table(call.message)
        elif call.data == "start_add_record":
            start_add_record(call.message)
        elif call.data == "find":
            start_find(call.message)
        elif call.data == "menu":
             menu(call.message)
        elif call.data == "start_delete_record":
            start_delete_record(call.message)
        elif call.data == "start_change_record":
            start_change_record(call.message)
        elif call.data == "export_xml":
            export_xml(call.message)
        elif call.data == "import_xml":
            start_import_xml(call.message)
        elif call.data.startswith("change_name"):
            lst = call.data.split("_")
            param = None
            if len(lst) > 2:
                param = int(lst[2])
            change_record_name(call.message, param)
        elif call.data.startswith("change_phone"):
            lst = call.data.split("_")
            param = None
            if len(lst) > 2:
                param = int(lst[2])
            change_record_phone(call.message, param)
        elif call.data.startswith("change_comment"):
            lst = call.data.split("_")
            param = None
            if len(lst) > 2:
                param = int(lst[2])
            change_record_comment(call.message, param)
    except Exception:
        bot.send_message(call.message, "Произошла ошибка")

@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.text == '/menu' or message.text == "/start":
         menu(message)

bot.polling(none_stop=True)
