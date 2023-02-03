from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin, payment
from data_base import sqlite_db


async def on_startup(_):
    print('Бот вышел в сеть')
    sqlite_db.sql_start()

client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
payment.register_payment_handlers(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
