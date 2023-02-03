from sqlmodel import Field, select
from ayaka import AyakaCat, get_adapter, UserDBBase

cat = AyakaCat("成就")
adapter = get_adapter()


class AnalyseBase(UserDBBase):
    '''可以继承，统计一些基本的信息'''
    done_cnt: int
    '''成功次数'''
    done_combo: int
    '''连续成功次数'''
    max_done_combo: int
    '''最大连续成功次数'''

    fail_cnt: int
    '''失败次数'''
    fail_combo: int
    '''连续失败次数'''
    max_fail_combo: int
    '''最大连续失败次数'''


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
