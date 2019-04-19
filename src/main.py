import pymysql.cursors
from src.classes import part_class
from src.functions import functions

parts_set = functions.create_machines()  # Вызываем функцию создания партий

print(parts_set[14].further_time)
