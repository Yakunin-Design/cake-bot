from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import datetime


# Кнопки меню
catalog_button = KeyboardButton('/Каталог')
basket_button = KeyboardButton('/Корзина')
orders_button = KeyboardButton('/Мои_заказы')
callback_button = KeyboardButton('/Обратная_связь')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.add(catalog_button).add(basket_button).add(orders_button).add(callback_button)


# Кнопки отмены
cancel_button = KeyboardButton('/Отмена_заказа')

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_cancel.add(cancel_button)


# Выбор даты
def get_dates():
    now_date = datetime.date.today()
    dates = []
    kb_dates = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    for i in range(2, 16, 3):
        dates.append((now_date + datetime.timedelta(i - 2)).strftime('%d-%m-%Y'))
        dates.append((now_date + datetime.timedelta(i - 1)).strftime('%d-%m-%Y'))
        dates.append((now_date + datetime.timedelta(i)).strftime('%d-%m-%Y'))

        kb_dates.add(KeyboardButton(str(dates[i - 2])), KeyboardButton(str(dates[i - 1])),
                     KeyboardButton(str(dates[i])))

    kb_dates.add(cancel_button)
    return kb_dates


# Выбор времени
def get_time_button(order_date):
    today = datetime.datetime.today()
    time1 = datetime.time(11, 00)
    time2 = datetime.time(13, 00)
    time3 = datetime.time(15, 00)
    time4 = datetime.time(17, 00)
    time5 = datetime.time(19, 00)

    time_button_1 = KeyboardButton('11:00 - 13:00')
    time_button_2 = KeyboardButton('13:00 - 15:00')
    time_button_3 = KeyboardButton('15:00 - 17:00')
    time_button_4 = KeyboardButton('17:00 - 19:00')
    time_button_5 = KeyboardButton('19:00 - 21:00')

    times = [time1, time2, time3, time4, time5]
    time_buttons = [time_button_1, time_button_2, time_button_3, time_button_4, time_button_5]
    kb_times = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if order_date == today.date().strftime('%d-%m-%Y'):
        for i in range(len(times)):
            if times[i] > today.time():
                kb_times.add(time_buttons[i])
    else:
        for i in range(5):
            kb_times.add(time_buttons[i])
    kb_times.add(cancel_button)
    return kb_times


# Получение контакта
contact_button = KeyboardButton('Использовать номер из Telegram', request_contact=True)

kb_contact = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_contact.add(contact_button).add(cancel_button)


# Возврат в меню
back_button = KeyboardButton('/Вернуться_в_меню')

kb_back = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(back_button)


# Возврат в корзину
back_basket_button = KeyboardButton('/Вернуться_в_корзину')

kb_back_basket = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(back_basket_button)\
    .add(back_button)


# Переход в корзину из каталога
kb_catalog_back = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(back_button).add(basket_button)


# Пропустить ввод промокода
next_button = KeyboardButton('Продолжить без промокода')

kb_promo = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(back_button).add(next_button)
