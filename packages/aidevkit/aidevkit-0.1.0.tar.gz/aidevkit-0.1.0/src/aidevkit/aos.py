# -*-coding:utf-8 -*-
"""
:创建时间: 2023/8/25 8:49
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import os
import logging

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import torch


def get_client():
    # 配置信息
    config = CosConfig(
        Region=os.environ['COS_Region'],
        SecretId=os.environ['COS_SecretId'],
        SecretKey=os.environ['COS_SecretKey'],
    )

    # 创建客户端
    client = CosS3Client(config)

    return client


def save_object(obj, file_path):
    if not os.path.isdir('./cos_work'):
        os.mkdir('./cos_work')
    local_path = os.path.join('./cos_work', file_path)

    torch.save(obj.state_dict(), local_path)

    # 创建客户端
    client = get_client()

    response = client.upload_file(
        Bucket=os.environ['COS_Bucket'],
        LocalFilePath=local_path,
        Key=file_path,
    )


def object_exists(file_path):
    # 创建客户端
    client = get_client()

    response = client.object_exists(
        Bucket=os.environ['COS_Bucket'],
        Key=file_path,
    )

    return response


def load_object(obj, file_path):
    """

    :param obj:
    :param file_path:
    :return:
    """
    if not os.path.isdir('./cos_work'):
        os.mkdir('./cos_work')
    local_path = os.path.join('./cos_work', file_path)

    if not os.path.isfile(local_path):
        # 创建客户端
        client = get_client()

        client.download_file(
            Bucket=os.environ['COS_Bucket'],
            Key=file_path,
            DestFilePath=local_path,
        )

    obj.load_state_dict(torch.load(local_path))


class Saver:
    def __init__(self, make_obj_callback, file_path, save_interval=256):
        self.obj = make_obj_callback()
        self.file_path = file_path
        self.save_interval = save_interval
        self.count = 0
        if object_exists(file_path):
            logging.debug('load_object')
            load_object(self.obj, self.file_path)

    def step(self):
        self.count += 1
        if self.count >= self.save_interval:
            save_object(self.obj, self.file_path)
            self.count = 0
            logging.debug('auto_save')

    def must_save(self):
        save_object(self.obj, self.file_path)
        logging.debug('must_save')


__all__ = ['save_object', 'object_exists', 'load_object', 'Saver']
