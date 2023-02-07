from random import sample
from time import time
from pydantic import BaseModel
from sqlmodel import Field, select
from ayaka import AyakaCat, load_data_from_file
from .bag import Money
from .utils import downloader, config,db

cat = AyakaCat("文字税",db=db)
cat.help = '''知识付费（doge

注意：只有买了文字的人之间才会相互交税，其他人不受影响'''

words: list[str] = []


@downloader.on_finish
async def finish():
    path = downloader.BASE_DIR / "文字税.txt"
    words.extend(load_data_from_file(path))


class UserWord(db.UserDBBase, table=True):
    __tablename__ = "word_tax"
    word: str = Field(primary_key=True)
    uname: str = ""
    time: int = 0

class GroupWord(db.GroupDBBase, table=True):
    __tablename__ = "word_tax_group"
    words: str = ""
    time: int = 0


def get_user_words(group_id: str):
    stmt = select(UserWord).filter_by(group_id=group_id)
    cursor = cat.db_session.exec(stmt)
    return cursor.all()


class GroupMarket(BaseModel):
    time: int = 0
    words: list[str] = []
    users: list[UserWord] = []
    first: bool = True

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.load(cat.group.id)

    def load(self, group_id):
        if self.first:
            self.first = False
            self.users = get_user_words(group_id)
            gw = GroupWord.get_or_create(group_id)
            self.time = gw.time
            self.words = [u for u in gw.words]

    def refresh(self, group_id):
        self.first = False
        self.time = int(time())
        self.words = sample(words, 20)
        gw = GroupWord.get_or_create(group_id)
        gw.words = "".join(self.words)
        gw.time = self.time

        for u in self.users:
            cat.db_session.delete(u)
        self.users = []

    def is_open(self):
        return int(time()) - self.time <= config.word_tax.open_duration

    def open_time_left(self):
        return max(0, config.word_tax.open_duration + self.time - int(time()))

    def is_valid(self):
        return int(time()) - self.time <= config.word_tax.valid_duration

    def buy(self, group_id, user_id, uname):
        us = [
            u for u in self.users
            if u.group_id == group_id and u.user_id == user_id
        ]
        for u in us:
            self.users.remove(u)
            cat.db_session.delete(u)

        words = sample(self.words, 3)
        us = [
            UserWord(
                group_id=group_id,
                user_id=user_id,
                word=word,
                time=self.time,
                uname=uname
            )
            for word in words
        ]
        for u in us:
            self.users.append(u)
            cat.db_session.add(u)
        return words

    def check(self, msg: str, user_id: int):
        check_dict: dict[str, list[UserWord]] = {}
        # 排除没抽的人
        for u in self.users:
            if u.user_id == user_id:
                break
        else:
            return {}

        for u in self.users:
            # # 不要排除自己
            # if u.user_id == user_id:
            #     continue
            if u.word not in check_dict:
                check_dict[u.word] = [u]
            else:
                check_dict[u.word].append(u)

        _check_dict: dict[str, list[UserWord]] = {}
        for m in msg:
            if m not in _check_dict and m in check_dict:
                _check_dict[m] = check_dict[m]
        return _check_dict

    def get_words(self, user_id: int):
        return [u.word for u in self.users if u.user_id == user_id]


@cat.on_cmd(cmds="文字市场")
async def open_word_market():
    '''查看文字市场'''
    market = cat.get_data(GroupMarket)
    info = "，".join(market.words)
    if market.is_open():
        dd = "开放"
    else:
        dd = "关闭"
    await cat.send(f"市场已{dd}，本轮文字池为\n{info}\n剩余持续时间{market.open_time_left()}s")


@cat.on_cmd(cmds=["开放文字市场", "刷新文字市场"])
async def open_word_market():
    '''刷新文字市场，开放福袋购买'''
    user = await cat.get_user(cat.user.id)
    if user.role not in ["owner", "admin"]:
        await cat.send("请联系管理员开放市场，您没有权限")
        return

    market = cat.get_data(GroupMarket)
    market.refresh(cat.group.id)
    info = "，".join(market.words)
    await cat.send(f"市场已开放，持续{config.word_tax.open_duration}s，本轮文字池为\n{info}")


@cat.on_cmd(cmds="购买文字")
async def buy_words():
    '''花费金钱购买一次福袋，获得3个随机文字'''
    market = cat.get_data(GroupMarket)
    if not market.is_open():
        await cat.send("市场未开放，请联系管理员开放市场后再购买")
    else:
        money = Money.get_or_create(cat.group.id, cat.user.id)
        money.money -= config.word_tax.buy_price
        words = market.buy(
            cat.group.id,
            cat.user.id,
            cat.user.name
        )
        info = "，".join(words)
        await cat.send(f"[{cat.user.name}] 花费{config.word_tax.buy_price}金，购买了文字 {info}")


@cat.on_cmd(cmds="我的文字")
async def my_words():
    '''查看自己的文字'''
    market = cat.get_data(GroupMarket)
    words = market.get_words(cat.user.id)
    info = "，".join(words)
    await cat.send(f"[{cat.user.name}]当前拥有 {info}")


@cat.on_cmd(cmds="所有文字")
async def all_words():
    '''查看所有人的文字'''
    market = cat.get_data(GroupMarket)
    if market.is_valid():
        data: dict[str, str] = {}
        for u in market.users:
            if u.uname not in data:
                data[u.uname] = ""
            data[u.uname] += u.word
        items = [f"[{k}] {v}" for k, v in data.items()]
        await cat.send_many(items)
    else:
        await cat.send("这一轮文字税尚未开始")


@cat.on_text()
async def get_tax():
    '''计算税收'''
    market = cat.get_data(GroupMarket)
    if market.is_open():
        return

    if not market.is_valid():
        return

    msg = cat.arg
    check_dict = market.check(msg, cat.user.id)
    if not check_dict:
        return

    user_moneys: dict[int, Money] = {}
    for users in check_dict.values():
        for u in users:
            if u.user_id not in user_moneys:
                user_moneys[u.user_id] = Money.get_or_create(u.group_id, u.user_id)
    user_moneys[cat.user.id] = Money.get_or_create(cat.group.id, cat.user.id)

    for w in check_dict.keys():
        msg = msg.replace(w, f"[{w}]")
    infos = [msg]

    for w, users in check_dict.items():
        t = int(config.word_tax.tax / len(users))
        tt = t*len(users)
        user_moneys[cat.user.id].money -= tt
        for u in users:
            user_moneys[u.user_id].money += t
        names = [u.uname for u in users]
        if names == [cat.user.name]:
            continue
        if cat.user.name in names:
            tt -= t
        infos.append(f"[{w}] 所有者：{names}，您为此字付费{tt}金")

    if config.word_tax.tax_notice:
        if len(infos) > 1:
            await cat.send_many(infos)
