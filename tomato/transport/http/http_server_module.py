#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      http_server.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    Gavin Tang
    @date:      June 11, 2018
    @desc:      Basic http server functions and router rules encapsulation
"""

import json
import logging

from aiohttp import web
from urllib.parse import parse_qs

from tomato.util.appmodule import AppModule
from tomato.transport.http import index_html


class HttpServerModule(AppModule):

    def __init__(self, *args, **kwargs):
        super(HttpServerModule, self).__init__(*args, **kwargs)
        setting = kwargs.get('setting', None)
        if setting: kwargs.update(setting)
        self._host = args[0] if len(args) > 0 else kwargs.get('host', 'localhost')
        self._port = int(args[1] if len(args) > 1 else kwargs.get('port', '1024'))
        self._routes_list = kwargs.get('routes_list', [])
        self._app = web.Application(middlewares=[self.base_middleware,])
        self._app.router.add_route('get', '/', self.default_handler)
        for routes in self._routes_list:
            self._app.router.add_routes(routes)

    def setup(self):
        pass

    def parse_form_data(self, data):
        parsed_data = parse_qs(data)
        cleaned_data = {key: values[0] for key, values in parsed_data.items()}
        return cleaned_data

    async def run(self):
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self._host, self._port)
        await site.start()
        logging.info('serving on [%s]', site.name)

    async def destroy(self):
        await self._runner.cleanup()
        await self._app.shutdown()
        await self._app.cleanup()

    async def close(self):
        await self.destroy()

    def default_handler(self, request):
        response = web.Response(body=index_html.text.encode('utf-8'))
        response.headers['Content-Language'] = 'en'
        response.headers['Content-Type'] = 'text/html'
        return response

    @web.middleware
    async def base_middleware(self, request, handler):
        request.body = None
        if request.body_exists and request.can_read_body:
            request.body = await request.content.read()
            if request.content_type == 'application/json':
                try:
                    request.body = json.loads(request.body)
                except Exception as e:
                    logging.warning('Fail to parse request, err: %s', str(e))
                    return web.Response(body={'code': 'BAD_REQUEST',
                                              'msg': 'Bad request, '
                                              'please check parameters'},
                                              status=400,
                                              content_type='application/json')
            elif request.content_type == 'application/x-www-form-urlencoded':
                try:
                    from_data = request.body.decode(encoding='utf-8')
                    request.body = self.parse_form_data(from_data)
                except Exception as e:
                    logging.warning('Fail to parse request, err: %s', str(e))
                    return web.Response(body={'code': 'BAD_REQUEST',
                                              'msg': 'Bad request, '
                                              'please check parameters'},
                                              status=400,
                                              content_type='application/json')
        response = await handler(request)
        if isinstance(response, dict):
            headers = response['headers'] if 'headers' in response else {}
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
            return web.Response(body=response['body'] if 'body' in response else None,
                                status=response['status'] if 'status' in response else 200,
                                headers=headers)
        else:
            return web.Response(body=response)
