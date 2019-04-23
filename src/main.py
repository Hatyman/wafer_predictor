from src.functions import functions
from itertools import groupby

# Функция для сортировки пула по занчениею веса партии
def sort_by_value(part):
    return parts_set[part].value


# Функция глобальной оптимизации
@functions.conn_decorator
def global_optimize(cursor=None):
    # Для возможности изменения
    global parts_set
    global machine_set
    global heap
    # Смотрим все партии, ищем мвхшные
    for item in parts_set:
        needs_to_print = False
        # Удаляем партии с предыдущих установок
        for prev_mach in parts_set[item].prev_entity:
            try:
                machine_set[prev_mach].in_queue.remove(parts_set[item].part_id)
            except ValueError:
                needs_to_print = True
        if needs_to_print:
            print("Партия id {0} {1} засиделась без места в очереди на установку {2} с id {3}".format(
                parts_set[item].part_id,
                parts_set[item].name,
                machine_set[parts_set[item].current_entity].name,
                machine_set[parts_set[item].current_entity].machine_id
            ))

        # Обновим все данные о партии
        parts_set[item].update_attr()
        # Отделяем только те мвхшные партии, которых еще нет в очередях
        if (parts_set[item].part_id not in machine_set[parts_set[item].current_entity].in_queue) and parts_set[item].time_limit:
            # Добавляем в очередь, если установка доступна для планирования
            machine_set[parts_set[item].current_entity].in_queue.append(parts_set[item].part_id)
            # Ставим флаг запрета планирования
            # machine_set[parts_set[item].current_entity].forbidden = True
            print('Добавлена в очередь ({5}) установки id:{0} "{1}" партия с id {2} с рецептом {3} и МВХ {4}'.format(
                machine_set[parts_set[item].current_entity].machine_id,
                machine_set[parts_set[item].current_entity].name,
                parts_set[item].part_id,
                parts_set[item].recipe_id,
                parts_set[item].time_limit,
                machine_set[parts_set[item].current_entity].in_queue.index(parts_set[item].part_id)
            ))
        elif (parts_set[item].part_id not in machine_set[parts_set[item].current_entity].in_queue) and (not parts_set[item].time_limit) and (parts_set[item].part_id not in heap):
            parts_set[item].estimate()
            heap.append(parts_set[item].part_id)

    heap.sort(key=sort_by_value, reverse=True)
    # Сначала ищем партии, у которых появится МВХ, затем распихиваем обычные
    tmp_heap = heap.copy()
    for item in heap:
        # print(item)
        print("Чекаем хип:", tmp_heap)
        needs_to_stop = False
        i = 0
        while not needs_to_stop:
            sql = "SELECT time_limit, machines_machines_id, recipe_id FROM `sosable_v0.6`.recipe r INNER JOIN `sosable_v0.6`.machines_has_recipe mhr ON r.recipe_id = mhr.recipe_recipe_id WHERE r.recipe_id = (SELECT `{0}` FROM `sosable_v0.6`.list WHERE list_id={1})".format(
                int(parts_set[item].act_process) + i,
                parts_set[item].list_id
            )
            cursor.execute(sql)
            res = cursor.fetchall()

            for next_mach in res:
                # print(next_mach, parts_set[item].part_id, needs_to_stop, i)
                if not next_mach['time_limit']:
                    if i:
                        machine_set[parts_set[item].current_entity].in_queue.append(item)
                        tmp_heap.remove(item)
                    else:
                        for ent in res:
                            if not machine_set[ent['machines_machines_id']].forbidden:
                                machine_set[ent['machines_machines_id']].in_queue.append(item)
                                parts_set[item].current_entity = ent['machines_machines_id']
                                tmp_heap.remove(item)
                    print("Выводим очередь на установку {0}, если партия куда-нибудь добавилась:".format(machine_set[parts_set[item].current_entity].machine_id), machine_set[parts_set[item].current_entity].in_queue)
                    needs_to_stop = True
                    break
                else:
                    min_time_queue = 999
                    ent_id = -1
                    for ent in res:
                        time_queue = 0
                        for items_queue in machine_set[ent['machines_machines_id']].in_queue:
                            time_queue += parts_set[items_queue].time_of_process
                        if (time_queue < min_time_queue) and (not machine_set[ent['machines_machines_id']].forbidden):
                            ent_id = ent['machines_machines_id']
                            min_time_queue = time_queue
                            # print(parts_set[item].part_id, min_time_queue, ent_id)
                    if ent_id > 0:
                        if not i:
                            parts_set[item].current_entity = ent_id
                        machine_set[ent_id].forbidden = True
                        print("Машина {0} c id {1} заблокирована для партии {2} c id {3}".format(
                            machine_set[ent_id].name,
                            ent_id,
                            parts_set[item].name,
                            parts_set[item].part_id
                        ))
                    else:
                        needs_to_stop = True
                    i += 1
                    break
            # Раскомментируй строку ниже, если хочешь посмотреть что выдает и как работает цикл!!!!!!!!!!!!!!!!!!
            # print(res, parts_set[item].part_id, needs_to_stop, i)
    heap = tmp_heap.copy()

parts_set = functions.create_parts()  # Вызываем функцию создания партий
machine_set = functions.create_machines()  # Вызываем функцию создания партий
heap = []  # Пул

# Тест сортировки
parts_set[14].value = 0.7
parts_set[5].value = 0.7
parts_set[8].value = 0.8
parts_set[3].value = 0.7
parts_set[10].value = 0.2
# test = [14, 3, 8, 5, 10]
# print(test)
# test.sort(key=sort_by_value, reverse=True)
# print(test)
global_optimize()
print('-----')
# print(machine_set[3].queue)
# print(machine_set[3].forbidden)
# print(parts_set[14].current_entity)
# print(parts_set[14].time_limit)
