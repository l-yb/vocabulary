# -*- coding: utf-8 -*-#
# 
# Project:      vocabulary
# Name:         base_user_role 
# Author:       lzq
# Date:         2021/4/17 下午3:47
#


from base.models import BaseRole
from common.basic import config
from common.utils.verify_parameter import VerifyParameter
from common.basic.redis_models import redis_resource_set_list_value


class BaseUserRoleMethod(VerifyParameter):

    @VerifyParameter.verify_check
    def operate_user_role(self, instance, operate):
        if operate not in config.OPERATE_LIST:
            return {'code': 10010, 'msg': f"url参数operate: {operate} 指定不正确, 预期值: {config.OPERATE_LIST}."}
        current_role_list = instance.role_list.all()
        current_role_id = [role.id for role in current_role_list]
        operate_success = list()
        operate_not_exist = list()
        operate_ignore = list()
        operate_failed = list()
        for role_id in self.verify_data['role_list']:
            role_obj = BaseRole.objects.filter(id=role_id).first()
            if role_obj is None:
                operate_not_exist.append(str(role_id))
                continue
            if (operate == 'attach' and role_id in current_role_id) or \
                    (operate == 'detach' and role_id not in current_role_id):
                operate_ignore.append(role_obj.name)
                continue
            try:
                if operate == 'attach':
                    instance.role_list.add(role_obj)
                else:
                    instance.role_list.remove(role_obj)
                operate_success.append(role_obj.name)
            except Exception as e:
                operate_failed.append(f"role<{role_obj.name}>:{e}")
            instance.save()

        operate_msg = '授予' if operate == 'attach' else '解绑'
        ignore_msg = '已绑定' if operate == 'attach' else '未绑定'
        ret_code = 10020 if len(operate_success) == 0 else 0
        msg_list = [f"{len(operate_success)}个成功"]
        if len(operate_success) > 0:
            msg_list[0] = msg_list[0] + f"[{', '.join(operate_success)}]"
        if len(operate_ignore) > 0:
            msg_list.append(f"{ignore_msg}{len(operate_ignore)}个[{', '.join(operate_ignore)}]")
        if len(operate_not_exist) > 0:
            msg_list.append(f"不存在{len(operate_not_exist)}个[id:{', '.join(operate_not_exist)}]")
        if len(operate_failed) > 0:
            msg_list.append(f"失败{len(operate_failed)}个[{', '.join(operate_failed)}]")

        # 修改角色成功，强制刷新用户token
        if ret_code == 0:
            redis_resource_set_list_value(f"user:token:{instance.id}", '_', 1)
        return {'code': ret_code, 'msg': f"系统用户{operate_msg}角色: {', '.join(msg_list)}"}
