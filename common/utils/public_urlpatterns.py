# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         public_urlpatterns 
# Author:       lzq
# Date:         4/16/21 4:01 PM
#


from django.conf.urls import url

# URL方法转换字典
URL_FUNC_DETAIL = {'post': 'partial_update', 'get': 'retrieve', 'delete': 'destroy'}


# 通用url生成方法
def pubic_url_patterns(view_set, exclude=[]):
    url_list = list()
    if 'create' not in exclude:
        url_list.append(url(r'^create$', view_set.as_view({'post': 'create'})))
    if 'list' not in exclude:
        url_list.append(url(r'^list', view_set.as_view({'get': 'list'})))
    detail_func = dict()
    for func in URL_FUNC_DETAIL:
        if func not in exclude:
            detail_func[func] = URL_FUNC_DETAIL[func]
    if len(detail_func) > 0:
        url_list.append(url(r'^(?P<pk>\d+)$', view_set.as_view(URL_FUNC_DETAIL)))
    return url_list
