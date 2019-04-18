from src.functions import functions

# Завтра еще подредачу, не помню что еще нужно добавить
class Machine:
    # Конструктор установок
    def __init__(self, machine_id, name, queue, broken, recipe_id):
        self.machine_id = machine_id
        self.name = name
        self.queue = queue
        self.broken = broken
        self.recipe_id = recipe_id
        self.get_recipe()
        self.get_queue()
        self.set_recipe()
        self.observe_next_entity()
        print('Создана установка с id {0}: {1} name: {2}]'.format(self.part_id, self.name, self.list_id))

    # Функция получения рецепта на установке, если мы будем цеплять его с бд (бд надо доработать)
    @functions.conn_decorator_method
    def get_recipe(self, cursor=None):
        sql = "SELECT recipe_on FROM `sosable_v0.6`.machines WHERE machine_id = {0}".format(self.machine_id)
        cursor.execute(sql)
        result = cursor.fetchone()
        self.recipe_id = result['recipe_on']

    # Функция получения очереди на установку
    @functions.conn_decorator_method
    def get_queue(self, cursor=None):
        try:
            sql = "CALL `sosable_v0.6`.`queue`('{0}')".format(self.name)
            cursor.execute(sql)
            result = cursor.fetchone()
            # По идее я ходу увидеть полноценную очередь, но не знаю, какой вывод будет точно
            self.queue = [result['part_id'], result['recipe_id']]
        except:
            print('Твою мать, она не работает, мб ошибка в данных')

    # Функция изменения рецепта на установку по первой партии в очереди
    def set_recipe(self):
        self.recipe_id = self.queue[0][1]
        print('Установлен рецепт: {0} на установке: {1}'.format(self.recipe_id, self.machine_id))

