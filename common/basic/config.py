# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         config 
# Author:       lzq
# Date:         4/16/21 4:02 PM
#


# URL方法转换字典
URL_FUNC_DETAIL = {'post': 'partial_update', 'get': 'retrieve', 'delete': 'destroy'}

# 系统用户绑定/解绑角色参数
OPERATE_LIST = ['attach', 'detach']

# 应用程序添加/删除用户
MODIFY_LIST = ['add', 'remove']

# SINGLE_MATCH 简单正则匹配
SINGLE_MATCH = {'digit': r'^[0-9]+$', 'word': r'^[a-zA-Z0-9_-]+$'}

