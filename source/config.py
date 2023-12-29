from os import getenv, environ
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


IS_THIS_LOCAL = "Pycharm" in str(Path.cwd())
MYSQL_URL = environ['MYSQL_URL'] if IS_THIS_LOCAL else getenv("MYSQL_URL")

# Интервал перезапуска, каждые 24 часа
LOOP_INTERVAL_TIME = 86400
NAME_GOOGLE_TABLE_BD_LIST = "БД (не редактировать)"
BANKS_RUS_NAMES = {
    'tinkoff': 'Тинькофф',
    'module': 'Модуль',
    'tochka': 'Точка',
}
SECRET_KEY = getenv('SECRET_KEY')
PROXY6NET_PROXIES = {"socks5://": getenv('PROXY_HTTPS_URL')}

