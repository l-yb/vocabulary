# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         pagination 
# Author:       lzq
# Date:         4/16/21 4:07 PM
#


from rest_framework import pagination


class PageNumberPagination(pagination.PageNumberPagination):
    """查第n页，每页显示n条数据"""
    page_size = 10  # 指定每页显示多少条数据
    max_page_size = 1500  # 每页最多显示多少条数据
    page_size_query_param = 'size'  # URL参数中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
