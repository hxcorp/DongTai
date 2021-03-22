#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:owefsad
# datetime:2020/11/23 下午2:15
# software: PyCharm
# project: lingzhi-webapi
from django.db.models import Q
from rest_framework.request import Request

from base import R
from iast.base.agent import get_agents_with_project, get_user_project_name, \
    get_user_agent_pro, get_all_server
from iast.base.user import UserEndPoint
from iast.models.vul_level import IastVulLevel
from iast.models.vulnerablity import IastVulnerabilityModel
from iast.serializers.vul import VulSerializer


class VulnList(UserEndPoint):

    def get(self, request: Request):
        """
        获取漏洞列表
        - 支持排序
        - 支持搜索
        - 支持分页
        :param request:
        :return:
        """
        end = {
            "status": 201,
            "msg": "success",
            "data": []
        }
        # 提取过滤条件：
        language = request.query_params.get('language', None)
        level = request.query_params.get('level', None)
        type = request.query_params.get('type', None)
        project_name = request.query_params.get('project_name', None)
        project_id = request.query_params.get('project_id', None)
        url = request.query_params.get('url', None)
        order = request.query_params.get('order', None)
        user = request.user
        auth_users = self.get_auth_users(user)

        condition = Q()

        if language and language != '':
            condition = condition & Q(language=language)
        if level and level != '':
            condition = condition & Q(level=level)
        if type and type != '':
            condition = condition & Q(type=type)
        if project_name and project_name != '':
            agent_ids = get_agents_with_project(project_name, condition, auth_users)
            if agent_ids:
                condition = condition & Q(agent_id__in=agent_ids)
        if project_id and project_id != '':
            agents = self.get_auth_agents(auth_users).filter(bind_project_id=project_id)
            if agents:
                condition = condition & Q(agent__in=agents)
        if url and url != '':
            condition = condition & Q(url__icontains=url)

        agents = self.get_auth_agents(auth_users)
        if order:
            queryset = IastVulnerabilityModel.objects.filter(condition, agent__in=agents).order_by(order)
        else:
            queryset = IastVulnerabilityModel.objects.filter(condition, agent__in=agents).order_by('-latest_time')
        # 获取所有项目名称
        proNames = get_user_project_name(auth_users)
        # 获取用户所有agent绑定项目ID
        agentArr = get_user_agent_pro(auth_users, proNames.keys())
        agentPro = agentArr['pidArr']
        agentServer = agentArr['serverArr']
        server_ids = agentArr['server_ids']
        allServer = get_all_server(server_ids)
        allType = IastVulLevel.objects.all().order_by("id")
        allTypeArr = {}
        if allType:
            for item in allType:
                allTypeArr[item.id] = item.name_value
        # 获取server_name

        page = request.query_params.get('page', 1)
        page_size = request.query_params.get("pageSize", 20)
        page_summary, page_data = self.get_paginator(queryset, page, page_size)

        datas = VulSerializer(page_data, many=True).data
        pro_length = len(datas)
        if pro_length > 0:
            for index in range(pro_length):
                item = datas[index]
                item['index'] = index
                item['project_name'] = proNames.get(agentPro.get(item['agent_id'], 0), "暂未绑定项目")
                item['server_name'] = allServer.get(agentServer.get(item['agent_id'], 0), "JavaApplication")
                item['server_type'] = VulSerializer.split_container_name(item['server_name'])

                item['level_type'] = item['level_id']
                item['level'] = allTypeArr.get(item['level_id'], "")
                end['data'].append(item)
        end['page'] = page_summary
        return R.success(page=page_summary, data=end['data'])
