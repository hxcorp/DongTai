#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:owefsad
# datetime:2020/8/24 18:18
# software: PyCharm
# project: sca

import requests


def log():
    resp = requests.get('http://81.69.171.187:81/')
