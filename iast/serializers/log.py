#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:owefsad
# datetime:2020/12/5 上午10:46
# software: PyCharm
# project: lingzhi-webapi
from django.contrib.admin.models import LogEntry
from rest_framework import serializers


class BaseLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry

    def get_user(self, obj):
        return obj.user.get_short_name()


class LogSerializer(BaseLogSerializer):
    user = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = ['id', 'action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag',
                  'change_message']

    def get_user(self, obj):
        return obj.user.get_short_name()

    def get_content_type(self, obj):
        return obj.content_type.app_labeled_name


class LogExportSerializer(BaseLogSerializer):
    class Meta:
        model = LogEntry
        fields = ['action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag',
                  'change_message']
