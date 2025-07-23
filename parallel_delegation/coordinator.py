#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/19 14:08
# @File    : coordinator.py
# @desc    : 并行委托协调器智能体

import asyncio
from typing import List
from utils.logger import logger
from utils.ChatModel import ChatModel
from parallel_delegation.prompts import NER_SYSTEM, NER_USER, COORDINATOR_SYSTEM, COORDINATOR_USER
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


    async def perform_ner(self, query: str) -> dict:
        """
        执行命名实体识别，提取查询中的意图和相关实体。

        :param query: 用户输入的查询内容。
        :return: 包含意图和实体的字典。
        """
        ner_user = NER_USER.format(query=query)
        try:
            logger.info(f"执行NER，查询内容: '{query}'")
            result = (
                self.agent
                .general(NER_SYSTEM)
                .input(ner_user)
                .output({
                    "entities": {
                        "FLIGHT": {
                            "duration": ("str", "指定旅行的时长, 未指定返回‘NA’"),
                            "destination": ("str", "旅行的目的地, 未指定返回‘NA’"),
                            "date": ("str", "旅行的日期或月份, 未指定返回‘NA’"),
                            "origin": ("str", "旅行的起点, 未指定返回‘NA’"),
                            "num_passengers": ("str", "旅行乘客人数, 未指定返回‘NA’")
                        },
                        "HOTEL": {
                            "duration": ("str", "如果有所规定的话，那么停留的时长。未指定返回‘NA’"),
                            "destination": ("str", "酒店的位置, 未指定返回‘NA’"),
                            "date": ("str", "停留的日期或月份。未指定返回‘NA’"),
                            "num_passengers": ("str", "入住人数, 未指定返回‘NA’"),
                            "hotel_amenities": ("str", "所需的酒店设施（如有具体要求）。多个设施用逗号隔开。未指定返回‘NA’"),
                        },
                        "CAR_RENTAL": {
                            "duration": ("str", "租车的时长, 未指定返回‘NA’"),
                            "date": ("str", "租车的日期或月份, 未指定返回‘NA’"),
                            "car_type": ("str", "所需的汽车类型（如SUV、轿车等）。未指定返回‘NA’"),
                            "pickup_location": ("str", "租车的起点, 未指定返回‘NA’"),
                            "dropoff_location": ("str", "租车的终点, 未指定返回‘NA’")
                        }
                    }
                })
                .start()
            )
            logger.info(f"NER结果: {result}")
            return result
        except Exception as e:
            logger.error(f"执行NER时出现意外错误: {e}")
            return {}


    async def route_to_agent(self, entities: dict):
        """
        根据识别到的实体路由到相应的子智能体。
        :param entities: 包含识别到的意图和实体的字典。
        :return: 子智能体实例。
        """
        tasks = []
        for entity_type, entity_values in entities['entities'].items():
            agent = None
            if entity_type == "FLIGHT":
                agent = self.sub_agents.get("FlightSearchAgent")
            elif entity_type == "HOTEL":
                agent = self.sub_agents.get("HotelSearchAgent")
            elif entity_type == "CAR_RENTAL":
                agent = self.sub_agents.get("CarRentalSearchAgent")
            if agent:
                task = asyncio.create_task(self.process_entity(agent, entity_type, entity_values))
                tasks.append(task)
        return await asyncio.gather(*tasks)

    async def process_entity(self, agent, entity_type: str, entity_values: dict) -> Message:
        """
        处理特定实体类型的查询，调用相应的子智能体。

        :param agent: 子智能体实例。
        :param entity_type: 实体类型（如FLIGHT、HOTEL、CAR_RENTAL）。
        :param entity_values: 实体值字典。
        :return: 包含响应内容的消息对象。
        """
        query = f"{entity_type}: {str(entity_values)}"
        message = Message(content=query, sender=self.name, recipient=agent.name,
                          metadata={"entity_type": entity_type})
        return await agent.process(message)

    async def consolidate_responses(self, query: str, sub_responses: List[Message]) -> str:
        """
        合并所有子智能体的响应，生成最终的综合响应。

        :param query: 用户原始查询。
        :param sub_responses: 从子智能体获取的响应列表。
        :return: 综合后的响应内容。
        """
        logger.info("正在为用户生成最终的综合回复。")
        flight_summary = next((r.content for r in sub_responses if r.metadata["entity_type"] == "FLIGHT"), ""),
        hotel_summary = next((r.content for r in sub_responses if r.metadata["entity_type"] == "HOTEL"), ""),
        car_rental_summary = next((r.content for r in sub_responses if r.metadata["entity_type"] == "CAR_RENTAL"), "")

        coordinator_user = COORDINATOR_USER.format(query=query, flight_summary=flight_summary, hotel_summary=hotel_summary, car_rental_summary=car_rental_summary)

        try:
            summary = (
                self.agent
                .general(COORDINATOR_SYSTEM)
                .input(coordinator_user)
                .output("给出清晰、信息丰富且易于理解的回应")
                .start()
            )
            return summary.strip()
        except Exception as e:
            logger.error(f"合并响应时出现意外错误: {e}")
            return ""


    async def process(self, message: Message) -> Message:
        """
        处理用户消息，执行命名实体识别、路由到子智能体、合并响应。

        :param message: 用户消息，包含查询内容和其他相关信息。
        :return: 综合响应消息。
        """
        logger.info(f"{self.name} processing message: {message.content}")
        try:
            query = message.content

            # 执行命名实体识别
            entities = await self.perform_ner(query)

            # 路由到子智能体
            sub_agent = await self.route_to_agent(entities)

            # 合并响应
            final_response_text = await self.consolidate_responses(query, sub_agent)

            return Message(content=final_response_text, sender=self.name, recipient="User")
        except Exception as e:
            logger.error(f"处理消息时出现意外错误: {e}")
            return Message(
                content="在处理您的请求时，我遇到了一个错误。请稍后再试",
                sender=self.name,
                recipient="User"
            )

if __name__ == "__main__":
    async def main():
        result = await TravelPlannerAgent().perform_ner(
            "我需要从北京飞到上海，3月15日出发，2个人，还要在上海订一个有游泳池和健身房的酒店住3晚，另外需要租一辆SUV，在浦东机场取车，3天后在虹桥机场还车"
)
        print(result)


    asyncio.run(main())