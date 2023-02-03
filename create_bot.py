from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2


storage = RedisStorage2()


Admin_ID = ['736301626', '629150228', '429995171']
bot = Bot(token='5870016703:AAFDYdGSEsVNYhs1yBiW57AidN6y2Z5Ai3s')
dp = Dispatcher(bot, storage=storage)
payment_token = '381764678:TEST:49470'
payment_img = 'https://www.rts22.ru/wp-content/uploads/2019/11/oplatamoney.jpg'
