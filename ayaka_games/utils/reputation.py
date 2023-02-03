from sqlmodel import Field, select
from ayaka import AyakaCat, get_adapter, UserDBBase

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
    max_done_combo: int = 0
    '''最大连续成功次数'''

    fail_cnt: int = 0
    '''失败次数'''
    fail_combo: int = 0
    '''连续失败次数'''
    max_fail_combo: int = 0
    '''最大连续失败次数'''

    last_done: int = 0
    '''上次为成功or失败，正为成功，负为失败'''

    def done(self):
        self.total_cnt += 1
        self.done_cnt += 1

        if self.last_done > 0:
            self.done_combo += 1
            if self.done_combo > self.max_done_combo:
                self.max_done_combo = self.done_combo

        if self.last_done < 0:
            self.fail_combo += 0

        self.last_done = 1

    def fail(self):
        self.total_cnt += 1
        self.fail_cnt += 1

        if self.last_done > 0:
            self.done_combo = 0

        if self.last_done < 0:
            self.fail_combo += 1
            if self.fail_combo > self.max_fail_combo:
                self.max_fail_combo = self.fail_combo

        self.last_done = -1


class Reputation(UserDBBase, table=True):
    name: str = Field(primary_key=True)
    label: str = Field(primary_key=True)
    desc: str
    rank: int

    @property
    def info(self):
        return f"[{self.name}] {'★'*self.rank}\n标签：{self.label}\n描述：{self.desc}"

    @classmethod
    def get_user_all_reputation(cls, group_id: str, user_id: str):
        stmt = select(cls).filter_by(group_id=group_id, user_id=user_id)
        cursor = cat.db_session.exec(stmt)
        result = cursor.fetchall()
        return result

    @classmethod
    async def add(cls, group_id: str, user_id: str, label: str, name: str, desc: str, rank: int):
        '''添加并发送成就'''
        data = cls(
            group_id=group_id,
            user_id=user_id,
            name=name,
            desc=desc,
            rank=rank,
            label=label
        )

        cat.db_session.add(data)
        await cat.send(data.info)


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
    items.extend(r.info for r in rs)
    await cat.send_many(items)
