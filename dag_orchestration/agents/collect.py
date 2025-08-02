#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/26 16:24
# @File    : collect
# @desc    : 文档收集智能体


import os
import asyncio
from glob import glob
from utils.logger import logger
from utils.message import Message
from utils.ChatModel import ChatModel
from typing import List, Dict, Any, Tuple


class CollectAgent:
    """
    文档收集智能体
    """
    def __init__(self, name: str, docs_folder: str = "./data/docs") -> None:
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()
        self.docs_folder = docs_folder
        self.name = name

    async def process(self, message: Message) -> Message:
        """
        使用大型语言模型(LLM)对收集的文档内容进行清洗预处理。
        这对于通过OCR或网络爬虫获取的文档内容特别有用，因为这些内容通常需要进一步处理。

        参数:
            message (Message): 包含收集文档的输入消息。

        返回:
            Message: 包含预处理后文档的消息。

        异常:
            RuntimeError: 如果文档预处理或验证失败时抛出。
        """
        logger.info(f"{self.name}开始收集文件")

        try:
            # 从指定文件夹异步收集文档
            docs = await self._collect_documents(self.docs_folder)
        except Exception as e:
            logger.error(f"文档收集验证失败：{e}")
            raise RuntimeError(f"文档预处理失败: {e}")

        logger.info(f"{self.name} 成功收集并验证了所有文件")
        return Message(content=docs, sender=self.name, recipient=message.sender)

    async def _collect_documents(self, folder_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        从指定文件夹收集文本文档并处理每个文档。

        参数:
            folder_path (str): 包含文本文档的文件夹路径。

        返回:
            Dict[str, List[Dict[str, Any]]]: 包含所收集文档元数据的字典。

        异常:
            RuntimeError: 如果文档收集过程中出现任何失败情况。
        """
        doc_files = glob(os.path.join(folder_path, "*.txt"))
        docs = {"docs": []}

        for idx, filepath in enumerate(doc_files):
            try:
                content, title = self._read_document(filepath)
                extracted_title = await self._extract_title_from_llm(content)

                docs["docs"].append({
                    "id": f"doc{idx + 1}",
                    "title": extracted_title if extracted_title else title,
                    "content": content,
                    "filepath": filepath
                })
            except Exception as e:
                logger.error(f"从 {filepath} 收集文档失败：{e}")
                raise RuntimeError(f"从 {filepath} 收集文档失败: {e}")
        return docs

    def _read_document(self, filepath: str) -> Tuple[str, str]:
        """
        读取文本文件并返回其内容及标题。

        参数：
            filepath (str): 文档路径。

        返回：
            Tuple[str, str]: 文档内容与标题组成的元组。
        """
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
            title = os.path.splitext(os.path.basename(filepath))[0]
            return content, title
        except Exception as e:
            logger.error(f"读取文档 {filepath} 失败: {e}")
            raise e

    async def _extract_title_from_llm(self, document: str) -> str:
        """
        使用大型语言模型（LLM）为文档提取合适的标题。

        参数：
            document (str): 用于提取标题的文档内容。

        返回值：
            str: 提取出的标题。
        """
        llm_input = (
            "以下文本代表一份需要精确且描述性标题的文档：\n\n"
            f"{document}\n\n"
            "请深入分析内容，生成一个简洁、专业、简短的标题，准确反映文档的核心标题。"
            "仅返回一个标题。"
        )
        logger.info(f"使用大模型提取标题，内容长度为：{len(document)}字符")
        try:
            def blocking_call():
                result = (
                    self.agent
                    .input(llm_input)
                    .output("生成精确且描述性标题")
                    .start()
                )
                return result.strip()
            extracted_title = await asyncio.to_thread(blocking_call)
            return extracted_title
        except Exception as e:
            logger.error(f"使用大模型提取标题失败: {e}")
            return ""


if __name__ == "__main__":
    # 示例用法
    collect_agent = CollectAgent(name="DocumentCollector")
    message = Message(content="", sender="User", recipient="DocumentCollector")

    res = asyncio.run(collect_agent.process(message))
    print(res)