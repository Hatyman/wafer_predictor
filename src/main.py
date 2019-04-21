from src.functions import functions


# Функция глобальной оптимизации
def global_optimize():
    # Для возможности изменения
    global parts_set
    global machine_set
    # Смотрим все партии, ищем мвхшные
    for item in parts_set:  
        parts_set[item].update_attr()
        # Отделяем только те мвхшные партии, которых еще нет в очередях
        if (parts_set[item].part_id not in machine_set[parts_set[item].current_entity].queue) and parts_set[item].time_limit and (not machine_set[parts_set[item].current_entity].forbidden):
            # Добавляем в очередь, если установка доступна для планирования
            machine_set[parts_set[item].current_entity].queue.append(parts_set[item].part_id)
            # Ставим флаг запрета планирования
            machine_set[parts_set[item].current_entity].forbidden = True
            print('Добавлена в очередь ({5}) установки id:{0} "{1}" партия с id {2} с рецептом {3} и МВХ {4}'.format(machine_set[parts_set[item].current_entity].machine_id, machine_set[parts_set[item].current_entity].name, parts_set[item].part_id, parts_set[item].recipe_id, parts_set[item].time_limit, machine_set[parts_set[item].current_entity].queue.index(parts_set[item].part_id)))


parts_set = functions.create_parts()  # Вызываем функцию создания партий
machine_set = functions.create_machines()  # Вызываем функцию создания партий

global_optimize()



