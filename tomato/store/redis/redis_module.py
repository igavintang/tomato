#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      redis_module.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @author:    steven(love.as.string@gmail.com)
    @date:      March 15, 2019
    @desc:      Redis module.
"""

import logging
import aioredis
from tomato.util.appmodule import AppModule


class RedisModule(AppModule):

    def __init__(self, *args, **kwargs):
        super(RedisModule, self).__init__(*args, **kwargs)
        setting = kwargs.get('setting', None)
        if setting: kwargs.update(setting)
        self._db = int(kwargs.get('db', 0))
        self._host = kwargs.get('host', 'localhost')
        self._port = int(kwargs.get('port', 6379))
        self._passwd = kwargs.get('passwd')
        self._minsize = int(kwargs.get('minsize'))
        self._maxsize = int(kwargs.get('maxsize'))
        self._encoding = 'utf-8'
        self._pool = None

    def setup(self):
        pass

    async def run(self):
        self._pool = await aioredis.create_redis_pool(
            (self._host, self._port),
            db=self._db,
            password=self._passwd,
            minsize=self._minsize,
            maxsize=self._maxsize,
            encoding=self._encoding)
        logging.info('redis connection success: redis://%s:%s'
            ';encoding=%s, db[%s] '
            'minsize[%s] maxsize[%s]',
            self._host, self._port, self._encoding,
            self._db, self._minsize, self._maxsize)

    async def destroy(self):
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()

    async def execute(self, command, *args, **kwargs):
        return await self._pool.execute(command, *args, **kwargs)

    def __getattr__(self, attr):
        return getattr(self._pool, attr)
