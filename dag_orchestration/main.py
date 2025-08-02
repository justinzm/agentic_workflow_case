#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/8/2 10:56
# @File    : main
# @desc    :


import json
import asyncio
from utils.logger import logger
from utils.message import Message
from dag_orchestration.coordinator import CoordinatorAgent


class DagOrchestrationAgent:
    """
    DAG编排智能体的主要入口点。
    该智能体负责协调执行DAG（有向无环图）中定义的任务。
    """
    def __init__(self) -> None:
        self.pattern_root_path = './data/'
        self.dag_file_path = f"{self.pattern_root_path}dag.yml"
        self.report_file_path = f"{self.pattern_root_path}final_report.md"

    async def run(self) -> None:
        """
        主流程函数，用于通过协调者智能体（Coordinator agent）编排任务处理。
        该函数处理主任务消息，并将最终输出保存为JSON文件。

        步骤：
        1. 使用指定的DAG文件初始化协调者。
        2. 向协调者发送主任务消息进行处理。
        3. 接收响应并提取内容。
        4. 将最终内容保存为JSON报告。

        返回值：None
        """
        try:
            logger.info("正在使用DAG文件初始化协调器智能体。")
            coordinator = CoordinatorAgent(name="CoordinatorAgent", dag_file=self.dag_file_path)

            # 主要任务是编排DAG（有向无环图），因此消息无需包含特定内容。
            message = Message(content='', sender="User", recipient="CoordinatorAgent")

            logger.info("将主要任务消息发送给协调器进行处理。")
            response = await coordinator.process(message)

            final_output = response.content
            self.save_final_report(final_output['report'])

            logger.info("任务已成功完成。最终报告已保存。")

        except Exception as e:
            logger.error(f"执行DAG编排智能体时发生错误: {e}")
            raise


    def save_final_report(self, report_data: str) -> None:
        """
        将最终输出保存为JSON文件。

        :param report_data: str: 处理后的输出内容，将被保存为JSON格式。
        :return: None
        """
        try:
            with open(self.report_file_path, 'w', encoding='utf-8') as f:
                # json.dump(report_data, f, ensure_ascii=False, indent=4)
                f.write(report_data)
            logger.info(f"最终报告已成功保存到 {self.report_file_path}")
        except Exception as e:
            logger.error(f"保存最终报告时发生错误: {e}")
            raise


if __name__ == "__main__":
    agent = DagOrchestrationAgent()
    asyncio.run(agent.run())
