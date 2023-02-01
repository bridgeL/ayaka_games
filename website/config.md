你可以自定义一些配置

## 推荐配置

```
command_start = [""]
```

## 记得重启

修改配置后需要**重启bot**才生效

## 总配置

`data/ayaka/ayaka_games.json`

| 属性               | 含义                           | 所属游戏 |
| ------------------ | ------------------------------ | -------- |
| `auto_update`      | 自动从github下载最新游戏数据   | -        |
| `dragon_reward`    | 接龙奖励                       | 接龙     |
| `checkin_reward`   | 签到奖励                       | 签到     |
| `calculate_reward` | 答题奖励                       | 24点     |
| `word_tax`         | -                              | 文字税   |
| `tax`              | 单字税收                       | 文字税   |
| `buy_price`        | 购买文字费用                   | 文字税   |
| `open_duration`    | 市场开放时长（单位：秒）       | 文字税   |
| `valid_duration`   | 文字购买后生效时长（单位：秒） | 文字税   |
| `tax_notice`       | 被收文字税时是否发送提示       | 文字税   |
| `pray`             | -                              | 祈祷     |
| `reward`           | 奖励                           | 祈祷     |
| `weight`           | 权重越大，随机到的可能性越大   | 祈祷     |

## 独立数据文件

### 接龙

- `data/ayaka_games/接龙/成语.txt`
- `data/ayaka_games/接龙/原神.txt`

可以自行添加你想要的词汇

如果想添加词典，直接添加`<词典名>.txt`文件即可，bot重启后会自动读取该词典

### 24点

- `data/ayaka_games/24点/24.json`
- `data/ayaka_games/24点/48.json`

如果想添加新题型，直接添加`<数字>.json`文件即可，bot重启后会自动读取该题型

### 文字税

`data/ayaka_games/文字税.txt`

设置文字市场的文字池，每次从文字池中抽取20个进入市场

### 谁是卧底

`data/ayaka_games/谁是卧底.txt`

可以自行添加你想要的词汇，一行一对词汇，前者是普通人，后者是卧底

### 原神随机事件

`data/ayaka_games/原神随机事件.json`

看得懂就自己改，看不懂就算了，写的比较随性（doge

## 下一步

<div align="right">
    在这里~ ↘
</div>
