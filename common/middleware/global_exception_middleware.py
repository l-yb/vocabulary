# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         global_exception_middleware
# Author:       lzq
# Date:         4/16/21 3:26 PM
#


import django
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


# 定义中间件类，处理全局异常
class GlobalExceptionMiddleware(MiddlewareMixin):
    # 如果注册多个process_exception函数，那么函数的执行顺序与注册的顺序相反。(其他中间件函数与注册顺序一致)
    # 中间件函数，用到哪个就写哪个，不需要写所有的中间件函数。
    def process_exception(self, request, exception):
        import traceback
        print(traceback.format_exc())
        '''视图函数发生异常时调用'''
        # print('----process_exception1----')
        exception_type = str(type(exception)).replace("<class '",'').replace("'>",'')
        # 默认错误码10099
        msg_info = {'code': 10099, 'exception': exception_type, 'env': settings.ENVIRONMENT,
                    'msg': f"{exception_type}: {str(exception)}", 'level': 1}
        # 数据库字段错误
        if isinstance(exception, django.core.exceptions.FieldError) or \
                isinstance(exception, django.core.exceptions.FieldDoesNotExist) or \
                isinstance(exception, django.core.exceptions.TooManyFieldsSent):
            msg_info.update({'code': 1004})
        settings.STUDY_LOG.exception(msg_info)
        return JsonResponse(msg_info)
