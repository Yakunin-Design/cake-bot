from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.types.message import ContentType
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from create_bot import payment_token, bot, payment_img, Admin_ID
from handlers.client import FSMClient, messages
from data_base import basket_bd, orders_bd
from keybords import client_kb
import datetime


uid = 0


async def buy_proces(callback_query: types.CallbackQuery, state: FSMContext):
    now_date = datetime.date.today().strftime('%d-%m-%Y')
    async with state.proxy() as data:
        global uid
        read = await basket_bd.sql_basket_read(callback_query.from_user.id)
        order = ''
        order_sum = 0
        for ret in read:
            order_sum += int(ret[2]) * int(ret[4])
            order += f'{ret[1]} ({ret[6]}гр)×{ret[4]}.'
        data['order'] = order
        data['id'] = callback_query.from_user.id
        uid = await orders_bd.create_uid(callback_query.from_user.id)
        data['uid'] = uid
        data['pay'] = 'Онлайн'
        order_sum = int((order_sum * (1 - data['promo_code'] / 100)) * 100)
        if data['date'] == now_date:
            order_sum += 40000
        price = LabeledPrice(label='basket', amount=order_sum)
        prices = [price, ]
    await bot.send_invoice(callback_query.message.chat.id,
                           title='Оплата заказа',
                           description='Оплата пользовательской корзины',
                           provider_token=payment_token,
                           currency='rub',
                           photo_url=payment_img,
                           photo_height=1000,
                           photo_width=1000,
                           prices=prices,
                           start_parameter='example',
                           payload='basket')
    await orders_bd.sql_orders_add_command(state)
    await basket_bd.sql_basket_clear(callback_query.from_user.id)
    await state.finish()
    if callback_query.message in messages[callback_query.from_user.id]:
        messages[callback_query.from_user.id].remove(callback_query.message)
    await callback_query.message.delete()
    messages.clear()


async def checkout_proces(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def successful_payment(message: Message):
    await orders_bd.sql_set_pay(uid)
    await bot.send_message(message.chat.id, 'Оплата прошла успешно', reply_markup=client_kb.kb_client)
    for i in Admin_ID:
        await bot.send_message(i, 'Поступил новый заказ')


def register_payment_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(buy_proces, lambda x: x.data and x.data.startswith('online'),
                                       state=FSMClient.payment)
    dp.register_pre_checkout_query_handler(checkout_proces, lambda q: True)
    dp.register_message_handler(successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)
