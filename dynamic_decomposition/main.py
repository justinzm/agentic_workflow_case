#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/24 14:15
# @File    : main
# @desc    : 任务分解模式的主入口，协调任务分解和子任务执行。


import asyncio
from utils.logger import logger
from utils.message import Message
from dynamic_decomposition.coordinator import CoordinatorAgent


class DynamicDecomposition:
    """
    任务分解模式的主入口，协调任务分解和子任务执行。
    """
    def __init__(self):
        self.input_file = "doc.txt"
        self.output_file = "extracted_info.md"

    async def run(self):
        """
        启动任务分解模式。
        """
        with open(self.input_file, 'r', encoding='utf-8') as file:
            document_content = file.read()

        message = Message(content=document_content, sender="User", recipient="CoordinatorAgent")

        response = await CoordinatorAgent(name="CoordinatorAgent").process(message)

        with open(self.output_file, 'w', encoding='utf-8') as output_file:
            output_file.write(response.content)

        logger.info(f"处理完成，结果已保存到 {self.output_file}")


if __name__ == '__main__':
    asyncio.run(DynamicDecomposition().run())