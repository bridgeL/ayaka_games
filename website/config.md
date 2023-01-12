你可以自定义一些配置

## 记得重启

修改配置后需要**重启bot**才生效

## 命令开头和分隔符

请修改相应机器人框架的配置

ayaka使用机器人框架的配置的command_start、command_sep项，且**仅取其第一项的值**

## 自动数据更新

bot重启后，自动从github拉取最新数据，由于网络原因，有概率拉取失败

位置 `data/ayaka/ayaka_games.json`

| 属性          | 意义                    |
| ------------- | ----------------------- |
| `auto_update` | 设置为false关闭自动更新 |

## 接龙

位置

- `data/ayaka_games/接龙/成语.txt`
- `data/ayaka_games/接龙/原神.txt`

可以自行添加你想要的词汇

如果想添加词典，直接添加`<词典名>.txt`文件即可，bot重启后会自动读取该词典

位置 `data/ayaka/ayaka_games.json`

| 属性            | 意义     |
| --------------- | -------- |
| `dragon_reward` | 接龙奖励 |

## 签到

位置 `data/ayaka/ayaka_games.json`

| 属性             | 意义     |
| ---------------- | -------- |
| `checkin_reward` | 签到奖励 |

## 24点

位置

- `data/ayaka_games/24点/24.json`
- `data/ayaka_games/24点/48.json`

可以自行添加题目

如果想添加新题型，直接添加`<数字>.json`文件即可，bot重启后会自动读取该题型

位置 `data/ayaka/ayaka_games.json`

| 属性               | 意义     |
| ------------------ | -------- |
| `calculate_reward` | 答题奖励 |

## 文字税

位置 `data/ayaka/ayaka_games.json`


`word_tax` 子项

| 属性             | 意义                          |
| ---------------- | ----------------------------- |
| `tax`            | 单字税收                      |
| `buy_price`      | 购买文字费用                  |
| `open_duration`  | 市场开放市场（单位：s）       |
| `valid_duration` | 文字购买后生效时长（单位：s） |
| `tax_notice`     | 被收文字税时是否发送提示      |

位置 `data/ayaka_games/文字税.txt`

设置文字市场的文字池，每次从文字池中抽取20个进入市场

## 祈祷

位置 `data/ayaka/ayaka_games.json`

`pray` 子项

| 属性     | 意义                               |
| -------- | ---------------------------------- |
| `reward` | 奖励                               |
| `weight` | 权重，权重越大，随机到的可能性越大 |

## 谁是卧底

位置 `data/ayaka_games/谁是卧底.txt`

可以自行添加你想要的词汇，一行一对词汇，前者是普通人，后者是卧底

## 原神随机事件

位置 `data/ayaka_games/原神随机事件.json`

看得懂就自己改，看不懂就算了（doge
