from ayaka import AyakaCat, get_session
from sqlmodel import SQLModel, Field
from .utils import get_or_create

cat = AyakaCat("背包")


class Money(SQLModel, table=True):
    group_id: str = Field(primary_key=True)
    user_id: str = Field(primary_key=True)
    money: int = 1000


def get_money(session, group_id: str, user_id: str):
    return get_or_create(session, Money, group_id=group_id, user_id=user_id)


@cat.on_cmd(cmds=["bag", "背包"], always=True)
async def show_bag():
    '''展示背包；你还可以 bag @xx 查看其他人的背包'''
    with get_session() as session:
        uid = cat.user.id
        name = cat.user.name

        if cat.event.at:
            user = await cat.get_user(cat.event.at)
            if not user:
                return await cat.send("查无此人")
            uid = user.id
            name = user.name

        money = get_money(session, cat.group.id, uid)
        await cat.send(f"[{name}]当前有 {money.money}金")
