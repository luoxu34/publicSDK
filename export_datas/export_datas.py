# -*- coding: utf-8 -*-

import os
import time
import datetime
from db_utils import database_proxy, get_db, all_table, large_db

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

try:
    from models.projects import Projects
except ImportError:
    from models.projects import Projects

output = '/data3/output'
if not os.path.exists(output):
    os.makedirs(output)


# mysql数据模型迭代器包装类
class ModelIterator(object):
    # 参考：
    start_id = 0

    def __init__(self, model, step=150000):
        self.model = model
        self.step = step

    def __iter__(self):
        rows = self.__getRows()
        while True:
            for item in rows:
                yield item
            rows = self.__getRows()

    def __getRows(self):
        rows = self.model.select().dicts().where(
            self.model.id > self.start_id).limit(self.step)

        if rows.count() == 0:
            raise StopIteration()
        else:
            self.start_id = rows[-1]['id']
            return rows


def write_ok_file(db_name, tb_name, pk_id):
    line = '{}.{}:{}\n'.format(db_name, tb_name, pk_id)
    with open('ok', 'a') as f:
        f.write(line)


def file_too_large(path):
    if os.path.isfile(path) and os.path.getsize(path) > 2097152:
        return True
    return False


def faster_export(db_name, game_alias, table):
    now = str(datetime.datetime.now())[:19]
    ts = str(int(time.time()))

    tb_name = table.__name__.lower()
    if tb_name == 'player':
        an_col = 'other'
        template = ('{now}|player|{game_alias}|{db_name}|{ts}|{server}|{player_id}|'
                    '{player_name}|{sdk_code}|{openid}|{create_time}|{last_time}|'
                    '{last_ip}|{login_num}|{status}|{log_channel}|{log_channel2}|'
                    '{mobile_key}|{network}|{resolution}|{other}\n')
    else:
        an_col = 'f4'
        template = ('{log_time}|{table_name}|{game_alias}|{db_name}|{log_type}|'
                    '{log_tag}|{log_user}|{log_sdk_code}|{log_previous}|{log_now}|'
                    '{log_name}|{log_server}|{log_level}|{log_version}|{log_mobile_key}|'
                    '{log_network}|{log_resolution}|{f1}|{f2}|{f3}|{f4}|{f5}|{f6}|'
                    '{log_channel}|{log_channel2}|{log_data}|{log_result}\n')

    max_id = 0
    with open(os.path.join(output, db_name), 'a') as f:

        for row in table.select().dicts():
            for col, value in row.iteritems():
                if value is None:
                    row[col] = ''

            if isinstance(row[an_col], basestring):
                row[an_col] = row[an_col].replace('|', '#')
            if row.get('f6'):
                row['f6'] = row['f6'].replace('\n', ' ')

            row.update(db_name=db_name, game_alias=game_alias,
                       table_name=tb_name, now=now, ts=ts)
            line = template.format(**row)
            f.write(line)
            max_id = row['id']

    write_ok_file(db_name, tb_name, max_id)


def safe_export(db_name, game_alias, table):
    pass


def export():
    for i in Projects.objects.all():
        if not i.game:
            continue
        db_name, game_alias = i.code, i.game.code

        database_proxy.initialize(get_db(db_name='db_' + db_name))
        try:
            database_proxy.connection()
        except:
            continue

        for table in all_table:
            print('export {}.{}'.format(db_name, table._meta.table_name))

            fun = safe_export if db_name in large_db else faster_export
            fun(db_name, game_alias, table)

        database_proxy.close()


st_time = datetime.datetime.now()
export()
ed_time = datetime.datetime.now()

print('Complete export!')
print('Time consuming: {}'.format(ed_time - st_time))

