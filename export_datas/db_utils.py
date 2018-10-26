# -*- coding: utf-8 -*-

from peewee import Proxy, MySQLDatabase, Model
from peewee import CharField, TextField

database_proxy = Proxy()  # Create a proxy for our db.


def make_table_name(model_class):
    model_name = model_class.__name__
    return 'log_' + model_name.lower()


class BaseModel(Model):

    class Meta:
        database = database_proxy
        table_function = make_table_name


class Player(BaseModel):
    id = CharField()
    server = CharField()
    player_id = CharField()
    player_name = CharField()
    sdk_code = CharField()
    openid = CharField()
    create_time = CharField()
    last_time = CharField()
    last_ip = CharField()
    login_num = CharField()
    status = CharField()
    log_channel = CharField()
    log_channel2 = CharField()
    mobile_key = CharField()
    network = CharField()
    resolution = CharField()
    other = CharField()

    class Meta:
        database = database_proxy
        table_function = None


class MyTable(BaseModel):

    id = CharField()
    log_time = CharField()
    log_type = CharField()
    log_tag = CharField()
    log_user = CharField()
    log_sdk_code = CharField()
    log_previous = CharField()
    log_now = CharField()
    log_name = CharField()
    log_server = CharField()
    log_level = CharField()
    log_version = CharField()
    log_mobile_key = CharField()
    log_network = CharField()
    log_resolution = CharField()
    f1 = CharField()
    f2 = CharField()
    f3 = CharField()
    f4 = CharField()
    f5 = CharField()
    f6 = TextField()
    log_channel = CharField()
    log_channel2 = CharField()
    log_data = CharField()
    log_result = CharField()


class Ad(MyTable):pass
class Ad_click(MyTable):pass
class Ad_gdt(MyTable):pass
class Ad_onload(MyTable):pass
class Ad_show(MyTable):pass
class Ad_statistic_result(MyTable):pass
class Chatdata(MyTable):pass
class Communication_record(MyTable):pass
class Device(MyTable):pass
class Enter(MyTable):pass
class Error_pay(MyTable):pass
class Event(MyTable):pass
class Game_role(MyTable):pass
class Game_role_pay(MyTable):pass
class Game_server(MyTable):pass
class Game_statistic_result(MyTable):pass
class Login(MyTable):pass
class New_device(MyTable):pass
class Open(MyTable):pass
class Open_new_device(MyTable):pass
class Opensdk(MyTable):pass
class Pay(MyTable):pass
class Post_pay(MyTable):pass
class Qufu_users(MyTable):pass
class Server_pay(MyTable):pass
class Statistic_date(MyTable):pass


all_table = [Ad, Ad_click, Ad_gdt, Ad_onload, Ad_show, Ad_statistic_result, Chatdata,
       Communication_record, Device, Enter, Error_pay, Event, Game_role, Game_role_pay,
       Game_server, Game_statistic_result, Login, New_device, Open, Open_new_device,
       Opensdk, Pay, Post_pay, Qufu_users, Server_pay, Player]


host = '127.0.0.1'
port = 3306
pw = ''


def get_db(db_name):
    return MySQLDatabase(db_name, user='root', password=pw,
                         host=host, port=port)

