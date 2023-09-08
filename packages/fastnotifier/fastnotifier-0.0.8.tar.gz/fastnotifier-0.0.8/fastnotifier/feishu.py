#!/usr/bin/env python3
# coding = utf8
import requests
import json
import envx
"""
help doc url：https://www.feishu.cn/hc/zh-cn/articles/360024984973-在群聊中使用机器人
"""


def make_con_info(
        env_file_name: str = 'feishu.notifier.env'
):
    # ---------------- 固定设置 ----------------
    inner_env = envx.read(file_name=env_file_name)
    con_info = {
        "webhook": inner_env['webhook'],
        "at_ids": inner_env.get('at_ids'),  # 艾特的id，以英文逗号分隔
        "at_mobiles": inner_env.get('at_mobiles')  # 艾特的手机号码，以英文逗号分隔
    }
    # ---------------- 固定设置 ----------------
    return con_info


class Basics:
    def __init__(
            self,
            con_info: dict = None
    ):
        self.webhook = con_info['webhook']

        at_ids = con_info.get('at_ids')
        self.at_ids = at_ids
        if at_ids is not None:
            self.at_id_list = at_ids.split(',')
        else:
            self.at_id_list = None

        at_mobiles = con_info.get('at_mobiles')
        self.at_mobiles = at_mobiles
        if at_mobiles is not None:
            self.at_mobile_list = at_mobiles.split(',')
        else:
            self.at_mobile_list = None

    def send_text(
            self,webhook_url, text):
        data = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }
        data_ = json.dumps(data, ensure_ascii=False)
        byte_data = data_.encode('utf-8')
        requests.post(webhook_url, byte_data)


def send_multi_text(webhook_url, title, content_list):
    """
    title is like: "项目更新通知"
    each content in content_list is like:
    [
        {
            "tag": "text",
            "text": "项目有更新: "
        },
        {
            "tag": "a",
            "text": "请查看",
            "href": "http://www.example.com/"
        }
    ]
    the massage is like :
    项目更新通知
    项目有更新: 请查看

    """
    data = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": content_list
                }
            }
        }
    }
    data_ = json.dumps(data, ensure_ascii=False)
    byte_data = data_.encode('utf-8')
    requests.post(webhook_url, byte_data)


def run_demo(webhook_url):
    content_list_test = [
        [
            {
                "tag": "text",
                "text": "项目有更新1: "
            },
            {
                "tag": "a",
                "text": "请查看1",
                "href": "http://www.example.com/"
            }
        ],
        [
            {
                "tag": "text",
                "text": "项目有更新2: "
            },
            {
                "tag": "a",
                "text": "请查看2",
                "href": "http://www.example.com/"
            }
        ]
    ]
    send_multi_text(webhook_url=webhook_url,
                    title='项目更新通知',
                    content_list=content_list_test)
