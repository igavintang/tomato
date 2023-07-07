'''
FilePath: /tomato/tomato/pay/wechatpay.py
Author: Gavin Tang
LastEditors: Gavin Tang
Description: WeChatPay
Date: 2023-05-04 16:23:27
LastEditTime: 2023-07-07 21:09:17
'''

# -*- coding:utf-8 -*-


import time
import json
import requests
import string
import base64
import random
import logging

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from tomato.util.singleton import singleton


class WeChatPayUtil(object):
    @staticmethod
    def signature(app_private_key_string, sign_str):
        """
        生成签名值
        app_private_key_string 私钥字符串
        sign_str 签名字符串
        https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_0.shtml
        """
        try:
            rsa_key = RSA.import_key(app_private_key_string)
            signer = PKCS1_v1_5.new(rsa_key)
            digest = SHA256.new(sign_str.encode('utf-8'))
            return base64.b64encode(signer.sign(digest)).decode('utf-8')
        except Exception:
            raise "WeChatPaySignIError"

@singleton
class WeChatPay(object):
    base_url = 'https://api.mch.weixin.qq.com'

    def __init__(self, *args, **kwargs):
        setting = kwargs.get('setting', None)
        if setting: kwargs.update(setting)
        self.mch_id = kwargs.get('mch_id')  # 直连商户号
        self.app_id = kwargs.get('app_id')  # 微信应用ID
        self.mch_serial_no = kwargs.get('mch_serial_no')  # # 商户API证书序列号
        self.cert_dir = kwargs.get('app_private_key')  # api client_key.pem 地址
        app_private_key = kwargs.get('app_private_key')
        with open(app_private_key) as file:
            self.app_private_key_string = file.read()
        self.apiv3_key = kwargs.get('apiv3_key')
        self.app_notify_url = kwargs.get('app_notify_url')  # 回调地址
        self.timeout_s = int(kwargs.get('timeout_s', 15))

    def _generate_request_sign(self, url_path, data, nonce_str, timestamp, method='POST'):
        """
        生成请求签名
        """
        sign_list = [method, url_path, timestamp, nonce_str]
        if data is not None:
            sign_list.append(data)
        else:
            sign_list.append('')
        sign_str = '\n'.join(sign_list) + '\n'

        logging.debug("sign_str: %s", sign_str)
        return WeChatPayUtil.signature(app_private_key_string=self.app_private_key_string, sign_str=sign_str)

    def _generate_pay_sign(self, app_id, data, nonce_str, timestamp):
        """
        生成支付签名
        """
        sign_list = [app_id, timestamp, nonce_str, data]
        sign_str = '\n'.join(sign_list) + '\n'
        return WeChatPayUtil.signature(app_private_key_string=self.app_private_key_string, sign_str=sign_str)

    def _generate_auth_header(self, signature, nonce_str, timestamp):
        """
        生成授权请求头
        """
        return f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",nonce_str="{nonce_str}",' \
               f'signature="{signature}",timestamp="{timestamp}",serial_no="{self.mch_serial_no}"'

    def trade_pay(self, pay_info):
        """
        APP下单API
        https://pay.wechatpay.cn/wiki/doc/apiv3/apis/chapter3_2_1.shtml
        """
        url_path = '/v3/pay/transactions/app'
        url = self.base_url + url_path

        data = {
            'appid': self.app_id,
            'mchid': pay_info['mch_id'] if 'mch_id' in pay_info else self.mch_id,
            'description': pay_info['subject'],
            'out_trade_no': pay_info['order_id'],
            'notify_url': pay_info['app_notify_url'] if 'app_notify_url' in pay_info else self.app_notify_url,
            'settle_info': {
                'profit_sharing': pay_info['profit_sharing'] if 'profit_sharing' in pay_info else False,
            },
            'amount': {
                'total': pay_info['original_amount'],
                'currency': pay_info['currency']
            },
        }

        if 'attach' in pay_info:
            data.update({'attach': pay_info['attach']})
        if 'expire_time' in pay_info:
            data.update({'time_expire': pay_info['expire_time']})
        if 'goods_tag' in pay_info:
            data.update({'goods_tag': pay_info['goods_tag']})
        if 'detail' in pay_info:
            data.update({'detail': pay_info['detail']})
        if 'scene_info' in pay_info:
            data.update({'scene_info': pay_info['scene_info']})

        timestamp = str(int(time.time()))
        nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
        data = json.dumps(data)
        signature = self._generate_request_sign(url_path=url_path, data=data, nonce_str=nonce_str, timestamp=timestamp)
        logging.debug("signature: %s", signature)

        logging.debug("Authorization signature: %s", self._generate_auth_header(signature, nonce_str, timestamp))
        headers = {'Authorization': self._generate_auth_header(signature, nonce_str, timestamp), 'Content-Type': 'application/json'}

        response = requests.post(url=url, data=data, headers=headers, timeout=self.timeout_s)
        prepay_info = json.loads(response.content)
        logging.debug("prepay_info: %s", prepay_info)

        # 支付签名
        pay_sign = self._generate_pay_sign(app_id=self.app_id, data=prepay_info['prepay_id'],
            nonce_str=nonce_str, timestamp=timestamp)
        return {
            'app_id': self.app_id,
            'partner_id': self.mch_id,
            'prepay_id': prepay_info['prepay_id'],
            'package_value': 'Sign=WXPay',
            'nonce_str': nonce_str,
            'timestamp': timestamp,
            'sign': pay_sign,
        }

    def decrypt_aesgcm(self, nonce, ciphertext, associated_data):
        nonce_bytes = str.encode(nonce)
        ad_bytes = str.encode(associated_data)
        data = base64.b64decode(ciphertext)

        key_bytes = str.encode(self.apiv3_key)
        aesgcm = AESGCM(key_bytes)
        return aesgcm.decrypt(nonce_bytes, data, ad_bytes).decode()
