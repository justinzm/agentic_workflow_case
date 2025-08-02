#!/usr/bin/env python
# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : justin.郑
# @mail    : 3907721@qq.com
# @Time    : 2025/7/24 10:22
# @File    : coordinator
# @desc    : DAG 编排模式协调器


import yaml
import json
import asyncio
import importlib
from utils.logger import logger
from utils.message import Message
from typing import List, Dict, Any, Optional


class CoordinatorAgent:
    """
    DAG 编排模式协调器
    """
    def __init__(self, name: str, dag_file: str) ->None:
        """
        初始化CoordinatorAgent，需指定名称和DAG文件。

        参数：
            - name (str): 协调器代理的名称。
            - dag_file (str): 定义DAG的YAML文件路径。
        """
        self.name = name
        self.dag_file = dag_file
        self.tasks = {}
        self.task_results = {}
        self.task_states = {}
        # 加载DAG定义
        self._load_dag()
        logger.info(f"{self.name} 初始化.")


    async def process(self, message: Message) -> Message:
        """
        处理传入的消息并执行有向无环图（DAG）。

        参数：
            message (Message): 协调器的输入消息。

        返回：
            Message: 执行DAG后的最终输出消息。
        """
        logger.info(f"{self.name} 开始处理消息")
        try:
            # 根据任务间的依赖关系执行DAG中定义的任务。
            await self._execute_dag()
            final_task_id = self._find_final_task()
            final_output = self.task_results.get(final_task_id, "未生成最终输出。")
            return Message(content=final_output, sender=self.name, recipient=message.sender)
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            return Message(
                content="处理任务时发生错误。",
                sender=self.name,
                recipient=message.sender
            )

    def _find_final_task(self) -> Optional[str]:
        """
        查找DAG中没有依赖项的最终任务。

        返回：
            Optional[str]: 最终任务的ID，若未找到则返回None。
        """
        all_tasks = set(self.tasks.keys())
        dependent_tasks = {dep for task in self.tasks.values() for dep in task['dependencies']}
        final_tasks = all_tasks - dependent_tasks
        return final_tasks.pop() if final_tasks else None

    async def _execute_dag(self) -> None:
        """
        根据任务间的依赖关系执行DAG中定义的任务。
        """
        logger.info(f"{self.name} 开始执行DAG任务")
        # 初始化待执行任务集合
        pending_tasks = set(self.tasks.keys())

        while pending_tasks:
            executable_tasks = self._find_executable_tasks(pending_tasks)
            if not executable_tasks:
                logger.warning("没有可执行的任务，可能存在循环依赖或未满足的依赖条件。")
                break

            tasks = []
            for task_id in executable_tasks:
                task_data = self.tasks[task_id]
                agent = self._create_agent(task_data['agent'], task_data['name'])
                input_data = self._collect_inputs(task_data['dependencies'])
                sub_message = Message(content=input_data, sender=self.name, recipient=agent.name)
                task = asyncio.create_task(self._run_task(task_id, agent, sub_message))
                tasks.append(task)
                pending_tasks.remove(task_id)
                self.task_states[task_id] = 'running'

            await asyncio.gather(*tasks)

    async def _run_task(self, task_id: str, agent, message: Message) -> None:
        """
        使用指定代理和消息运行单个任务。

        参数：
        - task_id (str): 要运行的任务ID。
        - agent (Agent): 负责处理任务的代理程序。
        - message (Message): 包含输入数据的消息对象。
        """
        logger.info(f"运行任务 {task_id} 使用代理 {agent.name}")
        try:
            result_message = await agent.process(message)
            self.task_results[task_id] = result_message.content
            self.task_states[task_id] = 'completed'
            logger.info(f"任务 {task_id} 完成，结果: {result_message.content}")
        except Exception as e:
            self.task_states[task_id] = 'failed'
            logger.error(f"任务 {task_id} 执行失败: {e}")


    def _create_agent(self, agent_class_name: str, agent_name: str):
        """
        动态根据代理类名创建智能体实例。

        参数：
            agent_class_name (str): 智能体类的名称。
            agent_name (str): 智能体实例的名称。

        返回值：
            Agent: 指定智能体类的实例对象。
        """
        agent_module_map = {
            'CollectAgent': 'collect',
            'PreprocessAgent': 'preprocess',
            'ExtractAgent': 'extract',
            'CompileAgent': 'compile',
            'SummarizeAgent': 'summarize',
        }

        module_name = agent_module_map.get(agent_class_name)
        if not module_name:
            raise ImportError(f"未找到智能体类“{agent_class_name}”对应的模块")

        try:
            # 加载指定模块并获取智能体类
            module = importlib.import_module(f'dag_orchestration.agents.{module_name}')
            agent_class = getattr(module, agent_class_name)
            return agent_class(name=agent_name)
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(f"无法从模块“{module_name}”创建代理“{agent_class_name}”：{e}")

    def _collect_inputs(self, dependencies: list) -> Dict[str, Any]:
        """
        根据任务依赖关系收集输入数据。

        参数:
            dependencies (list): 依赖任务ID的列表。

        返回:
            Dict[str, Any]: 为任务收集的输入数据。
        """
        if not dependencies:
            return {}
        elif len(dependencies) == 1:
            dep = dependencies[0]
            return self.task_results[dep]
        else:
            return {dep: self.task_results[dep] for dep in dependencies}

    def _find_executable_tasks(self, pending_tasks: set) -> List[str]:
        """
        查找可根据其依赖关系执行的任务。

        参数：
            pending_tasks (set)：待执行的任务集合。

        返回：
            List[str]：可执行的任务ID列表。
        """
        return [task_id for task_id in pending_tasks if self._can_execute(task_id)]


    def _can_execute(self, task_id: str) -> bool:
        """
        检查任务是否可根据其依赖项执行。

        参数：
            task_id (str): 待检查任务的ID。

        返回：
            bool: 若所有依赖条件均满足则返回True，否则返回False。
        """
        dependencies = self.tasks[task_id]['dependencies']
        return all(dep in self.task_results for dep in dependencies)

    def _load_dag(self) -> None:
        """
        从指定的YAML文件加载DAG定义。
        """
        with open(self.dag_file, 'r') as file:
            dag_data = yaml.safe_load(file)
            for task_data in dag_data.get('tasks', []):
                task_id = task_data['id']
                self.tasks[task_id] = task_data
                self.task_states[task_id] = 'pending'
                logger.info(f"任务 {task_id} 已加载: {task_data['description']}")


if __name__ == '__main__':
    coordinator = CoordinatorAgent(name="CoordinatorAgent", dag_file="data/dag.yml")
    message = Message(content='', sender="User", recipient="CoordinatorAgent")
    asyncio.run(coordinator.process(message))
