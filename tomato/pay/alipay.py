'''
FilePath: /tomato/tomato/pay/alipay.py
Author: Gavin Tang
LastEditors: Gavin Tang
Description: AliPay
Date: 2023-05-04 16:23:27
LastEditTime: 2023-07-07 20:03:51
'''

# -*- coding:utf-8 -*-


from tomato.util.singleton import singleton

from alipay import AliPay as AliPayModule
from alipay.utils import AliPayConfig


@singleton
class AliPay(object):
    def __init__(self, *args, **kwargs):
        setting = kwargs.get('setting', None)
        if setting: kwargs.update(setting)
        self._app_id = kwargs.get('app_id')
        app_notify_url = kwargs.get('app_notify_url')  # 默认回调url为空
        app_private_key = kwargs.get('app_private_key')
        with open(app_private_key) as file:
            app_private_key_string = file.read()
        alipay_public_key = kwargs.get('alipay_public_key')
        with open(alipay_public_key) as file:
            alipay_public_key_string = file.read()
        sign_type = kwargs.get('sign_type', 'RSA2')
        timeout_s = int(kwargs.get('timeout_s', 15))
        self._alipay = AliPayModule(
            appid = self._app_id,
            app_notify_url = app_notify_url,
            app_private_key_string = app_private_key_string,
            alipay_public_key_string = alipay_public_key_string,
            sign_type = sign_type,  # RSA 或者 RSA2
            debug = False,  # 默认 False
            verbose = False,  # 输出调试数据
            config = AliPayConfig(timeout=timeout_s)  # 可选，请求超时时间
        )

    def trade_pay(self, pay_info):
        order_string = self._alipay.api_alipay_trade_app_pay(
            out_trade_no=pay_info['order_id'],
            total_amount=pay_info['original_amount'] / 100,
            subject=pay_info['subject']
        )
        return {
            'app_id': self._app_id,
            'order_string': order_string,
        }

    def verify_sign(self, data):
        signature = data.pop('sign')
        return self._alipay.verify(data, signature)
