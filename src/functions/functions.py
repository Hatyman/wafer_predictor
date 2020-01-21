import pymysql.cursors
import sys
import numpy as np


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


def local_optimization(machines_set):
    """
    Функция запускает оптимизацию очередей для каждой установки.
    В итоге у каждой установки в поле out_queue будет список вида:
    [[PART1 - партия, PART2, PART3 ...] - группа партий, [...] ...] - очередь на установку.

    :param machines_set: Массив доступных установок
    """
    for machine in machines_set:
        machines_set[machine].local_optimizer()


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
    """
    Функция обновляет данные из базы. Здесь обновляются списки установок для текущего и следующего шагов,
    выполняется ли партия в установке, id рецепта, шаг по маршрутному листу, время выполнения текущего
    рецепта, МВХ (если есть) и номер в очереди на установку. Также рассчитывается целевая функция.

    Затем идёт выбор текущей (и сразу добавляется в очередь) и последующей установки из
    полученных из базы списков исходя из минимальных очередей.

    В случае, если партия зашла в установку, она удаляется из текущей очереди,
    номер в очереди устанавливается на None и обновляется база данных.

    :param machine_set: Массив доступных установок
    :param parts_set: Массив доступных партий
    """
    for part in parts_set:
        part.update_attr()  # Обновляем данных из БД.
        # Выбираем следующую установку с наименьшей очередью.
        _, index = min((ent.len_queue, index) for index, ent in enumerate(machine_set) if
                       ent.machine_id in part.next_entity_list)
        # Записываем соответствующую установку в поле объекта.
        part.set_next_entity(machine_set[index])
        try:
            # Если партия зашла в установку, она удаляется из текущей очереди,
            # номер в очереди устанавливается на None и обновляется база данных.
            if not part.wait:
                # Обновление номера очереди в программе и в БД.
                part.reset_queue()
                part.queue = None
                # Удаление партии из очереди.
                part.current_entity.out_queue[0].remove(part)
                # (Защита) Если партий в группе не осталось, удаляем группу.
                if not len(part.current_entity.out_queue[0]):
                    part.current_entity.out_queue.remove([])
        except ValueError:
            pass
        # Если партия уже не в установке, но номер в очереди None и партии нет в очереди текущей установки,
        # то меняем текущую установку на полученную из бд из соображения минимальной очереди.
        if part.wait and part.queue is None and part not in np.reshape(part.current_entity.out_queue, -1):
            _, index = min((ent.len_queue, index) for index, ent in enumerate(machine_set) if
                           ent.machine_id in part.current_entity_list)
            # Добавляем партию во временную (ноптимизированную) чередь на установку.
            machine_set[index].add_part_to_queue(part)
            # Записываем соответствующую установку в поле объекта.
            part.set_current_entity(machine_set[index])


@conn_decorator
def disable_for_planing(cursor=None, conn=None):
    cursor.callproc("flagdown")
    conn.commit()


def send_queue_db(part_set):
    for part in part_set:
        part.send_queue()


def flag(machine_set, parts_set, item):
    flag = True
    for group in machine_set[parts_set[item].current_entity].out_queue:
        for part in group:
            if item == part:
                flag = False
    return flag
