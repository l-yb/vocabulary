# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         api_base_role 
# Author:       lzq
# Date:         2021/4/10 下午3:15
#


from base.models import BaseRole
from rest_framework.filters import SearchFilter
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from common.utils import require_role_decorator, PublicModelViewSet
from base.serializers import BaseRoleSimpleSerializer, BaseRoleSerializer, BaseRoleFilter


@method_decorator(require_role_decorator(['manager']), name="dispatch")
class BaseRoleViewSet(PublicModelViewSet):
    """
    系统角色视图
    """
    queryset = BaseRole.objects.all().order_by('id')
    serializer_class = BaseRoleSerializer

    serializer_fields = {'remove': [{'fields': ['user_list'], 'action': ['create', 'partial_update']}]}

    # 使用过滤器
    filter_backends = (SearchFilter, DjangoFilterBackend,)
    # 引用自定义的过滤类
    filter_class = BaseRoleFilter

    # 搜索字段
    search_fields = ('name', 'code', 'describe')

    def list(self, request, *args, **kwargs):
        if str(request.query_params.get('simple', '0')) == '1':
            self.serializer_class = BaseRoleSimpleSerializer
            setattr(self, 'show_fields', ['id', 'name', 'code', 'level', 'user_count'])
        return super().list(request, *args, **kwargs)
