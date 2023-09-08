#!/usr/bin/env python3
# coding = utf8
from dingtalkchatbot.chatbot import DingtalkChatbot
from urllib import parse
import hashlib
import base64
import time
import hmac
import envx
"""
文档：https://developers.dingtalk.com/document/app/document-upgrade-notice
https://developers.dingtalk.com/document/app/overview-of-group-robots?spm=ding_open_doc.document.0.0.ac7828e1477wnC#topic-2026024
自定义机器人接入：https://developers.dingtalk.com/document/app/custom-robot-access?spm=ding_open_doc.document.0.0.37f37b4b2asVMv#topic-1914047
"""


def make_con_info(
        env_file_name: str = 'dingding.notifier.env'
):
    # ---------------- 固定设置 ----------------
    inner_env = envx.read(file_name=env_file_name)
    con_info = {
        "webhook": inner_env['webhook'],
        "secret": inner_env.get('secret'),
        "at_ids": inner_env.get('at_ids'),  # 艾特的id，以英文逗号分隔
        "at_mobiles": inner_env.get('at_mobiles')  # 艾特的手机号码，以英文逗号分隔
    }
    # ---------------- 固定设置 ----------------
    return con_info


class Basics:
    def __init__(
            self,
            con_info=None,
            webhook=None,
            secret=None
    ):
        inner_webhook = con_info.get('webhook')
        inner_secret = con_info.get('secret')
        if webhook is None:
            self.webhook = inner_webhook
        else:
            self.webhook = webhook
        if secret is None:
            self.secret = inner_secret
        else:
            self.secret = secret
        self.ding = self.make_bot()

    def make_bot(
            self
    ):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = parse.quote_plus(base64.b64encode(hmac_code))
        webhook_new = '%s&timestamp=%s&sign=%s' % (self.webhook, timestamp, sign)
        ding = DingtalkChatbot(webhook_new)
        return ding

    def send_text(
            self,
            msg,
            is_at_all=False,
            at_ids=None
    ):
        if at_ids is not None:
            return self.ding.send_text(
                msg=msg,
                is_at_all=is_at_all,
                at_dingtalk_ids=at_ids
            )
        else:
            return self.ding.send_text(
                msg=msg,
                is_at_all=is_at_all
            )


def send_text(
        msg,
        is_at=False,
        at_ids=None,
        is_at_all=False,
        con_info: dict = None,  # 若指定，将优先使用
        env_file_name: str = 'dingding.notifier.env',
):
    # ---------------- 固定设置 ----------------
    if con_info is None:
        con_info = make_con_info(env_file_name=env_file_name)
    else:
        pass
    # ---------------- 固定设置 ----------------
    ding_bot = Basics(con_info=con_info)
    if is_at is True:
        ding_bot.send_text(
            msg=msg,
            at_ids=at_ids,
            is_at_all=is_at_all
        )
    else:
        ding_bot.send_text(
            msg=msg,
            is_at_all=is_at_all
        )
