import pymysql.cursors
from src.classes import part_class
from src.functions import functions


# Подключение к бд убрали в обёртку (можно еще продублировать в файл отдельный как функцию)
# conn = pymysql.connect(host='localhost',
#                        user='root',
#                        password='91xz271999',
#                        # password='91xz271999',
#                        db='sosable_v0.6',
#                        charset='utf8mb4',
#                        cursorclass=pymysql.cursors.DictCursor)


functions.create_parts()  # Вызываем функцию создания партий

