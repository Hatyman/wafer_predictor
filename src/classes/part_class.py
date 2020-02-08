from src.functions import functions
import sys
import numpy as np


class Part:
    # Конструктор партий, туда надо еще добавить параметров, вызываться он будет через функцию get_other_params
    def __init__(self, part_id, name, list_id, act_process, queue, reserve, wait, recipe_id, priority):
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
        self.next_entity_list = []
        self.next_entity = 0
        self.time_of_process = 0
        self.current_entity = 0
        self.prev_entity = []
        self.priority = priority
        self.start_process = 0
        self.end_process = 0
        self.log_flag = 0
        try:
            self.get_other_params()
        except Exception as e:
            print(str(e))
            print(sys.exc_info())
        self.get_current_time()
        self.get_prev_entity()
        self.get_next_entity()
        # new coefficients
        self.step = 0
        self.delta_time = 5
        self.factor_A = 0
        self.factor_B = 0
        self.group_number = 0
        self.entity_number = 0
        self.target_function = 0
        self.current_entity_list = []
        print('Создана партия с id {0}: {1} [list_id: {2}]'.format(self.part_id, self.name, self.list_id))

    # Функция получения МВХ и установки, где партии сейчас надо быть
    @functions.conn_decorator_method
    def get_other_params(self, cursor=None, conn=None):
        self.current_entity_list = []
        sql = "SELECT m.machines_id FROM `production`.recipe r INNER JOIN `production`.machines_has_recipe mhr ON r.recipe_id = mhr.recipe_recipe_id INNER JOIN `production`.machines m ON mhr.machines_machines_id = m.machines_id WHERE recipe_id = {0}".format(
            self.recipe_id
        )
        cursor.execute(sql)
        res = cursor.fetchall()

        # self.current_entity = res['machines_id']
        for row in res:
            self.current_entity_list.append(row['machines_id'])

    @functions.conn_decorator_method
    def get_general_params(self, cursor=None, conn=None):
        sql = "SELECT active_process as act_process, queue, wait, reservation as reserve, " \
              "part_recipe_id as recipe_id FROM `production`.part WHERE part_id={0}".format(self.part_id)
        cursor.execute(sql)
        res = cursor.fetchone()

        self.act_process = res['act_process']
        self.queue = res['queue']
        self.wait = res['wait']
        self.reserve = res['reserve']
        self.recipe_id = res['recipe_id']

    def set_current_entity(self, value):
        self.current_entity = value

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
    # @functions.conn_decorator_method
    # def observe_next_entity(self, cursor=None):
    #
    #     # Получаем рецепт следующего шага
    #     sql = "SELECT `{0}` FROM `sosable_v0.6`.list WHERE list_id = {1}".format(int(self.act_process) + 1, self.list_id)
    #     cursor.execute(sql)
    #     res = cursor.fetchone()
    #
    #     # Так мы динамически зайдем в словарь проще всего
    #     for key, val in res.items():
    #         sql = "SELECT time_of_process FROM `sosable_v0.6`.recipe WHERE recipe_id = {0}".format(val)
    #
    #     # Получаем время следующего шага
    #     cursor.execute(sql)
    #     res = cursor.fetchone()
    #
    #     self.further_time = int(res['time_of_process'])

    def update_attr(self):
        """
        Метод обновления всех (которые могут изменяться) параметров партии.

        Здесь обновляются:

        · списки установок для текущего и следующего шагов;

        · выполняется ли партия в установке;

        · id рецепта;

        · шаг по маршрутному листу;

        · время выполнения текущего рецепта;

        · МВХ (если есть);

        · номер в очереди на установку.

        Также рассчитывается целевая функция.
        """
        self.get_general_params()
        self.get_next_entity()
        self.get_prev_entity()
        self.get_other_params()
        self.get_current_time()
        self.calculate_target_function()

    # Функция рассчета веса партии (пока пустая)
    def estimate(self):
        pass

    # Функция получения прошлой установки
    @functions.conn_decorator_method
    def get_prev_entity(self, cursor=None, conn=None):
        # Ищем все машины, которые могли быть по рецепту предыдущего шага
        sql = "SELECT machines_machines_id, time_limit FROM `production`.machines_has_recipe " \
              "INNER JOIN `production`.recipe ON machines_has_recipe.recipe_recipe_id = recipe.recipe_id " \
              "WHERE recipe_recipe_id=(SELECT `{0}` FROM `production`.list WHERE list_id={1})".format(
            int(self.act_process) - 1,
            self.list_id)
        cursor.execute(sql)
        res = cursor.fetchall()

        # Чистим каждый раз наше множество во избежание проблем с дублированием
        self.prev_entity.clear()

        # Обходим каждую из вернутых строк
        for cash in res:
            self.prev_entity.append(cash['machines_machines_id'])
            if self.time_limit != cash['time_limit']:
                self.least_tl = cash['time_limit']
            self.time_limit = cash['time_limit']

    # Функция получения прошлой установки
    @functions.conn_decorator_method
    def get_next_entity(self, cursor=None, conn=None):
        # Ищем все машины, которые могли быть по рецепту следующего шага
        sql = "SELECT machines_machines_id, time_limit FROM `production`.machines_has_recipe " \
              "INNER JOIN `production`.recipe ON machines_has_recipe.recipe_recipe_id = recipe.recipe_id " \
              "WHERE recipe_recipe_id=(SELECT `{0}` FROM `production`.list WHERE list_id={1})".format(
            int(self.act_process) + 1,
            self.list_id)
        cursor.execute(sql)
        res = cursor.fetchall()

        # Чистим каждый раз наше множество во избежание проблем с дублированием
        self.next_entity_list.clear()
        # Обходим каждую из вернутых строк
        for mach in res:
            self.next_entity_list.append(mach['machines_machines_id'])

    def set_next_entity(self, value):
        self.next_entity = value

    # Функция получения времени выполнения текущего рецепта
    @functions.conn_decorator_method
    def get_current_time(self, cursor=None, conn=None):
        sql = "SELECT time_of_process FROM `production`.recipe WHERE recipe_id={0}".format(
            self.recipe_id
        )
        cursor.execute(sql)
        res = cursor.fetchone()

        self.time_of_process = res['time_of_process']
        return self.time_of_process

    @functions.conn_decorator_method  # исходя из примера метод должен обновлять очередь в базе
    def send_queue(self, cursor=None, conn=None):
        if self.queue:
            sql = "UPDATE `production`.part SET queue = {0} WHERE part_id = {1}".format(
                self.queue,
                self.part_id
            )
            cursor.execute(sql)
            conn.commit()

    @functions.conn_decorator_method  # исходя из примера метод должен обновлять очередь в базе
    def reset_queue(self, cursor=None, conn=None):
        sql = "UPDATE `production`.part SET queue = NULL WHERE part_id = {0}".format(
            self.part_id
        )
        cursor.execute(sql)
        conn.commit()

    def calculate_value(self, max_next_queue=0, next_queue=0):
        if self.time_limit:
            k_mts = self.least_tl / self.time_limit
        else:
            k_mts = 0
        k_p = self.priority / 4
        if max_next_queue:
            k_o = 1 - (next_queue / max_next_queue)
        else:
            k_o = 1
        self.value = k_mts + k_p + k_o

    def calculate_target_function(self):
        """
        Метод расчета целевой фнукции
        """
        # Если есть МВХ, включаем экспоненциальную составляющую
        if self.time_limit:
            self.factor_B = 1
        else:
            self.factor_B = 0
        self.target_function = self.step * self.delta_time * self.factor_A + \
            np.exp(self.step * self.delta_time) * self.factor_B
        self.step += 1
