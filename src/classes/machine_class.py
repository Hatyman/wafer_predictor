from src.functions import functions


# Завтра еще подредачу, не помню что еще нужно добавить
class Machine:
    # Конструктор установок
    def __init__(self, machine_id, name, broken):
        self.machine_id = machine_id
        self.name = name
        self.queue = []
        self.broken = broken
        self.recipe_id = 0
        self.forbidden = False
        self.endQueue = 0
        self.get_recipe()
        # self.get_queue()
        self.set_recipe()
        self.group_recipe()
        print('Создана установка с id: {0}, recipe_id: {1} name: {2}'.format(self.machine_id, self.recipe_id, self.name))

    # Функция получения рецепта на установке, если мы будем цеплять его с бд (бд надо доработать)
    @functions.conn_decorator_method
    def get_recipe(self, cursor=None):
        sql = "SELECT recipe_on FROM `sosable_v0.6`.machines WHERE machine_id = {0}".format(self.machine_id)
        cursor.execute(sql)
        result = cursor.fetchone()
        self.recipe_id = result['recipe_on']

    # Функция изменения рецепта на установку по первой партии в очереди
    def set_recipe(self):
        self.recipe_id = self.queue[0][1]
        print('Установлен рецепт: {0} на установке: {1}'.format(self.recipe_id, self.machine_id))

    def forbid(self):
        self.forbidden = not self.forbidden

    @functions.conn_decorator_method
    def group_recipe(self, part_set, cursor=None):
        sql = "SELECT count(machines_has_recipe.recipe_id) FROM `sosable_v0.6`.machines_has_recipe WHERE machine_id = {0}".format(self.machine_id)
        cursor.execute(sql)
        recipes_count = cursor.fetchone() # запрашиваем количество возможных групп на установке
        group_value = []
        first_recipe = self.endQueue
        second_recipe = first_recipe + 1 # Начинаем отсчет с конца сформированной очереди
        for i in range(recipes_count): # Устанавлеваем порядок очереди по группам
            for j in range(len(self.queue) - first_recipe):
                if part_set[first_recipe].recipe_id == part_set[second_recipe].recipe_id:
                    first_recipe += 1
                    second_recipe += 1
                    self.queue.insert(first_recipe, part_set[self.queue.pop(second_recipe)])
        first_recipe = self.endQueue # Обнуляем счетчики
        second_recipe = first_recipe + 1
        for k in range(recipes_count): #Расчитываем среднюю ценность партий группы
            for j in range(len(self.queue) - first_recipe):
                if part_set[first_recipe].recipe_id == part_set[second_recipe].recipe_id:
                    group_value[k] += 0 +  part_set[first_recipe].value
                    group_value[k] = group_value[k] / j
                    first_recipe += 1
                    second_recipe += 1
                else:
                    break
        self.endQueue = first_recipe

    def transposition(self, part_set):


    def local_optimizer(self, part_set):
        self.group_recipe(part_set)
