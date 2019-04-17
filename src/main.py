import pymysql.cursors

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='91xz271999',
                       # password='91xz271999',
                       db='sosable_v0.6',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

