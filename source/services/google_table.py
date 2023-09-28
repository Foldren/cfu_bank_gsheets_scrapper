from os import getcwd

from google.oauth2.service_account import Credentials
from gspread_asyncio import AsyncioGspreadClientManager
from source.config import NAME_GOOGLE_TABLE_BD_LIST


class GoogleTable:
    agcm: AsyncioGspreadClientManager
    json_creds_path = "source/upravlyaika-credentials.json"  # "universe_domain": "googleapis.com"

    def __inti_credentials(self):
        creds = Credentials.from_service_account_file(self.json_creds_path)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped

    def __init__(self):
        self.agcm = AsyncioGspreadClientManager(self.__inti_credentials)

    async def add_rows_to_bd_list(self, table_url: str, rows_list: list):
        """
        Функция для добавления массива строк в таблицу

        :param table_url: ссылка на таблицу
        :param rows_list: лист строк для google table
        """

        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_url)
        ws = await ss.worksheet(NAME_GOOGLE_TABLE_BD_LIST)

        # value_input_option='USER_ENTERED' решает проблему с апострофом который появляется в таблице
        await ws.append_rows(rows_list, value_input_option='USER_ENTERED')

