# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         redis_models 
# Author:       lzq
# Date:         2021/4/16 下午7:48
#


import json
from django.conf import settings


# 根据搜索条件查询key
def redis_resource_get_key_by_rule(rule):
    return settings.REDIS_CACHE.keys(rule)


# 获取所有value
def redis_resource_get_value_by_keylist(keys):
    return [json.loads(settings.REDIS_CACHE.get(x)) for x in keys]


# 根据搜索条件查询key和value
def redis_resource_get_value_by_rule(rule, format='list'):
    key_list = settings.REDIS_CACHE.keys(rule)
    if format == 'dict':
        return {x: json.loads(settings.REDIS_CACHE.get(x)) for x in key_list}
    return [json.loads(settings.REDIS_CACHE.get(x)) for x in key_list]


# 获取所有value
def redis_resource_get_value_by_key(key, dataType=None):
    result = settings.REDIS_CACHE.get(key)

    if result is None:
        if dataType is None:
            return None
        return []

    return json.loads(result)


# 设置key, value 和过期时间
def redis_resource_setx_value_by_key_value(key, value, time):
    settings.REDIS_CACHE.setex(key, time, value)


# 删除key
def redis_resource_del_key(key):
    return settings.REDIS_CACHE.delete(key)


# 设置列表字符串，如果传长度参数，重置key长度
def redis_resource_set_list_value(key, value, length=0):
    settings.REDIS_CACHE.lpush(key, value)
    if length != 0:
        settings.REDIS_CACHE.ltrim(key, 0, length-1)


# 修改列表中的指定索引的值
def redis_resource_set_index_list_value(key, index, value):
    settings.REDIS_CACHE.lset(key, index, value)


# 获取列表数据
def redis_resource_get_list_value(key, start=0, end=-1):
    return settings.REDIS_CACHE.lrange(key, start, end)

