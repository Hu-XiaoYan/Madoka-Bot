from nonebot import on_command,get_driver
path=get_driver().config.bot_path
token=get_driver().config.dev_token
from nonebot.adapters.onebot.v11 import MessageSegment,Message,Event
from nonebot.params import CommandArg
import json,os,urllib.request,base64,aiohttp
from io import BytesIO
from PIL import ImageDraw,Image,ImageFont
from nonebot.permission import SUPERUSER

def check_ypos(chart:int):
    if chart==0:
        return 1060
    elif chart==1:
        return 1300
    elif chart==2:
        return 1540
    elif chart==3:
        return 1780
    else:
        return 2020
    
def check_rank(achi:str):
    if achi<50.0:
        return "d"
    elif achi<60.0:
        return "c"
    elif achi<70.0:
        return "b"
    elif achi<75.0:
        return "bb"
    elif achi<80.0:
        return "bbb"
    elif achi<90.0:
        return "a"
    elif achi<94.0:
        return "aa"
    elif achi<97.0:
        return "aaa"
    elif achi<98.0:
        return "s"
    elif achi<99.0:
        return "sp"
    elif achi<99.5:
        return "ss"
    elif achi<100.0:
        return "ssp"
    elif achi<100.5:
        return "sss"
    else:
        return "sssp"

async def get_playerdata(token,post_data):
    async with aiohttp.request("GET","https://www.diving-fish.com/api/maimaidxprober/dev/player/records",headers={'developer-token':token[0]},params=post_data) as resp_record:
        user_data=await resp_record.json()
        if resp_record.status==200:
            pass
        elif resp_record.status==400:
            await PlayerSongInfo.finish("⭐小圆没有找到该玩家⭐",reply_message=True)
        elif resp_record.status==403:
            await PlayerSongInfo.finish("⭐该玩家设置了隐私⭐",reply_message=True)
        else:
            await PlayerSongInfo.finish("⭐小圆把用户数据弄丢了⭐",reply_message=True)
        return user_data

def get_aliasdata():
    with open(f"./{path[0]}/src/Alias.json","r",encoding="UTF-8") as fs:
        alias_data=json.load(fs)
        alias_dict={}
        for info in alias_data:
            Now_Data=alias_data[info]
            alias_list=Now_Data["Alias"]
            alias_dict[info]=alias_list
        return alias_dict

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
            lv=NowSongInfo["level"]
            ds=NowSongInfo["ds"]
            ds_str=""
            for element in ds:
                ds_str=f"{element}/{ds_str}"
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
            info=[title,sid,"https://www.diving-fish.com/covers/{:05}.png".format(int(sid)),stype,lv,charts,dxs_max,artist,genre,bpm,sfrom,new,ds_str]
            Dict[sid]=info
        return Dict

def down_songpic(sid:str,url:str):
    if os.path.exists(f"./{path[0]}/src/Song_Pic")==False:
        os.makedirs(f"./{path[0]}/src/Song_Pic")
    if os.path.exists(f"./{path[0]}/src/Song_Pic/{sid}.png")==False:
        urllib.request.urlretrieve(url,f"./{path[0]}/src/Song_Pic/{sid}.png")

async def draw_achi(sarg,alias_data,music_data,player_data):
    geted_data=[]
    if sarg.isdigit()==True:
        if sarg not in music_data.keys():
            await PlayerSongInfo.finish("⭐歌曲ID错误,请检查⭐",reply_message=True)
        else:
            for info in player_data["records"]:
                if int(sarg)==info["song_id"]:
                    geted_data.append(info)
            if len(geted_data)==0:
                await PlayerSongInfo.finish("⭐小圆没找到数据呢⭐",reply_message=True)
            else:
                pass
    else:
        searched_songs=[]
        for info in alias_data:
            data=alias_data[info]
            for alias in data:
                if str(alias).lower().strip(" ")==sarg:
                    searched_songs.append(info)
        if len(searched_songs)>=2:
            message=""
            for sid in searched_songs:
                title=music_data[sid][0]
                message=message+f"{sid}.{title}\n"
            await PlayerSongInfo.finish("⭐小圆找到了下述歌曲⭐\n"+message+"⭐请使用单曲成绩 [歌曲ID]来查找下述歌曲⭐",reply_message=True)
        else:
            for info in player_data["records"]:
                if int(searched_songs[0])==info["song_id"]:
                    geted_data.append(info)
            if len(geted_data)==0:
                await PlayerSongInfo.finish("⭐小圆没找到数据呢⭐",reply_message=True)
            else:
                pass
    all_info=music_data[str(geted_data[0]["song_id"])]
    title=all_info[0]
    sid=all_info[1]
    url=all_info[2]
    stype=all_info[3]
    artist=all_info[7]
    ds=all_info[12].split("/")
    ds_rev=list(reversed(ds))
    genre=all_info[8]
    bpm=all_info[9]
    version=all_info[10]
    new=all_info[11]
    if stype=="MiLK PLUS":
        stype="maimai MiLK PLUS"
    if new==True:
        is_new="是"
    else:
        is_new="否"
    font=ImageFont.truetype(f"./{path[0]}/src/Font_Main.ttf",50)
    bg=Image.open(f"./{path[0]}/src/Pic/single_achi.png")
    down_songpic(sid,url)
    cover=Image.open(f"./{path[0]}/src/Song_Pic/{sid}.png")
    cover_re=cover.resize([440,440],Image.ANTIALIAS)
    _text=ImageDraw.Draw(bg)
    if len(title)>20:
        title=title[0:20]+"..."
    _text.text([975,345],sid,(255,255,255),font,stroke_width=5,stroke_fill=(0,0,0))
    _text.text([1160,345],genre,(255,255,255),font,stroke_width=5,stroke_fill=(0,0,0))
    _text.text([860,495],f"歌曲名:{title}\n艺术家:{artist}\nBPM:{bpm}\n版本:{version}\n是否为新歌:{is_new}",(255,255,255),font,stroke_width=5,stroke_fill=(0,0,0))
    bg.paste(cover_re,[310,386])
    if stype=="DX":
        song_type=Image.open(f"./{path[0]}/src/Pic/Song_DX.png")
    else:
        song_type=Image.open(f"./{path[0]}/src/Pic/Song_SD.png")
    bg.paste(song_type,(310,780),song_type)
    bg_=draw_detail(bg,geted_data,ds_rev)
    out_buffer=BytesIO()   
    bg_.save(out_buffer,"PNG")
    bytes_data=out_buffer.getvalue()
    image_ba64=base64.b64encode(bytes_data).decode()
    return image_ba64

def draw_detail(bg,played_data,ds_rev):
    x=400
    z=1558
    for element in played_data:
        achi_per=str(element["achievements"])+"%"
        achi=element["achievements"]
        fc=element["fc"]
        fs=element["fs"]
        chart=element["level_index"]
        y=check_ypos(chart)
        rank=check_rank(achi)
        for element in list(achi_per):
            _char=Image.open(f"./{path[0]}/src/Pic/x{element}.png")
            bg.paste(_char,[x,y],_char)
            x+=50
        x=400
        _rank=Image.open(f"./{path[0]}/src/Pic/rank_{rank}.png")
        bg.paste(_rank,[920,y-25],_rank)
        if fc=="":
            pass
        else:
            _fc=Image.open(f"./{path[0]}/src/Pic/2_{fc}.png")
            bg.paste(_fc,[1223,y-37],_fc)
        if fs=="":
            pass
        else:
            _fs=Image.open(f"./{path[0]}/src/Pic/2_{fs}.png")
            bg.paste(_fs,[1373,y-37],_fs)
        ds_list=ds_rev[chart+1]
        for element in ds_list:
            _char=Image.open(f"./{path[0]}/src/Pic/x{element}.png")
            bg.paste(_char,[z,y],_char)
            z+=50
        z=1558
        y+=240
    return bg

PlayerSongInfo=on_command("单曲成绩",priority=10)
@PlayerSongInfo.handle()
async def PlayerSongInfo_fanc(event:Event,command_arg:Message=CommandArg()):
    sarg=str(command_arg).strip()
    if sarg=="":
        await PlayerSongInfo.finish("⭐未检测到字符输入⭐",reply_message=True)
    user_id=str(event.get_user_id())
    post_data={"qq":user_id}
    player_data=await get_playerdata(token,post_data)
    alias_data=get_aliasdata()
    music_data=get_musicdata()
    image_ba64=await draw_achi(sarg,alias_data,music_data,player_data)
    await PlayerSongInfo.finish(MessageSegment.image(f"base64://{image_ba64}"),reply_message=True)