from tortoise import Tortoise
from config import MYSQL_URL


async def init_db():
    # Инициализируем таблицу admin_info
    await Tortoise.init(
        db_url=MYSQL_URL,
        modules={'models': ["admin_info_model"]},
    )
