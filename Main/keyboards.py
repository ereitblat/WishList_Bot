from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

kb1 = KeyboardButton(text="Добавить желание")
kb2 = KeyboardButton(text="Просмотреть свои желания")
kb3 = KeyboardButton(text="Посмотреть желания других")
kb4 = KeyboardButton(text="Забронировать желание")
kb5 = KeyboardButton(text="Отметить выполненым/удалить желание")

builder = ReplyKeyboardBuilder()

builder.add(kb1)
builder.row(kb2, kb3)
builder.row(kb4, kb5)

main = builder.as_markup(resize_keyboard=True, input_field_placeholder='Выберите пункт меню')
