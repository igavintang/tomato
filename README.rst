========================================
Python engineering component library
========================================


Features
========

- Manage common modules (MySQLModule, HttpServerModule) with Application class.
- Web routing configures the handler through the decorator.
- SQL normalization, avoiding heavy ORM, while also making readability.


Getting started
===============

Install
------

.. code-block:: shell

python3 setup.py sdist bdist_wheel
pip install dist/pytomato-0.0.1-py3-none-any.whl

Server
------

An example using a server:

.. code-block:: python

    # hello_handler.py

    from aiohttp import web
    from tomato.transport.http import Routes


    routes = Routes()

    @routes.get('/hello')
    @routes.get('/hello/{name}')
    async def xxx(request):
        name = request.match_info.get('name', "Anonymous")
        text = "Hello, " + name
        return web.Response(text=text)


.. code-block:: python

    # hello.py

    from hello_handler import routes
    from tomato.util import Application
    from tomato.transport import HttpServerModule


    app = Application()
    app['http_server'] = HttpServerModule(host='localhost', port=1024, routes_list=[routes, ])
    # app.run()
    # app.stop()
    app.run_forever()


MySQL
-----

.. code-block:: python

    import asyncio
    from tomato.util import Application
    from tomato.store import MySQLModule
    from tomato.store import SqlClauseAssemble
    from tomato.store import SqlParamCollections


    app = Application()
    # setting parameter is a dictionary type
    app['mysql'] = MySQLModule(setting=mysql_setting)
    app.run()
    sql_assemble = SqlClauseAssemble()
    sql_assemble.wanted_words = ['platform_id', 'open_id']
    sql_assemble.table_name = '`app_account_users`'
    where_params = SqlParamCollections()
    where_params.add_normal_param(('open_id', '=', 18888888888, True))
    sql_assemble.where_params = where_params
    (sql, params) = sql_assemble.get_query_clause()
    print((sql, params))
    loop = asyncio.get_event_loop()
    result_list = loop.run_until_complete(app['mysql'].get_all(sql,params))
    print(result_list)
    app.stop()


Redis
-----

.. code-block:: python

    from tomato.util import Application
    from tomato.store import RedisModule


    app = Application()
    app['redis'] = RedisModule(setting=redis_setting)
    app.run()
    redis = RedisController()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(redis.set('my-key', 'my-value'))
    assert loop.run_until_complete(redis.get('my-key')) == 'my-value'
    app.stop()


Example
-------
- `server <https://github.com/igavintang/tomato/tree/main/examples>`_

- `mysql <https://github.com/igavintang/tomato/blob/main/tomato/store/mysql/sql_clause_assemble.py>`_


Dependent library
=================

- `aiohttp <https://github.com/aio-libs/aiohttp>`_


Other contributors
==================
- zhouqinmin: zqm175899960@163.com
