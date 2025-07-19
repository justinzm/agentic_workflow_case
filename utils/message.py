#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/17 11:10
# @File    : message
# @desc    : 消息传递的核心数据结构


from typing import Optional, Dict


class Message:
    def __init__(self, content: str, sender: str, recipient: str, metadata: Optional[Dict[str, str]] = None) -> None:
        """
        初始化消息对象。

        :param content: 消息内容。
        :param sender: 发送者的名称。
        :param recipient: 接收者的名称。
        :param metadata: 可选的元数据字典，包含额外信息。
        """
        self.content = content
        self.sender = sender
        self.recipient = recipient
        self.metadata: Dict[str, str] = metadata or {}

    def __repr__(self) -> str:
        """
        返回消息对象的字符串表示形式。

        :return: 消息的字符串表示。
        """
        return f"Message(from={self.sender}, to={self.recipient}, content={self.content}, metadata={self.metadata})"