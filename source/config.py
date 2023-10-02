from os import getenv
from environs import Env
from pathlib import Path

env = Env()
env.read_env('.env')

IS_THIS_LOCAL = "Pycharm" in str(Path.cwd())
MYSQL_URL = getenv('MYSQL_URL') if IS_THIS_LOCAL else env("MYSQL_URL")

# Интервал перезапуска, каждые 24 часа
LOOP_INTERVAL_TIME = 86400
NAME_GOOGLE_TABLE_BD_LIST = "БД (не редактировать)"
BANKS_RUS_NAMES = {
    'tinkoff': 'Тинькофф',
    'module': 'Модуль',
    'tochka': 'Точка',
}

PROXY6NET_PROXIES = {
    "socks5://": getenv("PROXY_HTTPS_URL") if IS_THIS_LOCAL else env('PROXY_HTTPS_URL'),
}

