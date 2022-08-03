from src.chats import *
from src.messages import *
from src.commands import *


async def main():
    me = await bot.get_me()
    print(me.username)

    sendler = asyncio.create_task(messenger())
    await sendler

    await bot.start()
    await bot.run_until_disconnected()

with bot:
    bot.loop.run_until_complete(main())
