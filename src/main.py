import pymysql.cursors
from src.classes import part_class
from src.functions import functions

parts_set = functions.create_parts()  # Вызываем функцию создания партий
machine_set = functions.create_machines()  # Вызываем функцию создания партий

print(machine_set)

