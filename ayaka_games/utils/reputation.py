import datetime
from sqlmodel import Field, select
from ayaka import AyakaCat, get_adapter, UserDBBase
from .subscribe import subscribe

cat = AyakaCat("成就")
adapter = get_adapter()


class AnalyseBase(UserDBBase):
    '''可以继承，统计一些基本的信息'''
    total_cnt: int = 0
    '''总次数'''

    done_cnt: int = 0
    '''成功次数'''
    done_combo: int = 0
    '''连续成功次数'''

    fail_cnt: int = 0
    '''失败次数'''
    fail_combo: int = 0
    '''连续失败次数'''

    last_done: int = 0
    '''上次为成功or失败，正为成功，负为失败'''

    def done(self):
        '''成功'''
        self.total_cnt += 1
        self.done_cnt += 1

        if self.last_done > 0:
            self.done_combo += 1

        if self.last_done < 0:
            self.fail_combo = 0

        self.last_done = 1

    def fail(self):
        '''失败'''
        self.total_cnt += 1
        self.fail_cnt += 1

        if self.last_done > 0:
            self.done_combo = 0

        if self.last_done < 0:
            self.fail_combo += 1

        self.last_done = -1


class Reputation(UserDBBase, table=True):
    name: str = Field(primary_key=True)
    label: str = Field(primary_key=True)
    desc: str
    rank: int
    time: str

    @property
    def info(self):
        return f"[{self.name}] {'★'*self.rank}\n{self.desc}"

    @classmethod
    def get_user_all_reputation(cls, group_id: str, user_id: str):
        stmt = select(cls).filter_by(group_id=group_id,
                                     user_id=user_id).order_by(cls.label, cls.rank)
        cursor = cat.db_session.exec(stmt)
        return cursor.all()

    @classmethod
    async def add(cls, group_id: str, user_id: str, label: str, name: str, desc: str, rank: int):
        '''添加并发送成就'''
        statement = select(cls).filter_by(
            group_id=group_id,
            user_id=user_id,
            name=name,
            label=label
        )
        cursor = cat.db_session.exec(statement)
        data = cursor.one_or_none()

        if not data:
            data = cls(
                group_id=group_id,
                user_id=user_id,
                name=name,
                desc=desc,
                rank=rank,
                label=label,
                time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            cat.db_session.add(data)
            u = await cat.get_user(user_id)
            await cat.send(f"{u.name} 获得成就\n{data.info}")


@cat.on_cmd(cmds="成就", always=True)
async def show_reputation():
    '''展示成就。你还可以 成就 @xx 查看其他人的成就'''
    uid = cat.user.id
    name = cat.user.name

    if cat.event.at:
        user = await cat.get_user(cat.event.at)
        if not user:
            return await cat.send("查无此人")
        uid = user.id
        name = user.name

    rs = Reputation.get_user_all_reputation(cat.group.id, uid)
    if not rs:
        return await cat.send(f"[{name}]当前没有成就")
    items = [f"[{name}]当前成就"]
    items.extend(f"{r.info}\n获得时间：{r.time}" for r in rs)
    await cat.send_many(items)


def set_over_type_reputaion(cls_attr, rs: list[tuple[str, str, int]], reverse: bool = False, label: str | None = None):
    '''超过型成就'''
    if label is None:
        label = str(cls_attr)

    @subscribe.on_change(cls_attr)
    async def _(old_value: int, new_value: int, ca: UserDBBase):
        if reverse:
            old_value = -old_value
            new_value = -new_value

        gid = ca.group_id
        uid = ca.user_id

        for i, r in enumerate(rs):
            N = r[2]
            if old_value < N and new_value >= N:
                await Reputation.add(gid, uid, label, r[0], r[1], i+1)


def set_zero_type_reputaion(cls_attr, rs: list[tuple[str, str, int]], label: str | None = None, zero: int = 0):
    '''归零型成就'''
    if label is None:
        label = str(cls_attr)

    @subscribe.on_change(cls_attr)
    async def _(old_value: int, new_value: int, ca: UserDBBase):
        gid = ca.group_id
        uid = ca.user_id

        for i, r in enumerate(rs):
            N = r[2]
            if old_value >= N and new_value <= zero:
                await Reputation.add(gid, uid, label, r[0], r[1], i+1)
