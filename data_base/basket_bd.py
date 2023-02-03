import sqlite3 as sq

base = sq.connect('cake.db')
cur = base.cursor()


async def sql_basket_add_command(state):
    cur.execute('INSERT INTO basket VALUES(?, ?, ?, ?, ?, ?, ?)', state)
    base.commit()


async def sql_basket_read(data):
    return cur.execute('SELECT * FROM basket WHERE id == ?', (data,)).fetchall()


async def sql_basket_delete_command(data):
    cur.execute('DELETE FROM basket WHERE uid == ?', (data,))
    base.commit()


async def sql_in_basket(data):
    return cur.execute('SELECT name FROM basket WHERE uid == ?', (data,)).fetchone()


async def sql_get_count(data):
    return cur.execute('SELECT count FROM basket WHERE uid == ?', (data,)).fetchone()


async def sql_basket_count_command(data):
    cur.execute('UPDATE basket SET count == ? WHERE uid == ? ', data)
    base.commit()


async def sql_basket_clear(data):
    cur.execute('DELETE FROM basket WHERE id == ?', (data, ))
    base.commit()


async def sql_get_one(data):
    return cur.execute('SELECT * FROM basket WHERE uid == ?', (data, )).fetchone()

