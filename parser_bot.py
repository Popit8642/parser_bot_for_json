# import
import asyncio, json, aiofiles, os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

# router
router = Router()

# the main variables
JSON_FILE = f"{os.getcwd()}/data.json"
INTERVAL = 60
previous_value = None
active_chats = set()

# bot
bot = Bot(token="your_token")

# function for start bot
async def main():
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

# function read json file
async def read_json_file():
    try:
        async with aiofiles.open(JSON_FILE, 'r', encoding='utf-8') as data_file:
            content = await data_file.read()
            data = json.loads(content)
            return data
        
    except Exception as e:
        print(f"Произошла ошибка при чтении data.json: {e}")
        return None

# function for message in active chats
async def send_to_all_chats(message_text: str):
    for chat_id in active_chats.copy():
        try:
            await bot.send_message(chat_id, message_text)
        except Exception as e:
            active_chats.discard(chat_id)

# start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(f"Hi, {message.from_user.first_name}! This bot is not intended for use, but is a test instance. Create by")

# function for monitoring and parsing information in chats
async def monitoring():
    global previous_value

    while True:
        data = await read_json_file()
        if data:
            current_value = data.get("last_transaction")

            if previous_value != current_value:
                data1_message = f"""
--------------------------------------------------
Хэш транзакции: {current_value['tx_hash']}
--------------------------------------------------
Время: {current_value['timestamp']}
--------------------------------------------------
Сумма эфириума: {current_value['amount_eth']}           
--------------------------------------------------
Из: {current_value['from']}
--------------------------------------------------
В: {current_value['to']}
--------------------------------------------------
                                """
                await send_to_all_chats(data1_message)


                data2_message = data.get("total_transactions")
                data2_message = f"Общее кол-во транзакций: {data2_message}"
                data3_message = data.get("total_eth_sent")
                data3_message = f"Общее кол-во отправленного эфириума: {data3_message}"

                await send_to_all_chats(f"""{data2_message}
{data3_message}""")
            
            previous_value = current_value
        
        await asyncio.sleep(INTERVAL)
# command start monitoring
@router.message(F.text == "Запуск")
async def cmd_start_monitoring(message: Message):
    chat_id = message.chat.id
    active_chats.add(chat_id)
    asyncio.create_task(monitoring())
    await message.answer("Мониторинг запущен")


if __name__ == "__main__":
    try:
        print("Bot is on")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is off")