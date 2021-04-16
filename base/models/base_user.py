# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         base_user 
# Author:       lzq
# Date:         2021/4/10 下午1:38
#

from django.db import models
from .base_role import BaseRole


class BaseUser(models.Model):
    """
    系统基础用户表
    """

    username = models.CharField(u"用户名", max_length=128, unique=True)
    password = models.CharField(u"密码", max_length=128)
    cname = models.CharField(u"中文名", max_length=64, unique=True)
    user_sn = models.IntegerField(u"工号", unique=True)
    department = models.CharField(u"部门", max_length=128, blank=True, null=True)
    email = models.CharField(u"邮箱", max_length=64, unique=True, blank=True, null=True)
    phone = models.CharField(u"手机", max_length=16, unique=True, blank=True, null=True)
    avatar = models.ForeignKey('BaseAvatar', verbose_name="用户头像", default=1, on_delete=models.PROTECT)
    role_list = models.ManyToManyField(BaseRole, verbose_name="系统角色", related_name="user_list")
    describe = models.CharField(u"描述", max_length=128, blank=True, null=True)
    status = models.BooleanField(u"状态", default=1)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    def __str__(self):
        return f"<BaseUser {self.cname}: {self.user_sn}>"

    class Meta:
        db_table = 'base_user'
        verbose_name = "基础用户表"
        verbose_name_plural = verbose_name
