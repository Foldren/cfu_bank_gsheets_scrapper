import traceback
from datetime import datetime, timedelta
from banks_services.tinkoff import Tinkoff
from config import BANKS_RUS_NAMES
from init_models import User, Category, PaymentAccount


async def get_loop_interval_to_four_hour():
    """
    Функция для получения интервала запуска, с отсчетом от
    текущего времени до 4 часов утра следующего дня

    :return:
    """
    current_datetime = datetime.now()
    config_reload_datetime = current_datetime + timedelta(days=1)
    next_reload_datetime = datetime(
        year=config_reload_datetime.year,
        month=config_reload_datetime.month,
        day=config_reload_datetime.day,
        hour=4
    )

    new_loop_interval_time = (next_reload_datetime - current_datetime).total_seconds()

    return new_loop_interval_time


async def get_queue_categories_list_by_cat_id(category_id: int):
    """
    Функция для получения очереди категории, при помощи получения родителей через prefetch_related

    :param category_id: id категории
    :return:
    """

    parent = await Category.get(id=category_id).prefetch_related()
    categories_names_list = []

    while parent is not None:
        categories_names_list.append(parent.name)
        parent = await parent.parent

    categories_names_list.reverse()

    return categories_names_list


async def get_payment_account_statement(payment_account: PaymentAccount) -> list:
    bank = await payment_account.bank

    # Фиксируем дату, с которой нужно начать подгрузку операций из выписок
    if payment_account.last_date_reload_statement is None:
        from_date = payment_account.first_date_load_statement
    else:
        from_date = payment_account.last_date_reload_statement

    statements = None
    match bank.bank_name:
        case 'tinkoff':
            statements = await Tinkoff.get_statement(
                api_key=bank.api_key,
                rc_number=payment_account.number,
                from_date=from_date,
            )
        case 'module':
            pass
        case 'tochka':
            pass

    # Меняем дату последней подгрузки на сегодня
    payment_account.last_date_reload_statement = datetime.now().date()
    await payment_account.save()

    return statements


async def generate_list_gts_statements_rows() -> list:
    """
    Основная функция, для генерации списка строк с операциями,
    которые нужно будет добавлять в гугл таблицы пользователей

    :return:
    """

    admins = await User.filter(admin_id=None).all()
    admins_rows_in_gts = []

    for admin in admins:
        # Шаг 1: генерируем список категорий, к которым прикреплены Инн контрагентов -----------------------------------
        # (для сравнения с операциями из банков)
        admin_partners = await admin.admin_partners.all().exclude(bank_reload_category_id=None)

        partners_inn_list = []
        partners_names_list = []
        partners_category_queue_list = []
        for partner in admin_partners:
            partner_bank_reload_category = await partner.bank_reload_category
            cat_queue = await get_queue_categories_list_by_cat_id(partner_bank_reload_category.id)
            partners_inn_list.append(partner.inn)
            partners_category_queue_list.append(cat_queue)
            partners_names_list.append(partner.name)

        # Шаг 2: Генерируем список строк которые нужно будет добавить в таблицу админа ---------------------------------
        admin_banks = await admin.admin_banks.all()

        rows_to_write_in_gt = []
        for bank in admin_banks:
            bank_payment_accounts = await bank.payment_accounts.all()

            for payment_account in bank_payment_accounts:
                try:
                    # Если расчетный счет помечен как активный
                    if payment_account.status == 1:
                        bank_stats_operations = await get_payment_account_statement(payment_account)
                        payment_account_organization = await payment_account.organization.first()
                        organization_name = payment_account_organization.name

                        print(bank_stats_operations)

                        for operation in bank_stats_operations:
                            # Проверяем привязана ли организация внутри бота, если да, привязываем очередь категории
                            if operation['partner_inn'] in partners_inn_list:
                                index_partner_in_lists = partners_inn_list.index(operation['partner_inn'])
                                category_queue = partners_category_queue_list[index_partner_in_lists]

                                row_to_write_in_gt = [
                                    'Нет chat_id',
                                    partners_names_list[index_partner_in_lists],
                                    operation['op_date'],
                                    operation['op_type'],
                                    BANKS_RUS_NAMES[bank.bank_name],
                                    operation['op_volume'],
                                    organization_name,
                                ]

                                # Дополняем строку категориями из очереди
                                category_numbs = 0
                                for category in category_queue:
                                    category_numbs += 1
                                    row_to_write_in_gt.append(category)

                            else:
                                row_to_write_in_gt = [
                                    'Нет chat_id',
                                    operation['partner_name'],
                                    operation['op_date'],
                                    operation['op_type'],
                                    BANKS_RUS_NAMES[bank.bank_name],
                                    operation['op_volume'],
                                    organization_name,
                                    'Без распределения'
                                ]
                                category_numbs = 1

                            # Заполняем оставшиеся поля пустыми строками
                            for i2 in range(category_numbs, 5):
                                row_to_write_in_gt.append("")

                            # Добавляем инн контрагента в последний столбец
                            row_to_write_in_gt.append(operation['partner_inn'])

                            rows_to_write_in_gt.append(row_to_write_in_gt)
                except Exception:
                    continue

        # Шаг 3: Добавляем список таблиц и ссылку на таблицу админа в результат ----------------------------------------
        admin_info = await admin.admin_info.all()

        if rows_to_write_in_gt:
            admins_rows_in_gts.append({
                'gt_table_url': admin_info.google_table_url,
                'rows_to_add_in_bd': rows_to_write_in_gt
            })

    return admins_rows_in_gts

