import sqlite3 as sq
from create_bot import bot


def sql_start():
    global base, cur
    base = sq.connect('cake.db')
    cur = base.cursor()
    if base:
        print('База данных успешно подключена')
    base.execute('CREATE TABLE IF NOT EXISTS products (img TEXT, name TEXT PRIMARY KEY, description TEXT, price TEXT)')
    base.commit()

    base.execute('''CREATE TABLE IF NOT EXISTS basket 
    (img TEXT, name TEXT, price INTEGER, id TEXT, count INTEGER, uid TEXT PRIMARY KEY, weight TEXT)''')
    base.commit()

    base.execute('CREATE TABLE IF NOT EXISTS orders '
                 '(date TEXT, time TEXT, name TEXT, contact TEXT, address TEXT,'
                 '  discount INTEGER, ord TEXT, id TEXT, uid TEXT, pay TEXT)')
    base.commit()

    base.execute('CREATE TABLE IF NOT EXISTS promo (code TEXT PRIMARY KEY, discount INTEGER)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO products VALUES(?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_read(message):
    for ret in cur.execute('SELECT * FROM products').fetchall():
        await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание товара: '
                                                           f'{ret[2]}\nЦена товара: {ret[3]} руб.')


async def sql_read2():
    return cur.execute('SELECT * FROM products').fetchall()


async def sql_delete_command(data):
    cur.execute('DELETE FROM products WHERE name == ?', (data,))
    base.commit()


async def sql_read_one(data):
    return cur.execute('SELECT * FROM products WHERE name == ?', (data,)).fetchall()[0]


async def sql_get_photo(data):
    return cur.execute('SELECT img FROM products WHERE name == ?', (data,)).fetchone()[0]
