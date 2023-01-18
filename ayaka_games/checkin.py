'''
    签到模块
'''
import datetime
from ayaka import AyakaCat, get_session
from sqlmodel import SQLModel, Field
from .utils import get_or_create


from .bag import get_money
from .utils import config

cat = AyakaCat('签到')


class Checkin(SQLModel, table=True):
    group_id: str = Field(primary_key=True)
    user_id: str = Field(primary_key=True)
    last_date: str = ""


def get_checkin(session, group_id: str, user_id: str):
    return get_or_create(session, Checkin, group_id=group_id, user_id=user_id)


@cat.on_cmd(cmds=['checkin', '签到'], always=True)
async def checkin():
    date = str(datetime.datetime.now().date())

    with get_session() as session:
        checkin = get_checkin(session, cat.channel.id, cat.user.id)
        if date == checkin.last_date:
            await cat.send(f"[{cat.user.name}] 今天已经签到过了")
            return

        # 签到奖励
        money = get_money(session, cat.channel.id, cat.user.id)
        money.money += config.checkin_reward

        # 更新日期
        checkin.last_date = date

        name = cat.user.name
        await cat.send(f"[{name}] 签到成功，系统奖励 {config.checkin_reward}金\n[{name}] 当前拥有 {money.money}金")
        
        session.commit()
