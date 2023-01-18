from asyncio import sleep
from random import randint
from sqlmodel import SQLModel, Field
from ayaka import AyakaCat, get_session
from .bag import get_money
from .utils import get_or_create

god_names = ['欢愉', '悼亡', '深渊', '智慧']

cat = AyakaCat('mana')
cat.help = '''
===== m a n a =====
欢愉、悼亡、深渊、智慧
===== ======= =====
'''


class ManaGod(SQLModel, table=True):
    __tablename__ = "mana_god"
    group_id: str = Field(primary_key=True)
    name: str = "欢愉"
    power: int = 1
    cnt: int = 0
    mana: int = 0

    def say(self):
        words = {
            '欢愉': ['命途对你报之一笑', '命途轻咬你的耳根', '命途正引诱你堕入其中'],
            '悼亡': ['命途中，亡魂在悲叹', '命途中充斥着悲伤', '命途默然无声地崩解着'],
            '深渊': ['命途静静凝视着你'],
            '智慧': ['命途终极的智慧，令你感到畏惧', '命途看穿了你的企图', '命途对你的愚蠢感到无趣'],
        }

        cs = {
            '欢愉': '♥',
            '悼亡': '♠',
            '深渊': '♣',
            '智慧': '♦',
        }

        # ps = ['魔法师','女祭司','皇后','皇帝','教皇','恋人','战车','力量','隐士','命运之轮','正义','倒吊人','死神']

        rs = words[self.name]
        r = rs[randint(0, len(rs)-1)]
        c = cs[self.name]
        return f"{r} {c} {self.power}"


def get_mana_god(session, group_id: str):
    return get_or_create(session, ManaGod, group_id=group_id)


class UserMana(SQLModel, table=True):
    __tablename__ = "user_mana"
    group_id: str = Field(primary_key=True)
    user_id: str = Field(primary_key=True)
    mana: int = 10


def get_user_mana(session, group_id: str, user_id: str):
    return get_or_create(
        session, UserMana,
        group_id=group_id,
        user_id=user_id
    )


def change_god(god_name: str, god: ManaGod):
    god.name = god_name
    god.power = randint(1, 13)
    god.cnt = 0
    god.mana = 0


def happy(god: ManaGod, mana: int):
    if mana < -100:
        change_god(god_names[randint(0, 3)], god)
        return mana*2, "命途为你的愚行而惊讶"

    power = god.power

    god.mana += abs(mana)
    if god.mana >= 8:
        god.power += int(god.mana/8)
        god.mana = 0

    god.cnt += 1
    if god.cnt >= 3:
        god.power += 1
        god.cnt = 0

    if god.power > 13:
        change_god(god_names[randint(0, 3)], god)

    if power <= 3:
        return 0, "命途对你毫无兴趣"
    if power <= 6:
        return 2*(power-3), "命途微微舒展身姿"
    if power <= 10:
        return mana*(1+(power-6)/5), "命途对你兴趣颇丰"
    return mana*(power-9), "命途向你展示了星空的无限隐秘"


def sorrow(god: ManaGod, mana: int):
    if mana < -100:
        change_god(god_names[randint(0, 3)], god)
        return mana*2, "命途为你的愚行而哀伤"

    power = god.power

    god.mana += abs(mana)
    if god.mana >= power:
        god.power += int(god.mana/power)
        god.mana = 0

    god.cnt += 1
    if god.cnt >= 10:
        god.power += 1
        god.cnt = 0

    if god.power > 13:
        change_god(god_names[randint(0, 3)], god)

    if power <= 5:
        return mana, "命途对你悲叹"
    if power <= 10:
        return mana + power - 5, "命途对你怜悯"
    return - power, "命途对你哀悼"


def abyss(god: ManaGod, mana: int):
    if mana < -100:
        change_god(god_names[randint(0, 3)], god)
        return mana*2, "命途为你的愚行而喜悦"

    power = god.power

    if mana % 3 == 2:
        god.power -= 1
    else:
        god.power += abs(mana) % 3

    god.cnt += 1
    if god.cnt >= 12:
        change_god(god_names[randint(0, 3)], god)

    if god.power > 13:
        change_god('欢愉', god)

    if god.power <= 0:
        change_god('悼亡', god)

    if power % 3 == 0 and randint(0, 2):
        return mana * power / 3, "当你理解了命途，你也就成为了命途"
    return mana * (1 - power/6), "命途贪婪的吞噬了一切"


def wise(god: ManaGod, mana: int):
    if mana < -100:
        change_god(god_names[randint(0, 3)], god)
        return mana*2, "..."

    power = god.power
    reward = int(god.mana / 3)

    god.mana += abs(mana)*2 - reward
    if power <= 7:
        god.mana += power*3
    else:
        god.mana += (14 - power)*3

    god.power = int(god.mana / 3) + 1

    god.cnt += 1
    if god.cnt >= 12:
        change_god(god_names[randint(0, 3)], god)

    if god.power > 13 or god.power <= 0:
        change_god(god_names[randint(0, 3)], god)

    return reward, "宇宙的奥秘在命途中盘旋"


cat.set_wakeup_cmds(cmds=["mana", "玛娜"])
cat.set_rest_cmds(cmds=["exit", "退出"])


@cat.on_cmd(cmds=['divine', '占卜'], states="idle")
async def pray():
    '''花费1玛娜，祈求神的回应'''
    with get_session() as session:
        usermana = get_user_mana(session, cat.channel.id, cat.user.id)
        god = get_mana_god(session, cat.channel.id)

        name = cat.user.name
        mana = usermana.mana
        if mana <= 0:
            await cat.send(f"[{name}] 没有玛娜")
            return

        usermana.mana -= 1

        await cat.send(f"[{name}] 花费了 1玛娜，聆听星辰的呓语")
        await sleep(1)
        await cat.send(f"...")
        await sleep(1)
        await cat.send(f"...")
        await sleep(1)

        await cat.send(god.say())
        session.commit()


@cat.on_cmd(cmds=['pray', '祈祷'], states="idle")
async def handle():
    '''n 花费n玛娜，感受神的呼吸'''
    with get_session() as session:
        usermana = get_user_mana(session, cat.channel.id, cat.user.id)
        god = get_mana_god(session, cat.channel.id)

        if not cat.nums:
            await cat.send("请使用 pray <数字>")
            return

        arg = cat.nums[0]
        name = cat.user.name
        mana = usermana.mana
        if mana < arg:
            await cat.send(f"[{name}] 只有 {mana}玛娜")
            return

        funcs = {
            '欢愉': happy,
            '悼亡': sorrow,
            '深渊': abyss,
            '智慧': wise,
        }

        old_god_name = god.name

        func = funcs[god.name]
        reward, info = func(god=god, mana=arg)
        reward = int(reward)
        await cat.send(info)
        usermana.mana += reward - arg
        mana = usermana.mana
        await cat.send(f"[{name}] 花费了 {arg}玛娜，获得了 {reward}玛娜")
        await cat.send(f"[{name}] 当前有 {mana}玛娜")

        if old_god_name != god.name:
            await cat.send("星空在惊惧中震颤，旧的命途陨落，新的命途执掌星空")
            await cat.send(god.say())

        session.commit()


@cat.on_cmd(cmds="mana", states="idle")
async def handle():
    '''正数买入，负数卖出，0查询'''
    with get_session() as session:
        if not cat.nums:
            await cat.send("请使用 mana <数字>")
            return

        usermana = get_user_mana(session, cat.channel.id, cat.user.id)
        usermoney = get_money(session, cat.channel.id, cat.user.id)
        num = cat.nums[0]
        name = cat.user.name

        mana = usermana.mana
        money = usermoney.money

        if num == 0:
            await cat.send(f"[{name}] 当前持有 {mana}个玛娜")
            return

        # 买mana
        if num > 0:
            action = "购买"
        else:
            action = "卖出"
            num = -num

        if action == "购买":
            if money < num*1000:
                await cat.send(f"[{name}] 只有{money}个金币")
                return
            else:
                usermoney.money -= num*1000
                money = usermoney.money
                usermana.mana += num
                mana = usermana.mana
        else:
            if mana < num:
                await cat.send(f"[{name}] 只有{mana}个玛娜")
                return
            else:
                usermoney.money += num*1000
                money = usermoney.money
                usermana.mana -= num
                mana = usermana.mana

        await cat.send(f"[{name}] {action}玛娜成功，当前持有 {money}个金币，{mana}个玛娜")
        session.commit()
