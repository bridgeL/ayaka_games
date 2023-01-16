'''24点，以及拓展版48点'''
import re
from random import choice
from pydantic import BaseModel
from loguru import logger
from ayaka import AyakaCat, load_data_from_file
from .bag import get_money
from .data import downloader, config

cat = AyakaCat("24点")
cat.help = '''
加、减、乘、除、次方，5种运算符可用
给出4个1-9范围内的数字，请通过以上运算符算出24点
同时还有48点等其他模式可选，欢迎挑战
'''


questions_bin: dict[int, dict[str, list[str]]] = {}


class Cache(BaseModel):
    n: int = 0
    nums: list[int] = []
    solutions: list[str] = []

    @property
    def question(self):
        return " ".join(str(n) for n in self.nums)


@downloader.on_finish
async def finish():
    path = downloader.BASE_DIR / "24点"
    for p in path.iterdir():
        try:
            questions_bin[int(p.stem)] = load_data_from_file(p)
        except:
            pass


cat.set_rest_cmds(cmds=["退出", "exit"])


@cat.on_cmd(cmds="24点")
async def cat_start():
    '''唤醒猫猫，开始游戏'''
    await cat.wakeup()
    await cat.send_help()
    await set_mode_menu()


@cat.on_cmd(cmds="切换模式", states="*")
async def set_mode_menu():
    items = ["切换模式："]
    items.extend(f"- {n}" for n in questions_bin)
    items.append("请输入")
    await cat.send("\n".join(items))
    cat.state = "切换模式"


@cat.on_text(states="切换模式")
async def set_mode():
    '''更多挑战'''
    if not cat.current.nums or cat.current.nums[0] not in questions_bin:
        await cat.send("输入不合法")
        return

    cache = cat.get_data(Cache)
    cache.n = cat.current.nums[0]
    await cat.send(f"切换模式为 {cache.n}点")
    cat.state = "计算"
    await select_question()


@cat.on_cmd(cmds=["出题", "next"], states="计算")
async def select_question():
    '''出题'''
    cache = cat.get_data(Cache)

    data = questions_bin[cache.n]
    k, cache.solutions = choice(list(data.items()))
    cache.nums = [int(n) for n in k.split(" ")]

    await show_question()


@cat.on_cmd(cmds=["题目", "question"], states="计算")
async def show_question():
    '''展示题目'''
    cache = cat.get_data(Cache)
    await cat.send(cache.question)
    await cat.send(f"TIPS：本题至少有{len(cache.solutions)}种答案（使用不同的运算符）")


@cat.on_cmd(cmds=["答案", "answer"], states="计算")
async def show_solutions():
    '''展示答案'''
    cache = cat.get_data(Cache)
    solutions = cache.solutions

    info = "\n".join(solutions)
    await cat.send(info)
    await select_question()


@cat.on_text(states="计算")
async def calculate_exp():
    '''请使用正确的表达式，例如 (1+2)*(3+3)'''
    cache = cat.get_data(Cache)
    exp = cat.current.arg

    try:
        exp = pre_check(exp, cache.nums)
    except Exception as e:
        await cat.send(str(e))
        return

    try:
        r = calc(exp)
    except Exception as e:
        await cat.send(str(e))
        return

    await cat.send(f"{exp}={r}")

    if abs(r - cache.n) > 0.0001:
        await cat.send("错误")
        return

    await cat.send("正确！")
    reward = config.calculate_reward
    money = get_money(group_id=cat.current.session_id,
                      user_id=cat.current.sender_id)
    money.value += reward
    await cat.send(f"奖励{reward}金")
    await select_question()

# ---- 预检查：对字符串做初步的筛查和简单的纠正 ----


def check_len(exp: str):
    '''拒绝长度异常的表达式'''
    return len(exp) <= 20


def pre_correct(exp: str):
    '''初步矫正表达式：移除空格，纠正操作符'''
    exp = exp.strip().replace("\\", "/").replace(" ", "")
    exp = exp.replace("x", "*").replace("^", "**")
    exp = re.sub(r"[（{【\[]", "(", exp)
    exp = re.sub(r"[）}】\]]", ")", exp)
    return exp


def check_brackets_close(exp: str):
    '''检查括号配对是否闭合'''
    cnt = 0
    for t in exp:
        if t == "(":
            cnt += 1
        elif t == ")":
            cnt -= 1
            if cnt < 0:
                return False
    return cnt == 0


def check_op(exp: str):
    '''检测无效操作符'''
    patt = re.compile(r"\*\*|\*|\+|-|/|\(|\)|\d+")
    return not patt.sub("", exp)


def split_exp(exp: str):
    '''分割表达式'''
    patt = re.compile(r"\*\*|\*|\+|-|/|\(|\)|\d+")
    ts: list[int | str] = []
    for t in patt.findall(exp):
        if t not in ["(", ")", "+", "-", "*", "/", "**"]:
            t = int(t)
        ts.append(t)
    return ts


def check_num(ts: list[str | int], nums: list[int]):
    '''检查是否使用指定数字'''
    nums_copy = [n for n in nums]
    for t in ts:
        if isinstance(t, int):
            if t not in nums_copy:
                return False
            nums_copy.remove(t)
    return not nums_copy


def check_and_correct_op(ts: list[str | int]):
    '''补全缺失的*，检查错误组合'''

    _ts = [ts[0]]
    last = ts[0]

    for t in ts[1:]:
        # 数字 + (，补全*
        if isinstance(last, int) and t == "(":
            _ts.append("*")

        # (只能 + 数字或(
        elif last == "(" and isinstance(t, str) and t != "(":
            return

        # ) + (或数字，补全*
        elif last == ")" and (isinstance(t, int) or t == "("):
            _ts.append("*")

        # 其他操作符必定不 + )
        elif last in ["+", "-", "*", "/", "**"] and t == ")":
            return

        _ts.append(t)
        last = t
    return _ts


def pre_check(exp, nums):
    '''预检查，并简单矫正一些错误，返回纠正后的表达式，抛出错误'''
    if not check_len(exp):
        raise Exception("表达式过长")

    exp = pre_correct(exp)

    if not check_brackets_close(exp):
        raise Exception("括号未闭合")

    if not check_op(exp):
        raise Exception("无效操作符")

    ts = split_exp(exp)

    if not check_num(ts, nums):
        raise Exception("没有使用指定数字")

    ts = check_and_correct_op(ts)
    if not ts:
        raise Exception("错误的操作符组合")

    return "".join(str(t) for t in ts)

# ---- 计算合法格式的中缀表达式 ----


def mid2post(ts: list[str | int]):
    '''中缀表达式转后缀表达式'''
    ts.append("#")
    stack = ["#"]
    rs: list[str | int] = []

    _in = {
        "#": 0,
        "(": 1,
        "+": 3, "-": 3,
        "*": 5, "/": 5,
        "**": 7,
    }
    _out = {
        "#": 0,
        ")": 1,
        "+": 2, "-": 2,
        "*": 4, "/": 4,
        "**": 6,
        "(": 8,
    }

    for t in ts:
        # 数字直接计入结果
        if isinstance(t, int):
            rs.append(t)
            continue

        # 操作符判断优先级入栈
        d = _out[t] - _in[stack[-1]]

        # 若 out < in，则内部操作符优先级更高，出栈，计入结果，且循环判断
        # 注意：栈不可能通过此条件弹出至空，因为 # 对应 最小in = 最小out = 0
        while d < 0:
            rs.append(stack.pop())
            d = _out[t] - _in[stack[-1]]

        # 若 out > in，则外部操作符优先级更高，入栈
        if d > 0:
            stack.append(t)

        # 若 out == in，则优先级相同，出栈，且不计入结果
        else:
            stack.pop()

    return rs


def base_calc(n1: float, n2: float, op: str):
    '''计算数值，出错时抛出异常'''
    logger.debug(f"基本运算单元 {n1}{op}{n2}")

    if op == "*":
        return n1*n2

    # 除0自动抛出异常
    if op == "/":
        return n1 / n2

    if op == "+":
        return n1 + n2

    if op == "-":
        return n1 - n2

    if op == "**":
        # 阻断大指数运算
        if n1 > 100 or n2 > 100:
            raise
        return n1 ** n2

    # 未知操作符
    raise


def calc_post(ts: list[str | int]):
    '''计算后缀表达式'''
    ops: list[str] = []
    nums: list[float] = []
    for t in ts:
        if isinstance(t, str):
            ops.append(t)
        else:
            nums.append(float(t))

        if len(nums) >= 2 and ops:
            n2 = nums.pop()
            n1 = nums.pop()
            op = ops.pop()
            n = base_calc(n1, n2, op)

            # 中断过大或过小的运算
            if abs(n) > 10000 or abs(n) < 0.00001:
                raise

            nums.append(n)

    return nums[0]


def calc(exp):
    '''计算表达式，返回计算的结果，抛出异常'''
    ts = split_exp(exp)
    ts = mid2post(ts)

    logger.debug(f"后缀表达式 {ts}")

    try:
        v = calc_post(ts)
    except:
        raise Exception(choice(["什么鬼啦！", "你正常点，我害怕", "这，这不对吧", "寄"]))

    return v


@cat.on_cmd(cmds="测试24点", always=True)
async def test_exp():
    '''<表达式>'''
    exp = str(cat.current.arg)
    try:
        r = calc(exp)
    except Exception as e:
        await cat.send(str(e))
        return

    await cat.send(f"{exp}={r}")
