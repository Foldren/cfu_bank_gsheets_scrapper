import json
from asyncio import run
from datetime import datetime
from httpx import AsyncClient


class ModuleBank:
    @staticmethod
    async def get_statement(api_key: str, from_date: str):
        """
        Функция для получения выписок по счету в Модуль банке от заданной даты до текущего времени

        :param api_key: апи ключ клиентского Модуль банка
        :param from_date: дата начала периода отгрузки выписки (в формате 2023-07-13)

        """
        headers = {'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'}

        async with AsyncClient() as async_session:
            # Получаем company id
            r_company_info = await async_session.post("https://api.modulbank.ru/v1/account-info", headers=headers)
            company_id = r_company_info.json()[0]['companyId']

            if r_company_info.status_code != 200:
                raise Exception(f"[error]: ERROR ON API TINKOFF:\n\n {r_company_info.text}")

            url_operation = 'https://api.modulbank.ru/v1/operation-history/' + str(company_id)

            # Получаем выписки
            r_operations = await async_session.post(
                url=url_operation,
                headers=headers,
                data={
                    'from': from_date,
                    'till': datetime.now().strftime("%Y-%m-%d"),
                    'skip': 0,
                    'records': 50,
                }
            )

            if r_operations.status_code == 200:
                print(json.dumps(r_operations.json(), indent=4))
            else:
                print(r_operations.text)

            # if response.status_code == 200:
            #     operations_list = response.json()['operations']
            #     result_data_list = []
            #
            #     for operation in operations_list:
            #         cp_name = operation['counterParty']["name"]
            #         cp_inn = operation['counterParty']["inn"]
            #         type_operation = "расход" if operation["typeOfOperation"] == "Debit" else "приход"
            #         volume_operation = operation["operationAmount"]
            #         trxn_date = operation["trxnPostDate"]
            #         result_data_list.append([cp_inn, cp_name, volume_operation, type_operation, trxn_date])
            #
            #     return result_data_list
            # else:
            #     raise Exception(f"[error]: ERROR ON API TINKOFF:\n\n {response.text}")


if __name__ == "__main__":
    run(ModuleBank.get_statement(
        api_key="NTU1OTY4ZDMtN2EyYi00ZTM0LWI1ZmQtOTVlNWFlMDcwNDUwMzNhYmU0YTgtNjUxZi00MTNjLTlkNjAtOWU0ODMwMGMyNjM3",
        from_date="2023-01-01"))
