from pydantic import BaseModel
from ayaka import AyakaConfig


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
