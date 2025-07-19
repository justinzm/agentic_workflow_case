#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/19 18:46
# @File    : car_rental_search
# @desc    : 汽车租赁查询 智能体


from typing import Optional
from utils.logger import logger
from utils.message import Message
from utils.ChatModel import ChatModel
from web_access.main import WebAccess
from semantic_router.prompts import CAR_RENTAL_SYSTEM, CAR_RENTAL_USER


class CarRentalSearchAgent:
    """
    负责处理汽车租赁咨询、生成网络搜索查询，并返回汇总结果。
    """
    def __init__(self, name: str):
        self.name = name
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()

    def process(self, message: Message) -> Message:
        """
        处理汽车租赁查询，生成网络搜索查询并返回结果。

        :param message: 包含查询内容的消息对象。
        :return: 包含搜索结果的消息对象。
        """
        logger.info(f"汽车租凭查询: '{message.content}'")
        car_rental_user = CAR_RENTAL_USER.format(query=message.content)
        try:
            result = (
                self.agent
                .general(CAR_RENTAL_SYSTEM)
                .input(car_rental_user)
                .output({
                    "web_search_query": ("str", "汽车租赁查询优化后的内容")
                })
                .start()
            )
            web_search_query: Optional[str] = result.get("web_search_query")
            if not web_search_query:
                logger.error(f"响应中缺少Web搜索查询")
                return Message(
                    content="处理汽车租赁查询时发生错误，请稍后再试。",
                    sender="CarRentalSearchAgent",
                    recipient=message.sender
                )
            logger.info(f"运行web搜索查询: '{web_search_query}'")
            web_search_results_summary = WebAccess().run(web_search_query)
            return Message(
                content=web_search_results_summary,
                sender="CarRentalSearchAgent",
                recipient=message.sender
            )
        except Exception as e:
            logger.error(f"处理汽车租赁查询时发生错误: {e}")
            return Message(
                content="处理汽车租赁查询时发生错误，请稍后再试。",
                sender="CarRentalSearchAgent",
                recipient=message.sender
            )