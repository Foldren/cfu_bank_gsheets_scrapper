import asyncio
import traceback
from tortoise import run_async
from source.init_db import init_db
from source.config import LOOP_INTERVAL_TIME
from source.tools import get_loop_interval_to_four_hour, write_operations_list_in_bd_users


async def main():
    first_load_statement_flag = True

    print("[startup]: RELOAD STATEMENT SERVICE STARTED")

    while True:
        # Переводим время обновления на 4 утра при первом запуске
        if first_load_statement_flag:
            first_load_statement_flag = False
            new_loop_interval_time = await get_loop_interval_to_four_hour()
            print(f"[message]: SEEN FIRST START, RELOAD START THROW: {new_loop_interval_time} seconds")
            # Ждем 4 утра следующего дня
            await asyncio.sleep(new_loop_interval_time)
            continue

        else:
            try:
                print("[message]: START RELOAD")

            except Exception as E:
                print("[error]: ERROR WITH RELOAD")
                print(E)
                print(traceback.format_exc())

            # Ждем 24 часа - 86400 секунд
            await asyncio.sleep(LOOP_INTERVAL_TIME)


if __name__ == "__main__":
    run_async(init_db())
    # asyncio.run(main())
    asyncio.run(write_operations_list_in_bd_users())
