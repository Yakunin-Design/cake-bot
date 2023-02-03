from aiogram import types, Dispatcher
from create_bot import bot
from keybords import client_kb
from data_base import sqlite_db, basket_bd, orders_bd, promo_codes_bd
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from create_bot import Admin_ID

hello_text = 'Вы написали боту по продаже тортиков.\nДля общения пользуйтесь предоставленной клавиатурой)'
shipping_text = 'Введите дату для доставки\nОзнакомьтесь с условиями доставки:\nС сегодня на завтра (доставка ' \
                'бесплатно)\nПо предзаказу на нужную Вам дату (доставка бесплатно)\n С сегодня на сегодня (при ' \
                'наличии тортов, уточнять у операторов колл-центра) стоимость доставки 400 руб.'
messages = dict()


class FSMClient(StatesGroup):
    date = State()
    time = State()
    name = State()
    contact = State()
    address = State()
    promo = State()
    payment = State()


def register_client_dict(user_id):
    if user_id not in messages:
        messages[user_id] = []


async def command_start(message: types.Message):
    register_client_dict(message.from_user.id)
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, hello_text,
                                                                 reply_markup=client_kb.kb_client))


# Оформление заказа
async def order_start(callback_query: types.CallbackQuery):
    register_client_dict(callback_query.from_user.id)
    await FSMClient.date.set()
    messages[callback_query.from_user.id].append(await bot.send_message(callback_query.from_user.id, shipping_text,
                                                                        reply_markup=client_kb.get_dates()))
    await callback_query.answer()


# Дата доставки
async def load_date(message: types.Message, state: FSMContext):
    register_client_dict(message.from_user.id)
    async with state.proxy() as data:
        data['date'] = message.text
    await FSMClient.next()
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Выберете интервал для доставки',
                                                                 reply_markup=client_kb.get_time_button(message.text)))
    messages[message.from_user.id].append(message)


# Время доставки
async def load_time(message: types.Message, state: FSMContext):
    register_client_dict(message.from_user.id)
    async with state.proxy() as data:
        data['time'] = message.text
    await FSMClient.next()
    messages[message.from_user.id].append(
        await bot.send_message(message.from_user.id, 'Введите имя', reply_markup=client_kb.kb_cancel))
    messages[message.from_user.id].append(message)


# Имя клиента
async def load_name(message: types.Message, state: FSMContext):
    register_client_dict(message.from_user.id)
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMClient.next()
    messages[message.from_user.id].append(
        await bot.send_message(message.from_user.id, 'Введите контакт для связи или поделитесь привязанным к аккаунту',
                               reply_markup=client_kb.kb_contact))
    messages[message.from_user.id].append(message)


# Контакт с Telegram
async def load_contact(message: types.Message, state: FSMContext):
    register_client_dict(message.from_user.id)
    async with state.proxy() as data:
        if str(message.contact.phone_number)[0] == '7':
            data['contact'] = f'+{message.contact.phone_number}'
        else:
            data['contact'] = message.contact.phone_number
    await FSMClient.next()
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Введите адрес для доставки',
                                                                 reply_markup=client_kb.kb_cancel))
    messages[message.from_user.id].append(message)


# Контакт с клавиатуры
async def load_contact_2(message: types.Message, state: FSMContext):
    register_client_dict(message.from_user.id)
    async with state.proxy() as data:
        data['contact'] = message.text
    await FSMClient.next()
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Введите адрес для доставки',
                                                                 reply_markup=client_kb.kb_cancel))
    messages[message.from_user.id].append(message)


# Адрес доставки
async def load_address(message: types.Message, state: FSMContext):
    register_client_dict(message.from_user.id)
    async with state.proxy() as data:
        data['address'] = message.text
    await FSMClient.next()
    messages[message.from_user.id].append(
        await bot.send_message(message.from_user.id, 'Введите промокод', reply_markup=client_kb.kb_promo))
    messages[message.from_user.id].append(message)


# Промокод
async def get_promo_code(message: types.Message, state: FSMContext):
    register_client_dict(message.from_user.id)
    inline_online_payment = InlineKeyboardButton('Оплата онлайн', callback_data='online')
    inline_card_payment = InlineKeyboardButton('Оплата курьеру картой', callback_data='pay_card')
    inline_cash_payment = InlineKeyboardButton('Оплата курьеру наличными', callback_data='pay_cash')
    messages[message.from_user.id].append(message)

    if message.text in await promo_codes_bd.sql_promo_read_all():
        async with state.proxy() as data:
            data['promo_code'] = int(await promo_codes_bd.sql_promo_read_discount(message.text))
            messages[message.from_user.id].append(await bot.send_message(message.from_user.id,
                                                                         f'Активирован промокод на скидку '
                                                                         f'{data["promo_code"]}%'))
        for i in messages[message.from_user.id]:
            await i.delete()
        messages[message.from_user.id].clear()
        await FSMClient.next()
        messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Выберите способ оплаты',
                                                                     reply_markup=InlineKeyboardMarkup().add(
                                                                         inline_online_payment)
                                                                     .add(inline_card_payment).add(
                                                                         inline_cash_payment)))
    elif message.text == 'Продолжить без промокода':
        async with state.proxy() as data:
            data['promo_code'] = 0
        for i in messages[message.from_user.id]:
            await i.delete()
        messages[message.from_user.id].clear()
        await FSMClient.next()
        messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Выберите способ оплаты',
                                                                     reply_markup=InlineKeyboardMarkup().add(
                                                                         inline_online_payment)
                                                                     .add(inline_card_payment).add(
                                                                         inline_cash_payment)))
    else:
        messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Неверный промокод'))


# Способ оплаты
async def payment(callback_query: types.CallbackQuery, state: FSMContext):
    register_client_dict(callback_query.from_user.id)
    payment_type = callback_query.data.replace('pay_', '')

    async with state.proxy() as data:
        read = await basket_bd.sql_basket_read(callback_query.from_user.id)
        order = ''
        for ret in read:
            order += f'{ret[1]} ({ret[6]}гр)×{ret[4]}.'
        data['order'] = order
        data['id'] = callback_query.from_user.id
        data['uid'] = await orders_bd.create_uid(callback_query.from_user.id)

        if payment_type == 'card':
            data['pay'] = 'курьеру картой'
            await callback_query.answer('Вы выбрали оплату картой курьеру')
        elif payment_type == 'cash':
            data['pay'] = 'курьеру наличными'
            await callback_query.answer('Вы выбрали оплату наличными курьеру')

    await orders_bd.sql_orders_add_command(state)
    for ID in Admin_ID:
        await bot.send_message(ID, 'Поступил новый заказ')
    messages[callback_query.from_user.id].append(await bot.send_message(callback_query.from_user.id, 'Спасибо за заказ',
                                                                        reply_markup=client_kb.kb_client))
    await basket_bd.sql_basket_clear(callback_query.from_user.id)
    await state.finish()
    if callback_query.message in messages[callback_query.from_user.id]:
        messages[callback_query.from_user.id].remove(callback_query.message)
    await callback_query.message.delete()


# Отмена заказа в процессе
async def cancel_order(message: types.Message, state: FSMContext):
    register_client_dict(message.from_user.id)
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    messages[message.from_user.id].append(message)
    for i in messages[message.from_user.id]:
        await i.delete()
    messages[message.from_user.id].clear()
    messages[message.from_user.id].append(
        await bot.send_message(message.from_user.id, 'Заказ отменён', reply_markup=client_kb.kb_client))


# Каталог
async def command_catalog(message: types.Message):
    register_client_dict(message.from_user.id)
    read = await sqlite_db.sql_read2()
    for ret in read:
        inline_add_basket_button_1 = InlineKeyboardButton('В корзину (600 гр)', callback_data=f'add600 {ret[1]}')
        inline_add_basket_button_2 = InlineKeyboardButton('В корзину (1100 гр)', callback_data=f'add1100 {ret[1]}')
        inline_cut_button = InlineKeyboardButton('Показать разрез', callback_data=f'cut_1 {ret[1]}')
        messages[message.from_user.id].append(await bot.send_photo(message.from_user.id, ret[0].split(',')[0],
                                                                   f'{ret[1]}\nОписание товара: {ret[2]}\nЦена товара: '
                                                                   f'{ret[3].replace(" ", "/")} руб.',
                                                                   reply_markup=InlineKeyboardMarkup().row(
                                                                       inline_add_basket_button_1,
                                                                       inline_add_basket_button_2)
                                                                   .add(inline_cut_button)))
    messages[message.from_user.id].append(message)
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Выберите товары',
                                                                 reply_markup=client_kb.kb_catalog_back))


# Разрез торта
async def cut_callback(callback_query: types.CallbackQuery):
    if callback_query.data.split(' ')[0] == 'cut_1':
        message_photo = await sqlite_db.sql_get_photo(callback_query.data.replace('cut_1 ', ''))
        inline_add_basket_button_1 = InlineKeyboardButton(
            'В корзину (600 гр)', callback_data=f'add600 {callback_query.data.replace("cut_1 ", "")}')
        inline_add_basket_button_2 = InlineKeyboardButton(
            'В корзину (1100 гр)', callback_data=f'add1100 {callback_query.data.replace("cut_1 ", "")}')
        inline_back_catalog_button = InlineKeyboardButton('Показать торт целиком',
                                                          callback_data=callback_query.data.replace('cut_1', 'cut_2'))
        await callback_query.message.edit_media(InputMediaPhoto(message_photo.split(',')[1]))
        await callback_query.message.edit_caption(caption=callback_query.message.caption,
                                                  reply_markup=InlineKeyboardMarkup()
                                                  .row(inline_add_basket_button_1, inline_add_basket_button_2)
                                                  .add(inline_back_catalog_button))

    elif callback_query.data.split(' ')[0] == 'cut_2':
        message_photo = await sqlite_db.sql_get_photo(callback_query.data.replace('cut_2 ', ''))
        inline_add_basket_button_1 = InlineKeyboardButton(
            'В корзину (600 гр)', callback_data=f'add600 {callback_query.data.replace("cut_2 ", "")}')
        inline_add_basket_button_2 = InlineKeyboardButton(
            'В корзину (1100 гр)', callback_data=f'add1100 {callback_query.data.replace("cut_2 ", "")}')
        inline_cut_button = InlineKeyboardButton('Показать разрез',
                                                 callback_data=callback_query.data.replace('cut_2', 'cut_1'))
        await callback_query.message.edit_media(InputMediaPhoto(message_photo.split(',')[0]))
        await callback_query.message.edit_caption(caption=callback_query.message.caption,
                                                  reply_markup=InlineKeyboardMarkup()
                                                  .row(inline_add_basket_button_1, inline_add_basket_button_2)
                                                  .add(inline_cut_button))
    await callback_query.answer()


# Возврат в меню
async def back_command(message: types.Message):
    register_client_dict(message.from_user.id)
    messages[message.from_user.id].append(message)
    for i in messages[message.from_user.id]:
        await i.delete()
    messages[message.from_user.id].clear()
    messages[message.from_user.id].append(
        await bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=client_kb.kb_client))


# Добавление в корзину
async def add_callback_run(callback_query: types.CallbackQuery):
    if callback_query.data.replace('add', '')[0] == '6':
        read = await sqlite_db.sql_read_one(callback_query.data.replace('add600 ', ''))
        if await basket_bd.sql_in_basket(str(read[1]) + str(callback_query.from_user.id)) is not None:
            await callback_query.answer(text=f'Товар {callback_query.data.replace("add600 ", "")} уже в корзине')
        else:
            state = (read[0], read[1], read[3].split()[0], callback_query.from_user.id, 1, str(read[1]) +
                     str(callback_query.from_user.id), 600)
            await basket_bd.sql_basket_add_command(state)
            await callback_query.answer(text=f'Товар {callback_query.data.replace("add600 ", "")} добавлен в корзину')
    elif callback_query.data.replace('add', '')[0] == '1':
        read = await sqlite_db.sql_read_one(callback_query.data.replace('add1100 ', ''))
        if await basket_bd.sql_in_basket(str(read[1]) + str(callback_query.from_user.id)) is not None:
            await callback_query.answer(text=f'Товар {callback_query.data.replace("add1100 ", "")} уже в корзине')
        else:
            state = (read[0], read[1], read[3].split()[1], callback_query.from_user.id, 1, str(read[1]) +
                     str(callback_query.from_user.id), 1100)
            await basket_bd.sql_basket_add_command(state)
            await callback_query.answer(text=f'Товар {callback_query.data.replace("add1100 ", "")} добавлен в корзину')


# Редактирование корзины
async def command_basket(callback_query: types.CallbackQuery):
    register_client_dict(callback_query.from_user.id)
    read = await basket_bd.sql_basket_read(callback_query.from_user.id)
    for ret in read:
        inline_del_basket_button = InlineKeyboardButton('Удалить из корзины', callback_data=f'b_del {ret[1]}')
        inline_plus_basket_button = InlineKeyboardButton('+', callback_data=f'plus {ret[1]}')
        inline_minus_basket_button = InlineKeyboardButton('-', callback_data=f'minus {ret[1]}')
        messages[callback_query.from_user.id].append(
            await bot.send_photo(callback_query.from_user.id, ret[0].split(',')[0],
                                 f'{ret[1]}\nЦена товара: {ret[2]} руб.\nКоличество в корзине: {ret[4]}',
                                 reply_markup=InlineKeyboardMarkup().row(inline_plus_basket_button,
                                                                         inline_minus_basket_button)
                                 .add(inline_del_basket_button)))
    messages[callback_query.from_user.id].append(
        await bot.send_message(callback_query.from_user.id, 'Внесите изменения',
                               reply_markup=client_kb.kb_back_basket))


# Содержимое корзины
async def basket_message(message: types.Message):
    register_client_dict(message.from_user.id)
    for i in messages[message.from_user.id]:
        await i.delete()
    messages[message.from_user.id].clear()
    read = await basket_bd.sql_basket_read(message.from_user.id)
    if read:
        new_message = 'Ваша корзина:\n'
        sm = 0
        for ret in read:
            new_message += f'{ret[1]} ({ret[6]} гр) {ret[2]} руб. × {ret[4]}\n'
            sm += int(ret[2]) * int(ret[4])
        new_message += f'Общая сумма: {sm} руб.'
        inline_basket_button = InlineKeyboardButton('Редактировать корзину', callback_data='basket')
        inline_order_button = InlineKeyboardButton('Оформить заказ', callback_data='order')
        messages[message.from_user.id].append(await bot.send_message(message.from_user.id, new_message,
                                                                     reply_markup=InlineKeyboardMarkup().add(
                                                                         inline_basket_button).add(
                                                                         inline_order_button)))
        messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Выберите действие',
                                                                     reply_markup=client_kb.kb_back))
    else:
        messages[message.from_user.id].append(
            await bot.send_message(message.from_user.id, 'Корзина пуста', reply_markup=client_kb.kb_back))
    messages[message.from_user.id].append(message)


# Удаление из корзины
async def basket_del_callback_run(callback_query: types.CallbackQuery):
    await basket_bd.sql_basket_delete_command(str(callback_query.data.replace('b_del ', '')) +
                                              str(callback_query.from_user.id))
    if callback_query.message in messages[callback_query.from_user.id]:
        messages[callback_query.from_user.id].remove(callback_query.message)
        await callback_query.message.delete()
    await callback_query.answer(text=f'Товар {callback_query.data.replace("b_del ", "")} удалён из корзины')


# Увеличение количества товара в корзине
async def basket_plus_callback_run(callback_query: types.CallbackQuery):
    register_client_dict(callback_query.from_user.id)
    count = await basket_bd.sql_get_count(str(callback_query.data.replace('plus ', '')) +
                                          str(callback_query.from_user.id))
    data = (count[0] + 1, str(callback_query.data.replace('plus ', '')) + str(callback_query.from_user.id))
    if callback_query.message in messages[callback_query.from_user.id]:
        messages[callback_query.from_user.id].remove(callback_query.message)
    messages[callback_query.from_user.id].append(await callback_query.message.edit_caption(
        str(callback_query.message.caption)[:-len(str(count[0]))] + str(count[0] + 1),
        reply_markup=callback_query.message.reply_markup))
    await basket_bd.sql_basket_count_command(data)
    await callback_query.answer()


# Уменьшение количества товара в корзине
async def basket_minus_callback_run(callback_query: types.CallbackQuery):
    register_client_dict(callback_query.from_user.id)
    count = await basket_bd.sql_get_count(str(callback_query.data.replace('minus ', '')) +
                                          str(callback_query.from_user.id))
    if count[0] - 1 <= 0:
        await basket_bd.sql_basket_delete_command(
            str(callback_query.data.replace('minus ', '')) + str(callback_query.from_user.id))
        await callback_query.answer(text=f'Товар {callback_query.data.replace("minus ", "")} удалён из корзины')
        if callback_query.message in messages[callback_query.from_user.id]:
            messages[callback_query.from_user.id].remove(callback_query.message)
        await callback_query.message.delete()
    else:
        data = (count[0] - 1, str(callback_query.data.replace('minus ', '')) + str(callback_query.from_user.id))
        await basket_bd.sql_basket_count_command(data)
        messages[callback_query.from_user.id].remove(callback_query.message)
        messages[callback_query.from_user.id].append(await callback_query.message.edit_caption(
            str(callback_query.message.caption)[:-len(str(count[0]))] + str(count[0] - 1),
            reply_markup=callback_query.message.reply_markup))
        await callback_query.answer()


# Просмотр заказов
async def command_orders(message: types.Message):
    register_client_dict(message.from_user.id)
    read = await orders_bd.sql_orders_read(message.from_user.id)
    if read:
        for ret in read:
            all_ord = ret[6].split('.')
            ord_message = ''
            for i in all_ord:
                ord_message += f'{i}\n'
            messages[message.from_user.id].append(await bot.send_message(message.from_user.id,
                                                                         f'Заказ на имя: {ret[2]}\n'
                                                                         f'Доставка запланирована на {ret[0]}\n'
                                                                         f'По адресу: {ret[4]}\n'
                                                                         f'В промежуток: {ret[1]}\n'
                                                                         f'Заказ:\n{ord_message}Оплата {ret[-1]}\n'
                                                                         f'Контакт для связи: {ret[3]}\n',
                                                                         reply_markup=client_kb.kb_back))
    else:
        messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Нет активных заказов',
                                                                     reply_markup=client_kb.kb_back))
    messages[message.from_user.id].append(message)


# Обратная связь
async def command_feedback(message: types.Message):
    register_client_dict(message.from_user.id)
    messages[message.from_user.id].append(
        await bot.send_message(message.from_user.id, 'Для помощи обратитесь к @yakunin_egor',
                               reply_markup=client_kb.kb_back))
    messages[message.from_user.id].append(message)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(back_command, commands=['Вернуться_в_меню'])
    dp.register_callback_query_handler(order_start, lambda x: x.data and x.data.startswith('order'), state=None)
    dp.register_message_handler(cancel_order, state="*", commands='Отмена_заказа')
    dp.register_message_handler(cancel_order, Text(equals='Отмена_заказа', ignore_case=True), state='*')
    dp.register_message_handler(load_date, state=FSMClient.date)
    dp.register_message_handler(load_time, state=FSMClient.time)
    dp.register_message_handler(load_name, state=FSMClient.name)
    dp.register_message_handler(load_contact, content_types=types.ContentTypes.CONTACT, state=FSMClient.contact)
    dp.register_message_handler(load_contact_2, state=FSMClient.contact)
    dp.register_message_handler(load_address, state=FSMClient.address)
    dp.register_message_handler(get_promo_code, state=FSMClient.promo)
    dp.register_callback_query_handler(payment, lambda x: x.data and x.data.startswith('pay_'), state=FSMClient.payment)
    dp.register_message_handler(command_catalog, commands='Каталог')
    dp.register_message_handler(basket_message, commands='Корзина')
    dp.register_message_handler(command_orders, commands='Мои_заказы')
    dp.register_message_handler(command_feedback, commands='Обратная_связь')
    dp.register_message_handler(basket_message, commands='Вернуться_в_корзину')
    dp.register_callback_query_handler(add_callback_run, lambda x: x.data and x.data.startswith('add'))
    dp.register_callback_query_handler(cut_callback, lambda x: x.data and x.data.startswith('cut'))
    dp.register_callback_query_handler(basket_del_callback_run, lambda x: x.data and x.data.startswith('b_del'))
    dp.register_callback_query_handler(basket_plus_callback_run, lambda x: x.data and x.data.startswith('plus'))
    dp.register_callback_query_handler(basket_minus_callback_run, lambda x: x.data and x.data.startswith('minus'))
    dp.register_callback_query_handler(command_basket, lambda x: x.data and x.data.startswith('basket'))
