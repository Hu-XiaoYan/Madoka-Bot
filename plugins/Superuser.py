from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message,Bot
from nonebot import get_driver
path=get_driver().config.bot_path
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
import aiohttp

async def downfile(): 
    try:
        async with aiohttp.request("GET","https://api.yuzuai.xyz/maimaidx/maimaidxalias") as resp_alias:
            content=await resp_alias.read()
            with open(f"./{path[0]}/src/Alias.json","wb") as file:
                file.write(content)
        async with aiohttp.request("GET","https://www.diving-fish.com/api/maimaidxprober/music_data") as resp_names:
            content=await resp_names.read()
            with open(f"./{path[0]}/src/MusicData.json","wb") as file:
                file.write(content)
                return True
    except:
        return False

Update=on_command("update",priority=8,permission=SUPERUSER)
@Update.handle()
async def Update_fanc():
    await Update.send("⭐更新数据中,请稍后...⭐",reply_message=True)
    status=await downfile()
    if status==True:
        await Update.finish("⭐更新完成⭐",reply_message=True)
    else:
        await Update.finish("⭐更新失败⭐",reply_message=True)

Notice=on_command("notice",priority=8,permission=SUPERUSER)
@Notice.handle()
async def Notice_fanc(bot:Bot,command_arg:Message=CommandArg()):
    NoticeContent=str(command_arg).strip()
    Ingored_List=get_driver().config.notice_ingore
    Group_List=[]
    Header="⭐公告⭐\n"
    Foot="\n⭐魔法和奇迹,其实一直都存在哦⭐"
    if NoticeContent=="":
        await Notice.finish("⭐未检测到字符输入⭐",reply_message=True)
    else:
        for info in await bot.get_group_list():
            gid=str(info["group_id"])
            if gid in Ingored_List:
                pass
            else:
                Group_List.append(gid)
        for id in Group_List:
            await bot.send_group_msg(group_id=int(id),message=Header+NoticeContent+Foot)