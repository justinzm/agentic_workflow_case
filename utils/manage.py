#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郭
# @mail    : 3907721@qq.com
# @Time    : 2025/7/14 16:00
# @File    : manage.py
# @desc    :

from collections import OrderedDict
from typing import Optional
from typing import Dict
from typing import Any
from utils.logger import logger


class StateManager:
    """
    状态管理器类，维护一个有序字典来存储键值对，
    并提供将状态转换为Markdown格式字符串的功能。

    属性:
        _state (OrderedDict[str, Any]): 用于存储状态条目的有序字典。
        _state_md (Optional[str]): 状态的Markdown格式字符串表示。
    """

    def __init__(self):
        """
        使用空的有序字典初始化StateManager，Markdown状态设为None。
        """
        self._state: OrderedDict[str, Any] = OrderedDict()
        self._state_md: Optional[str] = None

    def add_entry(self, key: str, value: Any) -> None:
        """
        向状态中添加键值对并更新Markdown表示。

        参数:
            key (str): 状态条目的键。
            value (Any): 与键关联的值。

        异常:
            ValueError: 如果键为空或None。
            Exception: 如果在处理过程中发生任何其他错误。
        """
        if not key:
            logger.error("提供的键为空或None。")
            raise ValueError("键不能为空或None。")

        try:
            self._state[key] = value
            self._state_md = self.to_markdown()
            logger.debug(f"条目已添加到状态: {key} = {value}")
        except Exception as e:
            logger.error(f"向状态添加条目时出错: {e}")
            raise

    def to_markdown(self) -> str:
        """
        将当前状态转换为Markdown格式的字符串。

        返回:
            str: Markdown格式的状态字符串。

        异常:
            Exception: 如果在转换过程中发生错误。
        """
        try:
            markdown = []
            for key, value in self._state.items():
                markdown.append(f"### {key}\n")
                if isinstance(value, dict):
                    markdown.append(f"\n{self._dict_to_markdown(value)}\n")
                else:
                    markdown.append(f"\n{value}\n")
                markdown.append("\n")
            logger.info("状态已成功转换为Markdown。")
            return ''.join(markdown)
        except Exception as e:
            logger.error(f"将状态转换为Markdown时出错: {e}")
            raise

    @staticmethod
    def _dict_to_markdown(data: Dict[str, Any], indent_level: int = 0) -> str:
        """
        递归地将字典转换为Markdown格式的字符串。

        参数:
            data (Dict[str, Any]): 要转换的字典。
            indent_level (int): 嵌套字典的当前缩进级别。

        返回:
            str: Markdown格式的字典字符串。

        异常:
            Exception: 如果在转换过程中发生错误。
        """
        try:
            markdown = []
            indent = ' ' * indent_level
            for key, value in data.items():
                if isinstance(value, dict):
                    markdown.append(f"{indent}- **{key.capitalize()}**:\n")
                    markdown.append(StateManager._dict_to_markdown(value, indent_level + 2))
                else:
                    markdown.append(f"{indent}- **{key.capitalize()}**: {value}\n")
            logger.info("字典已成功转换为Markdown。")
            return ''.join(markdown)
        except Exception as e:
            logger.error(f"将字典转换为Markdown时出错: {e}")
            raise

    def get_state(self) -> OrderedDict[str, Any]:
        """
        获取当前状态作为有序字典。

        返回:
            OrderedDict[str, Any]: 当前状态。
        """
        return self._state

    def get_state_markdown(self) -> Optional[str]:
        """
        获取当前状态的Markdown格式字符串。

        返回:
            Optional[str]: Markdown格式的当前状态，如果状态为空则返回None。
        """
        return self._state_md


if __name__ == "__main__":
    state_manager = StateManager()

    # 2. 添加状态条目
    state_manager.add_entry("任务开始", "开始执行工作流程")
    state_manager.add_entry("步骤1", "完成数据收集")

    # 3. 添加复杂数据结构
    complex_data = {
        "结果": "成功",
        "详情": {
            "处理时间": "2分钟",
            "数据量": "1000条"
        }
    }
    state_manager.add_entry("执行结果", complex_data)

    # 4. 获取状态
    current_state = state_manager.get_state()  # 返回OrderedDict
    markdown_output = state_manager.get_state_markdown()  # 返回Markdown字符串

    # 5. 输出最终报告
    final_report = state_manager.to_markdown()
    print(final_report)