#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/19 21:16
# @File    : hotel_search.py
# @desc    : 酒店查询智能体


import asyncio
from typing import Optional
from utils.logger import logger
from utils.message import Message
from utils.ChatModel import ChatModel
from web_access.main import WebAccess
from parallel_delegation.prompts import HOTEL_SYSTEM, HOTEL_USER


class HotelSearchAgent:
    """
    负责处理酒店查询、生成网络搜索查询，并返回汇总结果。
    """
    def __init__(self, name: str):
        self.name = name
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()

    async def process(self, message: Message) -> Message:
        logger.info(f"酒店查询: '{message.content}'")
        hotel_user = HOTEL_USER.format(query=message.content)
        try:
            result = (
                self.agent
                .general(HOTEL_SYSTEM)
                .input(hotel_user)
                .output({
                    "web_search_query": ("str", "对用户酒店查询进行优化后的内容")
                })
                .start()
            )
            web_search_query: Optional[str] = result.get("web_search_query")
            if not web_search_query:
                logger.error(f"响应中缺少Web搜索查询")
                return Message(
                    content="处理酒店查询时发生错误，请稍后再试。",
                    sender="HotelSearchAgent",
                    recipient=message.sender,
                    metadata={"entity_type": "HOTEL"}
                )
            logger.info(f"运行web搜索查询: '{web_search_query}'")
            web_search_results_summary = await asyncio.to_thread(WebAccess().run, web_search_query)
            return Message(
                content=web_search_results_summary,
                sender="HotelSearchAgent",
                recipient=message.sender,
                metadata={"entity_type": "HOTEL"}
            )
        except Exception as e:
            logger.error(f"处理酒店查询时发生错误: {e}")
            return Message(
                content="处理酒店查询时发生错误，请稍后再试。",
                sender="HotelSearchAgent",
                recipient=message.sender,
                metadata={"entity_type": "HOTEL"}
            )
