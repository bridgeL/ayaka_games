from ..utils import subscribe, AnalyseBase, set_over_type_reputaion


@subscribe.cls_property_watch
class CalculateAnalyse(AnalyseBase, table=True):
    __tablename__ = "calculate_analyse"

    check_ans_cnt: int = 0
    '''查看答案次数'''


set_over_type_reputaion(
    cls_attr=CalculateAnalyse.total_cnt,
    rs=[
        ("浅尝辄止", "游玩10次24点", 10),
        ("渐入佳境", "游玩100次24点", 100),
        ("乐此不疲", "游玩1000次24点", 1000),
    ]
)

set_over_type_reputaion(
    cls_attr=CalculateAnalyse.check_ans_cnt,
    rs=[
        ("不懂就问", "查看10次24点的答案", 10),
        ("风灵月影", "查看100次24点的答案", 100),
        ("开挂爱好者", "查看1000次24点的答案", 1000),
    ]
)
