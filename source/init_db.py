from tortoise import Tortoise
from source.config import MYSQL_URL


async def init_db():
    # Инициализируем нужные для работы таблицы
    await Tortoise.init(
        db_url=MYSQL_URL,
        modules={'models': ["source.init_models"]},
    )
