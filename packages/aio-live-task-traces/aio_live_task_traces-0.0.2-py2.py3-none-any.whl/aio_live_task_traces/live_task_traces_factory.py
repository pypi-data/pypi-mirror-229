import asyncio
import traceback
from asyncio import Task


class LiveTaskTracesFactory:
    def __init__(self) -> None:
        self.original_factory = None

    def __call__(self, loop, coro, context=None):
        return self._create_original_task(loop, self._wrap_coroutine(coro), context)

    @staticmethod
    async def _wrap_coroutine(coro):
        try:
            await coro
        except Exception as e:
            traceback.print_exception(e)
            raise

    def _create_original_task(self, loop, coro, context=None):
        if self.original_factory is None:
            task = Task(coro, loop=loop, context=context)
            if task._source_traceback:
                del task._source_traceback[-1]
        else:
            if context is None:
                # Use legacy API if context is not needed
                task = self.original_factory(self, coro)
            else:
                task = self.original_factory(self, coro, context=context)
        return task


live_task_traces_factory = LiveTaskTracesFactory()


def set_live_task_traces(on: bool):
    if on:
        live_task_traces_factory.original_factory = asyncio.get_running_loop().get_task_factory()
        asyncio.get_running_loop().set_task_factory(live_task_traces_factory)
    else:
        asyncio.get_running_loop().set_task_factory(live_task_traces_factory.original_factory)
