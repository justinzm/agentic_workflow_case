#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/16 16:48
# @File    : summarize
# @desc    : 汇总类


import os
import hashlib
from typing import Optional
from utils.logger import logger
from utils.ChatModel import ChatModel
from web_access.prompts import SUMMARIZE_SYSTEM, SUMMARIZE_USER


class WebSummarizeAgent:
    def __init__(self):
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()

        self.INPUT_DIR = '../web_access/data/output/scrape'
        self.OUTPUT_DIR = '../web_access/data/output/summarize'

    def _read_file(self, path: str) -> Optional[str]:
        """
        读取一个 Markdown 文件的内容，并将其以文本对象的形式

        Args:
            path (str): 指向 Markdown 文件的路径。

        Returns:
            Optional[str]: 文件的内容以字符串形式呈现，若无法读取文件则为 None 。
        """
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content: str = file.read()
                return content
        except FileNotFoundError:
            logger.info(f"File not found: {path}")
            return None
        except Exception as e:
            logger.info(f"Error reading file: {e}")
            return None

    def generate_filename(self, query: str, extension: str) -> str:
        """
        根据提供的查询生成唯一哈希的文件名。

        :param query: 用于生成唯一哈希文件名的查询字符串。
        :param extension: 文件扩展名（例如 'json' 或 'txt'）。
        :return: 表示生成的文件名的字符串。
        :raises ValueError: 如果未提供查询，则引发异常。
        """
        try:
            if not query:
                raise ValueError("Query is missing")

            encoded_query = query.encode('utf-8')
            filename = hashlib.md5(encoded_query).hexdigest()
            return f"{filename}.{extension}"
        except Exception as e:
            logger.error(f"Error generating filename: {e}")
            raise

    def _read_scraped_content(self, query: str) -> str:
        """
        根据查询条件，从输入目录中读取抓取到的内容。

        Args:
            query (str): 用于定位特定抓取内容的查询字符串。

        Returns:
            str: 将抓取的内容转换为字符串形式。
        """
        try:
            logger.info(f"阅读采集数据文件: '{query}'")
            input_file_path = os.path.join(self.INPUT_DIR, self.generate_filename(query, 'txt'))
            return self._read_file(input_file_path)
        except Exception as e:
            logger.error(f"Error reading scraped content: {e}")
            raise

    def _save_summary(self, summary: str, query: str) -> None:
        """
        将生成的摘要保存到指定的输出目录中。

        Args:
            summary (str): 生成的用于保存的摘要。
            query (str): 用于生成文件名的查询字符串。
        """
        output_path = os.path.join(self.OUTPUT_DIR, f"{self.generate_filename(query, 'txt')}")
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            logger.info(f"存储摘要内容到 {output_path}")
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(summary)
            logger.info("完成摘要存储.")
        except Exception as e:
            logger.error(f"存储摘要错误: {e}", exc_info=True)
            raise

    def run(self, query: str) -> str:
        """
        生成摘要
        """
        scraped_content = self._read_scraped_content(query)
        summarize_user = SUMMARIZE_USER.format(query=query, scraped_content=scraped_content)
        try:
            summary = (
                self.agent
                .general(SUMMARIZE_SYSTEM)
                .input(summarize_user)
                .output("生成一份全面且带有恰当引用的摘要")
                .start()
            )
            # Save the summary
            self._save_summary(summary, query)
            return summary
        except Exception as e:
            logger.error(f"生成摘要错误: {e}")
            raise