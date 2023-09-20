from datetime import datetime, timedelta
import traceback
import asyncio
from tortoise import run_async
from init_db import init_db
from admin_bank_model import AdminInfo

# Интервал перезапуска, каждые 24 часа
LOOP_INTERVAL_TIME = 86400


async def main():
    first_load_statement_flag = True

    print("[startup]: RELOAD STATEMENT SERVICE STARTED")

    while True:
        # Переводим время обновления на 4 утра при первом запуске
        if first_load_statement_flag:
            first_load_statement_flag = False
            current_datetime = datetime.now()
            config_reload_datetime = current_datetime + timedelta(days=1)
            next_reload_datetime = datetime(
                year=config_reload_datetime.year,
                month=config_reload_datetime.month,
                day=config_reload_datetime.day,
                hour=4
            )

            new_loop_interval_time = (next_reload_datetime - current_datetime).total_seconds()
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
                return

            # Ждем 24 часа - 86400 секунд
            await asyncio.sleep(LOOP_INTERVAL_TIME)


if __name__ == "__main__":
    run_async(init_db())
    asyncio.run(main())

