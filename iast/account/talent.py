#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:owefsad
# datetime:2021/1/18 下午2:16
# software: PyCharm
# project: lingzhi-webapi
import time

from django.contrib.auth.models import Group
from django.db import transaction, DatabaseError
from django.http import JsonResponse

from iast.base.system import SystemEndPoint
from iast.models import User
from iast.models.department import Department
from iast.models.talent import Talent
from iast.serializers.talent import TalentSerializer


class TalentEndPoint(SystemEndPoint):
    name = 'api-v1-talent'
    description = '租户管理'

    def get(self, request):
        """
        查询所有租户
        :param request:
        :return:
        """
        queryset = Talent.objects.all()

        # todo 处理查询条件
        name = request.query_params.get('name')
        if name:
            queryset = queryset.filter(talent_name__icontains=name)

        created = request.query_params.get('created')
        if created:
            users = User.objects.filter(username__icontains=created).values('id')
            ids = [_['id'] for _ in users] if users else []
            queryset = queryset.filter(created_by__in=ids)

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('pageSize', 10))
        page_summary, proall = self.get_paginator(queryset, page, page_size)
        return JsonResponse({
            'status': 201,
            'msg': '',
            'data': TalentSerializer(queryset, many=True).data,
            "page": page_summary,
            "total": len(queryset)
        })

    def post(self, request, pk):
        """
        修改租户
        :param request:
        :param pk:
        :return:
        """
        talent = Talent.objects.filter(id=pk).first()
        if talent and talent.is_active:
            talent.created_by = request.user.id
            talent.update_time = int(time.time())

            talent_name = request.data.get('talent_name')
            if talent_name:
                talent.talent_name = talent_name

            is_active = request.data.get('is_active')
            if is_active:
                talent.is_active = bool(is_active)

            talent.save()

            return JsonResponse({
                'status': 201,
                'msg': 'success'
            })
        else:
            return JsonResponse({
                'status': 202,
                'msg': '租户已停用' if talent else '租户不存在'
            })

    def put(self, request):
        """
        新增租户
        :param request:
        :return:
        """
        talent_name = request.data.get('talent_name', None)
        talent_email = request.data.get('email', None)
        if talent_name is None or talent_email is None:
            return JsonResponse({
                'status': 202,
                'msg': '租户名称或联系邮箱未指定'
            })
        self.init_talent(talent_name, talent_email, request.user.id, request.user.get_username())

        return JsonResponse({
            'status': 201,
            'msg': f'租户{talent_name}创建成功',
        })

    def delete(self, request, pk):
        """
        删除租户
        :param request:
        :return:
        """
        talent = Talent.objects.filter(id=pk).first()
        msg = f'租户：{talent.get_talent_name()} 删除成功'
        departments = talent.departments.all()
        for department in departments:
            department.users.all().delete()
            # todo 增加用户创建的agent及相关数据的删除
        departments.delete()
        talent.delete()
        return JsonResponse({
            'status': 201,
            'msg': msg,
        })

    @staticmethod
    @transaction.atomic
    def init_talent(talent_name, talent_email, created_by, default_username):
        try:
            timestamp = int(time.time())
            talent = Talent(talent_name=talent_name, create_time=timestamp, update_time=timestamp,
                            created_by=created_by)
            talent.save()

            # todo 创建默认部门
            default_department = Department(name='默认部门', create_time=timestamp, update_time=timestamp,
                                            created_by=created_by)
            default_department.save()
            talent.departments.add(default_department)

            # todo 创建默认用户
            suffix_email = talent_email.split('@')[-1]
            email = f'{default_username}@{suffix_email}'
            password = '123456'
            default_user = User.objects.create_talent_user(username=email, password=password, email=email,
                                                           phone='11111111111')
            default_user.is_active = True
            default_user.save()

            # 将用户插入部门
            group, success = Group.objects.get_or_create(name='talent_admin')
            group.user_set.add(default_user)
            group.save()

            default_department.users.add(default_user)
        except:
            raise DatabaseError
