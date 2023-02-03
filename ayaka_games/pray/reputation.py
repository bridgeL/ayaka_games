from ..utils import subscribe, set_over_type_reputaion, AnalyseBase


@subscribe.cls_property_watch
class PrayerAnalyse(AnalyseBase, table=True):
    __tablename__ = "prayer"

    total_money: int = 0
    '''通过祈祷，总共使他人获得的金币数'''


@subscribe.cls_property_watch
class BePrayedAnalyse(AnalyseBase, table=True):
    __tablename__ = "be_prayed"

    total_money: int = 0
    '''因他人祈祷，总共获得的金币数'''


set_over_type_reputaion(
    cls_attr=PrayerAnalyse.done_cnt,
    rs=[
        ("乐于助人", "累计祈祷大成功达到3次", 3),
        ("幸运星", "累计祈祷大成功达到7次", 7),
        ("群菩萨", "累计祈祷大成功达到21次", 30),
    ]
)

set_over_type_reputaion(
    cls_attr=PrayerAnalyse.done_combo,
    rs=[
        ("闻一知二", "连续2次祈祷大成功", 2),
        ("接二连三", "连续3次祈祷大成功", 3),
        ("五光十色", "连续5次祈祷大成功", 5),
    ]
)

set_over_type_reputaion(
    cls_attr=PrayerAnalyse.fail_cnt,
    rs=[
        ("乐于助人", "累计祈祷大失败达到3次", 3),
        ("仗义疏财", "累计祈祷大失败达到7次", 7),
        ("明火执仗", "累计祈祷大失败达到21次", 30),
    ]
)

set_over_type_reputaion(
    cls_attr=PrayerAnalyse.fail_combo,
    rs=[
        ("小鬼预备队", "连续2次祈祷大失败", 2),
        ("小鬼大队长", "连续3次祈祷大失败", 3),
        ("群恶魔", "连续5次祈祷大失败", 5),
    ]
)

set_over_type_reputaion(
    cls_attr=BePrayedAnalyse.done_cnt,
    rs=[
        ("意外之财", "累计遭遇祈祷大成功达到1次", 1),
        ("金银花", "累计遭遇祈祷大成功达到3次", 3),
        ("致富经", "累计遭遇祈祷大成功达到5次", 5),
    ]
)

set_over_type_reputaion(
    cls_attr=BePrayedAnalyse.done_combo,
    rs=[
        ("红双喜", "连续遭遇2次祈祷大成功", 2),
        ("群欧皇", "连续遭遇3次祈祷大成功", 3),
        ("上辈子拯救地球", "连续遭遇5次祈祷大成功", 5),
    ]
)

set_over_type_reputaion(
    cls_attr=BePrayedAnalyse.fail_cnt,
    rs=[
        ("飞来横祸", "累计遭遇祈祷大失败达到1次", 1),
        ("倒霉蛋", "累计遭遇祈祷大失败达到3次", 3),
        ("群霉神", "累计遭遇祈祷大失败达到5次", 5),
    ]
)

set_over_type_reputaion(
    cls_attr=BePrayedAnalyse.fail_combo,
    rs=[
        ("祸不单行", "连续遭遇2次祈祷大失败", 2),
        ("三灾八难", "连续遭遇3次祈祷大失败", 3),
        ("五雷轰顶", "连续遭遇5次祈祷大失败", 5),
    ]
)
