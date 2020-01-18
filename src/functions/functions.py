import pymysql.cursors
import sys


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
                dict = func(cursor, conn)
        except Exception as e:
            print(str(e))
            print(sys.exc_info())
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

                func(self, cursor, conn)
        # except Exception as e:
        #     print(str(e))
        #     print(sys.exc_info())
        finally:  # Закрытие подключения выполнится в любом случае вконце
            conn.close()

    return wrapper


# Функция создания словаря всей партий parts_set
@conn_decorator  # Декоратор подключения к бд
def create_parts(cursor=None, conn=None):
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
def create_machines(cursor=None, conn=None):
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


def setting_current_entity(machine_set, parts_set):
    for part in parts_set:
        part.update_attr()
        _, index = min((ent.len_queue, index) for index, ent in enumerate(machine_set) if
                       ent.machine_id in part.current_entity_list)
        machine_set[index].add_part_to_queue(part)
        part.set_current_entity(machine_set[index])


def setting_next_entity(machine_set, parts_set):
    for part in parts_set:
        part.update_attr()
        _, index = min((ent.len_queue, index) for index, ent in enumerate(machine_set) if
                       ent.machine_id in part.next_entity_list)
        part.set_next_entity(machine_set[index])


# # Функция для получения доступа к данным об установках и выбор установки для партии с наименьшей очередью
# def setting_next_entity(machine_set, parts_set):
#     for key, val in machine_set.items():
#         val.get_len_queue()
#     for part in parts_set:
#         parts_set[part].get_next_entity()  # Получаем/обновляем список установок: куда дальше идти
#         min_queue = 999
#         next_id = 0
#         for ent in parts_set[part].next_entity_list:  # Перебираем все установки, куда мы можем пойти (учитывать флаг запрета???)
#             if machine_set[ent].len_queue < min_queue and (not machine_set[ent].forbidden):
#                 next_id = ent
#                 min_queue = machine_set[ent].len_queue
#         if next_id:
#             parts_set[part].set_next_entity(machine_set[next_id])
#             # parts_set[part].set_next_entity(next_id)   Записываем номер найденной установки в свойство


# Функция для вычисления ценности всех партий, которые находятся в установках
def calculate_entity_queue_gain(machine_set, parts_set):
    for machine in machine_set:
        machine_set[machine].parse_out_queue(machine_set, parts_set)


@conn_decorator
def allow_for_planing(cursor=None, conn=None):
    sql = "SELECT flag_optimization FROM `production`.communication"
    cursor.execute(sql)
    res = cursor.fetchall()
    flag = res[0]['flag_optimization']
    return flag


def update_part_info(machine_set, parts_set):
    for part in parts_set:
        part.update_attr(machine_set)
        try:
            if not part.wait:
                part.current_entity.out_queue[0].remove(part.part_id)
                if not len(part.current_entity.out_queue[0]):
                    part.current_entity.out_queue.remove([])

        except ValueError:
            pass


@conn_decorator
def disable_for_planing(cursor=None, conn=None):
    cursor.callproc("flagdown")
    conn.commit()


def send_queue_db(part_set):
    for id_part in part_set:
        part_set[id_part].send_queue()


def flag(machine_set, parts_set, item):
    flag = True
    for group in machine_set[parts_set[item].current_entity].out_queue:
        for part in group:
            if item == part:
                flag = False
    return flag
