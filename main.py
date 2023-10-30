import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
import json
from mongo import Mongo_DB
from dotenv import load_dotenv
load_dotenv()
from os import getenv

TOKEN = getenv('TOKEN')
bot= Bot(TOKEN, parse_mode='html')
dp =Dispatcher()
MDB = Mongo_DB("user", "user", port=27018)
MDB.set_db_collection("payments", "payments")





@dp.message(CommandStart())
async def start(message:Message):
    await message.answer('Пришлите входные данные')

@dp.message()
async def message_input(message:Message):
    dump:dict= json.loads(message.text)
    try:
        text=MDB.make_aggrigate(dt_from=dump.get('dt_from'), dt_upto=dump.get('dt_upto'),group_type=dump.get('group_type'))
        await message.answer(text)
    except:
        await message.answer('Случилась непредвиденная ошибка')




async def main():
    await dp.start_polling(bot)

if __name__=='__main__':
    asyncio.run(main())