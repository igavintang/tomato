#!/usr/bin/python
# -*- coding:utf-8 -*-

from aiohttp import web
from tomato.transport.http import Routes

routes = Routes()

@routes.get('/hello')
@routes.get('/hello/{name}')
async def hello(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)
