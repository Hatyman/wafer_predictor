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
        self.out_queue = []
        self.group_values = []
        #self.get_recipe()
        #self.set_recipe(part_set=[])
        # self.get_queue()
        #self.group_recipe(part_set=[])
        self.transposition(part_set=[], group=[])
        self.optimize_groups(group_values=[], group_has_values={})
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
    def group_recipe(self, part_set, cursor=None):
        sql = "SELECT count(machines_has_recipe.recipe_recipe_id) FROM `sosable_v0.6`." \
              "machines_has_recipe WHERE machines_machines_id = 1;".format(self.machine_id)
        cursor.execute(sql)
        recipes_count = cursor.fetchone()  # запрашиваем количество возможных групп на установке
        group_values = []
        grouped_queue = []
        amount_of_grouped = 0
        if self.in_queue != None:
            for i in range(recipes_count):  # Устанавлеваем порядок очереди по группам
                value = part_set[amount_of_grouped].value
                group = [self.in_queue[amount_of_grouped]]
                for j in range(len(self.in_queue)):
                    if part_set[amount_of_grouped].recipe_id == part_set[j].recipe_id:
                        group.append(self.in_queue[j])
                        amount_of_grouped += 1
                        value += part_set[j].value
                mean_value = value / amount_of_grouped
                amount_of_grouped += 1
                if len(group) > 1:
                    self.in_queue = grouped_queue.append(self.transposition(part_set, group))
                else:
                    self.in_queue = grouped_queue.append(group)
                group_values.append(mean_value)
            group_has_values = dict.fromkeys(group_values)
            count = 0
            for k in group_values:
                group_has_values[k] = self.in_queue[count]
                count += 1
        else:
            print('Нет очереди')
        return group_values, group_has_values

    def transposition(self, part_set, group):
        sorted_group = []
        if len(group) > 1:
            maxi = part_set[group[0]].value
            for i in range(len(group)):
                for j in range(len(group)):
                    if part_set[i].value < part_set[j].value:
                        maxi = part_set[j].value
                sorted_group.append(maxi)
        return sorted_group

    def optimize_groups(self, group_values, group_has_values):
        group_values = sorted(group_values, reverse=True)
        for i in range(len(self.in_queue)):
            self.in_queue[i] = group_has_values[group_values[i]]
        self.out_queue.extend(self.in_queue)

    def local_optimizer(self, part_set):
        group_values, group_has_values = self.group_recipe(part_set)
        self.optimize_groups(group_values, group_has_values)
