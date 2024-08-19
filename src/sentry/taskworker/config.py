from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import uuid4
import time

from arroyo.backends.kafka import KafkaPayload, KafkaProducer
from arroyo.types import Topic as ArroyoTopic

from sentry.conf.types.kafka_definition import Topic
from sentry.taskworker.task import Task
from sentry.utils import json
from sentry.utils.kafka_config import get_kafka_producer_cluster_options, get_topic_definition


class TaskNamespace:
    """
    Task namespaces link topics, config and default retry mechanics together
    All tasks within a namespace are stored in the same topic and run by shared
    worker pool.
    """

    __registered_tasks: dict[str, Task]
    __producer: KafkaProducer | None = None

    def __init__(self, name: str, topic: str, deadletter_topic: str, retry: Any):
        self.name = name
        self.topic = topic
        self.deadletter_topic = deadletter_topic
        self.default_retry = retry
        self.__registered_tasks = {}

    @property
    def producer(self) -> KafkaProducer:
        if self.__producer:
            return self.__producer
        cluster_name = get_topic_definition(Topic.HACKWEEK)["cluster"]
        producer_config = get_kafka_producer_cluster_options(cluster_name)
        self.__producer = KafkaProducer(producer_config)

        return self.__producer

    def register(self, name: str):
        """register a task, used as a decorator"""

        def wrapped(func):
            task = Task(name=name, func=func, namespace=self)
            self.__registered_tasks[name] = task
            return task

        return wrapped

    def send_task(self, task: Task, args, kwargs) -> None:
        task_message = self._serialize_task_call(task, args, kwargs)
        # TODO this could use an RPC instead of appending to the topic directly
        self.producer.produce(
            ArroyoTopic(name=self.topic),
            KafkaPayload(key=None, value=task_message.encode("utf-8"), headers=[]),
        )

    def _serialize_task_call(self, task: Task, args: list[Any], kwargs: Mapping[Any, Any]) -> str:
        task_payload = {
            "id": uuid4().hex,
            "namespace": self.name,
            "taskname": task.name,
            "parameters": {"args": args, "kwargs": kwargs},
            "received_at": time.time(),
            # TODO headers, retry_state and retries in general
            "headers": {},
            "retry_state": None,
        }
        return json.dumps(task_payload)


class TaskRegistry:
    """Registry of all namespaces"""

    __namespaces: dict[str, TaskNamespace]

    def __init__(self):
        self.__namespaces = {}

    def create_namespace(self, name: str, topic: str, deadletter_topic: str, retry: Any):
        # TODO So much
        # - validate topic names
        # - validate deadletter topic
        # - do topic : cluster resolution
        namespace = TaskNamespace(
            name=name, topic=topic, deadletter_topic=deadletter_topic, retry=retry
        )
        self.__namespaces[name] = namespace

        return namespace


taskregistry = TaskRegistry()
