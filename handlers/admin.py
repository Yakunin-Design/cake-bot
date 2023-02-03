from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import bot
from aiogram.dispatcher.filters import Text
from create_bot import Admin_ID
from data_base import sqlite_db
from keybords import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data_base import orders_bd, promo_codes_bd


class FSMAdmin(StatesGroup):
    photo_1 = State()
    photo_2 = State()
    name = State()
    description = State()
    price = State()


class FSMPromo(StatesGroup):
    code = State()


messages = dict()


def register_dict(user_id):
    if user_id not in messages:
        messages[user_id] = []


async def get_admin_kb(message: types.Message):
    register_dict(message.from_user.id)
    messages[message.from_user.id].append(message)
    if str(message.from_user.id) in Admin_ID:
        messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Добро пожаловать, '
                                                                                           'администратор!',
                                                                     reply_markup=admin_kb.kb_admin))
    else:
        messages[message.from_user.id].append(await bot.send_message(message.from_user.id,
                                                                     'У вас недостаточно прав для выполнения данной '
                                                                     'команды'))


# Добавление товара
async def cm_start(message: types.Message):
    register_dict(message.from_user.id)
    if str(message.from_user.id) in Admin_ID:
        await FSMAdmin.photo_1.set()
        messages[message.from_user.id].append(
            await bot.send_message(message.from_user.id, 'Загрузите фото', reply_markup=admin_kb.kb_cancel))
        messages[message.from_user.id].append(message)


async def load_photo_1(message: types.Message, state: FSMContext):
    register_dict(message.from_user.id)
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await FSMAdmin.next()
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Загрузите второе фото'))
    messages[message.from_user.id].append(message)


async def load_photo_2(message: types.Message, state: FSMContext):
    register_dict(message.from_user.id)
    async with state.proxy() as data:
        data['photo'] += f',{message.photo[0].file_id}'
    await FSMAdmin.next()
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Введите название товара'))
    messages[message.from_user.id].append(message)


async def load_name(message: types.Message, state: FSMContext):
    register_dict(message.from_user.id)
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Введите описание товара'))
    messages[message.from_user.id].append(message)


async def load_description(message: types.Message, state: FSMContext):
    register_dict(message.from_user.id)
    async with state.proxy() as data:
        data['description'] = message.text
    await FSMAdmin.next()
    messages[message.from_user.id].append(
        await bot.send_message(message.from_user.id, 'Введите цены товара через пробел'))
    messages[message.from_user.id].append(message)


async def load_price(message: types.Message, state: FSMContext):
    register_dict(message.from_user.id)
    async with state.proxy() as data:
        data['price'] = message.text
    await sqlite_db.sql_add_command(state)
    await state.finish()
    messages[message.from_user.id].append(message)
    for i in messages[message.from_user.id]:
        await i.delete()
    messages[message.from_user.id].clear()
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Товар успешно добавлен',
                                                                 reply_markup=admin_kb.kb_admin))


# Выход из состояния добавления товара
async def cancel_handler(message: types.Message, state: FSMContext):
    register_dict(message.from_user.id)
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    messages[message.from_user.id].append(message)
    for i in messages[message.from_user.id]:
        await i.delete()
    messages[message.from_user.id].clear()
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Добавление товара отменено',
                                                                 reply_markup=admin_kb.kb_admin))


# Удаление товара
async def delete_product(message: types.Message):
    register_dict(message.from_user.id)
    if str(message.from_user.id) in Admin_ID:
        read = await sqlite_db.sql_read2()
        for ret in read:
            inline_del_button = InlineKeyboardButton(f'Удалить {ret[1]}', callback_data=f'del {ret[1]}')
            messages[message.from_user.id].append(await bot.send_photo(message.from_user.id, ret[0].split(',')[0],
                                                                       f'{ret[1]}\nОписание товара: {ret[2]}\nЦена '
                                                                       f'товара: {ret[3]} руб.',
                                                                       reply_markup=InlineKeyboardMarkup().add(
                                                                           inline_del_button)))
        messages[message.from_user.id].append(
            await bot.send_message(message.from_user.id, 'Для удаления товара нажмите на кнопку',
                                   reply_markup=admin_kb.kb_back))
        messages[message.from_user.id].append(message)


async def del_callback_run(callback_query: types.CallbackQuery):
    register_dict(callback_query.from_user.id)
    await sqlite_db.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'Товар {callback_query.data.replace("del ", "")} удалён')
    if callback_query.message in messages[callback_query.from_user.id]:
        messages[callback_query.from_user.id].remove(callback_query.message)
    await callback_query.message.delete()


# Возврат в главное меню
async def back_command(message: types.Message):
    register_dict(message.from_user.id)
    messages[message.from_user.id].append(message)
    for i in messages[message.from_user.id]:
        await i.delete()
    messages[message.from_user.id].clear()
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Вы вернулись в главное меню',
                                                                 reply_markup=admin_kb.kb_admin))


# Просмотр текущих заказов
async def active_orders(message: types.Message):
    register_dict(message.from_user.id)
    read = await orders_bd.sql_orders_read_all()
    messages[message.from_user.id].append(message)
    if read:
        for ret in read:
            all_ord = ret[6].split('.')
            ord_message = ''
            for i in all_ord:
                ord_message += f'{i}\n'
            inline_shipped_button = InlineKeyboardButton('Товар доставлен', callback_data=f'shipped{ret[8]}')
            messages[message.from_user.id].append(await bot.send_message(message.from_user.id,
                                                                         f'Заказ на имя: {ret[2]}\nДоставка'
                                                                         f'запланирована на {ret[0]}\n'
                                                                         f'По адресу: {ret[4]}\nВ промежуток {ret[1]}\n'
                                                                         f'Заказ:\n{ord_message}Скидка: {ret[5]}%\n'
                                                                         f'Оплата {ret[-1]}\nКонтакт для связи: '
                                                                         f'{ret[3]}\n',
                                                                         reply_markup=InlineKeyboardMarkup().add(
                                                                             inline_shipped_button)))
        messages[message.from_user.id].append(
            await bot.send_message(message.from_user.id, 'Активные заказы', reply_markup=admin_kb.kb_back))
    else:
        messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Нет активных заказов',
                                                                     reply_markup=admin_kb.kb_back))


# Реакция на доставку
async def shipped_callback_run(callback_query: types.CallbackQuery):
    register_dict(callback_query.from_user.id)
    await orders_bd.sql_delete_order(callback_query.data.replace('shipped', ''))
    await bot.send_message(callback_query.data.replace('shipped', '')[:-4], 'Ваш заказ доставлен')
    if callback_query.message in messages[callback_query.from_user.id]:
        messages[callback_query.from_user.id].remove(callback_query.message)
    await callback_query.message.delete()
    await callback_query.answer()


# Промокоды
async def promo_codes(message: types.Message):
    register_dict(message.from_user.id)
    inline_add_button = InlineKeyboardButton('Добавить промокод', callback_data='promo_add')
    inline_edit_button = InlineKeyboardButton('Просмотреть промокоды', callback_data='read_promo')
    messages[message.from_user.id].append(await bot.send_message(message.from_user.id, 'Промокоды:',
                                                                 reply_markup=InlineKeyboardMarkup().add(
                                                                     inline_add_button).add(
                                                                     inline_edit_button)))
    messages[message.from_user.id].append(
        await bot.send_message(message.from_user.id, 'Выберете действие', reply_markup=admin_kb.kb_back))
    messages[message.from_user.id].append(message)


# Добавление промокода
async def add_promo(callback_query: types.CallbackQuery):
    register_dict(callback_query.from_user.id)
    await FSMPromo.code.set()
    messages[callback_query.from_user.id].append(await bot.send_message(callback_query.from_user.id,
                                                                        'Введите промокод, а затем через пробел '
                                                                        'скидку в процентах'))


async def finish_promo(message: types.Message, state: FSMContext):
    register_dict(message.from_user.id)
    async with state.proxy() as data:
        data['code'] = message.text.split()[0]
        data['discount'] = message.text.split()[1]
    await promo_codes_bd.sql_promo_add_command(state)
    await state.finish()
    messages[message.from_user.id].append(message)
    for i in messages[message.from_user.id]:
        await i.delete()
    messages[message.from_user.id].clear()
    messages[message.from_user.id].append(
        await bot.send_message(message.from_user.id, 'Выберете действие', reply_markup=admin_kb.kb_admin))


# Список всех промокодов
async def read_promo(callback_query: types.CallbackQuery):
    register_dict(callback_query.from_user.id)
    read = await promo_codes_bd.sql_promo_read()
    if read:
        for ret in read:
            inline_del_button = InlineKeyboardButton(f'Удалить {ret[0]}', callback_data=f'p_del_promo {ret[0]}')
            messages[callback_query.from_user.id].append(await bot.send_message(callback_query.from_user.id,
                                                                                f'Промокод: {ret[0]}\n'
                                                                                f'Скидка: {ret[1]}%',
                                                                                reply_markup=InlineKeyboardMarkup().add(
                                                                                    inline_del_button)))
        messages[callback_query.from_user.id].append(
            await bot.send_message(callback_query.from_user.id, 'Активные промокоды',
                                   reply_markup=admin_kb.kb_back))
    else:
        messages[callback_query.from_user.id].append(
            await bot.send_message(callback_query.from_user.id, 'Нет активных промокодов'))


# Удаление промокода
async def del_promo(callback_query: types.CallbackQuery):
    await promo_codes_bd.sql_promo_delete_command(callback_query.data.replace('p_del_promo ', ''))
    await callback_query.answer(text=f'Промокод {callback_query.data.replace("p_del_promo ", "")} удалён')
    if callback_query.message in messages[callback_query.from_user.id]:
        messages[callback_query.from_user.id].remove(callback_query.message)
    await callback_query.message.delete()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(get_admin_kb, commands='Админка')
    dp.register_message_handler(promo_codes, commands='Промокоды')
    dp.register_message_handler(active_orders, commands='Активные_заказы')
    dp.register_message_handler(cm_start, commands=['Добавить_товар'], state=None)
    dp.register_message_handler(load_photo_1, content_types=['photo'], state=FSMAdmin.photo_1)
    dp.register_message_handler(load_photo_2, content_types=['photo'], state=FSMAdmin.photo_2)
    dp.register_message_handler(cancel_handler, state="*", commands='Отмена')
    dp.register_message_handler(cancel_handler, Text(equals='Отмена', ignore_case=True), state='*')
    dp.register_message_handler(load_name, state=FSMAdmin.name)
    dp.register_message_handler(load_description, state=FSMAdmin.description)
    dp.register_message_handler(load_price, state=FSMAdmin.price)
    dp.register_message_handler(back_command, commands='Назад')
    dp.register_message_handler(delete_product, commands='Удаление_товаров')
    dp.register_message_handler(finish_promo, state=FSMPromo.code)
    dp.register_callback_query_handler(del_callback_run, lambda x: x.data and x.data.startswith('del'))
    dp.register_callback_query_handler(shipped_callback_run, lambda x: x.data and x.data.startswith('shipped'))
    dp.register_callback_query_handler(add_promo, lambda x: x.data and x.data.startswith('promo_add'))
    dp.register_callback_query_handler(read_promo, lambda x: x.data and x.data.startswith('read_promo'))
    dp.register_callback_query_handler(del_promo, lambda x: x.data and x.data.startswith('p_del_promo'))
