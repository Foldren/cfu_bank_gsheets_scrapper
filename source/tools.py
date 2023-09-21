from datetime import datetime, timedelta
from source.banks_services.tinkoff import Tinkoff
from source.config import BANKS_RUS_NAMES
from source.init_models import User, Category, AdminBank


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


async def get_user_bank_statement(bank: AdminBank, from_date) -> list:
    match bank.name:
        case 'tinkoff':
            return await Tinkoff.get_statement(
                api_key=bank.api_key,
                rc_number=bank.number_or_name_account,
                from_date=from_date,
            )
        case 'module':
            pass
        case 'tochka':
            pass


async def write_operations_list_in_bd_users():
    """
    Основная функция, для генерации списка строк с операциями,
    которые нужно будет добавлять в гугл таблицы пользователей

    :return:
    """

    admins = await User.filter(admin_id=None).all()
    admins_rows_in_gts = []

    for admin in admins:
        # Шаг 1: генерируем список категорий, к которым прикреплены Инн организаций ------------------------------------
        # (для сравнения с операциями из банков)
        admin_orgs = await admin.admin_organizations.all().exclude(bank_reload_category_id=None)

        organizations_inn_list = []
        organizations_cat_queue_list = []
        for org in admin_orgs:
            org_reload_category = await org.bank_reload_category
            cat_queue = await get_queue_categories_list_by_cat_id(org_reload_category.id)
            organizations_inn_list.append(org.inn)
            organizations_cat_queue_list.append(cat_queue)

        # Шаг 2: Генерируем список строк которые нужно будет добавить в таблицу админа ---------------------------------
        admin_banks = await admin.admin_banks.all()

        rows_to_write_in_gt = []
        for bank in admin_banks:
            if bank.status == 1:
                from_date = bank.first_date_load_statement if bank.last_date_reload_statement is None \
                    else bank.last_date_reload_statement
                bank_stats_operations = await get_user_bank_statement(bank, from_date)

                for operation in bank_stats_operations:
                    # Проверяем привязана ли организация внутри бота, если да, привязываем очередь категории
                    if operation['org_inn'] in organizations_inn_list:
                        index_org_in_lists = organizations_inn_list.index(operation['org_inn'])
                        category_queue = organizations_cat_queue_list[index_org_in_lists]

                        row_to_write_in_gt = [
                            'Нет chat_id',
                            operation['org_name'],
                            operation['op_date'],
                            operation['op_type'],
                            BANKS_RUS_NAMES[bank.name],
                            operation['volume'],
                            operation['org_name'],
                        ]

                        # Дополняем строку категориями из очереди
                        for category in category_queue:
                            row_to_write_in_gt.append(category)
                    else:
                        row_to_write_in_gt = [
                            'Нет chat_id',
                            operation['org_name'],
                            operation['op_date'],
                            operation['op_type'],
                            BANKS_RUS_NAMES[bank.name],
                            operation['op_volume'],
                            operation['org_name'],
                            'Без распределения'
                        ]
                    rows_to_write_in_gt.append(row_to_write_in_gt)

        # Шаг 3: Добавляем список таблиц и ссылку на таблицу админа в результат ----------------------------------------
        admin_info = await admin.admin_info.all()
        admins_rows_in_gts.append({
            'gt_table_url': admin_info.google_table_url,
            'rows_to_add_in_bd': rows_to_write_in_gt
        })

    print(admins_rows_in_gts)

    return admins_rows_in_gts

