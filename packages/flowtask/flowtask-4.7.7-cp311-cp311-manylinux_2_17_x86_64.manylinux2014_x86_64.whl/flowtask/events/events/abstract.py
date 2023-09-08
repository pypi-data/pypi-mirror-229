from abc import ABC, abstractmethod
import asyncio
from flowtask.utils import cPrint

class AbstractEvent(ABC):
    def __init__(self, *args, **kwargs):
        self.disable_notification: bool = kwargs.pop('disable_notification', False)
        self._loop = kwargs.pop('event_loop', asyncio.get_event_loop())
        self._task = kwargs.pop('task', None)
        self._args = args
        self._kwargs = kwargs

    @abstractmethod
    async def __call__(self):
        """Called when event is dispatched.
        """

    def echo(self, message: str, level: str = 'INFO'):
        cPrint(message, level=level)

class DummyEvent(AbstractEvent):
    async def __call__(self):
        cPrint(' == Task Executed === ', level="INFO")
