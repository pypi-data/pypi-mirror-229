from typing import Union, Any
from collections.abc import Callable, Awaitable
import asyncio
import threading
import importlib
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from navconfig.logging import logging
from .events import AbstractEvent


class EventManager:
    """
    Basic Event Manager of flowtask.
    """

    def __init__(self, name: str = None):
        self._handlers: list[Callable] = []
        self._name = name  # event name

    def dispatch(self, event_name: str, *args, **kwargs):
        event = getattr(self, event_name, None)
        if event is None:
            raise ValueError(
                f"No event named '{event_name}' found."
            )
        try:
            event(*args, **kwargs)
        except Exception as e:
            event.logger.error(
                f'Event Error: {e}'
            )

    class Event:
        def __init__(self, functions: list[Callable]) -> None:
            if not isinstance(functions, list):
                raise TypeError(
                    'Event Function Callable need to be a List'
                )
            self._handlers = functions
            self.logger = logging.getLogger('Flowtask.Event')
            self._event = threading.Event()
            self._lock = threading.Lock()
            self._executor = ThreadPoolExecutor(max_workers=20)

        def add(self, func: Union[Callable, Awaitable]) -> Any:
            with self._lock:
                self._handlers.append(func)
            return self

        def close(self):
            try:
                self._executor.shutdown()
            except Exception:
                pass

        def __iadd__(self, func: Union[Callable, Awaitable]) -> Any:
            with self._lock:
                self._handlers.append(func)
            return self

        def __isub__(self, func: Union[Callable, Awaitable]):
            with self._lock:
                self._handlers.remove(func)
            return self

        def __call__(self, *args, **kwargs):
            self._event.set()
            # creating the executor
            fn = partial(
                self._executeEvent,
                handlers=self._handlers,
                *args, **kwargs
            )
            # sending function coroutine to a thread
            self._executor.submit(fn)

        def _executeEvent(self, handlers: list[Callable], *args, **kwargs):
            """
            executeEvent.

            Executing Event Functions associated with an event dispatched from Flowtask.
            """
            self._event.wait()
            for fn in handlers:
                if asyncio.iscoroutinefunction(fn) or isinstance(fn, AbstractEvent):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(fn(*args, event_loop=loop, **kwargs))
                        finally:
                            tasks = asyncio.all_tasks(loop)
                            for task in tasks:
                                try:
                                    task.cancel()
                                    # await task
                                except asyncio.CancelledError:
                                    pass
                            loop.close()
                    except Exception as err:
                        raise RuntimeError(
                            f"Event Error: {err!s}"
                        ) from err
                else:
                    try:
                        fn(*args, **kwargs)
                    except Exception as err:
                        self.logger.exception(err)
                        raise RuntimeError(
                            f"Event Error: {err!s}"
                        ) from err

    @classmethod
    def addEvent(cls, **kwargs):
        """
        addEvent( event1 = [f1,f2,...], event2 = [g1,g2,...], ... )
        creates events using **kwargs to create any number of events.
        Each event recieves a list of functions,
        where every function in the list recieves the same parameters.
        Example:
        def hello(): print("Hello ")
        def world(): print("World")

        EventManager.addEvent( salute = [hello] )
        EventManager.salute += world

        EventManager.salute()

        Output:
        Hello
        World
        """
        evt = {}
        for key, value in kwargs.items():
            if not isinstance(value, list):
                fn = [value]
            else:
                fn = value
            evt[key] = cls.Event(fn)
            setattr(cls, key, evt[key])
        return evt

    def LoadEvent(self) -> list[Callable]:
        fns = []
        for fn in self._success_callbacks:
            try:
                pkg, module = fn.rsplit(".", 1)
                mod = importlib.import_module(pkg)
                obj = getattr(mod, module)
                fns.append(obj)
            except ImportError as e:
                raise RuntimeError(
                    f"Auth Callback: Error getting Callback Function: {fn}, {e!s}"
                ) from e
        self._callbacks = fns
