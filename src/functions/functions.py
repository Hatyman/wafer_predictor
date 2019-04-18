import pymysql.cursors
from src.classes import part_class


# Декоратор на подключение к БД
def conn_decorator(func):

    def wrapper():  # Сама обертка
        conn = pymysql.connect(host='localhost',
                               user='root',
                               password='91xz271999',
                               # password='91xz271999', НЕ УДАЛЯТЬ! НА ВСЯКИЙ СЛУЧАЙ!
                               db='sosable_v0.6',
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

        try:
            with conn.cursor() as cursor:  # Инициализируем менеджера с защитой от сбоев

                func (cursor)

        finally:  # Закрытие подключения выполнится в любом случае вконце
            conn.close()
    return wrapper


# Функция создания словаря всей партий parts_set
@conn_decorator  # Декоратор подключения к бд
def create_parts(cursor=None):
    parts_set = {}  # Словарь, который будет содержать список всех партий (ключи - их айдишники)

    sql = "SELECT * FROM `sosable_v0.6`.part"

    cursor.execute(sql)  # Запрашиваем из БД данные
    res = cursor.fetchall()  # Превращаем в удобочитаемый вид

    for row in res:  # Обходим то, что получили
        # Не работает (разобраться с присвоением переменных в методе класса), надо фиксить:
        parts_set[row['part_id']] = part_class.Part.get_other_params(row[:])  # Динамически создаем объекты партий

    print(parts_set)




