from datetime import datetime
from google.oauth2.service_account import Credentials
from gspread_asyncio import AsyncioGspreadClientManager
from source.config import NAME_GOOGLE_TABLE_BD_LIST


class GoogleTable:
    agcm: AsyncioGspreadClientManager
    json_creds_path = "upravlyaika-credentials.json"  # "universe_domain": "googleapis.com"

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

    async def add_new_str_to_bd(self, table_url: str, chat_id_worker: int, fullname_worker: str, volume_op: str,
                                org_op: str, queue_op: str, type_op: str, payment_method: str,
                                sender_is_org: bool = False):
        """
        Функция для добавления новой строки (записи) в гугл таблицу в лист БД
        Параметр type_op = profit или cost

        :param org_op: наименование организации
        :param sender_is_org: флаг, что исполнитель - юр лицо
        :param table_url: ссылка на гугл таблицу
        :param chat_id_worker: chat_id сотрудника в телеграм, который производит запись
        :param fullname_worker: полное имя сотрудника
        :param volume_op: сумма операции
        :param queue_op: очередь выбранных категорий для выполнения операции через знак - ' → '
        :param type_op: значения profit или cost (соответственно тип операции доход или расход)
        :param payment_method: тип оплаты, либо банк
        """

        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_url)
        ws = await ss.worksheet(NAME_GOOGLE_TABLE_BD_LIST)
        frmt_date_time = datetime.now().strftime('%d.%m.%Y %H:%M')
        queue_items = queue_op.split(" → ")
        menu_item_lvls = [" ", " ", " ", " ", " ", " "]
        profit_or_cost = type_op == "profit"
        type_op = "Доход" if profit_or_cost else "Расход"
        volume_with_sign = volume_op if profit_or_cost else -int(volume_op)
        surname_fstname = fullname_worker.split(" ")[1] + " " + fullname_worker.split(" ")[0]

        i = 0
        for e in queue_items:
            menu_item_lvls[i] = e
            i += 1

        await ws.append_row([int(chat_id_worker),
                             "ЮР Лицо" if sender_is_org else surname_fstname,
                             frmt_date_time,
                             type_op,
                             payment_method,
                             volume_with_sign,
                             org_op,
                             menu_item_lvls[0],
                             menu_item_lvls[1],
                             menu_item_lvls[2],
                             menu_item_lvls[3],
                             menu_item_lvls[4]
                             ], value_input_option='USER_ENTERED')
        # value_input_option='USER_ENTERED' решает проблему с апострофом который появляется в таблице

