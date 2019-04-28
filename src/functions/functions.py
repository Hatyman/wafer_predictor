import pymysql.cursors


# Функция подключения к бд
def connection(pwd='91xz271999'):
    # Подключение к бд убрали в обёртку (можно еще продублировать в файл отдельный как функцию)
    connect = pymysql.connect(host='localhost',
                              user='root',
                              password=pwd,
                              # password='91xz271999',
                              db='sosable_v0.6',
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

    sql = "SELECT * FROM `sosable_v0.6`.part"
    cursor.execute(sql)  # Запрашиваем из БД данные
    res = cursor.fetchall()  # Превращаем в удобочитаемый вид

    for row in res:  # Обходим то, что получили
        # Не работает (разобраться с присвоением переменных в методе класса), надо фиксить:
        part_id, name, list_id, act_process, queue, reserve, wait, recipe_id = row
        # Динамически создаем объекты партий
        inner_parts_set[row['part_id']] = part_class.Part(row[part_id], row[name], row[list_id], row[act_process],
                                                          row[queue], row[reserve], row[wait], row[recipe_id])

    return inner_parts_set


@conn_decorator
def create_machines(cursor=None):
    from src.classes import machine_class
    inner_machines_set = {}  # Словарь, который будет содержать список всех партий (ключи - их айдишники)

    sql = "SELECT * FROM `sosable_v0.6`.machines"
    cursor.execute(sql)  # Запрашиваем из БД данные
    res = cursor.fetchall()  # Превращаем в удобочитаемый вид

    for row in res:  # Обходим то, что получили
        # Не работает (разобраться с присвоением переменных в методе класса), надо фиксить:
        # Динамически создаем объекты партий
        inner_machines_set[row['machines_id']] = machine_class.Machine(row['machines_id'], row['work_stream_number'],
                                                                       row['broken'])
    return inner_machines_set


def local_optimization(machines_set, part_set):
    for machine in machines_set:
        machines_set[machine].local_optimizer(part_set)
