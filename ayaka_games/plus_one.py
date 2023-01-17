'''
    +1s 
'''
from asyncio import sleep
from random import choice
from ayaka import AyakaCat

cat = AyakaCat("加一秒")
cat.help = '''
每人初始时间值为0
每有3个不同的人执行一次或若干次加1，boss就会完成蓄力，吸取目前时间值最高的人的时间，如果有多人，则都被吸取
boss时间值>=17时，游戏结束，boss将带走所有比他时间值高的人，剩余人中时间值最高的获胜，世界重启
'''

feelings = [
    "感觉身体被掏空",
    "感受到一阵空虚",
    "的时间似乎变快了",
    "似乎被夺走了什么东西"
]

restarts = [
    "世界被虚空的狂风撕碎",
    "世界在不灭的火焰中湮灭",
    "&*@）#……游戏出故障了",
    "限界的界世了越超间时的ssob"
]


def get_max(data: dict[int, int]):
    '''
        data 是保存了 uid-time 数据的字典
    '''
    # 转换为items列表，方便排序
    items = list(data.items())
    items.sort(key=lambda x: x[1], reverse=True)

    uids = []
    if not items:
        return uids

    time_max = items[0][1]
    for uid, time in items:
        if time == time_max:
            uids.append(uid)
        else:
            break

    return uids


class PlayerGroup:
    def __init__(self) -> None:
        self.data: dict[str, int] = {}

    def get_time(self, uid: str) -> int:
        '''获取uid对应的时间值，如果不存在，返回为0'''
        if uid not in self.data:
            self.data[uid] = 0
            return 0

        # 存在则返回
        return self.data[uid]

    def change_time(self, uid: str, diff: int):
        '''修改uid对应的时间值'''

        time: int = self.data.get(uid, 0)

        # 修改time
        time += diff

        self.data[uid] = time

        # 返回修改后的值
        return time

    def clear_all(self):
        self.data = {}


class Boss:
    boss_default = {
        "time": 0,
        # 记录不同的人的发言
        "uids": []
    }

    max_time = 17
    max_power = 3

    def __init__(self, player_group: PlayerGroup) -> None:
        self.data = self.boss_default
        self.player_group = player_group

    @property
    def time(self) -> int:
        return self.data["time"]

    @time.setter
    def time(self, v: int):
        self.data["time"] = v

    @property
    def power(self):
        return len(self.data["uids"])

    def clear_power(self):
        self.data["uids"] = []

    def add_power(self, uid: int):
        # 防止重复
        uids: list = self.data["uids"]
        if uid in uids:
            return
        uids.append(uid)
        self.data["uids"] = uids

    def kill(self, data: dict):
        '''
            data 是保存了 uid-time 数据的字典
        '''
        # 发动攻击，清除power
        self.clear_power()

        # 记录吸取情况
        uids = get_max(data)

        # 吸取时间
        cnt = 0
        for uid in uids:
            i = choice([1, 1, 1, 2, 2, 3])
            cnt += i
            self.player_group.change_time(uid, -i)
        self.time += cnt

        # 告知吸取情况
        return uids

    @property
    def state(self):
        info = f"boss目前的时间：{self.time}/{self.max_time}\nboss目前的能量：{self.power}/{self.max_power}"
        if self.power >= self.max_power - 1:
            info += "\nboss即将发动攻击！"
        if self.time >= self.max_time - 1:
            info += "\nboss的时间即将到达顶峰！"
        return info


class Game:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.player_group = PlayerGroup()
        self.boss = Boss(self.player_group)

    def get_over_players(self):
        boss_time = self.boss.time
        data = self.player_group.data
        # 时间值>boss的人
        uids = [uid for uid, time in data.items() if time > boss_time]
        return uids

    def get_winners(self):
        boss_time = self.boss.time
        data = self.player_group.data
        # 时间值小于等于boss的人
        data = {uid: time for uid, time in data.items() if time <= boss_time}
        return get_max(data)


@cat.on_cmd(cmds="加一秒")
async def cat_start():
    '''启动游戏'''
    game = cat.get_data(Game)
    if not game.boss:
        game.reset()
    await cat.wakeup()
    await cat.send_help()


@cat.on_cmd(cmds=["exit", "退出"], states="*")
async def cat_close():
    '''退出游戏（数据保留）'''
    await cat.send("数据已保存")
    await cat.rest()


@cat.on_cmd(cmds="我的", states="idle")
async def inquiry():
    '''查看你目前的时间'''
    game = cat.get_data(Game)
    time = game.player_group.get_time(cat.current.sender_id)
    await cat.send(f"[{cat.current.sender_name}]目前的时间：{time}")


@cat.on_cmd(cmds="boss", states="idle")
async def inquiry_boss():
    '''查看boss的时间和能量'''
    game = cat.get_data(Game)
    await cat.send(game.boss.state)


@cat.on_cmd(cmds="全部", states="idle")
async def inquiry_all():
    '''查看所有人参与情况，以及boss的时间和能量'''
    game = cat.get_data(Game)
    # boss
    info = game.boss.state

    # 所有人
    data = game.player_group.data

    if not data:
        await cat.send(info)
        return

    # 查找名字
    users = await cat.get_users()
    user_data = {u.id: u.name for u in users}

    for uid, time in data.items():
        info += f"\n[{user_data[uid]}]目前的时间：{time}"
    await cat.send(info)


@cat.on_cmd(cmds=["加一", "+1", "加1"], states="idle")
async def plus():
    '''让你的时间+1'''
    game = cat.get_data(Game)

    # 玩家
    time = game.player_group.change_time(cat.current.sender_id, 1)
    await cat.send(f"[{cat.current.sender_name}]的时间增加了！目前为：{time}")

    # boss
    game.boss.add_power(cat.current.sender_id)
    await cat.send(game.boss.state)

    # boss 能量不够
    if game.boss.power < game.boss.max_power:
        return

    # boss 攻击
    uids = game.boss.kill(game.player_group.data)

    await cat.send("boss发动了攻击...")
    await sleep(2)
    await cat.send("...")
    await sleep(2)

    if not uids:
        await cat.send("无事发生")
        return

    # 查找名字
    users = await cat.get_users()
    user_data = {u.id: u.name for u in users}

    # 告知被攻击情况
    items = [f"[{user_data[uid]}] {choice(feelings)}" for uid in uids]
    info = "\n".join(items)
    await cat.send(info)
    await inquiry_all()

    # boss 时间不够
    if game.boss.time < game.boss.max_time:
        return

    # 游戏结束
    await sleep(2)
    await cat.send(f"boss的时间超越了世界的界限，{choice(restarts)}...")
    await sleep(2)
    await cat.send("...")
    await sleep(2)

    # 带走时间过高的玩家
    uids = game.get_over_players()
    items = [f"[{user_data[uid]}]" for uid in uids]

    if items:
        info = f"boss带走了所有时间高于它的玩家：" + "、".join(items)
        await cat.send(info)

    # 告知胜利者
    uids = game.get_winners()
    items = [f"[{user_data[uid]}]" for uid in uids]

    if not items:
        info = "没有人"
    else:
        info = "、".join(items)

    info = "在上一个世界中：" + info + "是最终的赢家！"
    await cat.send(info)

    game.player_group.clear_all()
    game.boss.time = 0
