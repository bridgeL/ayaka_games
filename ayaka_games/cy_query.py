'''
    成语查询
'''
from random import sample
from ayaka import AyakaCat, load_data_from_file
from .data import downloader

cat = AyakaCat("成语查询")
cat.help = '''
有效提高群文学氛围

数据来源：成语大全（20104条成语数据）
'''

search_dict = {}


@downloader.on_finish
async def finish():
    global search_dict
    path = downloader.BASE_DIR / "成语词典.json"
    search_dict = load_data_from_file(path)


async def show_word(word: str):
    if word in search_dict:
        info = word + "\n" + search_dict[word]
        await cat.send(info)
    else:
        await cat.send("没有找到相关信息")


@cat.on_cmd(cmds="搜索成语")
async def handle_3():
    '''搜索所有相关的成语，可输入多个关键词更准确'''
    args = [arg for arg in cat.current.args if isinstance(arg, str)]

    if not args:
        await cat.send("没有输入关键词")
        return

    words = []
    for _word in search_dict:
        for arg in args:
            if arg not in _word:
                break
        else:
            words.append(_word)

    if not words:
        await cat.send("没有找到相关信息")
        return

    n = len(words)

    if n > 3:
        infos = [
            f"搜索关键词：{args}",
            f"共找到{n}条相关信息"
        ]
        if n > 100:
            infos.append("数量过多，仅展示随机抽取的100条")
            words = sample(words, 100)
        infos.append("\n".join(words))
        await cat.send_many(infos)
    else:
        for word in words:
            await show_word(word)
