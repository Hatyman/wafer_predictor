from src.functions import functions
import numpy as np


# Завтра еще подредачу, не помню что еще нужно добавить
class Machine:
    # Конструктор установок
    def __init__(self, machine_id, name, broken):
        self.machine_id = machine_id
        self.name = name
        self.in_queue = []
        self.broken = broken
        self.recipe_id = 0
        self.forbidden = False
        self.who_forbidden = ""
        self.endQueue = 0
        self.len_queue = 0
        self.out_queue = [[]]
        self.group_values = []
        self.recipes_count = None
        self.get_groups()
        print('Создана установка с id: {0}, recipe_id: {1} '
              'name: {2}'.format(self.machine_id, self.recipe_id, self.name))

    # Функция получения рецепта на установке, если мы будем цеплять его с бд (бд надо доработать)
    @functions.conn_decorator_method
    def get_recipe(self, cursor=None, conn=None):
        sql = "SELECT recipe_on FROM `production`.machines WHERE machine_id = {0}".format(self.machine_id)
        cursor.execute(sql)
        result = cursor.fetchone()
        self.recipe_id = result['recipe_on']

    # Функция изменения рецепта на установку по первой партии в очереди
    def set_recipe(self, part_set):
        self.recipe_id = part_set[self.in_queue[0][0]].recipe_id
        print('Установлен рецепт: {0} на установке: {1}'.format(self.recipe_id, self.machine_id))

    def forbid(self):
        self.forbidden = not self.forbidden

    @functions.conn_decorator_method
    def get_groups(self, cursor=None, conn=None):
        sql = "SELECT count(machines_has_recipe.recipe_recipe_id) FROM `production`." \
              "machines_has_recipe WHERE machines_machines_id = {0};".format(self.machine_id)
        cursor.execute(sql)
        self.recipes_count = cursor.fetchone()
        self.recipes_count = self.recipes_count['count(machines_has_recipe.recipe_recipe_id)']

    # Группировка партий по рецептам

    # def group_recipe(self, part_set):
    #     group_values = []  # Список средней ценности всей группы
    #     grouped_queue = []  # Сгруппированная очередь
    #     group_has_values = {}  # Словарь для сопоставления группы партий и их ценности
    #     amount_of_grouped = 0  # Количество сгруппированных партий
    #     if len(self.in_queue) > 1:  # Группировка будет, только в случае если у нас есть что группировать
    #         for i in range(self.recipes_count):  # Устанавлеваем порядок очереди по количеству возможных групп
    #             value = part_set[self.in_queue[amount_of_grouped]].value
    #             group = []
    #             for j in self.in_queue:
    #                 if part_set[self.in_queue[amount_of_grouped]].recipe_id == part_set[j].recipe_id:
    #                     group.append(j)
    #                     amount_of_grouped += 1
    #                     value += part_set[j].value
    #             mean_value = value / amount_of_grouped
    #             if len(group) > 1:  # Если группа состоит не из одной партии, то переставляем также партии в группах
    #                 grouped_queue.append(self.transposition(part_set, group))
    #                 self.in_queue = grouped_queue.copy()
    #             else:  # Иначе просто идем дальше
    #                 self.in_queue = grouped_queue.append(group)
    #             group_values.append(mean_value)
    #             if len(self.in_queue) <= amount_of_grouped:
    #                 break
    #         group_has_values = dict.fromkeys(group_values)
    #         count = 0
    #         for k in group_values:  # Заполняем словарь соответствия ценности групп к самим группам
    #             group_has_values[k] = self.in_queue[count].copy()
    #             count += 1
    #     elif len(self.in_queue) == 1:
    #         # Если очередь состоит из одной партии, то толкаем ее в конец спланированной очереди
    #         insert = self.in_queue.copy()
    #         self.in_queue[0] = insert
    #         group_values.append(part_set[self.in_queue[0][0]].value)
    #         group_has_values[part_set[self.in_queue[0][0]].value] = self.in_queue.copy()
    #
    #     return group_values, group_has_values

    # def group_recipe(self, part_set):
    #     group_values = []  # Список средней ценности всей группы
    #     grouped_queue = []  # Сгруппированная очередь
    #     group_has_values = {}  # Словарь для сопоставления группы партий и их ценности
    #     amount_of_grouped = 0  # Количество сгруппированных партий
    #     if len(self.in_queue) > 1:  # Группировка будет, только в случае если у нас есть что группировать
    #         for i in range(self.recipes_count):  # Устанавлеваем порядок очереди по количеству возможных групп
    #             values = []
    #             group = []
    #             for j in self.in_queue:
    #                 if part_set[self.in_queue[amount_of_grouped]].recipe_id == part_set[j].recipe_id:
    #                     group.append(j)
    #                     amount_of_grouped += 1
    #                     values.append(part_set[j].target_function)
    #             # mean_value = value / amount_of_grouped
    #             max_value = max(values)
    #             if len(group) > 1:  # Если группа состоит не из одной партии, то переставляем также партии в группах
    #                 grouped_queue.append(self.transposition(part_set, group))
    #                 self.in_queue = grouped_queue.copy()
    #             else:  # Иначе просто идем дальше
    #                 self.in_queue = grouped_queue.append(group)
    #             # group_values.append(mean_value)
    #             group_values.append(max_value)
    #             if len(self.in_queue) <= amount_of_grouped:
    #                 break
    #         group_has_values = dict.fromkeys(group_values)
    #         count = 0
    #         for k in group_values:  # Заполняем словарь соответствия ценности групп к самим группам
    #             group_has_values[k] = self.in_queue[count].copy()
    #             count += 1
    #     elif len(self.in_queue) == 1:
    #         # Если очередь состоит из одной партии, то толкаем ее в конец спланированной очереди
    #         insert = self.in_queue.copy()
    #         self.in_queue[0] = insert
    #         group_values.append(part_set[self.in_queue[0][0]].value)
    #         group_has_values[part_set[self.in_queue[0][0]].value] = self.in_queue.copy()
    #
    #     return group_values, group_has_values

    def group_recipe_rebuild(self):
        """
        Метод, который оптимизирует очередь на установку по рецептам, чтобы не тратить лишние ресурсы
        при их смене.

        Здесь все партии из временной и оптимизированной очередей группируются по рецептам, затем
        внутри каждой группы происходит сортировка по целевым функциям (target_function) (это значение
        вычисляется в фунции обновления данных партии update_part_info(machine_set, parts_set)).

        Наконец для каждой группы выявляется максимальное значение целевой функции, а оптимизированная
        очередь составляется по убыванию максимальных целевых функций групп и имеет вид:

        [[PART1 - партия, PART2, PART3 ...] - группа партий с одним рецептом, [...] ...] - очередь на
        установку,

        где [PART1 - партия, PART2, PART3 ...] - группа патрий с наивысшим максимальным
        значением целевой функции среди всех групп, PART1 - партия с наибольшей целевой функцией в группе.
        """
        temp_dict = {}
        # Объединяем все имеющиеся партии в оптимизированной и временной очередях на установку.
        try:
            self.in_queue.extend(np.hstack(self.out_queue))
        except Exception:
            print(Exception)
        for part in self.in_queue:
            # Если нет в словаре группы с таким id рецепта, то создаём группу рецепта с этой партией,
            # иначе добавляем партию в группу.
            if not temp_dict.get(part.recipe_id):
                temp_dict[part.recipe_id] = [part]
            else:
                temp_dict[part.recipe_id].append(part)
        # После того, как все группы сформированы, находим в каждой из них максимальное значение
        # целевой функции и добавляем его в кортеж к сортированной по убыванию целевых фунций
        # группе партий. Таким образом получается:
        # словарь[рецепт] = (максимальная целевая функция, сортированная группа).
        for key, arr in temp_dict.items():
            temp_dict[key] = max(part.target_function for part in arr), sorted(arr, key=lambda x: x.target_function,
                                                                               reverse=True)
        # Формируем оптимизированную очередь, добавляя группы по убыванию максимальных целевых функций.
        self.out_queue = [group for value, group in sorted(temp_dict.values(), key=lambda x: x[0], reverse=True)]
        # Чистим временную очередь, так как партии, что в нее были
        # добавлены, сортированы и добавлены в out_queue.
        self.in_queue.clear()

    @staticmethod
    def transposition(part_set, group):  # переставляем партии в группе, исходя из их ценности
        sorted_value = []
        if len(group) > 1:
            for i in group:
                sorted_value.append(part_set[i].target_function)

        sorted_group = [x for _, x in sorted(zip(sorted_value, group), reverse=True)]

        return sorted_group

    def optimize_groups(self, group_values, group_has_values):  # Переставляем группы исходя из их ценности

        self.out_queue.extend([x for _, x in sorted(zip(group_values, self.in_queue))])

    def set_individual_queue(self):  # Установка номера очереди в свойство партии
        for index, part in enumerate(np.hstack(self.out_queue)):
            # Начинается с 1 для матлаба
            part.queue = 1 + index

    def group_entities(self):
        """
        Метод, который оптимизирует очередь исходя из очередей на следующую установку партий.

        Здесь, все партии, которые уже имеются в оптимизированной очереди (out_queue),
        добавляются к партиям во временной очереди (in_queue). Затем партии сортируются по
        возрастанию длин очередей установок, куда им следует идти в следующем шаге.

        В итоге заполняется оптимизированная очередь на установку по шаблону:

        [[PART1 - партия, PART2, PART3 ...] - группа партий] , где у PART1 наименьшая очередь
        на следующей установке.
        """
        self.in_queue.extend(np.hstack(self.out_queue))
        self.in_queue.sort(key=lambda x: x.part.next_entity.len_queue)
        self.out_queue = [self.in_queue.copy()]
        # Чистим временную очередь, так как партии, что в нее были
        # добавлены, сортированы и добавлены в out_queue.
        self.in_queue.clear()

    def local_optimizer(self):
        """
        Метод, который оптимизирует очередь с учетом партий
        во временной очереди (in_queue) и в уже оптимизированной ранее
        (out_queue). Таким образом, каждый раз очередь полностью перетасовывается.

        2 Режима оптимизации:

        1 - По установкам (для узких мест)

        2 - По рецептам (по умолчанию)
        """
        if len(self.in_queue) > 0:
            # Здесь проверка на узкое место (условие пока временное).
            if len(self.in_queue) > 4:
                # Оптимизация по установкам.
                self.group_entities()
            else:
                # Оптимизация по рецептам.
                self.group_recipe_rebuild()
            # Запись каждой партии её номер в очереди (необходимо для отправки в БД).
            self.set_individual_queue()
            print(self.out_queue)
            if self.name == 'EPN014':
                a = 'rferdfgf'
            print(self.name)

    # Метод получения количества партий в очереди
    def get_len_queue(self):
        self.len_queue = 0
        for _item in self.out_queue:
            self.len_queue += len(_item)
        self.len_queue += len(self.in_queue)

    # Метод подсчета ценности партий в очереди с учетом данных об очередях на следующую установку
    def parse_out_queue(self, machine_set, parts_set):
        max_next_queue = -1
        for part in self.in_queue:  # Здесь не уверен что парсить - вход или выход
            # if machine_set[parts_set[part].next_entity].len_queue > max_next_queue:
            if parts_set[part].next_entity.len_queue > max_next_queue:
                max_next_queue = parts_set[part].next_entity.len_queue
        for part in self.in_queue:  # Здесь не уверен что парсить - вход или выход
            parts_set[part].calculate_value(max_next_queue, parts_set[part].next_entity.len_queue)

    def add_part_to_queue(self, part):
        self.in_queue.append(part)
        self.get_len_queue()

