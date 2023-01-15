'''暴力遍历生成24点题库'''
import re
import json
from pydantic import BaseModel


class Question(BaseModel):
    nums: list[int]
    ops: list[str]
    solution: str

    def get_k(self):
        ts = [str(n) for n in self.nums]
        ts.sort()
        return " ".join(ts)

    def get_v(self):
        ts = [o for o in self.ops]
        ts.sort()
        return " ".join(ts)


def show_cnt(func):
    '''装饰器，展示输出的数字个数'''
    def _func(*args, **kwargs):
        rs = func(*args, **kwargs)
        print(func.__doc__ or func.__name__, len(rs))
        return rs
    return _func


class Builder:
    def __init__(self, n: int, template: str) -> None:
        self.n = n
        self.template = template

    def base_calc(self, n1: float, n2: float, op: str) -> float:
        # 阻断大指数运算
        if (n1 > 100 or n2 > 100) and op == "**":
            raise OverflowError
        return eval(f"n1{op}n2")

    def calc(self, nums: list[int], ops: list[str]) -> float:
        raise NotImplementedError

    def check_n(self, nums: list[int], ops: list[str]):
        try:
            n = self.calc(nums, ops)
        except OverflowError:
            return False
        except ZeroDivisionError:
            return False
        return abs(n-self.n) < 0.0001

    def load(self, name: str):
        with open(f"{self.n}_{name}.json", "r", encoding="utf8") as f:
            data = json.load(f)
        return [Question(**d) for d in data]

    def save(self, name: str, data: list[Question]):
        with open(f"{self.n}_{name}.json", "w+", encoding="utf8") as f:
            f.write("[\n")
            for d in data[:-1]:
                json.dump(d.dict(), f)
                f.write(",\n")
            json.dump(data[-1].dict(), f)
            f.write("\n]")

    def nums_iter(self):
        '''生成4个数字的迭代器'''
        nums = [i+1 for i in range(9)]
        for n1 in nums:
            print(n1)
            for n2 in nums:
                for n3 in nums:
                    for n4 in nums:
                        yield [n1, n2, n3, n4]

    def ops_iter(self):
        '''生成3个操作符的迭代器'''
        ops = ["+", "-", "*", "/", "**"]
        for op1 in ops:
            for op2 in ops:
                for op3 in ops:
                    yield [op1, op2, op3]

    def get_solution(self, nums: list[int], ops: list[str]):
        return self.template.format(
            n0=nums[0],
            n1=nums[1],
            n2=nums[2],
            n3=nums[3],
            op0=ops[0],
            op1=ops[1],
            op2=ops[2],
        )

    def sort(self, data: list[Question]):
        data.sort(key=lambda x: x.get_v())
        data.sort(key=lambda x: x.get_k())

    @show_cnt
    def create_rough_data(self):
        '''生成原始数据，并简单去重和排序'''
        record: dict[str, list[str]] = {}

        data: list[Question] = []
        for nums in self.nums_iter():
            for ops in self.ops_iter():
                if self.check_n(nums, ops):
                    q = Question(
                        nums=nums,
                        ops=ops,
                        solution=self.get_solution(nums, ops)
                    )
                    k = q.get_k()
                    v = q.get_v()
                    if k not in record:
                        record[k] = []
                    record[k].append(v)
                    data.append(q)

        self.sort(data)
        return data

    @show_cnt
    def remove_ops_same(self, data: list[Question]):
        '''移除三个操作符都一样的'''
        marks: set[str] = set()
        for d in data:
            if d.ops[0] == d.ops[1] and d.ops[1] == d.ops[2]:
                marks.add(d.get_k())

        data = [d for d in data if d.get_k() not in marks]
        return data

    @show_cnt
    def remove_special_ops(self, data: list[Question], ops: list[str]):
        '''移除指定的ops组合'''
        ops.sort()
        v = " ".join(ops)

        marks: set[str] = set()
        for d in data:
            if d.get_v() == v:
                marks.add(d.get_k())

        data = [d for d in data if d.get_k() not in marks]
        return data

    def beauty_save(self, name: str, data: list[Question]):
        rs: dict[str, list[str]] = {}
        for d in data:
            k = d.get_k()
            if k not in rs:
                rs[k] = []
            rs[k].append(d.solution)

        with open(f"{self.n}_{name}.json", "w+", encoding="utf8") as f:
            json.dump(rs, f, indent=4)


class Builder1(Builder):
    def __init__(self, n: int) -> None:
        super().__init__(n, "(({n0}{op0}{n1}){op1}{n2}){op2}{n3}")

    def calc(self, nums: list[int], ops: list[str]):
        n1 = nums[0]
        for op, n2 in zip(ops, nums[1:]):
            n1 = self.base_calc(n1, n2, op)
        return n1

    @show_cnt
    def remove_mult_one(self, data: list[Question]):
        '''排除一些简单的对1的乘除法、次方'''
        marks: set[str] = set()

        for d in data:
            if d.nums[0] == 1 and d.ops[0] in ["*", "**"]:
                marks.add(d.get_k())
                continue

            for i in range(3):
                if d.nums[i+1] == 1 and d.ops[i] in ["*", "**", "/"]:
                    marks.add(d.get_k())
                    break

        data = [d for d in data if d.get_k() not in marks]
        return data

    @show_cnt
    def remove_get_one(self, data: list[Question]):
        '''排除一些凑1的'''
        marks: set[str] = set()

        for d in data:
            if d.nums[0] == d.nums[1] and d.ops[0] == "/":
                marks.add(d.get_k())
                continue

        data = [d for d in data if d.get_k() not in marks]
        return data

    @show_cnt
    def combine_first_exchange(self, data: list[Question]):
        '''合并：头两个加乘法互换'''
        record: dict[str, list[set[int]]] = {}

        rs: list[Question] = []
        for d in data:
            if d.ops[0] in ["+", "*"]:
                k = d.get_k() + " " + d.get_v()
                v = set(d.nums[:2])
                if k not in record:
                    record[k] = []
                if v in record[k]:
                    continue
                record[k].append(v)
            rs.append(d)

        return rs

    @show_cnt
    def combine_mult_exchange(self, data: list[Question]):
        '''合并：中间两个或后两个乘除法互换'''
        patt1 = re.compile(r"\)([\*/]\d)\)([\*/]\d)")
        patt2 = re.compile(r"\d([\*/]\d)\)([\*/]\d)\)")

        rs: list[Question] = []

        ps1 = []
        ps2 = []
        k = ""

        for d in data:
            if k != d.get_k():
                k = d.get_k()
                ps1 = []
                ps2 = []

            s = d.solution
            r1 = patt1.search(s)
            r2 = patt2.search(s)
            if r1:
                ss = [r1.group(1), r1.group(2)]
                ss.sort()
                s = " ".join(ss)
                if s not in ps1:
                    ps1.append(s)
                else:
                    continue
            if r2:
                ss = [r2.group(1), r2.group(2)]
                ss.sort()
                s = " ".join(ss)
                if s not in ps2:
                    ps2.append(s)
                else:
                    continue

            rs.append(d)
        return rs

    @show_cnt
    def combine_add_exchange(self, data: list[Question]):
        '''合并：中间两个或后两个加减法互换'''
        patt1 = re.compile(r"\)([+-]\d)\)([+-]\d)")
        patt2 = re.compile(r"\d([+-]\d)\)([+-]\d)\)")

        rs: list[Question] = []

        ps1 = []
        ps2 = []
        k = ""

        for d in data:
            if k != d.get_k():
                k = d.get_k()
                ps1 = []
                ps2 = []

            s = d.solution
            r1 = patt1.search(s)
            r2 = patt2.search(s)
            if r1:
                ss = [r1.group(1), r1.group(2)]
                ss.sort()
                s = " ".join(ss)
                if s not in ps1:
                    ps1.append(s)
                else:
                    continue
            if r2:
                ss = [r2.group(1), r2.group(2)]
                ss.sort()
                s = " ".join(ss)
                if s not in ps2:
                    ps2.append(s)
                else:
                    continue

            rs.append(d)
        return rs


class Builder2(Builder):
    def __init__(self, n: int) -> None:
        super().__init__(n, "({n0}{op0}{n1}){op1}({n2}{op2}{n3})")

    def calc(self, nums: list[int], ops: list[str]):
        n1 = self.base_calc(nums[0], nums[1], ops[0])
        n2 = self.base_calc(nums[2], nums[3], ops[2])
        n = self.base_calc(n1, n2, ops[1])
        return n

    @show_cnt
    def remove_mult_one(self, data: list[Question]):
        '''排除一些简单的对1的乘除法、次方'''
        marks: set[str] = set()

        for d in data:
            if d.nums[0] == 1 and d.ops[0] in ["*", "**"]:
                marks.add(d.get_k())
                continue

            if d.nums[1] == 1 and d.ops[0] in ["*", "**", "/"]:
                marks.add(d.get_k())
                continue

            if d.nums[2] and d.ops[2] in ["*", "**"]:
                marks.add(d.get_k())
                continue

            if d.nums[3] and d.ops[2] in ["*", "**", "/"]:
                marks.add(d.get_k())
                continue

        data = [d for d in data if d.get_k() not in marks]
        return data

    @show_cnt
    def remove_get_one(self, data: list[Question]):
        '''排除一些凑1的'''
        marks: set[str] = set()

        for d in data:
            if d.nums[0] == d.nums[1] and d.ops[0] == "/":
                marks.add(d.get_k())
                continue

            if d.nums[2] == d.nums[3] and d.ops[0] == "/":
                marks.add(d.get_k())
                continue

        data = [d for d in data if d.get_k() not in marks]
        return data

    @show_cnt
    def combine_first_exchange(self, data: list[Question]):
        '''合并：头两个加乘法互换'''
        record: dict[str, list[set[int]]] = {}

        rs: list[Question] = []
        for d in data:
            if d.ops[0] in ["+", "*"]:
                k = d.get_k() + " " + d.get_v()
                v = set(d.nums[:2])
                if k not in record:
                    record[k] = []
                if v in record[k]:
                    continue
                record[k].append(v)
            rs.append(d)

        return rs

    @show_cnt
    def combine_final_exchange(self, data: list[Question]):
        '''合并：末两个加乘法互换'''
        record: dict[str, list[set[int]]] = {}

        rs: list[Question] = []
        for d in data:
            if d.ops[2] in ["+", "*"]:
                k = d.get_k() + " " + d.get_v()
                v = set(d.nums[2:])
                if k not in record:
                    record[k] = []
                if v in record[k]:
                    continue
                record[k].append(v)
            rs.append(d)

        return rs

    @show_cnt
    def combine_mid_exchange(self, data: list[Question]):
        '''合并：头尾两个加乘法互换'''
        record: dict[str, list[set[int]]] = {}

        rs: list[Question] = []
        for d in data:
            if d.ops[1] in ["+", "*"]:
                k = d.get_k() + " " + d.get_v()
                n1 = self.base_calc(d.nums[0], d.nums[1], d.ops[0])
                n2 = self.base_calc(d.nums[2], d.nums[3], d.ops[2])
                v = set([n1, n2])
                if k not in record:
                    record[k] = []
                if v in record[k]:
                    continue
                record[k].append(v)
            rs.append(d)

        return rs


# unit = Builder1(24)
# data = unit.create_rough_data()
# unit.save("1_temp", data)

# data = unit.load("1_temp")
# data = unit.remove_ops_same(data)
# data = unit.remove_get_one(data)
# data = unit.remove_special_ops(data, ["+", "+", "-"])
# data = unit.remove_special_ops(data, ["+", "-", "-"])
# data = unit.remove_special_ops(data, ["+", "+", "*"])
# data = unit.remove_special_ops(data, ["+", "-", "*"])
# data = unit.remove_special_ops(data, ["-", "-", "*"])
# data = unit.remove_mult_one(data)
# data = unit.combine_first_exchange(data)
# data = unit.combine_mult_exchange(data)
# data = unit.combine_add_exchange(data)
# unit.save("1", data)

# data = unit.load("1")
# data2 = data
# unit.beauty_save("1_b", data)

# unit = Builder2(24)
# data = unit.create_rough_data()
# unit.save("2_temp", data)

# data = unit.load("2_temp")
# data = unit.remove_ops_same(data)
# data = unit.remove_get_one(data)
# data = unit.remove_mult_one(data)
# data = unit.combine_first_exchange(data)
# data = unit.combine_final_exchange(data)
# data = unit.combine_mid_exchange(data)
# unit.save("2", data)

# data = unit.load("2")
# unit.beauty_save("2_b", data)


# # 合并
# data2 += data
# unit.sort(data2)
# unit.beauty_save("", data2)



unit = Builder1(48)
data = unit.create_rough_data()
unit.save("1_temp", data)

data = unit.load("1_temp")
data = unit.remove_ops_same(data)
data = unit.remove_get_one(data)
data = unit.remove_special_ops(data, ["+", "+", "-"])
data = unit.remove_special_ops(data, ["+", "-", "-"])
data = unit.remove_special_ops(data, ["+", "+", "*"])
data = unit.remove_special_ops(data, ["+", "-", "*"])
data = unit.remove_special_ops(data, ["-", "-", "*"])
data = unit.remove_mult_one(data)
data = unit.combine_first_exchange(data)
data = unit.combine_mult_exchange(data)
data = unit.combine_add_exchange(data)
unit.save("1", data)

data = unit.load("1")
data2 = data
unit.beauty_save("1_b", data)

unit = Builder2(48)
data = unit.create_rough_data()
unit.save("2_temp", data)

data = unit.load("2_temp")
data = unit.remove_ops_same(data)
data = unit.remove_get_one(data)
data = unit.remove_mult_one(data)
data = unit.combine_first_exchange(data)
data = unit.combine_final_exchange(data)
data = unit.combine_mid_exchange(data)
unit.save("2", data)

data = unit.load("2")
unit.beauty_save("2_b", data)


# 合并
data2 += data
unit.sort(data2)
unit.beauty_save("", data2)