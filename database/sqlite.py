from aiogram import html
import sqlite3 as sq

async def db_start():
    global db, cur

    db = sq.connect('new.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS wishes(wish_id TEXT PRIMARY KEY, name TEXT, description TEXT, owner TEXT, booker TEXT)")
    db.commit()


async def create_wish(wish_id, name, description, owner):
    cur.execute("INSERT INTO wishes VALUES(?, ?, ?, ?, ?)", (wish_id, name, description, owner, "Еще никто не забронировал"))
    db.commit()

async def db_book_wish(booker, wish_id):
    cur.execute("SELECT * FROM wishes WHERE wish_id = ?", (wish_id,))
    wish = cur.fetchone()
    if wish is None:
        return "У пользователя нет желания с таким ID"
    if wish[4] == "Еще никто не забронировал":
        cur.execute("UPDATE wishes SET booker = ? WHERE wish_id = ?", (booker, wish_id))
        db.commit()
        return "Желание забронировано"
    else:
        return "Это желание уже забронировано другим пользователем"

async def db_delete_wish(wish_id, owner):
    cur.execute("SELECT * FROM wishes WHERE wish_id = ?", (wish_id,))
    wish = cur.fetchone()
    if wish is None or wish[3]!= owner:
        return "У вас нет желания с данным ID"
    else:
        cur.execute("DELETE FROM wishes WHERE wish_id = ?", (wish_id,))
        db.commit()
        return "Данное желание удалено"

async def db_watch_wishes(owner, check_myself):
    if owner[0] == "@":
        owner = owner[1:]
    cur.execute("SELECT * FROM wishes WHERE owner=?", (owner,))
    wishes = cur.fetchall()
    result = f"Ваши хотелки:\n" if check_myself else f"Хотелки @{owner}:\n"
    for wish in wishes:
        result += f"{html.bold('id хотелки:')}\n"
        result += f"{wish[0]}\n"
        result += f"{html.bold('название хотелки:')}\n"
        result += f"{wish[1]}\n"
        result += f"{html.bold('описание хотелки:')}\n"
        result += f"{wish[2]}\n"
        if not check_myself:
            result += f"{html.bold('тот, кто забронировал хотелку:')}\n"
            if wish[4] == "Еще никто не забронировал":
                result += f"{('Еще никто не забронировал')}\n"
            else :
                result += f"{'@' + (wish[4])}\n"
        else:
            result += f"{html.bold('тот, кто забронировал хотелку:')}\n"
            if wish[4] == "Еще никто не забронировал":
                result += f"{('Еще никто не забронировал')}\n"
            else:
                result += f"{('Это желание уже забронировано')}\n"
        result += f"\n"
    if result == (f"Ваши хотелки:\n" if check_myself else f"Хотелки @{owner}:\n"):
        result = "У вас нет хотелок\n" if check_myself else "У пользователя нет хотелок\n"
    return result
