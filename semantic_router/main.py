#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/19 11:08
# @File    : main
# @desc    :


from typing import Union, List
from utils.logger import logger
from utils.message import Message
from semantic_router.coordinator import TravelPlannerAgent
from semantic_router.hotel_search import HotelSearch
from semantic_router.flight_search import FlightSearchAgent
from semantic_router.car_rental_search import CarRentalSearchAgent


class SemanticRouter:
    def __init__(self):
        self.flight_search = FlightSearchAgent(name='FlightSearchAgent')
        self.hotel_search = HotelSearch(name='HotelSearchAgent')
        self.car_rental_search = CarRentalSearchAgent(name='CarRentalSearchAgent')

        self.travel_planner = TravelPlannerAgent(
            name='TravelPlannerAgent',
            sub_agents=[self.flight_search, self.hotel_search, self.car_rental_search]
        )

    def run(self, queries: Union[List[str], str]) -> str:
        if isinstance(queries, str):
            queries = [queries]

        for query in queries:
            try:
                message = Message(content=query, sender="User", recipient="TravelPlannerAgent")
                reponse_message = self.travel_planner.process(message)

                logger.info(f"Query: {query}")
                logger.info(f"Response: {reponse_message.content}")

                return reponse_message.content
            except Exception as e:
                logger.error(f"处理查询 {query} 时出错: {str(e)}")
                raise

if __name__ == '__main__':
    res = SemanticRouter().run(queries="你能推荐几家武汉汉阳的酒店我下周入住吗？")

