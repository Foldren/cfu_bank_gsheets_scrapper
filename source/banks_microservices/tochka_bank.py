import json
from asyncio import run
from datetime import datetime, timedelta
from httpx import AsyncClient
from config import PROXY6NET_PROXIES


class TochkaBank:
    @staticmethod
    async def get_statement(api_key: str, rc_number: int, from_date: str) -> list:
        """
        Функция для получения выписок по счету в Точка банке от заданной даты до текущего времени

        :param api_key: апи ключ клиентского Точка банка
        :param rc_number: номер расчетного счета клиента
        :param from_date: дата начала периода отгрузки выписки (в формате 2023-07-13)
        """

        from_date_frmt = f'{from_date}T00:00:00Z'
        headers = {'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'}
        url_operation = 'https://enter.tochka.com/uapi/open-banking/v1.0/accounts'

        async with AsyncClient(proxies=PROXY6NET_PROXIES) as async_session:
            # Получаем информацию о компании ---------------------------------------------------------------------------
            r_company_info = await async_session.get(
                url=url_operation,
                headers=headers
            )

            if r_company_info.status_code != 200:
                raise Exception(f"[error]: ERROR ON API TOCHKA:\n\n {r_company_info.text}")

            r_company_accounts = r_company_info.json()['Data']['Account']
            account_id = ""

            # Берем account_id по указанному расчётному счёту ----------------------------------------------------------
            for a in r_company_accounts:
                if a['accountId'].split("/")[0] == str(rc_number):
                    account_id = a['accountId']
                    break

            # Создаем выписку за требуемый период ----------------------------------------------------------------------
            r_company_init_statement = await async_session.post(
                url="https://enter.tochka.com/uapi/open-banking/v1.0/statements",
                headers=headers,
                json={
                    'Data': {
                        'Statement': {
                            'accountId': account_id,
                            'startDateTime': str(from_date),
                            'endDateTime': str(datetime.now().strftime("%Y-%m-%d")),
                        }
                    },
                }
            )
            print(r_company_init_statement.json())


        # Получаем выписки, так как ограничение стоит на 5000 делаем это со смещением даты пока не выведем все ---------
        result_operations_list = []
        till_date_next = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        last_operations = []
        # while True:
        #     r_operations = await AsyncClient(proxies=PROXY6NET_PROXIES).get(
        #         url=url_operation,
        #         headers=headers,
        #         params={
        #             'accountNumber': rc_number,
        #             'limit': 5000,
        #             'from': str(from_date_frmt),
        #             'to': str(till_date_next),
        #         }
        #     )

        #     if r_operations.status_code != 200:
        #         raise Exception(f"[error]: ERROR ON API TINKOFF:\n\n {r_operations.text}")
        #
        #     r_operations_list = r_operations.json()['operations']
        #
        #     if last_operations == r_operations_list:
        #         break
        #
        #     index_last_operation = len(r_operations_list) - 1
        #     till_date_next = str(r_operations_list[index_last_operation]['trxnPostDate'])
        #     result_operations_list += r_operations_list
        #     last_operations = r_operations_list
        #
        # result_data_list = []
        # for operation in result_operations_list:
        #     cp_name = operation['counterParty']["name"]
        #     cp_inn = operation['counterParty']["inn"]
        #     type_operation = "Расход" if operation["typeOfOperation"] == "Debit" else "Доход"
        #     volume_operation = operation["operationAmount"]
        #     trxn_date = datetime.strptime(operation["trxnPostDate"], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y %H:%M')
        #     result_data_list.append({
        #         'partner_inn': cp_inn,
        #         'partner_name': cp_name,
        #         'op_volume': volume_operation if type_operation == "Доход" else -round(volume_operation, 2),
        #         'op_type': type_operation,
        #         'op_date': trxn_date,
        #     })
        #
        # return result_data_list


if __name__ == "__main__":
    run(TochkaBank.get_statement(
        api_key="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJUOWxiMlJoOFVjaFBoZWlvOUxzRjF2eWpNeXJaN3YxRyJ9.kX2lBukqa1IBPjlP4qzjs0U45Hspfg8Tg8I-QuffDome_VmtfyPv4hA0GENixs2JGMuerAmEM8iOzmeHeVedhcizEB72UWfB3OYugd8FAT36r3stOOF74EU3em9N-iSEJVJI5NfjoUkc7S1QpLhPdDB1ltYGHb1HUNFiprSPf2WKUdwA0hDkXJsBdq2_fPVR6domf6ZTBylC3pC7HDsQWuP5ab38sMUjxyZ2OF-3DDjO5AeP-nU54M_l82RF43sjm-FUkhdBoVmruOLnqTBg6jDmY7mroNfBWM12i7i7D-OgCnmD9wKWzflSh-Pp-_v46f62LhAqpXlWHxaL2XRyDCjCVOixwYPIHbMdSUCp66kVyaT237yAUEwKedo2Dh5mkD0G16Ylwz-kP1uAxce-xpd1-CJqW-ln1lnres39qPfwyY-HXd9siv68-T4cGkf22LXiWAECrs-RXNiFSFlXQmCq4PxqNBWI_gNf9n_sDzE98HN2BWG_VLWT7lHzgY9e",
        rc_number=40802810014500047652,
        from_date="2023-01-01"))
