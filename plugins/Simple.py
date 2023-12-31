from nonebot import on_command

Help=on_command("帮助",aliases={"help"},priority=10)
@Help.handle()
async def Help_fanc():
    await Help.finish(
"""まどかBot菜单 V0.8 Alpha
1.今日运势--获取你今天的运势
2.我的排名--获取你在水鱼查分器的排名
3.随机乐曲 [谱面类型] [等级][难度]--在指定条件内随机一首歌曲
4.查找乐曲 [乐曲名字/别名]--查找指定参数的歌曲
5.精确查找 [乐曲ID]--查找指定ID的歌曲
6.别名查找 [乐曲ID]--查找指定ID的歌曲别名
7.定数查找 [定数1] [定数2(可选)]--查找指定定数范围内的歌曲
8.B50 [用户名(可选)]--查询自己或他人的Best50成绩
9.设置 [姓名框/底板/真段位优先/头像] [序号]--设置自定义姓名框和底板
10.展示 [姓名框/底板/头像]--显示可设置的姓名框和底板
11.课题曲 [官方随机段位/定数1] [定数2(可选)]--进行课题曲的随机
12.单曲成绩 [歌曲ID/歌曲名字或别名]--进行单曲成绩查询
⭐魔法和奇迹,其实一直都存在哦~⭐""",reply_message=True)