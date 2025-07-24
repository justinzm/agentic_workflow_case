#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/24 10:22
# @File    : coordinator
# @desc    : 任务分解模式的协调器


import asyncio
from utils.logger import logger
from utils.message import Message
from task_decomposition.delegates import SubTaskAgent


class CoordinatorAgent:
    """
    通过将文档分解为提取子任务并将其分配给子代理并行执行来协调文档的处理。
    """
    def __init__(self, name: str) ->None:
        self.name = name
        logger.info(f"{self.name} 初始化.")

    async def process(self, message: Message) -> Message:
        """
        处理消息，分解任务并协调子代理执行。
        :param message: 包含文档内容和任务的消息对象。
        :return: 包含处理结果的消息对象。
        """
        logger.info(f"{self.name} 开始运行.")
        try:
            # 假设 message.content 包含文档内容
            document_content = message.content

            # 这里可以添加逻辑来分解任务并将其分配给子代理
            sub_tasks = self.decompose_task(document_content)

            # 创建子代理并行执行任务
            tasks = []
            for idx, sub_task in enumerate(sub_tasks):
                agent_name = f"SubTaskAgent_{idx + 1}"
                sub_message = Message(
                    content=sub_task,
                    sender=self.name,
                    recipient=agent_name,
                )
                agent = SubTaskAgent(name=agent_name)
                task = asyncio.create_task(agent.process(sub_message))
                tasks.append(task)

            # 并行执行所有子任务
            sub_results = await asyncio.gather(*tasks)

            # 将结果合并摘要
            combined_result = self.combine_results(sub_results)
            return Message(content=combined_result, sender=self.name, recipient=message.sender)

        except Exception as e:
            logger.error(f"{self.name} 运行失败: {e}")
            return Message(content="处理失败", sender=self.name, recipient=message.sender)

    def decompose_task(self, document_content: str) -> list:
        """
        分解文档为子任务。
        :param document_content: 文档内容。
        :return: 子任务列表。
        """
        return [
            {"document": document_content, "task": "提取文档中的所有命名实体（人名、机构名、地名、公司名等），并说明它们的作用和重要性。请用中文回答。"},
            {"document": document_content, "task": "识别并提取文档中的所有直接引用和间接引用，包括发言人和上下文背景。请用中文回答。"},
            {"document": document_content, "task": "提取文档中的所有数值数据（日期、统计数字、测量数据、百分比等）并提供相关描述和背景。请用中文回答。"},
            {"document": document_content, "task": "识别并提取文档中的关键术语、概念或专业词汇，并提供它们的定义或解释。请用中文回答。"},
            {"document": document_content, "task": "提取文档中提到的所有外部来源、参考资料、相关链接或引用信息。请用中文回答。"}
        ]

    def combine_results(self, sub_results: list) -> str:
        """
        合并子任务结果为最终输出。
        :param sub_results: 子任务结果列表。
        :return: 合并后的结果字符串。
        """
        summary = "文档处理结果摘要:\n"
        for result in sub_results:
            summary += f"{result.content}\n"
        return summary
