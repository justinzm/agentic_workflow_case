#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/8/2 13:41
# @File    : preprocess
# @desc    : 文档预处理智能体


import asyncio
from utils.logger import logger
from utils.message import Message
from utils.ChatModel import ChatModel


class PreprocessAgent:
    """
    文档预处理智能体
    该智能体负责对收集的文档内容进行清洗和预处理。
    """
    def __init__(self, name: str) -> None:
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()
        self.name = name

    async def process(self, message: Message) -> Message:
        """
        利用大型语言模型（LLM）对收集的文档内容进行清理预处理。这一步骤在通过OCR技术读取或从网页抓取内容时尤为实用。

        参数：
            message (Message): 包含待处理文档的输入消息。

        返回：
            Message: 包含预处理后文档的消息。

        异常：
            RuntimeError: 当文档预处理或验证失败时抛出。
        """
        logger.info(f"{self.name} 开始文档预处理")
        input_data = message.content

        preprocessed_docs = {"preprocessed_docs": []}

        for doc in input_data.get("docs", []):
            try:
                # 假设文档内容需要清洗和预处理
                cleaned_content = await self._clean_document_content(
                    doc["id"], doc["title"], doc["content"]
                )

                preprocessed_docs["preprocessed_docs"].append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "content": cleaned_content
                })

            except Exception as e:
                logger.error(f"未能预处理标题为“{doc['title']}”、ID为“{doc['id']}”的文档：{e}")
                raise RuntimeError(f"文档预处理错误：'{doc['title']}'")

        logger.info(f"{self.name} 已成功完成文档的预处理与验证。")
        return Message(content=preprocessed_docs, sender=self.name, recipient=message.sender)


    async def _clean_document_content(self, doc_id: str, doc_title: str, doc_content: str) -> str:
        """
        清洗单个文档的内容。

        参数：
            doc_id (str): 文档的唯一标识符。
            doc_title (str): 文档标题。
            doc_content (str): 文档内容。

        返回：
            str: 清洗后的文档内容。
        """
        llm_input = (
            "您是一位文本处理与内容优化专家。"
            "当接收到原始文档内容时，需执行深度清理与标准化处理：清除冗余格式、修正OCR识别错误、提升文本可读性，"
            "同时确保不改变原文的核心意义与表达意图。"
            "最终目标是生成结构清晰、表述专业的高质量文档文本。\n\n"
            f"文档标题：{doc_title}\n"
            f"原始文档内容：\n{doc_content}"
        )

        logger.info(f"正在使用LLM处理标题为{doc_title}、ID为“{doc_id}”的文档，进行内容清理。")

        try:
            cleaned_content = (
                self.agent
                .input(llm_input)
                .output("请提供清理后的文档内容")
                .start()
            )
            return cleaned_content
        except Exception as e:
            logger.error(f"未能清理文档“{doc_title}”（ID：{doc_id}）的内容：{e}")
            return ""
