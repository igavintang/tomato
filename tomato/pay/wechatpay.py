'''
FilePath: /tomato/tomato/pay/wechatpay.py
Author: Gavin Tang
LastEditors: Gavin Tang
Description: WeChat Payment
Date: 2023-05-04 16:23:27
LastEditTime: 2023-06-05 00:12:39
Copyright: ©2022 MaoMaoTrip All rights reserved.
'''

# -*- coding:utf-8 -*-


import time
import json
import requests
import string
import base64
import random

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class WeChatPayUtil(object):
    @staticmethod
    def signature(private_key_path, sign_str):
        """
        生成签名值
        private_key_path 私钥路径
        sign_str 签名字符串
        https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_0.shtml
        """
        with open(private_key_path) as file:
            private_key = file.read()
        try:
            rsa_key = RSA.import_key(private_key)
            signer = PKCS1_v1_5.new(rsa_key)
            digest = SHA256.new(sign_str.encode('utf-8'))
            return base64.b64encode(signer.sign(digest)).decode('utf-8')
        except Exception:
            raise "WeChatPaySignIError"


class WeChatPay(object):
    base_url = 'https://api.mch.weixin.qq.com'

    def __init__(self, mch_id, app_id, mch_serial_no, cert_dir, notify_url):
        self.mch_id = mch_id  # 直连商户号
        self.app_id = app_id  # 微信应用ID
        self.mch_serial_no = mch_serial_no  # # 商户API证书序列号
        self.cert_dir = cert_dir  # api client_key.pem 地址
        self.notify_url = notify_url  # 回调地址

        self.timestamp = str(int(time.time()))
        self.nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))

    def _generate_request_sign(self, url_path, data, method='POST'):
        """
        生成请求签名
        """
        sign_list = [method, url_path, self.timestamp, self.nonce_str]
        if data is not None:
            sign_list.append(data)
        else:
            sign_list.append('')
        sign_str = '\n'.join(sign_list) + '\n'

        print("sign_str:", sign_str)
        return WeChatPayUtil.signature(private_key_path=self.cert_dir, sign_str=sign_str)

    def _generate_pay_sign(self, app_id, package):
        """
        生成支付签名
        """
        sign_list = [app_id, self.timestamp, self.nonce_str, package]
        sign_str = '\n'.join(sign_list) + '\n'
        return WeChatPayUtil.signature(private_key_path=self.cert_dir, sign_str=sign_str)

    def _generate_auth_header(self, signature):
        """
        生成授权请求头
        """
        return f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",nonce_str="{self.nonce_str}",' \
               f'signature="{signature}",timestamp="{self.timestamp}",serial_no="{self.mch_serial_no}"'

    def unified_order(self, order_id, openid, amount, desc, mch_id=None, notify_url=None, profit_sharing=False,
                      expire_time=None, attach=None, goods_tag=None, detail=None, scene_info=None, currency='CNY'):
        """
        统一下单
        https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_1_1.shtml
        """
        url_path = '/v3/pay/transactions/jsapi'
        url = self.base_url + url_path

        data = {
            'appid': self.app_id,
            'mchid': mch_id if mch_id is not None else self.mch_id,
            'description': desc,
            'out_trade_no': order_id,
            'notify_url': notify_url if notify_url is not None else self.notify_url,
            'settle_info': {
                'profit_sharing': profit_sharing
            },
            'amount': {
                'total': amount,
                'currency': currency
            },
            'payer': {
                'openid': openid
            }
        }

        if attach:
            data.update({'attach': attach})
        if expire_time:
            data.update({'time_expire': expire_time})
        if goods_tag:
            data.update({'goods_tag': goods_tag})
        if detail:
            data.update({'detail': detail})
        if scene_info:
            data.update({'scene_info': scene_info})

        data = json.dumps(data)
        signature = self._generate_request_sign(url_path=url_path, data=data)
        print("signature:", signature)

        print("Authorization signature:", self._generate_auth_header(signature))
        headers = {'Authorization': self._generate_auth_header(signature), 'Content-Type': 'application/json'}

        res = requests.post(url=url, data=data, headers=headers, timeout=10)

        print("res:", json.loads(res.content))
