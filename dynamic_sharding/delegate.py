#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/18 09:10
# @File    : delegate
# @desc    : 获取信息智能体


import asyncio
from typing import List
from utils.logger import logger
from web_access.main import WebAccess
from dynamic_sharding.message import Message


class Delegate:
    def __init__(self, name: str) -> None:
        """
        初始化获取信息智能体

        Args:
            name (str): 智能体名.
        """
        self.name = name
        logger.info(f"{self.name} 初始化.")


    async def process(self, message: Message) -> Message:
        """
        通过获取该分片中每个关键词的相关信息来处理该分片。
        Args:
            message (Message): 包含分片的消息。

        Returns:
            Message: 输出消息。
        """
        logger.info(f"{self.name} 处理分片.")
        try:
            entities: List[str] = message.content
            tasks = []

            # 创建任务来获取每个实体的信息
            for entity in entities:
                task = asyncio.create_task(self.fetch_entity_info(entity))
                tasks.append(task)

            # 收集信息
            entity_info = await asyncio.gather(*tasks)
            shard_info = "\n\n".join(entity_info)

            return Message(content=shard_info, sender=self.name, recipient=message.sender)
        except Exception as e:
            logger.error(f"在 {self.name} 中发生错误: {e}")
            return Message(
                content="发生错误，请稍后再试。",
                sender=self.name,
                recipient=message.sender
            )

    async def fetch_entity_info(self, entity: str) -> str:
        """
        获取实体的相关信息。

        Args:
            entity (str): 要获取信息的实体。

        Returns:
            str: 实体的相关信息。
        """
        logger.info(f"{self.name} 获取 {entity} 的信息.")
        try:
            # 调用 WebAccess 类来获取实体信息
            info = await asyncio.to_thread(WebAccess().run, f"{entity} 消息")
            return f"信息关于 {entity}:\n{info}"
        except Exception as e:
            logger.error(f"{self.name} 获取 {entity} 的信息时出错: {str(e)}")
            return f"获取 {entity} 的信息时出错。"

