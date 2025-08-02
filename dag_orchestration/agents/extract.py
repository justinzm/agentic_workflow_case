#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/8/2 14:08
# @File    : extract
# @desc    : 文档内容提取智能体

import asyncio
from typing import Dict, Any
from utils.logger import logger
from utils.message import Message
from utils.ChatModel import ChatModel


class ExtractAgent:
    """
    文档内容提取智能体
    该智能体负责从预处理后的文档中提取关键信息。
    """
    def __init__(self, name: str) -> None:
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()
        self.name = name

    async def process(self, message: Message) -> Message:
        """
        使用大型语言模型（LLM）从预处理后的文档中提取关键信息。

        参数：
            message (Message): 包含预处理文档的输入消息。

        返回：
            Message: 包含按模式要求格式提取的关键信息的消息。
        """
        logger.info(f"{self.name} 开始文档内容提取")
        input_data = message.content

        extracted_items = []

        for doc in input_data.get("preprocessed_docs", []):
            try:
                extracted_data = await self._extract_key_information(doc["id"], doc["title"], doc["content"])

                # 按照更新后的架构创建提取项
                extracted_items.append({
                    "id": doc["id"],
                    "key_info": [
                        {
                            "characters": extracted_data.get("characters", []),
                            "themes": extracted_data.get("themes", []),
                            "plot_points": extracted_data.get("plot_points", [])
                        }
                    ]
                })
            except Exception as e:
                logger.error(f"未能从标题为“{doc['title']}”、ID为“{doc['id']}”的文档中提取关键信息：{e}")
                raise RuntimeError(f"文档内容提取错误：'{doc['title']}'")

        # 准备最终输出为所需格式
        output_data = {"extracted_items": extracted_items}

        logger.info(f"{self.name} 成功提取并验证了关键信息。")
        return Message(content=output_data, sender=self.name, recipient=message.sender)


    async def _extract_key_information(self, doc_id: str, doc_title: str, doc_content: str) -> Dict[str, Any]:
        """
        使用大型语言模型从文档中提取关键信息。

        参数:
            doc_id (str): 待处理文档的唯一标识符。
            doc_title (str): 文档标题。
            doc_content (str): 文档正文内容。

        返回:
            Dict[str, Any]: 以字典格式返回提取的关键信息。
        """
        llm_input = (
            "你是一位擅长文本解读的文学分析师。你的任务是分析以下文档并提取关键信息。具体需要识别以下内容：\n"
            "- 主要角色列表（仅限姓名）。\n"
            "- 文档中讨论或探讨的核心主题。\n"
            "- 对理解故事情节至关重要的关键情节。\n\n"
            "重要提示：请将输出结果以格式规范的单一JSON对象呈现，包含'characters'（角色）、'themes'（主题）和'plot_points'（情节要点）三个键。\n"
            "确保'characters'是仅包含角色姓名的字符串数组。\n"
            "不要在JSON之外添加任何解释性文字或额外内容。\n"
            "正确格式示例如下：\n"
            '{"characters": ["姓名1", "姓名2"], "themes": ["主题1", "主题2"], "plot_points": ["要点1", "要点2"]}\n\n'
            f"文档ID：{doc_id}\n"
            f"文档标题：{doc_title}\n"
            f"文档正文：\n{doc_content}"
        )

        logger.info(f"正在使用LLM从标题为“{doc_title}”、ID为“{doc_id}”的文档中提取关键信息。")

        try:
            extracted_data = (
                self.agent
                .general("你是一个经过训练的AI，专门从文档中提取关键信息并输出完美的JSON格式数据。")
                .input(llm_input)
                .output({
                    "characters": [("str", "主要角色姓名")],
                    "themes": [("str", "文档中讨论或探讨的核心主题")],
                    "plot_points": [("str", "对理解故事情节至关重要的关键情节")]
                })
                .start()
            )
            return extracted_data
        except Exception as e:
            logger.error(f"无法从标题为“{doc_title}”、ID为“{doc_id}”的文档中提取关键信息，原因：{e}")
            raise RuntimeError(f"文档内容提取失败：'{doc_title}'")

