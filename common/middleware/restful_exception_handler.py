# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         restful_exception_handler
# Author:       lzq
# Date:         4/16/21 3:27 PM
#


from rest_framework.exceptions import ErrorDetail
from rest_framework.views import exception_handler


def restful_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:

        response_object = setCustomResponse(response)

        return response_object.set_custom_response()

    return response


class setCustomResponse:
    def __init__(self, response):
        self.response = response
        self.raw_data = self.translate_data_format()
        self.status_code = response.status_code
        self.http_response_context = {400: 'Input error', 401: "Auth failed",
                                      403: "Access denied", 404: "Not found",
                                      405: 'Request method error'}

    # 设置自定义状态码
    def set_custom_response(self):
        # return self.response
        self.response.data.clear()
        self.response.data.update({'ret': self.status_code, 'code': self.status_code})
        # 自定义的状态码函数 - 优先调用
        if hasattr(self, f"set_{self.status_code}_response"):
            getattr(self, f"set_{self.status_code}_response")()
        # 状态码在指定的http_response_context中
        elif self.status_code in self.http_response_context:
            self.set_http_response()
        # 错误码大于500的操作
        elif self.status_code >= 500:
            self.set_5xx_response()
        # 返回数据
        return self.response

    def set_400_response(self):
        return self.set_4xx_response()

    def set_404_response(self):
        return self.set_4xx_response()

    def set_415_response(self):
        return self.set_4xx_response()

    def set_http_response(self):
        self.response.status_code = 200
        self.response.data.update({'msg': self.http_response_context[self.status_code]})

    def set_4xx_response(self):
        self.response.status_code = 200
        try:
            msg = self.raw_data if isinstance(self.raw_data, str) else self.set_json_string(self.raw_data)
            self.response.data.update({'msg': msg})
        except KeyError:
            self.response.data.update({'msg': self.http_response_context[self.status_code]})

    # 大于500的状态码
    def set_5xx_response(self):
        self.response.data['msg'] = "Internal service errors"

    def translate_data_format(self):
        # filter_field = ['ret', 'code']
        result = {}
        for key in self.response.data:
            # if key not in filter_field:
            result[key] = self.response.data[key]
        return result

    def set_json_string(self, raw_data):
        def show_error_string(info):
            if isinstance(info, list) and len(info) > 0 and isinstance(info[0], ErrorDetail):
                return str(info[0])
            return info

        if isinstance(raw_data, list):
            return f"[{', '.join(raw_data)}]"
        elif isinstance(raw_data, dict):
            raw_data_list = [f"{x}: {show_error_string(raw_data[x])}" for x in raw_data]
            return f"[{' '.join(raw_data_list)}]"
