from nonebot import on_command,get_driver
path=get_driver().config.bot_path
from nonebot.adapters.onebot.v11 import MessageSegment,Event
import time,json,os,urllib.request

def get_musicdata():
    with open(f"./{path[0]}/src/MusicData.json","r",encoding="UTF-8") as fs:
        All_Songs=json.load(fs)
        Dict={}
        for NowSongInfo in All_Songs:
            title=NowSongInfo["title"]
            stype=NowSongInfo["type"]
            if title in Dict.keys() and stype=="DX":
                title=title+"[DX]"
            sid=NowSongInfo["id"]
            ds=NowSongInfo["ds"]
            charts=NowSongInfo["charts"]
            dxs_max=[]
            for element in charts:
                _charts=element["notes"]
                x=0
                z=0
                for x in range(len(_charts)):
                    z+=_charts[x]
                    x+=1
                dxs_max.append(z*3)
            basic_info=NowSongInfo["basic_info"]
            artist=basic_info["artist"]
            genre=basic_info["genre"]
            bpm=basic_info["bpm"]
            sfrom=basic_info["from"]
            new=basic_info["is_new"]
            info=[title,sid,"https://www.diving-fish.com/covers/{:05}.png".format(int(sid)),stype,ds,charts,dxs_max,artist,genre,bpm,sfrom,new]
            Dict[sid]=info
        return Dict
    
def down_songpic(sid:str,url:str):
    if os.path.exists(f"./{path[0]}/src/Song_Pic")==False:
        os.makedirs(f"./{path[0]}/src/Song_Pic")
    if os.path.exists(f"./{path[0]}/src/Song_Pic/{sid}.png")==False:
        urllib.request.urlretrieve(url,f"./{path[0]}/src/Song_Pic/{sid}.png")

def fortune_num(user_qqid):
    today=(list(time.localtime())[2]+24)*list(time.localtime())[1]*user_qqid
    return today >> 8

Fortune=on_command("今日运势",aliases={"jrys"},priority=10)
@Fortune.handle()
async def Fortune_fanc(event:Event):
    user_qqid=event.get_user_id()
    _num=fortune_num(int(user_qqid))
    todo_list=["越级","下埋","吃分","打段位","打友人","吃麦麦","吃KFC","收歌","小憩","练准度"]
    lucky_num=_num%100
    yes_todo=[]
    no_todo=[]
    for count in range(10):
        value=_num&3
        _num>>=2
        if value==3:
            yes_todo.append(todo_list[count])
        elif value==1:
            no_todo.append(todo_list[count])
        else:
            pass
    Music_Dict=get_musicdata()
    today_music=_num%len(Music_Dict)
    while str(today_music) not in Music_Dict.keys():
        today_music+=1
    title=Music_Dict[str(today_music)][0]
    sid=Music_Dict[str(today_music)][1]
    url=Music_Dict[str(today_music)][2]
    ds=Music_Dict[str(today_music)][4]
    artist=Music_Dict[str(today_music)][7]
    genre=Music_Dict[str(today_music)][8]
    bpm=Music_Dict[str(today_music)][9]
    ver=Music_Dict[str(today_music)][10]
    if ver=="MiLK PLUS":
        ver="maimai MiLK PLUS"
    if len(yes_todo)==0:
        yes_todo.append("小圆没有要建议的哦~")
    elif len(no_todo)==0:
        no_todo.append("小圆没有要建议的哦~")
    ds_list=[str(x) for x in ds]
    ds_str="/".join(ds_list)
    down_songpic(str(sid),str(url))
    await Fortune.finish(f"今天是{time.strftime('%Y年%m月%d日')}\n你今天的幸运数字是:{lucky_num}\n宜:{','.join(yes_todo)}\n忌:{','.join(no_todo)}\n小圆提醒您:出勤不要大力拍打机器哦\n今日推荐歌曲:\n{sid}.{title}"
+MessageSegment.image(f"file:///{os.getcwd()}/{path[0]}/src/Song_Pic/{sid}.png")+f"\n{ds_str}\n艺术家:{artist}\nBPM:{bpm}\n分类:{genre}\n版本:{ver}",reply_message=True)
    