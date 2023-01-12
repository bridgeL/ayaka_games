from random import sample
from time import time
from pydantic import BaseModel, Field
from ayaka import AyakaCat, AyakaUserDB, AyakaGroupDB, AyakaDB, load_data_from_file
from .bag import get_money, Money
from .data import downloader, config

cat = AyakaCat("文字税")
cat.help = '''知识付费（doge

注意：只有买了文字的人之间才会相互交税，其他人不受影响'''

words: list[str] = []


@downloader.on_finish
async def finish():
    path = downloader.BASE_DIR / "文字税.txt"
    words.extend(load_data_from_file(path))


class UserWord(AyakaUserDB):
    __table_name__ = "word_tax"
    word: str = Field(extra=AyakaDB.__primary_key__)
    uname: str = ""
    time: int = 0


class GroupWord(AyakaGroupDB):
    __table_name__ = "word_tax_group"
    words: str = ""
    time: int = 0


class GroupMarket(BaseModel):
    time: int = 0
    words: list[str] = []
    users: list[UserWord] = []
    first: bool = True

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.load(cat.current.session_id)

    def load(self, group_id):
        if self.first:
            self.first = False
            self.users = UserWord.select_many(group_id=group_id)
            gw = GroupWord.select_one(group_id=group_id)
            self.time = gw.time
            self.words = [u for u in gw.words]

    def refresh(self, group_id):
        self.first = False
        self.time = int(time())
        self.words = sample(words, 20)
        gw = GroupWord.select_one(group_id=group_id)
        gw.words = "".join(self.words)
        gw.time = self.time
        self.users = []
        UserWord.delete(
            group_id=group_id
        )

    def is_open(self):
        return int(time()) - self.time <= config.word_tax.open_duration

    def open_time_left(self):
        return max(0, config.word_tax.open_duration + self.time - int(time()))

    def is_valid(self):
        return int(time()) - self.time <= config.word_tax.valid_duration

    def buy(self, group_id, user_id, uname):
        UserWord.delete(
            group_id=group_id,
            user_id=user_id,
        )
        self.users = [
            u for u in self.users
            if u.group_id != group_id or u.user_id != user_id
        ]
        words = sample(self.words, 3)
        users = [
            UserWord(
                group_id=group_id,
                user_id=user_id,
                word=word,
                time=self.time,
                uname=uname
            )
            for word in words
        ]
        UserWord.insert_many(users)
        self.users.extend(users)
        return words

    def check(self, msg: str, user_id: int):
        check_dict: dict[str, list[UserWord]] = {}
        for u in self.users:
            if u.user_id == user_id:
                break
        else:
            # 排除没抽的人
            return {}

        for u in self.users:
            if u.user_id == user_id:
                continue
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
    user = await cat.get_user(cat.current.sender_id)
    if user.role not in ["owner", "admin"]:
        await cat.send("请联系管理员开放市场，您没有权限")
        return

    market = cat.get_data(GroupMarket)
    market.refresh(cat.current.session_id)
    info = "，".join(market.words)
    await cat.send(f"市场已开放，持续{config.word_tax.open_duration}s，本轮文字池为\n{info}")


@cat.on_cmd(cmds="购买文字")
async def buy_words():
    '''花费金钱购买一次福袋，获得3个随机文字'''
    market = cat.get_data(GroupMarket)
    if not market.is_open():
        await cat.send("市场未开放，请联系管理员开放市场后再购买")
    else:
        money = get_money(cat.current.session_id, cat.current.sender_id)
        money.value -= config.word_tax.buy_price
        words = market.buy(
            cat.current.session_id, cat.current.sender_id, cat.current.sender_name)
        info = "，".join(words)
        await cat.send(f"[{cat.current.sender_name}] 花费{config.word_tax.buy_price}金，购买了文字 {info}")


@cat.on_cmd(cmds="我的文字")
async def buy_words():
    '''查看自己的文字'''
    market = cat.get_data(GroupMarket)
    words = market.get_words(cat.current.sender_id)
    info = "，".join(words)
    await cat.send(f"[{cat.current.sender_name}]当前拥有 {info}")


@cat.on_cmd(cmds="所有文字")
async def buy_words():
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

    msg = cat.current.arg
    check_dict = market.check(msg, cat.current.sender_id)
    if not check_dict:
        return

    user_moneys: dict[int, Money] = {}
    for users in check_dict.values():
        for u in users:
            if u.user_id not in user_moneys:
                user_moneys[u.user_id] = get_money(u.group_id, u.user_id)
    user_moneys[cat.current.sender_id] = get_money(
        cat.current.session_id, cat.current.sender_id)

    for w in check_dict.keys():
        msg = msg.replace(w, f"[{w}]")
    infos = [msg]

    for w, users in check_dict.items():
        t = int(config.word_tax.tax / len(users))
        tt = t*len(users)
        user_moneys[cat.current.sender_id].value -= tt
        for u in users:
            user_moneys[u.user_id].value += t
        names = [u.uname for u in users]
        infos.append(f"[{w}] 所有者：{names}，您为此字付费{tt}金")

    if config.word_tax.tax_notice:
        await cat.send_many(infos)
