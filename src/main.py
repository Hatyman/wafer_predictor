import sys
import time

from src.functions.functions import *

@conn_decorator
def get_recipes_id(cursor=None, conn=None):
    machine = ['DGF01A', 'DGF01B', 'DGF01C', 'EOX092', 'EOX093', 'EOX094', 'DBP010',
               'DBP01A', 'DBP01B', 'DON01A', 'DON01B', 'DON01C', 'DON01D', 'EOX021', 'EOX022',
               'EPN011', 'EPN012', 'EPN013', 'EPN014', 'MSP011', 'MSP012', 'MSP013', 'MSP014',
               'MSP01C', 'MSP01D', 'MSP022', 'MSP023', 'MTU01A', 'MTU01B']
    sql = "SELECT * FROM machines_has_recipe WHERE machines_machines_id IN (SELECT machines_id FROM machines WHERE work_stream_number IN ("

    sql_mach = "SELECT machines_id, work_stream_number FROM machines WHERE work_stream_number IN ("

    for name in machine:
        sql += f"'{name}', "
        sql_mach += f"'{name}', "

    sql = sql[:-2] + "))"
    sql_mach = sql_mach[:-2] + ")"

    cursor.execute(sql)
    res = cursor.fetchall()

    cursor.execute(sql_mach)
    machines = cursor.fetchall()

    print(res)
    print(machines)

    for mach in machines:
        mach['recipes_id'] = [list(dic.values())[1] for dic in res if list(dic.values())[0] == mach['machines_id']]

    print(machines)

    max_len = max(len(dic['recipes_id']) for dic in machines)

    print(max_len)

    arr = "["
    machi = "["

    for mach in machines:
        i = 0
        machi += f"'{mach['work_stream_number']}'; "
        for rec_id in mach['recipes_id']:
            i += 1
            arr += f"{rec_id} "
        for counter in range(i, 8):
            arr += "0 "
        arr = arr[:-1] + '; '
    arr = arr[:-2] + '];'
    machi = machi[:-2] + '];'

    print(arr)
    print(machi)

# get_recipes_id()
# exit(1)

prepare_bd()
parts_set = create_parts()  # Вызываем функцию создания партий
machine_set = create_machines()  # Вызываем функцию создания партий
while True:
    t1 = time.clock()  # Время начала планирования (для замера времени работы планировкщика)
    update_part_info(machine_set, parts_set)  # Обновление всех параметров партий
    local_optimization(machine_set)  # Работа с очередями
    send_queue_db(parts_set)  # Отправка очередей
    disable_for_planing()  # Выставляем флаг для работы модели
    t2 = time.clock() - t1  # Замер времени
    print(t2)
