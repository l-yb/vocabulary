# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         request_decorator 
# Author:       lzq
# Date:         4/16/21 4:10 PM
#


import json
from django.http import JsonResponse
from common.token.user_auth import BaseUserTokenAuth


# 访问资源限制的装饰器
def require_role_decorator(role_info):
    def verify_role(func):
        def wrapper(request, *args, **kwargs):
            # 初始化装饰器变量, 指定的角色信息
            if not (isinstance(role_info, str) or isinstance(role_info, int) or isinstance(role_info, list)):
                return JsonResponse({'code': 10086, 'msg': '装饰设置角色的参数类型: 字符串, 数值或列表.'})
            elif not isinstance(role_info, list):
                role_list = [role_info]
            else:
                role_list = role_info
            if len(role_list) == 0:
                return JsonResponse({'code': 10086, 'msg': '装饰器允许访问的角色为空.'})
            # 用户当前token校验和全局信息
            if hasattr(request, 'request'):
                token_status, user_data = BaseUserTokenAuth().verify_header_token(request.request)
            else:
                token_status, user_data = BaseUserTokenAuth().verify_header_token(request)
            if not token_status:
                return JsonResponse({'code': 10401, 'msg': user_data})
            # 设置的角色类型
            role_level = [x for x in role_list if isinstance(x, int)]
            role_code = [x for x in role_list if isinstance(x, str)]
            if len(role_level) == len(role_list):
                role_field = 'level'
                allow_role_list = role_level
            elif len(role_code) == len(role_list):
                role_field = 'code'
                allow_role_list = role_code
            else:
                return JsonResponse({'code': 10086, 'msg': '装饰设置角色的字段只能是level和code其中之一.'})
            # 当前用户授予的角色不能为空
            if len(user_data['role_list']) == 0:
                return JsonResponse({'code': 10019, 'msg': '当前用户未授予角色'})
            # 用户所属的系统角色
            # print(f"user_data: {user_data}")
            user_role_list = list(set([x[role_field] for x in user_data['role_list']]))
            # 这里的判断分两种情况
            if role_field == 'level':
                # 如果传入的是角色级别，高级别角色可以访问低级别角色的资源
                user_allow_role = [x for x in user_role_list if len(list(filter(lambda y: x <= y, allow_role_list)))> 0]
            else:
                # 如果传入的是角色编码，不能跨级或降级访问，明确指定的角色编码才可以访问
                user_allow_role = list(filter(lambda x: x in allow_role_list, user_role_list))

            if len(user_allow_role) == 0:
                msg = f"系统角色: {', '.join(allow_role_list)}, 用户角色: {', '.join(user_role_list)}"
                return JsonResponse({'code': 10019, 'msg': f"接口访问需要{msg}."})
            return func(request, *args, **kwargs)
        return wrapper
    return verify_role
