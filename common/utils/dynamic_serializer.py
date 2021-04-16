# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         dynamic_serializer 
# Author:       lzq
# Date:         4/16/21 4:06 PM
#


from rest_framework import serializers


class DynamicModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        depth = kwargs.pop('depth', None)
        serializer_fields = kwargs.pop('serializer_fields', None)
        primary_fields = kwargs.pop('primary_fields', None)
        remove_fields = kwargs.pop('remove_fields', None)

        if fields is None:
            fields = kwargs.pop('show_fields', None)

        # Instantiate the superclass normally
        super(DynamicModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if depth is not None:
            self.Meta.depth = depth
        elif getattr(self.Meta, 'depth', None) is not None:
            self.Meta.depth = None

        # 额外定义的数据字段转换
        if serializer_fields is not None and isinstance(serializer_fields, dict):
            # 每种类型的字段转换操作
            # print(f"serializer_fields: {serializer_fields}")
            for field_type in serializer_fields:
                field_list = serializer_fields[field_type]
                for field_name in field_list:
                    if field_type == 'primary':
                        new_field = f"{field_name}_id"
                        self.fields[field_name] = serializers.PrimaryKeyRelatedField(read_only=True)
                        self.fields[new_field] = serializers.IntegerField()
                    elif field_type == 'remove' and field_name in self.fields:
                        self.fields.pop(field_name)

        # 外键数据的字段转换
        if primary_fields is not None and isinstance(primary_fields, list):
            for field_name in primary_fields:
                new_field = f"{field_name}_id"
                self.fields[field_name] = serializers.PrimaryKeyRelatedField(read_only=True)
                self.fields[new_field] = serializers.IntegerField()

        # 移除的字段转换
        if remove_fields is not None and isinstance(remove_fields, list):
            for field_name in remove_fields:
                self.fields.pop(field_name)
