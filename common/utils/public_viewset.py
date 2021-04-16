# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         public_viewset 
# Author:       lzq
# Date:         4/16/21 4:05 PM
#


from rest_framework.viewsets import ModelViewSet
from django.http import JsonResponse
from django.http.response import Http404
from django.http.request import QueryDict


class PublicModelViewSet(ModelViewSet):
    #  额外操作的字段方法
    def get_serializer(self, *args, **kwargs):
        serializer_fields = dict()
        if hasattr(self, 'serializer_fields') and isinstance(self.serializer_fields, dict):
            # 字段操作类型的字典循环
            for field_type in self.serializer_fields:
                # 每个类型下面的字段与action组合
                field_list = self.serializer_fields[field_type]
                field_set = list()
                # 每个组合下面的循环
                for field_dict in field_list:
                    # 当前操作匹配方法
                    if self.action in field_dict['action'] or 'all' in field_dict['action']:
                        field_set += field_dict['fields']
                if len(field_set) > 0:
                    serializer_fields[field_type] = list(set(field_set))
            if len(serializer_fields) > 0:
                kwargs['serializer_fields'] = serializer_fields
        if hasattr(self, 'primary_fields'):
            kwargs['primary_fields'] = self.primary_fields
        if hasattr(self, 'remove_fields'):
            kwargs['remove_fields'] = self.remove_fields
        if hasattr(self, 'custom_fields'):
            kwargs['fields'] = self.custom_fields
        if hasattr(self, 'serializer_depth'):
            kwargs['depth'] = self.serializer_depth
        if hasattr(self, 'show_fields'):
            kwargs['show_fields'] = self.show_fields
        return super(PublicModelViewSet, self).get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return self.check_detach_fields(super(PublicModelViewSet, self).create(request, *args, **kwargs))

    def partial_update(self, request, *args, **kwargs):
        return self.check_detach_fields(super(PublicModelViewSet, self).partial_update(request, *args, **kwargs))

    def check_detach_fields(self, response):
        if hasattr(self, 'detach_response_fields'):
            for field in self.detach_response_fields:
                if field in response.data:
                    del(response.data[field])
        return response

    @staticmethod
    def pk_resource(func):
        def wrapper(self, *args, **kwargs):
            try:
                instance = self.get_object()
            except Http404:
                return JsonResponse({'code': 10404, 'msg': f"{self.resource_name} <id:{kwargs['pk']}> 不存在."})
            serializer = self.get_serializer(instance)
            setattr(self, 'instance', instance)
            setattr(self, 'pk_resource', serializer.data)
            return func(self, *args, **kwargs)
        return wrapper

    @staticmethod
    def update_resource_info(func):
        def wrapper(self, request, *args, **kwargs):
            if isinstance(request.data, QueryDict):
                request.data._mutable = True
            request.data['update_user_id'] = request.user_data['id']
            return func(self, request, *args, **kwargs)
        return wrapper

    @staticmethod
    def create_resource_info(func):
        def wrapper(self, request, *args, **kwargs):
            if isinstance(request.data, QueryDict):
                request.data._mutable = True
            request.data['create_user_id'] = request.user_data['id']
            request.data['update_user_id'] = request.user_data['id']
            return func(self, request, *args, **kwargs)
        return wrapper
