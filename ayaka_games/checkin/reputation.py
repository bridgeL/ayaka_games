import datetime
from ayaka import UserDBBase
from .checkin import Checkin
from ..utils import subscribe, Reputation


@subscribe.cls_property_watch
class CheckinAnalyse(UserDBBase, table=True):
    __tablename__ = "checkin_analyse"

    combo: int = 1
    '''连续签到天数'''
    max_combo: int = 1
    max_combo_break: int = 0


def to_date(s: str):
    if s:
        ss = s.split("-")
        ns = [int(s) for s in ss]
    else:
        ns = [2023, 1, 1]
    return datetime.date(*ns)


@subscribe.on_change(Checkin.last_date)
async def _(old_value: int, new_value: int, c: Checkin):
    diff = to_date(new_value) - to_date(old_value)
    diff = diff.days

    gid = c.group_id
    uid = c.user_id

    ca = CheckinAnalyse.get_or_create(gid, uid)

    if diff == 1:
        ca.combo += 1
        if ca.combo > ca.max_combo:
            ca.max_combo = ca.max_combo
    else:
        if ca.combo > ca.max_combo_break:
            ca.max_combo_break = ca.combo

            N = 2
            if ca.combo >= N:
                await Reputation.add(
                    gid, uid, "checkin",
                    "寸止", "连续签到至少2天后断签", 1
                )

            N = 6
            if ca.combo >= N:
                await Reputation.add(
                    gid, uid, "checkin",
                    "星期天", "连续签到至少6天后断签", 2
                )

            N = 29
            if ca.combo >= N:
                await Reputation.add(
                    gid, uid, "checkin",
                    "断签爱好者", "连续签到至少29天后断签", 3
                )

        ca.combo = 0


@subscribe.on_change(CheckinAnalyse.combo)
async def _(old_value: int, new_value: int, ca: CheckinAnalyse):
    gid = ca.group_id
    uid = ca.user_id

    N = 3
    if ca.max_combo < N and new_value >= N:
        await Reputation.add(
            gid, uid, "checkin",
            "常来看看", "连续签到3天", 1
        )

    N = 7
    if ca.max_combo < N and new_value >= N:
        await Reputation.add(
            gid, uid, "checkin",
            "坚持不懈", "连续签到1周", 2
        )

    N = 30
    if ca.max_combo < N and new_value >= N:
        await Reputation.add(
            gid, uid, "checkin",
            "月卡爱好者", "连续签到1个月", 3
        )
