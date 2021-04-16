# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         base_role 
# Author:       lzq
# Date:         2021/4/10 下午2:35
#


import django_filters
from rest_framework import serializers
from base.models import BaseUser, BaseRole
from common.utils import DynamicModelSerializer


class _baseUserSerializer(DynamicModelSerializer):
    class Meta:
        model = BaseUser
        fields = '__all__'


class BaseRoleSerializer(DynamicModelSerializer):
    user_list = _baseUserSerializer(many=True, fields=['id', 'user_sn', 'cname', 'username'])

    class Meta:
        model = BaseRole
        fields = '__all__'


class BaseRoleSimpleSerializer(BaseRoleSerializer):
    user_count = serializers.SerializerMethodField()

    def get_user_count(self, obj):
        return obj.user_list.count()


class BaseRoleFilter(django_filters.rest_framework.FilterSet):
    """
    系统角色过滤
    """
    level = django_filters.NumberFilter('level')

    class Meta:
        model = BaseRole
        fields = ['level']
