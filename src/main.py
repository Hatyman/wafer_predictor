import pymysql.cursors
# Подключение к бд
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='91xz271999',
                       # password='91xz271999',
                       db='sosable_v0.6',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

class part:
    # Конструктор партий, туда надо еще добавить параметров, вызываться он будет через функцию get_other_params
    def __init__(self, id, name, list_id, act_process, queue, reserve, wait, recipe_id):
        self.id = id,
        self.name = name,  # Это можно убрать, наверное
        self.list_id = list_id,
        self.act_process = act_process,
        self.queue = queue,
        self.reserve = reserve,
        self.wait = wait,
        self.recipe_id = recipe_id  # Надо добавить еще атрибуты из доп. запроса

    @classmethod  # Метод только для класса (в объекте он недоступен)
    def get_other_params(cls, data):
        pass