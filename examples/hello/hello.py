#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import getopt
import asyncio

import tomato
tomato.patch_json()

from tomato.util import Log
from tomato.util import loadconf
from tomato.util import autoreload
from tomato.util import Application
from tomato.store import MySQLModule
from tomato.store import SqlClauseAssemble
from tomato.store import SqlParamCollections
from tomato.transport import HttpServerModule
from hello_module.hello_handler import routes


def usage():
    print('usage:')
    print('-h,--help: print help message.')
    print('-v, --version: print program version')
    print('-c, --conf: program conf filename')

def version():
    print('1.0.0.0')

def parser_cmd(argv):
    try:
        conf_name = None
        opts, args = getopt.getopt(argv[1:], 'hvc:', ['help', 'version', 'conf='])
        for op, v in opts:
            if op in ('-h', '--help'):
                usage()
                sys.exit(0)
            elif op in ('-v', '--version'):
                version()
                sys.exit(0)
            elif op in ('-c', '--conf'):
                conf_name = v
            else:
                print('unhandled option')
                sys.exit(3)
        if conf_name is None:
            usage()
            sys.exit(3)

        return conf_name
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)

def main(argv):
    autoreload()
    conf_file = parser_cmd(argv)
    conf = loadconf(conf_file)
    log_conf_file = conf.get('logger', 'logger_conf')
    Log(conf_file=log_conf_file)

    app = Application()
    mysql_setting = dict(conf.items('mysql'))
    http_server_setting = dict(conf.items('http_server'))

    routes_list = [routes, ]
    app['mysql'] = MySQLModule(setting=mysql_setting)
    app['http_server'] = HttpServerModule(setting=http_server_setting, routes_list=routes_list)
    app.run()
    loop = asyncio.get_event_loop()

    sql_assemble = SqlClauseAssemble()
    sql_assemble.wanted_words = ['platform_id', 'open_id']
    sql_assemble.table_name = '`app_account_users`'
    where_params = SqlParamCollections()
    where_params.add_normal_param(('open_id', '=', 18888888888, True))
    sql_assemble.where_params = where_params
    (sql, params) = sql_assemble.get_query_clause()
    Log().info((sql, params))
    result_list = loop.run_until_complete(app['mysql'].get_all(sql,params))
    Log().info(result_list)

    app.stop()
    app.run_forever()

if __name__ == '__main__':
    main(sys.argv)

