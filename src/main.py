from src.functions import functions


# Функция для сортировки пула по занчениею веса партии
def sort_by_value(part):
    return parts_set[part].value


# Функция глобальной оптимизации
def global_optimize():
    # Для возможности изменения
    global parts_set
    global machine_set
    global heap
    # Смотрим все партии, ищем мвхшные
    for item in parts_set:
        parts_set[item].update_attr()
        # Отделяем только те мвхшные партии, которых еще нет в очередях
        if (parts_set[item].part_id not in machine_set[parts_set[item].current_entity].queue) and parts_set[item].time_limit:
            # Добавляем в очередь, если установка доступна для планирования
            machine_set[parts_set[item].current_entity].queue.append(parts_set[item].part_id)
            # Ставим флаг запрета планирования
            machine_set[parts_set[item].current_entity].forbidden = True
            print('Добавлена в очередь ({5}) установки id:{0} "{1}" партия с id {2} с рецептом {3} и МВХ {4}'.format(
                machine_set[parts_set[item].current_entity].machine_id,
                machine_set[parts_set[item].current_entity].name,
                parts_set[item].part_id,
                parts_set[item].recipe_id,
                parts_set[item].time_limit,
                machine_set[parts_set[item].current_entity].queue.index(parts_set[item].part_id)
            ))
        elif (parts_set[item].part_id not in machine_set[parts_set[item].current_entity].queue) and (not parts_set[item].time_limit) and (parts_set[item].part_id not in heap):
            parts_set[item].estimate()
            heap.append(parts_set[item].part_id)

    heap.sort(key=sort_by_value, reverse=True)

    # Сначала ищем партии, у которых появится МВХ, затем распихиваем обычные
    for item in heap:
        pass


parts_set = functions.create_parts()  # Вызываем функцию создания партий
machine_set = functions.create_machines()  # Вызываем функцию создания партий
heap = []  # Пул

global_optimize()

# Тест сортировки
parts_set[14].value = 0.7
parts_set[5].value = 0.7
parts_set[8].value = 0.8
parts_set[3].value = 0.7
parts_set[3].value = 0.7
test = [14, 5, 8, 3]
print(test)
test.sort(key=sort_by_value, reverse=True)
print(test)

print(heap)




