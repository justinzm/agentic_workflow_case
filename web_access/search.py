#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/15 12:10
# @File    : search
# @desc    :

from utils.logger import logger
from utils.ChatModel import ChatModel
from web_access.prompts import SEARCH_SYSTEM, SEARCH_USER
from web_access.serp import run as google_search


class WebSearchAgent:
    def __init__(self):
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()


    def run(self, query: str, location: str) -> str:
        search_user = SEARCH_USER.format(query=query)
        try:
            result = (
                self.agent
                .general(SEARCH_SYSTEM)
                .input(search_user)
                .output({
                    "search_terms": ("str", "搜索关键词")
                })
                .start()
            )
            logger.debug(f"搜索关键词: {result['search_terms']}")
            google_search(raw_query=query, search_query=result["search_terms"], location=location)
        except Exception as e:
            return f"搜索失败，原因是: {str(e)}"


if __name__ == "__main__":
    query = "中美贸易战的影响"
    results = WebSearchAgent().run(query)
    print(results)