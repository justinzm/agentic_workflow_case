#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/24 13:41
# @File    : delegates
# @desc    : 子智能体


import asyncio
from utils.logger import logger
from utils.message import Message
from utils.ChatModel import ChatModel



class SubTaskAgent:
    """
    子任务代理，负责处理特定的子任务并返回结果。
    """
    def __init__(self, name: str):
        self.name = name
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()

    async def process(self, message: Message) -> Message:
        """
        处理子任务并返回结果。

        :param message: 包含子任务信息的消息。
        :return: 包含子任务结果的消息。
        """
        logger.info(f"{self.name} 处理子任务")
        sub_task = message.content

        # 提取子任务包含文档和任务
        document = sub_task.get("document")
        task = sub_task.get("task")

        if not document or not task:
            return Message(
                content="无效任务格式，请提供有效的文档和任务。",
                sender=self.name,
                recipient=message.sender
            )

        llm_input = f"# 文档内容:\n{document}\n\n # 任务:\n{task}"
        logger.info(f"当前大模型执行的任务: {task}")

        try:
            # 定义一个阻塞函数，使其在单独的线程中运行
            def blocking_call():
                return (
                    self.agent
                    .input(llm_input)
                    .output("输出任务结果")
                    .start()
                )

            extraction_result = await asyncio.to_thread(blocking_call)
        except Exception as e:
            logger.error(f"{self.name} 处理子任务时发生错误: {e}")
            extraction_result = f"处理子任务时发生错误，{task}。"

        return Message(
            content=extraction_result,
            sender=self.name,
            recipient=message.sender
        )
