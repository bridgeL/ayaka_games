import datetime
from .checkin import Checkin
from ..utils import subscribe, set_over_type_reputaion, set_zero_type_reputaion, db


@subscribe.cls_property_watch
class CheckinAnalyse(db.UserDBBase, table=True):
    __tablename__ = "checkin_analyse"

    combo: int = 0
    '''连续签到天数'''


def to_date(s: str):
    ss = s.split("-")
    ns = [int(s) for s in ss]
    return datetime.date(*ns)


@subscribe.on_change(Checkin.last_date)
async def _(old_value: str, new_value: str, c: Checkin):
    gid = c.group_id
    uid = c.user_id
    ca = CheckinAnalyse.get_or_create(gid, uid)

    if not old_value:
        ca.combo = 1
        return

    if (to_date(new_value) - to_date(old_value)).days == 1:
        ca.combo += 1

    else:
        ca.combo = 1


set_over_type_reputaion(
    cls_attr=CheckinAnalyse.combo,
    rs=[
        ("常来看看", "连续签到3天", 3),
        ("坚持不懈", "连续签到1周", 7),
        ("月卡爱好者", "连续签到1个月", 30),
    ]
)

set_zero_type_reputaion(
    cls_attr=CheckinAnalyse.combo,
    rs=[
        ("寸止", "连续签到至少2天后断签", 2),
        ("星期天", "连续签到至少6天后断签", 6),
        ("多喝热水", "连续签到至少29天后断签", 30),
    ],
    zero=1,
)
