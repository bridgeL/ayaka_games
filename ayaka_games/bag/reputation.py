from ayaka import UserDBBase
from .bag import Money
from ..utils import subscribe, Reputation


@subscribe.cls_property_watch
class MoneyAnalyse(UserDBBase, table=True):
    __tablename__ = "money_analyse"

    fail_down_cnt: int = 0
    '''金币从正跌负的次数'''
    rise_up_cnt: int = 0
    '''金币从负回正的次数'''
    sum_get: int = 0
    '''累计获得金币'''
    sum_lose: int = 0
    '''累计损失金币'''
    max: int = 0
    '''历史最大值'''
    min: int = 0
    '''历史最小值'''


@subscribe.on_change(Money.money)
async def _(old_value: int, new_value: int, money: Money):
    diff = new_value - old_value
    gid = money.group_id
    uid = money.user_id

    ma = MoneyAnalyse.get_or_create(gid, uid)

    if old_value < 0 and new_value >= 0:
        ma.rise_up_cnt += 1
    if old_value > 0 and new_value <= 0:
        ma.fail_down_cnt += 1

    if diff > 0:
        ma.sum_get += diff
    else:
        ma.sum_lose -= diff

    if new_value > ma.max:
        ma.max = new_value
    if new_value < ma.min:
        ma.min = new_value

    if ma.rise_up_cnt == 1:
        await Reputation.add(
            gid, uid, "money.rise_up_cnt",
            "东山再起", "清空所有负资产", 1
        )

    if ma.rise_up_cnt == 2:
        await Reputation.add(
            gid, uid, "money.rise_up_cnt",
            "顽强不屈", "第二次清空所有负资产", 2
        )

    if ma.rise_up_cnt == 3:
        await Reputation.add(
            gid, uid, "money.rise_up_cnt",
            "永不言弃", "第三次清空所有负资产", 3
        )

    if ma.fail_down_cnt == 1:
        await Reputation.add(
            gid, uid, "money.fail_down_cnt",
            "家徒四壁", "失去所有资产", 1
        )

    if ma.fail_down_cnt == 2:
        await Reputation.add(
            gid, uid, "money.fail_down_cnt",
            "常败将军", "第二次失去所有资产", 2
        )

    if ma.fail_down_cnt == 3:
        await Reputation.add(
            gid, uid, "money.fail_down_cnt",
            "土块", "第三次失去所有资产", 3
        )


@subscribe.on_change(MoneyAnalyse.max)
async def _(old_value: int, new_value: int, ma: MoneyAnalyse):
    gid = ma.group_id
    uid = ma.user_id

    N = 100_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.max",
            "小有成就", "资产最大值突破10万", 1
        )

    N = 1_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.max",
            "百万富翁", "资产最大值突破100万", 2
        )

    N = 10_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.max",
            "路灯候选", "资产最大值突破1000万", 3
        )

    N = 100_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.max",
            "小目标", "资产最大值突破1亿", 4
        )


@subscribe.on_change(MoneyAnalyse.min)
async def _(old_value: int, new_value: int, ma: MoneyAnalyse):
    old_value = -old_value
    new_value = -new_value
    gid = ma.group_id
    uid = ma.user_id

    N = 100_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.min",
            "小有成就", "资产最小值突破负10万", 1
        )

    N = 1_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.min",
            "百万负翁", "资产最小值突破负100万", 2
        )

    N = 10_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.min",
            "银行贵宾", "资产最小值突破负1000万", 3
        )

    N = 100_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.min",
            "银行亲爹", "资产最小值突破负1亿", 4
        )


@subscribe.on_change(MoneyAnalyse.sum_get)
async def _(old_value: int, new_value: int, ma: MoneyAnalyse):
    gid = ma.group_id
    uid = ma.user_id

    N = 100_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.sum_get",
            "第一桶金", "累计获得10万金币", 1
        )

    N = 1_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.sum_get",
            "财运亨通", "累计获得100万金币", 2
        )

    N = 10_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.sum_get",
            "爱钱如命", "累计获得1000万金币", 3
        )

    N = 100_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.sum_get",
            "痛苦太多", "累计获得1亿金币", 4
        )


@subscribe.on_change(MoneyAnalyse.sum_lose)
async def _(old_value: int, new_value: int, ma: MoneyAnalyse):
    gid = ma.group_id
    uid = ma.user_id

    N = 100_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.sum_lose",
            "出手阔绰", "累计消费10万金币", 1
        )

    N = 1_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.sum_lose",
            "挥金如土", "累计消费100万金币", 2
        )

    N = 10_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.sum_lose",
            "一掷千金", "累计消费1000万金币", 3
        )

    N = 100_000_000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "money.sum_lose",
            "分享痛苦", "累计消费1亿金币", 4
        )
