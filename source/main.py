import asyncio
import traceback
from tortoise import run_async
from config import LOOP_INTERVAL_TIME
from init_db import init_db
from microservices.google_table import GoogleTable
from tools import generate_list_gts_statements_rows, get_loop_interval_to_four_hour


async def main():
    first_load_statement_flag = True

    print("[startup]: RELOAD STATEMENT SERVICE STARTED")

    while True:
        # # Переводим время обновления на 4 утра при первом запуске
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
                lists_admins_rows = await generate_list_gts_statements_rows()
                gt = GoogleTable()

                for list_rows in lists_admins_rows:
                    try:
                        await gt.add_rows_to_bd_list(
                            table_encr_url=list_rows['gt_table_url'],
                            rows_list=list_rows['rows_to_add_in_bd']
                        )
                    except Exception:
                        print(traceback.format_exc())

                print(f"[success]: RELOAD ENDED, NEXD RELOAD THROW: {LOOP_INTERVAL_TIME} seconds")

            except Exception:
                print("[error]: ERROR WITH RELOAD")
                print(traceback.format_exc())

        # Ждем 24 часа - 86400 секунд
        await asyncio.sleep(LOOP_INTERVAL_TIME)


if __name__ == "__main__":
    run_async(init_db())
    asyncio.run(main())
