#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:owefsad
# datetime:2021/1/14 下午3:35
# software: PyCharm
# project: dongtai-models
from django.db import models
from django.utils.translation import gettext_lazy as _

from dongtai_common.models.agent import IastAgent
from dongtai_common.models.hook_strategy import HookStrategy
from dongtai_common.utils.settings import get_managed

# 'id', 'agent', 'uri', 'http_method', 'http_scheme', 'req_header', 'req_params', 'req_data', 'taint_value','param_name'
class MethodPool(models.Model):
    agent = models.ForeignKey(IastAgent,
                              models.DO_NOTHING,
                              blank=True,
                              null=True,
                              db_constraint=False)
    url = models.CharField(max_length=2000, blank=True, null=True)
    uri = models.CharField(max_length=2000, blank=True, null=True)
    http_method = models.CharField(max_length=10, blank=True, default='')
    http_scheme = models.CharField(max_length=20, blank=True, null=True)
    http_protocol = models.CharField(max_length=255, blank=True, null=True)
    req_header = models.CharField(max_length=2000, blank=True, null=True)
    req_params = models.CharField(max_length=2000, blank=True, null=True)
    req_data = models.CharField(max_length=4000, blank=True, null=True)
    res_header = models.CharField(max_length=1000, blank=True, null=True)
    res_body = models.TextField( blank=True, null=True)
    req_header_fs = models.TextField(blank=True,
                                     null=True,
                                     db_column='req_header_for_search')
    context_path = models.CharField(max_length=255, blank=True, null=True)
    method_pool = models.TextField(blank=True,
                                   null=True)  # This field type is a guess.
    pool_sign = models.CharField(unique=True,
                                 max_length=40,
                                 blank=True,
                                 null=True)  # This field type is a guess.
    clent_ip = models.CharField(max_length=255, blank=True, null=True)
    create_time = models.IntegerField(blank=True, null=True)
    update_time = models.IntegerField(blank=True, null=True)
    uri_sha1 = models.CharField(max_length=40,
                                blank=True,
                                default='',
                                db_index=True)
    sinks = models.ManyToManyField(
        HookStrategy,
        verbose_name=_('sinks'),
        blank=True,
        related_name="method_pools",
        related_query_name="method_pool",
    )

    class Meta:
        managed = get_managed()
        db_table = 'iast_agent_method_pool'
        indexes = [models.Index(fields=['uri_sha1', 'http_method', 'agent'])]


from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry


@registry.register_document
class MethodPoolDocument(Document):

    class Index:
        name = 'alias-dongtai-v1-method-pool-dev'

    class Django:
        model = MethodPool

    # fields = [
    #     'res_header',
    #     'uri_sha1',
    #     'url',
    #     'update_time',
    #     'res_header',
    #     'res_body',
    #     'req_params',
    #     'req_header_for_search',
    #     'req_header',
    #     'req_data',
    #     'pool_sign',
    #     'method_pool',
    #     'language',
    #     'id',
    #     'http_scheme',
    #     'http_protocol',
    #     'http_method',
    #     'create_time',
    #     'context_path',
    #     'clent_ip',
    #     'agent_id',  #'user_id','bind_project_id','project_version_id',
    # ]


def search_generate():
    from elasticsearch_dsl import Q
    a = Q('bool',
          must=[
              Q('multi_match',
                query='123',
                fields=[
                    "uri", "req_header_for_search", "req_data", "res_body",
                    "res_header"
                ]),
              Q('range', update_time={
                  'gte': 1640598889,
                  'lte': 1640598891
              }),
              Q('range', update_time={
                  'lte': 1640598889,
              }),
              Q('terms', agent_id=[4631, 4632]),
          ],
          must_not=[Q('terms', ids=['350071', '350073'])])
    return a
