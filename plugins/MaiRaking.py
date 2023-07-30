from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment,Event
import aiohttp,base64
import matplotlib.pyplot as plt
from io import BytesIO

async def get_info(post_data):
    async with aiohttp.request("POST","https://www.diving-fish.com/api/maimaidxprober/query/player",json=post_data) as resp_userinfo:
        user_data=await resp_userinfo.json()
        if resp_userinfo.status==200:
            pass
        elif resp_userinfo.status==400:
            await MyRank.finish("⭐小圆没有找到该玩家⭐",reply_message=True)
        elif resp_userinfo.status==403:
            await MyRank.finish("⭐该玩家设置了隐私⭐",reply_message=True)
        else:
            await MyRank.finish("⭐用户数据丢失⭐",reply_message=True)
            
    async with aiohttp.request("GET","https://www.diving-fish.com/api/maimaidxprober/rating_ranking") as resp_rank:
        raking_data=await resp_rank.json()
        if resp_rank.status!=200:
            await MyRank.finish("⭐排名数据丢失⭐",reply_message=True)
    
    list_raking_data=[]
    dict_raking_data={}
    for info in raking_data:
        dict_raking_data[info["username"]]=info["ra"]
        list_raking_data.append(info["ra"])
    tuple_raking_data=sorted(dict_raking_data.items(),key=lambda kv:kv[1]) 
    dict_raking_data=dict(tuple_raking_data)
    return user_data,dict_raking_data,list_raking_data

async def draw_pic(post_data):
    user_data,raking_data,list_raking_data=await get_info(post_data)
    my_rating=user_data["rating"]
    my_name=user_data["username"]
    raking=len(raking_data)
    sum_ra=0
    for info in raking_data:
        if info==my_name:
            raking-=1
            break
        raking-=1
    for info in raking_data:
        sum_ra+=raking_data[info]
    if raking==0:
        await MyRank.finish("⭐该玩家设置了隐私⭐",reply_message=True)
    raking_percent=round(((len(raking_data)-raking)/len(raking_data))*100,2)
    avg_rating=round(sum_ra/len(raking_data),2)
    plt.rcParams['font.family']=['DingTalk JinBuTi']
    plt.rc('axes', unicode_minus=False)
    plt.xlabel("Rating")
    plt.ylabel("人数")
    plt.hist(list_raking_data,bins=30,color='pink',alpha=1.0,histtype="step")
    plt.annotate(f'这是你的位置\n你的Rating:{my_rating}\n你的排名:{raking}\n你超越了:{raking_percent}%的玩家\n平均Rating为:{avg_rating}\n本图表由鹿目圆Bot生成 >.<',xy=(my_rating,0),xytext=(0,600),arrowprops=dict(facecolor='pink',shrink=0.05,alpha=0.5),
                 bbox=dict(boxstyle='round,pad=0.5',fc='pink', alpha=0.5))
    out_buffer=BytesIO()
    plt.savefig(out_buffer,dpi=200)
    plt.clf()
    bytes_data=out_buffer.getvalue()
    image_ba64=base64.b64encode(bytes_data).decode()
    return f"base64://{image_ba64}"

MyRank=on_command("我的排名",priority=10)
@MyRank.handle()
async def MyRank_fanc(event:Event):
    user_qqid=str(event.get_user_id())
    image_ba64=await draw_pic({"qq":user_qqid})
    await MyRank.finish(MessageSegment.image(image_ba64),reply_message=True)