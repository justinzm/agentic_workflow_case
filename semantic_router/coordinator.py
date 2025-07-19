#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/19 14:08
# @File    : coordinator.py
# @desc    : 协调智能体


from typing import List
from utils.logger import logger
from utils.ChatModel import ChatModel
from semantic_router.prompts import ROUTE_SYSTEM, ROUTE_USER, COORDINATOR_SYSTEM, COORDINATOR_USER
from utils.message import Message


class TravelPlannerAgent:
    """
    旅行规划代理，负责根据检测到的意图将旅行相关查询路由到子代理，并生成综合响应。
    """

    def __init__(self, name: str, sub_agents: List):
        """
        初始化 TravelPlannerAgent，设置子代理和共享资源。

        :param name: 代理的名称。
        :param sub_agents: 负责特定任务（如航班、酒店等）的子代理列表。
        """
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()

        self.name = name
        self.sub_agents = {agent.name: agent for agent in sub_agents}
        logger.info(f"{self.name} initialized with {len(self.sub_agents)} sub-agents.")


    def determine_intent(self, query: str) -> str:
        """
        确定用户意图，基于查询内容返回确定的用户意图。

        :param query: 用户输入的查询内容。
        :return: 确定的用户意图。
        """
        route_user = ROUTE_USER.format(query=query)
        try:
            logger.info(f"确定意图，查询内容: '{query}'")
            result = (
                self.agent
                .general(ROUTE_SYSTEM)
                .input(route_user)
                .output({
                    'intent': ("str", "用户查询的意图，如航班搜索、酒店搜索、租车搜索和未知。输出四个意图之一。")
                })
                .start()
            )
            intent_str = result['intent']
            logger.info(f"确定意图: '{intent_str}'")
            if intent_str in ["航班搜索", "酒店搜索", "租车搜索", "未知"]:
                return intent_str
            else:
                logger.warning(f"意图 '{intent_str}' 不在预定义范围内，返回未知。")
                return "未知"
        except Exception as e:
            logger.error(f"确定意图时出现意外错误: {e}")
            return "未知"

    def route_to_agent(self, intent: str):
        """
        根据确定的意图路由到相应的子代理。

        :param intent: 确定的用户意图。
        :return: 相应子代理的输出。
        """
        intent_to_agent = {
            "航班搜索": "FlightSearchAgent",
            "酒店搜索": "HotelSearchAgent",
            "租车搜索": "CarRentalSearchAgent",
            "未知": None
        }

        agent_name = intent_to_agent.get(intent)
        if not agent_name:
            logger.error(f"没有找到有效的智能体: {intent}")
            return None

        logger.info(f"路由指向智能体: '{agent_name}'")
        return self.sub_agents.get(agent_name)

    def process(self, message: Message) -> Message:
        """
        处理用户消息，根据确定的意图路由到相应的子智能体，生成综合响应。

        :param message: 用户消息，包含查询内容和其他相关信息。
        :return: 综合响应消息。
        """
        try:
            logger.info(f"{self.name} 处理消息: '{message.content}'")
            intent = self.determine_intent(message.content)

            sub_agent = self.route_to_agent(intent)
            if sub_agent is None:
                raise ValueError(f"未知意图: {intent}")

            sub_message = Message(
                content=message.content,
                sender=self.name,
                recipient=sub_agent.name,
                metadata={"intent": intent}
            )

            sub_response = sub_agent.process(sub_message)
            summary = sub_response.content

            coordinator_system = COORDINATOR_SYSTEM.format(query=message.content, summary=summary)
            coordinator_user = COORDINATOR_USER.format(query=message.content, summary=summary)
            final_response_text = (
                self.agent
                .general(coordinator_system)
                .input(coordinator_user)
                .output("给出清晰、信息丰富且易于理解的回应")
                .start()
            )
            return Message(
                content=final_response_text,
                sender=self.name,
                recipient="User"
            )
        except Exception as e:
            logger.error(f"处理消息时出现意外错误: {e}")
            return Message(
                content="抱歉，我无法回答您的问题。",
                sender=self.name,
                recipient="User"
            )
