# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         api_base_avatar 
# Author:       lzq
# Date:         2021/4/10 下午3:15
#

from django.conf import settings
from base.models import BaseAvatar
from common.utils import PublicModelViewSet
from base.serializers import BaseAvatarSerializer


class BaseAvatarViewSet(PublicModelViewSet):
    """
    系统头像视图
    """
    queryset = BaseAvatar.objects.all().order_by('id')
    serializer_class = BaseAvatarSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['server'] = settings.BASE_AVATAR_URL
        return response
