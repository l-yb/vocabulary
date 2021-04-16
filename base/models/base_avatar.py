# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         base_avatar 
# Author:       lzq
# Date:         2021/4/24 下午3:43
#


from django.db import models


class BaseAvatar(models.Model):
    """
    基础图标表
    """
    name = models.CharField(u"图片名称", max_length=128, unique=True)

    def __str__(self):
        return f"<BaseAvatar: {self.id}, {self.name}>"

    class Meta:
        db_table = 'base_avatar'
        verbose_name = '基础图标表'
        verbose_name_plural = verbose_name
