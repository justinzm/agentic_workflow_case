#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/16 15:12
# @File    : scrape
# @desc    : 采集


import os
import re
import json
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from utils.logger import logger
from typing import Tuple, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


class WebScrapeAgent:
    """
    负责从搜索结果中抓取网页内容的类。
    """
    def __init__(self):
        self.INPUT_DIR = './data/output/search'
        self.OUTPUT_DIR = './data/output/scrape'
        self.MAX_WORKERS = 5  # 最大线程数

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

    def load_search_results(self, query: str, location: str) -> List[Dict[str, Any]]:
        """
        从 JSON 文件中根据查询和位置加载搜索结果。

        Args:
            query (str): 用于生成文件名的查询字符串。
            location (str): 用于附加文件上下文的位置标识符。

        Returns:
            List[Dict[str, Any]]: 搜索结果字典的列表。
        """
        try:
            filename = self.generate_filename(query, 'json')
            file_path = os.path.join(self.INPUT_DIR, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(
                    f"Search results file not found for query: '{query}' and location: '{location}'")

            with open(file_path, 'r') as file:
                data = json.load(file)

            logger.info(f"Loaded search results from '{filename}'")
            return data.get('Top Results', [])
        except Exception as e:
            logger.error(f"Error loading search results: {e}")
            raise

    def _clean_text(self, text: str) -> str:
        """
        清理提取的文本，去除多余的空格和换行符。

        Args：
            text (str)：原始提取的文本。

        Returns：
            str：去除不必要空格后的清理文本。
        """
        return re.sub(r'\s+', ' ', text).strip()

    def scrape_website(self, url: str) -> str:
        """
        从指定的 URL 抓取内容，超时时间为 5 秒。

        Args：
            url (str)：要抓取的网页 URL。

        Returns：
            str：提取的文本内容，如果发生错误则返回空字符串。
        """
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            extracted_text = ' '.join(elem.get_text() for elem in text_elements)
            return self._clean_text(extracted_text)
        except requests.Timeout:
            logger.warning(f"Skipping {url} due to timeout.")
            return ""
        except requests.RequestException as e:
            logger.warning(f"Error scraping {url}: {e}")
            return ""

    def scrape_with_delay(self, result: Dict[str, Any], delay: int) -> Tuple[Dict[str, Any], str]:
        """
        在一段时间后再次访问网站，以避免服务器过载

        Args:
            result (Dict[str, Any]): 包含 URL 和元数据的搜索结果。
            delay (int): 启动抓取操作前的延迟时间（单位：秒）。

        Returns:
            Tuple[Dict[str, Any], str]: 原始结果和抓取内容。
        """
        time.sleep(delay)
        content = self.scrape_website(result['Link'])
        return result, content

    def scrape_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        从提供的搜索结果中抓取内容。
        Args：
            results (List[Dict[str, Any]]):搜索结果的列表，每个元素为一个字典。
        返回值：
            List[Dict[str, Any]]: 包含标题、网址、摘要和内容的字典列表。
        """
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        scraped_results = []
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            future_to_result = {executor.submit(self.scrape_with_delay, result, i): result for i, result in enumerate(results)}
            for future in as_completed(future_to_result):
                try:
                    result, content = future.result()
                    if content:
                        scraped_results.append({
                            'title': result['Title'],
                            'url': result['Link'],
                            'snippet': result['Snippet'],
                            'content': content
                        })
                        logger.info(f"Scraped: {result['Title']}")
                    else:
                        logger.info(f"Skipping {result['Title']} due to empty content.")
                except Exception as e:
                    logger.error(f"Error processing result: {e}")
        return scraped_results

    def save_results(self, query: str, scraped_results: List[Dict[str, Any]]) -> None:
        """
        将抓取到的结果保存到文本文件中。

        Args:
            query (str): 用于生成文件名的查询字符串。
            scraped_results (List[Dict[str, Any]]): 抓取到的结果列表。
        """
        try:
            output_path = os.path.join(self.OUTPUT_DIR, self.generate_filename(query, 'txt'))

            with open(output_path, 'w', encoding='utf-8') as outfile:
                for result in scraped_results:
                    outfile.write("==== BEGIN ENTRY ====\n")
                    outfile.write(f"TITLE: {result['title']}\n")
                    outfile.write(f"URL: {result['url']}\n")
                    outfile.write(f"SNIPPET: {result['snippet']}\n")
                    outfile.write(f"CONTENT:\n{result['content']}\n")
                    outfile.write("==== END ENTRY ====\n\n")
            logger.info(f"采集完成，保存 '{output_path}'")
            time.sleep(3)
        except Exception as e:
            logger.error(f"保存采集数据错误: {e}")

    def run(self, query: str, location: str = '') -> str:
        """
        抓取与查询相关的网页内容。
        Args:
            query (str): 搜索关键词。
            location (str): 搜索位置。
        Returns:
            str: 抓取的网页内容摘要。
        """
        try:
            logger.info(f"Initiating scraping process for query: '{query}' and location: '{location}'")
            results = self.load_search_results(query, location)
            scraped_results = self.scrape_results(results)
            self.save_results(query, scraped_results)
        except Exception as e:
            logger.error(f"Error during scraping process: {e}")
            raise


if __name__ == '__main__':
    agent = WebScrapeAgent()
    url = "https://zh.wikipedia.org/zh-hans/%E4%B8%AD%E7%BE%8E%E8%B4%B8%E6%98%93%E6%88%98"
    content = agent.scrape_website(url)
    print(content)