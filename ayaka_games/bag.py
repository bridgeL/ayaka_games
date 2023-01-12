from ayaka import AyakaCat, AyakaUserDB

cat = AyakaCat("背包")


class Money(AyakaUserDB):
    __table_name__ = "money"
    value: int = 1000


def get_money(group_id: int, user_id: int):
    return Money.select_one(
        group_id=group_id,
        user_id=user_id
    )


@cat.on_cmd(cmds=["bag", "背包"], always=True)
async def show_bag():
    '''展示背包；你还可以 bag @xx 查看其他人的背包'''
    if not cat.current.arg:
        money = get_money(cat.current.session_id, cat.current.sender_id)
        name = cat.current.sender_name
    else:
        user = await cat.get_user(str(cat.current.nums[0]))
        if not user:
            await cat.send("查无此人")
            return
        money = get_money(cat.current.session_id, user.id)
        name = user.name

    await cat.send(f"[{name}]当前有 {money.value}金")
