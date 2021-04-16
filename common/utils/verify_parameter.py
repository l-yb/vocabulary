# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         verify_parameter 
# Author:       lzq
# Date:         4/16/21 4:02 PM
#


import re
from hashlib import md5
from copy import deepcopy
from common.basic import config
from rest_framework.request import Request
from django.http import HttpRequest
from common.basic.redis_models import redis_resource_get_value_by_key, redis_resource_set_list_value, \
    redis_resource_get_list_value, redis_resource_del_key, redis_resource_set_index_list_value


# api url parameter public object
class VerifyParameter:
    # init function
    def __init__(self, request=None, verify_args=[]):
        self.request = request or Request(HttpRequest())
        self.verify_args = deepcopy(verify_args)  # 校验过程中会修改rule中的参数规则，深拷贝才能避免默认初始化参数被修改
        self.message = ''
        self.verify_data = {}
        if self.request.method == 'POST':
            # self.resource_form_info = request.get_json() or request.form.to_dict() or {}
            self.resource_form_info = request.data
            # print(f"resource_form_info: {self.resource_form_info}")
        else:
            self.resource_form_info = {}
        self.verify_status = self.verify_control()

    # public control
    # 验证参数的控制方法,根据传入字段分发执行对应的验证方法
    def verify_control(self):
        # POST 请求需要严格指定参数，传入多的参数时报错
        if self.request.method == 'POST':
            post_status = self.verify_post_data()
            if not post_status:
                return False

        # 循环参数进行验证
        for rule in self.verify_args:
            # 20200820新增功能, 当require字段存在时，empty字段发生改变
            if 'require' in rule and rule['empty']:
                for filed in rule['require']:
                    # 当require 的字段是预期值时，有default_by_require字段，则修改default属性，否则修改empty属性
                    if filed in self.verify_data and self.verify_data[filed] == rule['require'][filed]:
                        if 'default_by_require' in rule:
                            rule['default'] = rule['default_by_require']
                        else:
                            rule['empty'] = False
                            print(f"rule2: {rule}")
            # 获取参数值, 并判断是否可以为空
            value, verify_empty = self.verify_parameter_value(rule)

            if not verify_empty:
                # 为空校验失败
                return False
            elif rule['empty'] and value is None:
                # 允许为空, 并且值为空, 忽略后续检查
                continue
            # 循环检查方法
            for func, check in rule['verify'].items():
                # 检查方法不存在
                func_name = f"verify_field_{func}"
                if not hasattr(self, func_name):
                    self.message = f"unknown verify function [{func_name}] for parameter: {rule['arg']} "
                    return False
                # 执行检查方法, check参数为空则不传
                if check == '':
                    verify_status = getattr(self, func_name)(rule)
                else:
                    verify_status = getattr(self, func_name)(rule, check)
                # 检查失败
                if not verify_status:
                    return verify_status
        return True

    # 根据请求方法获取参数的值, 返回值 + 为空检查
    def verify_parameter_value(self, rule):
        arg, empty = rule['arg'], rule['empty']
        map_key = rule['map'] if 'map' in rule else None
        if 'default' in rule and type(rule['default']).__name__ == 'function':
            rule['default'] = rule['default']()
        default_value = rule['default'] if 'default' in rule else None
        if self.request.method == 'GET':
            value = self.request.GET.get(arg) or None
        elif arg in self.resource_form_info:
            value = self.resource_form_info[arg]
        else:
            value = None
        # 不允许为空时，传入空值('')会被强制清理
        if value == '' and not empty:
            value = None
        # 允许为空时，传入空值(''), 如果不想保存空数据，需要传入remove_none（代表控制即为None）, 否则空值''将替换已有值
        elif value == '' and empty:
            if 'remove_none' in rule and rule['remove_none']:
                value = None
        # 允许为空时，并且是空值，先查看是否有默认值
        if value is None and empty:
            value = default_value
        # 不允许为空，数据为空时，验证失败
        if value is None and not empty:
            self.message = f'parameter: [{arg}] is empty.'
            return value, False
        if value is not None:
            self.verify_data[map_key or arg] = value
        return value, True

    # POST 请求需要严格指定参数，传入多的参数时报错
    def verify_post_data(self):
        verify_field_key = [rule['arg'] for rule in self.verify_args]
        for key in self.resource_form_info:
            if key not in verify_field_key:
                self.message = f'unknown parameter: {key}.'
                return False
        return True

    # 验证单个请求参数
    def verify_field_single(self, rule, check):
        parameter = rule['arg']
        map_key = rule['map'] if 'map' in rule else None
        if check not in config.SINGLE_MATCH:
            self.message = f'unknown single check [{check}] for unknown parameter: {parameter}.'
        # 参数值进行正则匹配
        elif re.match(config.SINGLE_MATCH[check], str(self.verify_data[parameter])) is None:
            self.message = f'parameter: {parameter} value [{self.verify_data[parameter]}] is not match {check} type.'
        else:
            if check == 'digit':
                self.verify_data[map_key or parameter] = int(self.verify_data[parameter])
            return True
        return False

    # 验证是否属于布尔值
    def verify_field_builtin_type(self, rule, cType):
        parameter = rule['arg']
        map_key = rule['map'] if 'map' in rule else None
        value = self.verify_data[map_key or parameter]
        if not isinstance(value, cType):
            self.message = f'parameter: {parameter} value <{str(value)[0:10]}>: is not {cType.__name__}.'
            return False
        # print(f'parameter: {parameter} value [{self.verify_data[parameter]}] is boolean.')
        return True

    # 验证是否属于布尔值
    def verify_field_boolean(self, rule):
        return self.verify_field_builtin_type(rule, bool)

    # 验证是否属于dict
    def verify_field_dict(self, rule):
        return self.verify_field_builtin_type(rule, dict)

    # 验证是否包含指定字符串
    def verify_field_contain(self, rule, keyword):
        parameter = rule['arg']
        map_key = rule['map'] if 'map' in rule else None
        value = self.verify_data[map_key or parameter]
        if value.find(keyword) == -1:
            self.message = f'parameter: {parameter} value [{value}] is not contain: <{keyword}>.'
            return False
        return True

    def verify_field_value_list(self, rule, dataType):
        parameter = rule['arg']
        map_key = rule['map'] if 'map' in rule else None
        value = self.verify_data[map_key or parameter]
        if not isinstance(value, list):
            self.message = f'parameter: {parameter} value [{value}: {type(value)}] is not list type.'
            return False
        if len(value) == 0 and not ('length' in rule and rule['length'] == 0):
            self.message = f'parameter: {parameter} value {value} is zero length.'
            return False
        if dataType == 'digit':
            for x in value:
                if not isinstance(x, int):
                    self.message = f'parameter: {parameter} value [{value}: {type(value)}] is not digit list.'
                    return False
        elif dataType == 'dict':
            for x in value:
                if not isinstance(x, dict):
                    self.message = f'parameter: {parameter} value [{value}: {type(value)}] is not dict list.'
                    return False
        return True

    def verify_field_special_list(self, rule, data):
        parameter = rule['arg']
        map_key = rule['map'] if 'map' in rule else None
        value = self.verify_data[map_key or parameter]
        if not ('length' not in rule or rule['length'] != 0 or len(value) != 0):
            self.message = f'parameter: {parameter} value {value} is zero length.'
            return False
        if value not in data:
            self.message = f"parameter: {parameter} value [{value}: {type(value).__name__}] is not in {data}."
            return False
        return True

    # 验证响应结构体
    def verify_response(self):
        return {'method': self.request.method, 'url': self.request.path,
                'parameter': self.verify_data, 'message': self.message,
                'verify_status': self.verify_status, 'code': 20007}

    @staticmethod # 内部检查，func类初始化之后的
    def verify_check(func):
        def wrapper(self, *args, **kwargs):
            # 验证失败直接返回
            if not self.verify_status:
                return self.verify_response()
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def refresh_user_token(user_id):
        user_token_active_list = f"sh:user:auth:{user_id}"
        token_list = redis_resource_get_list_value(user_token_active_list)
        # print(f"token_list: {token_list}")
        for token_md5 in token_list:
            if token_md5 == '_':
                continue
            token_key = f"sh:token:{token_md5}"
            token_cache = redis_resource_get_value_by_key(token_key)
            if token_cache is not None:
                redis_resource_del_key(token_key)

    def clean_user_token(self, user_id, token=None, clean_all=True):
        if token is None and not clean_all:
            return {'code': 0, 'message': '未传入有效token，无法清除.'}
        user_token_active_list = f"sh:user:auth:{user_id}"
        token_list = redis_resource_get_list_value(user_token_active_list)
        if clean_all:
            if len(token_list) > 0:
                redis_resource_set_list_value(user_token_active_list, '_', 1)
            return {'code': 0, 'message': '清除用户token成功!' if len(token_list) > 0 else '用户token数据不存在.'}
        else:
            token_md5 = md5(token.encode(encoding='UTF-8')).hexdigest()
            # token_key = f"sh:token:{token_md5}"
            token_index = None if token_md5 not in token_list else token_list.index(token_md5)
            if token_index is not None:
                redis_resource_set_index_list_value(user_token_active_list, token_index, '_')
            return {'code': 0, 'message': '清除用户token成功!' if token_index is not None else '用户token数据不存在.'}
