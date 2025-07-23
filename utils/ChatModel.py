#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2024/9/18 09:51
# @File    : ChatModel
# @desc    : 聊天模型类


import os
from dotenv import load_dotenv
load_dotenv()

import Agently

class ChatModel:
    # 创建agent
    def get_agent_factory(self, model_source="gemini"):
        if model_source == "doubao_deepseek":
            agent_factory = Agently.AgentFactory()
            (
                agent_factory
                .set_settings("current_model", "OAIClient")
                .set_settings("model.OAIClient.auth", {"api_key": os.getenv("DOUBAO_API_KEY")})
                .set_settings("model.OAIClient.url", "https://ark.cn-beijing.volces.com/api/v3")
                .set_settings("model.OAIClient.options", {"model": os.getenv('DOUBAO_DEEPSEEK_V3'), "temperature": 0.7})
                .set_settings("is_debug", False)
            )
        elif model_source == "doubao_1.6":
            agent_factory = Agently.AgentFactory()
            (
                agent_factory
                .set_settings("current_model", "OAIClient")
                .set_settings("model.OAIClient.auth", {"api_key": os.getenv("DOUBAO_API_KEY")})
                .set_settings("model.OAIClient.url", "https://ark.cn-beijing.volces.com/api/v3")
                .set_settings("model.OAIClient.options", {"model": os.getenv('DOUBAO_SEED_1.6'), "temperature": 0.7})
                .set_settings("is_debug", False)
            )
        elif model_source == "gemini":
            agent_factory = Agently.AgentFactory()
            (
                agent_factory
                .set_settings("current_model", "OAIClient")
                .set_settings("model.OAIClient.auth", {"api_key": os.getenv("GOOGLE_API_KEY")})
                .set_settings("model.OAIClient.url", "https://generativelanguage.googleapis.com/v1beta/openai/")
                .set_settings("model.OAIClient.options", {"model": "gemini-2.5-pro"})
                .set_proxy("http://127.0.0.1:7890")
            )
        else:
            raise ValueError(f"不支持的模型源: {model_source}")
        return agent_factory


if __name__ == '__main__':
    agent_factory = ChatModel().get_agent_factory(model_source="doubao_deepseek")
    agent = agent_factory.create_agent()
    print(
        agent
        .input("慈禧是谁")
        .instruct("输出语言", "中文")
        .start()
    )