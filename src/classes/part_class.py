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
        self.time_of_process = 0
        self.current_entity = 0
        self.prev_entity = []
        self.get_other_params()
        self.get_current_time()
        self.get_prev_entity()
        self.observe_next_entity()
        print('Создана партия с id {0}: {1} [list_id: {2}]'.format(self.part_id, self.name, self.list_id))

    # Функция получения МВХ и установки, где партии сейчас надо быть
    @functions.conn_decorator_method
    def get_other_params(self, cursor=None):
        sql = "SELECT m.machines_id FROM `sosable_v0.6`.recipe r INNER JOIN `sosable_v0.6`.machines_has_recipe mhr ON r.recipe_id = mhr.recipe_recipe_id INNER JOIN `sosable_v0.6`.machines m ON mhr.machines_machines_id = m.machines_id WHERE recipe_id = {0}".format(
            self.recipe_id
        )
        cursor.execute(sql)
        res = cursor.fetchone()

        self.current_entity = res['machines_id']

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

    # Функция обновления всех (которые могут изменяться) параметров партии
    @functions.conn_decorator_method
    def update_attr(self, cursor=None):

        sql = "SELECT active_process as act_process, queue, wait, reservation as reserve, part_recipe_id as recipe_id FROM `sosable_v0.6`.part WHERE part_id={0}".format(
            self.part_id
        )
        cursor.execute(sql)
        res = cursor.fetchone()

        self.act_process = res['act_process']
        self.queue = res['queue']
        self.wait = res['wait']
        self.reserve = res['reserve']
        self.recipe_id = res['recipe_id']
        self.observe_next_entity()
        self.get_prev_entity()
        self.get_other_params()
        self.get_current_time()


    # Функция рассчета веса партии (пока пустая)
    def estimate(self):
        pass

    # Функция получения прошлой установки
    @functions.conn_decorator_method
    def get_prev_entity(self, cursor=None):
        # Ищем все машины, которые могли быть по рецепту предыдущего шага
        sql = "SELECT machines_machines_id, time_limit FROM `sosable_v0.6`.machines_has_recipe INNER JOIN `sosable_v0.6`.recipe ON machines_has_recipe.recipe_recipe_id = recipe.recipe_id WHERE recipe_recipe_id=(SELECT `{0}` FROM `sosable_v0.6`.list WHERE list_id={1})".format(
            int(self.act_process) - 1,
            self.list_id
        )
        cursor.execute(sql)
        res = cursor.fetchall()

        # Чистим каждый раз наше множество во избежание проблем с дублированием
        self.prev_entity.clear()

        # Обходим каждую из вернутых строк
        for item in res:
            self.prev_entity.append(item['machines_machines_id'])
            self.time_limit = item['time_limit']
            self.least_tl = item['time_limit']


    # Функция получения времени выполнения текущего рецепта
    @functions.conn_decorator_method
    def get_current_time(self, cursor=None):
        sql = "SELECT time_of_process FROM `sosable_v0.6`.recipe WHERE recipe_id={0}".format(
            self.recipe_id
        )
        cursor.execute(sql)
        res = cursor.fetchone()

        self.time_of_process = res['time_of_process']
        return self.time_of_process

