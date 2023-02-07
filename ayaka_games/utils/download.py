import json
import asyncio
from typing import Awaitable, Callable
from pathlib import Path
from loguru import logger
from ayaka import ResInfo, resource_download_by_res_info, resource_download, get_adapter
from .config import config


AUTHOR = "bridgeL"
REPO = "ayaka_games"
BRANCH = "master"


class Downloader:
    RESINFO_URL = f"https://ghproxy.com/https://raw.githubusercontent.com/{AUTHOR}/{REPO}/{BRANCH}/res_info.json"
    '''资源信息下载地址'''

    BASE_DIR = Path("data", "ayaka_games")
    '''本地文件地址'''

    def __init__(self) -> None:
        self.funcs: list[Callable[[], Awaitable]] = []

    async def download_data(self):
        '''更新数据'''
        logger.info("检查资源文件...")

        if config.auto_update:
            try:
                data = await resource_download(self.RESINFO_URL)
            except:
                logger.warning("目前无法获取资源目录，这意味资源数据无法同步为最新版本，尽管如此，仍可加载本地的资源文件")
            else:
                data = json.loads(data)
                res_info = ResInfo(**data)
                await resource_download_by_res_info(res_info, self.BASE_DIR)

        ts = [asyncio.create_task(func()) for func in self.funcs]
        await asyncio.gather(*ts)

        logger.info("资源文件准备完毕")

    def on_finish(self, func: Callable[[], Awaitable]):
        '''检查文件更新结束后执行的异步回调'''
        self.funcs.append(func)
        return func


downloader = Downloader()


async def download():
    '''检查资源更新'''
    asyncio.create_task(downloader.download_data())

get_adapter().on_startup(download)
