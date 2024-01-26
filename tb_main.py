import telebot
from telebot import types, TeleBot
from models import Database, Keyboard
from config import admin
from sheets import add_to_sheets, add_price

bot_token = "6879243634:AAGxjNZR7fmj_EhZKrrD1HVrW29bneuUvng"

bot = TeleBot(bot_token)
requests = {}
bot.set_my_commands([types.BotCommand("/start", "Начать работу"),
                    types.BotCommand("/request_doctor", "Стать доктором"),
                    types.BotCommand("/request_operator", "Стать оператором")])

@bot.message_handler(commands=['start'])
def start(message):
    print(message.chat.id)
    bot.send_message(message.chat.id, "Здравствуйте!\nНапишите Создать, чтобы сформировать заявку.\nЖдите новых заявок, если вы врач.", parse_mode="html")

@bot.message_handler(content_types="text", func=lambda message: message.text.lower() == "создать")
def animal_type(message):
    db = Database("database.db")
    role = db.get_user_role(message.chat.id)
    if role == "op":
        bot.send_message(message.chat.id, "Напишите вид животного")
        bot.register_next_step_handler(message, contacts)
    else:
        bot.send_message(message.chat.id, "У вас недостаточно прав для выполнения этого действия! Обрабитетсь к администратору.")

def contacts(message):
    requests[message.chat.id] = {}
    requests[message.chat.id]["animal_type"] = f"{message.text}"
    bot.send_message(message.chat.id, "Напишите контакты")
    bot.register_next_step_handler(message, adress)

def adress(message):
    requests[message.chat.id]["contacts"] = f"{message.text}"
    bot.send_message(message.chat.id, "Напишите адрес")
    bot.register_next_step_handler(message, description)

def description(message):
    requests[message.chat.id]["adress"] = f"{message.text}"
    bot.send_message(message.chat.id, "Напишите описание")
    bot.register_next_step_handler(message, end_request)

def end_request(message):
    db = Database("database.db")
    #тут надо записать итоговые данные заявки уже в бд
    id = db.add_request(requests[message.chat.id]["animal_type"], requests[message.chat.id]['contacts'], requests[message.chat.id]["adress"], message.text, message.chat.id)
    bot.send_message(message.chat.id, f"Заявка №{id} успешно создана! \n Вид животного:\n {requests[message.chat.id]['animal_type']}\nАдрес:\n {requests[message.chat.id]['adress']}\nОписание:\n {message.text}")
    send_requests(id, message)

def send_requests(id, message):
    db = Database("database.db")
    request = db.get_request(id)
    print(request)
    ids_list = db.get_users_by_role("doc")
    kb = types.InlineKeyboardMarkup(row_width=2)
    button_watch = types.InlineKeyboardButton("Просмотреть", callback_data=f"watch_{id}")
    kb.add(button_watch)
    message_edit = bot.send_message(message.chat.id, "Рассылаю заявки...")
    try:
        ids_list = ids_list[0]
        for id_user in ids_list:
            bot.send_message(id_user, f"Пришла новая заявка №{request['id']}\nНажмите кнопку Просмотреть, чтобы увидеть больше", reply_markup=kb)
            bot.edit_message_text(text="Заявки успешно отправлены!", chat_id=message.chat.id, message_id=message_edit.id)
    except:
        bot.edit_message_text(text="Докторов нет, заявки отправлять некому.", chat_id=message.chat.id, message_id=message_edit.id)
    

@bot.callback_query_handler(func= lambda call: "watch" in call.data)
def watch_request(call):
    request_id = call.data[call.data.find('_')+1:]
    db = Database("database.db")
    request = db.get_request(request_id)
    kb = types.InlineKeyboardMarkup(row_width=2)
    button_yes = types.InlineKeyboardButton("Принять", callback_data=f"accept_{request_id}")
    button_no = types.InlineKeyboardButton("Отказаться", callback_data=f"decline_{request_id}")
    kb.add(button_yes, button_no)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"Пришла новая заявка №{request['id']}\nВид животного:\n {request['animal_type']}\nКонтакты:{request['contacts']}\nАдрес:\n {request['adress']}\nОписание:\n {request['description']}", reply_markup=kb)
    ops = db.get_users_by_role('op')[0]
    for op in ops:
        bot.send_message(op, f"Заявка №{request_id} просматривается {call.from_user.first_name} {call.from_user.last_name}")


@bot.message_handler(commands=["request_doctor"])
def request_membership_doc(message):
    kb = types.InlineKeyboardMarkup(row_width=2)
    button_accept = types.InlineKeyboardButton("Принять доктора", callback_data=f"docaccept_{message.chat.id}")
    button_decline = types.InlineKeyboardButton("Отклонить доктора", callback_data=f"docdecline_{message.chat.id}")
    kb.add(button_accept, button_decline)
    bot.send_message(admin, f"Пришла заявка доктора на вступление от {message.from_user.first_name} {message.from_user.last_name} \n@{message.from_user.username}", reply_markup=kb)

@bot.message_handler(commands=["request_operator"])
def request_membership_op(message):
    kb = types.InlineKeyboardMarkup(row_width=2)
    button_accept = types.InlineKeyboardButton(text="Принять оператора", callback_data=f"opaccept_{message.chat.id}")
    button_decline = types.InlineKeyboardButton(text="Отклонить оператора", callback_data=f"opdecline_{message.chat.id}")
    kb.add(button_accept, button_decline)
    bot.send_message(message.chat.id, "Ваша заявка отрпавлена на модерацию, пожалуйста, ожидайте решения!")
    bot.send_message(admin, f"Пришла заявка оператора на вступление от {message.from_user.first_name} {message.from_user.last_name} \n@{message.from_user.username}", reply_markup=kb)

@bot.callback_query_handler(func= lambda call: call.data[0:2] == "op")
def op_request(call):
    if "accept" in call.data:
        db = Database("database.db")
        chat_id = call.data[call.data.find('_') + 1:]
        db.add_user(chat_id, role="op")
        kb = types.ReplyKeyboardMarkup()
        button = types.KeyboardButton(text="Поделиться телефоном", request_contact=True)
        kb.add(button)
        bot.send_message(chat_id, "Чтобы закончить оформление заявки, поделитесь телефоном, нажав на кнопку в чате.", reply_markup=kb)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Заявка оператора успешно принята!")
    elif "decline" in call.data:
        bot.send_message(call.message.chat.id, "Заявка оператора отклонена!")

@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    print(message.contact.phone_number)
    number = message.contact.phone_number
    chat_id = message.chat.id
    db = Database("database.db")
    db.add_contacts(chat_id, number, message.from_user.username)
    hideBoard = types.ReplyKeyboardRemove()
    bot.send_message(chat_id, "Ваша заявка на вступление принята!", reply_markup=hideBoard)


@bot.callback_query_handler(func= lambda call: call.data[0:3] == "doc")
def doc_request(call):
    if "accept" in call.data:
        db = Database("database.db")
        chat_id = call.data[call.data.find('_') + 1:]
        print(chat_id)
        stat = db.add_user(chat_id, role="doc")
        kb = types.ReplyKeyboardMarkup()
        button = types.KeyboardButton(text="Поделиться телефоном", request_contact=True)
        kb.add(button)
        if stat == "success":
            bot.send_message(chat_id, "Чтобы закончить оформление заявки, поделитесь телефоном, нажав на кнопку в чате.", reply_markup=kb)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Заявка доктора успешно принята!")
        else:
            bot.send_message(chat_id, "Ваша заявка отклонена, вы уже зарегистрированы")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Заявка доктора отменена, пользователь уже имеет роль.")
    elif "decline" in call.data:
        bot.send_message(call.message.chat.id, "Заявка доктора отклонена!")

@bot.callback_query_handler(func= lambda call: call.data[0:6] == "accept")
def accept_request(call):
    db = Database("database.db")
    request_id = call.data[call.data.find('_') + 1:]
    if not db.is_accepted(request_id):
        db.set_doc_on_request(request_id, call.message.chat.id)
        request = db.get_request(request_id)
        kb = types.InlineKeyboardMarkup()
        button_close = types.InlineKeyboardButton("Закрыть заявку", callback_data=f"close_{request_id}")
        kb.add(button_close)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id ,text=f"Заявка №{request_id} принята вами! \n {request}", reply_markup=kb)
        excel_num = add_to_sheets([request["id"], request["open_date"], '', request["op_id"], request["doc_id"]])
        db.set_excel_num(request_id, excel_num)
        for chat_id in db.get_users_by_role("op")[0]:
            bot.send_message(chat_id, f"{call.from_user.first_name} {call.from_user.last_name} принял заявку №{request_id}!")
    else:
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, f"Заявка №{request_id} уже принята другим пользователем! Ожидайте другие заявки.")

@bot.callback_query_handler(func= lambda call: call.data[0:7] == "decline")
def decline_request(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)

@bot.callback_query_handler(func= lambda call: call.data[0:5] == "close")
def close_request(call):
    bot.send_message(call.message.chat.id, "Введите сумму закрытия")
    bot.delete_message(call.message.chat.id, call.message.id)
    request_id = call.data[call.data.find("_") + 1:]
    bot.register_next_step_handler(call.message, final_close, request_id)

def final_close(message, request_id):
    db = Database("database.db")
    db.set_close_date_on_request(request_id)
    request_info = db.get_request(request_id)
    print(request_info)
    for chat_id in db.get_users_by_role("op")[0]:
        bot.send_message(chat_id, f"{message.from_user.first_name} {message.from_user.last_name} закрыл заявку №{request_info['id']}!")
    bot.send_message(message.chat.id, "Вы закрыли заявку, поздравляем!")
    contacts_op = db.get_contacts(request_info["op_id"])["username"] if not None else db.get_contacts(request_info["op_id"])["phone"]
    contacts_doc = db.get_contacts(request_info["doc_id"])["username"] if not None else db.get_contacts(request_info["doc_id"])["phone"]
    add_to_sheets([request_info["id"], request_info["open_date"], request_info["close_date"], f"@{contacts_op}", f"@{contacts_doc}", message.text], int(request_info["excel_num"]))

bot.polling(non_stop=True)
