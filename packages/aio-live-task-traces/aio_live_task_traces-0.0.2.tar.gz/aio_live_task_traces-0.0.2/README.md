[![Python application](https://github.com/matan1008/aio-live-task-traces/workflows/Python%20application/badge.svg)](https://github.com/matan1008/aio-live-task-traces/actions/workflows/python-app.yml "Python application action")
[![Pypi version](https://img.shields.io/pypi/v/aio-live-task-traces.svg)](https://pypi.org/project/aio-live-task-traces/ "PyPi package")
[![Downloads](https://static.pepy.tech/personalized-badge/aio-live-task-traces?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads)](https://pepy.tech/project/aio-live-task-traces)
[![codecov](https://codecov.io/gh/matan1008/aio-live-task-traces/branch/master/graph/badge.svg?token=GL0FZD9SVG)](https://codecov.io/gh/matan1008/aio-live-task-traces)


# aio-live-tasks-exceptions
Trace python asyncio tasks exceptions live!

# Installation

Install the last released version using `pip`:

```shell
python3 -m pip install -U aio-live-task-traces
```

Or install the latest version from sources:

```shell
git clone git@github.com:matan1008/aio-live-task-traces.git
cd aio-live-task-traces
python3 -m pip install -U -e .
```

# Usage

Usually, if you run a task that throws exception using asyncio you will not be aware
of the exception until the task is awaited or deleted. For example:


```python
import asyncio


async def faulty_task():
    raise Exception('foo')


async def main():
    task = asyncio.create_task(faulty_task())
    await asyncio.sleep(3600)
    await task

    
if __name__ == '__main__':
    # The exception will be printed after 3600 seconds
    asyncio.run(main())
```

This package, will wrap each task you run so the exception will be traced
the moment it raises:

```python
import asyncio
from aio_live_task_traces import set_live_task_traces


async def faulty_task():
    raise Exception('foo')


async def main():
    set_live_task_traces(True)
    task = asyncio.create_task(faulty_task())
    await asyncio.sleep(3600)
    await task

    
if __name__ == '__main__':
    # The exception will be printed both immediately and after 3600 seconds
    asyncio.run(main())
```
