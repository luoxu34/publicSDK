# -*- coding: utf-8 -*-
"""
脚本的作用是找出数据量比较大的库，因为主机内存不够，
一次性加载大量数据到内存，会触发oom机制。找出大库后，可以分别收拾。
"""

import os
from db_utils import database_proxy, get_db, all_table

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

try:
    from models.projects import Projects
except ImportError:
    from models.projects import Projects

large_table = 500000
large_db = []

for i in Projects.objects.all():
    database_proxy.initialize(get_db(db_name='db_' + i.code))
    try:
        database_proxy.connection()
    except Exception as e:
        # print(e)
        continue  # 是有的库已经不存在了，但是记录还在

    for table in all_table:
        if table.select().count() > large_table:
            large_db.append(i.code)
            break

    database_proxy.close()

print('large dbs: ' + str(large_db))

