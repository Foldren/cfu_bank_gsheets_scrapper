from asyncio import run
from datetime import datetime
from httpx import AsyncClient
from config import PROXY6NET_PROXIES


class Tinkoff:
    @staticmethod
    async def get_statement(api_key: str, rc_number: int, from_date: str) -> list:
        """
        Функция для получения выписок по счету в Тинькофф от заданной даты до текущего времени

        :param api_key: апи ключ клиентского Тинькофф
        :param rc_number: номер расчетного счета клиента
        :param from_date: дата начала периода отгрузки выписки (в формате 2023-07-13)
        :return:
        """

        from_date_frmt = f'{from_date}T00:00:00Z'
        headers = {'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'}
        url_operation = 'https://business.tinkoff.ru/openapi/api/v1/statement'

        response = await AsyncClient(proxies=PROXY6NET_PROXIES).get(
            url=url_operation,
            headers=headers,
            params={
                'accountNumber': rc_number,
                'limit': 5000,
                'from': from_date_frmt,
                'to': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
        )

        if response.status_code == 200:
            operations_list = response.json()['operations']
            result_data_list = []

            for operation in operations_list:
                cp_name = operation['counterParty']["name"]
                cp_inn = operation['counterParty']["inn"]
                type_operation = "Расход" if operation["typeOfOperation"] == "Debit" else "Доход"
                volume_operation = operation["operationAmount"]
                trxn_date = datetime.strptime(operation["trxnPostDate"], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M')
                result_data_list.append({
                    'partner_inn': cp_inn,
                    'partner_name': cp_name,
                    'op_volume': volume_operation if type_operation == "Доход" else -round(volume_operation, 2),
                    'op_type': type_operation,
                    'op_date': trxn_date,
                })

            return result_data_list
        else:
            raise Exception(f"[error]: ERROR ON API TINKOFF:\n\n {response.text}")


# if __name__ == "__main__":
#     run(Tinkoff.get_statement(
#         api_key="t.qCm87E5ocCY4ziCoXaHQQMQ-NPLdmYmWueSTdPranxqPp4YbnJnFKtmGh7rYKoGmJxHIqP9yJMB9NLqxvTHe6A",
#         rc_number=40802810100002730336,
#         from_date="2023-01-01"))