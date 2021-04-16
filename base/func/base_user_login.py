# -*- coding: utf-8 -*-#
#
# Project:      vocabulary
# Name:         base_user_login
# Author:       lzq
# Date:         2021/4/15 上午12:15
#

import re
import time
import json
import hashlib
from jwt import JWT
from jwt.jwk import OctetJWK
from django.conf import settings
from base.models import BaseUser
from base.serializers import BaseUserListSerializer
from common.utils.verify_parameter import VerifyParameter
from common.token.user_auth import BaseUserTokenAuth
from common.basic.redis_models import redis_resource_setx_value_by_key_value, \
    redis_resource_set_list_value, redis_resource_get_list_value, redis_resource_set_index_list_value


class BaseLoginMethod(VerifyParameter):

    @VerifyParameter.verify_check
    def check_user_login(self):
        username = self.verify_data['username']
        user_field = 'username'
        # email
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", username) is not None:
            user_field = 'email'
        # phone
        elif len(username) == 11 and re.match('^(1[34578][0-9]{9})$', username) is not None:
            user_field = 'phone'

        try:
            user_object = BaseUser.objects.get(**{user_field: username})
            if self.check_password(user_object):
                return {'code': 0, 'token': self.create_token(user_object)}
            return {'code': 401, 'msg': '用户名或密码错误.'}
        except BaseUser.DoesNotExist:
            return {'code': 401, 'msg': '用户名不存在.'}

    # 检查用户用户密码正确性
    def check_password(self, user):
        return user.password == hashlib.sha1(self.verify_data['password'].encode('utf-8')).hexdigest()

    # 生成token
    def create_token(self, user):
        # 荷载
        payload = {'exp': int(time.time()) + settings.JWT_CONF['EXPIRED_HOUR'] * 3600}
        # 用户信息
        user_fields = ['id', 'role_list', 'roles', 'username', 'avatar_url',
                       'cname', 'user_sn', 'email', 'phone', 'describe']
        user_dict = BaseUserListSerializer(user, fields=user_fields).data
        # print(f'user_dict: {user_dict}')
        payload.update(user_dict)
        # 生成token
        token = JWT().encode(payload, OctetJWK(bytes(settings.SECRET_KEY, 'utf-8')), alg='HS256')
        # 设置token缓存
        self.set_token_cache(token, payload)
        return token

    # 检查用户token
    def check_user_token(self, request):
        status, data_msg = BaseUserTokenAuth().verify_header_token(request)
        return {'code': 0 if status else 401, 'data' if status else 'msg': data_msg}

    # 注销用户token
    def user_logout_by_token(self, request):
        status, data_msg = BaseUserTokenAuth().verify_header_token(request)
        if not status:
            return {'code': 10401, 'msg': data_msg}

        token = request.COOKIES.get('user_token')
        return self.clean_user_token(data_msg, token=token)

    def set_token_cache(self, token, user_dict):
        token_md5 = hashlib.md5(token.encode(encoding='UTF-8')).hexdigest()
        token_key = f"token:md5:{token_md5}"
        user_key = f"user:token:{user_dict['id']}"
        # token 缓存
        redis_resource_setx_value_by_key_value(token_key, json.dumps(user_dict), settings.REDIS_TOKEN_EXPIRE)
        # token 存入对应用户的缓存
        redis_resource_set_list_value(user_key, token_md5, 3)

    def clean_user_token(self, user_dict, token=None, clean_all=True):

        user_key = f"user:token:{user_dict['id']}"
        if token is None and not clean_all:
            return {'code': 0, 'msg': '未传入有效token，无法清除.'}
        token_list = redis_resource_get_list_value(user_key)
        if clean_all:
            if len(token_list) > 0:
                redis_resource_set_list_value(user_key, '_', 1)
            return {'code': 0, 'msg': '清除用户token成功!' if len(token_list) > 0 else '用户token数据不存在.'}
        else:
            token_md5 = hashlib.md5(token.encode(encoding='UTF-8')).hexdigest()
            token_key = f"token:md5:{token_md5}"
            token_index = None if token_key not in token_list else token_list.index(token_key)
            if token_index is not None:
                redis_resource_set_index_list_value(user_key, token_index, '_')
            return {'code': 0, 'msg': '清除用户token成功!' if token_index is not None else '用户token数据不存在.'}



