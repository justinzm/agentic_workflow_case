#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/14 17:24
# @File    : actor
# @desc    : 参与者类

from utils.logger import logger
from utils.save_to_disk import save_to_disk
from utils.ChatModel import ChatModel
from reflection.prompts import ACTOR_DRAFT_SYSTEM, ACTOR_DRAFT_USER, ACTOR_REVISE_USER, ACTOR_REVISE_SYSTEM


class Actor:
    def __init__(self, topic: str):
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()

        self.output_path = "./data/"
        self.topic = topic


    def generate_initial_draft(self) -> str:
        """
        生成初始草稿并存储。
        :return:
        """
        actor_draft_user = ACTOR_DRAFT_USER.format(topic=self.topic)
        try:
            result = (
                self.agent
                .general(ACTOR_DRAFT_SYSTEM)
                .input(actor_draft_user)
                .output("指定主题撰写内容")
                .start()
            )
            self._save_content(result, "draft", 0)
            return result
        except Exception as e:
            logger.error(f"生成初始草稿时出错: {e}")
            raise

    def revised_draft(self, state: str, version: int) -> str:
        """
        根据现有草稿的当前状态进行修改，并保存修改后的版本。

        参数:
        -----
            state : str            评论者的反馈内容。
            version : int          当前版本号。

        返回值:
        -------
            str : 修订后的草稿内容。
        """
        actor_revise_user = ACTOR_REVISE_USER.format(history=state)

        try:
            result = (
                self.agent
                .general(ACTOR_REVISE_SYSTEM)
                .input(actor_revise_user)
                .output("提供一份简洁、已整合所有反馈点的修订说明")
                .start()
            )
            self._save_content(result, "draft", version)
            return result
        except Exception as e:
            logger.error(f"修订草稿时出错: {e}")
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

if __name__ == "__main__":
    topic = "如何提高工作效率"
    actor = Actor(topic=topic)
    actor.generate_initial_draft()
    pass