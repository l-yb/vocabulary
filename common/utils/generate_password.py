# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary 
# Name:         generate_password 
# Author:       lzq
# Date:         4/16/21 4:06 PM
#

import re
import string
from random import sample


def generate_password_str(length):
    length = 8 if length < 8 else length
    special_symbol = """!@#$%^&*()_+}{[]?"""
    re_symbol = r'[' + re.escape(special_symbol) + ']+'
    password_str = ''
    while (re.search(r'[0-9]+', password_str) is None or
           re.search(r'[a-z]+', password_str) is None or
           re.search(r'[A-Z]+', password_str) is None or
           re.search(re_symbol, password_str) is None):
        password_str = ''.join(sample(string.ascii_letters + special_symbol + string.digits, length))
    return password_str
