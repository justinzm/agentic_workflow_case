#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/4/25 11:32
# @File    : search_tool
# @desc    : AI Search API
# API简介：通过调用该API可回答用户问题，返回网页、图片、多模态参考源、总结答案和追问问题等，还能获取垂域结构化数据，支持流式输出，每次搜索返回的参考网页最多50条。
# 搜索结果：网页最多返回50条含摘要的信息；图片为网页中附带的；模态卡类型多样，如天气、百科、医疗等，根据不同搜索词动态显示。自2024年11月13日起，抖音视频需配合SDK唤起播放，返回结果有相应变化。

import os
from dotenv import load_dotenv
load_dotenv()

import requests
from typing import Dict, Any


def baidu_search(query: str, max_results: int = 10) -> Dict[str, Any]:
    r"""
    搜索百度使用网络抓取检索相关的搜索结果。该方法查询百度的搜索引擎并提取搜索结果，包括标题、描述和url。

    Args:
        query (str): 搜索要提交给百度的查询字符串。
        max_results (int): 要返回的最大结果数。

    Returns:
        Dict[str, Any]: 包含搜索结果或错误消息的字典。
    """
    from bs4 import BeautifulSoup

    try:
        url = "https://www.baidu.com/s"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.baidu.com",
        }
        params = {"wd": query, "rn": str(max_results)}

        response = requests.get(url, headers=headers, params=params)
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for idx, item in enumerate(soup.select(".result"), 1):
            title_element = item.select_one("h3 > a")
            title = (
                title_element.get_text(strip=True) if title_element else ""
            )

            link = title_element["href"] if title_element else ""

            desc_element = item.select_one(".c-abstract, .c-span-last")
            desc = (
                desc_element.get_text(strip=True) if desc_element else ""
            )

            results.append(
                {
                    "result_id": idx,
                    "title": title,
                    "description": desc,
                    "url": link,
                }
            )
            if len(results) >= max_results:
                break

        if not results:
            print(
                "Warning: No results found. Check "
                "if Baidu HTML structure has changed."
            )

        return {"results": results}

    except Exception as e:
        return {"error": f"Baidu scraping error: {e!s}"}


def bocha_search(query: str, count: int = 10) -> str:
    """
    使用Bocha Web Search API 进行网页搜索。

    参数:
    - query: 搜索关键词
    - freshness: 搜索的时间范围
    - summary: 是否显示文本摘要
    - count: 返回的搜索结果数量

    返回:
    - 搜索结果的详细信息，包括网页标题、网页URL、网页摘要、网站名称、网站Icon、网页发布时间等。
    """

    url = 'https://api.bochaai.com/v1/ai-search'
    headers = {
        'Authorization': f'Bearer {os.getenv("BOCHA_KEY")}',  # 请替换为你的API密钥
        'Content-Type': 'application/json'
    }
    data = {
        "query": query,
        "freshness": "noLimit",  # 搜索的时间范围，例如 "oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"
        "count": count,
        "answer": True
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        json_response = response.json()
        try:
            if json_response["code"] != 200 or not json_response["messages"]:
                return f"搜索API请求失败，原因是: {response.msg or '未知错误'}"

            webpages = json_response["messages"]
            if not webpages:
                return "未找到相关结果。"
            formatted_results = ""
            for idx, page in enumerate(webpages, start=1):
                formatted_results += (
                    f"引用: {idx}\n"
                    f"发送消息实体: {page['role']}\n"
                    f"消息实体: {page['type']}\n"
                    f"消息内容: {page['content']}\n"
                    f"消息内容类型: {page['content_type']}\n"
                )
            return formatted_results.strip()
        except Exception as e:
            return f"搜索API请求失败，原因是：搜索结果解析失败 {str(e)}"
    else:
        return f"搜索API请求失败，状态码: {response.status_code}, 错误信息: {response.text}"


if __name__ == '__main__':
    query = "西瓜的功效与作用"
    res = bocha_search(query)
    print(res)
