'''
    签到模块
'''
import datetime
from ayaka import AyakaCat
from ..bag import Money
from ..utils import config, subscribe, db

cat = AyakaCat('签到',db=db)


@subscribe.cls_property_watch
class Checkin(db.UserDBBase, table=True):
    last_date: str = ""


@cat.on_cmd(cmds=['checkin', '签到'], always=True)
async def checkin():
    date = str(datetime.datetime.now().date())

    checkin = Checkin.get_or_create(cat.group.id, cat.user.id)
    if date == checkin.last_date:
        await cat.send(f"[{cat.user.name}] 今天已经签到过了")
        return

    # 签到奖励
    money = Money.get_or_create(cat.group.id, cat.user.id)
    money.money += config.checkin_reward

    # 更新日期
    checkin.last_date = date

    name = cat.user.name
    await cat.send(f"[{name}] 签到成功，系统奖励 {config.checkin_reward}金\n[{name}] 当前拥有 {money.money}金")
