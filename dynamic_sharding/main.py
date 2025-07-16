#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/17 09:42
# @File    : main
# @desc    : 动态分片的主入口文件


import asyncio
from utils.logger import logger
from dynamic_sharding.message import Message
from dynamic_sharding.coordinator import Coordinator


async def run(input_file: str, output_file: str, shard_size: int = 3) -> None:
    """
    初始化协调器、处理输入数据，并将整合后的信息保存到输出文件中。
    Args:
        input_file (str): 输入文件的路径。
        output_file (str): 用于保存整合后信息的输出文件的路径。
        shard_size (int): 用于处理的每个分片中的实体数量。
    """

    with open(input_file, 'r', encoding='utf-8') as file:
        entities = [line.strip() for line in file.readlines()]

    # 创建包含实体和分片大小的消息
    message_content = {
        'entities': entities,
        'shard_size': shard_size
    }

    message = Message(content=message_content, sender="User", recipient="CoordinatorAgent")

    # 通过智能体处理该消息并获取响应
    response = await Coordinator(name="CoordinatorAgent").run(message)

    # 将响应内容写入输出文件
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(response.content)

    logger.info(f"整合后的信息已保存到 {output_file}")


if __name__ == "__main__":
    """
    主函数入口，执行动态分片处理流程。
    """
    input_file = "../dynamic_sharding/data/entities.txt"
    output_file = "../dynamic_sharding/data/entity_info.txt"
    shard_size = 3  # 每个分片中的实体数量

    asyncio.run(run(input_file, output_file, shard_size))

