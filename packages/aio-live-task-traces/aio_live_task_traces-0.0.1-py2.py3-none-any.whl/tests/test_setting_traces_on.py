import asyncio

import pytest

from aio_live_task_traces import set_live_task_traces


async def faulty_task():
    raise Exception('foo')


@pytest.mark.asyncio
async def test_sanity(capsys):
    set_live_task_traces(True)

    task = asyncio.create_task(faulty_task())
    await asyncio.sleep(0)

    captured = capsys.readouterr()
    assert 'Exception: foo' in captured.err

    with pytest.raises(Exception):
        await task
