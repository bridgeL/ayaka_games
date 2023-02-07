from ayaka import get_db
from .bag import Money
from ..utils import subscribe, set_over_type_reputaion

db = get_db("ayaka_games")

@subscribe.cls_property_watch
class MoneyAnalyse(db.UserDBBase, table=True):

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


set_over_type_reputaion(
    cls_attr=MoneyAnalyse.rise_up_cnt,
    rs=[
        ("东山再起", "清空所有负资产", 1),
        ("顽强不屈", "第二次清空所有负资产", 2),
        ("永不言弃", "第三次清空所有负资产", 3),
    ]
)

set_over_type_reputaion(
    cls_attr=MoneyAnalyse.fail_down_cnt,
    rs=[
        ("家徒四壁", "失去所有资产", 1),
        ("常败将军", "第二次失去所有资产", 2),
        ("土块", "第三次失去所有资产", 3),
    ]
)

set_over_type_reputaion(
    cls_attr=MoneyAnalyse.max,
    rs=[
        ("小有成就", "资产最大值突破10万", 100_000),
        ("百万富翁", "资产最大值突破100万", 1_000_000),
        ("路灯候选", "资产最大值突破1000万", 10_000_000),
        ("小目标", "资产最大值突破1亿", 100_000_000),
    ]
)

set_over_type_reputaion(
    cls_attr=MoneyAnalyse.min,
    rs=[
        ("小有成就", "资产最小值突破负10万", 100_000),
        ("百万负翁", "资产最小值突破负100万", 1_000_000),
        ("银行贵宾", "资产最小值突破负1000万", 10_000_000),
        ("银行亲爹", "资产最小值突破负1亿", 100_000_000),
    ],
    reverse=True
)

set_over_type_reputaion(
    cls_attr=MoneyAnalyse.sum_get,
    rs=[
        ("第一桶金", "累计获得10万金币", 100_000),
        ("财运亨通", "累计获得100万金币", 1_000_000),
        ("爱钱如命", "累计获得1000万金币", 10_000_000),
        ("痛苦太多", "累计获得1亿金币", 100_000_000),
    ]
)

set_over_type_reputaion(
    cls_attr=MoneyAnalyse.sum_lose,
    rs=[
        ("出手阔绰", "累计消费10万金币", 100_000),
        ("挥金如土", "累计消费100万金币", 1_000_000),
        ("一掷千金", "累计消费1000万金币", 10_000_000),
        ("分享痛苦", "累计消费1亿金币", 100_000_000),
    ]
)
