import pymysql.cursors


# Функция подключения к бд
def connection(pwd='91xz271999'):
    # Подключение к бд убрали в обёртку (можно еще продублировать в файл отдельный как функцию)
    connect = pymysql.connect(host='localhost',
                              user='root',
                              password=pwd,
                              # password='91xz271999',
                              db='production',
                              charset='utf8mb4',
                              cursorclass=pymysql.cursors.DictCursor)
    return connect


# Декоратор на подключение к БД для функций
def conn_decorator(func):
    def wrapper():  # Сама обертка
        try:
            conn = connection()  # На вход передавать пароль для бд (по умолчанию будет 91xz271999)
        except pymysql.err.OperationalError:
            conn = connection('')

        try:
            with conn.cursor() as cursor:  # Инициализируем менеджера с защитой от сбоев
                dict = {}
                dict = func(cursor)

        finally:  # Закрытие подключения выполнится в любом случае вконце
            conn.close()
            return dict

    return wrapper


# Декоратор на подключение к БД для методов
def conn_decorator_method(func):
    def wrapper(self):  # Сама обертка
        try:
            conn = connection()  # На вход передавать пароль для бд (по умолчанию будет 91xz271999)
        except pymysql.err.OperationalError:
            conn = connection('')

        try:
            with conn.cursor() as cursor:  # Инициализируем менеджера с защитой от сбоев

                func(self, cursor)

        finally:  # Закрытие подключения выполнится в любом случае вконце
            conn.close()

    return wrapper


# Функция создания словаря всей партий parts_set
@conn_decorator  # Декоратор подключения к бд
def create_parts(cursor=None):
    from src.classes import part_class
    inner_parts_set = {}  # Словарь, который будет содержать список всех партий (ключи - их айдишники)

    sql = "SELECT * FROM `production`.part"
    cursor.execute(sql)  # Запрашиваем из БД данные
    res = cursor.fetchall()  # Превращаем в удобочитаемый вид

    for row in res:  # Обходим то, что получили
        # Не работает (разобраться с присвоением переменных в методе класса), надо фиксить:
        part_id, name, list_id, act_process, queue, reserve, wait, recipe_id, priority = row
        # Динамически создаем объекты партий
        inner_parts_set[row['part_id']] = part_class.Part(row[part_id], row[name], row[list_id], row[act_process],
                                                          row[queue], row[reserve], row[wait], row[recipe_id],
                                                          row[priority])

    return inner_parts_set


@conn_decorator
def create_machines(cursor=None):
    from src.classes import machine_class
    inner_machines_set = {}  # Словарь, который будет содержать список всех партий (ключи - их айдишники)

    sql = "SELECT * FROM `production`.machines"
    cursor.execute(sql)  # Запрашиваем из БД данные
    res = cursor.fetchall()  # Превращаем в удобочитаемый вид

    for row in res:  # Обходим то, что получили
        # Не работает (разобраться с присвоением переменных в методе класса), надо фиксить:
        # Динамически создаем объекты партий
        inner_machines_set[row['machines_id']] = machine_class.Machine(row['machines_id'], row['work_stream_number'],
                                                                       row['broken'])
    return inner_machines_set


def local_optimization(machines_set, part_set):  # Функция нужна для передачи в методы каждой
    for machine in machines_set:  # машины сет партий и запуске в глобальном файле
        machines_set[machine].local_optimizer(part_set)


# Функция для получения доступа к данным об установках и выбор установки для партии с наименьшей очередью
def setting_next_entity(machine_set, parts_set):
    for key, val in machine_set.items():
        val.get_len_queue()
    for part in parts_set:
        parts_set[part].get_next_entity()  # Получаем/обновляем список установок: куда дальше идти
        min_queue = 999
        next_id = 0
        for ent in parts_set[part].next_entity_list:  # Перебираем все установки, куда мы можем пойти (учитывать флаг запрета???)
            if machine_set[ent].len_queue < min_queue and (not machine_set[ent].forbidden):
                next_id = ent
                min_queue = machine_set[ent].len_queue
        if next_id:
            parts_set[part].set_next_entity(next_id)  # Записываем номер найденной установки в свойство


# Функция для вычисления ценности всех партий, которые находятся в установках
def calculate_entity_queue_gain(machine_set, parts_set):
    for machine in machine_set:
        machine_set[machine].parse_out_queue(machine_set, parts_set)


@conn_decorator
def allow_for_planing(cursor=None):
    sql = "SELECT flag_optimizatiion FROM `production`.communication"
    cursor.execute(sql)
    res = cursor.fetchall()
    flag = res[0]['flag_optimizatiion']
    return flag
