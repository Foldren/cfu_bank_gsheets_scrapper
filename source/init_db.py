from tortoise import Tortoise
from config import MYSQL_URL


async def init_db():
    # Инициализируем нужные для работы таблицы
    await Tortoise.init(
        db_url=MYSQL_URL,
        modules={'models': ["init_models"]},
    )
