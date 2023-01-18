import json
import asyncio
from typing import Awaitable, Callable, TypeVar
from sqlmodel import Session, SQLModel, select
from pathlib import Path
from pydantic import BaseModel
from loguru import logger
from ayaka import resource_download_by_res_info, ResInfo, resource_download, AyakaConfig, bridge


class WordTaxConfig(BaseModel):
    tax: int = 100
    buy_price: int = 1000
    open_duration: int = 300
    valid_duration: int = 86400
    tax_notice: bool = True


class PrayConfigItem(BaseModel):
    reward: int = 0
    weight: int = 0


class Config(AyakaConfig):
    __config_name__ = "ayaka_game"
    auto_update: bool = True
    calculate_reward: int = 1000
    checkin_reward: int = 10000
    dragon_reward: int = 1000
    word_tax: WordTaxConfig = WordTaxConfig()
    pray: list[PrayConfigItem] = [
        PrayConfigItem(reward=66, weight=10),
        PrayConfigItem(reward=666, weight=50),
        PrayConfigItem(reward=6666, weight=30),
        PrayConfigItem(reward=66666, weight=5),
        PrayConfigItem(reward=-66666, weight=5),
    ]


config = Config()
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


@bridge.on_startup
async def download():
    '''检查资源更新'''
    asyncio.create_task(downloader.download_data())

T = TypeVar("T", bound=SQLModel)


def get_or_create(session: Session, model: type[T], **kwargs) -> T:
    statement = select(model).filter_by(**kwargs)
    results = session.exec(statement)
    instance = results.one_or_none()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
    return instance
