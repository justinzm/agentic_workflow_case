#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/17 11:03
# @File    : coordinator
# @desc    :


import asyncio
from typing import List
from utils.logger import logger
from dynamic_sharding.message import Message
from dynamic_sharding.delegate import Delegate


class Coordinator:
    def __init__(self, name: str):
        """
        初始化 协调员

        Args:
            name (str): 智能体名.
        """
        self.name = name
        logger.info(f"{self.name} 初始化.")

    async def run(self, message: Message) -> Message:
        """
        处理包含实体和分片大小的传入消息，根据分片大小对列表进行分片，动态创建子代理，并收集结果。

        Args:
            message (Message): 包含列表及分片大小的传入消息。

        Returns:
            Message: 输出消息。
        """
        logger.info(f"{self.name} 运行处理信息.")
        try:
            # 从消息中获取实体列表和分片大小
            data = message.content
            entities: List[str] = data.get('entities', [])
            shard_size: int = data.get('shard_size', 1)

            if not entities:
                raise ValueError("No entities provided.")

            # 对列表进行分片
            shards = [entities[i:i + shard_size] for i in range(0, len(entities), shard_size)]
            logger.info(f"将列表分片为 {len(shards)} 片.")

            tasks = []
            for idx, shard in enumerate(shards):
                agent_name = f"ShardProcessingAgent_{idx}"
                # 创建子代理并处理每个分片
                agent = Delegate(name=agent_name)
                task = asyncio.create_task(
                    agent.process(
                        Message(content=shard, sender=self.name, recipient=message.sender)
                    )
                )
                tasks.append(task)

            sub_responses = await asyncio.gather(*tasks)

            # 汇总结果
            entity_info = [response.content for response in sub_responses if response.content]

            final_response = "\n\n".join(entity_info)

            return Message(content=final_response, sender=self.name, recipient=message.sender)
        except Exception as e:
            logger.error(f"在 {self.name} 中发生错误: {e}")
            return Message(content="发生错误，请稍后再试。", sender=self.name, recipient=message.sender)