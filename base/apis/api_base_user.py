# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         api_base_user 
# Author:       lzq
# Date:         2021/4/10 下午2:29
# 


from base.models import BaseUser
from collections import OrderedDict
from django.http import JsonResponse
from base.func import BaseUserRoleMethod
from rest_framework.filters import SearchFilter
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from common.utils import require_role_decorator, PublicModelViewSet
from common.basic.redis_models import redis_resource_set_list_value
from base.serializers import BaseUserSerializer, BaseUserListSerializer, BaseUserFilter


@method_decorator(require_role_decorator('manager'), name="dispatch")
class BaseUserViewSet(PublicModelViewSet):
    """
    系统用户视图
    """
    queryset = BaseUser.objects.all().order_by('id')
    serializer_class = BaseUserListSerializer
    resource_name = '系统用户'
    # 根据不同方法，操作不同类型的字段
    # primary: 用来申明主键字段
    # remove: 需要移除的字段
    serializer_fields = {'remove': [{'fields': ['password'], 'action': ['list', 'retrieve']}]}

    # 返回时需要去掉的字段
    detach_response_fields = ['password']

    # 使用过滤器
    filter_backends = (SearchFilter, DjangoFilterBackend,)
    # 引用自定义的过滤类
    filter_class = BaseUserFilter

    # 搜索字段
    search_fields = ('username', 'cname', 'user_sn', 'department', 'email', 'phone', 'describe')

    # 操作角色是需要传入的参数
    role_args = [{'arg': 'role_list', 'empty': False, 'verify': OrderedDict([('value_list', 'digit')])}]

    # 系统用户授予/解绑角色
    @PublicModelViewSet.pk_resource
    def user_role_relation(self, request, operate, pk):
        return JsonResponse(BaseUserRoleMethod(request, self.role_args).operate_user_role(self.instance, operate))

    def create(self, request, *args, **kwargs):
        self.serializer_class = BaseUserSerializer
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = BaseUserSerializer
        user_obj = self.get_object()
        user_old_role = list(user_obj.role_list.values_list('id', flat=True))
        response = super().partial_update(request, *args, **kwargs)
        user_new_role = list(user_obj.role_list.values_list('id', flat=True))
        # 角色变更，删除token
        if sorted(user_old_role) != sorted(user_new_role):
            redis_resource_set_list_value(f"user:token:{user_obj.id}", '_', 1)
        return response

    def list(self, request, *args, **kwargs):
        if str(request.query_params.get('simple', '0')) == '1':
            setattr(self, 'show_fields', ['id', 'username', 'user_sn', 'cname'])
        return super().list(request, *args, **kwargs)
