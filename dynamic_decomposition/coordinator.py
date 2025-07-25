#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/25 09:16
# @File    : coordinator
# @desc    : 协调器


import json
import asyncio
from utils.logger import logger
from utils.message import Message
from utils.ChatModel import ChatModel
from dynamic_decomposition.delegates import SubTaskAgent


class CoordinatorAgent:
    """
    协调器
    """
    def __init__(self, name: str) ->None:
        self.name = name
        logger.info(f"{self.name} 初始化.")
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()


    async def process(self, message: Message) -> Message:
        """
        处理消息，协调子代理执行任务。
        :param message: 包含任务内容的消息对象。
        :return: 包含处理结果的消息对象。
        """
        logger.info(f"{self.name} 开始运行.")
        try:
            # 假设 message.content 包含任务内容
            book_content = message.content

            # 这里可以添加逻辑来分解任务并将其分配给子代理
            sub_tasks = await self.decompose_task(book_content)

            # 创建子代理并行执行任务
            tasks = []
            for idx, sub_task in enumerate(sub_tasks):
                agent_name = f"SubTaskAgent_{idx + 1}"
                sub_message = Message(
                    content={"document": book_content, "task": sub_task},
                    sender=self.name,
                    recipient=agent_name,
                )
                agent = SubTaskAgent(name=agent_name)
                task = asyncio.create_task(agent.process(sub_message))
                tasks.append(task)

            # 并行执行所有子任务
            sub_results = await asyncio.gather(*tasks)

            # 将结果合并摘要
            combined_result = self.combine_results(sub_results, sub_tasks)

            return Message(content=combined_result, sender=self.name, recipient=message.sender)

        except Exception as e:
            logger.error(f"{self.name} 运行失败: {e}")


    async def decompose_task(self, book_content: str) -> dict:
        """
        使用大型语言模型将主要任务精确分解为 10 个独立的子任务。
        :param book_content: 书籍内容
        :return: 任务分解结果
        """
        logger.info(f"使用大型语言模型将主要任务分解为子任务")

        llm_input = f"""
        您是文学分析方面的专家。给定一本书的文本，请生成恰好 10 个可并行执行的独立提取任务。
        这些任务应侧重于提取不同类型的实体，例如人物、地点、主题、情节要点等等。
        输出应是一个 JSON 对象，键为 'task_1'、'task_2' 等等，对应的值为任务描述。
        不要包含需要数学运算的任务，比如计数和频率计算等。

        书籍文本：\n
        {book_content}
        """

        try:
            json_str = (
                self.agent
                .input(llm_input)
                .output("输出任务分解结果,输出一个json对象，键为 'task_1'、'task_2' 等等，对应的值为任务描述。")
                .start()
            )
            logger.info(f"分解任务结果: {json_str}")
            cleaned_json_str = json_str.strip().strip('```json').strip('```')
            result_dict = json.loads(cleaned_json_str)
            return result_dict
        except Exception as e:
            logger.error(f"分解任务失败: {e}")
            return {}

    def combine_results(self, sub_results: list, sub_tasks: dict) -> str:
        """
        合并子任务结果为最终输出。
        :param sub_results: 子任务结果列表。
        :param sub_tasks: 子任务字典。
        :return: 合并后的结果字符串。
        """
        document = "文档分析汇总:\n"
        for idx, (key, task_description) in enumerate(sub_tasks.items()):
            result = sub_results[idx]
            document += f"## {task_description}\n{result.content}\n\n"
        return document