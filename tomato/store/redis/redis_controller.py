#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      redis_controller.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @author:    steven(love.as.string@gmail.com)
    @date:      March 15, 2019
    @desc:      RedisController
"""

import logging
import datetime
from tomato.util.application import Application


class RedisController(object):

    def __init__(self):
        self.__redis_client = Application()['redis']

    async def get(self, key):
        return await self.__redis_client.execute('get', key)

    async def set(self, key, value):
        return await self.__redis_client.execute('set', key, value)

    async def zcard(self, key):
        return await self.__redis_client.execute('zcard', key)

    async def zrank(self, key, member):
        return await self.__redis_client.execute('zrank', key, member)

    async def zadd(self, key, score, member):
        return await self.__redis_client.execute('zadd', key, score, member)

    async def lpush(self, key, *values):
        return await self.__redis_client.execute('lpush', key, *values)

    async def hset(self, name, field, value):
        return await self.__redis_client.execute('hset', name, field, value)

    def __getattr__(self, attr):
        return getattr(self.__redis_client, attr)
