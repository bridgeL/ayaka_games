from ayaka import AyakaCat, get_adapter, UserDBBase
from ..utils import subscribe

cat = AyakaCat("背包")
adapter = get_adapter()


@subscribe.cls_property_watch
class Money(UserDBBase, table=True):
    money: int = 0


@cat.on_cmd(cmds=["bag", "背包"], always=True)
async def show_bag():
    '''展示背包；你还可以 bag @xx 查看其他人的背包'''
    uid = cat.user.id
    name = cat.user.name

    if cat.event.at:
        user = await cat.get_user(cat.event.at)
        if not user:
            return await cat.send("查无此人")
        uid = user.id
        name = user.name

    money = Money.get_or_create(cat.group.id, uid)
    await cat.send(f"[{name}]当前有 {money.money}金")
