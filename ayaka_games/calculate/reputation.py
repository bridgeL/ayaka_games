from ..utils import subscribe, Reputation, AnalyseBase


@subscribe.cls_property_watch
class CalculateAnalyse(AnalyseBase, table=True):
    __tablename__ = "calculate_analyse"

    check_ans_cnt: int = 0
    '''查看答案次数'''


@subscribe.on_change(CalculateAnalyse.total_cnt)
async def _(old_value: int, new_value: int, ca: CalculateAnalyse):
    gid = ca.group_id
    uid = ca.user_id

    N = 10
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "calculate.total_cnt",
            "浅尝辄止", "游玩10次24点", 1
        )

    N = 100
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "calculate.total_cnt",
            "渐入佳境", "游玩100次24点", 2
        )

    N = 1000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "calculate.total_cnt",
            "乐此不疲", "游玩1000次24点", 3
        )


@subscribe.on_change(CalculateAnalyse.check_ans_cnt)
async def _(old_value: int, new_value: int, ca: CalculateAnalyse):
    gid = ca.group_id
    uid = ca.user_id

    N = 10
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "calculate.check_ans_cnt",
            "不懂就问", "查看10次24点的答案", 1
        )

    N = 100
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "calculate.check_ans_cnt",
            "知乎网友", "查看100次24点的答案", 2
        )

    N = 1000
    if old_value < N and new_value >= N:
        await Reputation.add(
            gid, uid, "calculate.check_ans_cnt",
            "玩游戏必开无敌挂", "查看1000次24点的答案", 3
        )


# @subscribe.on_change(CalculateAnalyse.done_cnt)
# async def _(old_value: int, new_value: int, ca: CalculateAnalyse):
#     gid = ca.group_id
#     uid = ca.user_id

#     if new_value > ca

#     N = 10
#     if old_value < N and new_value >= N:
#         await Reputation.add(
#             gid, uid, "calculate.check_ans_cnt",
#             "不懂就问", "查看10次24点的答案", 1
#         )

#     N = 100
#     if old_value < N and new_value >= N:
#         await Reputation.add(
#             gid, uid, "calculate.check_ans_cnt",
#             "知乎网友", "查看100次24点的答案", 2
#         )

#     N = 1000
#     if old_value < N and new_value >= N:
#         await Reputation.add(
#             gid, uid, "calculate.check_ans_cnt",
#             "玩游戏必开无敌挂", "查看1000次24点的答案", 3
#         )
