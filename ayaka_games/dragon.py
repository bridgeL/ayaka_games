'''
    接龙，多个词库可选择
'''
import re
from random import choice
from pypinyin import lazy_pinyin
from pydantic import BaseModel
from sqlmodel import Field, select, desc
from ayaka import AyakaCat, load_data_from_file, UserDBBase
from .bag import Money
from .utils import downloader, config

cat = AyakaCat("接龙管理")
cat.help = '''接龙，在聊天时静默运行'''


class Dragon(BaseModel):
    '''接龙词库'''
    name: str
    use: bool = True
    words: list[str] = []
    pinyin_dict: dict[str, list] = {}

    def __init__(self, **data) -> None:
        super().__init__(**data)

        if not self.pinyin_dict:
            self.get_dict()

    def get_dict(self):
        for word in self.words:
            # 获取首字的拼音
            p = lazy_pinyin(word)[0]
            if p not in self.pinyin_dict:
                self.pinyin_dict[p] = []
            self.pinyin_dict[p].append(word)

    def check(self, word: str):
        return word in self.words

    def next(self, word: str):
        # 获取末字的拼音
        p = lazy_pinyin(word)[-1]
        words: list[str] = self.pinyin_dict.get(p)
        if not words:
            return ""
        return choice(words)


class DragonUserData(UserDBBase, table=True):
    '''用户数据'''
    __tablename__ = "dragon_user_data"
    dragon_name: str = Field(primary_key=True)
    cnt: int = 0

    @classmethod
    def get_or_create(cls, dragon_name: str):
        return cls._get_or_create(
            dragon_name=dragon_name,
            group_id=cat.group.id,
            user_id=cat.user.id
        )


dragon_list: list[Dragon] = []


@downloader.on_finish
async def finish():
    path = downloader.BASE_DIR / "接龙"
    for p in path.iterdir():
        try:
            words = load_data_from_file(p)
            dragon_list.append(Dragon(name=p.stem, words=words))
        except:
            pass


zh = re.compile(r"[\u4e00-\u9fff]+")


@cat.on_text(states=["", "idle"])
async def handle():
    '''自动接龙'''
    text = cat.arg
    r = zh.search(text)
    if not r:
        return

    word = r.group()

    for dragon in dragon_list:
        # 跳过不启用的接龙
        if not dragon.use:
            continue

        # 当前词语符合接龙词库
        if dragon.check(word):

            # 上次接龙
            last = cat.cache.get("dragon", {}).get(dragon.name, "")

            # 成功接龙
            if last and word:
                p1 = lazy_pinyin(last)[-1]
                p2 = lazy_pinyin(word)[0]
                if p1 == p2:
                    # 修改金钱
                    usermoney = Money.get_or_create(cat.group.id,cat.user.id)
                    usermoney.money += config.dragon_reward
                    await cat.send(f"[{cat.user.name}] 接龙成功！奖励{config.dragon_reward}金")

                    # 修改记录
                    user_data = DragonUserData.get_or_create(dragon.name)
                    user_data.cnt += 1

            # 无论是否成功接龙都发送下一个词
            word = dragon.next(word)
            cat.cache.setdefault("dragon", {})
            cat.cache["dragon"][dragon.name] = word
            if not word:
                word = choice(["%$#*-_", "你赢了", "接不上来..."])
            await cat.send(word)
            break


cat.set_wakeup_cmds(cmds="接龙管理")
cat.set_rest_cmds(cmds=["exit", "退出"])


@cat.on_cmd(cmds="list", states="idle")
async def list_all():
    '''列出所有词库'''
    items = ["所有词库："]
    for dragon in dragon_list:
        if dragon.use:
            items.append(f"[{dragon.name}] 正在使用")
        else:
            items.append(f"[{dragon.name}]")
    await cat.send("\n".join(items))


@cat.on_cmd(cmds="data", states="idle")
async def show_data():
    '''展示你的答题数据'''
    gid = cat.group.id
    uid = cat.user.id

    stmt = select(DragonUserData).filter_by(group_id=gid, user_id=uid)
    results = cat.db_session.exec(stmt)
    user_datas = results.all()

    if user_datas:
        info = "\n".join(
            f"[{u.dragon_name}] 接龙次数 {u.cnt}"
            for u in user_datas
        )
    else:
        info = "你还没有用过我...T_T"

    await cat.send(info)


@cat.on_cmd(cmds="rank", states="idle")
async def show_rank():
    '''展示排行榜'''
    data: dict[str, list[DragonUserData]] = {}

    # SELECT * from dragon_user_data ORDER BY dragon_name, cnt DESC
    stmt = select(DragonUserData).filter_by(group_id=cat.group.id).order_by(
        DragonUserData.dragon_name, desc(DragonUserData.cnt))
    results = cat.db_session.exec(stmt)
    for r in results:
        if r.dragon_name not in data:
            data[r.dragon_name] = []
        data[r.dragon_name].append(r)

    users = await cat.get_users()
    users = {u.id: u.name for u in users}

    info = "排行榜\n"
    for dragon_name, datas in data.items():
        info += f"\n[{dragon_name}]\n"
        if not datas:
            info += f"  - 暂时没人使用过...T_T\n"
        else:
            datas.sort(key=lambda x: x.cnt, reverse=1)
            for d in datas[:5]:
                info += f"  - [{users[d.user_id]}] 接龙次数 {d.cnt}\n"

    await cat.send(info.strip())
