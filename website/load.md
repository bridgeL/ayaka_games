得益于[ayaka](https://github.com/bridgeL/ayaka)，本插件可作为如下机器人框架的插件使用

- [nonebot2](https://github.com/nonebot/nonebot2)(使用[onebot11](https://github.com/nonebot/adapter-onebot)适配器)
- [hoshino](https://github.com/Ice-Cirno/HoshinoBot)
- [nonebot1](https://github.com/nonebot/nonebot)

也可将其作为console程序离线运行

## 作为nonebot2/nonebot1插件导入

- 通过pip安装
- 修改`bot.py`，加入`nonebot.load_plugin("ayaka_games")`

## 作为hoshino插件导入

- 从github仓库下载
- 安装依赖`pip install -r requirements.txt`
- 将内部的`ayaka_games`文件夹放入`hoshino/modules`
- 在`hoshino/config/__bot__.py`中的`MODULES_ON`里，写入字符串`ayaka_games`

## 作为console程序离线运行

```
# run.py
import ayaka.adapters as cat

cat.init()
cat.regist()

# 加载插件
import ayaka_games

if __name__ == "__main__":
    cat.run()
```

```
python run.py
```