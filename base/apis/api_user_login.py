# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         api_user_login
# Author:       lzq
# Date:         2021/4/16 下午3:38
#

from collections import OrderedDict
from rest_framework import viewsets
from django.http import JsonResponse
from base.func import BaseLoginMethod


class BaseCheckHealth(viewsets.ModelViewSet):
    permission_classes = []

    def check_health(self, request):
        return JsonResponse({'code': 0, 'health': 'OK'})


class UserLoginViewSet(viewsets.ModelViewSet):
    permission_classes = []

    login_args = [{'arg': 'username', 'empty': False, 'verify': OrderedDict([])},
                  {'arg': 'password', 'empty': False, 'verify': OrderedDict([])}]

    def user_login(self, request):
        # 参数验证对象初始化, 同时获取验证结果, 再根据判断后执行对应的方法
        return JsonResponse(BaseLoginMethod(request, self.login_args).check_user_login())

    def user_logout(self, request):
        return JsonResponse(BaseLoginMethod(request, []).user_logout_by_token(request))

    def check_login(self, request):
        return JsonResponse(BaseLoginMethod(request, []).check_user_token(request))
