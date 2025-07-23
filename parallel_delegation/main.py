#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/23 13:58
# @File    : main
# @desc    : 主函数，负责初始化代理并处理用户输入。


import asyncio
from utils.logger import logger
from utils.message import Message
from parallel_delegation.coordinator import TravelPlannerAgent
from parallel_delegation.hotel_search import HotelSearchAgent
from parallel_delegation.flight_search import FlightSearchAgent
from parallel_delegation.car_rental_search import CarRentalSearchAgent


async def main(user_query: str):
    """
    初始化子代理（航班、酒店、租车）以及“旅行规划代理”，然后处理用户查询以查找旅行安排。记录响应或遇到的任何错误。
    """
    # 初始化子代理
    flight_agent = FlightSearchAgent(name="FlightSearchAgent")
    hotel_agent = HotelSearchAgent(name="HotelSearchAgent")
    car_rental_agent = CarRentalSearchAgent(name="CarRentalSearchAgent")

    # 初始化旅行规划代理
    travel_planner = TravelPlannerAgent(
        name="TravelPlannerAgent",
        sub_agents=[flight_agent, hotel_agent, car_rental_agent]
    )

    initial_message = Message(content=user_query, sender="User", recipient="TravelPlannerAgent")

    try:
        # 处理用户查询
        response = await travel_planner.process(initial_message)
        if response:
            logger.info(f"Query: {user_query}")
            logger.info(f"Response: {response.content}")
    except Exception as e:
        logger.error(f"处理用户查询时出错: {e}")


if __name__ == "__main__":
    user_query = "我需要从北京飞到上海，3月15日出发，2个人，还要在上海订一个有游泳池和健身房的酒店住3晚，另外需要租一辆SUV，在浦东机场取车，3天后在虹桥机场还车"
    asyncio.run(main(user_query))