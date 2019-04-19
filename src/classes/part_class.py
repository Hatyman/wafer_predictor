from src.functions import functions


class Part:
    # Конструктор партий, туда надо еще добавить параметров, вызываться он будет через функцию get_other_params
    def __init__(self, part_id, name, list_id, act_process, queue, reserve, wait, recipe_id):
        self.part_id = part_id
        self.name = name  # Это можно убрать, наверное, но лучше пусть будет
        self.list_id = list_id
        self.act_process = act_process
        self.queue = queue
        self.reserve = reserve
        self.wait = wait
        self.recipe_id = recipe_id  # Надо добавить еще атрибуты из доп. запроса
        self.time_limit = 0  # На всякий случай объявим их заранее *4
        self.least_tl = 0.0
        self.value = 0.0
        self.further_time = 0
        self.get_other_params()
        self.observe_next_entity()
        print('Создана партия с id {0}: {1} [list_id: {2}]'.format(self.part_id, self.name, self.list_id))

    # Функция получения МВХ
    @functions.conn_decorator_method
    def get_other_params(self, cursor=None):
        sql = "SELECT time_limit FROM `sosable_v0.6`.recipe WHERE recipe_id = {0}".format(self.recipe_id)
        cursor.execute(sql)
        res = cursor.fetchone()

        self.time_limit = res['time_limit']
        self.least_tl = res['time_limit']

    # Функция изменения оставшегося МВХ (на 20 минут) и сигнализирования, если МВХ истекает
    def dying(self):
        # Проверяем есть ли вообще МВХ у партии
        if self.time_limit:
            # Проверяем осталось ли МВХ
            if self.least_tl > (1 / 3):
                self.least_tl -= 1 / 3
            else:
                print("Пришел звиздец партии с id {0} на шаге {1} на рецепте {2}".format(self.part_id, self.act_process,
                                                                                         self.recipe_id))

    # Функция получения времени обработки на следующей установке
    @functions.conn_decorator_method
    def observe_next_entity(self, cursor=None):

        # Получаем рецепт следующего шага
        sql = "SELECT {0} FROM `sosable_v0.6`.list WHERE list_id = {1}".format(int(self.act_process) + 1, self.list_id)
        cursor.execute(sql)
        res = cursor.fetchone()

        # Так мы динамически зайдем в словарь проще всего
        for key, val in res.items():
            sql = "SELECT time_of_process FROM `sosable_v0.6`.recipe WHERE recipe_id = {0}".format(val)

        # Получаем время следующего шага
        cursor.execute(sql)
        res = cursor.fetchone()

        self.further_time = res['time_of_process']

    # Функция обновления всех (или не всех) параметров партии
    @functions.conn_decorator_method
    def update_attr(self, cursor=None):

        sql = "SELECT active_process as act_process, queue, wait, reservation as reserve, part_recipe_id as recipe_id FROM `sosable_v0.6`.part WHERE part_id={0}".format(self.part_id)
        cursor.execute(sql)
        res = cursor.fetchone()

        self.act_process = res['act_process']
        self.queue = res['queue']
        self.wait = res['wait']
        self.reserve = res['reserve']
        self.recipe_id = res['recipe_id']

    def estimate(self):
        pass

