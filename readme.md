<div align="center">

# ayaka文字小游戏合集 - 0.0.0b1

开发进度 9/10，还剩1个小游戏等待构思

**特别感谢**  [@灯夜](https://github.com/lunexnocty/Meiri) 大佬的插件蛮好玩的~

</div>

得益于[ayaka](https://github.com/bridgeL/ayaka)，本插件可作为如下机器人框架的插件使用
- [nonebot2](https://github.com/nonebot/nonebot2)(使用[onebotv11](https://github.com/nonebot/adapter-onebot)适配器)
- [hoshino](https://github.com/Ice-Cirno/HoshinoBot)
- [nonebot1](https://github.com/nonebot/nonebot)

也可将其[作为console程序离线运行](#作为console程序离线运行)

## 安装

### 通过pip安装

```
pip install ayaka_games
```

### 手动下载后导入

还需额外安装依赖

```
pip install -r requirements.txt
```

## 指令

猫猫帮助

## 踩坑

CRLF换行符的文件，会在github上被强制换为LF换行符再发放，这会导致文件哈希值变化


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

## 其他

本插件的前身：[nonebot_plugin_ayaka_games](https://github.com/bridgeL/nonebot-plugin-ayaka-games)
