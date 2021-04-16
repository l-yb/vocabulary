# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         user_urls 
# Author:       lzq
# Date:         4/16/21 3:51 PM
#


from django.conf.urls import url
from base.apis import BaseUserViewSet, UserLoginViewSet, BaseAvatarViewSet
from common.utils import pubic_url_patterns

base_user_urls = pubic_url_patterns(BaseUserViewSet)

base_user_urls += [
    # 登录获取token
    url(r'^login$', UserLoginViewSet.as_view({'post': 'user_login'})),
    url(r'^logout$', UserLoginViewSet.as_view({'post': 'user_logout'})),
    # 验证登录后的token状态
    url(r'^checklogin$', UserLoginViewSet.as_view({'get': 'check_login'})),

    # 用户头像接口
    url(r'^avatar/list$', BaseAvatarViewSet.as_view({'get': 'list'})),

    # 系统用户授予/解绑角色
    url(r'^(?P<operate>\w+)/role/(?P<pk>\d+)$', BaseUserViewSet.as_view({'post': 'user_role_relation'})),

]
