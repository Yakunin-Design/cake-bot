import sqlite3 as sq
import random


base = sq.connect('cake.db')
cur = base.cursor()


async def sql_orders_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO orders VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_orders_read(data):
    return cur.execute('SELECT * FROM orders WHERE id == ?', (data,)).fetchall()


async def sql_orders_read_all():
    return cur.execute('SELECT * FROM orders').fetchall()


async def create_uid(data):
    uid = str(data) + str(random.randint(1000, 9999))
    is_unique = cur.execute('SELECT * FROM orders WHERE uid == ?', (uid,)).fetchone()
    while is_unique is not None:
        uid = str(data) + str(random.randint(1000, 9999))
        is_unique = cur.execute('SELECT * FROM orders WHERE uid == ?', (uid,)).fetchone()
    return uid


async def sql_set_pay(data):
    cur.execute('UPDATE orders SET pay == ? WHERE uid == ?', ('Оплачено', data))
    base.commit()


async def sql_delete_order(data):
    cur.execute('DELETE FROM orders WHERE uid == ?', (data,))
    base.commit()
