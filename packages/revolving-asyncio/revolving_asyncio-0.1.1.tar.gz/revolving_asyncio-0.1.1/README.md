# revolving_asyncio
同步异步互转工具

1. 本项目依赖于[nest_asyncio](https://github.com/erdewit/nest_asyncio) 在嵌套场景下，需要对`asyncio`打补丁
2. 本项目提取于[ksrpc](https://github.com/wukan1986/ksrpc) 中的同步异步任意转换功能

## Installation安装
```commandline
pip install revolving_asyncio -U
```

## Usage使用
See more [examples](examples)
```python
import asyncio
import time

from revolving_asyncio import to_async, to_sync

if __name__ == '__main__':
    @to_async
    def do_sync_work(name: str):
        time.sleep(5)
        print(f"sync function, to async by decorator, {name}")


    async def do_async_work(name: str):
        await asyncio.sleep(5)
        print(f"async function, to sync by wrapper, {name}")


    async def async_main():
        # Method 1
        await do_sync_work(name="Method 1")


    def sync_main():
        # Method 2
        to_sync(do_async_work)(name="Method 2")


    asyncio.run(async_main())
    sync_main()

```

## Exception 异常
如果直接使用使用`to_async`和`to_sync`报`RuntimeError: This event loop is already running`等一类的异常，可以在之前添加以下代码试试
```python
import revolving_asyncio
revolving_asyncio.apply()
```