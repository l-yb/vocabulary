# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         custom_request_and_response_middleware
# Author:       lzq
# Date:         4/16/21 3:32 PM
# 


from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


# 自定义请求响应处理中间件
class CustomRequestAndResponseMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        if isinstance(response, JsonResponse):
            return response

        if response.status_code in [201, 204]:
            try:
                raw = dict(response.data) if response.data is not None else None
            except:
                raw = response.data
            if raw is None and response.status_code == 204:
                raw = "204 No Content"
            data = {'ret': response.status_code, 'code': 0, 'data': raw}
            return JsonResponse(data)
        elif response.status_code == 200 and \
                ('code' not in response.data or ('code' in response.data and 'id' in response.data)):
            return JsonResponse(self.set_200_response(response.data))

        return response

    def set_200_response(self, data):
        result = {'code': 0}
        if 'count' in data and 'results' in data:
            result['data'] = data.pop('results')
            result['total'] = data.pop('count')
            result['current'] = len(result['data'])
            result.update(data)
        else:
            result['data'] = dict(data)
        return result
