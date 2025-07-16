#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/15 10:45
# @File    : main.py
# @desc    :


import os
import shutil
from utils.logger import logger
from web_access.search import WebSearchAgent
from web_access.scrape import WebScrapeAgent
from web_access.summarize import WebSummarizeAgent



class WebAccess:
    """
    负责协调执行搜索、抓取和总结任务的类。
    """
    def __init__(self):
        """
        初始化 WebAccess 类，设置日志记录器。
        """
        self._output_folders = [
            '../web_access/data/output/search',
            '../web_access/data/output/scrape',
            '../web_access/data/output/summarize'
        ]

    def _flush_output_folders(self):
        """
        在启动流程之前，会清空输出文件夹中的所有文件。
        """
        for folder in self._output_folders:
            try:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    logger.info(f"Flushed output folder: {folder}")
                else:
                    logger.warning(f"Output folder does not exist: {folder}")
            except Exception as e:
                logger.error(f"清空输出文件夹 {folder} 时出错: {str(e)}")
                raise


    def run(self, query: str, location: str = '') -> str:
        """
        依次执行以下流程：搜索、抓取和总结任务。
        Args:
            query (str): 搜索关键词。
            location (str): 搜索位置。
        Returns:
            str: 由搜索结果生成的摘要。
        """
        try:
            # 清空文件夹
            self._flush_output_folders()

            logger.info("执行搜索任务")
            WebSearchAgent().run(query, location)

            logger.info("执行采集任务")
            WebScrapeAgent().run(query, location)

            logger.info("执行汇总任务")
            summarize = WebSummarizeAgent().run(query)
            return summarize
        except Exception as e:
            logger.error(f"执行期间发生错误: {str(e)}")
            raise


if __name__ == "__main__":
    res = WebAccess().run(query="Leonardo DiCaprio", location="")