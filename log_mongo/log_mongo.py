# -*- coding: utf-8 -*-

import pymongo
import datetime
import traceback
from settings import mongo_uri

_DEBUG = False


class MonLog(object):

    def __init__(self, uri, dbname='sdk_log'):
        if _DEBUG:
            self.db = dict()
            return

        if uri:
            c = pymongo.MongoClient(uri)
            # test for connection
            c.database_names()

            self.db = c[dbname]
        else:
            self.db = None

    @staticmethod
    def _youai_request_handler_format(handler):
        request = handler.request

        config = getattr(handler, 'serverConfig', 'not config')

        returns = handler.returns

        url = request.protocol + "://" + request.host

        document = {
            'ip': request.remote_ip,
            'method': request.method,
            'url': url + request.uri,

            "gamename": handler.game_code,
            "sdkname": handler.sdk_code,
            "sdkversion": handler.sdk_version_name,

            'config': config,
            'returns': returns,

            "create_time": str(datetime.datetime.now())[:19],
        }

        if 'logincheck/check' in request.uri:
            login_data = handler.data
            data = {
                'openId': login_data.get('openId', ''),
                'sign': login_data.get('sign', ''),
                'other': login_data.get('other', ''),
                'timestamp': login_data.get('timestamp', '')
            }
            document['data'] = data
            document.update(**data)
        else:
            body = request.body
            arguments = {k: v[0] for k, v in request.arguments.iteritems()}
            result_msg = getattr(handler, 'result_msg', '')
            pay_status = getattr(handler, 'pay_status', '')
            remark = getattr(handler, 'remark', '')

            query_id = getattr(handler, 'query_id', '')
            order_id = getattr(handler, 'order_id', '')

            document['body'] = body
            document['arguments'] = arguments

            document['result_msg'] = result_msg
            document['pay_status'] = pay_status
            document['remark'] = remark

            document['query_id'] = query_id
            document['order_id'] = order_id

        return document

    def insert_doc(self, collection, handler):
        if not collection or not handler:
            return
        try:
            doc = self._youai_request_handler_format(handler)
            if _DEBUG:
                with open('test_log_mongo', 'a') as f:
                    f.write(str(doc)+'\n')
                    f.flush()
            else:
                self.db[collection].insert(doc)
        except:
            try:
                with open('log_mongo_error.log', 'a') as f:
                    f.write(traceback.format_exc()+ '\n')
                    f.flush()
            except:
                pass

    def login_log(self, handler):
        self.insert_doc('log_login', handler)

    def pay_log(self, handler):
        self.insert_doc('log_pay', handler)


try:
    log_mongo = MonLog(mongo_uri)
except:
    traceback.print_exc()
    # 万一连不上mongodb，或者不想配置mongodb，也不会影响使用
    log_mongo = MonLog("")

