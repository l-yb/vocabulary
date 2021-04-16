# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         __init__.py 
# Author:       lzq
# Date:         4/16/21 3:51 PM
#


from django.conf.urls import url, include
from common.utils import pubic_url_patterns
from base.apis import BaseRoleViewSet, BaseCheckHealth
from .user_urls import base_user_urls


urlpatterns = [
    url(r'^role/', include(pubic_url_patterns(BaseRoleViewSet)), name="base-role"),
    url(r'^user/', include(base_user_urls), name="base-user"),
    url(r'^check/health$', BaseCheckHealth.as_view({'get': 'check_health'}), name="check-health"),
]
