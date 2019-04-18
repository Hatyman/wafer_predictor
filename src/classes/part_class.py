class Part:
    # Конструктор партий, туда надо еще добавить параметров, вызываться он будет через функцию get_other_params
    def __init__(self, part_id, name, list_id, act_process, queue, reserve, wait, recipe_id):
        self.part_id = part_id,
        self.name = name,  # Это можно убрать, наверное, но лучше пусть будет
        self.list_id = list_id,
        self.act_process = act_process,
        self.queue = queue,
        self.reserve = reserve,
        self.wait = wait,
        self.recipe_id = recipe_id  # Надо добавить еще атрибуты из доп. запроса

    @classmethod  # Метод только для класса (в объекте он недоступен)
    def get_other_params(cls, data):

        part_id, name, list_id, act_process, queue, reserve, wait, recipe_id = data

        return cls(part_id, name, list_id, act_process, queue, reserve, wait, recipe_id)


