from aiogram import Dispatcher, Bot
from database import (
    init_pl,
    init_db
)

from bot.main_commands import router as commander_router

from scanners.eth import scanner as eth_scanner
from scanners.bnb import scanner as bnb_scanner
from scanners.gram import scanner as gram_scanner
from scanners.sol import scanner as sol_scanner

import logging
import asyncio
import os

logging.basicConfig(level=logging.INFO, format="%(message)s")

bot = Bot(
    token=os.environ["token"]
)

dp = Dispatcher()
dp.include_router(
    commander_router
)   

async def main():
    pl = await init_pl()
    await init_db(pl)
    dp['pl'] = pl
    
    try:
        async with asyncio.TaskGroup() as tgroup:
            tasks = [
                tgroup.create_task(
                    eth_scanner(pl, bot)
                ),
                tgroup.create_task(
                    bnb_scanner(pl, bot)
                ),
                tgroup.create_task(
                    gram_scanner(pl, bot)
                ),
                tgroup.create_task(
                    sol_scanner(pl, bot)
                )
            ]
            polling_task = tgroup.create_task(
                dp.start_polling(bot)
                )
            try: 
                await polling_task
            except asyncio.CancelledError as exc:
                print(f"Poll closing error - {exc}")
                raise
            finally:
                for task in tasks:
                    task.cancel()
    except asyncio.CancelledError as exc:
        print(f"Tasks closing error - {exc}.")
        raise
    finally:
        pl.close()
        await pl.wait_closed()
            
if __name__ == "__main__":
    asyncio.run(main()) 
