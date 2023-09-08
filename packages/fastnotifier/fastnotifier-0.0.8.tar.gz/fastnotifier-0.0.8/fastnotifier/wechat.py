#!/usr/bin/env python3
# coding = utf8
import requests
import json
import envx
"""
help doc url：
https://work.weixin.qq.com/api/doc/90000/90136/91770
https://work.weixin.qq.com/help?person_id=1&doc_id=13376
获取会话内容：https://work.weixin.qq.com/api/doc/90000/90135/91774
"""


def make_con_info(
        env_file_name: str = 'wechat.notifier.env'
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
            self,
            msg: str = 'this is a test :)',
            is_at: bool = False,
            webhook: str = None,  # webhook链接
            mentioned_list: list = None,  # 按照id艾特的id列表
            mentioned_mobile_list: list = None,  # 按照手机号码艾特的手机号码列表
            at_all: bool = False,  # 艾特所有人
    ):
        """
        发送文字信息
        """
        if webhook is None:
            inner_webhook = self.webhook
        else:
            inner_webhook = webhook

        if is_at is False:
            inner_mentioned_list = None
            inner_mentioned_mobile_list = None
        else:
            if mentioned_list is None:
                inner_mentioned_list = self.at_id_list
            else:
                inner_mentioned_list = mentioned_list

            if mentioned_mobile_list is None:
                inner_mentioned_mobile_list = self.at_mobile_list
            else:
                inner_mentioned_mobile_list = mentioned_mobile_list

        if at_all is False:
            pass
        else:
            inner_mentioned_list = ["@all"]

        data = {
            "msgtype": "text",
            "text": {
                "content": msg,
                "mentioned_list": inner_mentioned_list,
                "mentioned_mobile_list": inner_mentioned_mobile_list
            }
        }
        inner_data = json.dumps(data, ensure_ascii=False)
        byte_data = inner_data.encode('utf-8')
        response = requests.post(
            url=inner_webhook,
            data=byte_data
        )
        return response


def send_text(
        msg: str = None,
        env_file_name: str = None,
        webhook: str = None,
        is_at: bool = False,
        mentioned_list: list = None,
        mentioned_mobile_list: list = None,
        at_all: bool = False,
):
    """
    在内部实例化
    """
    if env_file_name:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        con_info = {
            "webhook": webhook,
            # "at_ids": mentioned_list,  # 艾特的id，以英文逗号分隔
            # "at_mobiles": mentioned_mobile_list  # 艾特的手机号码，以英文逗号分隔
        }
    bot = Basics(con_info=con_info)
    response = bot.send_text(
        msg=msg,
        is_at=is_at,
        webhook=webhook,
        mentioned_list=mentioned_list,
        mentioned_mobile_list=mentioned_mobile_list,
        at_all=at_all,
    )
    return response
