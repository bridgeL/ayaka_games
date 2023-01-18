'''
    原神随机事件
'''
from random import choice
from typing import Literal
from pydantic import BaseModel
from ayaka import AyakaCat, load_data_from_file
from .utils import downloader

cat = AyakaCat("原神随机事件")


class Group(BaseModel):
    type: Literal["Group"] = "Group"
    rules: list[str]
    parts: list["Part"]

    def get_value(self, rule: str = None, data: dict = None):
        params = {k: p.choice() for p in self.parts for k in p.names}

        # 内部参数 + 外部参数
        if data:
            params.update(data)

        # 内部规则 or 外部规则
        if not rule:
            if not self.rules:
                return ""
            rule = choice(self.rules)

        return rule.format(**params)


class Part(BaseModel):
    type: Literal["Part"] = "Part"
    names: list[str]
    values: list[str | Group]

    def choice(self):
        if not self.values:
            return ""
        value = choice(self.values)
        if isinstance(value, Group):
            return value.get_value()
        return value


# 很重要
Group.update_forward_refs()

'''
简单介绍原理：
1.每个句子都可以视为一个Group
2.Group由多个Part、以自定义的rule拼接而成，而每个Part都有自己的名字，通过名字来确定他们在拼接规则中的位置，例如rule = {名字}在{地点}做{动作}
3.rule可以有多个，Group随机选择一个rule进行拼接
4.Part内存有一个数据元素池，Part随机从数据元素池中抽取一个元素作为值
5.Part的数据元素池中的元素，可以是字符串，也可以是Group
6.开始套娃
'''

group = Group(rules=[], parts=[])


@downloader.on_finish
async def load():
    global group
    path = downloader.BASE_DIR / "原神随机事件.json"
    data = load_data_from_file(path)
    group = Group(**data)


@cat.on_cmd(cmds="原神随机事件")
async def _():
    '''带参数可以自定义事件，例如：原神随机事件 喝水'''
    event = str(cat.arg)
    if event:
        await cat.send(group.get_value(data={"事件": event}))
    else:
        await cat.send(group.get_value())
