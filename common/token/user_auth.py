
# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         user_auth 
# Author:       lzq
# Date:         4/16/21 3:44 PM
#


import json
import time
import hashlib
from jwt import JWT
from jwt.jwk import OctetJWK
from django.conf import settings
from common.basic.redis_models import redis_resource_setx_value_by_key_value, \
    redis_resource_get_value_by_key, redis_resource_get_list_value


class BaseUserTokenAuth:
    def has_permission(self, request, view):
        token_status, _ = self.verify_header_token(request)
        return token_status

    def has_object_permission(self, request, view, obj):
        # print(f"obj: {obj}, view: {view}")
        if request.method in settings.SAFE_METHODS:
            return True
        return False

    def verify_header_token(self, request):
        # 单次请求的全局变量，装饰器可能提前校验并设置了值，如果不为None说明已校验成功，直接返回
        if hasattr(request, 'user_data'):
            token_data = request.user_data
            if isinstance(token_data, dict):
                # print(f"request 中包含了user: {token_data}")
                return True, token_data

        token = request.COOKIES.get('user_token')
        if token is None:
            return False, '当前token信息为空.'
        try:
            token_md5 = hashlib.md5(token.encode(encoding='UTF-8')).hexdigest()
            token_key = f"token:md5:{token_md5}"
            # 从redis缓存获取token数据
            token_data = redis_resource_get_value_by_key(token_key)
            refresh_token = True if token_data is None else False
            # 缓存不存在
            if token_data is None:
                token_data = JWT().decode(token, OctetJWK(bytes(settings.SECRET_KEY, 'utf-8')), algorithms=['HS256'])
            user_token_key = f"user:token:{token_data['id']}"
            # 用户缓存的token信息
            user_token_cache = redis_resource_get_list_value(user_token_key)
            if token_md5 not in user_token_cache:
                return False, f"用户 <{token_data['username']}> token已失效."
            # token超时时间已过期
            # print(f"token_data: {token_data}")
            if token_data['exp'] < int(time.time()):
                return False, 'User login is expired.'
            # 刷新本地token
            if refresh_token:
                redis_resource_setx_value_by_key_value(token_key, json.dumps(token_data), settings.REDIS_TOKEN_EXPIRE)
            # 单次请求的全局变量
            if not hasattr(request, 'user_data'):
                request.user_data = token_data
            return True, token_data
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            # print(f"{type(e)}: {dir(e)}")
            msg = f"token verify failed: {e}"
            return False, msg
