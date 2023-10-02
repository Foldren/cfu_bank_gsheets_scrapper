import asyncio
from asyncio import run
from datetime import datetime
from httpx import AsyncClient
from config import PROXY6NET_PROXIES


class ModuleBank:
    @staticmethod
    async def get_statement(api_key: str, rc_number: int, from_date: str):
        """
        Функция для получения выписок по счету в Модуль банке от заданной даты до текущего времени

        :param api_key: апи ключ клиентского Модуль Банка
        :param rc_number: номер расчетного счета клиента
        :param from_date: дата начала периода отгрузки выписки (в формате 2023-07-13)
        :return:
        """
        headers = {'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'}

        async with AsyncClient(proxies=PROXY6NET_PROXIES) as async_session:
            # Получаем информацию о компании ---------------------------------------------------------------------------
            r_company_info = await async_session.post("https://api.modulbank.ru/v1/account-info", headers=headers)

            if r_company_info.status_code != 200:
                raise Exception(f"[error]: ERROR ON API MODULE:\n\n {r_company_info.text}")

            r_company_info_json = r_company_info.json()
            account_id = ""

            # Берем account_id по указанному расчётному счёту ----------------------------------------------------------
            for rc in r_company_info_json[0]['bankAccounts']:
                if rc['number'] == str(rc_number):
                    account_id = rc['id']

            url_operation = 'https://api.modulbank.ru/v1/operation-history/' + str(account_id)

            # Получаем выписки, так как ограничение стоит на 50 делаем это со смещением даты пока не выведем все -------
            result_operations_list = []
            till_date_next = datetime.now().strftime("%Y-%m-%d")
            last_operations = []
            while True:
                r_operations = await async_session.post(
                    url=url_operation,
                    headers=headers,
                    json={
                        'from': from_date,
                        'till': till_date_next,
                        'records': 50,
                    }
                )

                r_operations_list = r_operations.json()

                if last_operations == r_operations_list:
                    break

                index_last_operation = len(r_operations_list) - 1
                till_date_next = datetime \
                    .strptime(r_operations_list[index_last_operation]['executed'], "%Y-%m-%dT%H:%M:%S") \
                    .strftime("%Y-%m-%d")

                result_operations_list += r_operations_list
                last_operations = r_operations_list

            # Форматируем результаты -----------------------------------------------------------------------------------
            result_data_list = []
            for operation in result_operations_list:
                cp_name = operation['contragentName']
                cp_inn = operation['contragentInn']
                type_operation = "Расход" if operation["category"] == "Debit" else "Доход"
                volume_operation = operation["amount"] if type_operation == "Доход" else -round(operation["amount"], 2)
                trxn_date = datetime.strptime(operation["executed"], '%Y-%m-%dT%H:%M:%S').strftime('%d.%m.%Y %H:%M')
                result_data_list.append({
                    'partner_inn': cp_inn,
                    'partner_name': cp_name,
                    'op_volume': volume_operation if type_operation == "Доход" else -round(volume_operation, 2),
                    'op_type': type_operation,
                    'op_date': trxn_date,
                })

            return result_data_list


# if __name__ == "__main__":
#     run(ModuleBank.get_statement(
#         api_key="NTU1OTY4ZDMtN2EyYi00ZTM0LWI1ZmQtOTVlNWFlMDcwNDUwMzNhYmU0YTgtNjUxZi00MTNjLTlkNjAtOWU0ODMwMGMyNjM3",
#         rc_number=40802810070010406912,
#         from_date="2023-01-01"))
