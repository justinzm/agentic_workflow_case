#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/14 10:57
# @File    : main
# @desc    :


from actor import Actor
from critic import Critic
from utils.logger import logger
from utils.manage import StateManager


class Runner:
    def __init__(self, topic: str, num_cycles: int):
        self.topic = topic
        self.num_cycles = num_cycles
        self.state_manager = StateManager()

        self.actor = Actor(topic=topic)
        self.critic = Critic()

    def run(self) -> str:
        """
        运行指定周期数的流水线。

        返回值：
            str：最终状态的 Markdown 格式文本。
        """
        try:
            for cycle in range(self.num_cycles):
                self._run_cycle(cycle)
            logger.info("所有循环已完成")
            return self.state_manager.to_markdown()
        except Exception as e:
            logger.error(f"运行出错误: {e}")
            raise

    def _run_cycle(self, cycle: int) -> None:
        """
        运行一轮 参与者-评论者循环。

        参数：
            cycle（整型）：当前的循环次数。
        """
        try:
            logger.info(f"开始第 {cycle + 1} 轮对话")
            if cycle == 0:
                self._run_initial_cycle()
            else:
                self._run_revised_cycle(cycle)
            logger.info(f"完成第 {cycle + 1} 次循环")
        except Exception as e:
            logger.error(f"完成第 {cycle + 1} 次，循环错误: {e}")
            raise

    def _run_initial_cycle(self):
        """
        开始进行第一个循环，即参与者先撰写初稿，然后评论者对其进行评审。
        """
        try:
            logger.info("开始运行周期")
            initial_draft = self.actor.generate_initial_draft()
            self.state_manager.add_entry("initial_draft V0", initial_draft)

            initial_review = self.critic.review_draft(initial_draft)
            self.state_manager.add_entry("initial_review", initial_review)
        except Exception as e:
            logger.error(f"Error in Pipeline._run_initial_cycle: {e}")
            raise

    def _run_revised_cycle(self, cycle: int) -> None:
        """
        进行修订循环，即参与者和评论者对草稿和评论进行修订。

        参数：
            cycle（整型）：当前的循环次数。
        """
        try:
            logger.info(f"开始运行修订周期 {cycle + 1}")
            print(self.state_manager.to_markdown())
            revised_draft = self.actor.revised_draft(self.state_manager.to_markdown(), cycle)
            self.state_manager.add_entry(f"修订稿 V{cycle + 1}", revised_draft)

            revised_review = self.critic.revise_review(self.state_manager.to_markdown(), cycle)
            self.state_manager.add_entry(f"修订评论 V{cycle + 1}", revised_review)
        except Exception as e:
            logger.error(f"Error in Pipeline._run_revised_cycle (cycle {cycle + 1}): {e}")
            raise

if __name__ == "__main__":
    topic = "大模型 MCP"
    num_cycles = 3
    final_state = Runner(topic, num_cycles).run()
    print(final_state)
    pass