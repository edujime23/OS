import asyncio
import concurrent.futures
import threading
from typing import Any, Awaitable, Callable, Iterable, Mapping, Type, Union


class Class:
    ...

class AsyncManager:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        self._threads = []
        self._tasks = []

    def __del__(self):
        self.close()

    def close(self):
        self._loop.close()

    def new_thread(
        self, func: Union[Callable[..., Any], Type[Class]], args: Iterable = None, kwargs: Mapping = None
    ) -> threading.Thread:
        """
        Creates a new thread and returns the thread class.
        """
        thread = threading.Thread(
            target=func if func is Callable[..., Any] else func.__call__,
            args=args or (),
            kwargs=kwargs or {},
            name=func.__name__
            if func is Callable[..., Any]
            else func.__call__.__name__,
        )
        self._threads.append(thread)
        return thread

    async def new_task(self, func: Union[Callable[..., Awaitable[Any]], Type[Class]]) -> Awaitable:
        """
        Runs the function in a new task and returns the task object.

        The function must be an awaitable and be already initialized.
        """
        task = asyncio.ensure_future(func if func is Callable[..., Awaitable[Any]] else func.__call__(), loop=self._loop)
        self._tasks.append(task)
        return task
    
    def run(self, func: Union[Callable[..., Awaitable[Any]], Type[Class]]) -> Any:
        """
        Runs the function in the async loop and returns the result.

        The function must be an awaitable and be already initialized.
        """
        try:
            return self._loop.run_until_complete(
                self.new_task(func)
            )
        finally:
            self.close()
        
    async def run_async(self, func: Union[Callable[..., Awaitable[Any]], Type[Class]]) -> Any:
        """
        Runs the function in the async loop and returns the result.

        The function must be an awaitable and be already initialized.
        """
        return await asyncio.wrap_future(
            self._loop.run_in_executor(self._executor, lambda: func()), loop=self._loop
        )

    async def run_multiple_async(self, funcs: Iterable[Callable[..., Awaitable[Any]]]) -> Iterable[Any]:
        """
        Runs multiple functions concurrently in the async loop and returns their results.

        The functions must be awaitable and be already initialized.
        """
        tasks = [self.new_task(func) for func in funcs]
        results = await asyncio.gather(*tasks, loop=self._loop, return_exceptions=True)
        self._tasks.extend(tasks)
        return results

    def close_threads(self):
        """
        Joins all threads that were created using `new_thread`.
        """
        for thread in self._threads:
            thread.join()

        self._threads.clear()

    def cancel_tasks(self):
        """
        Cancels all tasks that were created using `new_task`.
        """
        for task in self._tasks:
            task.cancel()

        self._tasks.clear()
