# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         base_user 
# Author:       lzq
# Date:         2021/4/10 下午2:31
#

import re
import hashlib
import django_filters
from django.conf import settings
from rest_framework import serializers
from .base_role import BaseRoleSerializer
from base.models import BaseUser, BaseRole
from common.utils.dynamic_serializer import DynamicModelSerializer


class BaseUserSerializer(DynamicModelSerializer):
    class Meta:
        model = BaseUser
        fields = '__all__'

    # 自定义用户名的验证
    def validate_username(self, value):
        value_str = str(value)
        if re.search(r'[a-zA-Z]+', value_str) is None:
            raise serializers.ValidationError(detail='用户名至少需要包含字母')
        elif re.match(r'^[0-9a-zA-Z\.\-\_]+$', value_str) is None:
            raise serializers.ValidationError(detail='用户只能是大小写字母、数字和[.-_@]的组合')
        return value

    # 自定义密码的验证
    def validate_password(self, value):
        value_str = str(value)
        if len(value) < 8:
            raise serializers.ValidationError(detail='密码长度不能小于8')
        if (re.search(r'[A-Z]+', value_str) is None or re.search(r'[0-9]+', value_str) is None) and \
                (re.search(r'[a-z]+', value_str) is None or re.search(r'[0-9]+', value_str) is None):
            raise serializers.ValidationError(detail='密码需要包含字母和数字')
        return hashlib.sha1(value.encode('utf-8')).hexdigest()


class BaseUserListSerializer(BaseUserSerializer):
    role_list = BaseRoleSerializer(many=True, fields=['id', 'code', 'level'])
    roles = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        return f"{settings.BASE_AVATAR_URL}/{obj.avatar.name}"

    def get_roles(self, obj):
        return list(obj.role_list.values_list('code', flat=True))


class BaseUserFilter(django_filters.rest_framework.FilterSet):
    """
    系统用户过滤
    """
    role = django_filters.NumberFilter(method='get_by_role')
    role_level = django_filters.NumberFilter('role__level')

    class Meta:
        model = BaseUser
        fields = ['role', 'role_level']

    def get_by_role(self, queryset, name, value):
        role_obj = BaseRole.objects.filter(id=value).first()
        if role_obj is None:
            user_id = []
        else:
            user_id = list(role_obj.user_list.values_list('id', flat=True))
        return queryset.filter(id__in=user_id)
