import sqlite3 as sq

base = sq.connect('cake.db')
cur = base.cursor()


async def sql_promo_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO promo VALUES(?, ?)', tuple(data.values()))
        base.commit()


async def sql_promo_read():
    return cur.execute('SELECT * FROM promo').fetchall()


async def sql_promo_delete_command(data):
    cur.execute('DELETE FROM promo WHERE code == ?', (data,))
    base.commit()


async def sql_promo_read_all():
    return [i[0] for i in cur.execute('SELECT code FROM promo').fetchall()]


async def sql_promo_read_discount(data):
    return cur.execute('SELECT discount FROM promo WHERE code == ?', (data,)).fetchone()[0]
