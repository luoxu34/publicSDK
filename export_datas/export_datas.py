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

    with open(os.path.join(output, db_name), 'a') as f:

        for row in table.select().dicts():
            for col, value in row.iteritems():
                if value is None:
                    row[col] = ''

            if isinstance(row[an_col], basestring):
                row[an_col] = row[an_col].replace('|', '#')
            if row.get('f6'):
                row['f6'] = row['f6'].replace('\n', ' ')

            row.update(db_name=db_name, game_alias=game_alias, table_name=tb_name, now=now, ts=ts)
            line = template.format(**row)
            f.write(line)


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
            title = '{}.{}'.format(db_name, table._meta.table_name)
            print('export ' + title)

            fun = safe_export if db_name in large_db else faster_export
            fun(db_name, game_alias, table)
            with open('exported', 'a') as f:
                f.write(title + '\n')

        database_proxy.close()


st_time = datetime.datetime.now()
export()
ed_time = datetime.datetime.now()

print('Complete export!')
print('Time consuming: {}'.format(ed_time - st_time))

