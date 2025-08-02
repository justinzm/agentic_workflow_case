#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/26 17:13
# @File    : summarize
# @desc    : 文档摘要智能体

import os
import asyncio
from glob import glob
from utils.logger import logger
from utils.message import Message
from utils.ChatModel import ChatModel
from typing import List, Dict, Any, Tuple


class SummarizeAgent:
    """
    文档摘要智能体
    """
    def __init__(self, name: str) -> None:
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()

        self.name = name

    async def process(self, message: Message) -> Message:
        """
        使用大型语言模型（LLM）生成预处理文档的摘要。

        参数：
            message (Message): 包含预处理文档的输入消息。

        返回：
            Message: 包含生成摘要的消息，格式需符合模式要求。

        异常：
            RuntimeError: 若文档摘要生成或验证失败时抛出。
        """
        logger.info(f"{self.name} 开始生成摘要")
        input_data = message.content

        summaries = {"summaries": []}
        for doc in input_data.get("preprocessed_docs", []):
            try:
                summary = await self._generate_summary(
                    doc_id=doc["id"],
                    doc_title=doc["title"],
                    doc_content=doc["content"]
                )
                summaries["summaries"].append({
                    "doc_name": doc["id"],
                    "summary": summary
                })
            except Exception as e:
                logger.error(f"文档摘要生成失败: {e}")
                raise RuntimeError(f"文档摘要生成失败: {e}")

        logger.info(f"{self.name} 成功生成并验证了摘要")
        return Message(content=summaries, sender=self.name, recipient=message.sender)

    async def _generate_summary(self, doc_id: str, doc_title: str, doc_content: str) -> str:
        """
        使用大型语言模型(LLM)生成文档摘要。

        参数：
            doc_id (str): 正在处理的文档ID
            doc_title (str): 文档标题
            doc_content (str): 文档内容

        返回：
            str: 生成的摘要

        异常：
            RuntimeError: 当LLM无法生成响应时抛出
        """
        llm_input = (
            "你是一名专业的文档摘要撰写人。"
            "根据提供的文档内容，生成一个简洁的摘要，概括主要情节、人物和主题。摘要需简短，仅限两句话。\n\n"
            "重要提示：请以有效的JSON格式提供摘要，键名为‘summary‘。"
            "确保你的回复是一个单独且格式正确的JSON对象。"
            "不要在JSON之外包含任何解释或额外文本。\n"
            "正确格式示例：\n{'summary': '这是一个示例摘要。它用两句话概括了文档的精髓。'}\n\n"
            f"文档标题：{doc_title}\n"
            f"文档内容：\n{doc_content}"
        )
        logger.info(f"正在使用LLM为标题为‘{doc_title}’、ID为‘{doc_id}’的文档生成摘要")

        try:
            def blocking_call():
                result = (
                    self.agent
                    .general("你是一个经过训练的人工智能，专门用于总结文档并输出完美的JSON格式。")
                    .input(llm_input)
                    .output({
                        "summary": ("str", "生成一个简洁的摘要，概括主要情节、人物和主题。摘要需简短，仅限两句话。")
                    })
                    .start()
                )
                return result
            summary_result = await asyncio.to_thread(blocking_call)
            return summary_result["summary"]
        except Exception as e:
            logger.error(f"未能为标题为“{doc_title}”、ID为“{doc_id}”的文档生成摘要，原因：{e}")
            raise RuntimeError(f"未能为文档生成摘要: {e}")



