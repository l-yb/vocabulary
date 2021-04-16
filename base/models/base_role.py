# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         base_role
# Author:       lzq
# Date:         2021/4/10 下午2:05
#


from django.db import models


class BaseRole(models.Model):
    """
    系统基础角色表
    """
    name = models.CharField(u"角色名称", max_length=32, unique=True)
    code = models.CharField(u"角色代码", max_length=32, unique=True)
    describe = models.CharField(u"角色描述", max_length=128, blank=True, null=True)
    # 角色级别，从1开始，越小表示级别越高
    level = models.SmallIntegerField(u"角色级别")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    def __str__(self):
        return f"<BaseRole: {self.name}, {self.code}, {self.level}>"

    class Meta:
        db_table = 'base_role'
        verbose_name = '基础角色表'
        verbose_name_plural = verbose_name

