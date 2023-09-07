import asyncio
import inspect
from functools import partial, wraps

# RuntimeError: This event loop is already running， so apply patch
import nest_asyncio

from ._version import __version__

nest_asyncio.apply()


def to_async(f):
    """sync to async"""

    @wraps(f)
    async def decorated(*args, **kwargs):
        if inspect.iscoroutinefunction(f):
            # call directly
            return await f(*args, **kwargs)

        # no get_running_loop in python 3.6, have to copy that
        loop = asyncio._get_running_loop()
        if loop is None:
            raise RuntimeError('no running event loop')

        return await loop.run_in_executor(None, partial(f, *args, **kwargs))

    return decorated


def to_sync(f):
    """async to sync"""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not inspect.iscoroutinefunction(f):
            # call directly
            return f(*args, **kwargs)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # RuntimeError: There is no current event loop in thread 'ThreadPoolExecutor-0_0'.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # RuntimeError: This event loop is already running
        return loop.run_until_complete(f(*args, **kwargs))

    return decorated
