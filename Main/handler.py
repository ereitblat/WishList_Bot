from aiogram import html, F, Router

from aiogram.filters import CommandStart
from aiogram.types import Message
import keyboards as kb
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database.sqlite import create_wish, db_watch_wishes, db_book_wish, db_delete_wish


router = Router()


class Create(StatesGroup):
    name = State()
    description = State()
class AddNick(StatesGroup):
    nick = State()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Я бот, который поможет вам в осуществлении ваших желаний!", reply_markup=kb.main)


@router.message(F.text == "Добавить желание")
async def add_wish_name(message: Message, state: FSMContext):
    await state.set_state(Create.name)
    await message.answer("Задайте название своему желанию")


@router.message(Create.name)
async def add_wish_description(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Create.description)
    await message.answer("Опишите свое желание подробнее, можете добавить ссылку, цену")


@router.message(Create.description)
async def reading_wish_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await message.answer('Вы добавили новое желание!')
    await message.answer(
        f"Ваша хотелка:\n"
        f"{data['name']}\n"
        f"Описание:\n"
        f"{data['description']}"
    )
    await create_wish(hash(str(message.from_user.id)+data['name'])%100000, data['name'], data['description'], message.from_user.username)
    await state.clear()


@router.message(F.text == "Просмотреть свои желания")
async def watch_your_wishes(message: Message):
    await message.answer(await db_watch_wishes(message.from_user.username, True))


@router.message(F.text == "Посмотреть желания других")
async def add_person_name(message: Message, state: FSMContext):
    await state.set_state(AddNick.nick)
    await message.answer("Введите ник этого человека в телеграмме")

@router.message(AddNick.nick)
async def add_nick(message: Message, state: FSMContext):
    await state.update_data(nick=message.text)
    nick_data = await state.get_data()
    if message.from_user.username == nick_data['nick']:
        await message.answer(await db_watch_wishes(nick_data['nick'], True))
    else:
        await message.answer(await db_watch_wishes(nick_data['nick'], False))
    await state.clear()

class Book(StatesGroup):
    nick = State()
    id = State()

@router.message(F.text == "Забронировать желание")
async def add_name_to_book(message: Message, state: FSMContext):
    await state.set_state(Book.nick)
    await message.answer("Введите ник человека желание которого вы хотите забронировать")

@router.message(Book.nick)
async def add_nick(message: Message, state: FSMContext):
    await state.update_data(nick=message.from_user.username)
    result = await db_watch_wishes(message.text, False)
    await message.answer(result)
    if result == "У пользователя нет хотелок\n":
        await state.clear()
    else :
        await state.set_state(Book.id)
        await message.answer("Введите id желания, которое вы хотите забронировать")

@router.message(Book.id)
async def add_id(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    data = await state.get_data()
    await message.answer(await db_book_wish(data['nick'], data['id']))
    await state.clear()

class Delete(StatesGroup):
    id = State()
@router.message(F.text == "Отметить выполненым/удалить желание")
async def add_wish_name(message: Message, state: FSMContext):
    await state.set_state(Delete.id)
    result = await db_watch_wishes(message.from_user.username, True)
    await message.answer(result)
    if result != "У вас нет хотелок":
        await message.answer("Введите id желания, которое вы хотите удалить/отметить выполненым")
    else:
        await state.clear()

@router.message(Delete.id)
async def add_id(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    data = await state.get_data()
    await message.answer(await db_delete_wish(data["id"], message.from_user.username))
    await state.clear()
