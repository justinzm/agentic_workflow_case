#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/14 17:49
# @File    : critic
# @desc    : 评论者类

from utils.logger import logger
from utils.ChatModel import ChatModel
from utils.save_to_disk import save_to_disk
from reflection.prompts import CRITIC_REVIEW_SYSTEM, CRITIC_REVIEW_USER, CRITIC_REVISE_SYSTEM, CRITIC_REVISE_USER


class Critic:
    def __init__(self):
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()

        self.output_path = "./data/"


    def review_draft(self, draft: str) -> str:
        """
        查看所提供的草稿并完成评审。

        Parameters：
        -----------
        draft：str       需要审核的摘要内容。

        Returns：str     生成的评论内容。
        """
        critic_review_user = CRITIC_REVIEW_USER.format(article=draft)
        try:
            result = (
                self.agent
                .general(CRITIC_REVIEW_SYSTEM)
                .input(critic_review_user)
                .output("您的评审结果")
                .start()
            )
            self._save_content(result, "feedback", 0)
            return result
        except Exception as e:
            logger.error(f"评论草稿时出错: {e}")
            raise


    def revise_review(self, state: str, version: int) -> str:
        """
        根据现有评论的当前状态对其进行修改，并保存修改后的版本。

        参数：
        -----------
        state : str      待修订的评审的当前状态。
        version : int    修订后的评审的版本号。

        Returns：str     修订后的评审内容。
        """
        critic_revise_user = CRITIC_REVISE_USER.format(history=state)

        try:
            result = (
                self.agent
                .general(CRITIC_REVISE_SYSTEM)
                .input(critic_revise_user)
                .output("修订后的评审结果")
                .start()
            )
            self._save_content(result, "feedback", version)
            return result
        except Exception as e:
            logger.error(f"修订评论时出错: {e}")
            raise


    def _save_content(self, content: str, content_type: str, version: int) -> None:
        """
        将生成的内容保存到磁盘。

        参数:
        -----
        content : str             要保存的内容。
        content_type : str       保存内容的类型（例如 'draft'，'feedback'）。
        version : int            要保存内容的版本号。
        """
        try:
            save_to_disk(content, content_type, version, self.output_path)
        except Exception as e:
            logger.error(f"Error saving {content_type}: {e}")
            raise