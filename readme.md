<div align="center">

# Ayaka小游戏合集 - 0.2.2

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ayaka_games)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ayaka_games)
![PyPI - License](https://img.shields.io/pypi/l/ayaka_games)
![PyPI](https://img.shields.io/pypi/v/ayaka_games)

开发进度 10/10

**特别感谢**  [@灯夜](https://github.com/lunexnocty/Meiri) 大佬的印加宝藏

</div>

得益于[ayaka](https://github.com/bridgeL/ayaka)，本插件可作为如下机器人框架的插件使用

- [nonebot2](https://github.com/nonebot/nonebot2)(使用[onebot11](https://github.com/nonebot/adapter-onebot)适配器)
- [hoshino](https://github.com/Ice-Cirno/HoshinoBot)
- [nonebot1](https://github.com/nonebot/nonebot)

也可将其作为console程序离线运行

## 文档

https://bridgel.github.io/ayaka_games/

## 历史遗留问题

如果你之前安装过`nonebot_plugin_ayaka_games`，请先确保它卸载干净

```
pip uninstall nonebot_plugin_ayaka_games
pip uninstall nonebot_plugin_ayaka
```

## 安装

```
pip install ayaka_games
```

## 作为console程序离线运行

```py
# run.py
import ayaka.adapters.console as cat

# 加载插件
import ayaka_games

if __name__ == "__main__":
    cat.run()
```

```
python run.py
```

## 其他

本插件的前身：[nonebot_plugin_ayaka_games](https://github.com/bridgeL/nonebot-plugin-ayaka-games)
