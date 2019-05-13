from src.functions import functions


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
        self.endQueue = 0
        self.len_queue = 0
        self.out_queue = [[]]
        self.group_values = []
        self.recipes_count = None
        self.get_groups()
        # self.get_recipe()
        # self.set_recipe(part_set=[])
        # self.get_queue()
        # self.group_recipe(part_set=[])
        # self.transposition(part_set=[], group=[])
        # self.optimize_groups(group_values=[], group_has_values={})
        print('Создана установка с id: {0}, recipe_id: {1} '
              'name: {2}'.format(self.machine_id, self.recipe_id, self.name))

    # Функция получения рецепта на установке, если мы будем цеплять его с бд (бд надо доработать)
    @functions.conn_decorator_method
    def get_recipe(self, cursor=None):
        sql = "SELECT recipe_on FROM `sosable_v0.6`.machines WHERE machine_id = {0}".format(self.machine_id)
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
    def get_groups(self, cursor=None):
        sql = "SELECT count(machines_has_recipe.recipe_recipe_id) FROM `sosable_v0.6`." \
              "machines_has_recipe WHERE machines_machines_id = {0};".format(self.machine_id)
        cursor.execute(sql)
        self.recipes_count = cursor.fetchone()
        self.recipes_count = self.recipes_count['count(machines_has_recipe.recipe_recipe_id)']

    # Группировка партий по рецептам

    def group_recipe(self, part_set):
        group_values = []  # Список средней ценности всей группы
        grouped_queue = []  # Сгруппированная очередь
        group_has_values = {}  # Словарь для сопоставления группы партий и их ценности
        amount_of_grouped = 0  # Количество сгруппированных партий
        if len(self.in_queue) > 1:  # Группировка будет, только в случае если у нас есть что группировать
            for i in range(self.recipes_count):  # Устанавлеваем порядок очереди по количеству возможных групп
                value = part_set[self.in_queue[amount_of_grouped]].value
                group = []
                for j in self.in_queue:
                    if part_set[self.in_queue[amount_of_grouped]].recipe_id == part_set[j].recipe_id:
                        group.append(j)
                        amount_of_grouped += 1
                        value += part_set[j].value
                mean_value = value / amount_of_grouped
                if len(group) > 1:  # Если группа состоит не из одной партии, то переставляем также партии в группах
                    grouped_queue.append(self.transposition(part_set, group))
                    self.in_queue = grouped_queue.copy()
                else:  # Иначе просто идем дальше
                    self.in_queue = grouped_queue.append(group)
                group_values.append(mean_value)
                if len(self.in_queue) <= amount_of_grouped:
                    break
            group_has_values = dict.fromkeys(group_values)
            count = 0
            for k in group_values:  # Заполняем словарь соответствия ценности групп к самим группам
                group_has_values[k] = self.in_queue[count].copy()
                count += 1
        elif len(
                self.in_queue) == 1:  # Если очередь состоит из одной партии, то толкаем ее в конец спланированной очереди
            group_values.append(part_set[self.in_queue[0]].value)
            group_has_values[part_set[self.in_queue[0]].value] = self.in_queue.copy()

        return group_values, group_has_values

    def transposition(self, part_set, group):  # переставляем партии в группе, исходя из их ценности
        sorted_group = []
        count = 0
        if len(group) > 1:
            for i in group:
                maxi = group[count]
                for j in range(len(group) - count):
                    if part_set[i].value < part_set[group[j + count]].value:
                        maxi = group[j]
                count += 1
                sorted_group.append(maxi)
        return sorted_group

    def optimize_groups(self, group_values, group_has_values):  # Переставляем группы исходя из их ценности
        self.out_queue.extend([x for _, x in sorted(zip(group_values, self.in_queue))])

    def set_individual_queue(self, part_set):  # Установка номера очереди в свойство партии
        count = 0
        for i in range(len(self.out_queue)):
            for j in range(len(self.out_queue[i])):
                part_set[self.out_queue[i][j]].queue = count
                count += 1

    def local_optimizer(self, part_set):
        if len(self.in_queue) > 0:
            group_values, group_has_values = self.group_recipe(part_set)
            self.optimize_groups(group_values, group_has_values)
            self.set_individual_queue(part_set)
            print(self.out_queue)

    # Метод получения количества партий в очереди
    def get_len_queue(self):
        self.len_queue = 0
        for item in self.out_queue:
            self.len_queue += len(item)

    # Метод подсчета ценности партий в очереди с учетом данных об очередях на следующую установку
    def parse_out_queue(self, machine_set, parts_set):
        max_next_queue = -1
        for group in self.out_queue:  # Здесь не уверен что парсить - вход или выход
            for part in group:
                if parts_set[part].next_queue > max_next_queue:
                    max_next_queue = parts_set[part].next_queue
        for group in self.out_queue:  # Здесь не уверен что парсить - вход или выход
            for part in group:
                parts_set[part].calculate_value(max_next_queue, machine_set[parts_set[part].next_entity].len_queue)
