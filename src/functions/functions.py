import pymysql.cursors
from src.classes import part_class


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
        conn = connection('')  # На вход передавать пароль для бд (по умолчанию будет 91xz271999)

        try:
            with conn.cursor() as cursor:  # Инициализируем менеджера с защитой от сбоев

                dict = func (cursor)

        finally:  # Закрытие подключения выполнится в любом случае вконце
            conn.close()
            return dict
    return wrapper


# Декоратор на подключение к БД для методов
def conn_decorator_method(func):

    def wrapper(self):  # Сама обертка
        conn = connection('')  # На вход передавать пароль для бд (по умолчанию будет 91xz271999)

        try:
            with conn.cursor() as cursor:  # Инициализируем менеджера с защитой от сбоев

                func (self, cursor)

        finally:  # Закрытие подключения выполнится в любом случае вконце
            conn.close()
    return wrapper


# Функция создания словаря всей партий parts_set
@conn_decorator  # Декоратор подключения к бд
def create_parts(cursor=None):
    inner_parts_set = {}  # Словарь, который будет содержать список всех партий (ключи - их айдишники)

    sql = "SELECT * FROM `sosable_v0.6`.part"
    cursor.execute(sql)  # Запрашиваем из БД данные
    res = cursor.fetchall()  # Превращаем в удобочитаемый вид

    for row in res:  # Обходим то, что получили
        # Не работает (разобраться с присвоением переменных в методе класса), надо фиксить:
        part_id, name, list_id, act_process, queue, reserve, wait, recipe_id = row
        # Динамически создаем объекты партий
        inner_parts_set[row['part_id']] = part_class.Part(row[part_id], row[name], row[list_id], row[act_process], row[queue], row[reserve], row[wait], row[recipe_id])

    return inner_parts_set




