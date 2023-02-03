from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


button_load = KeyboardButton('/Добавить_товар')
button_delete = KeyboardButton('/Удаление_товаров')
button_active_orders = KeyboardButton('/Активные_заказы')
promo_code = KeyboardButton('/Промокоды')


kb_admin = ReplyKeyboardMarkup(resize_keyboard=True).add(button_load).add(button_delete).add(button_active_orders)\
    .add(promo_code)


cancel_button = KeyboardButton('/Отмена')


kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_button)

back_button = KeyboardButton('/Назад')

kb_back = ReplyKeyboardMarkup(resize_keyboard=True).add(back_button)