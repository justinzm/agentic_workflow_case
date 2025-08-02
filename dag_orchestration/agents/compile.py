#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/8/2 14:24
# @File    : compile
# @desc    : 文档编译智能体


from utils.logger import logger
from utils.message import Message
from utils.ChatModel import ChatModel


class CompileAgent:
    """
    文档编译智能体
    该智能体负责将提取的关键信息编译成最终的文档格式。
    """
    def __init__(self, name: str) -> None:
        agent_factory = ChatModel().get_agent_factory()
        self.agent = agent_factory.create_agent()
        self.name = name

    async def process(self, message: Message) -> Message:
        """
        根据关键信息和摘要编制最终报告。

        参数：
            message (Message): 包含关键信息和摘要的输入消息。

        返回值：
            Message: 包含已编制报告的消息。
        """
        logger.info(f"{self.name} 开始编译最终报告。")
        input_data = message.content

        key_info_data = input_data['task3']["extracted_items"]
        summaries_data = input_data['task4']["summaries"]

        report_sections = []

        for key_info_entry in key_info_data:
            try:
                report_section = await self._compile_report_section(
                    key_info_entry, summaries_data
                )
                if report_section:
                    report_sections.append(report_section)
            except Exception as e:
                logger.error(f"编译文档ID '{key_info_entry['id']}' 的报告部分失败: {e}")
                raise RuntimeError(f"编译文档 '{key_info_entry['id']}' 的报告部分时出错") from e

        report = {"report": "\n\n".join(report_sections)}
        logger.info(f"{self.name} 成功编译并验证了最终报告。")
        return Message(content=report, sender=self.name, recipient=message.sender)

    async def _compile_report_section(self, key_info_entry: dict, summaries_data: list) -> str:
        """
        根据关键信息和摘要编制报告部分。

        参数：
            key_info_entry (dict): 文档的关键信息条目。
            summaries_data (list): 所有文档的摘要数据。

        返回值：
            str: 编制的报告部分。
        """
        doc_id = key_info_entry["id"]
        summary_entry = next((s for s in summaries_data if s["doc_name"] == doc_id), None)

        if not summary_entry:
            raise ValueError(f"未找到文档ID '{doc_id}' 的摘要")

        logger.info(f"正在为文档ID“{doc_id}”使用LLM编译报告部分。")
        llm_input = (
            f"你是一名报告汇编员。根据文档的摘要和关键信息，为该文档整理一份格式规范的报告部分。报告应包含以下内容：\n"
            f"- 文档标题（使用文档ID作为标题）。\n"
            f"- 摘要。\n"
            f"- 主要角色列表及简要描述。\n"
            f"- 主要主题及简要说明。\n"
            f"- 以叙述形式呈现的重要情节要点。\n\n"
            f"重要提示：报告部分需以清晰、结构化的格式提供。使用Markdown格式设置标题和列表。确保内容连贯且组织有序。\n\n"
            f"文档ID：{doc_id}\n"
            f"摘要：\n{summary_entry['summary']}\n\n"
            f"角色：\n{', '.join(key_info_entry['key_info'][0]['characters'])}\n\n"
            f"主题：\n{', '.join(key_info_entry['key_info'][0]['themes'])}\n\n"
            f"情节要点：\n- {' '.join(key_info_entry['key_info'][0]['plot_points'])}"
        )

        try:
            report_section = (
                self.agent
                .general("你是一个经过训练的人工智能，擅长根据提供的信息整理出清晰、结构完善的报告。")
                .input(llm_input)
                .output("输出编制的报告部分，确保格式清晰且内容连贯。")
                .start()
            )
            return report_section
        except Exception as e:
            logger.error(f"未能为文档ID“{doc_id}”编译报告部分：{e}")
            raise RuntimeError(f"文档“{doc_id}”的报告部分编译出错")