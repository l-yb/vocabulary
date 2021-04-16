# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         base_avatar 
# Author:       lzq
# Date:         2021/4/10 下午2:35
#


from base.models import BaseAvatar
from common.utils.dynamic_serializer import DynamicModelSerializer


class BaseAvatarSerializer(DynamicModelSerializer):

    class Meta:
        model = BaseAvatar
        fields = '__all__'
